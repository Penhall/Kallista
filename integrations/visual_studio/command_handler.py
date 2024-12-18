# integrations/visual_studio/command_handler.py
from typing import Dict, List, Any
from pathlib import Path

class VSCommandHandler:
    def __init__(self):
        self.commands_path = Path("Commands")
        self.commands_path.mkdir(exist_ok=True)

    def generate_command(self, config: Dict) -> str:
        """Gera código para um comando do Visual Studio"""
        return f'''
using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using Task = System.Threading.Tasks.Task;

namespace Kallista.Commands
{{
    internal sealed class {config['name']}Command
    {{
        public const int CommandId = {config['command_id']};
        public static readonly Guid CommandSet = new Guid("{config['command_set']}");
        private readonly AsyncPackage package;

        private {config['name']}Command(AsyncPackage package, OleMenuCommandService commandService)
        {{
            this.package = package ?? throw new ArgumentNullException(nameof(package));
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, CommandId);
            var menuItem = new MenuCommand(Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }}

        public static async Task InitializeAsync(AsyncPackage package)
        {{
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new {config['name']}Command(package, commandService);
        }}

        public static {config['name']}Command Instance {{ get; private set; }}

        private void Execute(object sender, EventArgs e)
        {{
            ThreadHelper.ThrowIfNotOnUIThread();
            {self._generate_command_execution(config)}
        }}
        
        {self._generate_helper_methods(config)}
    }}
}}'''

    def _generate_command_execution(self, config: Dict) -> str:
        """Gera código para execução do comando"""
        code = []
        
        # Logging
        code.append('try {')
        code.append('    var dte = Package.GetGlobalService(typeof(EnvDTE.DTE)) as EnvDTE.DTE;')
        code.append('    if (dte == null) return;')
        
        # Command specific logic
        for action in config.get('actions', []):
            code.extend(self._generate_action_code(action))
        
        # Error handling
        code.append('} catch (Exception ex) {')
        code.append('    VsShellUtilities.ShowMessageBox(')
        code.append('        this.package,')
        code.append('        ex.Message,')
        code.append('        "Error",')
        code.append('        OLEMSGICON.OLEMSGICON_CRITICAL,')
        code.append('        OLEMSGBUTTON.OLEMSGBUTTON_OK,')
        code.append('        OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);')
        code.append('}')
        
        return '\n            '.join(code)

    def _generate_action_code(self, action: Dict) -> List[str]:
        """Gera código para uma ação específica do comando"""
        if action['type'] == 'create_project':
            return [
                f'var solution = dte.Solution;',
                f'var template = "{action["template"]}";',
                f'var projectName = "{action["name"]}";',
                f'solution.AddFromTemplate(template, projectName, projectName);'
            ]
        elif action['type'] == 'add_file':
            return [
                f'var project = dte.SelectedItems.Item(1).Project;',
                f'var template = "{action["template"]}";',
                f'project.ProjectItems.AddFromTemplate(template, "{action["filename"]}");'
            ]
        elif action['type'] == 'run_tool':
            return [
                f'var toolWindow = this.package.FindToolWindow(typeof({action["window"]}), 0, true);',
                f'if ((null == toolWindow) || (null == toolWindow.Frame))',
                f'    throw new NotSupportedException("Cannot create tool window");',
                f'IVsWindowFrame windowFrame = (IVsWindowFrame)toolWindow.Frame;',
                f'Microsoft.VisualStudio.ErrorHandler.ThrowOnFailure(windowFrame.Show());'
            ]
        return []

    def _generate_helper_methods(self, config: Dict) -> str:
        """Gera métodos auxiliares para o comando"""
        methods = []
        
        if config.get('needs_project_validation', False):
            methods.append('''
        private bool ValidateProject()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var dte = Package.GetGlobalService(typeof(EnvDTE.DTE)) as EnvDTE.DTE;
            if (dte?.SelectedItems.Item(1)?.Project == null)
            {
                VsShellUtilities.ShowMessageBox(
                    this.package,
                    "Please select a project in Solution Explorer.",
                    "No Project Selected",
                    OLEMSGICON.OLEMSGICON_INFO,
                    OLEMSGBUTTON.OLEMSGBUTTON_OK,
                    OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
                return false;
            }
            return true;
        }''')
            
        if config.get('needs_file_operations', False):
            methods.append('''
        private void SaveAllFiles()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var dte = Package.GetGlobalService(typeof(EnvDTE.DTE)) as EnvDTE.DTE;
            dte?.Documents.SaveAll();
        }''')
            
        return '\n'.join(methods)

    def save_command(self, name: str, content: str):
        """Salva o comando em arquivo"""
        command_file = self.commands_path / f"{name}Command.cs"
        command_file.write_text(content)