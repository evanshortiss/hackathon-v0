from urllib.parse import urlparse
from typing import Dict, List, Tuple
from os import getenv
from dotenv import load_dotenv
import subprocess
import tempfile
import os
import argparse
import requests
import base64

load_dotenv()

GITHUB_TOKEN = getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def fork_repository(repo_url):
    """
    Forks the given repository to the authenticated user's GitHub account.
    """
    owner, repo = repo_url.split('/')[-2:]
    fork_url = f'https://api.github.com/repos/{owner}/{repo}/forks'
    response = requests.post(fork_url, headers=HEADERS)
    if response.status_code in [202, 200]:
        forked_repo_url = response.json()['clone_url']
        print(f"Repository forked successfully: {forked_repo_url}")
        return forked_repo_url
    else:
        print(f"Failed to fork repository: {response.json()}")
        return None

def replace_file_contents(repo_path, file_contents_map):
    """
    Replaces the content of files in the repository based on the provided map.
    """
    for filepath, new_content in file_contents_map.items():
        full_path = os.path.join(repo_path, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

def create_pull_request(forked_repo_url, original_repo_url, branch_name='v1'):
    """
    Creates a pull request from the forked repository to the original repository.
    """
    owner, repo = original_repo_url.split('/')[-2:]
    pr_url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    data = {
        'title': 'Automated Update',
        'head': f"{forked_repo_url.split('/')[-2]}:{branch_name}",
        'base': 'main',  # Change this if the base branch is different
        'body': 'This is an automated pull request.',
    }
    response = requests.post(pr_url, headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f"Pull request created successfully: {response.json()['html_url']}")
    else:
        print(f"Failed to create pull request: {response.json()}")


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

def clone_repository(repo_url: str, tmp_dir: str):
    """
    Clones a repository into a specified temporary directory.
    :param repo_url: The Git repository URL to clone.
    :param tmp_dir: The temporary directory where the repository will be cloned.
    """
    print(f"Cloning repository into {tmp_dir}")
    subprocess.run(['git', 'clone', repo_url, tmp_dir], check=True)

def find_tsx_files_and_usages(tmp_dir: str, search_path: str = 'src/components') -> Tuple[Dict[str, str], Dict[str, List[str]], str]:
    """
    Finds .tsx files in the components folder and searches for their usage across the repository.
    :param tmp_dir: The temporary directory where the repository has been cloned.
    :param search_path: Path to the components directory within the repository.
    :return: A tuple containing two dictionaries (file contents, file usages) and an error message if any.
    """
    components_path = os.path.join(tmp_dir, search_path)
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
    
    file_usages = find_component_usages(tmp_dir, component_names)
    
    return file_contents, file_usages, None

def create_or_update_file(user, repo, path, token, content, message, branch="v1"):
    """
    Create or update a file in a GitHub repository.

    :param user: Username of the repository owner.
    :param repo: Name of the repository.
    :param path: Path to the file within the repository.
    :param token: GitHub Personal Access Token (PAT) with repo scope.
    :param content: Content to be written to the file.
    :param message: Commit message.
    :param branch: Branch where the commit should be applied.
    """
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    print(f'Create/update file {url}')
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Convert content to base64 encoding
    content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    data = {
        "message": message,
        "content": content_base64,
        "branch": branch
    }

    # Attempt to get the file to check if it exists and get its SHA if it does
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # If the file exists, include the SHA to update it
        data["sha"] = response.json()['sha']

    # Create or update the file
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"File {'created' if response.status_code == 201 else 'updated'} successfully.")
        print("URL:", response.json()['content']['html_url'])
    else:
        print("Failed to create or update the file:", response.json())

def extract_user_repo_from_url(url):
    """
    Extracts the GitHub username and repository name from a given GitHub repository URL.
    
    :param url: A string containing the GitHub repository URL.
    :return: A tuple containing the username and repository name.
    """
    parsed_url = urlparse(url)
    
    path_components = parsed_url.path[1:].split('/')
    
    username = path_components[0]
    repo_name = path_components[1].removesuffix('.git')
    
    return username, repo_name


def create_git_branch(user, repo, token, new_branch_name, base_branch='main'):
    """
    Create a new git branch in the specified repository.

    :param user: GitHub username or organization where the repo is hosted.
    :param repo: Repository name.
    :param token: Personal Access Token (PAT) for authentication with repo scope.
    :param new_branch_name: The name of the new branch to be created.
    :param base_branch: The name of the base branch from which to branch off.
    """
    repo_api_url = f'https://api.github.com/repos/{user}/{repo}'
    get_ref_url = f'{repo_api_url}/git/ref/heads/{base_branch}'
    create_ref_url = f'{repo_api_url}/git/refs'

    # Headers for authentication
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    # Step 1: Get the SHA of the latest commit on the base branch
    response = requests.get(get_ref_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch base branch SHA: {response.json()}")
    commit_sha = response.json()['object']['sha']

    # Step 2: Create a new branch by posting a new reference
    data = {
        'ref': f'refs/heads/{new_branch_name}',
        'sha': commit_sha
    }
    response = requests.post(create_ref_url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Branch '{new_branch_name}' created successfully.")
    else:
        raise Exception(f"Failed to create branch: {response.json()}")


def main():
    parser = argparse.ArgumentParser(description='Clone a Git repository, find .tsx files in a specified directory, and list their usages.')
    parser.add_argument('repo_url', type=str, help='The URL of the Git repository to clone.')
    parser.add_argument('--search-path', type=str, default='src/components', help='Path to search for the components directory (relative to the repository root).')

    args = parser.parse_args()

    # Fork the repo to v1 bot's account
    forked_repo_url = fork_repository(args.repo_url)

    # Clone the fork into a tmpdir
    tmpdirname = tempfile.TemporaryDirectory().name
    clone_repository(forked_repo_url, tmpdirname)
    
    # Find v0 components and references to the components in pages
    file_contents, file_usages, error = find_tsx_files_and_usages(tmpdirname, args.search_path)

    if error:
        print(error)
        exit(1)

    # Pass files and references to Langchain/LLM
    
    username, repo_name = extract_user_repo_from_url(forked_repo_url)
    create_git_branch(username, repo_name, GITHUB_TOKEN, 'v1')
    for filepath, content in test_file_contents.items():
        create_or_update_file(username, repo_name, filepath, GITHUB_TOKEN, content, f'v1 update/create {filepath}')

if __name__ == '__main__':
    main()
