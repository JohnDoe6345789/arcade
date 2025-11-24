#!/usr/bin/env pwsh
$remote = if ($args.Length -ge 1) { $args[0] } else { "origin" }
$branch = git rev-parse --abbrev-ref HEAD
if ($branch -notlike "custom/*") { exit 0 }

git push $remote $branch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$existing = gh pr list --head $branch --state open --json number 2>$null | ConvertFrom-Json
if ($existing.Count -gt 0) { exit 0 }

gh pr create --head $branch --base main --title "Auto PR for $branch" --fill
