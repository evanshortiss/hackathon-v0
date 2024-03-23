import subprocess
import tempfile
import os
import argparse

def clone_repo_and_find_tsx_files(repo_url, search_path='src/components'):
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f"Cloning repository into {tmpdirname}")
        subprocess.run(['git', 'clone', repo_url, tmpdirname], check=True)
        components_path = os.path.join(tmpdirname, search_path)
        if not os.path.exists(components_path):
            return [], "The 'components' directory does not exist at the specified path."
        tsx_files = [f for f in os.listdir(components_path) if f.endswith('.tsx')]
        return tsx_files, None

def main():
    parser = argparse.ArgumentParser(description='Clone a Git repository and list top-level .tsx files in a specific directory.')
    parser.add_argument('repo_url', type=str, help='The URL of the Git repository to clone.')
    parser.add_argument('--search-path', type=str, default='src/components', help='Path to search for the components directory (relative to the repository root).')

    args = parser.parse_args()

    tsx_files, error = clone_repo_and_find_tsx_files(args.repo_url, args.search_path)
    if error:
        print(error)
    else:
        print("Top-level .tsx files in 'components':", tsx_files)

if __name__ == '__main__':
    main()
