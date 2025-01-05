# tools/wpf/templates/viewmodels/main_viewmodel.py

class MainViewModelTemplate:
    @staticmethod
    def implementation(project_name: str) -> str:
        return f'''using System;
using System.Threading.Tasks;
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using {project_name}.Services.Navigation;

namespace {project_name}.ViewModels
{{
    public partial class MainViewModel : ViewModelBase
    {{
        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(WelcomeMessage))]
        private string userName = string.Empty;

        [ObservableProperty]
        private bool isInitialized;

        public string WelcomeMessage => string.IsNullOrEmpty(UserName) 
            ? "Welcome to {project_name}!" 
            : $"Welcome, {{UserName}}!";

        public ObservableCollection<string> RecentItems {{ get; }} = new();

        public MainViewModel(INavigationService navigationService) : base(navigationService)
        {{
            Title = "{project_name}";
            SetupCommands();
        }}

        [RelayCommand]
        private async Task InitializeAsync()
        {{
            await ExecuteAsync(async () =>
            {{
                await Task.Delay(1000);
                
                RecentItems.Clear();
                RecentItems.Add("Sample Item 1");
                RecentItems.Add("Sample Item 2");
                RecentItems.Add("Sample Item 3");

                IsInitialized = true;
                StatusMessage = "Application initialized successfully";
            }});
        }}

        [RelayCommand(CanExecute = nameof(CanUpdateUserName))]
        private void UpdateUserName(string newName)
        {{
            UserName = newName;
            StatusMessage = "Username updated successfully";
        }}

        private bool CanUpdateUserName(string newName)
        {{
            return !string.IsNullOrEmpty(newName) && !IsBusy;
        }}

        public override async Task LoadAsync()
        {{
            await base.LoadAsync();
            await InitializeAsync();
        }}

        private void SetupCommands()
        {{
            // Additional command setup if needed
        }}
    }}
}}'''