# integrations/workflow/workflow_manager.py
from typing import Dict, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime

class WorkflowType(Enum):
    CODE_REVIEW = "code_review"
    BUILD = "build"
    RELEASE = "release"
    DEPLOYMENT = "deployment"
    TESTING = "testing"

class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)

    async def create_workflow(self, config: Dict) -> Dict:
        """Cria um novo workflow"""
        try:
            workflow_type = WorkflowType(config['type'])
            workflow_id = f"{workflow_type.value}_{datetime.utcnow().timestamp()}"

            # Cria workflow no Azure DevOps
            azure_workflow = await self.azure.create_workflow({
                'name': config['name'],
                'type': workflow_type.value,
                'steps': config['steps'],
                'triggers': config.get('triggers', []),
                'variables': config.get('variables', {})
            })

            # Cria workflow no GitHub se necessário
            github_workflow = None
            if config.get('github_integration'):
                github_workflow = await self.github.create_workflow({
                    'name': config['name'],
                    'on': config.get('triggers', {}),
                    'jobs': self._convert_steps_to_github_jobs(config['steps'])
                })

            workflow = {
                'id': workflow_id,
                'type': workflow_type.value,
                'name': config['name'],
                'status': WorkflowStatus.PENDING.value,
                'azure_workflow_id': azure_workflow['id'],
                'github_workflow_id': github_workflow['id'] if github_workflow else None,
                'created_at': datetime.utcnow().isoformat(),
                'config': config
            }

            return workflow

        except Exception as e:
            self.logger.error(f"Failed to create workflow: {str(e)}")
            raise

    async def execute_workflow(self, workflow: Dict, context: Dict) -> Dict:
        """Executa um workflow"""
        try:
            workflow_type = WorkflowType(workflow['type'])
            
            # Atualiza status
            workflow['status'] = WorkflowStatus.IN_PROGRESS.value
            workflow['started_at'] = datetime.utcnow().isoformat()

            # Executa workflow baseado no tipo
            if workflow_type == WorkflowType.CODE_REVIEW:
                result = await self._execute_code_review_workflow(workflow, context)
            elif workflow_type == WorkflowType.BUILD:
                result = await self._execute_build_workflow(workflow, context)
            elif workflow_type == WorkflowType.RELEASE:
                result = await self._execute_release_workflow(workflow, context)
            elif workflow_type == WorkflowType.DEPLOYMENT:
                result = await self._execute_deployment_workflow(workflow, context)
            elif workflow_type == WorkflowType.TESTING:
                result = await self._execute_testing_workflow(workflow, context)

            # Atualiza workflow com resultados
            workflow.update({
                'status': WorkflowStatus.COMPLETED.value if result['success'] else WorkflowStatus.FAILED.value,
                'completed_at': datetime.utcnow().isoformat(),
                'result': result
            })

            return workflow

        except Exception as e:
            workflow['status'] = WorkflowStatus.FAILED.value
            workflow['error'] = str(e)
            self.logger.error(f"Failed to execute workflow: {str(e)}")
            raise

    async def _execute_code_review_workflow(self, workflow: Dict, context: Dict) -> Dict:
        """Executa workflow de code review"""
        try:
            steps_results = []

            # 1. Análise automatizada
            analysis = await self._run_automated_analysis(context['pr_info'])
            steps_results.append({
                'step': 'automated_analysis',
                'success': analysis['success'],
                'details': analysis
            })

            # 2. Atribuição de reviewers
            reviewers = await self._assign_reviewers(context['pr_info'])
            steps_results.append({
                'step': 'assign_reviewers',
                'success': reviewers['success'],
                'details': reviewers
            })

            # 3. Validação de políticas
            policies = await self._validate_policies(context['pr_info'])
            steps_results.append({
                'step': 'policy_validation',
                'success': policies['success'],
                'details': policies
            })

            success = all(step['success'] for step in steps_results)
            return {
                'success': success,
                'steps': steps_results
            }

        except Exception as e:
            self.logger.error(f"Failed to execute code review workflow: {str(e)}")
            raise

    async def _execute_build_workflow(self, workflow: Dict, context: Dict) -> Dict:
        """Executa workflow de build"""
        try:
            steps_results = []

            # 1. Preparação do ambiente
            prep = await self._prepare_build_environment(context)
            steps_results.append({
                'step': 'environment_prep',
                'success': prep['success'],
                'details': prep
            })

            # 2. Compilação
            build = await self._run_build(context)
            steps_results.append({
                'step': 'build',
                'success': build['success'],
                'details': build
            })

            # 3. Testes unitários
            tests = await self._run_unit_tests(context)
            steps_results.append({
                'step': 'unit_tests',
                'success': tests['success'],
                'details': tests
            })

            # 4. Análise de qualidade
            quality = await self._run_quality_analysis(context)
            steps_results.append({
                'step': 'quality_analysis',
                'success': quality['success'],
                'details': quality
            })

            success = all(step['success'] for step in steps_results)
            return {
                'success': success,
                'steps': steps_results
            }

        except Exception as e:
            self.logger.error(f"Failed to execute build workflow: {str(e)}")
            raise

    async def _execute_release_workflow(self, workflow: Dict, context: Dict) -> Dict:
        """Executa workflow de release"""
        try:
            steps_results = []

            # 1. Validação de pré-requisitos
            prereqs = await self._validate_release_prerequisites(context)
            steps_results.append({
                'step': 'prerequisites',
                'success': prereqs['success'],
                'details': prereqs
            })

            # 2. Geração de artefatos
            artifacts = await self._generate_release_artifacts(context)
            steps_results.append({
                'step': 'artifacts',
                'success': artifacts['success'],
                'details': artifacts
            })

            # 3. Criação de release notes
            notes = await self._generate_release_notes(context)
            steps_results.append({
                'step': 'release_notes',
                'success': notes['success'],
                'details': notes
            })

            # 4. Publicação da release
            publish = await self._publish_release(context, artifacts, notes)
            steps_results.append({
                'step': 'publish',
                'success': publish['success'],
                'details': publish
            })

            success = all(step['success'] for step in steps_results)
            return {
                'success': success,
                'steps': steps_results
            }

        except Exception as e:
            self.logger.error(f"Failed to execute release workflow: {str(e)}")
            raise

    def _convert_steps_to_github_jobs(self, steps: List[Dict]) -> Dict:
        """Converte steps do Azure DevOps para jobs do GitHub Actions"""
        jobs = {}
        
        for step in steps:
            job_name = step['name'].lower().replace(' ', '_')
            jobs[job_name] = {
                'name': step['name'],
                'runs-on': 'ubuntu-latest',  # Pode ser configurável
                'steps': self._convert_step_to_github_steps(step)
            }
            
        return jobs

    def _convert_step_to_github_steps(self, step: Dict) -> List[Dict]:
        """Converte um step do Azure DevOps para steps do GitHub Actions"""
        github_steps = []
        
        if step.get('checkout'):
            github_steps.append({
                'name': 'Checkout',
                'uses': 'actions/checkout@v2'
            })
            
        if step.get('setup'):
            github_steps.append({
                'name': 'Setup',
                'uses': f"actions/setup-{step['setup']['type']}@v2",
                'with': step['setup'].get('params', {})
            })
            
        if step.get('script'):
            github_steps.append({
                'name': step['name'],
                'run': step['script']
            })
            
        if step.get('action'):
            github_steps.append({
                'name': step['name'],
                'uses': step['action'],
                'with': step.get('params', {})
            })
            
        return github_steps