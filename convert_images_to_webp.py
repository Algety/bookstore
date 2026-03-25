#!/usr/bin/env python
"""
Convert PNG images to WebP format for better performance.
Reduces file size by 60-80% while maintaining quality.
"""

import os
from pathlib import Path
from PIL import Image

# Define paths
IMAGES_DIR = Path(__file__).parent / "static" / "images"
BACKUP_DIR = IMAGES_DIR / "backup_png"

def convert_png_to_webp(quality=85, keep_originals=True):
    """
    Convert all PNG files in static/images to WebP format.
    
    Args:
        quality: WebP quality (1-100). 85 is recommended (looks identical to PNG)
        keep_originals: If True, backup original PNG files
    """
    
    if not IMAGES_DIR.exists():
        print(f"Error: Images directory not found at {IMAGES_DIR}")
        return
    
    # Create backup directory if keeping originals
    if keep_originals:
        BACKUP_DIR.mkdir(exist_ok=True)
        print(f"📁 Backup directory: {BACKUP_DIR}\n")
    
    # Find all PNG files
    png_files = list(IMAGES_DIR.glob("*.png"))
    
    if not png_files:
        print("No PNG files found in static/images/")
        return
    
    print(f"Found {len(png_files)} PNG files to convert:\n")
    print("-" * 80)
    print(f"{'Filename':<40} {'Original':<15} {'WebP':<15} {'Savings'}")
    print("-" * 80)
    
    total_original = 0
    total_webp = 0
    
    for png_file in png_files:
        try:
            # Skip if already processed
            webp_file = png_file.with_suffix(".webp")
            if webp_file.exists():
                print(f"⏭️  {png_file.name:<36} (already WebP)")
                continue
            
            # Open and convert image
            img = Image.open(png_file)
            
            # Convert RGBA to RGB if necessary (WebP handles both, but PNG->RGB is smaller)
            if img.mode in ("RGBA", "LA", "P"):
                # Keep RGBA if it has transparency
                if img.mode == "P":
                    img = img.convert("RGBA")
            
            # Save as WebP
            img.save(webp_file, "WEBP", quality=quality, method=6)
            
            # Get file sizes
            original_size = png_file.stat().st_size
            webp_size = webp_file.stat().st_size
            savings = original_size - webp_size
            savings_pct = (savings / original_size) * 100
            
            total_original += original_size
            total_webp += webp_size
            
            # Format sizes for display
            orig_kb = f"{original_size / 1024:.1f} KiB"
            webp_kb = f"{webp_size / 1024:.1f} KiB"
            savings_str = f"{savings / 1024:.1f} KiB ({savings_pct:.1f}%)"
            
            print(f"✅ {png_file.name:<36} {orig_kb:<15} {webp_kb:<15} {savings_str}")
            
            # Backup original if requested
            if keep_originals:
                import shutil
                backup_file = BACKUP_DIR / png_file.name
                shutil.copy2(png_file, backup_file)
        
        except Exception as e:
            print(f"❌ {png_file.name:<36} Error: {str(e)}")
    
    # Print summary
    print("-" * 80)
    if total_original > 0:
        total_savings = total_original - total_webp
        total_savings_pct = (total_savings / total_original) * 100
        print(f"\n📊 SUMMARY:")
        print(f"   Total Original Size: {total_original / 1024 / 1024:.2f} MiB")
        print(f"   Total WebP Size:     {total_webp / 1024 / 1024:.2f} MiB")
        print(f"   Total Savings:       {total_savings / 1024:.1f} KiB ({total_savings_pct:.1f}%)")
        print(f"   Quality Setting:     {quality}/100")
        
        if keep_originals:
            print(f"\n💾 Original PNG files backed up to: {BACKUP_DIR}")
            print("   You can safely delete this folder once you verify WebP looks good.")
    
    print("\n✨ Conversion complete!")
    print("\n📝 Next steps:")
    print("   1. Test your website to ensure images look good")
    print("   2. Update templates to use .webp files (or keep PNG as fallback)")
    print("   3. Delete PNG files once verified")
    print("   4. Run: git add . && git commit && git push heroku main")

if __name__ == "__main__":
    print("🖼️  PNG to WebP Converter\n")
    print(f"Images directory: {IMAGES_DIR}\n")
    
    # Run conversion with quality=85 (best balance)
    convert_png_to_webp(quality=85, keep_originals=True)
