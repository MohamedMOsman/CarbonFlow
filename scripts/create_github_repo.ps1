param(
    [Parameter(Mandatory = $true)]
    [string]$RepoName,

    [string]$Description = "",

    [ValidateSet('public','private')]
    [string]$Visibility = 'private',

    [string]$Org,

    [string]$Token
)

# Requires: Git installed, and a valid GitHub token with `repo` scope
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\create_github_repo.ps1 -RepoName "system-dynamics-model" -Visibility private

$ErrorActionPreference = 'Stop'

function Fail($msg) {
  Write-Error $msg
  exit 1
}

if (-not $Token) {
  $Token = $env:GITHUB_TOKEN
}

if (-not $Token) {
  Fail 'Missing GitHub token. Provide -Token or set $env:GITHUB_TOKEN.'
}

# Determine API endpoint
$apiBase = 'https://api.github.com'
$createUri = if ($Org) { "$apiBase/orgs/$Org/repos" } else { "$apiBase/user/repos" }

$isPrivate = $Visibility -eq 'private'
$payload = @{ name = $RepoName; description = $Description; private = $isPrivate; auto_init = $false } | ConvertTo-Json

$headers = @{
  'Authorization' = "token $Token"
  'User-Agent'    = 'sdm-create-repo-script'
  'Accept'        = 'application/vnd.github+json'
}

Write-Host "Creating GitHub repo '$RepoName' (Visibility: $Visibility) ..." -ForegroundColor Cyan
$resp = Invoke-RestMethod -Method POST -Uri $createUri -Headers $headers -Body $payload

if (-not $resp -or -not $resp.clone_url) {
  Fail 'GitHub API response did not contain expected data.'
}

$cloneUrl = $resp.clone_url
$htmlUrl  = $resp.html_url
Write-Host "Created: $htmlUrl" -ForegroundColor Green

# Ensure we are in a git repository
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
  Fail 'Current folder is not a git repository. Run `git init -b main` first.'
}

# Add remote origin if missing
$remoteList = git remote *> $null; $remoteList = if ($LASTEXITCODE -eq 0) { (git remote).Trim() } else { @() }
if (-not ($remoteList -contains 'origin')) {
  Write-Host "Adding remote 'origin' -> $cloneUrl"
  git remote add origin $cloneUrl
} else {
  Write-Host "Remote 'origin' already exists. Updating URL -> $cloneUrl"
  git remote set-url origin $cloneUrl
}

# Determine current branch (default to main)
$branch = (git branch --show-current).Trim()
if (-not $branch) { $branch = 'main' }

Write-Host "Pushing branch '$branch' to origin ..."
git push -u origin $branch

if ($LASTEXITCODE -eq 0) {
  Write-Host "Success! Repo synced: $htmlUrl" -ForegroundColor Green
} else {
  Fail 'Push failed. Check your git configuration and try again.'
}

