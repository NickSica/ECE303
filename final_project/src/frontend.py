import serial
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import time
from itertools import zip_longest
import threading

gui = Tk()
dist_string = StringVar()
headlight_string = StringVar()
speed_string = StringVar()
coolant_string = StringVar()
temp_string = StringVar()

def main():
    gui_layout()
    start_process_thread()

def gui_layout():
    gui.wm_title("Process Control")
    gui.geometry("1000x600")
    gui.grid_rowconfigure(0, weight=1)
    gui.grid_rowconfigure(1, weight=1)
    gui.grid_columnconfigure(0, weight=1)
    gui.grid_columnconfigure(1, weight=1)
    #frame = Frame(gui)
    #frame.grid(column = 0, row=0)
    global canvas, speed_led, dist_string, headlight_string, speed_string, coolant_string, temp_string
    canvas = Canvas(gui)
    speed_led = canvas.create_oval(5, 5, 100, 100, fill="green")
    canvas.pack(side=TOP)

    dist_label = Label(gui, textvariable=dist_string)
    dist_label.pack(side=TOP)

    headlight_label = Label(gui, textvariable=headlight_string)
    headlight_label.pack(side=TOP)

    speed_label = Label(gui, textvariable=speed_string)
    speed_label.pack(side=TOP)

    coolant_label = Label(gui, textvariable=coolant_string)
    coolant_label.pack(side=TOP)

    temp_label = Label(gui, textvariable=temp_string)
    temp_label.pack(side=TOP)

    dist_string.set("Distance: N/A")
    headlight_string.set("Headlight: N/A")
    speed_string.set("Motor Speed: N/A")
    coolant_string.set("Coolant: N/A")
    temp_string.set("Temperature: N/A")

def start_process_thread():
    global process_thread
    process_thread = threading.Thread(target=run_process, name="child")
    process_thread.daemon = True
    process_thread.start()
    gui.mainloop()

def run_process():
    with serial.Serial("COM6", 9600, timeout=0.1) as ser:
        time.sleep(2)
        print("Connection to Arduino established!")
        while True:
            ser_line = ser.readline().decode("utf-8").strip().split(":")
            print(ser_line)
            if ser_line[0] == "speed":
                update_speed(int(ser_line[1].split('\r', 1)[0]))
            elif ser_line[0] == "distance":
                global dist_string
                dist_string.set("Distance: " + str(ser_line[1]))
            elif ser_line[0] == "headlight":
                global headlight_string
            elif ser_line[0] == "coolant":
                global coolant_string
            elif ser_line[0] == "temp":
                global temp_string

def update_speed(speed):
    global speed_led, speed_string
    speed_string.set("Motor Speed: " + str((speed / 255) * 100))
    if speed >= 170:
        canvas.itemconfig(speed_led, fill="green")
    elif speed >= 85:
        canvas.itemconfig(speed_led, fill="yellow")
    else:
        canvas.itemconfig(speed_led, fill="red")

if __name__ == "__main__":
    main()