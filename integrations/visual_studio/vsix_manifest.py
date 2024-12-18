# integrations/visual_studio/vsix_manifest.py
from typing import Dict
import xml.etree.ElementTree as ET
from pathlib import Path

class VSIXManifestGenerator:
    def __init__(self):
        self.manifest_path = Path("source.extension.vsixmanifest")

    def generate_manifest(self, config: Dict) -> str:
        """Gera o manifesto VSIX para a extensão"""
        namespace = "http://schemas.microsoft.com/developer/vsx-schema/2011"
        ET.register_namespace("", namespace)
        
        root = ET.Element("{%s}PackageManifest" % namespace)
        root.set("Version", "2.0.0")
        
        # Metadata
        metadata = ET.SubElement(root, "Metadata")
        
        identity = ET.SubElement(metadata, "Identity")
        identity.set("Id", config['id'])
        identity.set("Version", config['version'])
        identity.set("Language", "en-US")
        identity.set("Publisher", config['publisher'])
        
        display_name = ET.SubElement(metadata, "DisplayName")
        display_name.text = config['display_name']
        
        description = ET.SubElement(metadata, "Description")
        description.text = config['description']
        
        # Installation
        installation = ET.SubElement(root, "Installation")
        installTarget = ET.SubElement(installation, "InstallationTarget")
        installTarget.set("Id", "Microsoft.VisualStudio.Community")
        installTarget.set("Version", "[17.0,18.0)")
        
        # Dependencies
        dependencies = ET.SubElement(root, "Dependencies")
        dependency = ET.SubElement(dependencies, "Dependency")
        dependency.set("Id", "Microsoft.Framework.NDP")
        dependency.set("DisplayName", "Microsoft .NET Framework")
        dependency.set("Version", "[4.8,)")
        
        # Assets
        assets = ET.SubElement(root, "Assets")
        
        # VSPackage asset
        asset = ET.SubElement(assets, "Asset")
        asset.set("Type", "Microsoft.VisualStudio.VsPackage")
        asset.set("Path", "KallistaPackage.pkgdef")
        
        # MEF Component
        asset = ET.SubElement(assets, "Asset")
        asset.set("Type", "Microsoft.VisualStudio.MefComponent")
        asset.set("Path", "Kallista.dll")
        
        return ET.tostring(root, encoding="unicode", method="xml")

    def save_manifest(self, content: str):
        """Salva o manifesto em arquivo"""
        self.manifest_path.write_text(content)