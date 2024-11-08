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
        self.level = 1  # Start at level 1
        self.rfid_count = 0  # Count of RFIDs scanned in the current level
        self.rfid_targets = {1: 3, 2: 5, 3: 8}  # Targets for each level
        self.time_left = 30  # Countdown starting from 10 seconds

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Villager Storyline Sequence")
        self.root.geometry("1920x1080")
        self.root.config(bg="white")
        self.root.attributes("-fullscreen", True)

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, bg="white")
        self.canvas.pack()

        # Load images
        self.villager_photo = ImageTk.PhotoImage(Image.open("images/villager_intro.png").resize((1600, 900)))
        self.kelp_prompt = ImageTk.PhotoImage(Image.open("images/kelp_prompt.png").resize((1600, 900)))
        self.thank_you = ImageTk.PhotoImage(Image.open("images/villager_thankyou.png").resize((1600, 900)))
        self.homescreen = ImageTk.PhotoImage(Image.open("images/welcome_screen.gif").resize((1600, 900)))
        self.timeup = ImageTk.PhotoImage(Image.open("images/time_up.jpg").resize((1600,900)))
        self.kelp1 = ImageTk.PhotoImage(Image.open("images/kelp_1.jpg").resize((1600,900)))
        self.kelp2 = ImageTk.PhotoImage(Image.open("images/kelp_2.jpg").resize((1600,900)))
        self.kelp3 = ImageTk.PhotoImage(Image.open("images/kelp_3.jpg").resize((1600,900)))
        self.kelp4 = ImageTk.PhotoImage(Image.open("images/kelp_4.jpg").resize((1600,900)))
        self.kelp5 = ImageTk.PhotoImage(Image.open("images/kelp_5.jpg").resize((1600,900)))
        self.kelp6 = ImageTk.PhotoImage(Image.open("images/kelp_6.jpg").resize((1600,900)))
        self.kelp7 = ImageTk.PhotoImage(Image.open("images/kelp_7.jpg").resize((1600,900)))
        self.kelp8 = ImageTk.PhotoImage(Image.open("images/kelp_8.jpg").resize((1600,900)))
        self.level1 = ImageTk.PhotoImage(Image.open("images/level_1.jpg").resize((1600, 900)))
        self.level2 = ImageTk.PhotoImage(Image.open("images/level_2.jpg").resize((1600, 900)))

        #why the fuck is it 16:9. I cant figure out why it doesnt work with 1920x1080

        # Create labels on canvas for images and timer text
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.homescreen)
        

        # Bind space key to manual skip
        self.root.bind("<space>", self.on_space_press)

        # Storyline steps as an array of functions
        self.storyline_steps = [
            self.show_homescreen,
            self.show_intro,
            self.show_kelp_prompt,
            self.show_kelp1,
            self.show_kelp2,
            self.show_kelp3,
            self.show_level1,
            self.show_kelp_prompt, 
            self.show_kelp1,
            self.show_kelp2,
            self.show_kelp3,
            self.show_kelp4,
            self.show_kelp5,
            self.show_level2, 
            self.show_kelp_prompt,
            self.show_kelp1,
            self.show_kelp2,
            self.show_kelp3,
            self.show_kelp4,
            self.show_kelp5,
            self.show_kelp6,
            self.show_kelp7,
            self.show_kelp8,
            self.show_thank_you
        ]

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
        self.canvas.itemconfig(self.image_on_canvas, image=self.homescreen)

    def show_intro(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.villager_photo)
        self.play_sound("sounds/Villager_idle1.ogg")

    def show_kelp_prompt(self):
        """Display the kelp prompt."""
        self.button_mode = False
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp_prompt)
        self.time_text = self.canvas.create_text(800, 800, text=f"Time Left: {self.time_left}s", font=("Helvetica", 24), fill="black")
        self.play_sound("sounds/villager_idle3.ogg")
        self.update_countdown()
    
    def show_thank_you(self):
        """Display the thank you screen."""
        self.button_mode = False
        self.canvas.itemconfig(self.image_on_canvas, image=self.thank_you)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_timeup(self):
        """Display the time-up screen."""
        self.button_mode = False
        self.canvas.itemconfig(self.image_on_canvas, image=self.timeup)
        self.play_sound("sounds/failure.mp3")
        self.canvas.itemconfig(self.time_text, text="Time's up!")
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
        """Update the countdown timer on the canvas."""
        if self.time_left > 0:
            self.time_left -= 1
            self.canvas.itemconfig(self.time_text, text=f"Time Left: {self.time_left}s")
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
        """Display kelp image 1."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp1)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp2(self):
        """Display kelp image 2."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp2)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp3(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp3)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp4(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp4)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp5(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp5)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp6(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp6)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp7(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp7)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_kelp8(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp8)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_level1(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.level1)
        self.play_sound("sounds/villager_idle3.ogg")

    def show_level2(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.level2)
        self.play_sound("sounds/villager_idle3.ogg")

    def on_space_press(self, event):
        """Manual skip to the next storyline step."""
        print("Manual skip")
        self.storyline_step()

# Start the application
if __name__ == "__main__":
    StorylineApp()
