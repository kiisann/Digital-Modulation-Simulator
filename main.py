import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def binary_to_signal(bits, bit_duration, fs):
    samples_per_bit = int(bit_duration * fs)
    signal = []
    for bit in bits:
        value = int(bit)
        signal.extend([value] * samples_per_bit)
    return np.array(signal)

def line_coding(bits, bit_duration, fs, method="NRZ-L"):
    samples_per_bit = int(bit_duration * fs)
    total_samples = len(bits) * samples_per_bit
    t = np.linspace(0, len(bits) * bit_duration, total_samples, endpoint=False)
    signal = []
    if method == "Digital":
        for bit in bits:
            value = 1 if bit == '1' else 0
            signal.extend([value] * samples_per_bit)
    elif method == "NRZ-L":
        for bit in bits:
            value = -1 if bit == '1' else 1
            signal.extend([value] * samples_per_bit)
    elif method == "NRZ-I":
        last_value = 1
        for bit in bits:
            if bit == '1':
                last_value *= -1
            signal.extend([last_value] * samples_per_bit)
    elif method == "RZ":
        half = samples_per_bit // 2
        for bit in bits:
            high = 1 if bit == '1' else -1
            signal.extend([high] * half + [0] * (samples_per_bit - half))
    elif method == "Manchester":
        half = samples_per_bit // 2
        for bit in bits:
            if bit == '1':
                signal.extend([-1] * half + [1] * half)
            else:
                signal.extend([1] * half + [-1] * half)
    elif method == "Differential Manchester":
        last_value = 1
        half = samples_per_bit // 2
        for bit in bits:
            if bit == '0':
                last_value *= -1
                first_half = [last_value] * half
                second_half = [-last_value] * half
            else:
                first_half = [last_value] * half
                second_half = [-last_value] * half
                last_value *= -1
            signal.extend(first_half + second_half)
    return t, np.array(signal)

def modulation_from_bits(bits, fs=1000, fc=50, bit_duration=0.1, kf=50, kp=np.pi/2, fsk_dev=30):
    samples_per_bit = int(bit_duration * fs)
    total_samples = len(bits) * samples_per_bit
    t = np.linspace(0, len(bits) * bit_duration, total_samples, endpoint=False)
    m = binary_to_signal(bits, bit_duration, fs)
    carrier = np.cos(2 * np.pi * fc * t)
    am = (1 + 0.5 * m) * carrier
    fm = np.cos(2 * np.pi * fc * t + kf * np.cumsum(m) / fs)
    pm = np.cos(2 * np.pi * fc * t + kp * m)
    ask = m * carrier
    fsk = np.array([np.cos(2*np.pi*(fc if bit==0 else fc+fsk_dev)*ti) for bit, ti in zip(m, t)])
    psk = np.cos(2 * np.pi * fc * t + np.pi * m)
    return t, am, fm, pm, ask, fsk, psk

def run_simulation(binary_input, choice, canvas_frame):
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 4))
    digital_methods = ["Digital", "NRZ-L", "NRZ-I", "RZ", "Manchester", "Differential Manchester"]

    if choice in digital_methods:
        t_line, signal = line_coding(binary_input, 0.1, 1000, method=choice)
        ax.plot(t_line, signal, drawstyle="steps-pre", color="black", linewidth=2)
        ax.set_title(choice)

        bit_duration = 0.1
        for i, bit in enumerate(binary_input):
            xpos = i * bit_duration + bit_duration / 2
            ypos = min(signal) + 0.5
            ax.text(xpos, ypos, bit, ha="center", va="top",
                    fontsize=10, color="black", fontweight="bold")
            ax.axvline(x=i * bit_duration, color="black",
                       linestyle="--", linewidth=0.7)

        ax.axvline(x=len(binary_input) * bit_duration,
                   color="black", linestyle="--", linewidth=0.7)

    else:
        t, am, fm_signal, pm_signal, ask_signal, fsk_signal, psk_signal = modulation_from_bits(binary_input)
        if choice == "AM":
            ax.plot(t, am, color="black")
            ax.set_title("Amplitude Modulation (AM)")
            ref_signal = am
        elif choice == "FM":
            ax.plot(t, fm_signal, color="black")
            ax.set_title("Frequency Modulation (FM)")
            ref_signal = fm_signal
        elif choice == "PM":
            ax.plot(t, pm_signal, color="black")
            ax.set_title("Phase Modulation (PM)")
            ref_signal = pm_signal
        elif choice == "ASK":
            ax.plot(t, ask_signal, color="black")
            ax.set_title("Amplitude Shift Keying (ASK)")
            ref_signal = ask_signal
        elif choice == "FSK":
            ax.plot(t, fsk_signal, color="black")
            ax.set_title("Frequency Shift Keying (FSK)")
            ref_signal = fsk_signal
        elif choice == "PSK":
            ax.plot(t, psk_signal, color="black")
            ax.set_title("Phase Shift Keying (PSK)")
            ref_signal = psk_signal

        bit_duration = 0.1
        for i, bit in enumerate(binary_input):
            xpos = (i + 0.5) * bit_duration
            ypos = max(ref_signal) + 0.5
            ax.text(xpos, ypos, bit, ha="center", va="bottom",
                    fontsize=10, color="black", fontweight="bold")
            ax.axvline(x=i * bit_duration, color="black",
                       linestyle="--", linewidth=0.7)

        ax.axvline(x=len(binary_input) * bit_duration,
                   color="black", linestyle="--", linewidth=0.7)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Value", fontweight="bold", color="black")
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def launch_gui():
    root = tk.Tk()
    root.title("Digital Modulation Signal Simulator")

    try:
        bg_image = Image.open("bg1.png")
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.place(relwidth=1, relheight=1)
    except FileNotFoundError:
        pass

    input_frame = tk.Frame(root, bd=2)
    input_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    tk.Label(input_frame, text="Enter Binary Sequence:").pack(side=tk.LEFT, padx=10)
    binary_entry = tk.Entry(input_frame, width=20)
    binary_entry.pack(side=tk.LEFT, padx=5)

    tk.Label(input_frame, text="Select Type:").pack(side=tk.LEFT, padx=10)
    signal_choice = ttk.Combobox(input_frame, values=[
        "Digital", "AM", "FM", "PM", "ASK", "FSK", "PSK",
        "NRZ-L", "NRZ-I", "RZ", "Manchester", "Differential Manchester"
    ])
    signal_choice.current(0)
    signal_choice.pack(side=tk.LEFT, padx=5)

    canvas_frame = tk.Frame(root, bd=2)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    def on_run():
        binary_input = binary_entry.get().strip()
        if not all(bit in '01' for bit in binary_input):
            return
        choice = signal_choice.get()
        run_simulation(binary_input, choice, canvas_frame)

    tk.Button(root, text="Generate Signal", command=on_run).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()