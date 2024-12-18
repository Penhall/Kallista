# integrations/documentation/docs_manager.py
from typing import Dict, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import markdown
import json
import yaml

class DocumentType(Enum):
    API = "api"
    USER_GUIDE = "user_guide"
    TECHNICAL = "technical"
    RELEASE_NOTES = "release_notes"
    METRICS = "metrics"

class DocsManager:
    def __init__(self, github_client, azure_client):
        self.github = github_client
        self.azure = azure_client
        self.logger = logging.getLogger(__name__)
        self.docs_path = Path("documentation")
        self.docs_path.mkdir(exist_ok=True)

    async def generate_documentation(self, config: Dict) -> Dict:
        """Gera documentação baseada na configuração"""
        try:
            doc_id = f"doc_{datetime.utcnow().timestamp()}"
            doc_type = DocumentType(config['type'])

            # Coleta dados necessários
            data = await self._collect_documentation_data(config)

            # Gera documentação
            content = await self._generate_content(doc_type, data)

            # Formata documentação
            formatted_doc = await self._format_documentation(
                content,
                config.get('format', 'markdown')
            )

            # Salva documentação
            doc_path = await self._save_documentation(
                formatted_doc,
                doc_type,
                config.get('filename')
            )

            # Publica documentação
            if config.get('publish', False):
                await self._publish_documentation(doc_path, config)

            return {
                'id': doc_id,
                'type': doc_type.value,
                'path': str(doc_path),
                'generated_at': datetime.utcnow().isoformat(),
                'config': config
            }

        except Exception as e:
            self.logger.error(f"Failed to generate documentation: {str(e)}")
            raise

    async def generate_report(self, config: Dict) -> Dict:
        """Gera relatório baseado na configuração"""
        try:
            report_id = f"report_{datetime.utcnow().timestamp()}"

            # Coleta dados do relatório
            data = await self._collect_report_data(config)

            # Gera relatório
            report_content = await self._generate_report_content(data, config)

            # Formata relatório
            formatted_report = await self._format_report(
                report_content,
                config.get('format', 'markdown')
            )

            # Adiciona visualizações se necessário
            if config.get('visualizations', False):
                formatted_report = await self._add_visualizations(
                    formatted_report,
                    data,
                    config.get('visualization_config', {})
                )

            # Salva relatório
            report_path = await self._save_report(
                formatted_report,
                config.get('filename')
            )

            # Envia relatório se necessário
            if config.get('send', False):
                await self._send_report(report_path, config)

            return {
                'id': report_id,
                'path': str(report_path),
                'generated_at': datetime.utcnow().isoformat(),
                'config': config
            }

        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")
            raise

    async def _collect_documentation_data(self, config: Dict) -> Dict:
        """Coleta dados para documentação"""
        data = {}
        
        if config['type'] == DocumentType.API.value:
            # Coleta dados da API
            data['endpoints'] = await self._collect_api_endpoints(config)
            data['models'] = await self._collect_api_models(config)
            data['examples'] = await self._collect_api_examples(config)
            
        elif config['type'] == DocumentType.TECHNICAL.value:
            # Coleta dados técnicos
            data['architecture'] = await self._collect_architecture_info(config)
            data['components'] = await self._collect_component_info(config)
            data['dependencies'] = await self._collect_dependency_info(config)
            
        elif config['type'] == DocumentType.RELEASE_NOTES.value:
            # Coleta dados de release
            data['changes'] = await self._collect_changes(config)
            data['fixes'] = await self._collect_fixes(config)
            data['known_issues'] = await self._collect_known_issues(config)

        return data

    async def _generate_content(self, doc_type: DocumentType, data: Dict) -> str:
        """Gera conteúdo da documentação"""
        if doc_type == DocumentType.API:
            return self._generate_api_docs(data)
        elif doc_type == DocumentType.TECHNICAL:
            return self._generate_technical_docs(data)
        elif doc_type == DocumentType.USER_GUIDE:
            return self._generate_user_guide(data)
        elif doc_type == DocumentType.RELEASE_NOTES:
            return self._generate_release_notes(data)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    async def _format_documentation(self, content: str, format: str) -> str:
        """Formata documentação no formato especificado"""
        if format == 'markdown':
            return content
        elif format == 'html':
            return markdown.markdown(content)
        elif format == 'pdf':
            # Implementar conversão para PDF
            raise NotImplementedError("PDF conversion not implemented")
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _collect_report_data(self, config: Dict) -> Dict:
        """Coleta dados para relatório"""
        data = {
            'metrics': {},
            'analysis': {},
            'recommendations': []
        }

        # Coleta métricas
        if config.get('include_metrics', True):
            data['metrics'] = await self._collect_metrics(config)

        # Coleta análises
        if config.get('include_analysis', True):
            data['analysis'] = await self._analyze_data(config)

        # Gera recomendações
        if config.get('include_recommendations', True):
            data['recommendations'] = await self._generate_recommendations(
                data['metrics'],
                data['analysis']
            )

        return data

    async def _generate_report_content(self, data: Dict, config: Dict) -> str:
        """Gera conteúdo do relatório"""
        sections = []

        # Adiciona cabeçalho
        sections.append(self._generate_report_header(config))

        # Adiciona resumo executivo
        if config.get('include_summary', True):
            sections.append(self._generate_executive_summary(data))

        # Adiciona métricas
        if data.get('metrics'):
            sections.append(self._generate_metrics_section(data['metrics']))

        # Adiciona análises
        if data.get('analysis'):
            sections.append(self._generate_analysis_section(data['analysis']))

        # Adiciona recomendações
        if data.get('recommendations'):
            sections.append(self._generate_recommendations_section(data['recommendations']))

        return '\n\n'.join(sections)

    def _generate_report_header(self, config: Dict) -> str:
        """Gera cabeçalho do relatório"""
        return f"""# {config.get('title', 'Report')}

Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

{config.get('description', '')}

---"""

    def _generate_executive_summary(self, data: Dict) -> str:
        """Gera resumo executivo"""
        return f"""## Executive Summary

Key findings from the analysis:

{self._summarize_metrics(data.get('metrics', {}))}

{self._summarize_analysis(data.get('analysis', {}))}

Top recommendations:
{self._format_top_recommendations(data.get('recommendations', []))}
"""

    def _summarize_metrics(self, metrics: Dict) -> str:
        """Sumariza métricas principais"""
        summary = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                summary.append(f"- {key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, dict):
                summary.append(f"- {key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    summary.append(f"  - {k}: {v}")
        return '\n'.join(summary)

    def _summarize_analysis(self, analysis: Dict) -> str:
        """Sumariza análises principais"""
        summary = []
        for key, value in analysis.items():
            if isinstance(value, str):
                summary.append(f"- {key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, dict):
                summary.append(f"- {key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    summary.append(f"  - {k}: {v}")
        return '\n'.join(summary)

    def _format_top_recommendations(self, recommendations: List[str], limit: int = 5) -> str:
        """Formata principais recomendações"""
        return '\n'.join(f"- {rec}" for rec in recommendations[:limit])

    async def _add_visualizations(self, content: str, data: Dict, config: Dict) -> str:
        """Adiciona visualizações ao relatório"""
        # Implementar geração de gráficos e visualizações
        raise NotImplementedError("Visualizations not implemented")

    async def _save_documentation(self, content: str, doc_type: DocumentType, filename: Optional[str] = None) -> Path:
        """Salva documentação em arquivo"""
        if not filename:
            filename = f"{doc_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        
        doc_path = self.docs_path / filename
        doc_path.write_text(content)
        
        return doc_path

    async def _save_report(self, content: str, filename: Optional[str] = None) -> Path:
        """Salva relatório em arquivo"""
        if not filename:
            filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_path = self.docs_path / "reports" / filename
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(content)
        
        return report_path

    async def _publish_documentation(self, doc_path: Path, config: Dict) -> None:
        """Publica documentação"""
        if config.get('github_wiki'):
            await self._publish_to_github_wiki(doc_path, config)
        
        if config.get('azure_wiki'):
            await self._publish_to_azure_wiki(doc_path, config)

    async def _send_report(self, report_path: Path, config: Dict) -> None:
        """Envia relatório"""
        if config.get('email'):
            await self._send_report_email(report_path, config)
        
        if config.get('teams'):
            await self._send_report_teams(report_path, config)