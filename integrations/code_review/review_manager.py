# integrations/code_review/review_manager.py
from typing import Dict, List, Optional
from enum import Enum
import asyncio
import logging
from datetime import datetime

class ReviewStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"

class ReviewManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)

    async def create_review_request(self, config: Dict) -> Dict:
        """Cria solicitação de revisão"""
        try:
            # Cria PR no GitHub
            if config.get('platform') == 'github':
                pr = await self.github.create_pull_request({
                    'title': config['title'],
                    'body': config['description'],
                    'head': config['source_branch'],
                    'base': config['target_branch']
                })
                
                # Adiciona reviewers
                if config.get('reviewers'):
                    await self.github.add_pr_reviewers(pr['number'], config['reviewers'])
                
                # Adiciona labels
                if config.get('labels'):
                    await self.github.add_pr_labels(pr['number'], config['labels'])
                
                return {
                    'pr_number': pr['number'],
                    'status': ReviewStatus.PENDING.value,
                    'platform': 'github',
                    'url': pr['html_url']
                }
                
            # Cria PR no Azure DevOps
            else:
                pr = await self.azure.create_pull_request({
                    'repository_id': config['repository_id'],
                    'source_branch': config['source_branch'],
                    'target_branch': config['target_branch'],
                    'title': config['title'],
                    'description': config['description']
                })
                
                return {
                    'pr_number': pr['pullRequestId'],
                    'status': ReviewStatus.PENDING.value,
                    'platform': 'azure',
                    'url': pr['url']
                }
        
        except Exception as e:
            self.logger.error(f"Failed to create review request: {str(e)}")
            raise

    async def automate_code_review(self, pr_info: Dict) -> Dict:
        """Realiza revisão automatizada de código"""
        try:
            # Define conjunto de checagens
            checks = {
                'style': self._check_code_style,
                'complexity': self._check_code_complexity,
                'security': self._check_security,
                'tests': self._check_tests,
                'coverage': self._check_coverage
            }
            
            results = {}
            issues = []
            
            # Executa checagens
            for check_name, check_func in checks.items():
                check_result = await check_func(pr_info)
                results[check_name] = check_result['status']
                if check_result.get('issues'):
                    issues.extend(check_result['issues'])
            
            # Determina resultado final
            status = ReviewStatus.APPROVED.value
            if any(result == 'failed' for result in results.values()):
                status = ReviewStatus.CHANGES_REQUESTED.value
            
            # Adiciona comentários com issues encontradas
            if issues:
                await self._add_review_comments(pr_info, issues)
            
            return {
                'pr_number': pr_info['pr_number'],
                'status': status,
                'results': results,
                'issues_count': len(issues)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to automate code review: {str(e)}")
            raise

    async def monitor_review_status(self, pr_info: Dict) -> Dict:
        """Monitora status de revisão"""
        try:
            if pr_info['platform'] == 'github':
                reviews = await self.github.get_pull_request_reviews(pr_info['pr_number'])
            else:
                reviews = await self.azure.get_pull_request_reviews(pr_info['pr_number'])
            
            approved_count = sum(1 for r in reviews if r['state'] == 'APPROVED')
            changes_requested = any(r['state'] == 'CHANGES_REQUESTED' for r in reviews)
            
            status = ReviewStatus.IN_REVIEW.value
            if changes_requested:
                status = ReviewStatus.CHANGES_REQUESTED.value
            elif approved_count >= pr_info.get('required_approvals', 1):
                status = ReviewStatus.APPROVED.value
            
            return {
                'pr_number': pr_info['pr_number'],
                'status': status,
                'approved_count': approved_count,
                'total_reviews': len(reviews)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor review status: {str(e)}")
            raise

    async def _check_code_style(self, pr_info: Dict) -> Dict:
        """Verifica estilo de código"""
        # Implementação específica de verificação de estilo
        pass

    async def _check_code_complexity(self, pr_info: Dict) -> Dict:
        """Verifica complexidade do código"""
        # Implementação específica de verificação de complexidade
        pass

    async def _check_security(self, pr_info: Dict) -> Dict:
        """Verifica problemas de segurança"""
        # Implementação específica de verificação de segurança
        pass

    async def _check_tests(self, pr_info: Dict) -> Dict:
        """Verifica testes"""
        # Implementação específica de verificação de testes
        pass

    async def _check_coverage(self, pr_info: Dict) -> Dict:
        """Verifica cobertura de código"""
        # Implementação específica de verificação de cobertura
        pass

    async def _add_review_comments(self, pr_info: Dict, issues: List[Dict]):
        """Adiciona comentários de revisão"""
        try:
            for issue in issues:
                comment = self._format_issue_comment(issue)
                if pr_info['platform'] == 'github':
                    await self.github.create_review_comment(
                        pr_info['pr_number'],
                        comment,
                        issue['file'],
                        issue['line']
                    )
                else:
                    await self.azure.create_thread(
                        pr_info['pr_number'],
                        comment,
                        issue['file'],
                        issue['line']
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to add review comments: {str(e)}")
            raise

    def _format_issue_comment(self, issue: Dict) -> str:
        """Formata comentário de issue"""
        return f"""
**{issue['type']}**: {issue['title']}

{issue['description']}

Sugestão: {issue['suggestion']}
        """.strip()