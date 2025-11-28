#!/usr/bin/env python3
# Boot Animation Zipper Script
# Zips bootanimation folders in store-only mode (no compression)
# Each folder must have part0/ and desc.txt to be processed

import os
import sys
import zipfile
import re
from pathlib import Path


# Check if folder has part0/ directory and desc.txt file
def is_valid_bootanimation_folder(folder_path: Path) -> bool:
    part0_path = folder_path / "part0"
    desc_path = folder_path / "desc.txt"
    
    has_part0 = part0_path.exists() and part0_path.is_dir()
    has_desc = desc_path.exists() and desc_path.is_file()
    
    return has_part0 and has_desc


# Find all bootanimation folders (bootanimation, bootanimation01, bootanimation02, etc.)
def find_bootanimation_folders(directory: Path) -> list[Path]:
    pattern = re.compile(r'^bootanimation(\d*)$', re.IGNORECASE)
    
    bootanimation_folders = []
    
    for item in directory.iterdir():
        if item.is_dir() and pattern.match(item.name):
            bootanimation_folders.append(item)
    
    # Sort folders: bootanimation first, then bootanimation01, bootanimation02, etc.
    def sort_key(path):
        match = pattern.match(path.name)
        if match and match.group(1):
            return (1, int(match.group(1)))
        return (0, 0)
    
    return sorted(bootanimation_folders, key=sort_key)


# Zip folder using store-only mode (no compression)
def zip_folder_store_only(folder_path: Path, output_zip: Path) -> bool:
    try:
        with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_STORED) as zf:
            for root, dirs, files in os.walk(folder_path):
                # Sort directories and files for consistent ordering
                dirs.sort()
                files.sort()
                
                for file in files:
                    file_path = Path(root) / file
                    # Calculate the archive name (relative path within the zip)
                    arcname = file_path.relative_to(folder_path)
                    zf.write(file_path, arcname)
        
        return True
    except Exception as e:
        print(f"  Error zipping {folder_path.name}: {e}")
        return False


# Process all bootanimation folders in a directory
def process_directory(directory: Path) -> tuple[int, int]:
    print(f"Searching for bootanimation folders in: {directory}")
    print("-" * 60)
    
    bootanimation_folders = find_bootanimation_folders(directory)
    
    if not bootanimation_folders:
        print("No bootanimation folders found.")
        return 0, 0
    
    print(f"Found {len(bootanimation_folders)} bootanimation folder(s):\n")
    
    successful = 0
    failed = 0
    
    for folder in bootanimation_folders:
        print(f"Processing: {folder.name}")
        
        # Validate the folder
        if not is_valid_bootanimation_folder(folder):
            part0_exists = (folder / "part0").exists()
            desc_exists = (folder / "desc.txt").exists()
            
            missing = []
            if not part0_exists:
                missing.append("part0/")
            if not desc_exists:
                missing.append("desc.txt")
            
            print(f"  ✗ Skipped - Missing required: {', '.join(missing)}")
            failed += 1
            continue
        
        # Create the output zip filename
        output_zip = folder.with_suffix('.zip')
        
        # Zip the folder
        if zip_folder_store_only(folder, output_zip):
            print(f"  ✓ Created: {output_zip.name}")
            successful += 1
        else:
            failed += 1
    
    return successful, failed


# Main entry point
def main():
    if len(sys.argv) < 2:
        print("Usage: python zip_bootanimation.py <path_to_directory>")
        print("\nThe directory should contain bootanimation folders to zip.")
        print("Each folder must have 'part0/' and 'desc.txt' to be processed.")
        sys.exit(1)
    
    directory = Path(sys.argv[1]).resolve()
    
    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"Error: Path is not a directory: {directory}")
        sys.exit(1)
    
    successful, failed = process_directory(directory)
    
    print("-" * 60)
    print(f"Done! Successful: {successful}, Skipped/Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
