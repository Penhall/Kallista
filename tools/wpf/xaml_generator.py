# tools/wpf/xaml_generator.py
from typing import Dict, List, Any
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class XamlGenerator:
    def __init__(self):
        self.xmlns = {
            'default': "http://schemas.microsoft.com/winfx/2006/xaml/presentation",
            'x': "http://schemas.microsoft.com/winfx/2006/xaml",
            'local': "clr-namespace:YourNamespace"
        }

    def generate_window(self, config: Dict) -> str:
        """Gera XAML para uma janela WPF"""
        root = ET.Element('Window')
        for ns, uri in self.xmlns.items():
            root.set(f'xmlns:{ns}' if ns != 'default' else 'xmlns', uri)

        # Configurações básicas da janela
        for key, value in config.get('window_properties', {}).items():
            root.set(key, str(value))

        # Recursos
        if 'resources' in config:
            resources = ET.SubElement(root, 'Window.Resources')
            self._add_resources(resources, config['resources'])

        # Layout principal
        if 'layout' in config:
            layout = self._create_layout(config['layout'])
            root.append(layout)

        return self._format_xaml(root)

    def _create_layout(self, layout_config: Dict) -> ET.Element:
        """Cria elemento de layout"""
        layout = ET.Element(layout_config['type'])
        
        # Define rows e columns para Grid
        if layout_config['type'] == 'Grid':
            if 'rows' in layout_config:
                layout.set('Grid.RowDefinitions', 
                          ';'.join([f"{r['height']}*" for r in layout_config['rows']]))
            if 'columns' in layout_config:
                layout.set('Grid.ColumnDefinitions',
                          ';'.join([f"{c['width']}*" for c in layout_config['columns']]))

        # Adiciona controles
        for control in layout_config.get('controls', []):
            control_element = self._create_control(control)
            layout.append(control_element)

        return layout

    def _create_control(self, control_config: Dict) -> ET.Element:
        """Cria elemento de controle"""
        control = ET.Element(control_config['type'])
        
        # Propriedades básicas
        for key, value in control_config.get('properties', {}).items():
            control.set(key, str(value))

        # Posicionamento no Grid
        if 'grid_position' in control_config:
            pos = control_config['grid_position']
            if 'row' in pos:
                control.set('Grid.Row', str(pos['row']))
            if 'column' in pos:
                control.set('Grid.Column', str(pos['column']))
            if 'row_span' in pos:
                control.set('Grid.RowSpan', str(pos['row_span']))
            if 'column_span' in pos:
                control.set('Grid.ColumnSpan', str(pos['column_span']))

        # Bindings
        for prop, binding in control_config.get('bindings', {}).items():
            control.set(prop, f"{{Binding {binding}}}")

        return control

    def _add_resources(self, resources_element: ET.Element, resources: Dict):
        """Adiciona recursos ao XAML"""
        for res_type, res_items in resources.items():
            if res_type == 'styles':
                self._add_styles(resources_element, res_items)
            elif res_type == 'templates':
                self._add_templates(resources_element, res_items)
            elif res_type == 'converters':
                self._add_converters(resources_element, res_items)

    def _format_xaml(self, element: ET.Element) -> str:
        """Formata o XAML para melhor legibilidade"""
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")