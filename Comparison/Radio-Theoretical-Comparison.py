from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from astropy.time import Time
from matplotlib import dates
import numpy as np
import pandas as pd
import csv
import scipy.signal
import datetime 


# Open Radio data from fits file
hdu1 = fits.open("data/20240408-171452_TPI-PROJ01-SUN_02#_01#.fits")
data = hdu1[1].data
t = Time(data['jd'], format='jd')

date = data['jd']
t = t.plot_date
r_pol = data['RIGHT_POL']

# Below we will assign index values to the times of the eclipse contacts

# These times were found with an online calculator using uca's posted eclipse times
contact1st = 2460409.231829
contact2nd = 2460409.285475
contact3rd = 2460409.288160
contact4th = 2460409.341400

#These times were found just using math and python lists
final = date[-1]
pre1st = contact1st - (final - contact4th)

# These are the indeces of each of the times above in the date[] list
index_pre = 0
index_1st = 0
index_2nd = 0
index_3rd = 0
index_4th = 0
index_final = 0
epsilon = 1e-6 #Tolerance

# Finds pre1st contact index
for i in range(len(date)):
    if (pre1st - date[i]) < epsilon:
        index_pre = i
        #print("found pre1st index", index_pre)
        break

# Finds 1st contact index
for i in range(len(date)):
    if (contact1st - date[i]) < epsilon:
        index_1st = i
        #print("found 1st index", index_1st)
        break

# Finds 2nd contact index
for i in range(len(date)):
    if (contact2nd - date[i]) < epsilon:
        index_2nd = i
        #print("found 2nd index", index_2nd)
        break

# Finds 3rd contact index
for i in range(len(date)):
    if (contact3rd - date[i]) < epsilon:
        index_3rd = i
        #print("found 3rd index", index_3rd)
        break

# Finds 4th contact index
for i in range(len(date)):
    if (contact4th - date[i]) < epsilon:
        index_4th = i
        #print("found 4th index", index_4th)
        break

# Finds final data index
for i in range(len(date)):
    if (final - date[i]) < epsilon:
        index_final = i
        #print("found final index", index_final)
        break

# Code to calculate line of adjustment
# Calculates average magnitude before 1st contact
sum = 0
dif = index_1st - index_pre
for i in range(index_pre, index_1st):
    sum = sum + r_pol[i]
pre_average = sum/dif
#print(pre_average)

# Calculates average magnitude after 4th contact
sum = 0
dif = index_final - index_4th
for i in range(index_4th, index_final):
    sum = sum + r_pol[i]
post_average = sum/dif
#print(post_average)

# Calculates how much the last values in the data need to be adjusted
adj_num = pre_average - post_average

# Creates the linear adjustment function
m = adj_num/(date[-1]- date[index_1st])
adjustment_function = []

# This part sets the part of the function from 0 to 1st contact to 0 as to not effect that first part with the adjustment function.
for i in range(0, index_1st):
    adjustment_function.append(0)

# This part is the adjustment function, which affects the data from 1st contact to the last point of data.
for i in range(index_1st, index_final+1):
    adjustment_function.append(m*(date[i]- date[index_1st]))

# Making Visual Data counts into percentage
def read_lines():
    with open('data/PixelCount.csv', 'r') as data:
        reader = csv.reader(data)
        for row in reader:
            yield [ float(i) for i in row ]

# Time and count lists
xy = list(read_lines())
count = xy[0][:]
time = xy[1][:]

def read_lines2():
    with open('Time Test/timeframe test/clockjd.csv', 'r') as data:
        reader = csv.reader(data)
        for row in reader:
            yield [ float(i) for i in row ]
x = list(read_lines2())
clocktime = x[0][:]

cti1 = 0
cti2 = 0
cti3 = 0
cti4 = 0
error1 = 1
error2 = 1

for i in range(len(count)):
    if(count[i] == 91537):#cuts out the no signal section
        count[i] = None
    if(abs(contact2nd - clocktime[i]) <= error1):
        error1 = abs(clocktime[i] - contact2nd)
        cti1 =i
    if(abs(clocktime[i] - contact3rd) <= error2):
        error2 = abs(clocktime[i] - contact3rd)
        cti2 = i
for i in range(cti1, cti2):
    count[i] = None
for i in range(1):
    count[i] = None


# Normalizing and smoothing Radio Data
r_pol_filter = scipy.signal.savgol_filter(r_pol + adjustment_function, 51, 0) #smoothed radio data

def normalization(lightcurve):
    high = 0
    for i in range(len(lightcurve)):
        if (lightcurve[i] >= high):
            high = lightcurve[i]

    n = high/100

    return lightcurve/n

# Adding theoretical data

# Convert UTC to Julian Date
str2date = lambda x: pd.Timestamp(datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime.fromisoformat(x)), datetime.timezone.utc)).to_julian_date()

rsun_1 = np.genfromtxt("EclipseModels/tse_radius_1.csv", delimiter="," , converters = {0: str2date}, encoding = "utf-8")
rsun_1p20 = np.genfromtxt("EclipseModels/tse_radius_1.2.csv", delimiter="," , converters = {0: str2date}, encoding = "utf-8")
rsun_1p27 = np.genfromtxt("EclipseModels/tse_radius_1.27.csv", delimiter="," , converters = {0: str2date}, encoding = "utf-8")
rsun_1p45 = np.genfromtxt("EclipseModels/tse_radius_1.45.csv", delimiter="," , converters = {0: str2date}, encoding = "utf-8")


# Begin the graph and set line width
plt.figure(figsize=(15, 5)) 
plt.style.use('tableau-colorblind10') 
widthline = 3

# Design
titlesize = 30
labelsize = 15
ticksize = 12
legendsize = 15

# Smoothed and Normalized Radio Data
plt.plot(date - 2.460409e6, normalization(r_pol_filter), label = "Smoothed/Normalized Radio Data", linewidth=widthline)

# Theoretical Plots
plt.plot(rsun_1[:,0] - 2.460409e6, 100*rsun_1[:,1], label = "R/Rsun = 1", linewidth=widthline)
plt.plot(rsun_1p20[:,0] - 2.460409e6, 100*rsun_1p20[:,1], label = "R/Rsun = 1.2", linewidth=widthline)
plt.plot(rsun_1p27[:,0] - 2.460409e6, 100*rsun_1p27[:,1], label = "R/Rsun = 1.27", linewidth=widthline)
plt.plot(rsun_1p45[:,0] - 2.460409e6, 100*rsun_1p45[:,1], label = "R/Rsun = 1.45", linewidth=widthline)


plt.axvline(x = date[index_1st] - 2.460409e6, color = 'r', linestyle = '-') #1st contact
plt.axvline(x = date[index_2nd] - 2.460409e6, color = 'r', linestyle = '-') #2nd contact
plt.axvline(x = date[index_3rd] - 2.460409e6, color = 'r', linestyle = '-') #3rd contact
plt.axvline(x = date[index_4th] - 2.460409e6, color = 'r', linestyle = '-') #4th contact

#plt.title("Radio vs Theoretical Curves", fontsize = titlesize)
plt.xlabel('Julian Date - 2460409', fontsize = labelsize)
plt.ylabel('Relative Brightness', fontsize = labelsize)
plt.ticklabel_format(useOffset=False)
plt.xticks(fontsize = ticksize)
plt.yticks(fontsize = ticksize)
plt.ylim(-5,120)
#plt.xlim(2460409.16  - 2.460409e6,2460409.39 - 2.460409e6)
plt.xlim(0.2,0.35)
plt.legend(fontsize = legendsize, loc='lower left')
plt.tight_layout()
plt.savefig("RadioVsTheoretical.pdf")
plt.show()
