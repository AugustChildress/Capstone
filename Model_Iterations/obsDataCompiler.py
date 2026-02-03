from astropy.io import fits
from matplotlib.pylab import normal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from astropy.time import Time
from matplotlib import dates
import numpy as np
import pandas as pd
import csv
import scipy.signal
import datetime 
#from sqlalchemy import null

# -----------------------------------------------------------------------------------------------------------------------------------------------
# UCA DATA
# -----------------------------------------------------------------------------------------------------------------------------------------------

"""Data from the fits file"""
hdu1 = fits.open("data/20240408-171452_TPI-PROJ01-SUN_02#_01#.fits")
data = hdu1[1].data
t = Time(data['jd'], format='jd')
date = data['jd']
t = t.plot_date
r_pol = data['RIGHT_POL']

contact1st = 2460409.231829
contact2nd = 2460409.285475
contact3rd = 2460409.288160
contact4th = 2460409.341400

'''Normalizing and smoothing Radio Data'''
r_pol_adjusted = []
with open("data/r_pol_adjusted.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        r_pol_adjusted.append(float(row[0]))  # take first column

r_pol_adjusted = np.array(r_pol_adjusted)

def normalization(lightcurve):
    high = 0
    for i in range(len(lightcurve)):
        if (lightcurve[i] >= high):
            high = lightcurve[i]

    n = high/100

    return lightcurve/n

r_pol_adj_smooth = scipy.signal.savgol_filter(r_pol_adjusted, 51, 0)
r_pol_adj_smooth_norm = normalization(r_pol_adj_smooth)













# -----------------------------------------------------------------------------------------------------------------------------------------------
# NEU DATA
# -----------------------------------------------------------------------------------------------------------------------------------------------

"""NEU Data"""
"""Pulling data from NEU, converting to central time, and skewing the data to match our timing"""
file_path = 'NEUComparison/SolarEclipse2024/observation_log.xlsx' 
df = pd.read_excel(file_path) #use pandas to read excel sheet
NEU_data_raw = df.iloc[:, [2,7]] #only pull intensity and time
NEU_data_raw = NEU_data_raw.to_numpy().tolist() #convert dataframe to list 
NEU_data_raw = np.array(NEU_data_raw)#convert to array to properly index
time_raw = np.array(NEU_data_raw[:,0]) # in utc
data_raw = np.array(NEU_data_raw[:,1]) # in solar flux

"""Removing invalid data from NEU data"""
indexStart = 108
indexEnd = 115

#removes data points recommended by NEU
data_raw = data_raw.tolist()
for i in range(indexStart,indexEnd+1):
    data_raw[i] = None

data_raw = np.array(data_raw)

'''Converts time to JD'''
def convertToJD(time): #converts from 2024-04-08T+HH:MM:SS:ss format to JD
    t = Time('2024-04-08 '+time, scale='utc')
    return t.jd

time_JD = []
time_stretch = []
for i in range(len(time_raw)):
    time_JD.append(convertToJD(time_raw[i]))
    time_stretch.append(convertToJD(time_raw[i]))



"""Calculating first contact time of NEU Data in JD"""
firstContact_EDT = '14:16:05' #Time of first contact in Boston, MA in EDT
firstContact_UTC = '18:16:05' #Time of first contact in Boston, MA in UTC
firstContactNEU = Time('2024-04-08 '+firstContact_UTC, scale='utc').jd

"""Calculating fourth contact time of NEU Data in JD"""
fourthContact_EDT = '16:39:10' #Time of fourth contact in Boston, MA in EDT
fourthContact_UTC = '20:39:10' #Time of fourth contact in Boston, MA in UTC
fourthContactNEU = Time('2024-04-08 '+fourthContact_UTC, scale='utc').jd


"""Pulling adjusted NEU Data from csv file"""
data_adj = []
with open("data/NEU_adjusted.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        data_adj.append(float(row[0]))  # take first column

data_adj = np.array(data_adj)




"""Stretching NEU data to match UCA contact points"""
# add 15 minutes evenly throught the NEU data between 1st and 4th contact
time_difference = 15/(60*24) #minutes in JD

#"""Finds index of a value in a list"""
def findIndex(list, value):
    epsilon = 1e-6 #Tolerance
    for i in range(len(list)):
        if (value - list[i]) < epsilon:
            index = i
            break
    return index

# finds index of first and fourth contact
index_1st = findIndex(time_JD, firstContactNEU) #499
index_4th = findIndex(time_JD, fourthContactNEU) #1069

index_final = 1230

num_points = len(time_JD[index_1st:index_4th])
stretch_factor = time_difference/num_points


for i in range(index_1st, index_4th+1):
    time_stretch[i] = time_stretch[i]+stretch_factor*(i+1-index_1st)


for i in range(index_4th+1, index_final+1):
    time_stretch[i] = time_stretch[i]+time_difference 

time_stretch[index_4th:-1] = (np.array(time_stretch[index_4th:-1])+time_difference).tolist()

"""Shifting NEU data to match first contact times with UCA in JD"""
firstContactUCA = 2460409.231829

NEU_1cShift = firstContactNEU - firstContactUCA


# -----------------------------------------------------------------------------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------------------------------------------------------------------------
widthline = 3
dateadjust = 2460409

'''Radio Telescope Plots'''

#Smoothed/Normalized UCA
#plt.plot(np.array(date) - dateadjust, r_pol_adj_smooth_norm, label = "UCA", linewidth=widthline)#RADIO Smoothed/Normalization
plt.plot(np.array(date) - dateadjust, normalization(scipy.signal.savgol_filter(r_pol_adjusted, 51, 0)), label = "UCA", linewidth=widthline)

#smoothed/normalized NEU Stretch
plt.plot(np.array(time_stretch)- NEU_1cShift  - dateadjust, normalization(scipy.signal.savgol_filter(data_adj, 51, 0)), label = "NEU Adj Stretch", linewidth=widthline)
#plt.plot(np.array(time_stretch) - NEU_1cShift - dateadjust, normalization(scipy.signal.savgol_filter(data_adj, 51, 0)), label = "NEU Stretch", linewidth=widthline)

#plt.axvline(x = 2460409.260365-dateadjust, color = 'black', linestyle = '-', label = "Activity: 18:14:56 UTC, Lasts 8:44") #1st contact UCA
plt.axvline(x = 2460409.2363-dateadjust, color = 'black', linestyle = '-') #1st bright spot
plt.axvline(x = 2460409.2572-dateadjust, color = 'black', linestyle = '-') #2st bright spot
plt.axvline(x = 2460409.2777-dateadjust, color = 'black', linestyle = '-') #3st bright spot
plt.axvline(x = 2460409.2960-dateadjust, color = 'yellow', linestyle = '-') #4st bright spot
plt.axvline(x = 2460409.3145-dateadjust, color = 'yellow', linestyle = '-') #5st bright spot
plt.axvline(x = 2460409.3310-dateadjust, color = 'yellow', linestyle = '-') #6st bright spot


plt.axvline(x = contact1st-dateadjust, color = 'r', linestyle = '-') #1st contact UCA
#plt.axvline(x = firstContactNEU-dateadjust, color = 'black', linestyle = '-') #1st contact NEU
#plt.axvline(x = fourthContactNEU-dateadjust, color = 'black', linestyle = '-') #4th contact NEU

#plt.axvline(x = contact2nd-dateadjust, color = 'r', linestyle = '-') #2nd contact
#plt.axvline(x = contact3rd-dateadjust, color = 'r', linestyle = '-') #3rd contact
plt.axvline(x = contact4th-dateadjust, color = 'r', linestyle = '-') #4th contact

#Design
titlesize = 35
labelsize = 15
ticksize = 10
legendsize = 10

plt.title("UCA vs NEU", fontsize = titlesize)
plt.xlabel('Julian Date - 2460409', fontsize = labelsize)
plt.ylabel('Relative Brightness', fontsize = labelsize)
plt.xticks(fontsize = ticksize)
plt.yticks(fontsize = ticksize)
#plt.ticklabel_format(useOffset = "false")


plt.ylim(-5,120)
#plt.xlim(2460409.16-dateadjust,2460409.39-dateadjust)#For optical lightsensor only
plt.xlim(0.215,0.35)#For Radio only
#plt.xlim(0.20,0.35)#For livestream only

plt.legend(fontsize = legendsize, loc='lower left')
plt.tight_layout()
plt.savefig("LightcurveComparison.png")
plt.show()

'''

# -----------------------------------------------------------------------------------------------------------------------------------------------
# Output to other functions
# -----------------------------------------------------------------------------------------------------------------------------------------------
UCA_DATA = normalization(scipy.signal.savgol_filter(r_pol_adjusted, 51, 0))
UCA_TIME = np.array(date) - dateadjust
UCA_FIRSTCONTACT = 2460409.260365-dateadjust
'''
