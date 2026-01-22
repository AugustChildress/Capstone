import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Parameters"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
x_factor = 122/111  # 21cm x radius / visible light radius
y_factor = 193/222  # 21cm y radius / visible light radius

t1i, t2i, t3i = 30, 20, 10
h, w = 256, 256
solar_radius = 100  # radius of the sun in pixels

x_center = w // 2
y_center = h // 2

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Functions"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
def Radius(theta):
    r = np.sqrt((x_factor * y_factor) /
                (y_factor * np.cos(theta)**2 + x_factor * np.sin(theta)**2))
    return r * solar_radius

def disk(r):
    return 1 / ((r**8 / 4) + (1 / 1.4))

def corona(r):
    return (1 / (r**2 + 1e-3)) + 0.04  # add small epsilon for safety

def lobe(r, theta):
    z = (-(3 * r**5 * np.cos(theta) - 1.7 * r)**4) / (r**4 + 1e-3)
    z -= ((2.4 * r**5 * np.sin(theta))**2) / (r**7 + 1e-3)
    z += 3
    return z

def R(x, y):
    dx = x - x_center
    dy = y - y_center
    return np.sqrt(dx**2 + dy**2)

def Theta(x, y):
    return np.arctan2(y - y_center, x - x_center)

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Generate Image"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
sun = np.zeros((h, w), dtype=float)
pixel_scale = 255 / 3

for y in range(h):
    for x in range(w):
        theta = Theta(x, y)
        r_norm = R(x, y) / Radius(theta)

        if R(x, y) >= Radius(theta):
            pixel = corona(r_norm)
        else:
            pixel = 2 * disk(r_norm)

        if theta <= np.pi / 2:
            l_val = lobe(r_norm, theta)
            if pixel < l_val:
                pixel = l_val

        sun[y, x] = np.clip(pixel * pixel_scale, 0, 255)

img = Image.fromarray(sun.astype(np.uint8))
img.save("sun.jpg")

plt.imshow(img, cmap="inferno")
plt.axis("off")
plt.show()
