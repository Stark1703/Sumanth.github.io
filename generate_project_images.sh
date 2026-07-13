#!/bin/bash
# Script to generate project thumbnail images using Python
# This creates placeholder images for each project

python3 << 'EOF'
import os
from PIL import Image, ImageDraw, ImageFont
import random

# Create images directory if it doesn't exist
os.makedirs('images', exist_ok=True)

# Define project images
projects = {
    'etl_pipeline.png': {
        'title': 'ETL Pipeline',
        'subtitle': 'Apache Airflow',
        'color': (52, 152, 219),  # Blue
        'icon': '⚙️'
    },
    'warehouse.png': {
        'title': 'Cloud Data',
        'subtitle': 'Warehouse',
        'color': (155, 89, 182),  # Purple
        'icon': '☁️'
    },
    'quality.png': {
        'title': 'Data Quality',
        'subtitle': 'Framework',
        'color': (46, 204, 113),  # Green
        'icon': '✓'
    },
    'sql_optimization.png': {
        'title': 'SQL',
        'subtitle': 'Optimization',
        'color': (230, 126, 34),  # Orange
        'icon': '⚡'
    },
    'ml_model.png': {
        'title': 'Predictive',
        'subtitle': 'Analytics ML',
        'color': (231, 76, 60),  # Red
        'icon': '🤖'
    },
    'dashboard.png': {
        'title': 'Real-Time',
        'subtitle': 'Dashboard',
        'color': (52, 73, 94),  # Dark Blue
        'icon': '📊'
    }
}

# Generate images
for filename, config in projects.items():
    # Create image
    img = Image.new('RGB', (400, 300), color=config['color'])
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        icon_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        icon_font = ImageFont.load_default()
    
    # Draw background gradient effect (darker at bottom)
    for i in range(300):
        opacity = int(255 * (1 - i / 300) * 0.2)
        draw.line([(0, i), (400, i)], fill=tuple(max(0, c - opacity) for c in config['color']))
    
    # Draw icon
    icon_bbox = draw.textbbox((0, 0), config['icon'], font=icon_font)
    icon_width = icon_bbox[2] - icon_bbox[0]
    icon_x = (400 - icon_width) // 2
    draw.text((icon_x, 30), config['icon'], font=icon_font, fill=(255, 255, 255))
    
    # Draw title
    title_bbox = draw.textbbox((0, 0), config['title'], font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (400 - title_width) // 2
    draw.text((title_x, 140), config['title'], font=title_font, fill=(255, 255, 255))
    
    # Draw subtitle
    subtitle_bbox = draw.textbbox((0, 0), config['subtitle'], font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (400 - subtitle_width) // 2
    draw.text((subtitle_x, 205), config['subtitle'], font=subtitle_font, fill=(255, 255, 255, 200))
    
    # Save image
    img.save(f'images/{filename}')
    print(f'✓ Created {filename}')

print('\n✅ All project images created successfully!')

EOF
