# System Dynamics Model

This project contains assets for a System Dynamics Model (SDM).

## GitHub Repository Setup

This folder is initialized as a local git repository and includes a helper script to create a GitHub repository and push the current code.

### Quick Start

1) Set your GitHub token (with `repo` scope):

   - PowerShell (temporary for this session):
     
     `$env:GITHUB_TOKEN = 'YOUR_TOKEN_HERE'`

2) Create the GitHub repo and push:

   - From this folder run:
     
     `powershell -ExecutionPolicy Bypass -File .\scripts\create_github_repo.ps1 -RepoName "system-dynamics-model" -Visibility private -Description "System Dynamics Model"`

   - To create under an organization, add: `-Org YourOrgName`

The script will create the repo via GitHub's API, add it as `origin`, and push the current `main` branch.

