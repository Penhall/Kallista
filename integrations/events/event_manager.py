# integrations/events/event_manager.py
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json

class EventType(Enum):
    PR_CREATED = "pr_created"
    PR_UPDATED = "pr_updated"
    PR_MERGED = "pr_merged"
    BUILD_STARTED = "build_started"
    BUILD_COMPLETED = "build_completed"
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    RELEASE_CREATED = "release_created"
    ISSUE_CREATED = "issue_created"
    SECURITY_ALERT = "security_alert"

class EventManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)
        self.event_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self.event_history: List[Dict] = []

    async def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """Registra um handler para um tipo de evento"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            self.logger.info(f"Handler registered for event type: {event_type.value}")
        else:
            raise ValueError(f"Invalid event type: {event_type.value}")

    async def process_event(self, event: Dict) -> Dict:
        """Processa um evento recebido"""
        try:
            event_type = EventType(event['type'])
            event_id = f"{event_type.value}_{datetime.utcnow().timestamp()}"
            
            processed_event = {
                'id': event_id,
                'type': event_type.value,
                'timestamp': datetime.utcnow().isoformat(),
                'source': event.get('source'),
                'data': event.get('data'),
                'status': 'processing'
            }

            # Adiciona ao histórico
            self.event_history.append(processed_event)

            # Executa handlers
            results = []
            for handler in self.event_handlers[event_type]:
                try:
                    result = await handler(processed_event)
                    results.append({
                        'handler': handler.__name__,
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'handler': handler.__name__,
                        'success': False,
                        'error': str(e)
                    })

            # Atualiza evento processado
            processed_event.update({
                'status': 'completed',
                'results': results,
                'completed_at': datetime.utcnow().isoformat()
            })

            return processed_event

        except Exception as e:
            self.logger.error(f"Failed to process event: {str(e)}")
            raise

    async def send_notification(self, notification: Dict) -> Dict:
        """Envia uma notificação"""
        try:
            # Determina canais de notificação
            channels = notification.get('channels', ['email'])
            notification_id = f"notification_{datetime.utcnow().timestamp()}"

            notification_record = {
                'id': notification_id,
                'type': notification.get('type', 'info'),
                'message': notification['message'],
                'timestamp': datetime.utcnow().isoformat(),
                'channels': channels,
                'status': 'sending'
            }

            # Envia para cada canal
            results = []
            for channel in channels:
                try:
                    if channel == 'email':
                        result = await self._send_email_notification(notification)
                    elif channel == 'teams':
                        result = await self._send_teams_notification(notification)
                    elif channel == 'slack':
                        result = await self._send_slack_notification(notification)
                    elif channel == 'webhook':
                        result = await self._send_webhook_notification(notification)
                    
                    results.append({
                        'channel': channel,
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'channel': channel,
                        'success': False,
                        'error': str(e)
                    })

            # Atualiza registro da notificação
            notification_record.update({
                'status': 'sent',
                'results': results,
                'completed_at': datetime.utcnow().isoformat()
            })

            return notification_record

        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            raise

    async def _send_email_notification(self, notification: Dict) -> Dict:
        """Envia notificação por email"""
        try:
            # Implementação do envio de email
            # Pode usar serviços como SendGrid, AWS SES, etc.
            return {
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            raise

    async def _send_teams_notification(self, notification: Dict) -> Dict:
        """Envia notificação para Microsoft Teams"""
        try:
            # Implementação da integração com Teams
            return {
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to send Teams notification: {str(e)}")
            raise

    async def _send_slack_notification(self, notification: Dict) -> Dict:
        """Envia notificação para Slack"""
        try:
            # Implementação da integração com Slack
            return {
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
            raise

    async def _send_webhook_notification(self, notification: Dict) -> Dict:
        """Envia notificação via webhook"""
        try:
            # Implementação do envio via webhook
            return {
                'status': 'sent',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {str(e)}")
            raise

    def get_event_history(self, 
                         event_type: Optional[EventType] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict]:
        """Recupera histórico de eventos com filtros opcionais"""
        filtered_history = self.event_history

        if event_type:
            filtered_history = [
                event for event in filtered_history
                if event['type'] == event_type.value
            ]

        if start_date:
            filtered_history = [
                event for event in filtered_history
                if datetime.fromisoformat(event['timestamp']) >= start_date
            ]

        if end_date:
            filtered_history = [
                event for event in filtered_history
                if datetime.fromisoformat(event['timestamp']) <= end_date
            ]

        return filtered_history

    async def setup_webhook_listeners(self, config: Dict) -> Dict:
        """Configura listeners para webhooks"""
        try:
            # Configura webhook no GitHub
            if config.get('github_webhook'):
                github_webhook = await self.github.create_webhook({
                    'name': 'web',
                    'active': True,
                    'events': config['github_webhook']['events'],
                    'config': {
                        'url': config['github_webhook']['url'],
                        'content_type': 'json',
                        'secret': config['github_webhook'].get('secret')
                    }
                })

            # Configura webhook no Azure DevOps
            if config.get('azure_webhook'):
                azure_webhook = await self.azure.create_service_hook({
                    'publisherId': 'tfs',
                    'eventType': config['azure_webhook']['event_type'],
                    'resourceVersion': '1.0',
                    'consumerId': 'webHooks',
                    'consumerActionId': 'httpRequest',
                    'consumerInputs': {
                        'url': config['azure_webhook']['url']
                    }
                })

            return {
                'status': 'configured',
                'github_webhook': github_webhook if config.get('github_webhook') else None,
                'azure_webhook': azure_webhook if config.get('azure_webhook') else None,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to setup webhook listeners: {str(e)}")
            raise