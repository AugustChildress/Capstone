import numpy as np
import sys
import os
# Get the directory of the current script
current_dir = os.path.dirname(os.path.realpath("NEUComparison/NEUComparison.py"))
# Add the directory containing the module to sys.path
sys.path.append(current_dir)

import scipy.special as sp
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw
import NEUComparison
from statistics import mean


#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Parameters"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
x_factor = 122/111#the ratio of 21cm x radius and visible light radius of the sun
y_factor = 193/222 #the ratio of 21cm y radius and visible light radius of the sun

solar_radius = 160 #radius of the sun in pixels ADJUST FOR ACTUAL PARAMETERS

gemini_intensity = Image.open('gemini_radio_intensity.png').convert('RGB')
gemini_temp = Image.open('gemini_radio_temp.png').convert('RGB')
band = Image.open('gemini_band.png').convert('RGB')
stretch = Image.open('gemini_stretch.png').convert('RGB')
dot = Image.open('gemini_dot.png').convert('RGB')


w, h = gemini_intensity.size
step = 1


#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Functions"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
def generateMoon(image, x, y, radius):
    copy = image.copy()
    draw = ImageDraw.Draw(copy)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(0, 0, 0))
    return copy

def Normalize(array):
    return array/max(array)

def ContactFinder(x, y):
    '''calculate radial distance between moon and sun, shouts when first and fourth contact occurs.
        x, y: coordinates for the center of the moon
    '''
    center = h/2 #center of sun

    #unit vector for moon center to sun center (can be reversed for sun to moon)
    mag = np.sqrt((center-x)**2+(center-y)**2)
    uv_x = (center-x)/mag
    uv_y = (center-y)/mag

    #calculate closest part of moon to sun coordinates
    moon_x = solar_radius*uv_x+x
    moon_y = solar_radius*uv_y+y

    #calculate closest part of moon to sun coordinates
    sun_x = solar_radius*(-uv_x)+center
    sun_y = solar_radius*(-uv_y)+center

    
    if abs(sun_x-moon_x)<= 1:
        print("Contact!: x = ", x, "  y = ",y)
        return True

def Eclipse(image):
    counts_raw = []
    path = []
    count_index = 0
    contact = []
    for i in range(0, max(w, h), step): 
        eclipse = generateMoon(image, i, i, solar_radius)
        counts = np.asarray(eclipse).sum()  # total brightness
        counts_raw.append(counts)
        path.append(i)
        if ContactFinder(i,i):
            if count_index == 0:
                contact.append(i)
                count_index += 1
            else:
                contact.append(i)

    return counts_raw, path, contact

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Main"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
#Eclipsing various models of the sun
counts_gemini_intensity, path, contact = Eclipse(gemini_intensity)
counts_gemini_temp, _, _ = Eclipse(gemini_temp)
counts_band, _, _ = Eclipse(band)
counts_stretch, _, _ = Eclipse(stretch)
counts_dot, _, _ = Eclipse(dot)



counts_gemini_intensity = Normalize(counts_gemini_intensity)
counts_gemini_temp = Normalize(counts_gemini_temp)
counts_band = Normalize(counts_band)
counts_stretch= Normalize(counts_stretch)
counts_dot= Normalize(counts_dot)

'''
#Editing UCA data to fit on graph
def Shrink(input_data,input_time, target_length):
    # Now I want to reduce all the lists to exactly 1000 elements
    # I tried this approched like I read in some other questions:
    indeces = np.array(range(len(input_data))) ## make indeces
    remove = np.random.permutation(len(input_data))[:target_length] ## select indeces to remove
    selected = np.isin(indeces, remove, assume_unique=True) ## make list of indeces that are selected, faster on unique 
    output_data = input_data[selected] # len(aa) = 1000 ## select indeces
    output_time = input_time[selected] # len(aa) = 1000 ## select indeces


    return output_data, output_time

uca_data_shrink, uca_time_shrink = Shrink(NEUComparison.UCA_DATA, NEUComparison.UCA_TIME, len(path))

print("Length Shrink UCA: ",len(uca_data_shrink), "     Length Path: ", len(path))
'''


# Plot brightness vs position
plt.figure(figsize=(8, 4))
plt.plot(path, counts_gemini_intensity, label = 'Intensity')
#plt.plot(path, counts_gemini_temp, label = 'gemini temp')
#plt.plot(path, counts_band, label = 'band')
#plt.plot(path, counts_stretch, label = 'stretch')
plt.plot(path, counts_dot, label = 'Sunspot')
plt.axvline(x = contact[0], color = 'r', linestyle = '-')#1st contact
plt.axvline(x = contact[2], color = 'r', linestyle = '-')#fourth contact

plt.axvline(x = 200, color = 'black', linestyle = '-') #1st bright spot
plt.axvline(x = 296, color = 'black', linestyle = '-') #2st bright spot
plt.axvline(x = 375, color = 'black', linestyle = '-') #3st bright spot
plt.axvline(x = 425, color = 'yellow', linestyle = '-') #4st bright spot
plt.axvline(x = 504, color = 'yellow', linestyle = '-') #5st bright spot
plt.axvline(x = 600, color = 'yellow', linestyle = '-') #6st bright spot


plt.xlabel("Moon X-position (pixels)")
plt.ylabel("Total Brightness (Normalized sum of pixel values)")
plt.title("Simulated Eclipse Brightness Lightcurve")
plt.legend()
plt.grid(True)
plt.ylim(0, 1.1)
plt.savefig("theoreticalComparison.png")
plt.show()

