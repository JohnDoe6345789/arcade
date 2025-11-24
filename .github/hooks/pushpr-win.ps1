#!/usr/bin/env pwsh
$remote = if ($args.Length -ge 1) { $args[0] } else { "origin" }

$branch = git rev-parse --abbrev-ref HEAD
if ($branch -notlike "custom/*") { exit 0 }

git push $remote $branch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { exit 0 }

$existing = gh pr list --head $branch --state open --json number 2>$null | ConvertFrom-Json
if (-not $existing -or $existing.Count -eq 0) {
  gh pr create --head $branch --base main --title "Auto PR for $branch" --fill | Out-Null
}
