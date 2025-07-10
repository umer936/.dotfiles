#!/bin/bash

set -euo pipefail

# Optional first argument: target subdirectory inside the repo (default to repo root)
target_dir=${1:-.}

# Get repo root directory
repo_root=$(git rev-parse --show-toplevel)

echo "Repo root: $repo_root"

# Absolute path of target directory inside repo
target_path="$repo_root/$target_dir"

# Check target_dir exists inside repo
if [[ ! -d "$target_path" ]]; then
    echo "Error: target directory '$target_dir' does not exist inside repo."
    exit 1
fi

# Get current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch detected: $current_branch"

echo "Fetching latest changes from origin/$current_branch..."
git fetch origin "$current_branch"

echo "Getting list of files changed between local and origin/$current_branch under '$target_dir'..."
cd "$repo_root"

git diff --name-only -z "origin/$current_branch" -- "$target_dir" | while IFS= read -r -d '' file; do
    full_path="$repo_root/$file"

    # Skip if file doesn't exist locally (deleted or renamed)
    if [[ ! -e "$full_path" ]]; then
        echo "Skipping missing file: $file"
        continue
    fi

    # Get remote permission mode (e.g., 644 or 755)
    remote_mode_full=$(git ls-files -s "$file" | awk '{print $1}')
    remote_mode=${remote_mode_full#100}  # strip leading '100'

    # Get local file permission in numeric format (e.g., 644 or 755)
    local_mode=$(stat -c "%a" "$full_path")

    if [[ "$local_mode" != "$remote_mode" ]]; then
        echo "Updating permissions for $file: $local_mode -> $remote_mode"
        chmod "$remote_mode" "$full_path"
    else
        echo "Permissions for $file already match remote ($remote_mode)"
    fi

    # Additionally ensure executable bit matches git index exactly for regular files (100644 or 100755)
    if [[ "$remote_mode_full" =~ ^100(644|755)$ ]]; then
        if [[ "$remote_mode_full" == "100755" ]]; then
            if [[ ! -x "$full_path" ]]; then
                echo "Adding execute bit to $file"
                chmod +x "$full_path"
            fi
        else
            if [[ -x "$full_path" ]]; then
                echo "Removing execute bit from $file"
                chmod -x "$full_path"
            fi
        fi
    fi
done

echo "Permission sync completed."
