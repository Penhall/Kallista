# tools/wpf/style_generator.py
from typing import Dict, List, Any
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class StyleGenerator:
    def __init__(self):
        self.default_styles = self._load_default_styles()

    def generate_styles(self, style_config: Dict) -> str:
        """Gera estilos WPF baseados na configuração"""
        root = ET.Element('ResourceDictionary')
        
        # Adiciona estilos
        for control_type, style_def in style_config.items():
            style = self._create_style(control_type, style_def)
            root.append(style)

        return self._format_xaml(root)

    def _create_style(self, control_type: str, style_def: Dict) -> ET.Element:
        """Cria um elemento Style"""
        style = ET.Element('Style')
        style.set('TargetType', control_type)
        
        if 'base_on' in style_def:
            style.set('BasedOn', style_def['base_on'])

        # Setters
        for prop, value in style_def.get('setters', {}).items():
            setter = ET.SubElement(style, 'Setter')
            setter.set('Property', prop)
            setter.set('Value', str(value))

        # Triggers
        if 'triggers' in style_def:
            for trigger_def in style_def['triggers']:
                trigger = self._create_trigger(trigger_def)
                style.append(trigger)

        return style

    def _create_trigger(self, trigger_def: Dict) -> ET.Element:
        """Cria um elemento Trigger"""
        if trigger_def['type'] == 'property':
            trigger = ET.Element('Trigger')
            trigger.set('Property', trigger_def['property'])
            trigger.set('Value', str(trigger_def['value']))
        elif trigger_def['type'] == 'data':
            trigger = ET.Element('DataTrigger')
            trigger.set('Binding', trigger_def['binding'])
            trigger.set('Value', str(trigger_def['value']))
        else:
            raise ValueError(f"Unsupported trigger type: {trigger_def['type']}")

        # Setters do trigger
        for prop, value in trigger_def.get('setters', {}).items():
            setter = ET.SubElement(trigger, 'Setter')
            setter.set('Property', prop)
            setter.set('Value', str(value))

        return trigger

    def _load_default_styles(self) -> Dict:
        """Carrega estilos padrão"""
        return {
            'Button': {
                'setters': {
                    'Background': '#007ACC',
                    'Foreground': 'White',
                    'Padding': '10,5',
                    'BorderThickness': '0'
                },
                'triggers': [
                    {
                        'type': 'property',
                        'property': 'IsMouseOver',
                        'value': 'True',
                        'setters': {
                            'Background': '#005A9E'
                        }
                    }
                ]
            },
            'TextBox': {
                'setters': {
                    'Padding': '5',
                    'BorderThickness': '1',
                    'BorderBrush': '#CCCCCC'
                },
                'triggers': [
                    {
                        'type': 'property',
                        'property': 'IsFocused',
                        'value': 'True',
                        'setters': {
                            'BorderBrush': '#007ACC'
                        }
                    }
                ]
            }
        }

    def _format_xaml(self, element: ET.Element) -> str:
        """Formata o XAML para melhor legibilidade"""
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")