# agents/specialized/wpf_agent.py
from crewai import Agent
from typing import Dict, List, Any
import json
from pathlib import Path

class WpfAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='WPF Specialist',
            goal='Design and implement WPF interfaces and controls',
            backstory="""You are an expert WPF developer with deep knowledge of 
            XAML, data binding, and WPF controls. You specialize in creating 
            responsive and user-friendly interfaces following MVVM pattern.""",
            llm=llm
        )
        self.templates_path = Path("templates/wpf")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    async def design_interface(self, requirements: Dict) -> Dict[str, Any]:
        """Design a WPF interface based on requirements"""
        try:
            layout = self._create_layout(requirements)
            controls = self._define_controls(requirements)
            styles = self._define_styles(requirements)
            resources = self._define_resources(requirements)
            
            return {
                'layout': layout,
                'controls': controls,
                'styles': styles,
                'resources': resources,
                'validation': self._validate_design(layout, controls)
            }
        except Exception as e:
            raise Exception(f"Error designing interface: {str(e)}")

    def _create_layout(self, requirements: Dict) -> Dict:
        """Create the layout structure"""
        return {
            'type': requirements.get('layout_type', 'Grid'),
            'rows': requirements.get('rows', []),
            'columns': requirements.get('columns', []),
            'margins': requirements.get('margins', '10'),
            'spacing': requirements.get('spacing', '5')
        }

    def _define_controls(self, requirements: Dict) -> List[Dict]:
        """Define the WPF controls to be used"""
        controls = []
        for control in requirements.get('controls', []):
            controls.append({
                'type': control.get('type'),
                'name': control.get('name'),
                'grid_position': {
                    'row': control.get('row', 0),
                    'column': control.get('column', 0),
                    'row_span': control.get('row_span', 1),
                    'column_span': control.get('column_span', 1)
                },
                'properties': control.get('properties', {}),
                'bindings': control.get('bindings', {}),
                'events': control.get('events', {})
            })
        return controls

    def _define_styles(self, requirements: Dict) -> Dict:
        """Define styles for the interface"""
        return {
            'colors': requirements.get('colors', self._get_default_colors()),
            'fonts': requirements.get('fonts', self._get_default_fonts()),
            'control_styles': requirements.get('control_styles', {}),
            'animations': requirements.get('animations', [])
        }

    def _define_resources(self, requirements: Dict) -> Dict:
        """Define resources for the interface"""
        return {
            'brushes': self._create_brushes(requirements),
            'templates': self._create_templates(requirements),
            'converters': self._create_converters(requirements)
        }

    def _validate_design(self, layout: Dict, controls: List[Dict]) -> Dict:
        """Validate the interface design"""
        issues = []
        recommendations = []

        # Validate layout
        if not layout.get('rows') and not layout.get('columns'):
            issues.append("Layout doesn't have any rows or columns defined")
            recommendations.append("Define at least one row or column")

        # Validate controls
        control_names = set()
        for control in controls:
            # Check for duplicate names
            if control['name'] in control_names:
                issues.append(f"Duplicate control name: {control['name']}")
            control_names.add(control['name'])

            # Check grid positions
            pos = control['grid_position']
            if pos['row'] < 0 or pos['column'] < 0:
                issues.append(f"Invalid grid position for control: {control['name']}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations
        }

    def _get_default_colors(self) -> Dict:
        """Get default color scheme"""
        return {
            'primary': '#007ACC',
            'secondary': '#5C2D91',
            'background': '#FFFFFF',
            'text': '#000000',
            'accent': '#FFB900'
        }

    def _get_default_fonts(self) -> Dict:
        """Get default font settings"""
        return {
            'main': 'Segoe UI',
            'headers': 'Segoe UI Light',
            'code': 'Consolas',
            'sizes': {
                'small': 12,
                'normal': 14,
                'large': 16,
                'header': 20
            }
        }

    def _create_brushes(self, requirements: Dict) -> Dict:
        """Create brush resources"""
        colors = requirements.get('colors', self._get_default_colors())
        return {
            f"{name}Brush": f"{{StaticResource {name}Color}}"
            for name in colors.keys()
        }

    def _create_templates(self, requirements: Dict) -> Dict:
        """Create control templates"""
        return {
            control_type: self._load_template(f"{control_type.lower()}_template.xaml")
            for control_type in requirements.get('template_types', [])
        }

    def _create_converters(self, requirements: Dict) -> List[Dict]:
        """Create value converters"""
        converters = []
        for conv in requirements.get('converters', []):
            converters.append({
                'name': f"{conv['type']}Converter",
                'type': conv['type'],
                'parameters': conv.get('parameters', {})
            })
        return converters

    def _load_template(self, template_name: str) -> str:
        """Load a XAML template from file"""
        template_file = self.templates_path / template_name
        if template_file.exists():
            return template_file.read_text()
        return ""

    async def generate_xaml(self, design: Dict) -> str:
        """Generate XAML code from design"""
        # Implementação da geração de XAML
        xaml = []
        xaml.append('<Window x:Class="Application.MainWindow"')
        xaml.append('        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"')
        xaml.append('        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"')
        xaml.append('        Title="MainWindow" Height="450" Width="800">')
        
        # Add resources
        xaml.append('    <Window.Resources>')
        for resource in design['resources'].values():
            xaml.append(f'        {resource}')
        xaml.append('    </Window.Resources>')
        
        # Add layout
        layout = design['layout']
        xaml.append(f'    <{layout["type"]}>')
        
        # Add controls
        for control in design['controls']:
            xaml.append(self._generate_control_xaml(control))
            
        xaml.append(f'    </{layout["type"]}>')
        xaml.append('</Window>')
        
        return '\n'.join(xaml)

    def _generate_control_xaml(self, control: Dict) -> str:
        """Generate XAML for a single control"""
        xaml = [f'        <{control["type"]}']
        
        # Add name if present
        if control.get('name'):
            xaml.append(f' x:Name="{control["name"]}"')
            
        # Add grid position
        pos = control['grid_position']
        xaml.append(f' Grid.Row="{pos["row"]}"')
        xaml.append(f' Grid.Column="{pos["column"]}"')
        if pos['row_span'] > 1:
            xaml.append(f' Grid.RowSpan="{pos["row_span"]}"')
        if pos['column_span'] > 1:
            xaml.append(f' Grid.ColumnSpan="{pos["column_span"]}"')
            
        # Add properties
        for prop, value in control.get('properties', {}).items():
            xaml.append(f' {prop}="{value}"')
            
        # Add bindings
        for prop, binding in control.get('bindings', {}).items():
            xaml.append(f' {prop}="{{Binding {binding}}}"')
            
        xaml.append('/>')
        return ''.join(xaml)