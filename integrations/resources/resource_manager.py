# integrations/resources/resource_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import psutil
import os
import shutil
import tempfile
import aiofiles
import multiprocessing

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    THREAD = "thread"

class ResourcePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResourceManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_path = Path(tempfile.gettempdir()) / "kallista"
        self.temp_path.mkdir(exist_ok=True)
        
        # Configurações de recursos
        self.max_threads = config.get('max_threads', multiprocessing.cpu_count())
        self.max_memory = config.get('max_memory', psutil.virtual_memory().total * 0.8)
        self.min_disk_space = config.get('min_disk_space', 1024 * 1024 * 1024)  # 1GB
        
        # Pools de recursos
        self.thread_pool = asyncio.Semaphore(self.max_threads)
        self.active_resources: Dict[str, Dict] = {}

    async def allocate_resource(
        self,
        resource_type: ResourceType,
        amount: Optional[int] = None,
        priority: ResourcePriority = ResourcePriority.MEDIUM
    ) -> Dict:
        """Aloca recursos do sistema"""
        try:
            resource_id = f"{resource_type.value}_{datetime.utcnow().timestamp()}"
            
            # Verifica disponibilidade
            if not await self._check_resource_availability(resource_type, amount):
                raise ResourceError(f"Insufficient {resource_type.value} resources")
            
            # Aloca recurso
            allocation = await self._allocate_specific_resource(
                resource_type,
                amount,
                priority
            )
            
            # Registra alocação
            self.active_resources[resource_id] = {
                'type': resource_type.value,
                'amount': amount,
                'priority': priority.value,
                'allocated_at': datetime.utcnow().isoformat(),
                'allocation': allocation
            }
            
            return {
                'resource_id': resource_id,
                'allocation': allocation,
                'status': 'allocated'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to allocate resource: {str(e)}")
            raise

    async def release_resource(self, resource_id: str) -> Dict:
        """Libera recursos alocados"""
        try:
            if resource_id not in self.active_resources:
                raise ResourceError(f"Resource {resource_id} not found")
            
            resource = self.active_resources[resource_id]
            
            # Libera recurso
            await self._release_specific_resource(
                ResourceType(resource['type']),
                resource['allocation']
            )
            
            # Remove registro
            del self.active_resources[resource_id]
            
            return {
                'resource_id': resource_id,
                'status': 'released'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to release resource: {str(e)}")
            raise

    async def optimize_resources(self) -> Dict:
        """Otimiza uso de recursos"""
        try:
            optimizations = {
                'cpu': await self._optimize_cpu(),
                'memory': await self._optimize_memory(),
                'disk': await self._optimize_disk(),
                'thread': await self._optimize_threads()
            }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'optimizations': optimizations
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize resources: {str(e)}")
            raise

    async def get_resource_usage(self) -> Dict:
        """Obtém uso atual dos recursos"""
        try:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': psutil.cpu_percent(),
                    'count': psutil.cpu_count(),
                    'load': os.getloadavg()
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'thread': {
                    'active': len(self.active_resources),
                    'max': self.max_threads
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {str(e)}")
            raise

    async def _check_resource_availability(
        self,
        resource_type: ResourceType,
        amount: Optional[int]
    ) -> bool:
        """Verifica disponibilidade de recursos"""
        if resource_type == ResourceType.CPU:
            return psutil.cpu_percent() < self.config.get('cpu_threshold', 80)
            
        elif resource_type == ResourceType.MEMORY:
            if amount:
                return psutil.virtual_memory().available >= amount
            return psutil.virtual_memory().percent < self.config.get('memory_threshold', 80)
            
        elif resource_type == ResourceType.DISK:
            if amount:
                return psutil.disk_usage('/').free >= amount
            return psutil.disk_usage('/').percent < self.config.get('disk_threshold', 80)
            
        elif resource_type == ResourceType.THREAD:
            return len(self.active_resources) < self.max_threads
            
        return False

    async def _allocate_specific_resource(
        self,
        resource_type: ResourceType,
        amount: Optional[int],
        priority: ResourcePriority
    ) -> Any:
        """Aloca um recurso específico"""
        if resource_type == ResourceType.THREAD:
            await self.thread_pool.acquire()
            return {'thread_id': len(self.active_resources) + 1}
            
        elif resource_type == ResourceType.MEMORY:
            # Aloca memória temporária
            return await self._allocate_temp_memory(amount)
            
        elif resource_type == ResourceType.DISK:
            # Aloca espaço em disco temporário
            return await self._allocate_temp_disk(amount)
            
        return None

    async def _release_specific_resource(
        self,
        resource_type: ResourceType,
        allocation: Any
    ):
        """Libera um recurso específico"""
        if resource_type == ResourceType.THREAD:
            self.thread_pool.release()
            
        elif resource_type == ResourceType.MEMORY:
            # Libera memória temporária
            await self._release_temp_memory(allocation)
            
        elif resource_type == ResourceType.DISK:
            # Libera espaço em disco temporário
            await self._release_temp_disk(allocation)

    async def _optimize_cpu(self) -> Dict:
        """Otimiza uso de CPU"""
        optimizations = []
        
        # Verifica processos consumindo muita CPU
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > self.config.get('cpu_process_threshold', 50):
                    # Ajusta prioridade do processo
                    proc.nice(19)  # Menor prioridade
                    optimizations.append({
                        'process': proc.info['name'],
                        'action': 'reduced_priority',
                        'original_cpu': proc.info['cpu_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return {
            'type': 'cpu',
            'optimizations': optimizations
        }

    async def _optimize_memory(self) -> Dict:
        """Otimiza uso de memória"""
        optimizations = []
        
        # Limpa cache de sistema se necessário
        if psutil.virtual_memory().percent > self.config.get('memory_threshold', 80):
            if os.name == 'posix':
                os.system('sync; echo 3 > /proc/sys/vm/drop_caches')
                optimizations.append({
                    'action': 'cleared_system_cache',
                    'saved': 'unknown'
                })
        
        # Limpa arquivos temporários
        temp_size = await self._clean_temp_files()
        if temp_size > 0:
            optimizations.append({
                'action': 'cleared_temp_files',
                'saved': temp_size
            })
            
        return {
            'type': 'memory',
            'optimizations': optimizations
        }

    async def _optimize_disk(self) -> Dict:
        """Otimiza uso de disco"""
        optimizations = []
        
        # Limpa arquivos antigos
        cleaned = await self._clean_old_files()
        if cleaned > 0:
            optimizations.append({
                'action': 'removed_old_files',
                'saved': cleaned
            })
        
        # Compacta logs antigos
        compressed = await self._compress_old_logs()
        if compressed > 0:
            optimizations.append({
                'action': 'compressed_logs',
                'saved': compressed
            })
            
        return {
            'type': 'disk',
            'optimizations': optimizations
        }

    async def _optimize_threads(self) -> Dict:
        """Otimiza uso de threads"""
        optimizations = []
        
        # Verifica threads ociosas
        idle_count = 0
        for resource_id, resource in list(self.active_resources.items()):
            if resource['type'] == ResourceType.THREAD.value:
                # Verifica última atividade
                last_active = datetime.fromisoformat(resource['allocated_at'])
                if datetime.utcnow() - last_active > timedelta(minutes=30):
                    await self.release_resource(resource_id)
                    idle_count += 1
                    
        if idle_count > 0:
            optimizations.append({
                'action': 'released_idle_threads',
                'count': idle_count
            })
            
        return {
            'type': 'thread',
            'optimizations': optimizations
        }

    async def _clean_temp_files(self) -> int:
        """Limpa arquivos temporários"""
        total_size = 0
        
        for file in self.temp_path.glob('*'):
            if file.is_file():
                total_size += file.stat().st_size
                file.unlink()
                
        return total_size

    async def _clean_old_files(self) -> int:
        """Remove arquivos antigos"""
        total_size = 0
        max_age = timedelta(days=self.config.get('max_file_age', 30))
        
        for root, _, files in os.walk(self.temp_path):
            for file in files:
                file_path = Path(root) / file
                if datetime.fromtimestamp(file_path.stat().st_mtime) < datetime.now() - max_age:
                    total_size += file_path.stat().st_size
                    file_path.unlink()
                    
        return total_size

    async def _compress_old_logs(self) -> int:
        """Compacta logs antigos"""
        total_saved = 0
        logs_path = Path(self.config.get('log_path', 'logs'))
        
        if not logs_path.exists():
            return 0
            
        for log_file in logs_path.glob('*.log'):
            if log_file.stat().st_mtime < (datetime.now() - timedelta(days=7)).timestamp():
                original_size = log_file.stat().st_size
                
                # Compacta arquivo
                shutil.make_archive(
                    str(log_file),
                    'gzip',
                    root_dir=str(logs_path),
                    base_dir=log_file.name
                )
                
                # Remove arquivo original
                log_file.unlink()
                
                # Calcula espaço economizado
                compressed_size = (log_file.parent / f"{log_file.name}.gz").stat().st_size
                total_saved += original_size - compressed_size
                
        return total_saved

class ResourceError(Exception):
    pass