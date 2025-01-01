# tools/wpf/templates/infrastructure/project.py
class ProjectTemplates:
    @staticmethod
    def csproj(project_name: str, packages: list) -> str:
        package_refs = '\n'.join(
            f'        <PackageReference Include="{package}" Version="{version}" />'
            for package, version in packages
        )
        
        return f'''<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <OutputType>WinExe</OutputType>
        <TargetFramework>net7.0-windows</TargetFramework>
        <Nullable>enable</Nullable>
        <UseWPF>true</UseWPF>
        <RootNamespace>{project_name}</RootNamespace>
        <AssemblyName>{project_name}</AssemblyName>
        <Version>1.0.0</Version>
        <Authors>Kallista Generator</Authors>
        <Company>Kallista</Company>
        <Product>{project_name}</Product>
    </PropertyGroup>

    <ItemGroup>
{package_refs}
    </ItemGroup>
</Project>'''

    @staticmethod
    def solution(project_name: str, project_guid: str) -> str:
        return f'''Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{project_name}", "{project_name}.csproj", "{{{project_guid}}}"
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Any CPU = Debug|Any CPU
        Release|Any CPU = Release|Any CPU
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {{{project_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {{{project_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {{{project_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {{{project_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU
    EndGlobalSection
EndGlobal'''