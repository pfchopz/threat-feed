import requests
import re
import os
from github import Github


def main():
    url = "https://raw.githubusercontent.com/Cisco-Talos/IOCs/main/2024/04/large-scale-brute-force-activity-targeting-vpns-ssh-services-with-commonly-used-login-credentials.txt"
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")
    git_file_path = os.getenv("GIT_FILE_PATH")
    github_token = os.getenv("GITHUB_TOKEN")
    local_file = "/tmp/threat-feed.txt"
    branch_name = os.getenv("GIT_BRANCH_NAME")

    write_valid_ips_to_file(get_threat_feed(url), local_file)
    update_github_file(repo_owner, repo_name, git_file_path, github_token, local_file, branch_name)


def get_threat_feed(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to download content from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_square_brackets(input_string):
    cleaned_string = input_string.replace("[", "")
    cleaned_string = cleaned_string.replace("]", "")
    return cleaned_string

def is_valid_ip(ip):
    # Regular expression pattern for IPv4 address
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    # Check if the string matches the IPv4 pattern
    if re.match(ipv4_pattern, ip):
        return True
    else:
        return False

def write_valid_ips_to_file(threat_feed, output_file):
    with open(output_file, "w") as f:
        for line in threat_feed.splitlines():
            new_line = delete_square_brackets(line)
            if is_valid_ip(new_line):
                f.write(new_line + "\n")

def update_github_file(repo_owner, repo_name, file_path, github_token, local_file, branch_name):
    # Authenticate with GitHub using the provided token
    g = Github(github_token)

    # Get the repository
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    # Get the contents of the existing file
    file_content = repo.get_contents(file_path)
    
    # Read the contents of the local file
    with open(local_file, "r") as f:
        new_content = f.read()

    # Update the file
    repo.update_file(
        path=file_path,
        message="Updated file via API",
        content=new_content,
        sha=file_content.sha,
        branch=branch_name
    )
    print("File updated successfully!")
    
def handler(event, context):
    main()


if __name__ == '__main__':
    main()
