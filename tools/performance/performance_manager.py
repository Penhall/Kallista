# tools/performance/performance_manager.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json
import psutil
import time

class PerformanceManager:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
        self.thresholds = self._load_thresholds()
        self.resource_monitor = None
        self.cache_manager = None

    def _load_thresholds(self) -> Dict:
        """Carrega thresholds de performance"""
        default_thresholds = {
            'cpu_usage': 80.0,  # Percentual máximo de CPU
            'memory_usage': 85.0,  # Percentual máximo de memória
            'response_time': 2.0,  # Tempo máximo de resposta em segundos
            'disk_usage': 90.0,  # Percentual máximo de uso de disco
            'cache_size': 512,  # Tamanho máximo do cache em MB
            'thread_count': 200  # Número máximo de threads
        }
        
        # Carrega configurações customizadas se existirem
        try:
            config_path = Path("config/performance/thresholds.json")
            if config_path.exists():
                with open(config_path) as f:
                    custom_thresholds = json.load(f)
                    return {**default_thresholds, **custom_thresholds}
        except Exception as e:
            self.logger.warning(f"Failed to load custom thresholds: {str(e)}")
            
        return default_thresholds

    async def monitor_performance(self) -> Dict:
        """Monitora performance do sistema"""
        try:
            results = {
                'system_metrics': await self._collect_system_metrics(),
                'application_metrics': await self._collect_application_metrics(),
                'resource_usage': await self._collect_resource_usage(),
                'bottlenecks': [],
                'recommendations': [],
                'timestamp': datetime.utcnow().isoformat()
            }

            # Identifica gargalos
            bottlenecks = await self._identify_bottlenecks(results)
            results['bottlenecks'] = bottlenecks

            # Gera recomendações
            recommendations = await self._generate_recommendations(bottlenecks)
            results['recommendations'] = recommendations

            # Atualiza métricas internas
            self.metrics = results

            return results

        except Exception as e:
            self.logger.error(f"Performance monitoring failed: {str(e)}")
            raise

    async def optimize_performance(self, target_area: str = None) -> Dict:
        """Executa otimizações de performance"""
        try:
            results = {
                'optimizations': [],
                'errors': [],
                'timestamp': datetime.utcnow().isoformat()
            }

            # Monitora performance atual
            current_metrics = await self.monitor_performance()

            # Executa otimizações baseado na área alvo
            if target_area == 'memory':
                await self._optimize_memory(results)
            elif target_area == 'cpu':
                await self._optimize_cpu(results)
            elif target_area == 'disk':
                await self._optimize_disk(results)
            elif target_area == 'cache':
                await self._optimize_cache(results)
            else:
                # Executa todas as otimizações
                await self._optimize_all(results)

            # Monitora performance após otimizações
            final_metrics = await self.monitor_performance()

            # Calcula impacto
            impact = self._calculate_optimization_impact(
                current_metrics,
                final_metrics
            )
            results['impact'] = impact

            return results

        except Exception as e:
            self.logger.error(f"Performance optimization failed: {str(e)}")
            raise

    async def _collect_system_metrics(self) -> Dict:
        """Coleta métricas do sistema"""
        try:
            metrics = {
                'cpu': {
                    'usage_percent': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'used_percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'free': psutil.disk_usage('/').free,
                    'used_percent': psutil.disk_usage('/').percent
                },
                'network': {
                    'connections': len(psutil.net_connections()),
                    'stats': psutil.net_io_counters()._asdict()
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {str(e)}")
            return {}

    async def _collect_application_metrics(self) -> Dict:
        """Coleta métricas da aplicação"""
        try:
            current_process = psutil.Process()
            
            metrics = {
                'process': {
                    'cpu_percent': current_process.cpu_percent(),
                    'memory_info': current_process.memory_info()._asdict(),
                    'num_threads': current_process.num_threads(),
                    'open_files': len(current_process.open_files()),
                    'connections': len(current_process.connections())
                },
                'threads': {
                    'active': threading.active_count(),
                    'peak': threading.active_count()  # Implementar tracking de pico
                },
                'gc': {
                    'counts': gc.get_count(),
                    'thresholds': gc.get_threshold()
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect application metrics: {str(e)}")
            return {}

    async def _collect_resource_usage(self) -> Dict:
        """Coleta uso de recursos específicos"""
        try:
            metrics = {
                'cache': await self._get_cache_metrics(),
                'database': await self._get_database_metrics(),
                'files': await self._get_file_metrics(),
                'network': await self._get_network_metrics()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect resource usage: {str(e)}")
            return {}

    async def _identify_bottlenecks(self, metrics: Dict) -> List[Dict]:
        """Identifica gargalos de performance"""
        bottlenecks = []
        
        # Verifica CPU
        if metrics['system_metrics']['cpu']['usage_percent'] > self.thresholds['cpu_usage']:
            bottlenecks.append({
                'type': 'cpu',
                'severity': 'high',
                'current_value': metrics['system_metrics']['cpu']['usage_percent'],
                'threshold': self.thresholds['cpu_usage'],
                'description': 'CPU usage above threshold'
            })

        # Verifica memória
        if metrics['system_metrics']['memory']['used_percent'] > self.thresholds['memory_usage']:
            bottlenecks.append({
                'type': 'memory',
                'severity': 'high',
                'current_value': metrics['system_metrics']['memory']['used_percent'],
                'threshold': self.thresholds['memory_usage'],
                'description': 'Memory usage above threshold'
            })

        # Verifica disco
        if metrics['system_metrics']['disk']['used_percent'] > self.thresholds['disk_usage']:
            bottlenecks.append({
                'type': 'disk',
                'severity': 'medium',
                'current_value': metrics['system_metrics']['disk']['used_percent'],
                'threshold': self.thresholds['disk_usage'],
                'description': 'Disk usage above threshold'
            })

        # Verifica threads
        if metrics['application_metrics']['threads']['active'] > self.thresholds['thread_count']:
            bottlenecks.append({
                'type': 'threads',
                'severity': 'medium',
                'current_value': metrics['application_metrics']['threads']['active'],
                'threshold': self.thresholds['thread_count'],
                'description': 'Thread count above threshold'
            })
            
        return bottlenecks

    async def _generate_recommendations(self, bottlenecks: List[Dict]) -> List[Dict]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'cpu':
                recommendations.extend(self._get_cpu_recommendations(bottleneck))
            elif bottleneck['type'] == 'memory':
                recommendations.extend(self._get_memory_recommendations(bottleneck))
            elif bottleneck['type'] == 'disk':
                recommendations.extend(self._get_disk_recommendations(bottleneck))
            elif bottleneck['type'] == 'threads':
                recommendations.extend(self._get_thread_recommendations(bottleneck))
                
        return recommendations

    def _get_cpu_recommendations(self, bottleneck: Dict) -> List[Dict]:
        """Gera recomendações para otimização de CPU"""
        return [
            {
                'type': 'cpu',
                'priority': 'high',
                'description': 'Implement request caching to reduce CPU load',
                'action': 'implement_caching',
                'expected_impact': 'Medium to high reduction in CPU usage'
            },
            {
                'type': 'cpu',
                'priority': 'medium',
                'description': 'Optimize database queries and indexes',
                'action': 'optimize_queries',
                'expected_impact': 'Reduction in CPU usage for database operations'
            },
            {
                'type': 'cpu',
                'priority': 'medium',
                'description': 'Implement asynchronous processing for heavy tasks',
                'action': 'implement_async',
                'expected_impact': 'Better CPU utilization and responsiveness'
            }
        ]

    def _get_memory_recommendations(self, bottleneck: Dict) -> List[Dict]:
        """Gera recomendações para otimização de memória"""
        return [
            {
                'type': 'memory',
                'priority': 'high',
                'description': 'Implement object pooling for frequently used objects',
                'action': 'implement_pooling',
                'expected_impact': 'Reduced memory allocation and garbage collection'
            },
            {
                'type': 'memory',
                'priority': 'high',
                'description': 'Optimize cache size and eviction policies',
                'action': 'optimize_cache',
                'expected_impact': 'Better memory utilization'
            },
            {
                'type': 'memory',
                'priority': 'medium',
                'description': 'Review and optimize large object allocations',
                'action': 'optimize_allocations',
                'expected_impact': 'Reduced memory pressure'
            }
        ]

    def _get_disk_recommendations(self, bottleneck: Dict) -> List[Dict]:
        """Gera recomendações para otimização de disco"""
        return [
            {
                'type': 'disk',
                'priority': 'medium',
                'description': 'Implement file cleanup routine',
                'action': 'implement_cleanup',
                'expected_impact': 'Reduced disk usage'
            },
            {
                'type': 'disk',
                'priority': 'medium',
                'description': 'Optimize file storage structure',
                'action': 'optimize_storage',
                'expected_impact': 'Better disk space utilization'
            },
            {
                'type': 'disk',
                'priority': 'low',
                'description': 'Implement compression for stored files',
                'action': 'implement_compression',
                'expected_impact': 'Reduced disk space usage'
            }
        ]

    def _get_thread_recommendations(self, bottleneck: Dict) -> List[Dict]:
        """Gera recomendações para otimização de threads"""
        return [
            {
                'type': 'threads',
                'priority': 'high',
                'description': 'Implement thread pooling',
                'action': 'implement_thread_pool',
                'expected_impact': 'Controlled thread creation and better resource usage'
            },
            {
                'type': 'threads',
                'priority': 'medium',
                'description': 'Review and optimize async operations',
                'action': 'optimize_async',
                'expected_impact': 'Reduced thread creation'
            },
            {
                'type': 'threads',
                'priority': 'medium',
                'description': 'Implement better task scheduling',
                'action': 'implement_scheduling',
                'expected_impact': 'Better thread utilization'
            }
        ]

    async def _optimize_all(self, results: Dict) -> None:
        """Executa todas as otimizações possíveis"""
        try:
            await self._optimize_memory(results)
            await self._optimize_cpu(results)
            await self._optimize_disk(results)
            await self._optimize_cache(results)
        except Exception as e:
            self.logger.error(f"Failed to execute all optimizations: {str(e)}")
            results['errors'].append(str(e))

    def _calculate_optimization_impact(
        self,
        before: Dict,
        after: Dict
    ) -> Dict:
        """Calcula impacto das otimizações"""
        return {
            'cpu': {
                'before': before['system_metrics']['cpu']['usage_percent'],
                'after': after['system_metrics']['cpu']['usage_percent'],
                'improvement': before['system_metrics']['cpu']['usage_percent'] - 
                             after['system_metrics']['cpu']['usage_percent']
            },
            'memory': {
                'before': before['system_metrics']['memory']['used_percent'],
                'after': after['system_metrics']['memory']['used_percent'],
                'improvement': before['system_metrics']['memory']['used_percent'] - 
                             after['system_metrics']['memory']['used_percent']
            },
            'disk': {
                'before': before['system_metrics']['disk']['used_percent'],
                'after': after['system_metrics']['disk']['used_percent'],
                'improvement': before['system_metrics']['disk']['used_percent'] - 
                             after['system_metrics']['disk']['used_percent']
            }
        }