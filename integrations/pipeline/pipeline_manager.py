# integrations/pipeline/pipeline_manager.py
from typing import Dict, List, Optional
from enum import Enum
import asyncio
import logging
from datetime import datetime

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)

    async def setup_ci_pipeline(self, config: Dict) -> Dict:
        """Configura pipeline de CI completo"""
        try:
            # Cria pipeline no Azure DevOps
            pipeline = await self.azure.create_pipeline(config['pipeline_config'])
            
            # Configura branch policies
            await self.azure.create_branch_policy(config['policy_config'])
            
            # Configura proteções no GitHub
            await self.github.update_branch_protection(
                config['branch'],
                config['protection_config']
            )
            
            return {
                "pipeline_id": pipeline['id'],
                "status": "configured",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup CI pipeline: {str(e)}")
            raise

    async def trigger_build(self, config: Dict) -> Dict:
        """Inicia uma nova build"""
        try:
            # Cria branch se necessário
            if config.get('create_branch'):
                await self.github.create_branch(
                    config['branch_name'],
                    config['base_branch']
                )
            
            # Inicia build no Azure DevOps
            build = await self.azure.create_pipeline(config['build_config'])
            
            # Cria check run no GitHub
            check = await self.github.create_check_run({
                "name": config['check_name'],
                "head_sha": config['commit_sha'],
                "status": "in_progress"
            })
            
            return {
                "build_id": build['id'],
                "check_id": check['id'],
                "status": PipelineStatus.RUNNING.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to trigger build: {str(e)}")
            raise

    async def monitor_build(self, build_id: int, check_id: Optional[int] = None) -> Dict:
        """Monitora status de uma build"""
        try:
            status = await self.azure.get_build_status(build_id)
            
            if check_id:
                # Atualiza status no GitHub
                await self.github.create_check_run({
                    "name": status['definition']['name'],
                    "head_sha": status['sourceVersion'],
                    "status": "completed",
                    "conclusion": "success" if status['result'] == "succeeded" else "failure"
                })
            
            return {
                "build_id": build_id,
                "status": status['status'],
                "result": status['result'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor build: {str(e)}")
            raise

    async def create_release(self, config: Dict) -> Dict:
        """Cria uma nova release"""
        try:
            # Cria release no Azure DevOps
            release = await self.azure.update_release(
                config['release_id'],
                config['release_config']
            )
            
            # Cria tag no GitHub
            if config.get('create_tag'):
                await self.github.create_ref(
                    f"refs/tags/{config['tag_name']}",
                    config['commit_sha']
                )
            
            return {
                "release_id": release['id'],
                "status": release['status'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create release: {str(e)}")
            raise