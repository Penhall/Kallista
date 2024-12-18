# integrations/config/config_manager.py
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import yaml
import logging
from datetime import datetime
import keyring
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigManager:
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.config_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._init_crypto()

    def _init_crypto(self):
        """Inicializa sistema de criptografia"""
        # Gera ou carrega chave
        try:
            key = keyring.get_password("kallista", "crypto_key")
            if not key:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'kallista_salt',  # Em produção, usar salt seguro e único
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(b"kallista_key"))  # Em produção, usar chave segura
                keyring.set_password("kallista", "crypto_key", key.decode())
            self.cipher_suite = Fernet(key if isinstance(key, bytes) else key.encode())
        except Exception as e:
            self.logger.error(f"Failed to initialize crypto: {str(e)}")
            raise

    async def save_config(self, config: Dict, name: str, encrypt: bool = False) -> Dict:
        """Salva configuração em arquivo"""
        try:
            config_file = self.config_path / f"{name}.{'enc' if encrypt else 'yml'}"
            
            # Adiciona metadados
            config_with_meta = {
                'metadata': {
                    'name': name,
                    'created_at': datetime.utcnow().isoformat(),
                    'encrypted': encrypt
                },
                'config': config
            }

            # Encripta se necessário
            if encrypt:
                encrypted_data = self.cipher_suite.encrypt(
                    json.dumps(config_with_meta).encode()
                )
                config_file.write_bytes(encrypted_data)
            else:
                with open(config_file, 'w') as f:
                    yaml.safe_dump(config_with_meta, f)

            self.logger.info(f"Configuration saved: {name}")
            return config_with_meta

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            raise

    async def load_config(self, name: str) -> Dict:
        """Carrega configuração de arquivo"""
        try:
            # Tenta primeiro arquivo encriptado
            enc_file = self.config_path / f"{name}.enc"
            if enc_file.exists():
                encrypted_data = enc_file.read_bytes()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                return json.loads(decrypted_data)

            # Se não encontrar, tenta arquivo yaml
            yaml_file = self.config_path / f"{name}.yml"
            if yaml_file.exists():
                with open(yaml_file, 'r') as f:
                    return yaml.safe_load(f)

            raise FileNotFoundError(f"Configuration not found: {name}")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

    async def store_credentials(self, service: str, credentials: Dict) -> Dict:
        """Armazena credenciais de forma segura"""
        try:
            # Encripta credenciais
            encrypted_creds = {
                key: self.cipher_suite.encrypt(str(value).encode()).decode()
                for key, value in credentials.items()
            }

            # Salva no sistema
            keyring.set_password(
                "kallista_credentials",
                service,
                json.dumps(encrypted_creds)
            )

            return {
                'service': service,
                'stored_at': datetime.utcnow().isoformat(),
                'status': 'stored'
            }

        except Exception as e:
            self.logger.error(f"Failed to store credentials: {str(e)}")
            raise

    async def get_credentials(self, service: str) -> Dict:
        """Recupera credenciais armazenadas"""
        try:
            # Recupera credenciais encriptadas
            encrypted_creds = keyring.get_password("kallista_credentials", service)
            if not encrypted_creds:
                raise KeyError(f"Credentials not found for service: {service}")

            # Decripta credenciais
            encrypted_dict = json.loads(encrypted_creds)
            decrypted_creds = {
                key: self.cipher_suite.decrypt(value.encode()).decode()
                for key, value in encrypted_dict.items()
            }

            return decrypted_creds

        except Exception as e:
            self.logger.error(f"Failed to get credentials: {str(e)}")
            raise

    async def validate_config(self, config: Dict, schema: Dict) -> Dict:
        """Valida configuração contra um schema"""
        try:
            validation_results = {
                'valid': True,
                'errors': []
            }

            # Valida campos obrigatórios
            for field in schema.get('required', []):
                if field not in config:
                    validation_results['valid'] = False
                    validation_results['errors'].append(
                        f"Missing required field: {field}"
                    )

            # Valida tipos
            for field, field_type in schema.get('types', {}).items():
                if field in config and not isinstance(config[field], field_type):
                    validation_results['valid'] = False
                    validation_results['errors'].append(
                        f"Invalid type for field {field}: expected {field_type.__name__}"
                    )

            # Valida valores permitidos
            for field, allowed_values in schema.get('allowed_values', {}).items():
                if field in config and config[field] not in allowed_values:
                    validation_results['valid'] = False
                    validation_results['errors'].append(
                        f"Invalid value for field {field}: must be one of {allowed_values}"
                    )

            return validation_results

        except Exception as e:
            self.logger.error(f"Failed to validate configuration: {str(e)}")
            raise

    async def merge_configs(self, configs: List[Dict]) -> Dict:
        """Mescla múltiplas configurações"""
        try:
            merged_config = {}

            for config in configs:
                self._deep_merge(merged_config, config)

            return merged_config

        except Exception as e:
            self.logger.error(f"Failed to merge configurations: {str(e)}")
            raise

    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """Realiza merge profundo de dicionários"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    async def create_config_backup(self, name: str) -> Dict:
        """Cria backup de configuração"""
        try:
            config = await self.load_config(name)
            
            # Cria nome do backup
            backup_name = f"{name}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Salva backup
            backup_result = await self.save_config(
                config['config'],
                backup_name,
                encrypt=config['metadata'].get('encrypted', False)
            )

            return {
                'original_config': name,
                'backup_name': backup_name,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'backed_up'
            }

        except Exception as e:
            self.logger.error(f"Failed to create config backup: {str(e)}")
            raise

    async def rotate_credentials(self, service: str) -> Dict:
        """Rotaciona credenciais"""
        try:
            # Recupera credenciais atuais
            current_creds = await self.get_credentials(service)

            # Implementar lógica de rotação específica para cada serviço
            new_creds = await self._generate_new_credentials(service, current_creds)

            # Armazena novas credenciais
            await self.store_credentials(service, new_creds)

            return {
                'service': service,
                'rotated_at': datetime.utcnow().isoformat(),
                'status': 'rotated'
            }

        except Exception as e:
            self.logger.error(f"Failed to rotate credentials: {str(e)}")
            raise

    async def _generate_new_credentials(self, service: str, current_creds: Dict) -> Dict:
        """Gera novas credenciais"""
        # Implementar lógica específica para cada serviço
        raise NotImplementedError("Credential rotation not implemented for this service")