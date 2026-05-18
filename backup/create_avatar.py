#!/usr/bin/env python
"""Generate a default avatar PNG"""
try:
    from PIL import Image, ImageDraw
    
    # Create a new image with a gradient background
    img = Image.new('RGB', (52, 52), color='#10b981')  # Emerald color
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circle/avatar placeholder
    # This is a solid emerald square, but you can customize
    img.save('static/img/default-avatar.png')
    print("✓ Default avatar created at static/img/default-avatar.png")
except ImportError:
    # If PIL is not available, create a minimal PNG using raw bytes
    # This is a 1x1 transparent PNG as fallback
    import base64
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAADQAAAA0CAYAAADFeBvrAAAACklEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    )
    with open('static/img/default-avatar.png', 'wb') as f:
        f.write(png_data)
    print("✓ Fallback avatar created")
