import serial
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import time
from itertools import zip_longest
import threading

duty_cycles = []
led_voltages = []
led_currents = []
photocell_voltages = []
photocell_currents = []
photocell_resistances = []
gui = Tk()
duty_cycle_string = StringVar()

def main():
    gui.wm_title("Process Control")
    gui.geometry("1000x600")
    gui.grid_rowconfigure(0, weight=1)
    gui.grid_rowconfigure(1, weight=1)
    gui.grid_columnconfigure(0, weight=1)
    gui.grid_columnconfigure(1, weight=2)
    frame = Frame(gui)
    frame.grid(column = 0, row=0)
    global start_btn
    start_btn = Button(frame, text="Start", command=start_process_thread, height=2, width=10)
    start_btn.pack(side=TOP)
    label = Label(frame, textvariable=duty_cycle_string)
    label.pack(side=TOP)
    gui.mainloop()

def start_process_thread():
    global start_btn, process_thread, duty_cycle_string
    process_thread = threading.Thread(target=run_process, name="child")
    process_thread.daemon = True
    process_thread.start()
    gui.after(20, check_process)
    start_btn["state"] = DISABLED
    duty_cycle_string.set("Process Started")
    

def check_process():
    if process_thread.is_alive():
        gui.after(20, check_process)
    else:
        start_btn["state"] = NORMAL
        plot_graphs()

def run_process():
    global duty_cycles, led_voltages, photocell_voltages
    duty_cycles.clear()
    led_voltages.clear()
    photocell_voltages.clear()
    with serial.Serial("COM6", 9600, timeout=0.1) as ser:
        time.sleep(2)
        print("Connection to Arduino established!")
        ser.write(b"start\r\n")
        title = ""
        duty_cycle = 0
        led_voltage = 0.0
        photocell_voltage = 0.0
        while title != "done":
            title = ser.readline().decode("utf-8").strip()
            if title == "Duty Cycle, LED Resistor Voltage, Photocell Resistor Voltage":
                global duty_cycle_string
                duty_cycle = int(ser.readline().decode("utf-8").strip())
                duty_cycle_string.set("Duty Cycle: " + str(duty_cycle))
                led_voltage = float(ser.readline().decode("utf-8").strip())
                photocell_voltage = float(ser.readline().decode("utf-8").strip())
                duty_cycles.append(duty_cycle)
                led_voltages.append(led_voltage)
                photocell_voltages.append(photocell_voltage)
                
            if title:
                print("Title", title)
                print(duty_cycle)
                print(led_voltage)
                print(photocell_voltage)
  
def plot_graphs():
    global led_voltages, led_currents, photocell_voltages, photocell_currents, photocell_resistances
    led_resistance = 5.0 / max(led_voltages) - 1.0
    led_voltages = [ 5.0 - voltage for voltage in led_voltages ]
    led_currents = [ voltage / led_resistance for voltage in led_voltages ]
    photocell_resistances = [ 50.0 / voltage - 10.0 if voltage != 0 else 0.0 for voltage in photocell_voltages ]
    photocell_voltages = [ 5.0 - voltage for voltage in photocell_voltages]
    photocell_currents = [ voltage / resistance if resistance != 0 else 0.0 for voltage, resistance in zip_longest(photocell_voltages, photocell_resistances) ]

    fig, axs = plt.subplots(1, 2)
    axs[0].plot(duty_cycles, led_currents, '--g', linewidth=2)
    axs[0].set(title="LED Current", xlabel="Duty Cycle (%)", ylabel="LED Current (mA)")
    axs[1].plot(duty_cycles, led_voltages, '--r', linewidth=2)
    axs[1].set(title="LED Voltage", xlabel="Duty Cycle (%)", ylabel="LED Voltage (V)")
    canvas = FigureCanvasTkAgg(fig, master=gui)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=1, sticky=W+E+N+S)

    fig, axs = plt.subplots(1, 3)
    axs[0].set(title="Photocell Voltage", xlabel="Duty Cycle (%)", ylabel="Photocell Voltage (V)")
    axs[0].plot(duty_cycles, photocell_voltages, '--b', linewidth=2)
    axs[1].set(title="Photocell Current", xlabel="Duty Cycle (%)", ylabel="Photocell Current (mA)")
    axs[1].plot(duty_cycles, photocell_currents, '--p', linewidth=2)
    axs[2].set(title="Photocell Resistance", xlabel="LED Current (mA)", ylabel="Photocell Resistance (kOhm)")
    axs[2].plot(led_currents, photocell_resistances, '--y', linewidth=2)
    canvas = FigureCanvasTkAgg(fig, master=gui)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky=W+E+N+S)

if __name__ == "__main__":
    main()