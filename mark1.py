import sys
import RPi.GPIO as GPIO
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as IMG
import math

from time import sleep
from matplotlib.image import imread
from matplotlib.pyplot import figure, show, axes, sci
from picamera import PiCamera
sys.path.insert(0, "/home/pi/Desktop/mlx90640-library/python/build/lib.linux-armv7l-2.7")

import MLX90640 as X

def move_Row_angle(angle):
    pwm_row.ChangeDutyCycle(angle)
    print "row:",(angle - 2.5) / 0.0278
    sleep(1)
    pwm_row.ChangeDutyCycle(0)
    sleep(1)

def move_Col_angle(angle):
    print "col:",(angle - 2.5) / 0.0278
    pwm_col.ChangeDutyCycle(angle)
    sleep(1)
    pwm_col.ChangeDutyCycle(0)
    sleep(1)

def getLength_withFOV(degree, distance):
    print "DEGREE"
    Degree = degree
    Degree_Radians = math.radians(Degree)
    Degree_Tan = math.tan(Degree_Radians)

    print "tan =", Degree_Tan
    print "distance =", Distance

    length_Full = Degree_Tan * Distance

    print "full :",length_Full
    print("")
    return length_Full

def getDegree_perAngle(length_Full, length_pixel):
    Degree_pixel = length_Full / length_pixel
    print "Degree_Pixel :", Degree_pixel
    return Degree_pixel

def getAngle_withLength(move_distance, distance):
    get_shoting_angle = math.degrees(math.atan(move_distance/distance))
    print "move_Degree :",get_shoting_angle,"degree" 
    return get_shoting_angle

def getLength_withAngle(move_angle, distance):
    angle = math.radians(move_angle)
    get_shoting_length = math.tan(angle) * distance
    get_shoting_length = get_shoting_length * 2.0
    print "move_distance :",get_shoting_length,"cm"
    return get_shoting_length


def take_Temperature():

    global X

    X.setup(16)
    f = X.get_frame()
    X.cleanup()

    v_min = min(f)
    v_max = max(f)

    for x in range(24):
        row = []
        for y in range(32):
            val = f[32 * (23-x) + y]
            row.append(val)
   
        cu[x] = row

    return cu[x]

def Motor():

    global Row_Pixel, Col_Pixel, row_sw, col_sw, set_row_angle, set_col_angle, nrow, ncol,one_degree,cu,tw,stop_angle,row_degree
    print "-----------------------------------------------"

    move_Row_angle(set_row_angle)
    move_Col_angle(set_col_angle)

    width_angle_1 = set_row_angle
    length_angle_1 = set_col_angle

    width_angle = set_row_angle
    length_angle = set_col_angle

    k = 1

    for z in range(0, (nrow * ncol)):

        for i in range(0, nrow):

            for j in range(0, ncol):
                print "------------------------------------------"
                width_angle = width_angle + (tw * one_degree) 
                move_Row_angle(width_angle)

                width_angle = width_angle - ((tw - (Row_Pixel/nrow)) * one_degree)
                move_Row_angle(width_angle)

                take_Temperature()
                sleep(1)
                
                globals()["dp_{}".format(k)] = np.array(cu)
                cu = np.zeros((row_array, col_array))

                k = k + 1

            if i < ncol-1:
                length_angle = length_angle + (tw * one_degree) 
                move_Col_angle(length_angle)
                
                length_angle = length_angle - ((tw - (Col_Pixel/ncol)) * one_degree)
                move_Col_angle(length_angle)

                width_angle = width_angle_1 + (tw * one_degree) 
                move_Row_angle(width_angle)

                width_angle = width_angle - (tw * one_degree)
                move_Row_angle(width_angle)

            else:
                length_angle = length_angle_1 + (tw * one_degree) 
                move_Col_angle(length_angle)
                
                length_angle = length_angle - (tw * one_degree)
                move_Col_angle(length_angle)
                

        if z == 0:  
            width_angle = width_angle_1 - (row_degree * one_degree )
            move_Row_angle(width_angle)

            width_angle_1 = width_angle

        elif z == 1:
            length_angle = length_angle_1 + ((col_degree * 3.9/3)* one_degree )
            move_Col_angle(length_angle)

            length_angle_1 = length_angle

        else:
            width_angle = width_angle_1 + (row_degree * one_degree )
            move_Row_angle(width_angle)

            width_angle_1 = width_angle
                
    return dp_1, dp_2, dp_3, dp_4, dp_5, dp_6, dp_7, dp_8, dp_9, dp_10, dp_11, dp_12, dp_13, dp_14, dp_15, dp_16

def Sum_Image():
    
    global ncol_array, nrow_array, ncol_array_double, nrow_array_double, ncol_array_fourth, nrow_array_fourth
    
    dp_1, dp_2, dp_3, dp_4, dp_5, dp_6, dp_7, dp_8, dp_9, dp_10, dp_11, dp_12, dp_13, dp_14, dp_15, dp_16 = Motor()
    
    for i in range(row_array_double):
            
        if i == 0:
                
            for k in range(col_array_double):
                    
                if k == 0: 
                    mt_1[i][k] = dp_1[i][k]
                elif k == col_array_double-1:
                    mt_1[i][k] = dp_2[i][col_array-1]
                else:
                    mt_1[i][k] = (dp_1[i][k/2] + dp_2[i][(k-1)/2]) / 2.0
                                        
        elif i == row_array_double-1:
                    
            for m in range(col_array_double):
                                    
                if m == 0:
                    mt_1[i][m] = dp_3[i/2][m]
                elif m == col_array_double-1:
                    mt_1[i][m] = dp_4[i/2][col_array-1]
                else:
                    mt_1[i][m] = (dp_3[i/2][m/2] + dp_4[i/2][(m-1)/2]) / 2.0

        else:
            
            for n in range(col_array_double):
                
                if n == 0:
                    mt_1[i][n] = (dp_1[i/2][n] + dp_3[(i-1)/2][n]) / 2.0
                elif n == col_array_double-1 :
                    mt_1[i][n] = (dp_2[i/2][col_array-1] + dp_4[(i-1)/2][col_array-1]) / 2.0
                else:
                    mt_1[i][n] = (dp_1[i/2][n/2] + dp_2[i/2][(n-1)/2] + dp_3[(i-1)/2][n/2] + dp_4[(i-1)/2][(n-1)/2]) / 4.0

    for x in range(row_array_double):
            
        if x == 0:
                
            for k in range(col_array_double):
                    
                if k == 0: 
                    mt_2[x][k] = dp_5[x][k]
                elif k == col_array_double-1:
                    mt_2[x][k] = dp_6[x][col_array-1]
                else:
                    mt_2[x][k] = (dp_5[x][k/2] + dp_6[x][(k-1)/2]) / 2.0
                                        
        elif x == row_array_double-1:
                    
            for m in range(col_array_double):
                                    
                if m == 0:
                    mt_2[x][m] = dp_7[x/2][m]
                elif m == col_array_double-1:
                    mt_2[x][m] = dp_8[x/2][col_array-1]
                else:
                    mt_2[x][m] = (dp_7[x/2][m/2] + dp_8[x/2][(m-1)/2]) / 2.0


        else:
            
            for n in range(col_array_double):
                
                if n == 0:
                    mt_2[x][n] = (dp_5[x/2][n] + dp_7[(x-1)/2][n]) / 2.0
                elif n == col_array_double-1 :
                    mt_2[x][n] = (dp_6[x/2][col_array-1] + dp_8[(x-1)/2][col_array-1]) / 2.0
                else:
                    mt_2[x][n] = (dp_5[x/2][n/2] + dp_6[x/2][(n-1)/2] + dp_7[(x-1)/2][n/2] + dp_8[(x-1)/2][(n-1)/2]) / 4.0

    for u in range(row_array_double):
            
        if u == 0:
                
            for k in range(col_array_double):
                    
                if k == 0: 
                    mt_3[u][k] = dp_9[u][k]
                elif k == col_array_double-1:
                    mt_3[u][k] = dp_10[u][col_array-1]
                else:
                    mt_3[u][k] = (dp_9[u][k/2] + dp_10[u][(k-1)/2]) / 2.0
                                        
        elif u == row_array_double-1:
                    
            for m in range(col_array_double):
                                    
                if m == 0:
                    mt_3[u][m] = dp_11[u/2][m]
                elif m == col_array_double-1:
                    mt_3[u][m] = dp_12[u/2][col_array-1]
                else:
                    mt_3[u][m] = (dp_11[u/2][m/2] + dp_12[u/2][(m-1)/2]) / 2.0

        else:
            
            for n in range(col_array_double):
                
                if n == 0:
                    mt_3[u][n] = (dp_9[u/2][n] + dp_11[(u-1)/2][n]) / 2.0
                elif n == col_array_double-1 :
                    mt_3[u][n] = (dp_10[u/2][col_array-1] + dp_12[(u-1)/2][col_array-1]) / 2.0
                else:
                    mt_3[u][n] = (dp_9[u/2][n/2] + dp_10[u/2][(n-1)/2] + dp_11[(u-1)/2][n/2] + dp_12[(u-1)/2][(n-1)/2]) / 4.0

    for b in range(row_array_double):
            
        if b == 0:
                
            for k in range(col_array_double):
                    
                if k == 0: 
                    mt_4[b][k] = dp_13[b][k]
                elif k == col_array_double-1:
                    mt_4[b][k] = dp_14[b][col_array-1]
                else:
                    mt_4[b][k] = (dp_13[b][k/2] + dp_14[b][(k-1)/2]) / 2.0
                                        
        elif b == row_array_double-1:
                    
            for m in range(col_array_double):
                                    
                if m == 0:
                    mt_4[b][m] = dp_15[b/2][m]
                elif m == col_array_double-1:
                    mt_4[b][m] = dp_16[b/2][col_array-1]
                else:
                    mt_4[b][m] = (dp_15[b/2][m/2] + dp_16[b/2][(m-1)/2]) / 2.0

        else:
            
            for n in range(col_array_double):
                
                if n == 0:
                    mt_4[b][n] = (dp_13[b/2][n] + dp_15[(b-1)/2][n]) / 2.0
                elif n == col_array_double-1 :
                    mt_4[b][n] = (dp_14[b/2][col_array-1] + dp_16[(b-1)/2][col_array-1]) / 2.0
                else:
                    mt_4[b][n] = (dp_13[b/2][n/2] + dp_14[b/2][(n-1)/2] + dp_15[(b-1)/2][n/2] + dp_16[(b-1)/2][(n-1)/2]) / 4.0

    for z in range(row_array_fourth):

        if z <= row_array_double-1:

            for d in range(col_array_fourth):
                if d <= col_array_double-1:
                    mt[z][d] = mt_1[z][d]
                elif d == col_array_double:
                    mt[z][d] = (mt_1[z][col_array_double-1] + mt_2[z][0]) / 2.0
                else:
                    mt[z][d] = mt_2[z][(d-65)]

        elif z == row_array_double:

            for e in range(col_array_fourth):
                if e <= col_array_double-1:
                    mt[z][e] = (mt_1[z-1][e] + mt_4[0][e]) / 2.0
                elif e == col_array_double:
                    mt[z][e] = (mt_1[z-1][col_array_double-1] + mt_4[z-1][col_array_double-1] + mt_2[0][0] + mt_3[0][0]) / 4.0
                else:
                    mt[z][e] = (mt_2[z-1][(e-65)] + mt_3[0][(e-65)]) /2.0

        else:
            for f in range(col_array_fourth):
                if f <= col_array_double-1:
                    mt[z][f] = mt_4[(z-49)][f]
                elif f == col_array_double:
                    mt[z][f] = (mt_4[(z-49)][col_array_double-1] + mt_3[(z-49)][0]) / 2.0
                else:
                    mt[z][f] = mt_3[(z-49)][(f-65)]
    
    return mt, mt_1, mt_2, mt_3, mt_4

def Image_View():
    
    global ncol_array_dp, ncol_array_dp, ncol_array_mt
 
    mt, mt_1, mt_2, mt_3, mt_4 = Sum_Image()

    plt.figure()
                        
    plt.subplot(2, 3, 1)
    plt.imshow(mt_1,cmap='jet',vmin=0.00, vmax=30.00)

    plt.subplot(2, 3, 2)         
    plt.imshow(mt_2,cmap='jet',vmin=0.00, vmax=30.00)

    plt.subplot(2, 3, 3)
    plt.imshow(mt,cmap='jet',vmin=0.00, vmax=30.00)

    plt.subplot(2, 3, 4)         
    plt.imshow(mt_4,cmap='jet',vmin=0.00, vmax=30.00)

    plt.subplot(2, 3, 5)         
    plt.imshow(mt_3,cmap='jet',vmin=0.00, vmax=30.00)

    plt.show()

    mt_1 = np.zeros((row_array_double, col_array_double))
    mt_2 = np.zeros((row_array_double, col_array_double))
    mt_3 = np.zeros((row_array_double, col_array_double))
    mt_4 = np.zeros((row_array_double, col_array_double))
    mt = np.zeros((row_array_fourth,col_array_fourth))

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    pwm_row = GPIO.PWM(11, 50) # 50Hz
    pwm_col = GPIO.PWM(13, 50) # 50Hz
    pwm_row.start(0)
    pwm_col.start(0)
    
    one_degree = 0.0278
    
    set_row_angle = 180 * 0.0278 + 2.5
    set_col_angle = 162.5 * 0.0278 + 2.5

    nrow = 2
    ncol = 2

    row_array = 24
    col_array = 32

    row_array_double = row_array * nrow
    col_array_double = col_array * ncol

    row_array_fourth = row_array_double * nrow
    col_array_fourth = col_array_double * ncol

    tw = 20.0
    row_sw = tw 
    col_sw = tw 

    mt_1 = np.zeros((row_array_double, col_array_double))
    mt_2 = np.zeros((row_array_double, col_array_double))
    mt_3 = np.zeros((row_array_double, col_array_double))
    mt_4 = np.zeros((row_array_double, col_array_double))
    
    mt = np.zeros((row_array_fourth, col_array_fourth))
    cu = np.zeros((row_array, col_array))

    while True:
        
        row_degree = input("enter row the degree : ")
        col_degree = input("enter col the degree : ")
        row_pixel = input("enter row_pixel : ")
        col_pixel = input("enter col_pixel : ")
        Distance = input("enter the distance : ")

        Row_length_full = getLength_withFOV(row_degree, Distance)
        Col_length_full = getLength_withFOV(col_degree, Distance)

        #Row_angle = getAngle_withLength(Row_length_full, Distance)
        #Col_angle = getAngle_withLength(Col_length_full, Distance)

        Row_Pixel = getDegree_perAngle(Row_length_full,row_pixel)
        Col_Pixel = getDegree_perAngle(Col_length_full,col_pixel)
        
        #Row_Pixel = getDegree_perAngle(getAngle_withLength(Row_length_full, Distance),row_pixel)
        #Col_Pixel = getDegree_perAngle(getAngle_withLength(Col_length_full, Distance),col_pixel)
        
        print ""

        Image_View()
            
except KeyboardInterrupt:
    move_Row_angle(90)
    move_Col_angle(90)
    pwm_row.stop()
    pwm_col.stop()
    GPIO.cleanup()
