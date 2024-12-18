# integrations/github/github_client.py
from typing import Dict, List, Optional
import aiohttp
import asyncio
from datetime import datetime
import logging

class GitHubClient:
    def __init__(self, token: str, repo: str, owner: str):
        self.base_url = "https://api.github.com"
        self.token = token
        self.repo = repo
        self.owner = owner
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.logger = logging.getLogger(__name__)

    async def create_pull_request(self, config: Dict) -> Dict:
        """Cria um novo Pull Request"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        data = {
            "title": config['title'],
            "body": config['body'],
            "head": config['head'],
            "base": config['base'],
            "maintainer_can_modify": True
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    pr = await response.json()
                    self.logger.info(f"PR created successfully: #{pr['number']}")
                    return pr
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create PR: {error}")
                    raise Exception(f"Failed to create PR: {error}")

    async def add_pr_reviewers(self, pr_number: int, reviewers: List[str]) -> Dict:
        """Adiciona reviewers ao PR"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/requested_reviewers"
        data = {"reviewers": reviewers}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    self.logger.info(f"Reviewers added to PR #{pr_number}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to add reviewers: {error}")
                    raise Exception(f"Failed to add reviewers: {error}")

    async def add_pr_labels(self, pr_number: int, labels: List[str]) -> Dict:
        """Adiciona labels ao PR"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{pr_number}/labels"
        data = {"labels": labels}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Labels added to PR #{pr_number}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to add labels: {error}")
                    raise Exception(f"Failed to add labels: {error}")

    async def create_branch(self, branch_name: str, base_ref: str) -> Dict:
        """Cria uma nova branch"""
        # Primeiro, obtém o SHA do commit base
        base_sha = await self._get_ref_sha(base_ref)
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    self.logger.info(f"Branch {branch_name} created successfully")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create branch: {error}")
                    raise Exception(f"Failed to create branch: {error}")

    async def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict:
        """Cria uma nova issue"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        data = {
            "title": title,
            "body": body
        }
        if labels:
            data["labels"] = labels
            
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    issue = await response.json()
                    self.logger.info(f"Issue created successfully: #{issue['number']}")
                    return issue
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create issue: {error}")
                    raise Exception(f"Failed to create issue: {error}")

    async def update_branch_protection(self, branch: str, config: Dict) -> Dict:
        """Atualiza proteções da branch"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/branches/{branch}/protection"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.put(url, json=config) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Branch protection updated for {branch}")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to update branch protection: {error}")
                    raise Exception(f"Failed to update branch protection: {error}")

    async def _get_ref_sha(self, ref: str) -> str:
        """Obtém SHA de uma referência"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs/heads/{ref}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['object']['sha']
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to get ref SHA: {error}")
                    raise Exception(f"Failed to get ref SHA: {error}")

    async def get_pull_requests(self, state: str = "open") -> List[Dict]:
        """Obtém lista de PRs"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        params = {"state": state}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to get PRs: {error}")
                    raise Exception(f"Failed to get PRs: {error}")

    async def create_check_run(self, config: Dict) -> Dict:
        """Cria um check run"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/check-runs"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=config) as response:
                if response.status == 201:
                    result = await response.json()
                    self.logger.info(f"Check run created successfully")
                    return result
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to create check run: {error}")
                    raise Exception(f"Failed to create check run: {error}")