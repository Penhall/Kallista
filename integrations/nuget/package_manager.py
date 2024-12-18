# integrations/nuget/package_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import semver
import aiohttp
import shutil

class PackageSource(Enum):
    NUGET = "nuget"
    LOCAL = "local"
    CUSTOM = "custom"

class PackageManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.packages_path = Path(config.get('packages_path', 'packages'))
        self.packages_path.mkdir(parents=True, exist_ok=True)
        
        self.nuget_api = "https://api.nuget.org/v3/index.json"
        self.local_feed = self.packages_path / "local-feed"
        self.local_feed.mkdir(exist_ok=True)

    async def install_package(
        self,
        package_name: str,
        version: Optional[str] = None,
        source: PackageSource = PackageSource.NUGET
    ) -> Dict:
        """Instala um pacote NuGet"""
        try:
            # Verifica se já está instalado
            if await self._is_package_installed(package_name, version):
                return {
                    'package': package_name,
                    'version': version,
                    'status': 'already_installed'
                }

            # Obtém informações do pacote
            package_info = await self._get_package_info(
                package_name,
                version,
                source
            )

            # Download do pacote
            package_path = await self._download_package(package_info)

            # Instala pacote
            install_result = await self._install_package_files(package_path)

            # Atualiza referências
            await self._update_package_references(package_info)

            return {
                'package': package_name,
                'version': package_info['version'],
                'status': 'installed',
                'location': str(install_result['location'])
            }

        except Exception as e:
            self.logger.error(f"Failed to install package: {str(e)}")
            raise

    async def uninstall_package(
        self,
        package_name: str,
        version: Optional[str] = None
    ) -> Dict:
        """Remove um pacote NuGet"""
        try:
            # Verifica se está instalado
            if not await self._is_package_installed(package_name, version):
                raise ValueError(f"Package {package_name} is not installed")

            # Remove arquivos do pacote
            await self._remove_package_files(package_name, version)

            # Atualiza referências
            await self._update_package_references({
                'id': package_name,
                'version': version
            }, remove=True)

            return {
                'package': package_name,
                'version': version,
                'status': 'uninstalled'
            }

        except Exception as e:
            self.logger.error(f"Failed to uninstall package: {str(e)}")
            raise

    async def update_package(
        self,
        package_name: str,
        version: Optional[str] = None
    ) -> Dict:
        """Atualiza um pacote NuGet"""
        try:
            # Verifica se está instalado
            if not await self._is_package_installed(package_name):
                raise ValueError(f"Package {package_name} is not installed")

            # Obtém versão atual
            current_version = await self._get_installed_version(package_name)

            # Obtém informações da nova versão
            package_info = await self._get_package_info(package_name, version)
            
            # Compara versões
            if semver.compare(package_info['version'], current_version) <= 0:
                return {
                    'package': package_name,
                    'version': current_version,
                    'status': 'up_to_date'
                }

            # Remove versão atual
            await self.uninstall_package(package_name, current_version)

            # Instala nova versão
            install_result = await self.install_package(
                package_name,
                package_info['version']
            )

            return {
                'package': package_name,
                'previous_version': current_version,
                'new_version': package_info['version'],
                'status': 'updated'
            }

        except Exception as e:
            self.logger.error(f"Failed to update package: {str(e)}")
            raise

    async def list_packages(
        self,
        include_dependencies: bool = False
    ) -> List[Dict]:
        """Lista pacotes instalados"""
        try:
            packages = []
            
            # Lê arquivo de packages.config
            config_file = Path("packages.config")
            if not config_file.exists():
                return packages

            tree = ET.parse(config_file)
            root = tree.getroot()

            for package in root.findall("package"):
                package_info = {
                    'id': package.get('id'),
                    'version': package.get('version'),
                    'targetFramework': package.get('targetFramework')
                }

                if include_dependencies:
                    package_info['dependencies'] = await self._get_package_dependencies(
                        package_info['id'],
                        package_info['version']
                    )

                packages.append(package_info)

            return packages

        except Exception as e:
            self.logger.error(f"Failed to list packages: {str(e)}")
            raise

    async def search_packages(
        self,
        query: str,
        source: PackageSource = PackageSource.NUGET,
        include_prerelease: bool = False
    ) -> List[Dict]:
        """Pesquisa pacotes disponíveis"""
        try:
            if source == PackageSource.NUGET:
                return await self._search_nuget_packages(
                    query,
                    include_prerelease
                )
            elif source == PackageSource.LOCAL:
                return await self._search_local_packages(query)
            else:
                return await self._search_custom_packages(
                    query,
                    self.config.get('custom_source')
                )

        except Exception as e:
            self.logger.error(f"Failed to search packages: {str(e)}")
            raise

    async def create_package(
        self,
        package_config: Dict
    ) -> Dict:
        """Cria um novo pacote NuGet"""
        try:
            # Valida configuração
            validation = self._validate_package_config(package_config)
            if not validation['valid']:
                raise ValueError(f"Invalid package configuration: {validation['errors']}")

            # Cria estrutura do pacote
            package_dir = await self._create_package_structure(package_config)

            # Gera arquivo .nuspec
            nuspec_path = await self._generate_nuspec(package_config, package_dir)

            # Compila arquivos
            if package_config.get('compile', True):
                await self._compile_package_files(package_dir)

            # Cria pacote .nupkg
            package_file = await self._create_nupkg(nuspec_path)

            # Move para feed local
            final_path = self.local_feed / package_file.name
            shutil.move(package_file, final_path)

            return {
                'id': package_config['id'],
                'version': package_config['version'],
                'path': str(final_path)
            }

        except Exception as e:
            self.logger.error(f"Failed to create package: {str(e)}")
            raise

    async def publish_package(
        self,
        package_path: Union[str, Path],
        source: PackageSource = PackageSource.NUGET,
        api_key: Optional[str] = None
    ) -> Dict:
        """Publica um pacote NuGet"""
        try:
            package_path = Path(package_path)
            if not package_path.exists():
                raise FileNotFoundError(f"Package file not found: {package_path}")

            if source == PackageSource.NUGET:
                return await self._publish_to_nuget(package_path, api_key)
            elif source == PackageSource.LOCAL:
                return await self._publish_to_local(package_path)
            else:
                return await self._publish_to_custom(
                    package_path,
                    self.config.get('custom_source'),
                    api_key
                )

        except Exception as e:
            self.logger.error(f"Failed to publish package: {str(e)}")
            raise

    async def _get_package_info(
        self,
        package_name: str,
        version: Optional[str],
        source: PackageSource
    ) -> Dict:
        """Obtém informações de um pacote"""
        if source == PackageSource.NUGET:
            async with aiohttp.ClientSession() as session:
                url = f"{self.nuget_api}/v3/registration5-semver1/{package_name.lower()}/index.json"
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError(f"Package {package_name} not found")
                        
                    data = await response.json()
                    
                    if version:
                        # Procura versão específica
                        for entry in data['items']:
                            if entry['catalogEntry']['version'] == version:
                                return entry['catalogEntry']
                    else:
                        # Retorna versão mais recente
                        return data['items'][-1]['catalogEntry']
                        
        elif source == PackageSource.LOCAL:
            # Procura no feed local
            package_path = self.local_feed / f"{package_name}.nuspec"
            if not package_path.exists():
                raise ValueError(f"Package {package_name} not found in local feed")
                
            tree = ET.parse(package_path)
            root = tree.getroot()
            
            metadata = root.find('metadata')
            return {
                'id': metadata.find('id').text,
                'version': metadata.find('version').text,
                'description': metadata.find('description').text
            }
            
        else:
            # Implementar busca em fonte customizada
            raise NotImplementedError("Custom source not implemented")

    async def _get_package_dependencies(
        self,
        package_name: str,
        version: str
    ) -> List[Dict]:
        """Obtém dependências de um pacote"""
        try:
            # Carrega informações do pacote
            package_dir = self.packages_path / f"{package_name}.{version}"
            nuspec_file = package_dir / f"{package_name}.nuspec"
            
            if not nuspec_file.exists():
                return []
                
            tree = ET.parse(nuspec_file)
            root = tree.getroot()
            
            dependencies = []
            deps_elem = root.find(".//dependencies")
            
            if deps_elem is not None:
                for dep in deps_elem.findall("dependency"):
                    dependencies.append({
                        'id': dep.get('id'),
                        'version': dep.get('version')
                    })
                    
            return dependencies
            
        except Exception as e:
            self.logger.warning(f"Failed to get package dependencies: {str(e)}")
            return []

    def _validate_package_config(self, config: Dict) -> Dict:
        """Valida configuração de pacote"""
        errors = []
        
        required_fields = ['id', 'version', 'authors', 'description']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
                
        if 'version' in config:
            try:
                semver.parse(config['version'])
            except ValueError:
                errors.append("Invalid version format")
                
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    async def _generate_nuspec(
        self,
        config: Dict,
        package_dir: Path
    ) -> Path:
        """Gera arquivo .nuspec"""
        nuspec = ET.Element('package')
        nuspec.set('xmlns', 'http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd')
        
        metadata = ET.SubElement(nuspec, 'metadata')
        
        # Campos obrigatórios
        ET.SubElement(metadata, 'id').text = config['id']
        ET.SubElement(metadata, 'version').text = config['version']
        ET.SubElement(metadata, 'authors').text = config['authors']
        ET.SubElement(metadata, 'description').text = config['description']
        
        # Campos opcionais
        if 'title' in config:
            ET.SubElement(metadata, 'title').text = config['title']
        if 'tags' in config:
            ET.SubElement(metadata, 'tags').text = ' '.join(config['tags'])
        if 'projectUrl' in config:
            ET.SubElement(metadata, 'projectUrl').text = config['projectUrl']
        
        # Dependências
        if 'dependencies' in config:
            deps = ET.SubElement(metadata, 'dependencies')
            for dep in config['dependencies']:
                dep_elem = ET.SubElement(deps, 'dependency')
                dep_elem.set('id', dep['id'])
                dep_elem.set('version', dep['version'])
        
        # Salva arquivo
        nuspec_path = package_dir / f"{config['id']}.nuspec"
        tree = ET.ElementTree(nuspec)
        tree.write(nuspec_path, encoding='utf-8', xml_declaration=True)
        
        return nuspec_path