# workflows/integration_workflow.py
from typing import Dict, List, Optional
from pathlib import Path
import logging
from datetime import datetime

from integrations.nuget.feed_manager import FeedManager, FeedType
from integrations.pipeline.pipeline_manager import PipelineManager
from integrations.visual_studio.project_system import VSProjectSystem
from integrations.visual_studio.command_handler import VSCommandHandler
from integrations.visual_studio.vsix_manifest import VSIXManifestGenerator

class IntegrationWorkflow:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.feed_manager = FeedManager(config.get('nuget_config', {}))
        self.pipeline_manager = PipelineManager(
            config.get('github_client'),
            config.get('azure_client')
        )
        self.project_system = VSProjectSystem()
        self.command_handler = VSCommandHandler()
        self.manifest_generator = VSIXManifestGenerator()

    async def setup_development_environment(self, project_config: Dict) -> Dict:
        """Configura ambiente de desenvolvimento completo"""
        try:
            results = {
                'vs_integration': None,
                'nuget_setup': None,
                'pipeline_setup': None,
                'errors': []
            }

            # 1. Configuração do Visual Studio
            try:
                vs_result = await self._setup_visual_studio(project_config)
                results['vs_integration'] = vs_result
            except Exception as e:
                results['errors'].append(f"VS Setup failed: {str(e)}")

            # 2. Configuração do NuGet
            try:
                nuget_result = await self._setup_nuget(project_config)
                results['nuget_setup'] = nuget_result
            except Exception as e:
                results['errors'].append(f"NuGet Setup failed: {str(e)}")

            # 3. Configuração do Pipeline
            try:
                pipeline_result = await self._setup_pipeline(project_config)
                results['pipeline_setup'] = pipeline_result
            except Exception as e:
                results['errors'].append(f"Pipeline Setup failed: {str(e)}")

            return results

        except Exception as e:
            self.logger.error(f"Failed to setup development environment: {str(e)}")
            raise

    async def _setup_visual_studio(self, config: Dict) -> Dict:
        """Configura integração com Visual Studio"""
        try:
            # 1. Gera manifesto VSIX
            manifest_config = {
                'id': 'Kallista.VSExtension',
                'version': '1.0',
                'publisher': config['publisher'],
                'display_name': 'Kallista Development Tools',
                'description': 'Tools for WPF development with Kallista'
            }
            manifest = self.manifest_generator.generate_manifest(manifest_config)
            self.manifest_generator.save_manifest(manifest)

            # 2. Configura comandos
            command_config = {
                'name': 'GenerateWpfProject',
                'command_id': '0x0100',
                'command_set': config['command_set'],
                'actions': [
                    {
                        'type': 'create_project',
                        'template': 'KallistaWPF.zip',
                        'name': '$safeprojectname$'
                    }
                ]
            }
            command = self.command_handler.generate_command(command_config)
            self.command_handler.save_command('GenerateWpfProject', command)

            # 3. Gera templates de projeto
            template_config = {
                'name': 'KallistaWPF',
                'description': 'WPF Project with Kallista',
                'template_id': f"{manifest_config['id']}.ProjectTemplate",
                'window_title': 'Kallista WPF Application'
            }
            templates = self.project_system.generate_project_template(template_config)
            self.project_system.save_templates(templates, template_config['name'])

            return {
                'status': 'configured',
                'vsix': manifest_config['id'],
                'templates': [template_config['name']]
            }

        except Exception as e:
            raise Exception(f"Failed to setup Visual Studio integration: {str(e)}")

    async def _setup_nuget(self, config: Dict) -> Dict:
        """Configura integração com NuGet"""
        try:
            results = {
                'feeds': [],
                'packages': []
            }

            # 1. Configura feeds
            for feed in config.get('nuget_feeds', []):
                feed_result = await self.feed_manager.register_feed(
                    name=feed['name'],
                    url=feed['url'],
                    feed_type=FeedType(feed['type']),
                    credentials=feed.get('credentials')
                )
                results['feeds'].append(feed_result)

            # 2. Configura mirror local se necessário
            if config.get('setup_local_mirror'):
                mirror_result = await self.feed_manager.mirror_feed(
                    source_name='public',
                    mirror_name='local_mirror',
                    sync_interval=3600
                )
                results['feeds'].append(mirror_result)

            return results

        except Exception as e:
            raise Exception(f"Failed to setup NuGet integration: {str(e)}")

    async def _setup_pipeline(self, config: Dict) -> Dict:
        """Configura pipeline de CI/CD"""
        try:
            # 1. Configura pipeline CI
            pipeline_config = {
                'pipeline_config': {
                    'name': f"{config['name']}_CI",
                    'trigger': ['main', 'develop'],
                    'steps': [
                        {'task': 'NuGetCommand@2', 'inputs': {'command': 'restore'}},
                        {'task': 'VSBuild@1', 'inputs': {'solution': '**/*.sln'}},
                        {'task': 'VSTest@2', 'inputs': {'testSelector': 'testAssemblies'}}
                    ]
                },
                'policy_config': {
                    'requiredReviewers': config.get('required_reviewers', 1),
                    'requiredApprovals': config.get('required_approvals', 1)
                },
                'protection_config': {
                    'required_status_checks': True,
                    'enforce_admins': True
                }
            }

            # 2. Cria pipeline
            ci_result = await self.pipeline_manager.setup_ci_pipeline(pipeline_config)

            return {
                'pipeline_id': ci_result['pipeline_id'],
                'status': ci_result['status']
            }

        except Exception as e:
            raise Exception(f"Failed to setup pipeline: {str(e)}")
