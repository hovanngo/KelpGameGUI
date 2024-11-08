import tkinter as tk
from PIL import Image, ImageTk
import pygame
import time
import threading

# Initialize pygame for sound
pygame.mixer.init()

# Initialize serial connection (Example port)
import serial
arduino_port = 'COM6'  # Change to your serial port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)

#flags
button_mode = True  # True for button, False for RFID

# Tkinter setup
root = tk.Tk()
root.title("Villager Storyline Sequence")
root.geometry("1920x1080")
root.config(bg="white")
root.attributes("-fullscreen", True)

# Images
villager_photo = ImageTk.PhotoImage(Image.open("images/villager_intro.png").resize((1920, 1080)))
kelp_prompt = ImageTk.PhotoImage(Image.open("images/kelp_prompt.png").resize((1920, 1080)))
thank_you = ImageTk.PhotoImage(Image.open("images/villager_thankyou.png").resize((1920, 1080)))
homescreen = ImageTk.PhotoImage(Image.open("images/temphomescreen.png").resize((1920, 1080)))

# Create a label for images
image_label = tk.Label(root)
image_label.pack()

# Global variable to track current step in storyline
current_step = 0

# Functions to handle storyline steps
def play_sound(file_path):
    """Play sound using pygame."""
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def show_homescreen():
    """Display the homescreen."""
    global button_mode
    button_mode = True
    image_label.config(image=homescreen)

def show_intro():
    """Display the introduction screen."""
    image_label.config(image=villager_photo)
    play_sound("sounds/Villager_idle1.ogg")

def show_kelp_prompt():
    """Display the kelp prompt."""
    global button_mode
    button_mode = False
    image_label.config(image=kelp_prompt)
    play_sound("sounds/villager_idle3.ogg")

def show_thank_you():
    global button_mode
    button_mode = False
    image_label.config(image=thank_you)
    play_sound("sounds/villager_idle3.ogg")

# Storyline steps as an array of functions
storyline_steps = [show_homescreen, show_intro, show_kelp_prompt, show_thank_you]

# Function to execute the current step in the storyline
def storyline_step():
    global current_step
    if current_step < len(storyline_steps):
        storyline_steps[current_step]()  # Call the function for the current step
        current_step += 1  # Move to the next step
    else:
        print("Storyline has ended.")

# Button press handler
def button_press():
    """Handle button press to progress the storyline."""
    storyline_step()

# Serial read thread to check for RFID input (if needed)
def read_serial():
    global button_mode
    while True:
        if ser.in_waiting > 0:
            serialdata = ser.readline().decode().strip()
            print("Serial data: ", serialdata)
            if button_mode == True and serialdata == "button": #check button
                button_press()
            if button_mode == False and len(serialdata) == 14:   #check rfid
                storyline_step()
        time.sleep(0.1)

# Start the serial reading thread
serial_thread = threading.Thread(target=read_serial)
serial_thread.daemon = True
serial_thread.start()

# Start the storyline with the first step
storyline_step()  # Call the first step


# Run the Tkinter event loop
root.mainloop()
