import numpy as np
from PIL import Image

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Parameters
#-------------------------------------------------------------------------------------------------------------------------------------------------
x_factor = 122/111  # 21cm x-radius / visible radius
y_factor = 193/222  # 21cm y-radius / visible radius

h = 256
w = 128
x_center = w / 2     # center horizontally
y_center = h / 2     # center vertically
solar_radius = 100   # in pixels

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------------------------------------------------------------------------
def Radius(theta):
    """Elliptical solar radius as a function of angle."""
    r = np.sqrt((x_factor * y_factor) /
                (y_factor * np.cos(theta)**2 + x_factor * np.sin(theta)**2))
    return r * solar_radius

def disk(r):
    """Disk brightness (inner region)."""
    return 1 / ((r**8 / 4) + (1/1.4))

def corona(r):
    """Corona brightness (outer region)."""
    return (1 / (r**2 + 1e-6)) + 0.04

def lobe(r, theta):
    """Optional surface structure for more realism."""
    z = (-(3 * r**3 * np.cos(theta) - 1.7 * r)**4) / (r**4 + 1e-6) \
        - ((2.4 * r**5 * np.sin(theta))**2)/(r**7 + 1e-6) + 3
    return z

def R(x, y):
    """Radial distance from center."""
    return np.sqrt((x - x_center)**2 + (y - y_center)**2)

def Theta(x, y):
    """Polar angle."""
    return np.arctan2(y - y_center, x - x_center)

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Image generation
#-------------------------------------------------------------------------------------------------------------------------------------------------
sun = np.zeros((h, w), dtype=float)

for x in range(w):
    for y in range(h):
        r = R(x, y)
        theta = Theta(x, y)
        R_edge = Radius(theta)

        if r >= R_edge:
            pixel = corona(r)
        else:
            pixel = disk(r) + 0.3 * lobe(r / solar_radius, theta)

        sun[y, x] = pixel

# Normalize to 0–255
sun -= sun.min()
sun /= sun.max()
sun *= 255

# Save image
Image.fromarray(sun.astype(np.uint8)).save("sun.jpg")
print("✅ Image saved as sun.jpg")
