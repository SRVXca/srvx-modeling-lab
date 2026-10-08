#!/usr/bin/env bash
set -euo pipefail

repos=(
  "canmet-energy/h2k-hpxml"
  "canmet-energy/community-energy-orchestrator"
  "canmet-energy/hpxml-schema-api"
  "canmet-energy/housing-archetypes"
  "canmet-energy/tandm"
  "NatLabRockies/OpenStudio-HPXML"
  "NatLabRockies/EnergyPlus"
  "open205/toolkit-205"
  "IfcOpenShell/IfcOpenShell"
  "cityjson/cjio"
)

echo "== validating upstream repositories =="

for repo in "${repos[@]}"; do
  url="https://github.com/${repo}.git"
  printf '%-50s ' "$repo"

  if git ls-remote -q "$url" HEAD >/dev/null 2>&1; then
    echo "OK"
  else
    echo "MISSING"
    echo
    echo "Stopped before cloning anything."
    exit 1
  fi
done

echo
echo "== adding upstream repositories =="

for repo in "${repos[@]}"; do
  owner="${repo%%/*}"
  name="${repo#*/}"
  path="repos/${owner}/${name}"
  url="https://github.com/${repo}.git"

  mkdir -p "repos/${owner}"

  if [ -f .gitmodules ] &&
     git config -f .gitmodules --get-regexp path 2>/dev/null |
       grep -Fq "$path"; then
    echo "SKIP  $repo"
    continue
  fi

  echo "ADD   $repo"
  git submodule add --depth 1 "$url" "$path"
done

echo
echo "== initializing nested upstream dependencies =="

git submodule update --init --recursive --depth 1

echo
echo "== registered repositories =="

git submodule status --recursive
