# integrations/metrics/metrics_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn import metrics

class MetricType(Enum):
    PERFORMANCE = "performance"
    QUALITY = "quality"
    PRODUCTIVITY = "productivity"
    DEPLOYMENT = "deployment"
    COLLABORATION = "collaboration"

class AnalysisType(Enum):
    TRENDS = "trends"
    PATTERNS = "patterns"
    ANOMALIES = "anomalies"
    PREDICTIONS = "predictions"
    CORRELATIONS = "correlations"

class MetricsManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics_path = Path(config.get('metrics_path', 'metrics'))
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        self.metrics_cache: Dict[str, pd.DataFrame] = {}
        self._init_metrics_system()

    def _init_metrics_system(self):
        """Inicializa sistema de métricas"""
        try:
            # Cria diretórios para cada tipo de métrica
            for metric_type in MetricType:
                (self.metrics_path / metric_type.value).mkdir(exist_ok=True)
            
            # Carrega métricas históricas
            self._load_historical_metrics()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics system: {str(e)}")
            raise

    async def collect_metrics(
        self,
        metric_type: MetricType,
        data: Dict
    ) -> Dict:
        """Coleta novas métricas"""
        try:
            timestamp = datetime.utcnow()
            
            # Processa métricas
            processed_metrics = await self._process_metrics(metric_type, data)
            
            # Adiciona timestamp
            processed_metrics['timestamp'] = timestamp.isoformat()
            
            # Salva métricas
            await self._save_metrics(metric_type, processed_metrics)
            
            # Atualiza cache
            await self._update_metrics_cache(metric_type, processed_metrics)
            
            return {
                'type': metric_type.value,
                'timestamp': timestamp.isoformat(),
                'metrics': processed_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {str(e)}")
            raise

    async def analyze_metrics(
        self,
        metric_type: MetricType,
        analysis_type: AnalysisType,
        params: Optional[Dict] = None
    ) -> Dict:
        """Analisa métricas coletadas"""
        try:
            # Carrega métricas do cache
            metrics_df = await self._get_metrics_dataframe(metric_type)
            
            # Realiza análise
            if analysis_type == AnalysisType.TRENDS:
                analysis = await self._analyze_trends(metrics_df, params)
            elif analysis_type == AnalysisType.PATTERNS:
                analysis = await self._analyze_patterns(metrics_df, params)
            elif analysis_type == AnalysisType.ANOMALIES:
                analysis = await self._analyze_anomalies(metrics_df, params)
            elif analysis_type == AnalysisType.PREDICTIONS:
                analysis = await self._analyze_predictions(metrics_df, params)
            elif analysis_type == AnalysisType.CORRELATIONS:
                analysis = await self._analyze_correlations(metrics_df, params)
            
            return {
                'metric_type': metric_type.value,
                'analysis_type': analysis_type.value,
                'timestamp': datetime.utcnow().isoformat(),
                'results': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze metrics: {str(e)}")
            raise

    async def get_metrics_summary(
        self,
        metric_type: Optional[MetricType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Obtém resumo das métricas"""
        try:
            summaries = {}
            
            for mtype in MetricType if not metric_type else [metric_type]:
                metrics_df = await self._get_metrics_dataframe(mtype)
                
                # Aplica filtro de data
                if start_date or end_date:
                    metrics_df = self._filter_by_date(
                        metrics_df,
                        start_date,
                        end_date
                    )
                
                # Calcula estatísticas
                summaries[mtype.value] = {
                    'count': len(metrics_df),
                    'statistics': self._calculate_statistics(metrics_df),
                    'trends': self._calculate_trends(metrics_df)
                }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'summaries': summaries
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {str(e)}")
            raise

    async def _process_metrics(
        self,
        metric_type: MetricType,
        data: Dict
    ) -> Dict:
        """Processa métricas por tipo"""
        if metric_type == MetricType.PERFORMANCE:
            return self._process_performance_metrics(data)
        elif metric_type == MetricType.QUALITY:
            return self._process_quality_metrics(data)
        elif metric_type == MetricType.PRODUCTIVITY:
            return self._process_productivity_metrics(data)
        elif metric_type == MetricType.DEPLOYMENT:
            return self._process_deployment_metrics(data)
        elif metric_type == MetricType.COLLABORATION:
            return self._process_collaboration_metrics(data)
        
        raise ValueError(f"Unsupported metric type: {metric_type}")

    def _process_performance_metrics(self, data: Dict) -> Dict:
        """Processa métricas de performance"""
        return {
            'response_time': np.mean(data.get('response_times', [])),
            'error_rate': len(data.get('errors', [])) / len(data.get('requests', [])),
            'throughput': len(data.get('requests', [])) / data.get('duration', 1),
            'resource_usage': {
                'cpu': np.mean(data.get('cpu_usage', [])),
                'memory': np.mean(data.get('memory_usage', [])),
                'disk': np.mean(data.get('disk_usage', []))
            }
        }

    def _process_quality_metrics(self, data: Dict) -> Dict:
        """Processa métricas de qualidade"""
        return {
            'code_coverage': data.get('coverage', 0),
            'bug_density': len(data.get('bugs', [])) / data.get('loc', 1),
            'technical_debt': {
                'score': data.get('debt_score', 0),
                'issues': len(data.get('debt_issues', []))
            },
            'test_results': {
                'passed': len(data.get('passed_tests', [])),
                'failed': len(data.get('failed_tests', [])),
                'skipped': len(data.get('skipped_tests', []))
            }
        }

    def _process_productivity_metrics(self, data: Dict) -> Dict:
        """Processa métricas de produtividade"""
        return {
            'commits': len(data.get('commits', [])),
            'pull_requests': len(data.get('pull_requests', [])),
            'code_review_time': np.mean(data.get('review_times', [])),
            'issue_resolution_time': np.mean(data.get('resolution_times', [])),
            'velocity': {
                'points': sum(data.get('story_points', [])),
                'tasks': len(data.get('completed_tasks', []))
            }
        }

    def _process_deployment_metrics(self, data: Dict) -> Dict:
        """Processa métricas de deployment"""
        return {
            'frequency': len(data.get('deployments', [])),
            'success_rate': (
                len(data.get('successful_deployments', [])) /
                len(data.get('deployments', []))
            ),
            'lead_time': np.mean(data.get('lead_times', [])),
            'rollback_rate': (
                len(data.get('rollbacks', [])) /
                len(data.get('deployments', []))
            ),
            'time_to_recovery': np.mean(data.get('recovery_times', []))
        }

    def _process_collaboration_metrics(self, data: Dict) -> Dict:
        """Processa métricas de colaboração"""
        return {
            'active_contributors': len(data.get('contributors', [])),
            'code_review_participation': (
                len(data.get('reviewers', [])) /
                len(data.get('pull_requests', []))
            ),
            'comment_frequency': len(data.get('comments', [])) / data.get('duration', 1),
            'cross_team_collaboration': {
                'pr_reviews': len(data.get('cross_team_reviews', [])),
                'issue_comments': len(data.get('cross_team_comments', []))
            }
        }

    async def _analyze_trends(
        self,
        metrics_df: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> Dict:
        """Analisa tendências nas métricas"""
        try:
            trends = {}
            
            # Análise de tendência temporal
            for column in metrics_df.select_dtypes(include=[np.number]).columns:
                trend = self._calculate_trend_metrics(metrics_df[column])
                trends[column] = {
                    'direction': trend['direction'],
                    'slope': trend['slope'],
                    'significance': trend['significance']
                }
            
            return {
                'trends': trends,
                'summary': self._summarize_trends(trends)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trends: {str(e)}")
            raise

    async def _analyze_patterns(
        self,
        metrics_df: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> Dict:
        """Analisa padrões nas métricas"""
        try:
            patterns = {}
            
            # Análise de sazonalidade
            patterns['seasonality'] = self._analyze_seasonality(metrics_df)
            
            # Análise de ciclos
            patterns['cycles'] = self._analyze_cycles(metrics_df)
            
            # Análise de clusters
            patterns['clusters'] = self._analyze_clusters(metrics_df)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to analyze patterns: {str(e)}")
            raise

    async def _analyze_anomalies(
        self,
        metrics_df: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> Dict:
        """Analisa anomalias nas métricas"""
        try:
            anomalies = {}
            
            for column in metrics_df.select_dtypes(include=[np.number]).columns:
                # Detecção de outliers
                anomalies[column] = self._detect_outliers(metrics_df[column])
            
            return {
                'anomalies': anomalies,
                'summary': self._summarize_anomalies(anomalies)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze anomalies: {str(e)}")
            raise

    async def _analyze_predictions(
        self,
        metrics_df: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> Dict:
        """Realiza previsões baseadas nas métricas"""
        try:
            predictions = {}
            
            # Previsão para próximo período
            predictions['next_period'] = self._forecast_metrics(
                metrics_df,
                periods=1
            )
            
            # Previsão para próxima semana
            predictions['next_week'] = self._forecast_metrics(
                metrics_df,
                periods=7
            )
            
            # Previsão para próximo mês
            predictions['next_month'] = self._forecast_metrics(
                metrics_df,
                periods=30
            )
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to analyze predictions: {str(e)}")
            raise

    async def _analyze_correlations(
        self,
        metrics_df: pd.DataFrame,
        params: Optional[Dict] = None
    ) -> Dict:
        """Analisa correlações entre métricas"""
        try:
            # Calcula matriz de correlação
            corr_matrix = metrics_df.corr()
            
            # Identifica correlações significativas
            significant_corr = self._find_significant_correlations(corr_matrix)
            
            return {
                'correlation_matrix': corr_matrix.to_dict(),
                'significant_correlations': significant_corr
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze correlations: {str(e)}")
            raise

    def _calculate_trend_metrics(self, series: pd.Series) -> Dict:
        """Calcula métricas de tendência"""
        try:
            # Calcula inclinação
            x = np.arange(len(series))
            slope, intercept = np.polyfit(x, series, 1)
            
            # Determina direção
            direction = 'increasing' if slope > 0 else 'decreasing'
            
            # Calcula significância
            correlation = np.corrcoef(x, series)[0, 1]
            significance = abs(correlation)
            
            return {
                'direction': direction,
                'slope': slope,
                'significance': significance
            }
            
        except Exception:
            return {
                'direction': 'unknown',
                'slope': 0,
                'significance': 0
            }