# tools/wpf/template_generator.py
from typing import Dict, List, Any
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from pathlib import Path

class TemplateGenerator:
    def __init__(self):
        self.template_path = Path("templates/wpf")
        self.template_path.mkdir(parents=True, exist_ok=True)

    def generate_control_template(self, template_config: Dict) -> str:
        """Gera template de controle"""
        template = ET.Element('ControlTemplate')
        template.set('TargetType', template_config['target_type'])

        # Root element do template
        root = self._create_template_root(template_config['root'])
        template.append(root)

        # Triggers do template
        if 'triggers' in template_config:
            triggers = ET.SubElement(template, 'ControlTemplate.Triggers')
            for trigger_def in template_config['triggers']:
                trigger = self._create_trigger(trigger_def)
                triggers.append(trigger)

        return self._format_xaml(template)

    def _create_template_root(self, root_config: Dict) -> ET.Element:
        """Cria elemento raiz do template"""
        root = ET.Element(root_config['type'])
        
        # Visual states
        if 'visual_states' in root_config:
            vsm = ET.SubElement(root, 'VisualStateManager.VisualStateGroups')
            for group in root_config['visual_states']:
                self._add_visual_state_group(vsm, group)

        # Children elements
        for child in root_config.get('children', []):
            child_element = self._create_template_part(child)
            root.append(child_element)

        return root

    def _create_template_part(self, part_config: Dict) -> ET.Element:
        """Cria parte do template"""
        part = ET.Element(part_config['type'])
        
        # Template part name
        if 'name' in part_config:
            part.set('Name', part_config['name'])

        # Properties
        for key, value in part_config.get('properties', {}).items():
            part.set(key, str(value))

        # Child elements
        for child in part_config.get('children', []):
            child_element = self._create_template_part(child)
            part.append(child_element)

        return part

    def _add_visual_state_group(self, vsm: ET.Element, group_config: Dict):
        """Adiciona grupo de visual states"""
        group = ET.SubElement(vsm, 'VisualStateGroup')
        group.set('x:Name', group_config['name'])

        for state in group_config['states']:
            vs = ET.SubElement(group, 'VisualState')
            vs.set('x:Name', state['name'])

            if 'storyboard' in state:
                sb = ET.SubElement(vs, 'Storyboard')
                for anim in state['storyboard']:
                    self._add_animation(sb, anim)

    def _add_animation(self, storyboard: ET.Element, anim_config: Dict):
        """Adiciona animação ao storyboard"""
        anim = ET.SubElement(storyboard, anim_config['type'])
        
        for key, value in anim_config.get('properties', {}).items():
            anim.set(key, str(value))

        if 'target_name' in anim_config:
            anim.set('Storyboard.TargetName', anim_config['target_name'])
        if 'target_property' in anim_config:
            anim.set('Storyboard.TargetProperty', anim_config['target_property'])

    def save_template(self, template_name: str, xaml: str):
        """Salva template em arquivo"""
        template_file = self.template_path / f"{template_name}.xaml"
        template_file.write_text(xaml)

    def load_template(self, template_name: str) -> str:
        """Carrega template de arquivo"""
        template_file = self.template_path / f"{template_name}.xaml"
        if template_file.exists():
            return template_file.read_text()
        return ""

    def _format_xaml(self, element: ET.Element) -> str:
        """Formata o XAML para melhor legibilidade"""
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")