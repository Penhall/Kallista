# workflows/nuget_workflow.py
from pathlib import Path
from typing import Dict, List
from integrations.nuget.dependency_manager import DependencyManager
from integrations.nuget.feed_manager import FeedManager, FeedType
from integrations.nuget.package_manager import PackageManager
from integrations.nuget.version_manager import VersionManager, VersionStrategy

class NuGetWorkflow:
    def __init__(self, config: Dict):
        self.config = config
        self.package_manager = PackageManager(config)
        self.feed_manager = FeedManager(config)
        self.version_manager = VersionManager(self.package_manager)
        self.dependency_manager = DependencyManager(self.package_manager)

    async def setup_project_packages(self, project_config: Dict) -> Dict:
        """Configura pacotes para um novo projeto"""
        results = {
            'installed_packages': [],
            'configured_feeds': [],
            'errors': []
        }
        
        try:
            # 1. Configura feeds
            for feed in project_config.get('feeds', []):
                try:
                    await self.feed_manager.register_feed(
                        name=feed['name'],
                        url=feed['url'],
                        feed_type=FeedType(feed['type']),
                        credentials=feed.get('credentials')
                    )
                    results['configured_feeds'].append(feed['name'])
                except Exception as e:
                    results['errors'].append(f"Failed to configure feed {feed['name']}: {str(e)}")

            # 2. Instala pacotes necessários
            for package in project_config.get('packages', []):
                try:
                    # Resolve dependências
                    deps = await self.dependency_manager.resolve_dependencies(
                        package['name'],
                        package.get('version')
                    )

                    # Instala pacote e dependências
                    install_result = await self.package_manager.install_package(
                        package['name'],
                        package.get('version')
                    )
                    
                    results['installed_packages'].append({
                        'package': package['name'],
                        'version': install_result['version'],
                        'dependencies': deps['dependencies']
                    })
                except Exception as e:
                    results['errors'].append(f"Failed to install package {package['name']}: {str(e)}")

            # 3. Configura versionamento
            if 'version_policy' in project_config:
                await self.version_manager.create_version_policy(
                    project_config['version_policy']
                )

            return results

        except Exception as e:
            raise Exception(f"Failed to setup project packages: {str(e)}")

    async def create_package(self, package_config: Dict) -> Dict:
        """Cria e publica um novo pacote"""
        try:
            # 1. Cria o pacote
            package = await self.package_manager.create_package(package_config)

            # 2. Configura versionamento
            await self.version_manager.create_version_policy({
                'versioning_strategy': VersionStrategy.MINOR.value,
                'prerelease_naming': 'alpha',
                'auto_increment': True
            })

            # 3. Publica o pacote
            publish_result = await self.package_manager.publish_package(
                package['path'],
                source=package_config.get('target_feed', 'nuget'),
                api_key=package_config.get('api_key')
            )

            return {
                'package': package['id'],
                'version': package['version'],
                'published': publish_result,
                'location': package['path']
            }

        except Exception as e:
            raise Exception(f"Failed to create and publish package: {str(e)}")

    async def update_project_packages(self, update_config: Dict) -> Dict:
        """Atualiza pacotes do projeto"""
        results = {
            'updated_packages': [],
            'failed_updates': [],
            'skipped_updates': []
        }

        try:
            # 1. Analisa pacotes atuais
            current_packages = await self.package_manager.list_packages(
                include_dependencies=True
            )

            # 2. Verifica e aplica atualizações
            for package in current_packages:
                try:
                    # Verifica compatibilidade
                    compatibility = await self.version_manager.check_version_compatibility(
                        package['id'],
                        package.get('target_version', 'latest')
                    )

                    if not compatibility['compatible']:
                        results['skipped_updates'].append({
                            'package': package['id'],
                            'reason': compatibility['analysis']
                        })
                        continue

                    # Atualiza pacote
                    update_result = await self.package_manager.update_package(
                        package['id'],
                        package.get('target_version')
                    )

                    results['updated_packages'].append(update_result)

                except Exception as e:
                    results['failed_updates'].append({
                        'package': package['id'],
                        'error': str(e)
                    })

            return results

        except Exception as e:
            raise Exception(f"Failed to update project packages: {str(e)}")

    async def validate_dependencies(self) -> Dict:
        """Valida dependências do projeto"""
        try:
            # 1. Lista todos os pacotes
            packages = await self.package_manager.list_packages(
                include_dependencies=True
            )

            # 2. Verifica compatibilidade entre pacotes
            compatibility = await self.dependency_manager.check_compatibility(packages)

            # 3. Analisa conflitos
            conflicts = []
            for issue in compatibility.get('issues', []):
                # Tenta resolver conflito
                resolution = await self._resolve_dependency_conflict(
                    issue['package1'],
                    issue['package2']
                )
                
                if resolution['resolved']:
                    await self._apply_dependency_resolution(resolution)
                else:
                    conflicts.append(issue)

            return {
                'valid': len(conflicts) == 0,
                'packages': len(packages),
                'compatibility_matrix': compatibility['matrix'],
                'unresolved_conflicts': conflicts
            }

        except Exception as e:
            raise Exception(f"Failed to validate dependencies: {str(e)}")

    async def _resolve_dependency_conflict(
        self,
        package1: str,
        package2: str
    ) -> Dict:
        """Tenta resolver conflito entre dependências"""
        try:
            # Implementar lógica de resolução de conflitos
            # Por exemplo, tentar encontrar uma versão compatível
            pass
        except Exception as e:
            return {
                'resolved': False,
                'error': str(e)
            }