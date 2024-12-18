# integrations/automation/code_analysis_manager.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
import re

class CodeAnalysisManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)

    async def analyze_pull_request(self, pr_info: Dict) -> Dict:
        """Realiza análise completa do código em um PR"""
        try:
            analysis_results = {
                'static_analysis': await self._run_static_analysis(pr_info),
                'code_metrics': await self._calculate_code_metrics(pr_info),
                'dependency_check': await self._check_dependencies(pr_info),
                'security_scan': await self._scan_security_issues(pr_info),
                'test_analysis': await self._analyze_tests(pr_info)
            }

            summary = self._generate_analysis_summary(analysis_results)
            await self._post_analysis_results(pr_info, analysis_results, summary)

            return {
                'pr_number': pr_info['pr_number'],
                'status': 'completed',
                'summary': summary,
                'details': analysis_results
            }

        except Exception as e:
            self.logger.error(f"Failed to analyze pull request: {str(e)}")
            raise

    async def _run_static_analysis(self, pr_info: Dict) -> Dict:
        """Executa análise estática do código"""
        results = {
            'code_style': [],
            'complexity': [],
            'best_practices': [],
            'potential_bugs': []
        }

        try:
            # Análise de estilo de código
            style_issues = await self._analyze_code_style(pr_info)
            results['code_style'].extend(style_issues)

            # Análise de complexidade
            complexity_issues = await self._analyze_complexity(pr_info)
            results['complexity'].extend(complexity_issues)

            # Verificação de boas práticas
            practice_issues = await self._check_best_practices(pr_info)
            results['best_practices'].extend(practice_issues)

            # Detecção de bugs potenciais
            bug_issues = await self._detect_potential_bugs(pr_info)
            results['potential_bugs'].extend(bug_issues)

            return {
                'status': 'completed',
                'total_issues': sum(len(issues) for issues in results.values()),
                'results': results
            }

        except Exception as e:
            self.logger.error(f"Static analysis failed: {str(e)}")
            raise

    async def _calculate_code_metrics(self, pr_info: Dict) -> Dict:
        """Calcula métricas do código"""
        metrics = {
            'lines_changed': 0,
            'files_changed': 0,
            'complexity_score': 0,
            'maintainability_index': 0,
            'test_coverage': 0
        }

        try:
            # Análise de alterações
            changes = await self._analyze_changes(pr_info)
            metrics['lines_changed'] = changes['lines']
            metrics['files_changed'] = changes['files']

            # Cálculo de complexidade
            complexity = await self._calculate_complexity(pr_info)
            metrics['complexity_score'] = complexity['score']

            # Índice de manutenibilidade
            maintainability = await self._calculate_maintainability(pr_info)
            metrics['maintainability_index'] = maintainability['index']

            # Cobertura de testes
            coverage = await self._calculate_test_coverage(pr_info)
            metrics['test_coverage'] = coverage['percentage']

            return {
                'status': 'completed',
                'metrics': metrics,
                'recommendations': self._generate_metrics_recommendations(metrics)
            }

        except Exception as e:
            self.logger.error(f"Code metrics calculation failed: {str(e)}")
            raise

    async def _check_dependencies(self, pr_info: Dict) -> Dict:
        """Verifica dependências do projeto"""
        try:
            dependencies = {
                'outdated': [],
                'vulnerable': [],
                'deprecated': [],
                'recommendations': []
            }

            # Verifica dependências desatualizadas
            outdated = await self._check_outdated_dependencies(pr_info)
            dependencies['outdated'].extend(outdated)

            # Verifica vulnerabilidades
            vulnerable = await self._check_vulnerable_dependencies(pr_info)
            dependencies['vulnerable'].extend(vulnerable)

            # Verifica dependências depreciadas
            deprecated = await self._check_deprecated_dependencies(pr_info)
            dependencies['deprecated'].extend(deprecated)

            # Gera recomendações
            dependencies['recommendations'] = self._generate_dependency_recommendations(dependencies)

            return {
                'status': 'completed',
                'total_issues': sum(len(issues) for issues in dependencies.values()),
                'dependencies': dependencies
            }

        except Exception as e:
            self.logger.error(f"Dependency check failed: {str(e)}")
            raise

    async def _scan_security_issues(self, pr_info: Dict) -> Dict:
        """Realiza varredura de problemas de segurança"""
        try:
            security_issues = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }

            # Análise de segurança estática
            static_issues = await self._run_security_static_analysis(pr_info)
            for issue in static_issues:
                security_issues[issue['severity']].append(issue)

            # Verificação de secrets
            secret_issues = await self._check_secrets(pr_info)
            for issue in secret_issues:
                security_issues[issue['severity']].append(issue)

            # Análise de vulnerabilidades
            vuln_issues = await self._analyze_vulnerabilities(pr_info)
            for issue in vuln_issues:
                security_issues[issue['severity']].append(issue)

            return {
                'status': 'completed',
                'total_issues': sum(len(issues) for issues in security_issues.values()),
                'issues': security_issues,
                'recommendations': self._generate_security_recommendations(security_issues)
            }

        except Exception as e:
            self.logger.error(f"Security scan failed: {str(e)}")
            raise

    async def _analyze_tests(self, pr_info: Dict) -> Dict:
        """Analisa testes do projeto"""
        try:
            test_analysis = {
                'coverage': 0,
                'new_tests': 0,
                'modified_tests': 0,
                'test_quality': {},
                'missing_coverage': []
            }

            # Análise de cobertura
            coverage = await self._analyze_test_coverage(pr_info)
            test_analysis['coverage'] = coverage['percentage']
            test_analysis['missing_coverage'] = coverage['missing_areas']

            # Análise de mudanças em testes
            test_changes = await self._analyze_test_changes(pr_info)
            test_analysis['new_tests'] = test_changes['new']
            test_analysis['modified_tests'] = test_changes['modified']

            # Análise de qualidade dos testes
            test_analysis['test_quality'] = await self._analyze_test_quality(pr_info)

            return {
                'status': 'completed',
                'analysis': test_analysis,
                'recommendations': self._generate_test_recommendations(test_analysis)
            }

        except Exception as e:
            self.logger.error(f"Test analysis failed: {str(e)}")
            raise

    def _generate_analysis_summary(self, results: Dict) -> Dict:
        """Gera sumário da análise"""
        return {
            'total_issues': sum(
                result.get('total_issues', 0) 
                for result in results.values()
                if isinstance(result, dict)
            ),
            'critical_issues': len(results.get('security_scan', {})
                                      .get('issues', {})
                                      .get('critical', [])),
            'code_quality_score': self._calculate_quality_score(results),
            'recommendations': self._prioritize_recommendations(results)
        }

    def _calculate_quality_score(self, results: Dict) -> float:
        """Calcula score de qualidade do código"""
        weights = {
            'maintainability': 0.3,
            'complexity': 0.2,
            'coverage': 0.2,
            'security': 0.3
        }

        scores = {
            'maintainability': results['code_metrics']['metrics']['maintainability_index'] / 100,
            'complexity': max(0, 1 - results['code_metrics']['metrics']['complexity_score'] / 100),
            'coverage': results['code_metrics']['metrics']['test_coverage'] / 100,
            'security': max(0, 1 - len(results['security_scan']['issues']['critical']) / 10)
        }

        return sum(score * weights[metric] for metric, score in scores.items())

    async def _post_analysis_results(self, pr_info: Dict, results: Dict, summary: Dict):
        """Posta resultados da análise no PR"""
        try:
            comment = self._format_analysis_comment(summary, results)
            
            if pr_info['platform'] == 'github':
                await self.github.create_issue_comment(
                    pr_info['pr_number'],
                    comment
                )
            else:
                await self.azure.create_thread(
                    pr_info['pr_number'],
                    comment
                )

        except Exception as e:
            self.logger.error(f"Failed to post analysis results: {str(e)}")
            raise