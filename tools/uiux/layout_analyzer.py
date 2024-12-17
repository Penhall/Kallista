# tools/uiux/layout_analyzer.py
from typing import Dict, List, Any
import math
from dataclasses import dataclass

@dataclass
class LayoutMetrics:
    density_score: float
    hierarchy_depth: int
    alignment_score: float
    spacing_consistency: float
    readability_score: float

class LayoutAnalyzer:
    def __init__(self):
        self.optimal_density = 0.7
        self.max_hierarchy_depth = 4
        self.min_spacing = 8
        self.optimal_line_length = 66  # caracteres

    def analyze_layout(self, layout_config: Dict) -> Dict[str, Any]:
        """Analisa o layout e fornece métricas e recomendações"""
        metrics = self._calculate_metrics(layout_config)
        
        return {
            'metrics': metrics.__dict__,
            'issues': self._identify_issues(metrics, layout_config),
            'recommendations': self._generate_recommendations(metrics, layout_config),
            'compliance_score': self._calculate_compliance_score(metrics)
        }

    def _calculate_metrics(self, layout: Dict) -> LayoutMetrics:
        """Calcula métricas do layout"""
        return LayoutMetrics(
            density_score=self._calculate_density(layout),
            hierarchy_depth=self._calculate_hierarchy_depth(layout),
            alignment_score=self._calculate_alignment_score(layout),
            spacing_consistency=self._analyze_spacing_consistency(layout),
            readability_score=self._calculate_readability_score(layout)
        )

    def _calculate_density(self, layout: Dict) -> float:
        """Calcula densidade de elementos no layout"""
        total_space = self._get_total_space(layout)
        used_space = self._get_used_space(layout)
        return used_space / total_space if total_space > 0 else 0

    def _calculate_hierarchy_depth(self, layout: Dict, current_depth: int = 0) -> int:
        """Calcula profundidade da hierarquia visual"""
        if not layout.get('children'):
            return current_depth
        
        child_depths = [
            self._calculate_hierarchy_depth(child, current_depth + 1)
            for child in layout['children']
        ]
        return max(child_depths) if child_depths else current_depth

    def _calculate_alignment_score(self, layout: Dict) -> float:
        """Calcula score de alinhamento dos elementos"""
        alignments = self._collect_alignments(layout)
        if not alignments:
            return 0.0
        
        # Calcula consistência de alinhamento
        primary_alignment = max(set(alignments), key=alignments.count)
        alignment_score = alignments.count(primary_alignment) / len(alignments)
        
        return alignment_score

    def _analyze_spacing_consistency(self, layout: Dict) -> float:
        """Analisa consistência de espaçamento"""
        spacings = self._collect_spacings(layout)
        if not spacings:
            return 1.0
        
        # Calcula desvio padrão dos espaçamentos
        mean = sum(spacings) / len(spacings)
        variance = sum((x - mean) ** 2 for x in spacings) / len(spacings)
        std_dev = math.sqrt(variance)
        
        # Normaliza para um score entre 0 e 1
        max_acceptable_std_dev = self.min_spacing
        consistency_score = 1 - min(std_dev / max_acceptable_std_dev, 1)
        
        return consistency_score

    def _calculate_readability_score(self, layout: Dict) -> float:
        """Calcula score de legibilidade"""
        text_elements = self._collect_text_elements(layout)
        if not text_elements:
            return 1.0
        
        scores = []
        for text in text_elements:
            length_score = self._calculate_line_length_score(text)
            contrast_score = self._calculate_contrast_score(text)
            size_score = self._calculate_text_size_score(text)
            scores.extend([length_score, contrast_score, size_score])
        
        return sum(scores) / len(scores) if scores else 0.0

    def _identify_issues(self, metrics: LayoutMetrics, layout: Dict) -> List[Dict]:
        """Identifica problemas no layout"""
        issues = []
        
        if metrics.density_score > self.optimal_density:
            issues.append({
                'type': 'density',
                'severity': 'high',
                'message': 'Layout muito denso, pode prejudicar a usabilidade'
            })
            
        if metrics.hierarchy_depth > self.max_hierarchy_depth:
            issues.append({
                'type': 'hierarchy',
                'severity': 'medium',
                'message': 'Hierarquia muito profunda, pode confundir usuários'
            })
            
        if metrics.spacing_consistency < 0.7:
            issues.append({
                'type': 'spacing',
                'severity': 'medium',
                'message': 'Espaçamento inconsistente entre elementos'
            })
            
        return issues

    def _generate_recommendations(self, metrics: LayoutMetrics, layout: Dict) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        if metrics.density_score > self.optimal_density:
            recommendations.append(
                "Considere aumentar o espaçamento entre elementos ou remover elementos não essenciais"
            )
            
        if metrics.hierarchy_depth > self.max_hierarchy_depth:
            recommendations.append(
                "Simplifique a hierarquia visual agrupando elementos de maneira mais eficiente"
            )
            
        if metrics.spacing_consistency < 0.7:
            recommendations.append(
                "Padronize o espaçamento entre elementos para melhorar a consistência visual"
            )
            
        if metrics.readability_score < 0.8:
            recommendations.append(
                "Melhore a legibilidade ajustando tamanhos de fonte, contraste e comprimento de linha"
            )
            
        return recommendations

    def _calculate_compliance_score(self, metrics: LayoutMetrics) -> float:
        """Calcula score geral de conformidade com boas práticas"""
        weights = {
            'density': 0.25,
            'hierarchy': 0.2,
            'alignment': 0.2,
            'spacing': 0.15,
            'readability': 0.2
        }
        
        scores = {
            'density': 1 - abs(metrics.density_score - self.optimal_density),
            'hierarchy': 1 - (metrics.hierarchy_depth / self.max_hierarchy_depth),
            'alignment': metrics.alignment_score,
            'spacing': metrics.spacing_consistency,
            'readability': metrics.readability_score
        }
        
        weighted_score = sum(
            score * weights[metric]
            for metric, score in scores.items()
        )
        
        return weighted_score