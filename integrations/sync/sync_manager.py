# integrations/sync/sync_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

class SyncDirection(Enum):
    GITHUB_TO_AZURE = "github_to_azure"
    AZURE_TO_GITHUB = "azure_to_github"
    BIDIRECTIONAL = "bidirectional"

class SyncEntityType(Enum):
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    COMMENT = "comment"
    COMMIT = "commit"
    WIKI = "wiki"
    RELEASE = "release"

class SyncManager:
    def __init__(self, github_client, azure_client, config: Dict):
        self.github = github_client
        self.azure = azure_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sync_path = Path(config.get('sync_path', 'sync'))
        self.sync_path.mkdir(parents=True, exist_ok=True)
        
        self.sync_cache: Dict[str, Dict] = {}
        self.sync_locks: Dict[str, asyncio.Lock] = {}
        self._init_sync_system()

    def _init_sync_system(self):
        """Inicializa sistema de sincronização"""
        try:
            # Carrega mapeamentos existentes
            self._load_sync_mappings()
            
            # Cria diretórios para cada tipo de entidade
            for entity_type in SyncEntityType:
                (self.sync_path / entity_type.value).mkdir(exist_ok=True)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize sync system: {str(e)}")
            raise

    async def sync_entity(
        self,
        entity_type: SyncEntityType,
        entity_id: str,
        direction: SyncDirection,
        force: bool = False
    ) -> Dict:
        """Sincroniza uma entidade específica"""
        try:
            # Adquire lock para a entidade
            lock = self._get_entity_lock(entity_type, entity_id)
            async with lock:
                # Verifica se sincronização é necessária
                if not force and not await self._needs_sync(entity_type, entity_id):
                    return {
                        'entity_id': entity_id,
                        'type': entity_type.value,
                        'status': 'no_sync_needed'
                    }
                
                # Realiza sincronização
                if direction == SyncDirection.GITHUB_TO_AZURE:
                    result = await self._sync_to_azure(entity_type, entity_id)
                elif direction == SyncDirection.AZURE_TO_GITHUB:
                    result = await self._sync_to_github(entity_type, entity_id)
                else:  # BIDIRECTIONAL
                    result = await self._sync_bidirectional(entity_type, entity_id)
                
                # Atualiza cache
                await self._update_sync_cache(entity_type, entity_id, result)
                
                return {
                    'entity_id': entity_id,
                    'type': entity_type.value,
                    'direction': direction.value,
                    'status': 'synced',
                    'timestamp': datetime.utcnow().isoformat(),
                    'result': result
                }
            
        except Exception as e:
            self.logger.error(f"Failed to sync entity: {str(e)}")
            raise

    async def bulk_sync(
        self,
        entity_type: SyncEntityType,
        direction: SyncDirection,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Realiza sincronização em massa"""
        try:
            start_time = datetime.utcnow()
            results = []
            
            # Obtém entidades para sincronização
            entities = await self._get_entities_for_sync(entity_type, filters)
            
            # Executa sincronização para cada entidade
            for entity in entities:
                try:
                    result = await self.sync_entity(
                        entity_type,
                        entity['id'],
                        direction
                    )
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to sync entity {entity['id']}: {str(e)}")
                    results.append({
                        'entity_id': entity['id'],
                        'type': entity_type.value,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return {
                'type': entity_type.value,
                'direction': direction.value,
                'total_entities': len(entities),
                'successful_syncs': len([r for r in results if r['status'] == 'synced']),
                'failed_syncs': len([r for r in results if r['status'] == 'failed']),
                'skipped_syncs': len([r for r in results if r['status'] == 'no_sync_needed']),
                'start_time': start_time.isoformat(),
                'end_time': datetime.utcnow().isoformat(),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to perform bulk sync: {str(e)}")
            raise

    async def verify_sync(
        self,
        entity_type: SyncEntityType,
        entity_id: str
    ) -> Dict:
        """Verifica estado de sincronização de uma entidade"""
        try:
            # Obtém dados do GitHub
            github_data = await self._get_github_entity(entity_type, entity_id)
            
            # Obtém dados do Azure DevOps
            azure_data = await self._get_azure_entity(entity_type, entity_id)
            
            # Compara dados
            comparison = await self._compare_entities(
                entity_type,
                github_data,
                azure_data
            )
            
            return {
                'entity_id': entity_id,
                'type': entity_type.value,
                'github_hash': self._calculate_hash(github_data),
                'azure_hash': self._calculate_hash(azure_data),
                'is_synced': comparison['is_synced'],
                'differences': comparison['differences'],
                'last_sync': self._get_last_sync(entity_type, entity_id),
                'verification_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to verify sync: {str(e)}")
            raise

    async def resolve_conflict(
        self,
        entity_type: SyncEntityType,
        entity_id: str,
        resolution: Dict
    ) -> Dict:
        """Resolve conflito de sincronização"""
        try:
            # Verifica estado atual
            sync_state = await self.verify_sync(entity_type, entity_id)
            
            if sync_state['is_synced']:
                return {
                    'entity_id': entity_id,
                    'type': entity_type.value,
                    'status': 'no_conflict'
                }
            
            # Aplica resolução
            if resolution.get('source') == 'github':
                await self._sync_to_azure(entity_type, entity_id)
            else:
                await self._sync_to_github(entity_type, entity_id)
            
            # Verifica resultado
            final_state = await self.verify_sync(entity_type, entity_id)
            
            return {
                'entity_id': entity_id,
                'type': entity_type.value,
                'status': 'resolved' if final_state['is_synced'] else 'failed',
                'resolution': resolution,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to resolve conflict: {str(e)}")
            raise

    def _get_entity_lock(self, entity_type: SyncEntityType, entity_id: str) -> asyncio.Lock:
        """Obtém ou cria lock para uma entidade"""
        lock_key = f"{entity_type.value}_{entity_id}"
        if lock_key not in self.sync_locks:
            self.sync_locks[lock_key] = asyncio.Lock()
        return self.sync_locks[lock_key]

    @staticmethod
    def _calculate_hash(data: Dict) -> str:
        """Calcula hash dos dados de uma entidade"""
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

    def _get_last_sync(
        self,
        entity_type: SyncEntityType,
        entity_id: str
    ) -> Optional[datetime]:
        """Obtém timestamp da última sincronização"""
        cache_key = f"{entity_type.value}_{entity_id}"
        if cache_key in self.sync_cache:
            return datetime.fromisoformat(
                self.sync_cache[cache_key]['last_sync']
            )
        return None

    async def _needs_sync(
        self,
        entity_type: SyncEntityType,
        entity_id: str
    ) -> bool:
        """Verifica se sincronização é necessária"""
        try:
            # Verifica última sincronização
            last_sync = self._get_last_sync(entity_type, entity_id)
            if not last_sync:
                return True
            
            # Verifica alterações desde última sincronização
            sync_state = await self.verify_sync(entity_type, entity_id)
            return not sync_state['is_synced']
            
        except Exception:
            return True

    async def _compare_entities(
        self,
        entity_type: SyncEntityType,
        github_data: Dict,
        azure_data: Dict
    ) -> Dict:
        """Compara entidades do GitHub e Azure DevOps"""
        differences = []
        
        # Compara campos relevantes baseado no tipo
        fields = self._get_comparable_fields(entity_type)
        
        for field in fields:
            github_value = github_data.get(field)
            azure_value = azure_data.get(field)
            
            if github_value != azure_value:
                differences.append({
                    'field': field,
                    'github_value': github_value,
                    'azure_value': azure_value
                })
        
        return {
            'is_synced': len(differences) == 0,
            'differences': differences
        }

    def _get_comparable_fields(self, entity_type: SyncEntityType) -> List[str]:
        """Obtém campos comparáveis por tipo de entidade"""
        if entity_type == SyncEntityType.ISSUE:
            return ['title', 'description', 'state', 'labels', 'assignees']
        elif entity_type == SyncEntityType.PULL_REQUEST:
            return ['title', 'description', 'state', 'reviewers', 'labels']
        elif entity_type == SyncEntityType.COMMENT:
            return ['content', 'author', 'created_at']
        elif entity_type == SyncEntityType.COMMIT:
            return ['message', 'author', 'changes']
        elif entity_type == SyncEntityType.WIKI:
            return ['content', 'author', 'updated_at']
        elif entity_type == SyncEntityType.RELEASE:
            return ['name', 'description', 'tag_name', 'assets']
        return []