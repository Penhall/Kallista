
            using System;
            using System.Windows;
            using Microsoft.Extensions.DependencyInjection;
            
            namespace KanbanLegal
            {
                public partial class App : Application
                {
                    private readonly IServiceProvider _serviceProvider;
            
                    public App()
                    {
                        IServiceCollection services = new ServiceCollection();
                        ConfigureServices(services);
                        _serviceProvider = services.BuildServiceProvider();
                    }
            
                    private void ConfigureServices(IServiceCollection services)
                    {
                        // Register services here
                        RegisterViewModels(services);
                        RegisterServices(services);
                    }
            
                    private void RegisterViewModels(IServiceCollection services)
                    {
                        // Register ViewModels here
                    }
            
                    private void RegisterServices(IServiceCollection services)
                    {
                        // Register Services here
                    }
            
                    protected override void OnStartup(StartupEventArgs e)
                    {
                        base.OnStartup(e);
                    }
                }
            }
            