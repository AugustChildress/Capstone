import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Parameters"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
solar_radius = 160
step = 5  # how far the moon moves each frame (smaller = smoother animation)
output_gif = "eclipse.gif"

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Functions"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
def generateMoon(image, x, y, radius):
    """Draw a black circle (the moon) over the image and return it."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(0, 0, 0))
    return img_copy

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Main"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
sun_21cm = Image.open('Code_Generated_Image.png').convert('RGB')
w, h = sun_21cm.size

generateMoon(sun_21cm,h/2, h/2, solar_radius).save("testImage.png")
'''
frames = []
# Move the moon across the Sun (left to right)
for i in range(0, max(w, h), step):
    x = i
    y = i
    frame = generateMoon(sun_21cm, x, y, solar_radius)
    frames.append(frame)
# Save as animated GIF
frames[0].save(
    output_gif,
    save_all=True,
    append_images=frames[1:],
    duration=50,   # ms per frame
    loop=0         # 0 = infinite loop
)

'''

print(f"✅ Eclipse animation saved as {output_gif}")
