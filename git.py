import os

def remove_openai_key_from_env():
    env_file_path = '.env'

    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as file:
            lines = file.readlines()

        with open(env_file_path, 'w') as file:
            for line in lines:
                if 'OPENAI_API_KEY' not in line:
                    file.write(line)

remove_openai_key_from_env()
