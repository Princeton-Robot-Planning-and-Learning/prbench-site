#!/usr/bin/env python3
"""
Script to optimize all GIF files in the project using gifsicle.
This reduces file sizes while maintaining visual quality.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    return filepath.stat().st_size

def optimize_gif(filepath: Path, optimization_level: int = 3) -> Tuple[bool, int, int]:
    """
    Optimize a single GIF file using gifsicle.
    
    Args:
        filepath: Path to the GIF file
        optimization_level: Optimization level (1-3, where 3 is most aggressive)
    
    Returns:
        Tuple of (success, original_size, new_size)
    """
    original_size = get_file_size(filepath)
    temp_file = filepath.with_suffix('.gif.tmp')
    
    try:
        # Run gifsicle with optimization
        # -O3: Maximum optimization level
        # --colors 256: Keep full color palette (default)
        # --lossy: Use lossy optimization for even smaller files (optional)
        cmd = [
            'gifsicle',
            f'-O{optimization_level}',
            '--batch',
            str(filepath)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"  ⚠️  Warning: gifsicle failed for {filepath}")
            print(f"      Error: {result.stderr}")
            return False, original_size, original_size
        
        new_size = get_file_size(filepath)
        return True, original_size, new_size
        
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout optimizing {filepath}")
        return False, original_size, original_size
    except Exception as e:
        print(f"  ⚠️  Error optimizing {filepath}: {e}")
        return False, original_size, original_size

def find_all_gifs(root_dir: Path) -> List[Path]:
    """Find all GIF files in the directory tree."""
    return list(root_dir.glob('**/*.gif'))

def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    """Main function to optimize all GIFs in the project."""
    project_root = Path(__file__).parent
    
    print("🔍 Finding all GIF files...")
    gif_files = find_all_gifs(project_root)
    
    if not gif_files:
        print("No GIF files found!")
        return
    
    print(f"📊 Found {len(gif_files)} GIF files")
    print("🚀 Starting optimization...\n")
    
    total_original = 0
    total_optimized = 0
    successful = 0
    failed = 0
    
    for i, gif_path in enumerate(gif_files, 1):
        rel_path = gif_path.relative_to(project_root)
        print(f"[{i}/{len(gif_files)}] Optimizing: {rel_path}")
        
        success, orig_size, new_size = optimize_gif(gif_path)
        
        if success:
            successful += 1
            total_original += orig_size
            total_optimized += new_size
            
            if new_size < orig_size:
                savings = orig_size - new_size
                percent = (savings / orig_size) * 100
                print(f"  ✓ {format_size(orig_size)} → {format_size(new_size)} "
                      f"(saved {format_size(savings)}, {percent:.1f}%)")
            else:
                print(f"  ✓ Already optimized ({format_size(orig_size)})")
        else:
            failed += 1
        
        print()
    
    # Print summary
    print("=" * 70)
    print("📈 OPTIMIZATION SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(gif_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nOriginal total size: {format_size(total_original)}")
    print(f"Optimized total size: {format_size(total_optimized)}")
    
    if total_original > 0:
        total_savings = total_original - total_optimized
        percent_savings = (total_savings / total_original) * 100
        print(f"Total space saved: {format_size(total_savings)} ({percent_savings:.1f}%)")
    
    print("=" * 70)
    print("✨ Optimization complete!")

if __name__ == "__main__":
    main()

