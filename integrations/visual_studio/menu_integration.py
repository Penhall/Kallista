# integrations/visual_studio/menu_integration.py
from typing import Dict, List
from pathlib import Path
import xml.etree.ElementTree as ET

class VSMenuIntegration:
    def __init__(self):
        self.vsct_path = Path("KallistaPackage.vsct")

    def generate_vsct(self, config: Dict) -> str:
        """Gera arquivo VSCT para definição de menus e comandos"""
        vsct = ET.Element("CommandTable")
        vsct.set("xmlns", "http://schemas.microsoft.com/VisualStudio/2005-10-18/CommandTable")
        
        # Includes
        includes = ET.SubElement(vsct, "Includes")
        include = ET.SubElement(includes, "Include")
        include.set("href", "stdidcmd.h")
        include = ET.SubElement(includes, "Include")
        include.set("href", "vsshlids.h")
        
        # Commands
        commands = ET.SubElement(vsct, "Commands")
        commands.set("package", config['package_guid'])
        
        # Menus
        menus = ET.SubElement(commands, "Menus")
        for menu in config.get('menus', []):
            self._add_menu(menus, menu)
        
        # Groups
        groups = ET.SubElement(commands, "Groups")
        for group in config.get('groups', []):
            self._add_group(groups, group)
        
        # Buttons
        buttons = ET.SubElement(commands, "Buttons")
        for button in config.get('buttons', []):
            self._add_button(buttons, button)
        
        # Key Bindings
        keybindings = ET.SubElement(vsct, "KeyBindings")
        for binding in config.get('keybindings', []):
            self._add_keybinding(keybindings, binding)
        
        return ET.tostring(vsct, encoding="unicode", method="xml")

    def _add_menu(self, parent: ET.Element, menu: Dict):
        """Adiciona definição de menu"""
        menu_elem = ET.SubElement(parent, "Menu")
        menu_elem.set("guid", menu['guid'])
        menu_elem.set("id", str(menu['id']))
        menu_elem.set("priority", str(menu['priority']))
        
        parent_elem = ET.SubElement(menu_elem, "Parent")
        parent_elem.set("guid", menu['parent_guid'])
        parent_elem.set("id", str(menu['parent_id']))
        
        strings = ET.SubElement(menu_elem, "Strings")
        button_text = ET.SubElement(strings, "ButtonText")
        button_text.text = menu['text']

    def _add_group(self, parent: ET.Element, group: Dict):
        """Adiciona definição de grupo"""
        group_elem = ET.SubElement(parent, "Group")
        group_elem.set("guid", group['guid'])
        group_elem.set("id", str(group['id']))
        group_elem.set("priority", str(group['priority']))
        
        parent_elem = ET.SubElement(group_elem, "Parent")
        parent_elem.set("guid", group['parent_guid'])
        parent_elem.set("id", str(group['parent_id']))