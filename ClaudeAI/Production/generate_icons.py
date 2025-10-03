#!/usr/bin/env python3
"""Generate PWA icons from favicon or create simple branded icons"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_branded_icon(size, output_path, maskable=False):
    """Create a simple branded icon with gradient background"""
    # Create image with gradient-like background
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)

    # Add gradient effect (simple linear gradient simulation)
    for y in range(size):
        # Blend from #667eea to #764ba2
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        color = (r, g, b)
        draw.line([(0, y), (size, y)], fill=color)

    # Add "Z" letter in the center
    if maskable:
        # For maskable icons, keep content in safe zone (80% of canvas)
        safe_zone = int(size * 0.8)
        margin = (size - safe_zone) // 2
        text_size = int(safe_zone * 0.6)
    else:
        text_size = int(size * 0.6)
        margin = int(size * 0.2)

    # Draw large "Z" in white
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", text_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text size and center it
    text = "Z"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]

    # Draw white "Z"
    draw.text((x, y), text, fill='white', font=font)

    # Save
    img.save(output_path, 'PNG')
    print(f"Created {output_path}")

def convert_favicon_if_exists(favicon_path, size, output_path):
    """Convert existing favicon to PNG icon"""
    try:
        img = Image.open(favicon_path)
        img = img.convert('RGB')
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        img.save(output_path, 'PNG')
        print(f"Converted favicon to {output_path}")
        return True
    except Exception as e:
        print(f"Could not convert favicon: {e}")
        return False

# Main execution
base_dir = '/Users/dansidanutz/Desktop/ZmartBot/ClaudeAI/Production'
icons_dir = os.path.join(base_dir, 'icons')
favicon_path = os.path.join(base_dir, 'favicon.ico')

# Ensure icons directory exists
os.makedirs(icons_dir, exist_ok=True)

# Try to convert favicon first, otherwise create branded icons
sizes = [192, 512]
for size in sizes:
    standard_path = os.path.join(icons_dir, f'icon-{size}.png')
    maskable_path = os.path.join(icons_dir, f'icon-{size}-maskable.png')

    # Try favicon conversion first
    if os.path.exists(favicon_path):
        if not convert_favicon_if_exists(favicon_path, size, standard_path):
            create_branded_icon(size, standard_path, maskable=False)
    else:
        create_branded_icon(size, standard_path, maskable=False)

    # Always create maskable version with safe zone
    create_branded_icon(size, maskable_path, maskable=True)

print("\n✅ All icons generated successfully!")
print(f"Icons location: {icons_dir}")
