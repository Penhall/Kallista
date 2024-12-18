# integrations/backup/backup_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import zipfile
import json
import tempfile

class BackupType(Enum):
    FULL = "full"  # Backup completo
    INCREMENTAL = "incremental"  # Backup de alterações
    DIFFERENTIAL = "differential"  # Backup desde último full

class StorageType(Enum):
    LOCAL = "local"  # Armazenamento local
    GIT = "git"  # Repositório Git
    CLOUD = "cloud"  # Armazenamento em nuvem

class BackupManager:
    def __init__(self, github_client, azure_client, config: Dict):
        self.github = github_client
        self.azure = azure_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backup_path = Path(config.get('backup_path', 'backups'))
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.temp_path = Path(tempfile.gettempdir()) / "backup_temp"
        self.temp_path.mkdir(exist_ok=True)

    async def create_backup(
        self,
        backup_type: BackupType,
        storage_type: StorageType,
        entities: Optional[List[str]] = None
    ) -> Dict:
        """Cria um novo backup"""
        try:
            backup_id = f"backup_{datetime.utcnow().timestamp()}"
            temp_backup_dir = self.temp_path / backup_id
            temp_backup_dir.mkdir(exist_ok=True)

            # Coleta dados para backup
            backup_data = await self._collect_backup_data(
                backup_type,
                entities
            )

            # Salva dados temporariamente
            await self._save_backup_data(
                temp_backup_dir,
                backup_data
            )

            # Armazena backup
            storage_result = await self._store_backup(
                backup_id,
                temp_backup_dir,
                storage_type
            )

            # Limpa arquivos temporários
            shutil.rmtree(temp_backup_dir)

            return {
                'backup_id': backup_id,
                'type': backup_type.value,
                'storage': storage_type.value,
                'timestamp': datetime.utcnow().isoformat(),
                'size': storage_result['size'],
                'location': storage_result['location'],
                'entities': list(backup_data.keys())
            }

        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            if temp_backup_dir.exists():
                shutil.rmtree(temp_backup_dir)
            raise

    async def restore_backup(
        self,
        backup_id: str,
        entities: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict:
        """Restaura dados de um backup"""
        try:
            # Localiza backup
            backup_info = await self._locate_backup(backup_id)
            
            # Prepara diretório temporário
            temp_restore_dir = self.temp_path / f"restore_{backup_id}"
            temp_restore_dir.mkdir(exist_ok=True)

            # Recupera dados do backup
            backup_data = await self._retrieve_backup_data(
                backup_info,
                temp_restore_dir
            )

            if dry_run:
                # Simula restauração
                simulation = await self._simulate_restore(
                    backup_data,
                    entities
                )
                shutil.rmtree(temp_restore_dir)
                return simulation

            # Executa restauração
            restore_results = await self._execute_restore(
                backup_data,
                entities
            )

            # Limpa arquivos temporários
            shutil.rmtree(temp_restore_dir)

            return {
                'backup_id': backup_id,
                'timestamp': datetime.utcnow().isoformat(),
                'restored_entities': restore_results['entities'],
                'status': restore_results['status'],
                'issues': restore_results.get('issues', [])
            }

        except Exception as e:
            self.logger.error(f"Failed to restore backup: {str(e)}")
            if temp_restore_dir.exists():
                shutil.rmtree(temp_restore_dir)
            raise

    async def list_backups(
        self,
        backup_type: Optional[BackupType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Lista backups disponíveis"""
        try:
            backups = []

            # Lista backups locais
            for backup_dir in self.backup_path.glob("*"):
                if not backup_dir.is_dir():
                    continue

                try:
                    # Carrega metadados
                    metadata = self._load_backup_metadata(backup_dir)
                    
                    # Aplica filtros
                    if backup_type and metadata['type'] != backup_type.value:
                        continue
                        
                    backup_date = datetime.fromisoformat(metadata['timestamp'])
                    if start_date and backup_date < start_date:
                        continue
                    if end_date and backup_date > end_date:
                        continue

                    backups.append(metadata)

                except Exception as e:
                    self.logger.warning(f"Failed to load backup metadata: {str(e)}")

            return sorted(
                backups,
                key=lambda x: x['timestamp'],
                reverse=True
            )

        except Exception as e:
            self.logger.error(f"Failed to list backups: {str(e)}")
            raise

    async def verify_backup(self, backup_id: str) -> Dict:
        """Verifica integridade de um backup"""
        try:
            # Localiza backup
            backup_info = await self._locate_backup(backup_id)
            
            # Verifica metadados
            metadata_check = await self._verify_backup_metadata(backup_info)
            
            # Verifica dados
            data_check = await self._verify_backup_data(backup_info)
            
            # Verifica integridade
            integrity_check = await self._verify_backup_integrity(backup_info)

            return {
                'backup_id': backup_id,
                'verified_at': datetime.utcnow().isoformat(),
                'is_valid': all([
                    metadata_check['valid'],
                    data_check['valid'],
                    integrity_check['valid']
                ]),
                'checks': {
                    'metadata': metadata_check,
                    'data': data_check,
                    'integrity': integrity_check
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to verify backup: {str(e)}")
            raise

    async def cleanup_backups(
        self,
        retention_days: Optional[int] = None,
        min_backups: Optional[int] = None
    ) -> Dict:
        """Remove backups antigos"""
        try:
            if not retention_days:
                retention_days = self.config.get('backup_retention_days', 30)
            if not min_backups:
                min_backups = self.config.get('min_backups', 5)

            deletion_cutoff = datetime.utcnow() - timedelta(days=retention_days)
            backups = await self.list_backups()
            
            # Mantém número mínimo de backups
            if len(backups) <= min_backups:
                return {
                    'deleted_backups': 0,
                    'retained_backups': len(backups)
                }

            deleted = 0
            retained = 0

            for backup in backups[min_backups:]:  # Preserva os min_backups mais recentes
                backup_date = datetime.fromisoformat(backup['timestamp'])
                
                if backup_date < deletion_cutoff:
                    # Remove backup
                    await self._delete_backup(backup['backup_id'])
                    deleted += 1
                else:
                    retained += 1

            return {
                'deleted_backups': deleted,
                'retained_backups': retained + min_backups,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to cleanup backups: {str(e)}")
            raise

    async def _collect_backup_data(
        self,
        backup_type: BackupType,
        entities: Optional[List[str]]
    ) -> Dict:
        """Coleta dados para backup"""
        backup_data = {}

        # Determina ponto de início para backup incremental/diferencial
        last_backup = None
        if backup_type in [BackupType.INCREMENTAL, BackupType.DIFFERENTIAL]:
            last_backup = await self._get_last_backup(BackupType.FULL)

        # Coleta dados do GitHub
        github_data = await self._collect_github_data(
            entities,
            last_backup
        )
        backup_data['github'] = github_data

        # Coleta dados do Azure DevOps
        azure_data = await self._collect_azure_data(
            entities,
            last_backup
        )
        backup_data['azure'] = azure_data

        return backup_data

    async def _store_backup(
        self,
        backup_id: str,
        backup_dir: Path,
        storage_type: StorageType
    ) -> Dict:
        """Armazena backup no destino especificado"""
        if storage_type == StorageType.LOCAL:
            return await self._store_local_backup(backup_id, backup_dir)
        elif storage_type == StorageType.GIT:
            return await self._store_git_backup(backup_id, backup_dir)
        elif storage_type == StorageType.CLOUD:
            return await self._store_cloud_backup(backup_id, backup_dir)
        
        raise ValueError(f"Unsupported storage type: {storage_type}")

    def _load_backup_metadata(self, backup_dir: Path) -> Dict:
        """Carrega metadados de um backup"""
        metadata_file = backup_dir / "metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found for backup: {backup_dir}")
            
        with open(metadata_file) as f:
            return json.load(f)

    async def _verify_backup_metadata(self, backup_info: Dict) -> Dict:
        """Verifica metadados do backup"""
        required_fields = ['backup_id', 'type', 'timestamp', 'entities']
        missing_fields = [
            field for field in required_fields
            if field not in backup_info
        ]
        
        return {
            'valid': len(missing_fields) == 0,
            'missing_fields': missing_fields
        }

    async def _verify_backup_data(self, backup_info: Dict) -> Dict:
        """Verifica dados do backup"""
        issues = []
        
        try:
            # Verifica existência dos arquivos
            backup_dir = Path(backup_info['location'])
            for entity in backup_info['entities']:
                entity_file = backup_dir / f"{entity}.json"
                if not entity_file.exists():
                    issues.append(f"Missing data file for entity: {entity}")
                else:
                    # Verifica formato dos dados
                    try:
                        with open(entity_file) as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        issues.append(f"Invalid JSON data for entity: {entity}")
                        
            return {
                'valid': len(issues) == 0,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [str(e)]
            }

    async def _verify_backup_integrity(self, backup_info: Dict) -> Dict:
        """Verifica integridade do backup"""
        try:
            # Verifica checksums
            checksum_file = Path(backup_info['location']) / "checksums.json"
            if not checksum_file.exists():
                return {
                    'valid': False,
                    'issues': ["Checksum file not found"]
                }

            with open(checksum_file) as f:
                stored_checksums = json.load(f)

            current_checksums = await self._calculate_backup_checksums(
                Path(backup_info['location'])
            )

            mismatches = []
            for file, stored_hash in stored_checksums.items():
                if current_checksums.get(file) != stored_hash:
                    mismatches.append(file)

            return {
                'valid': len(mismatches) == 0,
                'mismatched_files': mismatches
            }

        except Exception as e:
            return {
                'valid': False,
                'issues': [str(e)]
            }