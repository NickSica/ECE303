import serial
from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
import time
from itertools import zip_longest

duty_cycles = []
led_voltages = []
led_currents = []
photocell_voltages = []
photocell_currents = []
photocell_resistances = []

def main():
    gui = Tk()
    gui.wm_title("Process Control")
    start_btn = Button(gui, text="Start", command=run_process)
    start_btn.pack(anchor = W)
    gui.mainloop()

def run_process():
    global duty_cycles, led_voltages, led_currents, photocell_voltages, photocell_currents, photocell_resistances
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
                duty_cycle = int(ser.readline().decode("utf-8").strip())
                led_voltage = float(ser.readline().decode("utf-8").strip())
                photocell_voltage = float(ser.readline().decode("utf-8").strip())

            if title:
                print("Title", title)
                print(duty_cycle)
                print(led_voltage)
                print(photocell_voltage)
                duty_cycles.append(duty_cycle)
                led_voltages.append(led_voltage)
                photocell_voltages.append(photocell_voltage)
    plot_graphs()

def plot_graphs():
    global duty_cycles, led_voltages, led_currents, photocell_voltages, photocell_currents, photocell_resistances
    led_resistance = 5000.0 / max(led_voltages) - 1000.0
    led_voltages = [ 5.0 - voltage for voltage in led_voltages ]
    led_currents = [ voltage / led_resistance for voltage in led_voltages ]
    photocell_resistances = [ 50000.0 / voltage - 10000.0 for voltage in photocell_voltages ]
    photocell_voltages = [ 5.0 - voltage for voltage in photocell_voltages]
    photocell_currents = [ voltage / resistance for voltage, resistance in zip_longest(photocell_voltages, photocell_resistances) ]

    plt.plot(duty_cycles, led_currents, '--g', linewidth=2)
    plt.figure()
    plt.plot(duty_cycles, led_voltages, '--r', linewidth=2)
    plt.figure()
    plt.plot(duty_cycles, photocell_voltages, '--b', linewidth=2)
    plt.figure()
    plt.plot(duty_cycles, photocell_currents, '--p', linewidth=2)
    plt.figure()
    plt.plot(led_currents, photocell_resistances, '--y', linewidth=2)
    plt.show()

if __name__ == "__main__":
    main()