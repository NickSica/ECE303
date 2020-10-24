import serial
from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
import time
from itertools import zip_longest
import pickle

duty_cycles = []
led_voltages = []
led_currents = []
photocell_voltages = []
photocell_currents = []
photocell_resistances = []
num_colors = 2#5

def main():
    global duty_cycles, led_voltages, photocell_voltages
    duty_cycles.clear()
    led_voltages.clear()
    photocell_voltages.clear()
    with serial.Serial("COM6", 9600, timeout=0.1) as ser:
        time.sleep(2)
        print("Connection to Arduino established!")
        for i in range(0, num_colors):
            time.sleep(20)
            ser.write(b"start\r\n")
            title = ""
            duty_cycle = 0
            led_voltage = 0.0
            photocell_voltage = 0.0
            duty_cycles.append([])
            led_voltages.append([])
            photocell_voltages.append([])
            while title != "done":
                title = ser.readline().decode("utf-8").strip()
                if title == "Duty Cycle, LED Resistor Voltage, Photocell Resistor Voltage":
                    duty_cycle = int(ser.readline().decode("utf-8").strip())
                    led_voltage = float(ser.readline().decode("utf-8").strip())
                    photocell_voltage = float(ser.readline().decode("utf-8").strip())
                    duty_cycles[i].append(duty_cycle)
                    led_voltages[i].append(led_voltage)
                    photocell_voltages[i].append(photocell_voltage)

                if title:
                    print("Title", title)
                    print(duty_cycle)
                    print(led_voltage)
                    print(photocell_voltage)
            
            with open("data_" + str(i), "wb") as file:
                pickle.dump(duty_cycles[i], file)
                pickle.dump(led_voltages[i], file)
                pickle.dump(photocell_voltages[i], file)
    plot_graphs()

def plot_graphs():
    global duty_cycles, led_voltages, led_currents, photocell_voltages, photocell_currents, photocell_resistances
    led_resistances = []
    for i in range(0, num_colors):
        led_resistances.append(5.0 / max(led_voltages[i]) - 1.0)
        led_voltages.append([ 5.0 - voltage for voltage in led_voltages[i] ])
        led_currents.append([ voltage / led_resistances[i] for voltage in led_voltages[i] ])
        photocell_resistances.append([ 50.0 / voltage - 10.0 if voltage != 0 else 0.0 for voltage in photocell_voltages[i] ])
        photocell_voltages.append([ 5.0 - voltage for voltage in photocell_voltages[i] ])
        photocell_currents.append([ voltage / resistance if resistance != 0 else 0.0 for voltage, resistance in zip_longest(photocell_voltages[i], photocell_resistances[i]) ])

    line_colors = [ "black", "red", "yellow", "green", "blue" ]
    color_labels = [ "White LED", "Red LED", "Yellow LED", "Green LED", "Blue LED" ]
    for i in range(0, num_colors):
        plt.plot(duty_cycles[i], led_currents[i], marker='', linestyle="dashed", linewidth=2, color=line_colors[i], label=color_labels[i])
        plt.xlabel("Duty Cycle (%)")
        plt.ylabel("LED Circuit Current (mA)")
    plt.legend()
    plt.figure()

    for i in range(0, num_colors):
        plt.plot(duty_cycles[i], [led_resistances[i]] * len(duty_cycles[i]), marker='', linestyle="dashed", linewidth=2, color=line_colors[i], label=color_labels[i])
        plt.xlabel("Duty Cycle (%)")
        plt.ylabel("LED Resistance (kOhm)")
    plt.legend()
    plt.figure()

    for i in range(0, num_colors):
        plt.plot(duty_cycles[i], photocell_resistances[i], marker='', linestyle="dashed", linewidth=2, color=line_colors[i], label=color_labels[i])
        plt.xlabel("Duty Cycle (%)")
        plt.ylabel("Photocell Resistance (kOhm)")
    plt.legend()
    plt.figure()

    for i in range(0, num_colors):   
        plt.plot(duty_cycles[i], photocell_currents[i], marker='', linestyle="dashed", linewidth=2, color=line_colors[i], label=color_labels[i])
        plt.xlabel("Duty Cycle (%)")
        plt.ylabel("Photocell Current (mA)")
    plt.legend()
    plt.figure()

    for i in range(0, num_colors):
        plt.plot(led_currents[i], photocell_resistances[i], marker='', linestyle="dashed", linewidth=2, color=line_colors[i], label=color_labels[i])
        plt.xlabel("LED Current (mA)")
        plt.ylabel("Photocell Resistance (kOhm)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()