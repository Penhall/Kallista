# integrations/performance/cache_manager.py
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import json
import pickle
from pathlib import Path
import aioredis
import hashlib

class CacheStrategy(Enum):
    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"

class CacheManager:
    def __init__(self, config: Dict):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.strategy = CacheStrategy(config.get('strategy', 'memory'))
        self.cache_path = Path(config.get('cache_path', 'cache'))
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Any] = {}
        self._init_cache()

    async def _init_cache(self):
        """Inicializa sistema de cache"""
        try:
            if self.strategy == CacheStrategy.REDIS:
                self.redis = await aioredis.create_redis_pool(
                    self.config['redis_url'],
                    minsize=5,
                    maxsize=10
                )
            
            # Limpa cache expirado
            await self._cleanup_expired_cache()
            
        except Exception as e:
            self.logger.error(f"Cache initialization failed: {str(e)}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Recupera item do cache"""
        try:
            cache_key = self._generate_cache_key(key)
            
            if self.strategy == CacheStrategy.MEMORY:
                return await self._get_from_memory(cache_key)
            elif self.strategy == CacheStrategy.FILE:
                return await self._get_from_file(cache_key)
            elif self.strategy == CacheStrategy.REDIS:
                return await self._get_from_redis(cache_key)
            
        except Exception as e:
            self.logger.error(f"Cache retrieval failed: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena item no cache"""
        try:
            cache_key = self._generate_cache_key(key)
            expiration = datetime.utcnow() + timedelta(seconds=ttl) if ttl else None
            
            if self.strategy == CacheStrategy.MEMORY:
                return await self._set_in_memory(cache_key, value, expiration)
            elif self.strategy == CacheStrategy.FILE:
                return await self._set_in_file(cache_key, value, expiration)
            elif self.strategy == CacheStrategy.REDIS:
                return await self._set_in_redis(cache_key, value, ttl)
            
        except Exception as e:
            self.logger.error(f"Cache storage failed: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove item do cache"""
        try:
            cache_key = self._generate_cache_key(key)
            
            if self.strategy == CacheStrategy.MEMORY:
                return self._delete_from_memory(cache_key)
            elif self.strategy == CacheStrategy.FILE:
                return await self._delete_from_file(cache_key)
            elif self.strategy == CacheStrategy.REDIS:
                return await self._delete_from_redis(cache_key)
            
        except Exception as e:
            self.logger.error(f"Cache deletion failed: {str(e)}")
            return False

    async def clear(self) -> bool:
        """Limpa todo o cache"""
        try:
            if self.strategy == CacheStrategy.MEMORY:
                self.memory_cache.clear()
            elif self.strategy == CacheStrategy.FILE:
                for file in self.cache_path.glob("*.cache"):
                    file.unlink()
            elif self.strategy == CacheStrategy.REDIS:
                await self.redis.flushdb()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache clear failed: {str(e)}")
            return False

    def _generate_cache_key(self, key: str) -> str:
        """Gera chave de cache"""
        return hashlib.md5(key.encode()).hexdigest()

    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """Recupera item do cache em memória"""
        if key not in self.memory_cache:
            return None
            
        item = self.memory_cache[key]
        
        # Verifica expiração
        if item.get('expiration'):
            if datetime.utcnow() > item['expiration']:
                del self.memory_cache[key]
                return None
                
        return item['value']

    async def _get_from_file(self, key: str) -> Optional[Any]:
        """Recupera item do cache em arquivo"""
        cache_file = self.cache_path / f"{key}.cache"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'rb') as f:
                item = pickle.load(f)
                
            # Verifica expiração
            if item.get('expiration'):
                if datetime.utcnow() > item['expiration']:
                    cache_file.unlink()
                    return None
                    
            return item['value']
            
        except Exception:
            return None

    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Recupera item do cache Redis"""
        value = await self.redis.get(key)
        
        if value is None:
            return None
            
        return pickle.loads(value)

    async def _set_in_memory(self, key: str, value: Any, expiration: Optional[datetime]) -> bool:
        """Armazena item no cache em memória"""
        self.memory_cache[key] = {
            'value': value,
            'expiration': expiration
        }
        return True

    async def _set_in_file(self, key: str, value: Any, expiration: Optional[datetime]) -> bool:
        """Armazena item no cache em arquivo"""
        cache_file = self.cache_path / f"{key}.cache"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'value': value,
                    'expiration': expiration
                }, f)
            return True
        except Exception:
            return False

    async def _set_in_redis(self, key: str, value: Any, ttl: Optional[int]) -> bool:
        """Armazena item no cache Redis"""
        try:
            value_bytes = pickle.dumps(value)
            
            if ttl:
                await self.redis.setex(key, ttl, value_bytes)
            else:
                await self.redis.set(key, value_bytes)
                
            return True
        except Exception:
            return False

    def _delete_from_memory(self, key: str) -> bool:
        """Remove item do cache em memória"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            return True
        return False

    async def _delete_from_file(self, key: str) -> bool:
        """Remove item do cache em arquivo"""
        cache_file = self.cache_path / f"{key}.cache"
        
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    async def _delete_from_redis(self, key: str) -> bool:
        """Remove item do cache Redis"""
        deleted = await self.redis.delete(key)
        return deleted > 0

    async def _cleanup_expired_cache(self):
        """Limpa itens expirados do cache"""
        try:
            if self.strategy == CacheStrategy.MEMORY:
                # Limpa cache em memória
                expired_keys = [
                    key for key, item in self.memory_cache.items()
                    if item.get('expiration') and datetime.utcnow() > item['expiration']
                ]
                
                for key in expired_keys:
                    del self.memory_cache[key]
                    
            elif self.strategy == CacheStrategy.FILE:
                # Limpa cache em arquivo
                for cache_file in self.cache_path.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            item = pickle.load(f)
                            
                        if item.get('expiration') and datetime.utcnow() > item['expiration']:
                            cache_file.unlink()
                    except Exception:
                        cache_file.unlink()
                        
            # Redis gerencia automaticamente a expiração
                
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {str(e)}")