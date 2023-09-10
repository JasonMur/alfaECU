#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import math
import serial
from tkinter import *
from tkinter.font import Font
import tkinter.filedialog
import tkinter.messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.animation import FuncAnimation
from itertools import count
from statistics import mean


# In[ ]:


# Global Variables
try:
    ser = serial.Serial(
        port="COM3", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
    )
    nullValue=ser.readline()
except:
    print("Error opening Serial port!")

len1,len2 = 0.85,0.3 #Dimensions of the needle, relative to the canvas ray.
minFuelPress,maxFuelPress, stepFuelPress = 0,10,2 
minRpm,maxRpm,stepRpm = 0,8000,1000
minTemp,maxTemp,stepTemp = 100,300,50
minOilPress,maxOilPress,stepOilPress = 0,120,20
minBatt,maxBatt,stepBatt = 8,16,2
minAdvance, maxAdvance,stepAdvance = 0,45,10
minDwell,maxDwell,stepDwell = 0,60,10

root = Tk()
meter_font = Font(family="Tahoma",size=12,weight='normal')

plt.style.use('fivethirtyeight')
# values for first graph
x = []
y = []
# values for second graph
y2 = []

index = count()
index2 = count()


# In[ ]:


def setTitles(): 
    root.title('Alfa Romeo Spider')
    root.iconbitmap(r'C:/Users/c-jas/workbook/jupyter/Car/Capture.jpg')
    
    fuelPress.itemconfig(fuelPress.title,text='Fuel Pressure')
    fuelPress.itemconfig(fuelPress.unit,text='PSI')
    
    rpm.itemconfig(rpm.title,text='RPM')
    rpm.itemconfig(rpm.unit,text='RPM')
    
    temp.itemconfig(temp.title,text='Engine Temp')
    temp.itemconfig(temp.unit,text='C')
    
    oilPress.itemconfig(oilPress.title,text='Oil Pressure')
    oilPress.itemconfig(oilPress.unit,text='PSI')
    
    batt.itemconfig(batt.title,text='Battery Voltage')
    batt.itemconfig(batt.unit,text='Volts')
    
    advance.itemconfig(advance.title,text='Advance Angle')
    advance.itemconfig(advance.unit,text='Degrees')
    
    dwell.itemconfig(dwell.title,text='Dwell Angle')
    dwell.itemconfig(dwell.unit,text='Degrees')


# In[ ]:


class Meter(Canvas):

    def draw(self,vmin,vmax,step,title,unit,width, height):
        self.vmin = vmin
        self.vmax = vmax
        x0 = width/2
        y0 = width/2
        ray = int(0.7*width/2)
        self.title = self.create_text(width/2,12,fill="#000",
            font=meter_font)#Window title.
        self.create_oval(x0-ray*1.1,y0-ray*1.1,x0+ray*1.1,y0+ray*1.1,
            fill="blue")#The gray outer ring.
        self.create_oval(x0-ray,y0-ray,x0+ray,y0+ray,fill="#000")#The dial.
        coef = 0.1
        self.create_oval(x0-ray*coef,y0-ray*coef,x0+ray*coef,y0+ray*coef,
            fill="white")#This is the connection point blob of the needle.

        #This loop fills in the values at each step or gradation of the dial.
        for i in range(1+int((vmax-vmin)/step)):
            v = vmin + step*i
            angle = (5+6*((v-vmin)/(vmax-vmin)))*math.pi/4
            self.create_line(x0+ray*math.sin(angle)*0.9,
                y0 - ray*math.cos(angle)*0.9,
                x0+ray*math.sin(angle)*0.98,
                y0 - ray*math.cos(angle)*0.98,fill="#FFF",width=2)
            self.create_text(x0+ray*math.sin(angle)*0.75,
                y0 - ray*math.cos(angle)*0.75,
                text=v,fill="#FFF",font=meter_font)
            if i==int(vmax-vmin)/step:
                continue
            for dv in range(1,5):
                angle = (5+6*((v+dv*(step/5)-vmin)/(vmax-vmin)))*math.pi/4
                self.create_line(x0+ray*math.sin(angle)*0.94,
                    y0 - ray*math.cos(angle)*0.94,
                    x0+ray*math.sin(angle)*0.98,
                    y0 - ray*math.cos(angle)*0.98,fill="#FFF")
        self.unit = self.create_text(width/2,y0+0.8*ray,fill="#FFF",
            font=meter_font)
        self.needle = self.create_line(x0-ray*math.sin(5*math.pi/4)*len2,
            y0+ray*math.cos(5*math.pi/4)*len2,
            x0+ray*math.sin(5*math.pi/4)*len1,
            y0-ray*math.cos(5*math.pi/4)*len1,
            width=2,fill="#FFF")
        lb1=Label(self, compound='right', textvariable=v)

    #Draws the needle based on the speed or input value.
    def draw_needle(self,v,width):        
        x0=width/2
        y0=width/2
        ray = int(0.7*width/2) 
        #print(v) #Not required, but helps in debugging.
        v = max(v,self.vmin)#If input is less than 0 then the pointer stays at 0
        v = min(v,self.vmax)#If input is greater than the greatest value then the pointer stays at the maximum value.
        angle = (5+6*((v-self.vmin)/(self.vmax-self.vmin)))*math.pi/4
        self.coords(self.needle,x0-ray*math.sin(angle)*len2,
            y0+ray*math.cos(angle)*len2,
            x0+ray*math.sin(angle)*len1,
            y0-ray*math.cos(angle)*len1)


# In[ ]:


def animate(i):
    # Generate values
    x_vals.append(next(index))
    y_vals.append(random.randint(0, 5))
    y_vals2.append(random.randint(0, 5))
    # Get all axes of figure
    ax1, ax2 = plt.gcf().get_axes()
    # Clear current data
    ax1.cla()
    ax2.cla()
    # Plot new data
    ax1.plot(x_vals, y_vals)
    ax2.plot(x_vals, y_vals2)


# In[ ]:


#Create meters.

meters = Frame(root,width=2400,height=1200,bg="grey94")
meters.grid(row=0,column=0, sticky="n")
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)


fuelPress = Meter(meters,width=200,height=200)
fuelPress.draw(minFuelPress,maxFuelPress,stepFuelPress,"Fuel Pressure","PSI",200,200)
fuelPress.grid(column=0, row=0)

oilPress= Meter(meters,width=200,height=200)
oilPress.draw(minOilPress,maxOilPress,stepOilPress,"Oil Pressure","x1000",200,200)
oilPress.grid(column=1, row=0)

temp = Meter(meters,width=200,height=200)
temp.draw(minTemp,maxTemp,stepTemp,"Temperature","x1000",200,200)
temp.grid(column=2, row=0)

batt= Meter(meters,width=200,height=200)
batt.draw(minBatt,maxBatt,stepBatt,"Battery Volts","x1000",200,200)
batt.grid(column=3, row=0)

advance= Meter(meters,width=200,height=200)
advance.draw(minAdvance,maxAdvance,stepAdvance,"Advance","x1000",200,200)
advance.grid(column=0, row=1)

dwell= Meter(meters,width=200,height=200)
dwell.draw(minDwell,maxDwell,stepDwell,"Dwell","x1000",200,200)
dwell.grid(column=0, row=2)

rpm = Meter(meters,width=400,height=400)
rpm.draw(minRpm,maxRpm,stepRpm,"RPM","x1000",400,400)
rpm.grid(column=1, row=1, sticky = "w", columnspan=2, rowspan=2)


#image = PhotoImage(file="C:/Users/c-jas/workbook/jupyter/Car/alfaIcon.png")
#small_img = image.subsample(4,4)

#img = Label(root, image=small_img)
#img.grid(row=0, column=0, rowspan=1, padx=5, pady=5, sticky='nw')

x = [500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000]
y = [0,5,9,13,16,19,21,23,25,27,28,29,30,30,30,30]

fig, ax = plt.subplots(figsize=(5.4, 4.8))
canvas = FigureCanvasTkAgg(fig, master=meters)

canvas.get_tk_widget().grid(row=1, column=3, columnspan=2, rowspan=2)
plt.title("Advance Curve")
plt.xlabel("RPM")
plt.ylabel("Advance Angle")
plt.tight_layout()
# Set the range of x-axis
plt.xlim(0, 8000)
# Set the range of y-axis
plt.ylim(0, 40)
#ax.scatter(x,y)

line1, = ax.plot(x, y, linestyle = 'dashed', color='green', linewidth=0.5)
#plt.plot(x,y, linestyle = 'dotted')
plt.xticks(x, rotation=90)
canvas.draw()

setTitles()


# In[ ]:


# Infinate Loop - Read Values and Update Canvas
loopCnt=0
advanceList = []
revList = []
i=0

while True:
    
    try:
        s=ser.readline()
        line = s.decode()

        if 'Oil' in line:
            oilPressure = (float)(line.split(": ",1)[1])
            oilPress.draw_needle(oilPressure,200)       
        elif 'Fuel' in line:
            fuelPressure = (float)(line.split(": ",1)[1])
            fuelPress.draw_needle(fuelPressure,200)
        elif 'Coolant' in line:
            coolantTemp = int((float)(line.split(": ",1)[1]))
            temp.draw_needle(coolantTemp,200)
        elif 'RPM' in line:
            revs = (float)(line.split(": ",1)[1])
            rpm.draw_needle(revs,400)
            revList.append(revs)  
        elif 'Batt' in line:
            battVoltage = int((float)(line.split(": ",1)[1]))
            batt.draw_needle(battVoltage,200)
        elif 'Dwell Time' in line:
            dwellTime = (float)(line.split(": ",1)[1])
        elif 'Spark' in line:
            sparkTime = (float)(line.split(": ",1)[1])
        elif 'Advance Angle' in line:
            advanceAngle = int((float)(line.split(": ",1)[1]))
            advance.draw_needle(advanceAngle,200)
            advanceList.append(advanceAngle)
        elif 'Dwell Angle' in line:
            dwellAngle = int((float)(line.split(": ",1)[1]))
            dwell.draw_needle(dwellAngle,200)
            print (dwellAngle)

        #new_y =[0,5,9,13,16,19,21,23,25,27,28,29,30,30,30,30]
    except:
        print("Serial read error!")
 #   ax.scatter(4000,30)
 #   ax.scatter(1000,4)
    #line1.set_xdata(x)
    #line1.set_ydata(new_y)
 #   fig.canvas.draw()
    
    fig.canvas.flush_events()
        
    root.update_idletasks()
    root.update()
  


# In[ ]:


line


# In[ ]:


revList


# In[ ]:


loopCnt


# In[ ]:




