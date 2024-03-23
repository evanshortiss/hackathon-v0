import subprocess
import tempfile
import os
import argparse
from typing import Dict, List, Tuple

def find_component_usages(repo_path: str, component_names: List[str]) -> Dict[str, List[str]]:
    """
    Search for component usage throughout the repo.
    :param repo_path: The repository's local path.
    :param component_names: A list of component names to search for without the .tsx extension.
    :return: A dictionary where keys are component filenames and values are lists of files where the component is used.
    """
    usage_dict = {name: [] for name in component_names}
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.tsx'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for component in component_names:
                        # Match component usage by checking for the component name without the .tsx extension
                        search_str = f'/components/{os.path.splitext(component)[0]}'  # Adjust based on how components are referenced in your project
                        if search_str in content:
                            usage_dict[component].append(file_path[len(repo_path)+1:])  # Store relative path
    return usage_dict

def clone_repo_and_find_tsx_files(repo_url: str, search_path: str = 'src/components') -> Tuple[Dict[str, str], Dict[str, List[str]], str]:
    """
    Clones a repository, finds .tsx files in the components folder, and searches for their usage across the repo.
    :param repo_url: The Git repository URL.
    :param search_path: Path to the components directory within the repository.
    :return: A tuple containing two dictionaries (file contents, file usages) and an error message if any.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f"Cloning repository into {tmpdirname}")
        subprocess.run(['git', 'clone', repo_url, tmpdirname], check=True)
        
        components_path = os.path.join(tmpdirname, search_path)
        if not os.path.exists(components_path):
            return {}, {}, "The 'components' directory does not exist at the specified path."
        
        file_contents = {}
        component_names = []
        for filename in os.listdir(components_path):
            if filename.endswith('.tsx'):
                filepath = os.path.join(components_path, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    file_contents[filename] = content
                    component_names.append(filename)
        
        file_usages = find_component_usages(tmpdirname, component_names)
        
        return file_contents, file_usages, None

def main():
    parser = argparse.ArgumentParser(description='Clone a Git repository, find .tsx files in a specified directory, and list their usages.')
    parser.add_argument('repo_url', type=str, help='The URL of the Git repository to clone.')
    parser.add_argument('--search-path', type=str, default='src/components', help='Path to search for the components directory (relative to the repository root).')

    args = parser.parse_args()

    file_contents, file_usages, error = clone_repo_and_find_tsx_files(args.repo_url, args.search_path)
    if error:
        print(error)
    else:
        for filename, contents in file_contents.items():
            print(f"Filename: {filename}")
            for f in file_usages:
                print(f"{f} Used in: {', '.join(file_usages[f])}\n")

if __name__ == '__main__':
    main()
