# integrations/visual_studio/debugging_support.py
from typing import Dict
from pathlib import Path

class VSDebuggingSupport:
    def __init__(self):
        self.visualizers_path = Path("Visualizers")
        self.visualizers_path.mkdir(exist_ok=True)

    def generate_debugger_visualizer(self, config: Dict) -> str:
        """Gera visualizador de debug personalizado"""
        return f'''using System.Diagnostics;
using Microsoft.VisualStudio.DebuggerVisualizers;

[assembly: DebuggerVisualizer(
    typeof({config['visualizer_type']}),
    typeof(VisualizerObjectSource),
    Target = typeof({config['target_type']}),
    Description = "{config['description']}")]

namespace {config['namespace']}
{{
    public class {config['visualizer_name']} : DialogDebuggerVisualizer
    {{
        protected override void Show(IDialogVisualizerService windowService, IVisualizerObjectProvider objectProvider)
        {{
            if (windowService == null)
                throw new ArgumentNullException(nameof(windowService));

            if (objectProvider == null)
                throw new ArgumentNullException(nameof(objectProvider));

            var data = ({config['target_type']})objectProvider.GetObject();
            
            {self._generate_visualizer_logic(config)}
        }}
        
        {self._generate_helper_methods(config)}
    }}
}}'''

    def generate_type_proxy(self, config: Dict) -> str:
        """Gera proxy para tipo personalizado"""
        return f'''using System.Runtime.Serialization;

namespace {config['namespace']}
{{
    [Serializable]
    public class {config['proxy_name']} : ISerializable
    {{
        private readonly {config['target_type']} _instance;

        public {config['proxy_name']}({config['target_type']} instance)
        {{
            _instance = instance;
        }}

        protected {config['proxy_name']}(SerializationInfo info, StreamingContext context)
        {{
            {self._generate_deserialization_logic(config)}
        }}

        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {{
            {self._generate_serialization_logic(config)}
        }}
        
        {self._generate_proxy_properties(config)}
    }}
}}'''

    def _generate_visualizer_logic(self, config: Dict) -> str:
        """Gera lógica do visualizador"""
        logic = []
        
        # Form generation
        logic.append('using (var form = new Form())')
        logic.append('{')
        logic.append('    form.Text = "Data Visualizer";')
        logic.append('    form.Size = new System.Drawing.Size(400, 300);')
        
        # Controls
        for control in config.get('controls', []):
            logic.extend(self._generate_control(control))
        
        # Show form
        logic.append('    form.ShowDialog();')
        logic.append('}')
        
        return '\n            '.join(logic)

    def _generate_control(self, control: Dict) -> List[str]:
        """Gera código para controles do visualizador"""
        if control['type'] == 'PropertyGrid':
            return [
                f'var grid = new PropertyGrid();',
                f'grid.SelectedObject = data;',
                f'grid.Dock = DockStyle.Fill;',
                f'form.Controls.Add(grid);'
            ]
        elif control['type'] == 'TreeView':
            return [
                f'var tree = new TreeView();',
                f'tree.Dock = DockStyle.Fill;',
                f'PopulateTree(tree, data);',
                f'form.Controls.Add(tree);'
            ]
        return []

    def save_visualizer(self, name: str, content: str):
        """Salva visualizador em arquivo"""
        visualizer_file = self.visualizers_path / f"{name}Visualizer.cs"
        visualizer_file.write_text(content)