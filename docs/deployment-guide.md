# 🚀 Kallista - Guia de Deployment

## 📋 Índice
1. [Requisitos](#requisitos)
2. [Ambientes](#ambientes)
3. [Configuração](#configuração)
4. [Pipeline de Deployment](#pipeline-de-deployment)
5. [Processo de Release](#processo-de-release)
6. [Monitoramento](#monitoramento)
7. [Troubleshooting](#troubleshooting)

## Requisitos

### 💻 Sistema
- Windows Server 2019 ou superior
- .NET 6.0 Runtime
- SQL Server 2019+
- IIS 10+
- 8GB RAM (mínimo)
- 50GB espaço em disco

### 🔑 Permissões
- Acesso ao Azure DevOps
- Permissões de administrador no IIS
- Acesso ao SQL Server
- Certificados SSL válidos

### 📦 Dependências
- Nuget packages
- External services
- Configuration keys

## Ambientes

### 🔧 Desenvolvimento (DEV)
```json
{
    "Environment": "Development",
    "ConnectionStrings": {
        "DefaultConnection": "Server=dev-sql;Database=KallistaDB;..."
    },
    "Logging": {
        "Level": "Debug"
    }
}
```

### 🧪 Homologação (STG)
```json
{
    "Environment": "Staging",
    "ConnectionStrings": {
        "DefaultConnection": "Server=stg-sql;Database=KallistaDB;..."
    },
    "Logging": {
        "Level": "Information"
    }
}
```

### 🌐 Produção (PROD)
```json
{
    "Environment": "Production",
    "ConnectionStrings": {
        "DefaultConnection": "Server=prod-sql;Database=KallistaDB;..."
    },
    "Logging": {
        "Level": "Warning"
    }
}
```

## Configuração

### 🔧 IIS Setup
```powershell
# Install IIS Features
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Install ASP.NET Core Hosting Bundle
Invoke-WebRequest -Uri https://dot.net/v1/dotnet-install.ps1 -OutFile dotnet-install.ps1
./dotnet-install.ps1 -Channel 6.0 -Runtime aspnetcore

# Configure Application Pool
New-WebAppPool -Name "KallistaPool"
Set-ItemProperty -Path "IIS:\AppPools\KallistaPool" -Name "managedRuntimeVersion" -Value ""
Set-ItemProperty -Path "IIS:\AppPools\KallistaPool" -Name "startMode" -Value "AlwaysRunning"
```

### 📄 Web.config
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" />
    </handlers>
    <aspNetCore processPath="dotnet" 
                arguments=".\Kallista.dll" 
                stdoutLogEnabled="true" 
                stdoutLogFile=".\logs\stdout" 
                hostingModel="inprocess" />
  </system.webServer>
</configuration>
```

## Pipeline de Deployment

### 🔄 Azure DevOps Pipeline
```yaml
trigger:
  branches:
    include:
    - main
    - release/*

variables:
  solution: '**/*.sln'
  buildPlatform: 'Any CPU'
  buildConfiguration: 'Release'

stages:
- stage: Build
  jobs:
  - job: Build
    pool:
      vmImage: 'windows-latest'
    steps:
    - task: NuGetToolInstaller@1
    - task: NuGetCommand@2
      inputs:
        restoreSolution: '$(solution)'
    - task: VSBuild@1
      inputs:
        solution: '$(solution)'
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'
    - task: VSTest@2
      inputs:
        platform: '$(buildPlatform)'
        configuration: '$(buildConfiguration)'

- stage: Deploy
  jobs:
  - deployment: Deploy
    pool:
      vmImage: 'windows-latest'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: IISWebAppDeploymentOnMachineGroup@0
            inputs:
              WebSiteName: 'Kallista'
              Package: '$(System.DefaultWorkingDirectory)/**/*.zip'
```

## Processo de Release

### 📝 Checklist Pré-Deploy
1. Verificar todos os testes
2. Validar migrações de banco
3. Revisar logs de erro
4. Backup do ambiente atual
5. Notificar stakeholders

### 🚀 Deployment Steps
1. **Backup**
```powershell
# Backup Database
$date = Get-Date -Format "yyyyMMdd"
Backup-SqlDatabase -ServerInstance "prod-sql" -Database "KallistaDB" -BackupFile "C:\Backups\KallistaDB_$date.bak"

# Backup Application Files
$appPath = "C:\inetpub\wwwroot\Kallista"
Compress-Archive -Path $appPath -DestinationPath "C:\Backups\Kallista_$date.zip"
```

2. **Database Migration**
```powershell
# Run Migrations
dotnet ef database update --connection "Server=prod-sql;Database=KallistaDB;..."
```

3. **Application Deployment**
```powershell
# Stop Application Pool
Stop-WebAppPool -Name "KallistaPool"

# Deploy New Files
Expand-Archive -Path "Release.zip" -DestinationPath $appPath -Force

# Start Application Pool
Start-WebAppPool -Name "KallistaPool"
```

### ✅ Verificação Pós-Deploy
1. Verificar status do aplicativo
2. Validar conexões de banco
3. Testar funcionalidades críticas
4. Monitorar logs de erro
5. Verificar métricas de performance

## Monitoramento

### 📊 Métricas
- CPU Usage
- Memory Usage
- Response Time
- Error Rate
- Active Users

### 📝 Logs
```plaintext
/logs
  ├── application.log    # Logs da aplicação
  ├── error.log         # Erros e exceções
  ├── audit.log         # Logs de auditoria
  └── performance.log   # Métricas de performance
```

### 🔍 Alertas
```json
{
    "alerts": {
        "highCpu": {
            "threshold": 80,
            "duration": "5m"
        },
        "highMemory": {
            "threshold": 85,
            "duration": "5m"
        },
        "errorRate": {
            "threshold": 5,
            "duration": "1m"
        }
    }
}
```

## Troubleshooting

### 🔍 Problemas Comuns

1. **Erro de Conexão com Banco**
```powershell
# Verificar status do SQL Server
Get-Service MSSQLSERVER

# Testar conexão
$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = "Server=prod-sql;Database=KallistaDB;..."
$conn.Open()
```

2. **Erro 503 - Application Pool**
```powershell
# Reiniciar Application Pool
Restart-WebAppPool "KallistaPool"

# Verificar logs do IIS
Get-EventLog -LogName "Application" -Source "IIS*" -Newest 50
```

3. **Problemas de Performance**
```powershell
# Monitorar Performance
Get-Counter '\Processor(_Total)\% Processor Time'
Get-Counter '\Memory\Available MBytes'
Get-Counter '\ASP.NET Applications(__Total__)\Requests/Sec'
```

### 🔄 Rollback
```powershell
# Rollback Database
Restore-SqlDatabase -ServerInstance "prod-sql" -Database "KallistaDB" -BackupFile "C:\Backups\KallistaDB_$date.bak"

# Rollback Application
Remove-Item -Path $appPath -Recurse
Expand-Archive -Path "C:\Backups\Kallista_$date.zip" -DestinationPath $appPath
```

---
Data de Atualização: 20/12/2024