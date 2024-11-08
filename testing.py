import tkinter as tk
from PIL import Image, ImageTk
import pygame
import time
import threading
import serial

class StorylineApp:
    def __init__(self):
        # Initialize pygame for sound
        pygame.mixer.init()

        # Initialize serial connection (Example port)
        self.arduino_port = 'COM6'  # Change to your serial port
        self.baud_rate = 9600
        self.ser = serial.Serial(self.arduino_port, self.baud_rate)

        # Flags
        self.button_mode = True  # True for button, False for RFID
        self.current_step = 0  # Track current step in storyline

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Villager Storyline Sequence")
        self.root.geometry("1920x1080")
        self.root.config(bg="white")
        self.root.attributes("-fullscreen", True)

        # Images
        self.villager_photo = ImageTk.PhotoImage(Image.open("images/villager_intro.png").resize((1920, 1080)))
        self.kelp_prompt = ImageTk.PhotoImage(Image.open("images/kelp_prompt.png").resize((1920, 1080)))
        self.thank_you = ImageTk.PhotoImage(Image.open("images/villager_thankyou.png").resize((1920, 1080)))
        self.homescreen = ImageTk.PhotoImage(Image.open("images/temphomescreen.png").resize((1920, 1080)))

        # Create a label for images
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        # Storyline steps as an array of functions
        self.storyline_steps = [self.show_homescreen, self.show_intro, self.show_kelp_prompt, self.show_thank_you]

        # Start the storyline with the first step
        self.storyline_step()

        # Start the serial reading thread
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

        # Run the Tkinter event loop
        self.root.mainloop()

    def play_sound(self, file_path):
        """Play sound using pygame."""
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def show_homescreen(self):
        """Display the homescreen."""
        self.button_mode = True
        self.image_label.config(image=self.homescreen)

    def show_intro(self):
        """Display the introduction screen."""
        self.image_label.config(image=self.villager_photo)
        self.play_sound("sounds/Villager_idle1.ogg")

    def show_kelp_prompt(self):
        """Display the kelp prompt."""
        self.button_mode = False
        self.image_label.config(image=self.kelp_prompt)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_thank_you(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.image_label.config(image=self.thank_you)
        self.play_sound("sounds/villager_idle3.ogg")

    def storyline_step(self):
        """Execute the current step in the storyline."""
        if self.current_step < len(self.storyline_steps):
            self.storyline_steps[self.current_step]()  # Call the function for the current step
            self.current_step += 1  # Move to the next step
        else:
            print("Storyline has ended.")

    def button_press(self):
        """Handle button press to progress the storyline."""
        self.storyline_step()

    def read_serial(self):
        """Serial read thread to check for RFID input (if needed)."""
        while True:
            if self.ser.in_waiting > 0:
                serialdata = self.ser.readline().decode().strip()
                print("Serial data: ", serialdata)
                if self.button_mode and serialdata == "button":  # check button
                    self.button_press()
                if not self.button_mode and len(serialdata) == 14:  # check RFID
                    self.storyline_step()
            time.sleep(0.1)

# Start the application
if __name__ == "__main__":
    StorylineApp()
