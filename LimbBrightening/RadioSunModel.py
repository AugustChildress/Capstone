import numpy as np
import scipy.special as sp
import matplotlib.pyplot as plt
from PIL import Image

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Parameters"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
x_factor = 122/111#the ratio of 21cm x radius and visible light radius of the sun
y_factor = 193/222 #the ratio of 21cm y radius and visible light radius of the sun

t1i = 30
t2i = 20
t3i = 10

h = 500
w = 500
x_center = 0
y_center = 0

solar_radius = 160 #radius of the sun in pixels ADJUST FOR ACTUAL PARAMETERS


#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Functions"""
#-------------------------------------------------------------------------------------------------------------------------------------------------

'''
def Radius(x,y): #radius in terms of x and y coordinates
    r = (x**2)/x_factor + (y**2)/y_factor
    return r
'''
def Radius(theta): #radius in terms of theta
    r = np.sqrt((x_factor * y_factor)/(y_factor * np.cos(theta)**2 + x_factor * np.sin(theta)**2))
    return r * solar_radius

def disk(r):
    z = 1/((r**20 / 4) + (1/1.4))
    return z

def corona(r):
    z = (1/r**5) + 0.04
    return z

def lobe(r, theta):
    #z = (-(3 * r**5 * np.cos(theta) - 1.2 * r)**4) / (r**4) - ((2.4 * r**5 * np.sin(theta))**2)/(r**7) + 3\
    z = (-(5 * r**7 * np.cos(theta) - 1.13 * r)**4) / (r**4) - ((2 * r**5 * np.sin(theta))**2)/(r**7) + 3

    return z

def R(x,y):
    dx = x - x_center
    dy = y - y_center
    r = np.sqrt(dx**2 + dy**2)
    return r

def Theta(x,y):
    if y == 0:
        theta = 0
    elif x == 0:
        theta = 90*np.pi/180
    else:
        theta = np.arctan(y/x)
    return theta

def Intensity(T):
    '''
    h = 6.626e-34 # Planck COnstant
    c = 300000000 # speed of light
    k = 1.38e-23 # Boltzmann constant
    l = 0.21 #wavelength of the light
    I = ((2*h*c**2)/l**5)*(1/(np.e**((h*c)/(l*k*T))-1))
    '''
    a = 5.67e-8 #Stefan-Boltzmann constant
    e = 1 #emissivity of the object (sun) is very close to a blackbody radiator, so we can say e = 1
    I = e*a*T**4

    return I

def Normalize(array):
    return array/max(array)

#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Setting up Image"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
sun = np.zeros((h,w), dtype=float)

def radioModel(x,y):

    theta = Theta(x,y)
    r = R(x,y)/Radius(theta)

    #Corona
    if R(x,y) >= Radius(theta):
        pixel = corona(r)
    #Disk
    else:
        pixel = disk(r)
    
    if theta <= np.pi/2 and r > 0.3:
        if pixel < lobe(r, theta):
            pixel = lobe(r, theta)

    #print("Pixel: ",pixel)

    T = pixel*36000 #Converting the pixel values into degrees k
    I = Intensity(T)

    return I

sun = []
high = 0
for y in range(0, h):
    row = []
    for x in range(0, w):
        if radioModel(x,y)> high:
            high = radioModel(x,y)
        row.append(radioModel(x,y))
    sun.append(row)

sun = np.array(sun)
sun = sun*255/high #converts the intensity into pixel values

sun_q4 = Image.fromarray(sun.astype(np.uint8))
#-------------------------------------------------------------------------------------------------------------------------------------------------
"""Building Final Image"""
#-------------------------------------------------------------------------------------------------------------------------------------------------
# Mirror horizontally (left to right)
sun_q3 = sun_q4.transpose(Image.FLIP_LEFT_RIGHT)

# Mirror vertically (top to bottom)
sun_q1 = sun_q4.transpose(Image.FLIP_TOP_BOTTOM)

# Both
sun_q2 = sun_q3.transpose(Image.FLIP_TOP_BOTTOM)

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

get_concat_v(get_concat_h(sun_q2, sun_q1), get_concat_h(sun_q3, sun_q4)).save('sun21cm.bmp')



