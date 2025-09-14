import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def binary_to_signal(bits, bit_duration, fs):
    signal = []
    for bit in bits:
        value = int(bit)
        signal.extend([value] * int(bit_duration * fs))
    return np.array(signal)

def modulation_from_bits(bits, fs=1000, fc=50, bit_duration=0.1, kf=50, kp=np.pi/2, fsk_dev=30):
    
    t = np.arange(0, len(bits) * bit_duration, 1/fs)
    m = binary_to_signal(bits, bit_duration, fs)
    t = t[:len(m)]
    carrier = np.cos(2 * np.pi * fc * t)
    
    #AM
    am = (1 + 0.5 * m) * carrier
    #FM
    fm = np.cos(2 * np.pi * fc * t + kf * np.cumsum(m) / fs)
    #PM
    pm = np.cos(2 * np.pi * fc * t + kp * m)
    #ASK
    ask = m * carrier
    #FSK
    fsk = np.array([np.cos(2*np.pi*(fc if bit==0 else fc+fsk_dev)*ti) for bit, ti in zip(m, t)])
    #PSK
    psk = np.cos(2 * np.pi * fc * t + np.pi * m)
    
    return t, m, am, fm, pm, ask, fsk, psk

def run_modulation(binary_input, choice, canvas_frame):
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    t, m, am, fm_signal, pm_signal, ask_signal, fsk_signal, psk_signal = modulation_from_bits(binary_input)

    fig, axs = plt.subplots(2, 1, figsize=(8, 5))
    axs[0].plot(t, m, drawstyle="steps-pre")
    axs[0].set_title(f"Message Signal (Binary: {binary_input})")
    axs[0].set_xlabel("Time (s)")
    axs[0].set_ylabel("Amplitude")

    if choice == "AM":
        axs[1].plot(t, am)
        axs[1].set_title("Amplitude Modulation (AM)")
    elif choice == "FM":
        axs[1].plot(t, fm_signal)
        axs[1].set_title("Frequency Modulation (FM)")
    elif choice == "PM":
        axs[1].plot(t, pm_signal)
        axs[1].set_title("Phase Modulation (PM)")
    elif choice == "ASK":
        axs[1].plot(t, ask_signal)
        axs[1].set_title("Amplitude Shift Keying (ASK)")
    elif choice == "FSK":
        axs[1].plot(t, fsk_signal)
        axs[1].set_title("Frequency Shift Keying (FSK)")
    elif choice == "PSK":
        axs[1].plot(t, psk_signal)
        axs[1].set_title("Phase Shift Keying (PSK)")
    else:
        axs[1].set_title("Invalid choice!")

    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Amplitude")

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def launch_gui():
    root = tk.Tk()
    root.title("Digital Modulation Simulator")

    input_frame = tk.Frame(root)
    input_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    tk.Label(input_frame, text="Enter Binary Sequence:").pack(side=tk.LEFT, padx=5)
    binary_entry = tk.Entry(input_frame, width=20)
    binary_entry.pack(side=tk.LEFT, padx=5)

    tk.Label(input_frame, text="Select Modulation Type:").pack(side=tk.LEFT, padx=5)
    modulation_choice = ttk.Combobox(input_frame, values=["AM", "FM", "PM", "ASK", "FSK", "PSK"])
    modulation_choice.current(0)
    modulation_choice.pack(side=tk.LEFT, padx=5)

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    def on_run():
        binary_input = binary_entry.get()
        choice = modulation_choice.get()
        run_modulation(binary_input, choice, canvas_frame)

    tk.Button(root, text="Generate Signal", command=on_run).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
