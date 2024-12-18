# integrations/nuget/feed_manager.py
from typing import Dict, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json
import shutil
import hashlib
import aiohttp
import xml.etree.ElementTree as ET

class FeedType(Enum):
    PUBLIC = "public"      # Feed público (nuget.org)
    PRIVATE = "private"    # Feed privado
    LOCAL = "local"        # Feed local
    MIRROR = "mirror"      # Espelho de outro feed

class FeedManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.feeds_path = Path(config.get('feeds_path', 'feeds'))
        self.feeds_path.mkdir(parents=True, exist_ok=True)
        self.feeds_config_file = self.feeds_path / "feeds.json"
        self._load_feeds_config()

    def _load_feeds_config(self):
        """Carrega configuração dos feeds"""
        if self.feeds_config_file.exists():
            with open(self.feeds_config_file) as f:
                self.feeds = json.load(f)
        else:
            self.feeds = {
                'public': {
                    'url': 'https://api.nuget.org/v3/index.json',
                    'type': FeedType.PUBLIC.value,
                    'enabled': True
                }
            }
            self._save_feeds_config()

    def _save_feeds_config(self):
        """Salva configuração dos feeds"""
        with open(self.feeds_config_file, 'w') as f:
            json.dump(self.feeds, f, indent=2)

    async def register_feed(
        self,
        name: str,
        url: str,
        feed_type: FeedType,
        credentials: Optional[Dict] = None
    ) -> Dict:
        """Registra um novo feed"""
        try:
            if name in self.feeds:
                raise ValueError(f"Feed {name} already exists")

            # Valida URL do feed
            if feed_type != FeedType.LOCAL:
                await self._validate_feed_url(url)

            # Configura feed
            feed_config = {
                'url': url,
                'type': feed_type.value,
                'enabled': True,
                'registered_at': datetime.utcnow().isoformat()
            }

            if credentials:
                # Armazena credenciais de forma segura
                feed_config['credentials_id'] = await self._store_credentials(
                    name,
                    credentials
                )

            self.feeds[name] = feed_config
            self._save_feeds_config()

            return {
                'name': name,
                'config': feed_config
            }

        except Exception as e:
            self.logger.error(f"Failed to register feed: {str(e)}")
            raise

    async def list_feeds(self, include_disabled: bool = False) -> List[Dict]:
        """Lista feeds registrados"""
        feeds = []
        for name, config in self.feeds.items():
            if not config.get('enabled') and not include_disabled:
                continue
            feeds.append({
                'name': name,
                'url': config['url'],
                'type': config['type'],
                'enabled': config.get('enabled', True),
                'packages': await self._count_feed_packages(name)
            })
        return feeds

    async def get_feed_info(self, name: str) -> Dict:
        """Obtém informações detalhadas de um feed"""
        if name not in self.feeds:
            raise ValueError(f"Feed {name} not found")

        config = self.feeds[name]
        packages = await self._get_feed_packages(name)
        metrics = await self._get_feed_metrics(name)

        return {
            'name': name,
            'config': config,
            'packages': packages,
            'metrics': metrics
        }

    async def enable_feed(self, name: str) -> Dict:
        """Habilita um feed"""
        if name not in self.feeds:
            raise ValueError(f"Feed {name} not found")

        self.feeds[name]['enabled'] = True
        self._save_feeds_config()

        return {
            'name': name,
            'status': 'enabled'
        }

    async def disable_feed(self, name: str) -> Dict:
        """Desabilita um feed"""
        if name not in self.feeds:
            raise ValueError(f"Feed {name} not found")

        self.feeds[name]['enabled'] = False
        self._save_feeds_config()

        return {
            'name': name,
            'status': 'disabled'
        }

    async def sync_feed(
        self,
        source_name: str,
        target_name: str,
        packages: Optional[List[str]] = None
    ) -> Dict:
        """Sincroniza pacotes entre feeds"""
        try:
            if source_name not in self.feeds:
                raise ValueError(f"Source feed {source_name} not found")
            if target_name not in self.feeds:
                raise ValueError(f"Target feed {target_name} not found")

            # Obtém pacotes para sincronização
            if not packages:
                packages = await self._get_feed_packages(source_name)

            results = {
                'success': [],
                'failed': []
            }

            # Sincroniza cada pacote
            for package in packages:
                try:
                    await self._sync_package(
                        package,
                        source_name,
                        target_name
                    )
                    results['success'].append(package)
                except Exception as e:
                    results['failed'].append({
                        'package': package,
                        'error': str(e)
                    })

            return {
                'source': source_name,
                'target': target_name,
                'results': results
            }

        except Exception as e:
            self.logger.error(f"Failed to sync feed: {str(e)}")
            raise

    async def mirror_feed(
        self,
        source_name: str,
        mirror_name: str,
        sync_interval: int = 3600
    ) -> Dict:
        """Cria um espelho de um feed"""
        try:
            if source_name not in self.feeds:
                raise ValueError(f"Source feed {source_name} not found")

            # Configura feed espelho
            mirror_url = str(self.feeds_path / mirror_name)
            mirror_config = {
                'url': mirror_url,
                'type': FeedType.MIRROR.value,
                'source_feed': source_name,
                'sync_interval': sync_interval,
                'last_sync': None,
                'enabled': True
            }

            # Registra feed espelho
            self.feeds[mirror_name] = mirror_config
            self._save_feeds_config()

            # Inicia sincronização inicial
            sync_result = await self.sync_feed(source_name, mirror_name)

            return {
                'name': mirror_name,
                'config': mirror_config,
                'initial_sync': sync_result
            }

        except Exception as e:
            self.logger.error(f"Failed to create mirror feed: {str(e)}")
            raise

    async def check_feed_health(self, name: str) -> Dict:
        """Verifica saúde de um feed"""
        try:
            if name not in self.feeds:
                raise ValueError(f"Feed {name} not found")

            config = self.feeds[name]
            checks = {
                'connectivity': await self._check_feed_connectivity(name),
                'packages': await self._check_feed_packages(name),
                'performance': await self._check_feed_performance(name)
            }

            # Determina status geral
            status = 'healthy'
            if any(not check['healthy'] for check in checks.values()):
                status = 'unhealthy'

            return {
                'name': name,
                'status': status,
                'checks': checks,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to check feed health: {str(e)}")
            raise

    async def _validate_feed_url(self, url: str) -> None:
        """Valida URL do feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError(f"Invalid feed URL: {url}")
        except Exception as e:
            raise ValueError(f"Failed to validate feed URL: {str(e)}")

    async def _store_credentials(
        self,
        feed_name: str,
        credentials: Dict
    ) -> str:
        """Armazena credenciais de forma segura"""
        # Implementar armazenamento seguro de credenciais
        pass

    async def _count_feed_packages(self, feed_name: str) -> int:
        """Conta número de pacotes em um feed"""
        try:
            if self.feeds[feed_name]['type'] == FeedType.LOCAL.value:
                feed_dir = self.feeds_path / feed_name
                return len(list(feed_dir.glob("*.nupkg")))
            else:
                # Implementar contagem para feeds remotos
                pass
        except Exception:
            return 0

    async def _get_feed_packages(self, feed_name: str) -> List[Dict]:
        """Obtém lista de pacotes de um feed"""
        try:
            if self.feeds[feed_name]['type'] == FeedType.LOCAL.value:
                return await self._get_local_feed_packages(feed_name)
            else:
                return await self._get_remote_feed_packages(feed_name)
        except Exception as e:
            self.logger.error(f"Failed to get feed packages: {str(e)}")
            return []

    async def _sync_package(
        self,
        package: Dict,
        source_feed: str,
        target_feed: str
    ) -> None:
        """Sincroniza um pacote entre feeds"""
        try:
            # Download do pacote
            package_path = await self._download_package(
                package,
                source_feed
            )

            # Upload do pacote
            await self._upload_package(
                package_path,
                target_feed
            )

            # Limpa arquivos temporários
            package_path.unlink()

        except Exception as e:
            raise Exception(f"Failed to sync package: {str(e)}")

    async def _check_feed_connectivity(self, feed_name: str) -> Dict:
        """Verifica conectividade com feed"""
        try:
            config = self.feeds[feed_name]
            start_time = datetime.utcnow()

            async with aiohttp.ClientSession() as session:
                async with session.get(config['url']) as response:
                    latency = (datetime.utcnow() - start_time).total_seconds()

                    return {
                        'healthy': response.status == 200,
                        'latency': latency,
                        'status_code': response.status
                    }

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    async def _check_feed_packages(self, feed_name: str) -> Dict:
        """Verifica integridade dos pacotes"""
        try:
            packages = await self._get_feed_packages(feed_name)
            invalid_packages = []

            for package in packages:
                if not await self._validate_package(package, feed_name):
                    invalid_packages.append(package)

            return {
                'healthy': len(invalid_packages) == 0,
                'total_packages': len(packages),
                'invalid_packages': invalid_packages
            }

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }

    async def _check_feed_performance(self, feed_name: str) -> Dict:
        """Verifica performance do feed"""
        try:
            metrics = []
            for _ in range(3):  # Realiza 3 medições
                start_time = datetime.utcnow()
                await self._get_feed_packages(feed_name)
                latency = (datetime.utcnow() - start_time).total_seconds()
                metrics.append(latency)

            avg_latency = sum(metrics) / len(metrics)
            return {
                'healthy': avg_latency < 5.0,  # Threshold de 5 segundos
                'average_latency': avg_latency,
                'measurements': metrics
            }

        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }