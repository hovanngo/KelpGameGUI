import tkinter as tk
from PIL import Image, ImageTk
import pygame
import time
import threading
import serial
import keyboard



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
        self.level = 1  # Start at level 1
        self.rfid_count = 0  # Count of RFIDs scanned in the current level
        self.rfid_targets = {1: 3, 2: 5, 3: 8}  # Targets for each level
        self.time_left = 10  # Countdown starting from 60 seconds

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Villager Storyline Sequence")
        self.root.geometry("1920x1080")
        self.root.config(bg="white")
        self.root.attributes("-fullscreen", True)

        # Images
        self.villager_photo = ImageTk.PhotoImage(Image.open("images/villager_intro.png").resize((1920, 1080)))
        self.kelp_prompt = ImageTk.PhotoImage(Image.open("images/kelp_prompt.png").resize((300, 300)))
        self.thank_you = ImageTk.PhotoImage(Image.open("images/villager_thankyou.png").resize((1920, 1080)))
        self.homescreen = ImageTk.PhotoImage(Image.open("images/temphomescreen.png").resize((1920, 1080)))
        self.timeup = ImageTk.PhotoImage(Image.open("images/timeup.png").resize((800,600)))
        self.kelp1 = ImageTk.PhotoImage(Image.open("images/temp1.png").resize((1920,1080)))
        self.kelp2 = ImageTk.PhotoImage(Image.open("images/temp2.png").resize((1920,1080)))
        self.kelp3 = ImageTk.PhotoImage(Image.open("images/temp3.png").resize((1920,1080)))
        

        # Create a label for images
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        # Create a label to show countdown

        self.time_label = tk.Label(self.root, text=f"Time Left: {self.time_left}s", font=("Helvetica", 24), bg = "white")
        self.time_label.place(x=1000, y=100)
        self.time_label.pack(pady=20)

        


        self.root.bind("<space>", self.on_space_press)

        # Storyline steps as an array of functions
        self.storyline_steps = [
            self.show_homescreen,
            self.show_intro,
            self.show_kelp_prompt,
            self.show_kelp1,
            self.show_kelp2,
            self.show_kelp3,
            #show level2 
            self.show_kelp_prompt,
            self.show_kelp1,
            self.show_kelp2,
            self.show_kelp3,
            self.show_kelp3,
            self.show_kelp3,
            #show level3
            self.show_kelp_prompt,
            self.show_kelp1,
            self.show_kelp2,
            self.show_kelp3,
            self.show_kelp3,
            self.show_kelp3,
            self.show_kelp3,
            self.show_kelp3,
            self.show_kelp3,
            self.show_thank_you
        ]

        # Start the storyline with the first step
        self.storyline_step()

        # Start the serial reading thread
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

        # Start the countdown timer

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
        self.update_countdown()
    

    def show_thank_you(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.image_label.config(image=self.thank_you)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_timeup(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.image_label.config(image=self.timeup)
        self.play_sound("sounds/failure.mp3")
        self.time_label.config(text="Time's up!")
        print(f"Level {self.level} failed! Time's up!")

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
                    self.rfid_scanned()

            time.sleep(0.1)

    def rfid_scanned(self):
        """Handle RFID scan for the current level."""
        if self.rfid_count < self.rfid_targets[self.level]:
            self.rfid_count += 1
            self.storyline_step()
            print(f"RFID {self.rfid_count}/{self.rfid_targets[self.level]} scanned")
            if self.rfid_count == self.rfid_targets[self.level]:
                self.level_up()
                

    def level_up(self):
        """Move to the next level."""
        if self.level < 3:
            self.level += 1
            self.rfid_count = 0  # Reset RFID count for the next level
            self.time_left = 60  # Reset the timer for the new level
            print(f"Level {self.level} reached. Scanning {self.rfid_targets[self.level]} RFIDs.")
            self.root.after(3000, self.storyline_step)
        else:
            print("All levels completed.")
            self.show_thank_you()  # Show the final thank you screen

    def update_countdown(self):
        """Update the countdown timer."""
        if self.time_left > 0:
            self.time_left -= 1
            self.time_label.config(text=f"Time Left: {self.time_left}s")
            self.root.after(1000, self.update_countdown)
        else:
            self.check_level_status()

    def check_level_status(self):
        """Check if the current level is complete."""
        if self.rfid_count < self.rfid_targets[self.level]:
            self.show_timeup()  # Show thank you screen if time runs out before completing the task
        else:
            print(f"Level {self.level} complete!")
            self.level_up()
    
    def show_kelp1(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.image_label.config(image=self.kelp1)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp2(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.image_label.config(image=self.kelp2)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp3(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.image_label.config(image=self.kelp3)
        self.play_sound("sounds/villager_idle3.ogg")

    def on_space_press(self,event):
            print("manual skip")
            self.storyline_step()


    
# Start the application
if __name__ == "__main__":
    StorylineApp()
