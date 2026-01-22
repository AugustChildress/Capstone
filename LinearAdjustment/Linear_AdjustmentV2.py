from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.time import Time
from matplotlib import dates
import numpy as np
import csv

"""Data from the fits file"""
hdu1 = fits.open("Capstone/data/20240408-171452_TPI-PROJ01-SUN_02#_01#.fits")
data = hdu1[1].data
t = Time(data['jd'], format='jd')
date = data['jd']
t = t.plot_date
r_pol = data['RIGHT_POL']
#len date 9935
"""code used to find the indexes of the 1-4 contact"""
list = [1,2,3,4,5,6,7,8,9,10]

#These times were found with an online calculator using uca's posted eclipse times
contact1st = 2460409.231829
contact2nd = 2460409.285475
contact3rd = 2460409.288160
contact4th = 2460409.341400

#These times were found just using math and python lists
final = date[-1]
pre1st = contact1st - (final - contact4th)

#these are the indexes of each of the times above in the date[] list
index_pre = 0
index_1st = 0
index_2nd = 0
index_3rd = 0
index_4th = 0
index_final = 0
epsilon = 1e-6 #Tolerance

#"""Finds pre1st contact index"""
for i in range(len(date)):
    if (pre1st - date[i]) < epsilon:
        index_pre = i
        print("found pre1st index", index_pre)
        break

#"""Finds 1st contact index"""
for i in range(len(date)):
    if (contact1st - date[i]) < epsilon:
        index_1st = i
        print("found 1st index", index_1st)
        break

#"""Finds 2nd contact index"""
for i in range(len(date)):
    if (contact2nd - date[i]) < epsilon:
        index_2nd = i
        print("found 2nd index", index_2nd)
        break

#"""Finds 3rd contact index"""
for i in range(len(date)):
    if (contact3rd - date[i]) < epsilon:
        index_3rd = i
        print("found 3rd index", index_3rd)
        break

#"""Finds 4th contact index"""
for i in range(len(date)):
    if (contact4th - date[i]) < epsilon:
        index_4th = i
        print("found 4th index", index_4th)
        break

#"""Finds final data index"""
for i in range(len(date)):
    if (final - date[i]) < epsilon:
        index_final = i
        print("found final index", index_final)
        break

"""Code to calculate line of adjustment"""
#calculates average magnitude of the amount of time before 1st contact that is available post 4th contact
sum = 0
dif = index_1st - index_pre
for i in range(index_pre, index_1st):
    sum = sum + r_pol[i]
pre_average = sum/dif
print(pre_average)

#calculates average magnitude after 4th contact
sum = 0
dif = index_final - index_4th
for i in range(index_4th, index_final):
    sum = sum + r_pol[i]
post_average = sum/dif
print(post_average)

#calculates how much the last values in the data need to be adjusted
adj_num = pre_average - post_average

#Creates the linear adjustment function
m = adj_num/(date[-1]- date[index_1st])
adjustment_function = []

#This part sets the part of the function from 0 to 1st contact to 0 as to not effect that first part with the adjustment function.
for i in range(0, index_1st):
    adjustment_function.append(0)

#This part is the adjustment function, which affects the data from 1st contact to the last point of data.
for i in range(index_1st, index_final+1):
    adjustment_function.append(m*(date[i]- date[index_1st]))

r_pol_adjusted = np.array(r_pol)+adjustment_function
r_pol_adjusted = r_pol_adjusted.tolist()

'''Writes adjusted r_pol to csv file for later use'''
with open('Capstone/data/r_pol_adjusted.csv', 'w', newline='') as file:
    # Create a csv.writer object
    writer = csv.writer(file)
    for item in r_pol_adjusted:
        writer.writerow([item])

"""Graphs Data"""
plt.plot(date, r_pol, label = "Raw Data")#not adjusted Graph
plt.plot(date, r_pol + adjustment_function, label = "Skew Adjusted Data")#adjusted Graph
plt.plot(date, adjustment_function, label = "Linear Adjustment Function")#Linear adjustment
plt.axvline(x = date[index_1st], color = 'r', linestyle = '-') #1st contact
plt.axvline(x = date[index_2nd], color = 'r', linestyle = '-') #2nd contact
plt.axvline(x = date[index_3rd], color = 'r', linestyle = '-') #3rd contact
plt.axvline(x = date[index_4th], color = 'r', linestyle = '-') #4th contact

plt.legend()
plt.savefig("linear_adjustment.png")
plt.show()