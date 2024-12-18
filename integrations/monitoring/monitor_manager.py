# integrations/monitoring/monitor_manager.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import aiohttp
import psutil
import sys
import traceback

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MonitoringMetric(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    API_LATENCY = "api_latency"
    ERROR_RATE = "error_rate"

class MonitorManager:
    def __init__(self, config: Dict):
        self.config = config
        self.log_path = Path(config.get('log_path', 'logs'))
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.metrics_path = Path(config.get('metrics_path', 'metrics'))
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.metrics: Dict[str, List[Dict]] = {
            metric.value: [] for metric in MonitoringMetric
        }

    def _setup_logging(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_path / 'application.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    async def start_monitoring(self):
        """Inicia monitoramento"""
        try:
            # Inicia coleta de métricas
            asyncio.create_task(self._collect_system_metrics())
            asyncio.create_task(self._monitor_api_health())
            
            # Inicia rotinas de manutenção
            asyncio.create_task(self._rotate_logs())
            asyncio.create_task(self._archive_metrics())
            
            self.logger.info("Monitoring started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            raise

    async def log_event(self, event: Dict, level: LogLevel = LogLevel.INFO):
        """Registra um evento"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': level.value,
                'event': event
            }
            
            # Adiciona informações de contexto
            log_entry.update(self._get_context_info())
            
            # Registra no log
            getattr(self.logger, level.value)(json.dumps(log_entry))
            
            # Salva evento em arquivo específico se necessário
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                await self._save_error_event(log_entry)
                
        except Exception as e:
            self.logger.error(f"Failed to log event: {str(e)}")

    async def get_metrics(
        self,
        metric_type: Optional[MonitoringMetric] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, List[Dict]]:
        """Recupera métricas coletadas"""
        try:
            if metric_type:
                metrics = {metric_type.value: self.metrics[metric_type.value]}
            else:
                metrics = self.metrics.copy()
            
            # Aplica filtro de tempo
            if start_time or end_time:
                filtered_metrics = {}
                for metric_name, metric_data in metrics.items():
                    filtered_data = []
                    for data in metric_data:
                        timestamp = datetime.fromisoformat(data['timestamp'])
                        if start_time and timestamp < start_time:
                            continue
                        if end_time and timestamp > end_time:
                            continue
                        filtered_data.append(data)
                    filtered_metrics[metric_name] = filtered_data
                return filtered_metrics
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {str(e)}")
            raise

    async def get_health_status(self) -> Dict:
        """Verifica status de saúde do sistema"""
        try:
            # Coleta métricas atuais
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # Verifica limites
            status = 'healthy'
            issues = []
            
            if cpu > self.config.get('cpu_threshold', 80):
                status = 'warning'
                issues.append(f'High CPU usage: {cpu}%')
                
            if memory > self.config.get('memory_threshold', 80):
                status = 'warning'
                issues.append(f'High memory usage: {memory}%')
                
            if disk > self.config.get('disk_threshold', 80):
                status = 'warning'
                issues.append(f'High disk usage: {disk}%')
            
            # Verifica erros recentes
            recent_errors = await self._get_recent_errors()
            if recent_errors:
                status = 'unhealthy'
                issues.append(f'Recent errors detected: {len(recent_errors)}')
            
            return {
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {
                    'cpu': cpu,
                    'memory': memory,
                    'disk': disk
                },
                'issues': issues,
                'recent_errors': recent_errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get health status: {str(e)}")
            raise

    async def _collect_system_metrics(self):
        """Coleta métricas do sistema"""
        while True:
            try:
                # CPU
                self.metrics['cpu'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'value': psutil.cpu_percent(),
                    'cores': psutil.cpu_count()
                })
                
                # Memory
                memory = psutil.virtual_memory()
                self.metrics['memory'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                })
                
                # Disk
                disk = psutil.disk_usage('/')
                self.metrics['disk'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                })
                
                # Network
                network = psutil.net_io_counters()
                self.metrics['network'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                })
                
                # Limita tamanho do histórico
                for metric in self.metrics.values():
                    if len(metric) > self.config.get('max_metrics_history', 1000):
                        metric.pop(0)
                
                await asyncio.sleep(self.config.get('metrics_interval', 60))
                
            except Exception as e:
                self.logger.error(f"Failed to collect system metrics: {str(e)}")
                await asyncio.sleep(5)

    async def _monitor_api_health(self):
        """Monitora saúde das APIs"""
        while True:
            try:
                start_time = datetime.utcnow()
                
                # Verifica GitHub API
                github_status = await self._check_github_api()
                
                # Verifica Azure DevOps API
                azure_status = await self._check_azure_api()
                
                # Registra latências
                self.metrics['api_latency'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'github': github_status['latency'],
                    'azure': azure_status['latency']
                })
                
                # Registra erros se houver
                if not github_status['healthy'] or not azure_status['healthy']:
                    await self.log_event(
                        {
                            'github': github_status,
                            'azure': azure_status
                        },
                        LogLevel.ERROR
                    )
                
                await asyncio.sleep(self.config.get('api_check_interval', 300))
                
            except Exception as e:
                self.logger.error(f"Failed to monitor API health: {str(e)}")
                await asyncio.sleep(5)

    async def _check_github_api(self) -> Dict:
        """Verifica saúde da API do GitHub"""
        try:
            start_time = datetime.utcnow()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.github.com/status') as response:
                    latency = (datetime.utcnow() - start_time).total_seconds()
                    return {
                        'healthy': response.status == 200,
                        'status_code': response.status,
                        'latency': latency
                    }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'latency': None
            }

    async def _check_azure_api(self) -> Dict:
        """Verifica saúde da API do Azure DevOps"""
        try:
            start_time = datetime.utcnow()
            async with aiohttp.ClientSession() as session:
                async with session.get('https://status.dev.azure.com/_apis/status/health') as response:
                    latency = (datetime.utcnow() - start_time).total_seconds()
                    return {
                        'healthy': response.status == 200,
                        'status_code': response.status,
                        'latency': latency
                    }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'latency': None
            }

    def _get_context_info(self) -> Dict:
        """Obtém informações de contexto"""
        return {
            'process_id': os.getpid(),
            'thread_id': threading.get_ident(),
            'python_version': sys.version,
            'system': platform.system(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total
        }