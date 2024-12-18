# integrations/monitoring/metrics_manager.py
from typing import Dict, List, Optional, Union
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import aiohttp

class MetricType(Enum):
    PIPELINE = "pipeline"
    DEPLOYMENT = "deployment"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    SECURITY = "security"

class MetricsManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)
        
    async def collect_metrics(self, project_info: Dict, metric_types: List[MetricType]) -> Dict:
        """Coleta métricas do projeto"""
        try:
            metrics = {}
            
            collection_tasks = []
            for metric_type in metric_types:
                if metric_type == MetricType.PIPELINE:
                    collection_tasks.append(self._collect_pipeline_metrics(project_info))
                elif metric_type == MetricType.DEPLOYMENT:
                    collection_tasks.append(self._collect_deployment_metrics(project_info))
                elif metric_type == MetricType.PERFORMANCE:
                    collection_tasks.append(self._collect_performance_metrics(project_info))
                elif metric_type == MetricType.QUALITY:
                    collection_tasks.append(self._collect_quality_metrics(project_info))
                elif metric_type == MetricType.SECURITY:
                    collection_tasks.append(self._collect_security_metrics(project_info))

            results = await asyncio.gather(*collection_tasks)
            
            for metric_type, result in zip(metric_types, results):
                metrics[metric_type.value] = result

            return {
                'project_id': project_info['id'],
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {str(e)}")
            raise

    async def _collect_pipeline_metrics(self, project_info: Dict) -> Dict:
        """Coleta métricas de pipeline"""
        try:
            # Coleta dados do último mês
            start_date = datetime.utcnow() - timedelta(days=30)
            
            # Azure DevOps pipelines
            azure_builds = await self.azure.get_builds(
                project_info['azure_project'],
                start_date
            )
            
            # GitHub Actions
            github_runs = await self.github.get_workflow_runs(
                project_info['github_repo'],
                start_date
            )
            
            metrics = {
                'total_runs': len(azure_builds) + len(github_runs),
                'success_rate': self._calculate_success_rate(azure_builds, github_runs),
                'average_duration': self._calculate_average_duration(azure_builds, github_runs),
                'failure_analysis': self._analyze_failures(azure_builds, github_runs),
                'trending': self._analyze_pipeline_trends(azure_builds, github_runs)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect pipeline metrics: {str(e)}")
            raise

    async def _collect_deployment_metrics(self, project_info: Dict) -> Dict:
        """Coleta métricas de deployment"""
        try:
            # Coleta dados do último mês
            start_date = datetime.utcnow() - timedelta(days=30)
            
            # Azure DevOps releases
            azure_releases = await self.azure.get_releases(
                project_info['azure_project'],
                start_date
            )
            
            # GitHub deployments
            github_deployments = await self.github.get_deployments(
                project_info['github_repo'],
                start_date
            )
            
            metrics = {
                'total_deployments': len(azure_releases) + len(github_deployments),
                'success_rate': self._calculate_deployment_success_rate(
                    azure_releases,
                    github_deployments
                ),
                'average_lead_time': self._calculate_lead_time(
                    azure_releases,
                    github_deployments
                ),
                'rollback_rate': self._calculate_rollback_rate(
                    azure_releases,
                    github_deployments
                ),
                'environment_metrics': self._analyze_environment_metrics(
                    azure_releases,
                    github_deployments
                )
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect deployment metrics: {str(e)}")
            raise

    async def _collect_performance_metrics(self, project_info: Dict) -> Dict:
        """Coleta métricas de performance"""
        try:
            builds = await self.azure.get_builds(project_info['azure_project'])
            test_results = await self.azure.get_test_results(project_info['azure_project'])
            
            metrics = {
                'build_performance': {
                    'average_duration': self._calculate_build_duration(builds),
                    'success_rate': self._calculate_build_success_rate(builds),
                    'resource_usage': self._analyze_resource_usage(builds)
                },
                'test_performance': {
                    'execution_time': self._calculate_test_execution_time(test_results),
                    'parallel_execution_rate': self._calculate_parallel_execution_rate(test_results),
                    'resource_consumption': self._analyze_test_resource_consumption(test_results)
                },
                'bottlenecks': self._identify_performance_bottlenecks(builds, test_results)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics: {str(e)}")
            raise

    async def _collect_quality_metrics(self, project_info: Dict) -> Dict:
        """Coleta métricas de qualidade"""
        try:
            code_coverage = await self.azure.get_code_coverage(project_info['azure_project'])
            test_results = await self.azure.get_test_results(project_info['azure_project'])
            code_analysis = await self.azure.get_code_analysis_results(project_info['azure_project'])
            
            metrics = {
                'code_coverage': {
                    'overall_coverage': code_coverage['overall'],
                    'coverage_by_component': code_coverage['by_component'],
                    'trend': code_coverage['trend']
                },
                'test_quality': {
                    'pass_rate': self._calculate_test_pass_rate(test_results),
                    'stability': self._analyze_test_stability(test_results),
                    'coverage_quality': self._analyze_coverage_quality(code_coverage)
                },
                'code_quality': {
                    'issues_density': self._calculate_issues_density(code_analysis),
                    'maintainability_index': self._calculate_maintainability_index(code_analysis),
                    'duplications': self._analyze_code_duplications(code_analysis)
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect quality metrics: {str(e)}")
            raise

    async def _collect_security_metrics(self, project_info: Dict) -> Dict:
        """Coleta métricas de segurança"""
        try:
            security_scans = await self.azure.get_security_scans(project_info['azure_project'])
            dependency_scans = await self.github.get_dependency_alerts(project_info['github_repo'])
            
            metrics = {
                'vulnerabilities': {
                    'total': len(security_scans) + len(dependency_scans),
                    'by_severity': self._group_by_severity(security_scans, dependency_scans),
                    'trend': self._analyze_vulnerability_trend(security_scans, dependency_scans)
                },
                'dependency_health': {
                    'outdated_dependencies': self._analyze_outdated_dependencies(dependency_scans),
                    'vulnerability_exposure': self._calculate_vulnerability_exposure(dependency_scans),
                    'update_compliance': self._calculate_update_compliance(dependency_scans)
                },
                'security_compliance': {
                    'policy_violations': self._analyze_policy_violations(security_scans),
                    'compliance_score': self._calculate_compliance_score(security_scans),
                    'risk_assessment': self._assess_security_risk(security_scans, dependency_scans)
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect security metrics: {str(e)}")
            raise

    def _calculate_success_rate(self, azure_builds: List[Dict], github_runs: List[Dict]) -> float:
        """Calcula taxa de sucesso de builds/runs"""
        total = len(azure_builds) + len(github_runs)
        if total == 0:
            return 0.0
            
        successful = (
            len([b for b in azure_builds if b['result'] == 'succeeded']) +
            len([r for r in github_runs if r['conclusion'] == 'success'])
        )
        
        return (successful / total) * 100

    def _calculate_average_duration(self, azure_builds: List[Dict], github_runs: List[Dict]) -> float:
        """Calcula duração média de builds/runs"""
        durations = []
        
        for build in azure_builds:
            if build.get('startTime') and build.get('finishTime'):
                start = datetime.fromisoformat(build['startTime'])
                finish = datetime.fromisoformat(build['finishTime'])
                durations.append((finish - start).total_seconds())
                
        for run in github_runs:
            if run.get('started_at') and run.get('completed_at'):
                start = datetime.fromisoformat(run['started_at'])
                finish = datetime.fromisoformat(run['completed_at'])
                durations.append((finish - start).total_seconds())
                
        return sum(durations) / len(durations) if durations else 0.0

    def _analyze_failures(self, azure_builds: List[Dict], github_runs: List[Dict]) -> Dict:
        """Analisa falhas em builds/runs"""
        failures = {
            'by_type': {},
            'by_stage': {},
            'most_common': []
        }
        
        # Análise de builds do Azure
        for build in azure_builds:
            if build['result'] != 'succeeded':
                failure_type = build.get('reason', 'unknown')
                failures['by_type'][failure_type] = failures['by_type'].get(failure_type, 0) + 1
                
                if 'timeline' in build:
                    for record in build['timeline'].get('records', []):
                        if record.get('result') != 'succeeded':
                            stage = record.get('name', 'unknown')
                            failures['by_stage'][stage] = failures['by_stage'].get(stage, 0) + 1
                            
        # Análise de runs do GitHub
        for run in github_runs:
            if run['conclusion'] != 'success':
                failure_type = run.get('conclusion', 'unknown')
                failures['by_type'][failure_type] = failures['by_type'].get(failure_type, 0) + 1
                
        # Identifica falhas mais comuns
        failures['most_common'] = sorted(
            failures['by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return failures