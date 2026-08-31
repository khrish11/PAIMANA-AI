"""Performance diagnostic script for PAIMANA-AI project."""

import os
import time
from pathlib import Path
from typing import Dict, List


def get_directory_size(path: Path) -> int:
    """Get total size of directory in bytes."""
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            try:
                total += item.stat().st_size
            except (OSError, PermissionError):
                pass
    return total


def count_files(path: Path, extensions: List[str] = None) -> int:
    """Count files in directory optionally filtered by extension."""
    count = 0
    for item in path.rglob('*'):
        if item.is_file():
            if extensions is None or item.suffix in extensions:
                count += 1
    return count


def measure_import_time(module_name: str) -> float:
    """Measure time to import a Python module."""
    start = time.time()
    try:
        __import__(module_name)
        return time.time() - start
    except ImportError:
        return -1


def main():
    """Run performance diagnostics."""
    project_root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("PAIMANA-AI Performance Diagnostic")
    print("=" * 60)
    
    # Directory sizes
    print("\n1. Directory Sizes:")
    print("-" * 40)
    dirs_to_check = ['backend', 'frontend', 'ml_pipeline', 'data', 'scripts']
    for dir_name in dirs_to_check:
        dir_path = project_root / dir_name
        if dir_path.exists():
            size_mb = get_directory_size(dir_path) / (1024 * 1024)
            print(f"{dir_name:20s}: {size_mb:8.2f} MB")
    
    # Data subdirectory analysis
    print("\n2. Data Directory Analysis:")
    print("-" * 40)
    data_dir = project_root / 'data'
    if data_dir.exists():
        for subdir in data_dir.iterdir():
            if subdir.is_dir():
                size_mb = get_directory_size(subdir) / (1024 * 1024)
                file_count = count_files(subdir)
                print(f"{subdir.name:30s}: {size_mb:8.2f} MB ({file_count:6d} files)")
    
    # File type breakdown
    print("\n3. File Type Breakdown:")
    print("-" * 40)
    extensions = {'.csv', '.py', '.js', '.tsx', '.ts', '.json', '.pdf'}
    for ext in sorted(extensions):
        count = count_files(project_root, [ext])
        print(f"{ext:10s}: {count:8d} files")
    
    # Python import times
    print("\n4. Python Import Times:")
    print("-" * 40)
    modules = ['sys', 'fastapi', 'pydantic']
    for module in modules:
        duration = measure_import_time(module)
        if duration >= 0:
            print(f"{module:20s}: {duration:8.4f}s")
    
    # Backend app import
    print("\n5. Backend App Import:")
    print("-" * 40)
    os.chdir(project_root / 'backend')
    duration = measure_import_time('app.main')
    if duration >= 0:
        print(f"app.main: {duration:8.4f}s")
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
