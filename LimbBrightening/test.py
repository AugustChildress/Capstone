import numpy as np
from PIL import Image

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Parameters
#-------------------------------------------------------------------------------------------------------------------------------------------------
x_factor = 122/111  # ratio of 21cm x radius / visible light radius
y_factor = 193/222  # ratio of 21cm y radius / visible light radius

h = 256
w = 128
x_center = 0
y_center = h / 2

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Radius, brightness models
#-------------------------------------------------------------------------------------------------------------------------------------------------
def Radius(theta):  # elliptical radius as a function of angle
    R0 = 80
    r = R0 * np.sqrt((x_factor * y_factor) /
                     (y_factor * np.cos(theta)**2 + x_factor * np.sin(theta)**2))
    return r

def disk(r):
    z = 1 / ((r**8 / 4) + (1/1.4))
    return z

def corona(r):
    z = (1 / (r**2 + 1)) + 0.04  # avoid divide-by-zero
    return z

def lobe(r, theta):
    z = (-(3 * r**3 * np.cos(theta) - 1.7 * r)**4) / (r**4 + 1e-6) \
        - ((2.4 * r**5 * np.sin(theta))**2)/(r**7 + 1e-6) + 3
    return z

def R(x, y):
    dx = x - x_center
    dy = y - y_center
    return np.sqrt(dx**2 + dy**2)

def Theta(x, y):
    dx = x - x_center
    dy = y - y_center
    return np.arctan2(dy, dx)

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Generate Image
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
            pixel = disk(r) + 0.3 * lobe(r / 80, theta)

        sun[y, x] = pixel

# Normalize to [0, 255]
sun -= sun.min()
sun /= sun.max()
sun *= 255

Image.fromarray(sun.astype(np.uint8)).save("sun.jpg")
