import numpy as np
import scipy.special as sp
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw
import PIL.ImageOps    
#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Parameters"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
x_factor = 122/111#the ratio of 21cm x radius and visible light radius of the sun
y_factor = 193/222 #the ratio of 21cm y radius and visible light radius of the sun

solar_radius = 100 #radius of the sun in pixels ADJUST FOR ACTUAL PARAMETERS


#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Functions"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
def generateMoon(image, x, y, radius):
    copy = image.copy()
    draw = ImageDraw.Draw(copy)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(0, 0, 0))
    return copy

def Intensity(T):
    h = 6.626e-34 # Planck COnstant
    c = 300000000 # speed of light
    k = 1.38e-23 # Boltzmann constant
    l = 0.21 #wavelength of the light
    return ((2*h*c**2)/l**5)*(1/(np.e**((h*c)/(l*k*T))-1))

def pixelToIntensity(pixel, temp_scale):
    T = pixel * temp_scale
    I = Intensity(T)
    return I


img = Image.open('Screenshot 2025-10-27 at 12.27.57 PM.png').convert('L')
test_21cm = np.array(PIL.ImageOps.invert(img))

high = 0
for x in range(img.width):
    for y in range(img.height):
        if test_21cm[y][x] > high:
            high = test_21cm[y][x]

intensity = np.zeros((img.height,img.width), dtype=float)
for x in range(img.width):
    for y in range(img.height):
        intensity[y][x] = (pixelToIntensity(test_21cm, 30*3600/high))



solar_radius = 100

counts_raw = []

# Move the moon diagonally across the Sun
high = 0
for i in range(0, img.width, 5):  # step to make it faster
    eclipse = generateMoon(intensity, i, i, solar_radius)
    counts = np.asarray(eclipse).sum()  # total brightness
    if counts > high:
        high = counts
    counts_raw.append(counts)

counts = np.array(counts_raw)/high

# Create position array
positions = list(range(0, img.width, 5))

w, h = img.size

frames = []

# Move the moon across the Sun (left to right)
for i in range(-solar_radius, w + solar_radius, 5):
    frame = generateMoon(intensity, i, h // 2, solar_radius)
    frames.append(frame)

# Save as animated GIF
frames[0].save(
    'eclispe1.gif',
    save_all=True,
    append_images=frames[1:],
    duration=50,   # ms per frame
    loop=0         # 0 = infinite loop
)

# Plot brightness vs position
plt.figure(figsize=(8, 4))
plt.plot(positions, counts, color='orange')
plt.xlabel("Moon X-position (pixels)")
plt.ylabel("Total Brightness (sum of pixel values)")
plt.title("Simulated Eclipse Brightness Curve")
plt.grid(True)
plt.ylim(0, 1.1)
plt.show()
