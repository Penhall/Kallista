# integrations/config/dynamic_config_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json
from pathlib import Path
import yaml
import dotenv
import os
import re

class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigScope(Enum):
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    PROJECT = "project"
    USER = "user"

class DynamicConfigManager:
    def __init__(self, base_config: Dict):
        self.logger = logging.getLogger(__name__)
        self.config_path = Path("config")
        self.config_path.mkdir(exist_ok=True)
        
        self.base_config = base_config
        self.current_environment = EnvironmentType(
            os.getenv('ENVIRONMENT', 'development')
        )
        
        self.config_cache: Dict[str, Dict] = {}
        self._init_config_system()

    def _init_config_system(self):
        """Inicializa sistema de configuração"""
        try:
            # Carrega variáveis de ambiente
            dotenv.load_dotenv()
            
            # Cria diretórios de configuração
            for scope in ConfigScope:
                (self.config_path / scope.value).mkdir(exist_ok=True)
            
            # Carrega configurações base
            self._load_base_configs()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize config system: {str(e)}")
            raise

    async def get_config(
        self,
        scope: ConfigScope,
        name: str,
        environment: Optional[EnvironmentType] = None
    ) -> Dict:
        """Recupera configuração"""
        try:
            cache_key = f"{scope.value}_{name}_{environment.value if environment else 'all'}"
            
            # Verifica cache
            if cache_key in self.config_cache:
                return self.config_cache[cache_key]
            
            # Carrega configuração
            config = await self._load_config(scope, name, environment)
            
            # Atualiza cache
            self.config_cache[cache_key] = config
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to get config: {str(e)}")
            raise

    async def set_config(
        self,
        scope: ConfigScope,
        name: str,
        config: Dict,
        environment: Optional[EnvironmentType] = None
    ) -> Dict:
        """Atualiza configuração"""
        try:
            # Valida configuração
            validation = self._validate_config(config)
            if not validation['valid']:
                raise ConfigError(f"Invalid configuration: {validation['errors']}")
            
            # Determina caminho do arquivo
            config_file = self._get_config_path(scope, name, environment)
            
            # Salva configuração
            await self._save_config(config_file, config)
            
            # Limpa cache
            cache_key = f"{scope.value}_{name}_{environment.value if environment else 'all'}"
            if cache_key in self.config_cache:
                del self.config_cache[cache_key]
            
            return {
                'scope': scope.value,
                'name': name,
                'environment': environment.value if environment else 'all',
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set config: {str(e)}")
            raise

    async def delete_config(
        self,
        scope: ConfigScope,
        name: str,
        environment: Optional[EnvironmentType] = None
    ) -> Dict:
        """Remove configuração"""
        try:
            config_file = self._get_config_path(scope, name, environment)
            
            if config_file.exists():
                config_file.unlink()
            
            # Limpa cache
            cache_key = f"{scope.value}_{name}_{environment.value if environment else 'all'}"
            if cache_key in self.config_cache:
                del self.config_cache[cache_key]
            
            return {
                'scope': scope.value,
                'name': name,
                'environment': environment.value if environment else 'all',
                'deleted_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete config: {str(e)}")
            raise

    async def list_configs(
        self,
        scope: Optional[ConfigScope] = None,
        environment: Optional[EnvironmentType] = None
    ) -> List[Dict]:
        """Lista configurações disponíveis"""
        try:
            configs = []
            
            for config_scope in ConfigScope if not scope else [scope]:
                scope_path = self.config_path / config_scope.value
                
                for config_file in scope_path.glob("*.yml"):
                    try:
                        config = yaml.safe_load(config_file.read_text())
                        
                        # Filtra por ambiente
                        if environment and config.get('environment') != environment.value:
                            continue
                            
                        configs.append({
                            'scope': config_scope.value,
                            'name': config_file.stem,
                            'environment': config.get('environment', 'all'),
                            'updated_at': datetime.fromtimestamp(
                                config_file.stat().st_mtime
                            ).isoformat()
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to load config {config_file}: {str(e)}")
            
            return configs
            
        except Exception as e:
            self.logger.error(f"Failed to list configs: {str(e)}")
            raise

    async def get_environment_variables(
        self,
        environment: Optional[EnvironmentType] = None
    ) -> Dict[str, str]:
        """Recupera variáveis de ambiente"""
        try:
            env_vars = {}
            
            # Carrega variáveis do sistema
            for key, value in os.environ.items():
                if key.startswith(self.base_config.get('env_prefix', 'KALLISTA_')):
                    env_vars[key] = value
            
            # Carrega variáveis do ambiente específico
            if environment:
                env_file = self.config_path / f".env.{environment.value}"
                if env_file.exists():
                    env_vars.update(dotenv.dotenv_values(env_file))
            
            return env_vars
            
        except Exception as e:
            self.logger.error(f"Failed to get environment variables: {str(e)}")
            raise

    async def set_environment_variable(
        self,
        key: str,
        value: str,
        environment: Optional[EnvironmentType] = None
    ) -> Dict:
        """Define variável de ambiente"""
        try:
            if environment:
                env_file = self.config_path / f".env.{environment.value}"
                
                # Carrega variáveis existentes
                env_vars = dotenv.dotenv_values(env_file) if env_file.exists() else {}
                
                # Atualiza variável
                env_vars[key] = value
                
                # Salva arquivo
                with open(env_file, 'w') as f:
                    for k, v in env_vars.items():
                        f.write(f"{k}={v}\n")
            else:
                # Define variável no ambiente atual
                os.environ[key] = value
            
            return {
                'key': key,
                'environment': environment.value if environment else 'current',
                'updated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set environment variable: {str(e)}")
            raise

    def _load_base_configs(self):
        """Carrega configurações base"""
        try:
            # Carrega configuração global
            global_config = self._load_yaml_file(
                self.config_path / 'global/base.yml'
            )
            if global_config:
                self.base_config.update(global_config)
            
            # Carrega configuração do ambiente
            env_config = self._load_yaml_file(
                self.config_path / f'environment/{self.current_environment.value}.yml'
            )
            if env_config:
                self.base_config.update(env_config)
                
        except Exception as e:
            self.logger.error(f"Failed to load base configs: {str(e)}")
            raise

    async def _load_config(
        self,
        scope: ConfigScope,
        name: str,
        environment: Optional[EnvironmentType]
    ) -> Dict:
        """Carrega configuração específica"""
        config = {}
        
        # Carrega configuração base do escopo
        base_config = self._load_yaml_file(
            self.config_path / scope.value / f"{name}.yml"
        )
        if base_config:
            config.update(base_config)
        
        # Carrega configuração do ambiente
        if environment:
            env_config = self._load_yaml_file(
                self.config_path / scope.value / f"{name}.{environment.value}.yml"
            )
            if env_config:
                config.update(env_config)
        
        # Processa variáveis de ambiente
        config = self._process_env_vars(config)
        
        return config

    def _get_config_path(
        self,
        scope: ConfigScope,
        name: str,
        environment: Optional[EnvironmentType]
    ) -> Path:
        """Determina caminho do arquivo de configuração"""
        if environment:
            return self.config_path / scope.value / f"{name}.{environment.value}.yml"
        return self.config_path / scope.value / f"{name}.yml"

    async def _save_config(self, config_file: Path, config: Dict):
        """Salva configuração em arquivo"""
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

    def _validate_config(self, config: Dict) -> Dict:
        """Valida configuração"""
        errors = []
        
        # Verifica estrutura básica
        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            
        # Verifica valores não permitidos
        for key, value in config.items():
            if isinstance(value, (dict, list)):
                continue
            if not isinstance(value, (str, int, float, bool)):
                errors.append(f"Invalid value type for key {key}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _process_env_vars(self, config: Dict) -> Dict:
        """Processa variáveis de ambiente na configuração"""
        if isinstance(config, dict):
            return {
                key: self._process_env_vars(value)
                for key, value in config.items()
            }
        elif isinstance(config, list):
            return [
                self._process_env_vars(item)
                for item in config
            ]
        elif isinstance(config, str):
            # Procura referências a variáveis de ambiente
            matches = re.findall(r'\${([^}]+)}', config)
            
            if matches:
                for match in matches:
                    env_value = os.getenv(match)
                    if env_value:
                        config = config.replace(f"${{{match}}}", env_value)
            
        return config

    @staticmethod
    def _load_yaml_file(file_path: Path) -> Optional[Dict]:
        """Carrega arquivo YAML"""
        if file_path.exists():
            with open(file_path) as f:
                return yaml.safe_load(f)
        return None

class ConfigError(Exception):
    pass