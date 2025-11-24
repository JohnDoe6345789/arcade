#!/usr/bin/env pwsh
function Show-Usage {
@'
Usage: pushpr-win.ps1 [remote] [--auto-merge] [--merge-method=<merge|squash|rebase>]
  remote          Remote to push to (default: origin)
  --auto-merge    Enable gh auto-merge with branch deletion for the PR
  --merge-method  Preferred merge method when setting auto-merge (default: repo/GitHub default)

You can also set:
  $env:PUSHPR_AUTO_MERGE=1            # same as --auto-merge
  $env:PUSHPR_MERGE_METHOD=<method>   # same as --merge-method
'@
}

$remote = "origin"
$autoMerge = if ($env:PUSHPR_AUTO_MERGE) { 1 } else { 0 }
$mergeMethod = if ($env:PUSHPR_MERGE_METHOD) { $env:PUSHPR_MERGE_METHOD } else { "" }

foreach ($arg in $args) {
  switch -Regex ($arg) {
    '^--auto-merge$' { $autoMerge = 1; continue }
    '^--merge-method=(.+)$' { $mergeMethod = $Matches[1]; continue }
    '^(--help|-h)$' { Show-Usage; exit 0 }
    default { $remote = $arg }
  }
}

$branch = git rev-parse --abbrev-ref HEAD
if ($branch -notlike "custom/*") { exit 0 }

git push $remote $branch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { exit 0 }

$prNumber = gh pr list --head $branch --state open --json number 2>$null | ConvertFrom-Json | Select-Object -First 1 -ExpandProperty number
if (-not $prNumber) {
  $prNumber = gh pr create --head $branch --base main --title "Auto PR for $branch" --fill --json number --jq '.number' 2>$null
}

if ($prNumber) {
  $diffSummary = ""
  try {
    $diffSummary = gh pr diff $prNumber --stat 2>$null
  } catch {
    $diffSummary = ""
  }

  if (-not [string]::IsNullOrWhiteSpace($diffSummary)) {
    $commentBody = @"
Automated diff summary from push hook:
```
$diffSummary
```
"@
    gh pr comment $prNumber --body $commentBody 2>$null | Out-Null
  }
}

if ($prNumber -and $autoMerge -eq 1) {
  $mergeFlag = ""
  switch ($mergeMethod) {
    "merge" { $mergeFlag = "--merge" }
    "squash" { $mergeFlag = "--squash" }
    "rebase" { $mergeFlag = "--rebase" }
  }
  gh pr merge $prNumber --auto --delete-branch $mergeFlag 2>$null | Out-Null
}
