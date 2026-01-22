import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import ffmpeg
import datetime
import os
import pandas as pd
import csv

#Testing 
#t_0 = 1:56:50
#t_f = 1:57:10

eclipse_mp4 = "EclipseStreamAnalysis/2024 April 8, 4k Live Stream of the Solar Eclipse from the UCA Observatory [lrWkmZvI3JY].mp4"
start_time = "00:00:00"
totality_start_time = "01:57:26"
totality_end_time = "02:01:22"
end_time = "03:18:47"
crop_dimensions = '1300:1300:1300:500' #sets values for cropping, from left to right: Width of cropped video, height of cropped video, top left x coordinate of cropped video, top left y coordinate for cropped video

#setting up test storage for pixel count info inital date = 2460409.2186657293
SecondToJD = 1.1574e-5 #Conversion factor for seconds to julian date
t0 = 2460409.162013889#This is the real start date based on the time of the video #2460409.2036806
time = []#time in julian date of each pixel count
pixelcount = []#pixelcount of frame with mask

for i in range(3*60+18): #keep in mind what j value you choose, as you will have to modulate in responce. Can be seconds or minutes
    j = i*60 #change this value if you want to look at different time jumps. j = i is seconds, j = 60*i is minutes etc
    starttimeindex = str(datetime.timedelta(seconds = j))
    endtimeindex = str(datetime.timedelta(seconds = j+1))
    (
        ffmpeg.input(eclipse_mp4, ss=starttimeindex, to=endtimeindex)#the video we want to extract data from
        .filter('crop', *crop_dimensions.split(":"))#crops the video
        .filter('fps', fps=1, round='up')
        .output('PixelCount/FrameStore/countframe.png')# extracts frames and saves them as pngs
        .run()
    )
    
    filename = "PixelCount/FrameStore/countframe.png"
    img = cv.imread(filename, cv.IMREAD_GRAYSCALE) #reads the image file and converts to grayscale

    #The four thresholding items below are gaussian, mean, otsu, and global
    #thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 199, 5) #Adaptive gaussian threholding
    #thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 199, 5) #adaptive mean thresholding
    ret, thresh = cv.threshold(img, 0, 255, cv.THRESH_OTSU)#Otsu threholding
    #ret, thresh = cv.threshold(img, 127, 255, cv.THRESH_BINARY)#global threshold

    nonzero_pixel_count = np.sum(thresh > 0) #counts nonzero pixels of the thresholded image matrix
    pixelcount.append(nonzero_pixel_count) #adds the pixel count to a list to display as a graph
    time.append(t0 + (j)*SecondToJD) #counts the time
    os.remove('PixelCount/FrameStore/countframe.png')

with open('data/PixelCount.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows((pixelcount, time))

plt.plot(time, pixelcount, label = "Pixel Count")
plt.title("2024-04-08 Total Solar Eclipse, Conway, AR 1429.25 MHz")
plt.xlabel('JD Time')
plt.ylabel('# of Pixels')
plt.show()


