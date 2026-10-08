#!/usr/bin/env bash
set -u

mapfile -t repos < <(
  git config -f .gitmodules --get-regexp '^submodule\..*\.path$' |
  awk '{print $2}'
)

manifest_names=(
  pyproject.toml
  uv.lock
  requirements.txt
  requirements-dev.txt
  setup.py
  setup.cfg
  package.json
  package-lock.json
  Gemfile
  Gemfile.lock
  Cargo.toml
  go.mod
  CMakeLists.txt
  Makefile
  Dockerfile
  docker-compose.yml
)

echo "=== TOP-LEVEL UPSTREAMS ==="

for repo in "${repos[@]}"; do
  echo
  echo "============================================================"
  echo "$repo"
  echo "============================================================"

  printf 'commit:  '
  git -C "$repo" rev-parse HEAD

  printf 'branch:  '
  git -C "$repo" symbolic-ref --short -q HEAD || echo "DETACHED"

  printf 'origin:  '
  git -C "$repo" remote get-url origin 2>/dev/null || echo "none"

  echo
  echo "root structure:"
  find "$repo" \
    -mindepth 1 \
    -maxdepth 1 \
    -not -name .git \
    -printf '  %f\n' |
    sort |
    head -80

  echo
  echo "dependency/build manifests:"

  found=0

  for name in "${manifest_names[@]}"; do
    while IFS= read -r file; do
      printf '  - %s\n' "${file#"$repo"/}"
      found=1
    done < <(
      find "$repo" \
        -maxdepth 3 \
        -type f \
        -name "$name" \
        -not -path '*/.git/*' \
        -not -path '*/third_party/*' \
        -not -path '*/build/*' \
        2>/dev/null |
      sort
    )
  done

  if [ "$found" -eq 0 ]; then
    echo "  (none detected)"
  fi

  echo
  echo "nested git dependencies:"

  if [ -f "$repo/.gitmodules" ]; then
    git -C "$repo" config -f .gitmodules --get-regexp '^submodule\..*\.\(path\|url\)$' \
      2>/dev/null |
      sed 's/^/  /' || true
  else
    echo "  (none)"
  fi

done

echo
echo "============================================================"
echo "ALL SUBMODULES INCLUDING NESTED"
echo "============================================================"

git submodule status --recursive || true
