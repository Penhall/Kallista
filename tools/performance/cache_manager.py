# tools/performance/cache_manager.py
from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import threading
import time
from collections import OrderedDict
import pickle

class CacheManager:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.cache = OrderedDict()
        self.metadata = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        self.lock = threading.Lock()
        self._load_config()
        self._start_maintenance_task()

    def _load_config(self) -> None:
        """Carrega configuração do cache"""
        try:
            config_path = Path("config/performance/cache_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    self.config.update(json.load(f))
        except Exception as e:
            self.logger.error(f"Failed to load cache config: {str(e)}")

        # Configurações padrão
        self.config.setdefault('max_size', 1000)  # Número máximo de itens
        self.config.setdefault('max_memory', 100 * 1024 * 1024)  # 100MB
        self.config.setdefault('ttl', 3600)  # 1 hora em segundos
        self.config.setdefault('eviction_policy', 'lru')  # least recently used
        self.config.setdefault('persistent', False)  # Cache persistente

    def _start_maintenance_task(self) -> None:
        """Inicia tarefa de manutenção do cache"""
        maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True
        )
        maintenance_thread.start()

  # tools/performance/cache_manager.py (continuação)
    def _maintenance_loop(self) -> None:
        """Loop de manutenção do cache"""
        while True:
            try:
                # Remove itens expirados
                self._remove_expired()
                
                # Verifica limites de memória
                self._check_memory_limits()
                
                # Persiste cache se necessário
                if self.config['persistent']:
                    self._persist_cache()
                    
                # Aguarda próxima execução
                time.sleep(60)  # Executa a cada minuto
                
            except Exception as e:
                self.logger.error(f"Cache maintenance failed: {str(e)}")
                time.sleep(60)  # Aguarda mesmo em caso de erro

    async def get(self, key: str) -> Optional[Any]:
        """Obtém item do cache"""
        with self.lock:
            try:
                if key not in self.cache:
                    self.stats['misses'] += 1
                    return None

                value = self.cache[key]
                metadata = self.metadata[key]

                # Verifica expiração
                if self._is_expired(metadata):
                    self._remove_item(key)
                    self.stats['misses'] += 1
                    return None

                # Atualiza metadata para LRU
                metadata['last_access'] = datetime.utcnow()
                self.cache.move_to_end(key)
                self.stats['hits'] += 1

                return value

            except Exception as e:
                self.logger.error(f"Cache get failed for key {key}: {str(e)}")
                return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Adiciona item ao cache"""
        with self.lock:
            try:
                # Verifica limites antes de adicionar
                if len(self.cache) >= self.config['max_size']:
                    self._evict()

                # Define TTL
                if ttl is None:
                    ttl = self.config['ttl']

                # Adiciona ao cache
                self.cache[key] = value
                self.metadata[key] = {
                    'created_at': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(seconds=ttl),
                    'last_access': datetime.utcnow(),
                    'size': self._get_size(value)
                }

                # Move para o fim (LRU)
                self.cache.move_to_end(key)

                return True

            except Exception as e:
                self.logger.error(f"Cache set failed for key {key}: {str(e)}")
                return False

    async def delete(self, key: str) -> bool:
        """Remove item do cache"""
        with self.lock:
            try:
                return self._remove_item(key)
            except Exception as e:
                self.logger.error(f"Cache delete failed for key {key}: {str(e)}")
                return False

    async def clear(self) -> bool:
        """Limpa todo o cache"""
        with self.lock:
            try:
                self.cache.clear()
                self.metadata.clear()
                self.stats = {
                    'hits': 0,
                    'misses': 0,
                    'evictions': 0
                }
                return True
            except Exception as e:
                self.logger.error(f"Cache clear failed: {str(e)}")
                return False

    async def get_stats(self) -> Dict:
        """Obtém estatísticas do cache"""
        with self.lock:
            total_size = sum(
                meta['size'] for meta in self.metadata.values()
            )
            
            return {
                'size': len(self.cache),
                'memory_usage': total_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_ratio': self._calculate_hit_ratio(),
                'evictions': self.stats['evictions'],
                'oldest_item': self._get_oldest_item_age(),
                'newest_item': self._get_newest_item_age()
            }

    def _is_expired(self, metadata: Dict) -> bool:
        """Verifica se um item expirou"""
        return datetime.utcnow() > metadata['expires_at']

    def _remove_expired(self) -> None:
        """Remove todos os itens expirados"""
        with self.lock:
            expired_keys = [
                key for key, meta in self.metadata.items()
                if self._is_expired(meta)
            ]
            
            for key in expired_keys:
                self._remove_item(key)

    def _check_memory_limits(self) -> None:
        """Verifica e ajusta limites de memória"""
        with self.lock:
            total_size = sum(
                meta['size'] for meta in self.metadata.values()
            )
            
            while total_size > self.config['max_memory']:
                if not self.cache:
                    break
                    
                # Remove item mais antigo
                self._evict()
                
                total_size = sum(
                    meta['size'] for meta in self.metadata.values()
                )

    def _evict(self) -> None:
        """Remove item baseado na política de evicção"""
        if not self.cache:
            return

        if self.config['eviction_policy'] == 'lru':
            # Remove o primeiro item (menos recentemente usado)
            key, _ = self.cache.popitem(last=False)
            del self.metadata[key]
            self.stats['evictions'] += 1
            
        elif self.config['eviction_policy'] == 'largest':
            # Remove o maior item
            largest_key = max(
                self.metadata.items(),
                key=lambda x: x[1]['size']
            )[0]
            self._remove_item(largest_key)
            self.stats['evictions'] += 1

    def _remove_item(self, key: str) -> bool:
        """Remove um item específico do cache"""
        if key in self.cache:
            del self.cache[key]
            del self.metadata[key]
            return True
        return False

    def _get_size(self, value: Any) -> int:
        """Calcula tamanho aproximado de um valor"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return sys.getsizeof(value)

    def _calculate_hit_ratio(self) -> float:
        """Calcula taxa de acertos do cache"""
        total = self.stats['hits'] + self.stats['misses']
        if total == 0:
            return 0.0
        return self.stats['hits'] / total * 100

    def _get_oldest_item_age(self) -> Optional[timedelta]:
        """Obtém idade do item mais antigo"""
        if not self.metadata:
            return None
            
        oldest = min(
            (m['created_at'] for m in self.metadata.values()),
            default=None
        )
        
        if oldest:
            return datetime.utcnow() - oldest
        return None

    def _get_newest_item_age(self) -> Optional[timedelta]:
        """Obtém idade do item mais novo"""
        if not self.metadata:
            return None
            
        newest = max(
            (m['created_at'] for m in self.metadata.values()),
            default=None
        )
        
        if newest:
            return datetime.utcnow() - newest
        return None

    def _persist_cache(self) -> None:
        """Persiste cache em disco"""
        if not self.config['persistent']:
            return

        try:
            cache_dir = Path("data/cache")
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Salva dados do cache
            cache_file = cache_dir / "cache.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
                
            # Salva metadata
            metadata_file = cache_dir / "metadata.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
                
            # Salva estatísticas
            stats_file = cache_dir / "stats.json"
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f)
                
        except Exception as e:
            self.logger.error(f"Cache persistence failed: {str(e)}")

    def _load_persistent_cache(self) -> None:
        """Carrega cache persistente"""
        if not self.config['persistent']:
            return

        try:
            cache_dir = Path("data/cache")
            
            # Carrega dados do cache
            cache_file = cache_dir / "cache.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                    
            # Carrega metadata
            metadata_file = cache_dir / "metadata.pkl"
            if metadata_file.exists():
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                    
            # Carrega estatísticas
            stats_file = cache_dir / "stats.json"
            if stats_file.exists():
                with open(stats_file) as f:
                    self.stats = json.load(f)
                    
        except Exception as e:
            self.logger.error(f"Failed to load persistent cache: {str(e)}")
            # Reinicia cache em caso de erro
            self.cache = OrderedDict()
            self.metadata = {}