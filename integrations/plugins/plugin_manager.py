# integrations/plugins/plugin_manager.py
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
import asyncio
import logging
from datetime import datetime
import importlib
import inspect
import json
from pathlib import Path
import yaml

class PluginType(Enum):
    TOOL = "tool"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    ANALYZER = "analyzer"
    GENERATOR = "generator"

class PluginStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

class PluginManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.plugins_path = Path(config.get('plugins_path', 'plugins'))
        self.plugins_path.mkdir(exist_ok=True)
        
        self.plugins: Dict[str, Dict] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        
        self._init_plugin_system()

    def _init_plugin_system(self):
        """Inicializa sistema de plugins"""
        try:
            # Cria diretórios necessários
            for plugin_type in PluginType:
                (self.plugins_path / plugin_type.value).mkdir(exist_ok=True)
            
            # Carrega plugins existentes
            self._load_installed_plugins()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin system: {str(e)}")
            raise

    async def install_plugin(self, plugin_data: Dict) -> Dict:
        """Instala um novo plugin"""
        try:
            plugin_id = f"{plugin_data['name']}_{datetime.utcnow().timestamp()}"
            
            # Valida plugin
            validation = await self._validate_plugin(plugin_data)
            if not validation['valid']:
                raise PluginError(f"Invalid plugin: {validation['errors']}")
            
            # Cria diretório do plugin
            plugin_dir = self.plugins_path / plugin_data['type'] / plugin_data['name']
            plugin_dir.mkdir(exist_ok=True)
            
            # Salva arquivos do plugin
            await self._save_plugin_files(plugin_dir, plugin_data)
            
            # Registra plugin
            self.plugins[plugin_id] = {
                'id': plugin_id,
                'name': plugin_data['name'],
                'type': plugin_data['type'],
                'version': plugin_data['version'],
                'status': PluginStatus.ENABLED.value,
                'installed_at': datetime.utcnow().isoformat(),
                'config': plugin_data.get('config', {})
            }
            
            # Carrega plugin
            await self._load_plugin(plugin_id)
            
            return {
                'plugin_id': plugin_id,
                'status': 'installed'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to install plugin: {str(e)}")
            raise

    async def uninstall_plugin(self, plugin_id: str) -> Dict:
        """Remove um plugin"""
        try:
            if plugin_id not in self.plugins:
                raise PluginError(f"Plugin {plugin_id} not found")
            
            plugin = self.plugins[plugin_id]
            
            # Desabilita plugin
            await self.disable_plugin(plugin_id)
            
            # Remove arquivos
            plugin_dir = self.plugins_path / plugin['type'] / plugin['name']
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            
            # Remove registro
            del self.plugins[plugin_id]
            
            return {
                'plugin_id': plugin_id,
                'status': 'uninstalled'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall plugin: {str(e)}")
            raise

    async def enable_plugin(self, plugin_id: str) -> Dict:
        """Habilita um plugin"""
        try:
            if plugin_id not in self.plugins:
                raise PluginError(f"Plugin {plugin_id} not found")
            
            # Carrega plugin
            await self._load_plugin(plugin_id)
            
            # Atualiza status
            self.plugins[plugin_id]['status'] = PluginStatus.ENABLED.value
            
            return {
                'plugin_id': plugin_id,
                'status': 'enabled'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to enable plugin: {str(e)}")
            self.plugins[plugin_id]['status'] = PluginStatus.ERROR.value
            raise

    async def disable_plugin(self, plugin_id: str) -> Dict:
        """Desabilita um plugin"""
        try:
            if plugin_id not in self.plugins:
                raise PluginError(f"Plugin {plugin_id} not found")
            
            # Remove hooks do plugin
            plugin = self.plugins[plugin_id]
            for hook_name in self.hooks:
                self.hooks[hook_name] = [
                    h for h in self.hooks[hook_name]
                    if getattr(h, '__plugin__', None) != plugin_id
                ]
            
            # Atualiza status
            plugin['status'] = PluginStatus.DISABLED.value
            
            return {
                'plugin_id': plugin_id,
                'status': 'disabled'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to disable plugin: {str(e)}")
            raise

    async def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[Dict]:
        """Lista plugins instalados"""
        try:
            plugins = []
            
            for plugin_id, plugin in self.plugins.items():
                if plugin_type and plugin['type'] != plugin_type.value:
                    continue
                plugins.append(plugin)
            
            return plugins
            
        except Exception as e:
            self.logger.error(f"Failed to list plugins: {str(e)}")
            raise

    async def get_plugin_info(self, plugin_id: str) -> Dict:
        """Obtém informações detalhadas de um plugin"""
        try:
            if plugin_id not in self.plugins:
                raise PluginError(f"Plugin {plugin_id} not found")
            
            plugin = self.plugins[plugin_id]
            
            # Carrega README se existir
            readme = None
            readme_file = (
                self.plugins_path / plugin['type'] / 
                plugin['name'] / 'README.md'
            )
            if readme_file.exists():
                readme = readme_file.read_text()
            
            return {
                **plugin,
                'readme': readme,
                'hooks': self._get_plugin_hooks(plugin_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get plugin info: {str(e)}")
            raise

    def register_hook(self, hook_name: str, callback: Callable):
        """Registra um hook para um plugin"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    async def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Executa hooks registrados"""
        results = []
        
        if hook_name in self.hooks:
            for hook in self.hooks[hook_name]:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        result = await hook(*args, **kwargs)
                    else:
                        result = hook(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Hook execution failed: {str(e)}")
                    
        return results

    async def _validate_plugin(self, plugin_data: Dict) -> Dict:
        """Valida dados do plugin"""
        errors = []
        
        # Verifica campos obrigatórios
        required_fields = ['name', 'type', 'version']
        for field in required_fields:
            if field not in plugin_data:
                errors.append(f"Missing required field: {field}")
        
        # Verifica tipo do plugin
        if 'type' in plugin_data:
            try:
                PluginType(plugin_data['type'])
            except ValueError:
                errors.append(f"Invalid plugin type: {plugin_data['type']}")
        
        # Verifica versão
        if 'version' in plugin_data:
            if not self._is_valid_version(plugin_data['version']):
                errors.append(f"Invalid version format: {plugin_data['version']}")
        
        # Verifica código python
        if 'code' in plugin_data:
            try:
                compile(plugin_data['code'], '<string>', 'exec')
            except Exception as e:
                errors.append(f"Invalid Python code: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    async def _save_plugin_files(self, plugin_dir: Path, plugin_data: Dict):
        """Salva arquivos do plugin"""
        # Salva código
        if 'code' in plugin_data:
            code_file = plugin_dir / 'plugin.py'
            code_file.write_text(plugin_data['code'])
        
        # Salva configuração
        if 'config' in plugin_data:
            config_file = plugin_dir / 'config.yml'
            with open(config_file, 'w') as f:
                yaml.dump(plugin_data['config'], f)
        
        # Salva README
        if 'readme' in plugin_data:
            readme_file = plugin_dir / 'README.md'
            readme_file.write_text(plugin_data['readme'])

    def _load_installed_plugins(self):
        """Carrega plugins instalados"""
        for plugin_type in PluginType:
            type_dir = self.plugins_path / plugin_type.value
            if not type_dir.exists():
                continue
            
            for plugin_dir in type_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue
                
                try:
                    # Carrega configuração
                    config_file = plugin_dir / 'config.yml'
                    if not config_file.exists():
                        continue
                        
                    with open(config_file) as f:
                        config = yaml.safe_load(f)
                    
                    plugin_id = f"{plugin_dir.name}_{config['version']}"
                    self.plugins[plugin_id] = {
                        'id': plugin_id,
                        'name': plugin_dir.name,
                        'type': plugin_type.value,
                        'version': config['version'],
                        'status': PluginStatus.ENABLED.value,
                        'config': config
                    }
                    
                    # Carrega plugin
                    self._load_plugin(plugin_id)
                    
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {plugin_dir.name}: {str(e)}")

    async def _load_plugin(self, plugin_id: str):
        """Carrega um plugin específico"""
        plugin = self.plugins[plugin_id]
        plugin_dir = self.plugins_path / plugin['type'] / plugin['name']
        
        # Importa módulo do plugin
        spec = importlib.util.spec_from_file_location(
            plugin['name'],
            plugin_dir / 'plugin.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Registra hooks
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '_hook'):
                setattr(obj, '__plugin__', plugin_id)
                self.register_hook(obj._hook, obj)

    def _get_plugin_hooks(self, plugin_id: str) -> List[str]:
        """Obtém hooks registrados por um plugin"""
        plugin_hooks = []
        
        for hook_name, hooks in self.hooks.items():
            for hook in hooks:
                if getattr(hook, '__plugin__', None) == plugin_id:
                    plugin_hooks.append(hook_name)
                    
        return plugin_hooks

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Verifica se versão é válida"""
        try:
            major, minor, patch = version.split('.')
            return all(part.isdigit() for part in [major, minor, patch])
        except:
            return False

class PluginError(Exception):
    pass