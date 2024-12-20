# tools/performance/resource_manager.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import psutil
import json
import threading
import gc

class ResourceManager:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.resources = {}
        self.usage_history = []
        self.resource_limits = self._load_resource_limits()

    def _load_resource_limits(self) -> Dict:
        """Carrega limites de recursos"""
        try:
            limits_file = Path("config/performance/resource_limits.json")
            if limits_file.exists():
                with open(limits_file) as f:
                    return json.load(f)
            return {
                'memory': {
                    'max_heap': 1024 * 1024 * 1024,  # 1GB
                    'max_stack': 8 * 1024 * 1024,    # 8MB
                    'max_objects': 1000000           # 1M objetos
                },
                'threads': {
                    'max_threads': 200,
                    'pool_size': 50,
                    'queue_size': 1000
                },
                'file_handles': {
                    'max_open': 1000,
                    'max_size': 100 * 1024 * 1024  # 100MB
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to load resource limits: {str(e)}")
            return {}

    async def monitor_resources(self) -> Dict:
        """Monitora uso de recursos"""
        try:
            current_usage = {
                'memory': await self._monitor_memory(),
                'threads': await self._monitor_threads(),
                'file_handles': await self._monitor_file_handles(),
                'timestamp': datetime.utcnow().isoformat()
            }

            # Atualiza histórico
            self.usage_history.append(current_usage)
            if len(self.usage_history) > 1000:  # Mantém últimas 1000 medições
                self.usage_history.pop(0)

            return current_usage

        except Exception as e:
            self.logger.error(f"Resource monitoring failed: {str(e)}")
            raise

    async def optimize_resources(self) -> Dict:
        """Otimiza uso de recursos"""
        try:
            results = {
                'optimizations': [],
                'released': {
                    'memory': 0,
                    'handles': 0,
                    'threads': 0
                },
                'errors': []
            }

            # Otimiza memória
            await self._optimize_memory(results)

            # Otimiza threads
            await self._optimize_threads(results)

            # Otimiza handles de arquivo
            await self._optimize_file_handles(results)

            return results

        except Exception as e:
            self.logger.error(f"Resource optimization failed: {str(e)}")
            raise

    async def _monitor_memory(self) -> Dict:
        """Monitora uso de memória"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_usage = {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'shared': memory_info.shared,
                'heap': self._get_heap_size(),
                'non_heap': memory_info.vms - self._get_heap_size(),
                'gc_stats': {
                    'collections': gc.get_count(),
                    'thresholds': gc.get_threshold(),
                    'objects': len(gc.get_objects())
                }
            }
            
            # Calcula percentuais
            memory_usage['usage_percent'] = (
                memory_usage['rss'] / psutil.virtual_memory().total * 100
            )
            
            return memory_usage
            
        except Exception as e:
            self.logger.error(f"Memory monitoring failed: {str(e)}")
            return {}

    async def _monitor_threads(self) -> Dict:
        """Monitora threads"""
        try:
            process = psutil.Process()
            
            thread_usage = {
                'total': process.num_threads(),
                'active': threading.active_count(),
                'daemon': len([t for t in threading.enumerate() if t.daemon]),
                'peak': max(t.num_threads() for t in [process]),
                'states': self._get_thread_states()
            }
            
            return thread_usage
            
        except Exception as e:
            self.logger.error(f"Thread monitoring failed: {str(e)}")
            return {}

    async def _monitor_file_handles(self) -> Dict:
        """Monitora handles de arquivo"""
        try:
            process = psutil.Process()
            
            handle_usage = {
                'open_files': len(process.open_files()),
                'connections': len(process.connections()),
                'handles': process.num_handles() if hasattr(process, 'num_handles') else None,
                'limits': {
                    'soft': process.rlimit(psutil.RLIMIT_NOFILE)[0],
                    'hard': process.rlimit(psutil.RLIMIT_NOFILE)[1]
                }
            }
            
            return handle_usage
            
        except Exception as e:
            self.logger.error(f"File handle monitoring failed: {str(e)}")
            return {}

    async def _optimize_memory(self, results: Dict) -> None:
        """Otimiza uso de memória"""
        try:
            # Força coleta de lixo
            gc.collect()
            
            # Limpa caches internos
            self._clear_internal_caches()
            
            # Compacta heap se possível
            if hasattr(gc, 'compact'):
                gc.compact()
            
            results['optimizations'].append({
                'type': 'memory',
                'action': 'gc_collect',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Memory optimization failed: {str(e)}")
            results['errors'].append(str(e))

    async def _optimize_threads(self, results: Dict) -> None:
        """Otimiza uso de threads"""
        try:
            # Identifica threads ociosas
            idle_threads = self._identify_idle_threads()
            
            # Finaliza threads ociosas
            for thread in idle_threads:
                if hasattr(thread, 'terminate'):
                    thread.terminate()
            
            results['optimizations'].append({
                'type': 'threads',
                'action': 'terminate_idle',
                'count': len(idle_threads),
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Thread optimization failed: {str(e)}")
            results['errors'].append(str(e))

    async def _optimize_file_handles(self, results: Dict) -> None:
        """Otimiza handles de arquivo"""
        try:
            # Fecha handles não utilizados
            closed_count = self._close_unused_handles()
            
            results['optimizations'].append({
                'type': 'file_handles',
                'action': 'close_unused',
                'count': closed_count,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"File handle optimization failed: {str(e)}")
            results['errors'].append(str(e))

    def _get_heap_size(self) -> int:
        """Obtém tamanho do heap"""
        try:
            return sum(obj.__sizeof__() for obj in gc.get_objects())
        except Exception:
            return 0

    def _get_thread_states(self) -> Dict:
        """Obtém estados das threads"""
        states = {}
        for thread in threading.enumerate():
            state = 'running' if thread.is_alive() else 'stopped'
            states[state] = states.get(state, 0) + 1
        return states

    def _clear_internal_caches(self) -> None:
        """Limpa caches internos"""
        # Limpa cache de imports
        if hasattr(sys, 'modules'):
            unused_modules = []
            for module_name in sys.modules:
                if not sys.modules[module_name]:
                    unused_modules.append(module_name)
            for module_name in unused_modules:
                del sys.modules[module_name]

    def _identify_idle_threads(self) -> List[threading.Thread]:
        """Identifica threads ociosas"""
        idle_threads = []
        for thread in threading.enumerate():
            if hasattr(thread, '_started') and not thread.is_alive():
                idle_threads.append(thread)
        return idle_threads

    def _close_unused_handles(self) -> int:
        """Fecha handles não utilizados"""
        try:
            process = psutil.Process()
            closed_count = 0
            
            # Fecha arquivos não utilizados
            for file in process.open_files():
                try:
                    os.close(file.fd)
                    closed_count += 1
                except (OSError, IOError):
                    pass
                    
            return closed_count
            
        except Exception:
            return 0

    async def get_resource_report(self) -> Dict:
        """Gera relatório de recursos"""
        try:
            current_usage = await self.monitor_resources()
            history = self.usage_history[-10:]  # Últimas 10 medições
            
            report = {
                'current_usage': current_usage,
                'history': history,
                'trends': self._analyze_trends(history),
                'recommendations': self._generate_recommendations(current_usage),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate resource report: {str(e)}")
            raise

    def _analyze_trends(self, history: List[Dict]) -> Dict:
        """Analisa tendências de uso de recursos"""
        if not history:
            return {}

        trends = {
            'memory': self._calculate_trend(
                [h['memory']['usage_percent'] for h in history]
            ),
            'threads': self._calculate_trend(
                [h['threads']['total'] for h in history]
            ),
            'file_handles': self._calculate_trend(
                [h['file_handles']['open_files'] for h in history]
            )
        }

        return trends

    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendência de uma série de valores"""
        if len(values) < 2:
            return 'stable'

        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

        diff = second_half - first_half
        if abs(diff) < 0.05 * first_half:
            return 'stable'
        return 'increasing' if diff > 0 else 'decreasing'

    def _generate_recommendations(self, usage: Dict) -> List[Dict]:
        """Gera recomendações baseadas no uso atual"""
        recommendations = []

        # Recomendações de memória
        if usage['memory']['usage_percent'] > 80:
            recommendations.append({
                'type': 'memory',
                'priority': 'high',
                'description': 'Memory usage is high',
                'action': 'Consider increasing memory limits or optimizing memory usage'
            })

        # Recomendações de threads
        if usage['threads']['total'] > self.resource_limits['threads']['max_threads']:
            recommendations.append({
                'type': 'threads',
                'priority': 'medium',
                'description': 'Thread count exceeds limit',
                'action': 'Review thread usage and consider using a thread pool'
            })

        # Recomendações de file handles
        if usage['file_handles']['open_files'] > self.resource_limits['file_handles']['max_open']:
            recommendations.append({
                'type': 'file_handles',
                'priority': 'medium',
                'description': 'Too many open file handles',
                'action': 'Review file handle usage and close unused handles'
            })

        return recommendations