# integrations/nuget/version_manager.py
from typing import Dict, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import semver
import json
import xml.etree.ElementTree as ET

class VersionStrategy(Enum):
    MAJOR = "major"  # Mudanças incompatíveis com versões anteriores
    MINOR = "minor"  # Novas funcionalidades compatíveis
    PATCH = "patch"  # Correções de bugs
    PRERELEASE = "prerelease"  # Versões de teste

class VersionManager:
    def __init__(self, package_manager):
        self.package_manager = package_manager
        self.logger = logging.getLogger(__name__)
        self.version_history_path = Path("version_history")
        self.version_history_path.mkdir(exist_ok=True)

    async def bump_version(
        self,
        package_name: str,
        strategy: VersionStrategy,
        prerelease_id: Optional[str] = None
    ) -> Dict:
        """Incrementa versão do pacote"""
        try:
            # Obtém versão atual
            current_version = await self.package_manager._get_installed_version(
                package_name
            )
            current = semver.VersionInfo.parse(current_version)

            # Calcula nova versão
            if strategy == VersionStrategy.MAJOR:
                new_version = current.bump_major()
            elif strategy == VersionStrategy.MINOR:
                new_version = current.bump_minor()
            elif strategy == VersionStrategy.PATCH:
                new_version = current.bump_patch()
            elif strategy == VersionStrategy.PRERELEASE:
                if not prerelease_id:
                    prerelease_id = "alpha"
                new_version = current.bump_prerelease(prerelease_id)

            # Atualiza versão no projeto
            await self._update_project_version(package_name, str(new_version))

            # Registra histórico
            await self._record_version_change(
                package_name,
                current_version,
                str(new_version),
                strategy
            )

            return {
                'package': package_name,
                'previous_version': current_version,
                'new_version': str(new_version),
                'strategy': strategy.value,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to bump version: {str(e)}")
            raise

    async def get_version_history(
        self,
        package_name: str,
        include_prereleases: bool = False
    ) -> List[Dict]:
        """Obtém histórico de versões"""
        try:
            history_file = self.version_history_path / f"{package_name}.json"
            if not history_file.exists():
                return []

            with open(history_file) as f:
                history = json.load(f)

            if not include_prereleases:
                history = [
                    h for h in history
                    if not semver.VersionInfo.parse(h['version']).prerelease
                ]

            return sorted(
                history,
                key=lambda x: semver.VersionInfo.parse(x['version']),
                reverse=True
            )

        except Exception as e:
            self.logger.error(f"Failed to get version history: {str(e)}")
            raise

    async def set_version_constraints(
        self,
        package_name: str,
        constraints: Dict
    ) -> Dict:
        """Define restrições de versão"""
        try:
            # Valida restrições
            validation = self._validate_version_constraints(constraints)
            if not validation['valid']:
                raise ValueError(f"Invalid version constraints: {validation['errors']}")

            # Atualiza restrições no projeto
            await self._update_version_constraints(package_name, constraints)

            return {
                'package': package_name,
                'constraints': constraints,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to set version constraints: {str(e)}")
            raise

    async def check_version_compatibility(
        self,
        package_name: str,
        target_version: str
    ) -> Dict:
        """Verifica compatibilidade de versão"""
        try:
            # Obtém versão atual
            current_version = await self.package_manager._get_installed_version(
                package_name
            )
            current = semver.VersionInfo.parse(current_version)
            target = semver.VersionInfo.parse(target_version)

            # Analisa compatibilidade
            breaking_changes = target.major > current.major
            new_features = target.minor > current.minor
            bug_fixes = target.patch > current.patch

            # Verifica restrições
            constraints = await self._get_version_constraints(package_name)
            meets_constraints = self._check_version_constraints(
                target_version,
                constraints
            )

            return {
                'compatible': not breaking_changes and meets_constraints,
                'analysis': {
                    'breaking_changes': breaking_changes,
                    'new_features': new_features,
                    'bug_fixes': bug_fixes,
                    'meets_constraints': meets_constraints
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to check version compatibility: {str(e)}")
            raise

    async def create_version_policy(
        self,
        policy_config: Dict
    ) -> Dict:
        """Cria política de versionamento"""
        try:
            # Valida configuração
            validation = self._validate_policy_config(policy_config)
            if not validation['valid']:
                raise ValueError(f"Invalid policy configuration: {validation['errors']}")

            # Salva política
            policy_file = self.version_history_path / "version_policy.json"
            with open(policy_file, 'w') as f:
                json.dump(policy_config, f, indent=2)

            return {
                'policy': policy_config,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to create version policy: {str(e)}")
            raise

    async def _update_project_version(
        self,
        package_name: str,
        new_version: str
    ) -> None:
        """Atualiza versão no projeto"""
        try:
            # Atualiza .csproj
            for proj_file in Path(".").glob("**/*.csproj"):
                tree = ET.parse(proj_file)
                root = tree.getroot()

                for version_elem in root.findall(".//Version"):
                    version_elem.text = new_version

                # Atualiza PackageReference se existir
                for ref in root.findall(".//PackageReference"):
                    if ref.get('Include') == package_name:
                        ref.set('Version', new_version)

                tree.write(proj_file, encoding='utf-8', xml_declaration=True)

            # Atualiza .nuspec se existir
            nuspec_file = Path(f"{package_name}.nuspec")
            if nuspec_file.exists():
                tree = ET.parse(nuspec_file)
                root = tree.getroot()

                version_elem = root.find(".//version")
                if version_elem is not None:
                    version_elem.text = new_version

                tree.write(nuspec_file, encoding='utf-8', xml_declaration=True)

        except Exception as e:
            self.logger.error(f"Failed to update project version: {str(e)}")
            raise

    async def _record_version_change(
        self,
        package_name: str,
        old_version: str,
        new_version: str,
        strategy: VersionStrategy
    ) -> None:
        """Registra mudança de versão"""
        history_file = self.version_history_path / f"{package_name}.json"
        history = []

        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)

        history.append({
            'version': new_version,
            'previous_version': old_version,
            'strategy': strategy.value,
            'timestamp': datetime.utcnow().isoformat()
        })

        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def _validate_version_constraints(self, constraints: Dict) -> Dict:
        """Valida restrições de versão"""
        errors = []

        if 'min_version' in constraints:
            try:
                semver.VersionInfo.parse(constraints['min_version'])
            except ValueError:
                errors.append("Invalid min_version format")

        if 'max_version' in constraints:
            try:
                semver.VersionInfo.parse(constraints['max_version'])
            except ValueError:
                errors.append("Invalid max_version format")

        if 'allowed_versions' in constraints:
            for version in constraints['allowed_versions']:
                try:
                    semver.VersionInfo.parse(version)
                except ValueError:
                    errors.append(f"Invalid version format in allowed_versions: {version}")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _validate_policy_config(self, config: Dict) -> Dict:
        """Valida configuração de política"""
        errors = []

        required_fields = ['versioning_strategy', 'prerelease_naming']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        if 'versioning_strategy' in config:
            valid_strategies = [s.value for s in VersionStrategy]
            if config['versioning_strategy'] not in valid_strategies:
                errors.append(f"Invalid versioning strategy: {config['versioning_strategy']}")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _check_version_constraints(
        self,
        version: str,
        constraints: Dict
    ) -> bool:
        """Verifica se versão atende às restrições"""
        v = semver.VersionInfo.parse(version)

        if 'min_version' in constraints:
            min_v = semver.VersionInfo.parse(constraints['min_version'])
            if v < min_v:
                return False

        if 'max_version' in constraints:
            max_v = semver.VersionInfo.parse(constraints['max_version'])
            if v > max_v:
                return False

        if 'allowed_versions' in constraints:
            if version not in constraints['allowed_versions']:
                return False

        if constraints.get('allow_prereleases', False) is False:
            if v.prerelease:
                return False

        return True
        