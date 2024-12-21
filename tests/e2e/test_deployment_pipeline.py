# tests/e2e/test_deployment_pipeline.py

import unittest
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from kallista.integrations.azure import AzureDevOpsClient
from kallista.integrations.github import GitHubClient
from kallista.integrations.nuget import (
    PackageManager,
    FeedManager,
    VersionManager
)
from kallista.integrations.deployment import ReleaseManager
from kallista.integrations.pipeline import PipelineManager
from kallista.tools.testing import TestRunner
from kallista.tools.security import SecurityScanner
from kallista.tools.code import CodeQualityAnalyzer
from kallista.core.management import StateManager, ContextManager

class TestDeploymentPipeline(unittest.TestCase):
    """End-to-end tests for deployment pipeline."""

    async def asyncSetUp(self):
        """Setup test environment."""
        # Initialize managers
        self.state_manager = StateManager()
        self.context_manager = ContextManager()
        await self.state_manager.initialize()
        await self.context_manager.initialize()
        
        # Initialize clients
        self.azure_client = AzureDevOpsClient()
        self.github_client = GitHubClient()
        
        # Initialize managers
        self.package_manager = PackageManager()
        self.feed_manager = FeedManager()
        self.version_manager = VersionManager()
        self.release_manager = ReleaseManager()
        self.pipeline_manager = PipelineManager()
        
        # Initialize tools
        self.test_runner = TestRunner()
        self.security_scanner = SecurityScanner()
        self.code_analyzer = CodeQualityAnalyzer()
        
        # Setup test project
        self.test_dir = Path('./TestDeployProject')
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        
        # Setup test configuration
        self.project_config = {
            'name': 'TestDeployProject',
            'version': '1.0.0',
            'repository': {
                'type': 'github',
                'owner': 'test-org',
                'name': 'test-repo',
                'branch': 'main'
            },
            'pipeline': {
                'type': 'azure-devops',
                'organization': 'test-org',
                'project': 'test-project'
            },
            'artifacts': {
                'type': 'nuget',
                'feed': 'test-feed'
            }
        }

    async def asyncTearDown(self):
        """Cleanup test environment."""
        await self.state_manager.cleanup()
        await self.context_manager.cleanup()
        
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    async def test_001_complete_deployment_pipeline(self):
        """Test complete deployment pipeline from code to production."""
        # 1. Source Control Integration
        repo_result = await self.github_client.setup_repository({
            'name': self.project_config['name'],
            'private': True,
            'init': True,
            'branch': 'main'
        })
        self.assertTrue(repo_result['success'])
        self.assertIn('clone_url', repo_result)
        
        # Clone repository
        clone_result = await self.github_client.clone_repository(
            repo_result['clone_url'],
            self.test_dir
        )
        self.assertTrue(clone_result['success'])
        
        # 2. Setup Azure Pipeline
        pipeline_config = {
            'name': f"{self.project_config['name']}-pipeline",
            'trigger': ['main'],
            'pr_trigger': ['main'],
            'stages': ['build', 'test', 'package', 'deploy'],
            'environments': ['dev', 'staging', 'prod']
        }
        
        pipeline_result = await self.pipeline_manager.create_pipeline(pipeline_config)
        self.assertTrue(pipeline_result['success'])
        self.assertIn('id', pipeline_result)
        
        # 3. Configure Build Stage
        build_config = {
            'solution': '**/*.sln',
            'configuration': 'Release',
            'platform': 'Any CPU',
            'restore': True,
            'tests': True
        }
        
        build_result = await self.pipeline_manager.configure_build(
            pipeline_result['id'],
            build_config
        )
        self.assertTrue(build_result['success'])
        
        # 4. Configure Testing Stage
        test_config = {
            'frameworks': ['xUnit'],
            'coverage': True,
            'parallel': True,
            'categories': ['Unit', 'Integration', 'E2E']
        }
        
        test_result = await self.pipeline_manager.configure_testing(
            pipeline_result['id'],
            test_config
        )
        self.assertTrue(test_result['success'])
        
        # 5. Configure Package Stage
        package_config = {
            'type': 'nuget',
            'version': self.project_config['version'],
            'metadata': {
                'authors': 'Test Author',
                'description': 'Test Package',
                'tags': ['wpf', 'test']
            }
        }
        
        package_result = await self.package_manager.configure_packaging(
            pipeline_result['id'],
            package_config
        )
        self.assertTrue(package_result['success'])
        
        # 6. Configure Deployment Stage
        deploy_config = {
            'environments': {
                'dev': {
                    'auto_deploy': True,
                    'approvers': []
                },
                'staging': {
                    'auto_deploy': False,
                    'approvers': ['test-approver']
                },
                'prod': {
                    'auto_deploy': False,
                    'approvers': ['test-approver'],
                    'conditions': ['successful-staging']
                }
            },
            'variables': {
                'Configuration': 'Release',
                'DeploymentType': 'ClickOnce'
            }
        }
        
        deploy_result = await self.release_manager.configure_deployment(
            pipeline_result['id'],
            deploy_config
        )
        self.assertTrue(deploy_result['success'])
        
        # 7. Setup Quality Gates
        quality_config = {
            'code_coverage': {'minimum': 80},
            'code_quality': {
                'duplicate_lines': {'maximum': 5},
                'cyclomatic_complexity': {'maximum': 10}
            },
            'security': {
                'critical_vulnerabilities': {'maximum': 0},
                'high_vulnerabilities': {'maximum': 0}
            },
            'performance': {
                'startup_time': {'maximum': 2000},
                'memory_usage': {'maximum': 200}
            }
        }
        
        quality_result = await self.pipeline_manager.configure_quality_gates(
            pipeline_result['id'],
            quality_config
        )
        self.assertTrue(quality_result['success'])
        
        # 8. Run Complete Pipeline
        run_config = {
            'branch': 'main',
            'variables': {
                'BuildConfiguration': 'Release',
                'NuGetFeed': self.project_config['artifacts']['feed']
            },
            'artifacts': {
                'build': '**/*.dll',
                'test': '**/*.trx',
                'package': '**/*.nupkg'
            }
        }
        
        pipeline_run = await self.pipeline_manager.run_pipeline(
            pipeline_result['id'],
            run_config
        )
        self.assertTrue(pipeline_run['success'])
        
        # 9. Monitor Pipeline Progress
        stages = ['build', 'test', 'package', 'deploy']
        for stage in stages:
            stage_result = await self.pipeline_manager.wait_for_stage(
                pipeline_run['id'],
                stage,
                timeout=1800  # 30 minutes
            )
            self.assertEqual(stage_result['status'], 'succeeded')
            
            if stage == 'test':
                # Verify test results
                test_results = await self.test_runner.get_test_results(
                    pipeline_run['id']
                )
                self.assertTrue(test_results['success'])
                self.assertEqual(test_results['failed'], 0)
                self.assertGreater(test_results['passed'], 0)
                
                # Verify code coverage
                coverage = await self.test_runner.get_code_coverage(
                    pipeline_run['id']
                )
                self.assertGreaterEqual(coverage['percentage'], 80)
            
            elif stage == 'package':
                # Verify package creation
                package = await self.package_manager.get_package(
                    self.project_config['name'],
                    self.project_config['version']
                )
                self.assertIsNotNone(package)
                self.assertEqual(package['status'], 'available')

    async def test_002_deployment_environments(self):
        """Test deployment to different environments."""
        # 1. Setup deployment configurations
        environments = ['dev', 'staging', 'prod']
        
        for env in environments:
            config = {
                'environment': env,
                'artifact_version': self.project_config['version'],
                'configuration': {
                    'ConnectionStrings': {
                        'DefaultConnection': f'Server=server-{env};Database=db-{env}'
                    },
                    'AppSettings': {
                        'Environment': env.upper(),
                        'ApiUrl': f'https://api-{env}.example.com'
                    }
                }
            }
            
            # Deploy to environment
            deploy_result = await self.release_manager.deploy_to_environment(
                config
            )
            self.assertTrue(deploy_result['success'])
            
            # Verify deployment
            verification = await self.release_manager.verify_deployment(
                env,
                self.project_config['version']
            )
            self.assertTrue(verification['success'])
            
            # Run smoke tests
            smoke_test = await self.test_runner.run_smoke_tests(env)
            self.assertTrue(smoke_test['success'])
            
            if env != 'dev':
                # Verify approvals for non-dev environments
                approvals = await self.release_manager.get_approvals(deploy_result['id'])
                self.assertTrue(approvals['completed'])
                self.assertEqual(approvals['status'], 'approved')

    async def test_003_rollback_scenario(self):
        """Test rollback scenario in case of deployment issues."""
        # 1. Setup problematic deployment
        problem_config = {
            'environment': 'staging',
            'artifact_version': self.project_config['version'],
            'configuration': {
                'ConnectionStrings': {
                    'DefaultConnection': 'invalid-connection-string'
                }
            }
        }
        
        # 2. Deploy problematic version
        deploy_result = await self.release_manager.deploy_to_environment(
            problem_config
        )
        self.assertTrue(deploy_result['success'])
        
        # 3. Verify deployment failure
        verification = await self.release_manager.verify_deployment(
            'staging',
            self.project_config['version']
        )
        self.assertFalse(verification['success'])
        
        # 4. Trigger rollback
        rollback_result = await self.release_manager.rollback_deployment(
            'staging',
            deploy_result['id']
        )
        self.assertTrue(rollback_result['success'])
        
        # 5. Verify rollback
        rollback_verification = await self.release_manager.verify_deployment(
            'staging',
            rollback_result['version']
        )
        self.assertTrue(rollback_verification['success'])
        
        # 6. Check system health after rollback
        health_check = await self.release_manager.check_system_health('staging')
        self.assertTrue(health_check['healthy'])

    async def test_004_continuous_deployment(self):
        """Test continuous deployment workflow."""
        # 1. Setup continuous deployment
        cd_config = {
            'environments': ['dev'],
            'triggers': ['main'],
            'automatic': True,
            'conditions': {
                'test_pass_rate': 100,
                'code_coverage': 80,
                'no_critical_issues': True
            }
        }
        
        cd_result = await self.pipeline_manager.setup_continuous_deployment(
            cd_config
        )
        self.assertTrue(cd_result['success'])
        
        # 2. Make code change
        change = {
            'file': 'README.md',
            'content': f'Updated on {datetime.now().isoformat()}'
        }
        
        commit_result = await self.github_client.commit_change(
            self.project_config['repository']['name'],
            change,
            'Update README.md'
        )
        self.assertTrue(commit_result['success'])
        
        # 3. Wait for automatic deployment
        deployment = await self.pipeline_manager.wait_for_deployment(
            'dev',
            timeout=900  # 15 minutes
        )
        self.assertTrue(deployment['success'])
        
        # 4. Verify automatic deployment
        verification = await self.release_manager.verify_deployment(
            'dev',
            deployment['version']
        )
        self.assertTrue(verification['success'])

def run_async_test(coro):
    """Helper to run async tests."""
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == '__main__':
    unittest.main()