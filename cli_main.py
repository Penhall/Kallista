# cli_main.py
from cli.command_handler import ProjectCLI

def main():
    print("=== Kallista Project Generator ===")
    print("Digite 'help' para ver os comandos disponíveis")
    cli = ProjectCLI()
    cli.start()

if __name__ == "__main__":
    main()