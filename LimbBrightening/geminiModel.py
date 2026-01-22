import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def solar_brightness_temperature(x, y, R0=1):
    """
    Calculates the solar brightness temperature at 1420 MHz based on the derived model.
    """
    x_factor = 122/111#the ratio of 21cm x radius and visible light radius of the sun
    y_factor = 193/222 #the ratio of 21cm y radius and visible light radius of the sun
    
    theta = np.arctan(y/x)

    r = R0*np.sqrt((x_factor * y_factor)/(y_factor * np.cos(theta)**2 + x_factor * np.sin(theta)**2))

    rho = np.sqrt(x**2 + y**2) #converts x and y variable to radius
    
    with np.errstate(divide='ignore', invalid='ignore'):
        cos_theta = np.nan_to_num(x / rho)
        sin_theta = np.nan_to_num(y / rho)
        
    T = np.zeros_like(rho)
    T0 = 3600
    
    # --- Part 1 & 2: Disk and Lobes (rho <= R0) ---
    mask_disk = rho <= r
    T_disk = 10 * T0
    
    xn = x / r
    yn = y / r
    
    exponent1 = -((xn - 0.9)**2) / 0.01 - (yn**2) / 0.125
    exponent2 = -((xn + 0.9)**2) / 0.01 - (yn**2) / 0.125
    exponent3 = 0#-100*(xn*.1)**2 - 8*(1.5*yn)**2 #added as test band
    
    T_lobes = 25 * T0 * (np.exp(exponent1) + np.exp(exponent2))

    #T_spot = 20 * T0 * (np.exp(-(100 * (x - 0.35)**2 + 100 * (y - 0.35)**2)))

    T[mask_disk] = T_disk + T_lobes[mask_disk]# + T_spot[mask_disk]
    
    # --- Part 3: Corona (rho > R0) ---
    mask_corona = rho > r
    T_limb = (10 + 10 * cos_theta**2) * T0
    h_theta = 0.4 * r * cos_theta**2 + 0.2 * r * sin_theta**2
    decay = np.exp(-(rho - r) / h_theta)
    T_corona = T_limb * decay
    
    T[mask_corona] = T_corona[mask_corona]
    
    return T**4

# Create a grid
x = np.linspace(-2.5, 2.5, 1000)
y = np.linspace(-2.5, 2.5, 1000)
X, Y = np.meshgrid(x, y)

# Calculate Temperature (proportional to Intensity)
Intensity_Map = solar_brightness_temperature(X, Y)

# Plot as a grayscale image
fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off')

# Use a grayscale colormap where high values are white (bright)
plt.imshow(Intensity_Map, extent=[-2.5, 2.5, -2.5, 2.5], origin='lower', cmap='gray', vmin=0)

# Save as PNG first
png_filename = 'solar_radio_intensity_temp.png'
plt.savefig(png_filename)
plt.close(fig) # Close plot to free memory

# Convert PNG to BMP using PIL
img = Image.open(png_filename)
bmp_filename = 'solar_radio_intensity.bmp'
img.save(bmp_filename)

print(f"BMP image saved as: {bmp_filename}")