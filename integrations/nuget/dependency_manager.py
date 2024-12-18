# integrations/nuget/dependency_manager.py
from typing import Dict, List, Optional, Set
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import semver
import networkx as nx

class DependencyType(Enum):
    DIRECT = "direct"  # Dependência direta
    TRANSITIVE = "transitive"  # Dependência transitiva
    DEVELOPMENT = "development"  # Dependência de desenvolvimento

class DependencyManager:
    def __init__(self, package_manager):
        self.package_manager = package_manager
        self.logger = logging.getLogger(__name__)
        self.dependency_graph = nx.DiGraph()

    async def resolve_dependencies(
        self,
        package_name: str,
        version: Optional[str] = None,
        dependency_type: DependencyType = DependencyType.DIRECT
    ) -> Dict:
        """Resolve dependências de um pacote"""
        try:
            # Limpa grafo existente
            self.dependency_graph.clear()
            
            # Adiciona pacote inicial
            await self._add_package_to_graph(
                package_name,
                version,
                dependency_type
            )
            
            # Resolve dependências recursivamente
            await self._resolve_dependencies_recursive(
                package_name,
                version
            )
            
            # Analisa conflitos
            conflicts = self._analyze_conflicts()
            
            # Gera plano de instalação
            installation_plan = self._generate_installation_plan()
            
            return {
                'package': package_name,
                'version': version,
                'dependencies': self._get_all_dependencies(),
                'conflicts': conflicts,
                'installation_plan': installation_plan
            }
            
        except Exception as e:
            self.logger.error(f"Failed to resolve dependencies: {str(e)}")
            raise

    async def check_compatibility(
        self,
        packages: List[Dict]
    ) -> Dict:
        """Verifica compatibilidade entre pacotes"""
        try:
            compatibility_matrix = {}
            issues = []
            
            # Verifica cada par de pacotes
            for i, pkg1 in enumerate(packages):
                compatibility_matrix[pkg1['id']] = {}
                
                for pkg2 in packages[i+1:]:
                    result = await self._check_package_compatibility(
                        pkg1,
                        pkg2
                    )
                    
                    compatibility_matrix[pkg1['id']][pkg2['id']] = result
                    
                    if not result['compatible']:
                        issues.append({
                            'package1': pkg1['id'],
                            'package2': pkg2['id'],
                            'reason': result['reason']
                        })
            
            return {
                'compatible': len(issues) == 0,
                'matrix': compatibility_matrix,
                'issues': issues
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check compatibility: {str(e)}")
            raise

    async def analyze_impact(
        self,
        package_name: str,
        new_version: str
    ) -> Dict:
        """Analisa impacto de atualização de pacote"""
        try:
            current_version = await self.package_manager._get_installed_version(
                package_name
            )
            
            # Obtém dependências atuais
            current_deps = await self._get_package_dependencies(
                package_name,
                current_version
            )
            
            # Obtém dependências da nova versão
            new_deps = await self._get_package_dependencies(
                package_name,
                new_version
            )
            
            # Analisa mudanças
            added_deps = self._compare_dependencies(new_deps, current_deps)
            removed_deps = self._compare_dependencies(current_deps, new_deps)
            changed_deps = self._find_changed_dependencies(
                current_deps,
                new_deps
            )
            
            # Analisa projetos afetados
            affected_projects = await self._find_affected_projects(package_name)
            
            return {
                'package': package_name,
                'current_version': current_version,
                'new_version': new_version,
                'changes': {
                    'added_dependencies': added_deps,
                    'removed_dependencies': removed_deps,
                    'changed_dependencies': changed_deps
                },
                'affected_projects': affected_projects
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze impact: {str(e)}")
            raise

    async def _resolve_dependencies_recursive(
        self,
        package_name: str,
        version: Optional[str],
        visited: Optional[Set[str]] = None
    ) -> None:
        """Resolve dependências recursivamente"""
        if visited is None:
            visited = set()
            
        package_key = f"{package_name}@{version}"
        if package_key in visited:
            return
            
        visited.add(package_key)
        
        # Obtém dependências diretas
        dependencies = await self._get_package_dependencies(
            package_name,
            version
        )
        
        for dep in dependencies:
            # Adiciona dependência ao grafo
            await self._add_package_to_graph(
                dep['id'],
                dep['version'],
                DependencyType.TRANSITIVE
            )
            
            # Resolve dependências da dependência
            await self._resolve_dependencies_recursive(
                dep['id'],
                dep['version'],
                visited
            )

    async def _add_package_to_graph(
        self,
        package_name: str,
        version: Optional[str],
        dependency_type: DependencyType
    ) -> None:
        """Adiciona pacote ao grafo de dependências"""
        # Obtém informações do pacote
        package_info = await self.package_manager._get_package_info(
            package_name,
            version,
            self.package_manager.config.get('default_source')
        )
        
        # Adiciona nó ao grafo
        node_id = f"{package_name}@{package_info['version']}"
        self.dependency_graph.add_node(
            node_id,
            package=package_name,
            version=package_info['version'],
            type=dependency_type.value
        )
        
        # Se já existir, atualiza tipo de dependência
        if dependency_type == DependencyType.DIRECT:
            self.dependency_graph.nodes[node_id]['type'] = DependencyType.DIRECT.value

    def _analyze_conflicts(self) -> List[Dict]:
        """Analisa conflitos de dependências"""
        conflicts = []
        
        # Agrupa nós por pacote
        package_versions = {}
        for node in self.dependency_graph.nodes:
            package = self.dependency_graph.nodes[node]['package']
            version = self.dependency_graph.nodes[node]['version']
            
            if package not in package_versions:
                package_versions[package] = set()
            package_versions[package].add(version)
        
        # Identifica pacotes com múltiplas versões
        for package, versions in package_versions.items():
            if len(versions) > 1:
                conflicts.append({
                    'package': package,
                    'versions': list(versions),
                    'type': 'multiple_versions'
                })
        
        return conflicts

    def _generate_installation_plan(self) -> List[Dict]:
        """Gera plano de instalação baseado em dependências"""
        # Ordena nós topologicamente
        try:
            ordered_nodes = list(nx.topological_sort(self.dependency_graph))
        except nx.NetworkXUnfeasible:
            self.logger.error("Circular dependency detected")
            ordered_nodes = list(self.dependency_graph.nodes)
        
        # Gera plano de instalação
        plan = []
        for node in ordered_nodes:
            package = self.dependency_graph.nodes[node]['package']
            version = self.dependency_graph.nodes[node]['version']
            dep_type = self.dependency_graph.nodes[node]['type']
            
            plan.append({
                'package': package,
                'version': version,
                'type': dep_type,
                'dependencies': [
                    self.dependency_graph.nodes[pred]['package']
                    for pred in self.dependency_graph.predecessors(node)
                ]
            })
        
        return plan

    def _get_all_dependencies(self) -> List[Dict]:
        """Obtém todas as dependências do grafo"""
        dependencies = []
        
        for node in self.dependency_graph.nodes:
            dependencies.append({
                'package': self.dependency_graph.nodes[node]['package'],
                'version': self.dependency_graph.nodes[node]['version'],
                'type': self.dependency_graph.nodes[node]['type'],
                'required_by': [
                    self.dependency_graph.nodes[pred]['package']
                    for pred in self.dependency_graph.predecessors(node)
                ]
            })
            
        return dependencies

    async def _check_package_compatibility(
        self,
        package1: Dict,
        package2: Dict
    ) -> Dict:
        """Verifica compatibilidade entre dois pacotes"""
        try:
            # Obtém dependências dos pacotes
            deps1 = await self._get_package_dependencies(
                package1['id'],
                package1['version']
            )
            deps2 = await self._get_package_dependencies(
                package2['id'],
                package2['version']
            )
            
            # Verifica dependências compartilhadas
            shared_deps = self._find_shared_dependencies(deps1, deps2)
            conflicts = []
            
            for dep in shared_deps:
                if not self._are_versions_compatible(
                    dep['version1'],
                    dep['version2']
                ):
                    conflicts.append({
                        'package': dep['package'],
                        'version1': dep['version1'],
                        'version2': dep['version2']
                    })
            
            return {
                'compatible': len(conflicts) == 0,
                'shared_dependencies': shared_deps,
                'conflicts': conflicts
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check package compatibility: {str(e)}")
            raise

    def _are_versions_compatible(
        self,
        version1: str,
        version2: str
    ) -> bool:
        """Verifica se duas versões são compatíveis"""
        try:
            v1 = semver.VersionInfo.parse(version1)
            v2 = semver.VersionInfo.parse(version2)
            
            # Considera compatível se major version é igual
            return v1.major == v2.major
            
        except ValueError:
            return False

    async def _find_affected_projects(
        self,
        package_name: str
    ) -> List[Dict]:
        """Encontra projetos afetados por uma atualização"""
        affected_projects = []
        
        # Procura referências ao pacote
        for proj_file in Path(".").glob("**/*.csproj"):
            try:
                tree = ET.parse(proj_file)
                root = tree.getroot()
                
                # Verifica PackageReference
                for ref in root.findall(".//PackageReference"):
                    if ref.get('Include') == package_name:
                        affected_projects.append({
                            'project': proj_file.stem,
                            'path': str(proj_file),
                            'version': ref.get('Version')
                        })
                        
            except Exception as e:
                self.logger.warning(
                    f"Failed to check project {proj_file}: {str(e)}"
                )
                
        return affected_projects