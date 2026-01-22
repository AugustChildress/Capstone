from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.time import Time
from matplotlib import dates
import numpy as np
import pandas as pd
import datetime
import scipy.signal
import csv


"""Pulling data from NEU, converting to central time, and skewing the data to match our timing"""
file_path = 'Capstone/NEUComparison/SolarEclipse2024/observation_log.xlsx' 
df = pd.read_excel(file_path) #use pandas to read excel sheet
NEU_data_raw = df.iloc[:, [2,7]] #only pull intensity and time
NEU_data_raw = NEU_data_raw.to_numpy().tolist() #convert dataframe to list 
NEU_data_raw = np.array(NEU_data_raw)#convert to array to properly index
time_raw = (NEU_data_raw[:,0]) # in utc
data_raw = (NEU_data_raw[:,1]) # in solar flux

def convertToJD(time): #converts from 2024-04-08T+HH:MM:SS:ss format to JD
    t = Time('2024-04-08 '+time, scale='utc')
    return t.jd

time_JD = []
for i in range(len(time_raw)):
    time_JD.append(convertToJD(time_raw[i]))

#Normalizing data
def normalization(lightcurve):
    high = 0
    for i in range(len(lightcurve)):
        if (lightcurve[i] >= high):
            high = lightcurve[i]

    n = high/100

    return lightcurve/n

"""Removing invalid data from NEU data"""
indexStart = 108
indexEnd = 115

#removes data points recommended by NEU
data_raw = data_raw.tolist()
for i in range(indexStart,indexEnd+1):
    data_raw[i] = None

data_raw = np.array(data_raw).astype(float)

def convertToJD(time): #converts from 2024-04-08T+HH:MM:SS:ss format to JD
    t = Time('2024-04-08 '+time, scale='utc')
    return t.jd

time_JD = []
for i in range(len(time_raw)):
    time_JD.append(convertToJD(time_raw[i]))


"""Calculating first contact time of NEU Data in JD"""
firstContact_EDT = '14:16:05' #Time of first contact in Boston, MA in EDT
firstContact_UTC = '18:16:05' #Time of first contact in Boston, MA in UTC
firstContactNEU = Time('2024-04-08 '+firstContact_UTC, scale='utc').jd

"""Calculating fourth contact time of NEU Data in JD"""
fourthContact_EDT = '16:39:10' #Time of fourth contact in Boston, MA in EDT
fourthContact_UTC = '20:39:10' #Time of fourth contact in Boston, MA in UTC
fourthContactNEU = Time('2024-04-08 '+fourthContact_UTC, scale='utc').jd

"""Code to calculate line of adjustment"""
#"""Finds index of a value in a list"""
def findIndex(list, value):
    epsilon = 1e-6 #Tolerance
    for i in range(len(list)):
        if (value - list[i]) < epsilon:
            index = i
            break
    return index

# finds index of first and fourth contact
index_pre = findIndex(time_JD, firstContactNEU - (time_JD[-1] - fourthContactNEU))
index_1st = findIndex(time_JD, firstContactNEU) #499
index_4th = findIndex(time_JD, fourthContactNEU) #1069
index_final = findIndex(time_JD, time_JD[-1]) 

#calculates average magnitude of the amount of time before 1st contact that is available post 4th contact
sum = 0
dif = index_1st - index_pre
for i in range(index_pre, index_1st):
    sum = sum + float(data_raw[i])
pre_average = sum/dif

#calculates average magnitude after 4th contact
sum = 0
dif = index_final - index_4th
for i in range(index_4th, index_final):
    sum = sum + float(data_raw[i])
post_average = sum/dif

#calculates how much the last values in the data need to be adjusted
adj_num = pre_average - post_average

#Creates the linear adjustment function
m = adj_num/(time_JD[-1]- time_JD[index_1st])
adjustment_function = []

#This part sets the part of the function from 0 to 1st contact to 0 as to not effect that first part with the adjustment function.
for i in range(0, index_1st):
    adjustment_function.append(0)

#This part is the adjustment function, which affects the data from 1st contact to the last point of data.
for i in range(index_1st, index_final+1):
    adjustment_function.append(m*(time_JD[i]- time_JD[index_1st]))

'''Writes adjusted data_raw_adjusted to csv file for later use'''
with open('Capstone/data/NEU_adjusted.csv', 'w', newline='') as file:
    # Create a csv.writer object
    writer = csv.writer(file)
    for item in (data_raw+adjustment_function):
        writer.writerow([item])

plt.vlines(firstContactNEU, 0, 1, colors='r')
plt.vlines(fourthContactNEU, 0, 1, colors='r')

plt.plot(time_JD, normalization(scipy.signal.savgol_filter(data_raw+adjustment_function, 51, 0)),label = 'Adjusted Normalized Smoothed')
plt.plot(time_JD, normalization(scipy.signal.savgol_filter(data_raw, 51, 0)), label = 'Unadjusted Normalized Smoothed')
plt.show()