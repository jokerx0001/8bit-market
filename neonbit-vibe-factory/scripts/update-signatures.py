#!/usr/bin/env python3
"""
Compute SHA256 signatures for page files and write them to maintenance and result files.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EXTENSIONS = {'.vue', '.tsx', '.jsx', '.js', '.css', '.scss', '.less'}
MAINTENANCE_FILENAME = '.page-signatures.jsonl'
RESULT_DIRNAME = 'page-signatures-result'


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of a single file's contents."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        sha256.update(f.read())
    return sha256.hexdigest()


def compute_page_hash(base_dir: Path, page_name: str) -> tuple[str | None, list[str]]:
    """
    Compute SHA256 hash for all relevant files in a page directory.
    Returns (hash, errors). hash is None if page dir doesn't exist.
    """
    page_dir = base_dir / page_name
    if not page_dir.exists():
        return None, []

    # Find all relevant files, sort them
    files = []
    for ext in EXTENSIONS:
        files.extend(page_dir.rglob(f'*{ext}'))
    files.sort()

    # Concatenate all file bytes and hash
    sha256 = hashlib.sha256()
    errors = []
    for filepath in files:
        try:
            with open(filepath, 'rb') as f:
                sha256.update(f.read())
        except OSError:
            errors.append(str(filepath))

    return sha256.hexdigest(), errors


def load_maintenance(filepath: Path) -> dict[str, str]:
    """Load existing signatures from maintenance file."""
    signatures = {}
    if filepath.exists():
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        signatures[parts[0]] = parts[1]
    return signatures


def write_maintenance(filepath: Path, signatures: dict[str, str]) -> None:
    """Write signatures to maintenance file in JSONL format."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        for page_name, hash_value in signatures.items():
            f.write(f'{page_name}:{hash_value}\n')


def write_result_file(result_file: Path, page_name: str, old_hash: str | None, new_hash: str) -> None:
    """Append a result entry to the result file."""
    result_file.parent.mkdir(parents=True, exist_ok=True)
    with open(result_file, 'a') as f:
        f.write(json.dumps({'page': page_name, 'old': old_hash, 'new': new_hash}) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Update page signatures')
    parser.add_argument('--pages', required=True, help='Comma-separated list of page names')
    parser.add_argument('--base-dir', required=True, help='Base directory containing page folders')
    parser.add_argument('--output-dir', required=True, help='Output directory for maintenance and result files')
    args = parser.parse_args()

    pages = [p.strip() for p in args.pages.split(',') if p.strip()]
    base_dir = Path(args.base_dir)
    output_dir = Path(args.output_dir)

    maintenance_file = output_dir / MAINTENANCE_FILENAME
    result_file = output_dir / RESULT_DIRNAME / f'result-{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.jsonl'
    signatures = load_maintenance(maintenance_file)

    updated_pages = []
    errors = []

    for page_name in pages:
        new_hash, file_errors = compute_page_hash(base_dir, page_name)

        if new_hash is None:
            # Page directory doesn't exist - skip
            continue

        # Record errors but continue
        if file_errors:
            errors.append(f'Page {page_name}: failed to read {len(file_errors)} file(s)')

        old_hash = signatures.get(page_name)
        if new_hash != old_hash:
            updated_pages.append(page_name)
        signatures[page_name] = new_hash

        try:
            write_result_file(result_file, page_name, old_hash, new_hash)
        except OSError as e:
            print(json.dumps({'status': 'error', 'message': f'Failed to write result file: {e}'}))
            return 1

    # Write maintenance file
    try:
        write_maintenance(maintenance_file, signatures)
    except OSError as e:
        print(json.dumps({'status': 'error', 'message': f'Failed to write maintenance file: {e}'}))
        return 1

    print(json.dumps({'status': 'ok', 'updated': updated_pages}))
    return 0


if __name__ == '__main__':
    sys.exit(main())