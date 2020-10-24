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
                duty_cycle = int(ser.readline().decode("utf-8").strip())
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
    plot_graphs()

def plot_graphs():
    global duty_cycles, led_voltages, led_currents, photocell_voltages, photocell_currents, photocell_resistances
    led_resistance = 5.0 / max(led_voltages) - 1.0
    led_voltages = [ 5.0 - voltage for voltage in led_voltages ]
    led_currents = [ voltage / led_resistance for voltage in led_voltages ]
    photocell_resistances = [ 50.0 / voltage - 10.0 if voltage != 0 else 0.0 for voltage in photocell_voltages ]
    photocell_voltages = [ 5.0 - voltage for voltage in photocell_voltages]
    photocell_currents = [ voltage / resistance if resistance != 0 else 0.0 for voltage, resistance in zip_longest(photocell_voltages, photocell_resistances) ]

    color = "red"
    plt.plot(duty_cycles, led_currents, '--', linewidth=2)
    plt.xlabel("Duty Cycle (%)")
    plt.ylabel("LED Circuit Current (mA)")
    plt.savefig(color + "_duty_cycle_led_circuit_curr.png", dpi=300, bbox_inches="tight")
    
    plt.figure()
    plt.plot(duty_cycles, [led_resistance] * len(duty_cycles), '--', linewidth=2)
    plt.xlabel("Duty Cycle (%)")
    plt.ylabel("LED Resistance (kOhm)")
    plt.savefig(color + "_duty_cycle_led_res.png", dpi=300, bbox_inches="tight")
    
    plt.figure()
    plt.plot(duty_cycles, photocell_resistances, '--', linewidth=2)
    plt.xlabel("Duty Cycle (%)")
    plt.ylabel("Photocell Resistance (kOhm)")
    plt.savefig(color + "_duty_cycle_photo_res.png", dpi=300, bbox_inches="tight")
    
    plt.figure()
    plt.plot(duty_cycles, photocell_currents, '--', linewidth=2)
    plt.xlabel("Duty Cycle (%)")
    plt.ylabel("Photocell Current (mA)")
    plt.savefig(color + "_duty_cycle_photo_curr.png", dpi=300, bbox_inches="tight")
    
    plt.figure()
    plt.plot(photocell_resistances, led_currents, '--', linewidth=2)
    plt.ylabel("LED Current (mA)")
    plt.xlabel("Photocell Resistance (kOhm)")
    plt.savefig(color + "_photo_res_led_curr.png", dpi=300, bbox_inches="tight")
    
    plt.show()

if __name__ == "__main__":
    main()