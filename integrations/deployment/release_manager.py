# integrations/deployment/release_manager.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from enum import Enum

class ReleaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReleaseManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)

    async def create_release(self, config: Dict) -> Dict:
        """Cria uma nova release"""
        try:
            # Cria release no Azure DevOps
            azure_release = await self.azure.create_release({
                'definition_id': config['definition_id'],
                'description': config['description'],
                'artifacts': config.get('artifacts', []),
                'variables': config.get('variables', {})
            })

            # Cria release no GitHub
            github_release = await self.github.create_release({
                'tag_name': config['version'],
                'name': config['name'],
                'body': config['description'],
                'draft': config.get('draft', False),
                'prerelease': config.get('prerelease', False)
            })

            # Upload de artefatos
            if config.get('artifacts'):
                await self._upload_artifacts(config['artifacts'], github_release['id'])

            return {
                'azure_release_id': azure_release['id'],
                'github_release_id': github_release['id'],
                'status': ReleaseStatus.PENDING.value,
                'version': config['version'],
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to create release: {str(e)}")
            raise

    async def deploy_release(self, release_info: Dict, environment: str) -> Dict:
        """Realiza deploy de uma release"""
        try:
            # Inicia deployment no Azure DevOps
            deployment = await self.azure.create_deployment({
                'release_id': release_info['azure_release_id'],
                'environment_id': environment,
                'status': 'inProgress'
            })

            # Cria deployment no GitHub
            github_deployment = await self.github.create_deployment({
                'ref': release_info['version'],
                'environment': environment,
                'description': f"Deploying version {release_info['version']} to {environment}"
            })

            # Executa steps de deployment
            deployment_result = await self._execute_deployment_steps(
                release_info,
                environment,
                deployment['id']
            )

            # Atualiza status nos dois sistemas
            await self._update_deployment_status(
                deployment_result,
                deployment['id'],
                github_deployment['id']
            )

            return {
                'deployment_id': deployment['id'],
                'status': deployment_result['status'],
                'environment': environment,
                'details': deployment_result['details']
            }

        except Exception as e:
            self.logger.error(f"Failed to deploy release: {str(e)}")
            raise

    async def rollback_release(self, deployment_info: Dict) -> Dict:
        """Realiza rollback de um deployment"""
        try:
            # Inicia rollback no Azure DevOps
            rollback = await self.azure.create_deployment({
                'release_id': deployment_info['previous_release_id'],
                'environment_id': deployment_info['environment'],
                'status': 'inProgress',
                'is_rollback': True
            })

            # Registra rollback no GitHub
            await self.github.create_deployment_status({
                'deployment_id': deployment_info['github_deployment_id'],
                'state': 'failure',
                'description': 'Deployment rolled back'
            })

            # Executa steps de rollback
            rollback_result = await self._execute_rollback_steps(
                deployment_info,
                rollback['id']
            )

            return {
                'rollback_id': rollback['id'],
                'status': rollback_result['status'],
                'environment': deployment_info['environment'],
                'details': rollback_result['details']
            }

        except Exception as e:
            self.logger.error(f"Failed to rollback release: {str(e)}")
            raise

    async def monitor_deployment(self, deployment_info: Dict) -> Dict:
        """Monitora status de um deployment"""
        try:
            # Obtém status no Azure DevOps
            azure_status = await self.azure.get_deployment_status(
                deployment_info['deployment_id']
            )

            # Obtém status no GitHub
            github_status = await self.github.get_deployment_status(
                deployment_info['github_deployment_id']
            )

            # Coleta métricas de deployment
            metrics = await self._collect_deployment_metrics(deployment_info)

            return {
                'deployment_id': deployment_info['deployment_id'],
                'status': azure_status['status'],
                'environment': deployment_info['environment'],
                'start_time': azure_status['startTime'],
                'end_time': azure_status.get('endTime'),
                'duration': metrics['duration'],
                'success_rate': metrics['success_rate'],
                'errors': metrics['errors']
            }

        except Exception as e:
            self.logger.error(f"Failed to monitor deployment: {str(e)}")
            raise

    async def _execute_deployment_steps(
        self,
        release_info: Dict,
        environment: str,
        deployment_id: str
    ) -> Dict:
        """Executa os passos do deployment"""
        try:
            steps = [
                self._validate_environment,
                self._deploy_infrastructure,
                self._deploy_application,
                self._run_smoke_tests,
                self._update_configuration
            ]

            results = []
            for step in steps:
                step_result = await step(release_info, environment, deployment_id)
                results.append(step_result)
                
                if not step_result['success']:
                    return {
                        'status': 'failed',
                        'details': {
                            'failed_step': step.__name__,
                            'error': step_result['error'],
                            'steps_completed': len(results)
                        }
                    }

            return {
                'status': 'succeeded',
                'details': {
                    'steps_completed': len(steps),
                    'duration': sum(r['duration'] for r in results),
                    'results': results
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to execute deployment steps: {str(e)}")
            raise

    async def _execute_rollback_steps(self, deployment_info: Dict, rollback_id: str) -> Dict:
        """Executa os passos do rollback"""
        try:
            steps = [
                self._restore_backup,
                self._rollback_infrastructure,
                self._rollback_application,
                self._verify_rollback
            ]

            results = []
            for step in steps:
                step_result = await step(deployment_info, rollback_id)
                results.append(step_result)
                
                if not step_result['success']:
                    return {
                        'status': 'failed',
                        'details': {
                            'failed_step': step.__name__,
                            'error': step_result['error'],
                            'steps_completed': len(results)
                        }
                    }

            return {
                'status': 'succeeded',
                'details': {
                    'steps_completed': len(steps),
                    'duration': sum(r['duration'] for r in results),
                    'results': results
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to execute rollback steps: {str(e)}")
            raise

    async def _collect_deployment_metrics(self, deployment_info: Dict) -> Dict:
        """Coleta métricas do deployment"""
        try:
            # Coleta métricas básicas
            metrics = {
                'duration': 0,
                'success_rate': 0,
                'errors': []
            }

            # Obtém logs do deployment
            logs = await self.azure.get_deployment_logs(deployment_info['deployment_id'])

            # Analisa duração
            if logs:
                start_time = datetime.fromisoformat(logs[0]['timestamp'])
                end_time = datetime.fromisoformat(logs[-1]['timestamp'])
                metrics['duration'] = (end_time - start_time).total_seconds()

            # Analisa erros
            error_logs = [log for log in logs if log['level'] == 'Error']
            metrics['errors'] = [{'message': log['message'], 'timestamp': log['timestamp']}
                               for log in error_logs]

            # Calcula taxa de sucesso
            total_steps = len(logs)
            failed_steps = len(error_logs)
            metrics['success_rate'] = ((total_steps - failed_steps) / total_steps * 100
                                     if total_steps > 0 else 0)

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect deployment metrics: {str(e)}")
            raise