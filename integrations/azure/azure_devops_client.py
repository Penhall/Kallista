# integrations/azure/azure_devops_client.py
from typing import Dict, List, Optional
import aiohttp
import asyncio
import base64
import logging
from datetime import datetime

class AzureDevOpsClient:
    def __init__(self, organization: str, project: str, pat: str):
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis"
        self.auth = base64.b64encode(f":{pat}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    async def create_pipeline(self, config: Dict) -> Dict:
        """Cria uma nova pipeline"""
        url = f"{self.base_url}/pipelines?api-version=6.0"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=config) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Pipeline created successfully: {result['id']}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create pipeline: {error}")
                    raise Exception(f"Failed to create pipeline: {error}")

    async def create_pull_request(self, config: Dict) -> Dict:
        """Cria um novo Pull Request"""
        url = f"{self.base_url}/git/repositories/{config['repository_id']}/pullrequests?api-version=6.0"
        
        pr_config = {
            "sourceRefName": f"refs/heads/{config['source_branch']}",
            "targetRefName": f"refs/heads/{config['target_branch']}",
            "title": config['title'],
            "description": config['description']
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=pr_config) as response:
                if response.status == 201:
                    result = await response.json()
                    self.logger.info(f"PR created successfully: {result['pullRequestId']}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create PR: {error}")
                    raise Exception(f"Failed to create PR: {error}")

    async def get_build_status(self, build_id: int) -> Dict:
        """Obtém status de uma build"""
        url = f"{self.base_url}/build/builds/{build_id}?api-version=6.0"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to get build status: {error}")
                    raise Exception(f"Failed to get build status: {error}")

    async def create_work_item(self, work_item_type: str, config: Dict) -> Dict:
        """Cria um novo work item"""
        url = f"{self.base_url}/wit/workitems/${work_item_type}?api-version=6.0"
        
        operations = []
        for field, value in config.items():
            operations.append({
                "op": "add",
                "path": f"/fields/System.{field}",
                "value": value
            })
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=operations) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Work item created successfully: {result['id']}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create work item: {error}")
                    raise Exception(f"Failed to create work item: {error}")

    async def update_release(self, release_id: int, config: Dict) -> Dict:
        """Atualiza uma release"""
        url = f"{self.base_url}/release/releases/{release_id}?api-version=6.0"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.patch(url, json=config) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Release updated successfully: {release_id}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to update release: {error}")
                    raise Exception(f"Failed to update release: {error}")

    async def get_test_results(self, run_id: int) -> List[Dict]:
        """Obtém resultados de testes"""
        url = f"{self.base_url}/test/runs/{run_id}/results?api-version=6.0"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to get test results: {error}")
                    raise Exception(f"Failed to get test results: {error}")

    async def create_branch_policy(self, config: Dict) -> Dict:
        """Cria uma política de branch"""
        url = f"{self.base_url}/policy/configurations?api-version=6.0"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=config) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Branch policy created successfully")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create branch policy: {error}")
                    raise Exception(f"Failed to create branch policy: {error}")

    async def update_build_definition(self, definition_id: int, config: Dict) -> Dict:
        """Atualiza uma definição de build"""
        url = f"{self.base_url}/build/definitions/{definition_id}?api-version=6.0"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.put(url, json=config) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Build definition updated successfully")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to update build definition: {error}")
                    raise Exception(f"Failed to update build definition: {error}")