# integrations/policy/branch_policy_manager.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime

class BranchPolicyManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)

    async def setup_branch_policies(self, config: Dict) -> Dict:
        """Configura políticas de branch"""
        try:
            results = {}
            
            # Configura políticas no GitHub
            if config.get('github_policies'):
                github_result = await self._setup_github_policies(config['github_policies'])
                results['github'] = github_result
                
            # Configura políticas no Azure DevOps
            if config.get('azure_policies'):
                azure_result = await self._setup_azure_policies(config['azure_policies'])
                results['azure'] = azure_result
            
            return {
                'status': 'configured',
                'timestamp': datetime.utcnow().isoformat(),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup branch policies: {str(e)}")
            raise

    async def _setup_github_policies(self, policies: Dict) -> Dict:
        """Configura políticas no GitHub"""
        try:
            results = []
            
            for branch, policy in policies.items():
                protection = await self.github.update_branch_protection(branch, {
                    'required_status_checks': policy.get('status_checks', {
                        'strict': True,
                        'contexts': ['continuous-integration']
                    }),
                    'enforce_admins': policy.get('enforce_admins', True),
                    'required_pull_request_reviews': policy.get('review_requirements', {
                        'required_approving_review_count': 1,
                        'dismiss_stale_reviews': True,
                        'require_code_owner_reviews': True
                    }),
                    'restrictions': policy.get('restrictions', None)
                })
                
                results.append({
                    'branch': branch,
                    'status': 'configured',
                    'protection': protection
                })
            
            return {
                'status': 'success',
                'configured_branches': len(results),
                'details': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup GitHub policies: {str(e)}")
            raise

    async def _setup_azure_policies(self, policies: Dict) -> Dict:
        """Configura políticas no Azure DevOps"""
        try:
            results = []
            
            for branch, policy in policies.items():
                # Política de build
                if policy.get('build_validation'):
                    build_policy = await self.azure.create_branch_policy({
                        'type': 'build',
                        'settings': {
                            'buildDefinitionId': policy['build_validation']['definition_id'],
                            'displayName': f"Build Validation - {branch}",
                            'filenamePrefixes': policy['build_validation'].get('paths', []),
                            'scope': [{'refName': f"refs/heads/{branch}"}]
                        }
                    })
                    results.append({
                        'type': 'build',
                        'branch': branch,
                        'status': 'configured'
                    })
                
                # Política de revisão
                if policy.get('review_requirements'):
                    review_policy = await self.azure.create_branch_policy({
                        'type': 'reviewers',
                        'settings': {
                            'minimumApproverCount': policy['review_requirements'].get('min_reviewers', 1),
                            'creatorVoteCounts': False,
                            'resetOnSourcePush': True,
                            'scope': [{'refName': f"refs/heads/{branch}"}]
                        }
                    })
                    results.append({
                        'type': 'review',
                        'branch': branch,
                        'status': 'configured'
                    })
            
            return {
                'status': 'success',
                'configured_policies': len(results),
                'details': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to setup Azure policies: {str(e)}")
            raise