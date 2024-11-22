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
        self.time_left = 60  # Initialize timer
        self.timer_status = False

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
        self.homescreen = ImageTk.PhotoImage(Image.open("images/welcome_screen2.gif").resize((1920, 1080)))
        self.story1 = ImageTk.PhotoImage(Image.open("images/2.jpg").resize((1920, 1080)))
        self.story2 = ImageTk.PhotoImage(Image.open("images/3.jpg").resize((1920, 1080)))
        self.story3 = ImageTk.PhotoImage(Image.open("images/4.jpg").resize((1920, 1080)))
        self.story4 = ImageTk.PhotoImage(Image.open("images/5.jpg").resize((1920,1080)))
        self.story5 = ImageTk.PhotoImage(Image.open("images/6.jpg").resize((1920,1080)))
        self.story6 = ImageTk.PhotoImage(Image.open("images/7.jpg").resize((1920,1080)))
        self.level1 = ImageTk.PhotoImage(Image.open("images/8.jpg").resize((1920,1080)))
        self.instruct1 = ImageTk.PhotoImage(Image.open("images/9.jpg").resize((1920,1080)))
        self.instruct2 = ImageTk.PhotoImage(Image.open("images/10.jpg").resize((1920,1080)))
        self.kelp1 = ImageTk.PhotoImage(Image.open("images/11.jpg").resize((1920,1080)))
        self.fact1 = ImageTk.PhotoImage(Image.open("images/12.jpg").resize((1920,1080)))
        self.kelp2 = ImageTk.PhotoImage(Image.open("images/13.jpg").resize((1920,1080)))
        self.fact2 = ImageTk.PhotoImage(Image.open("images/14.jpg").resize((1920, 1080)))
        self.kelp3 = ImageTk.PhotoImage(Image.open("images/15.jpg").resize((1920, 1080)))
        self.fact3 = ImageTk.PhotoImage(Image.open("images/16.jpg").resize((1920, 1080)))
        self.thankyou1 = ImageTk.PhotoImage(Image.open("images/17.jpg").resize((1920, 1080)))
        self.level1fail = ImageTk.PhotoImage(Image.open("images/18.jpg").resize((1920, 1080)))
        self.failscreen1 = ImageTk.PhotoImage(Image.open("images/19.jpg").resize((1920, 1080)))
        self.retry = ImageTk.PhotoImage(Image.open("images/20.jpg").resize((1920, 1080)))
        self.story7 = ImageTk.PhotoImage(Image.open("images/21.jpg").resize((1920, 1080)))
        self.story8 = ImageTk.PhotoImage(Image.open("images/22.jpg").resize((1920, 1080)))
        self.story9 = ImageTk.PhotoImage(Image.open("images/23.jpg").resize((1920, 1080)))
        self.story10 = ImageTk.PhotoImage(Image.open("images/24.jpg").resize((1920, 1080)))
        self.level2 = ImageTk.PhotoImage(Image.open("images/25.jpg").resize((1920, 1080)))
        self.instruct3 = ImageTk.PhotoImage(Image.open("images/26.jpg").resize((1920, 1080)))
        self.instruct4 = ImageTk.PhotoImage(Image.open("images/27.jpg").resize((1920, 1080)))
        self.fact4 = ImageTk.PhotoImage(Image.open("images/29.jpg").resize((1920, 1080)))
        self.fact5 = ImageTk.PhotoImage(Image.open("images/32.jpg").resize((1920, 1080)))
        self.kelp4 = ImageTk.PhotoImage(Image.open("images/33.jpg").resize((1920, 1080)))
        self.kelp5 = ImageTk.PhotoImage(Image.open("images/34.jpg").resize((1920, 1080)))
        self.fact6 = ImageTk.PhotoImage(Image.open("images/35.jpg").resize((1920, 1080)))
        self.thankyou2 = ImageTk.PhotoImage(Image.open("images/36.jpg").resize((1920, 1080)))
        self.level2fail = ImageTk.PhotoImage(Image.open("images/37.jpg").resize((1920, 1080)))
        self.failscreen2 = ImageTk.PhotoImage(Image.open("images/38.jpg").resize((1920, 1080)))
        self.thankyou3 = ImageTk.PhotoImage(Image.open("images/39.jpg").resize((1920, 1080)))
        self.kelp6 = ImageTk.PhotoImage(Image.open("images/44.jpg").resize((1920, 1080)))
        self.kelp7 = ImageTk.PhotoImage(Image.open("images/45.jpg").resize((1920, 1080)))
        self.kelp8 = ImageTk.PhotoImage(Image.open("images/46.jpg").resize((1920, 1080)))
        #change display of computer to fit 1920x1080 -> display scale to 100%

        # Create labels on canvas for images and timer text
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.homescreen)
        self.homescreen_frames = self.load_gif_frames("images/welcome_screen2.gif")
        self.current_frame_index = 0  # Start from the first frame
        
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw")
        

        # Bind space key to manual skip
        self.root.bind("<space>", self.on_space_press)

        # Storyline steps as an array of functions
        self.storyline_steps = [
            self.show_homescreen,
            self.show_story1,
            self.show_story2,
            self.show_story3,
            self.show_story4,
            self.show_story5,
            self.show_story6,
            self.show_level1,
            self.show_instruct1,
            self.show_instruct2,
            self.show_kelp1,
            self.show_fact1,
            self.show_kelp2,
            self.show_fact2,
            self.show_kelp3,
            self.show_fact3,
            self.show_thankyou1,
            self.show_story7,
            self.show_story8,
            self.show_story9,
            self.show_story10,
            self.show_level2,
            self.show_instruct3,
            self.show_instruct4,
            self.show_kelp1,
            self.show_fact4,
            self.show_kelp2,
            self.show_fact5,
            self.show_kelp3,
            self.show_kelp4,
            self.show_fact6,
            self.show_kelp5,
            self.show_thankyou2
            #maybe end screen?
        ]


        #Storyline setup. Start the storyline with the first step.
        self.storyline_step()
        self.play_sound("sounds/Subwoofer_lullaby.mp3")

        # Start the serial reading thread
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

        # Run the Tkinter event loop
        self.root.mainloop()

    def load_gif_frames(self, gif_path):
        """Load frames from a GIF file."""
        gif_image = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = gif_image.copy().resize((1920, 1080))
                frames.append(ImageTk.PhotoImage(frame))
                gif_image.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass  # End of frames
        return frames


    def play_sound(self, file_path):
        """Play sound using pygame."""
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def show_homescreen(self):
        """Display the homescreen."""
        frame = self.homescreen_frames[self.current_frame_index]
        self.canvas.itemconfig(self.image_on_canvas, image=frame)
        self.button_mode = True
    
        # Move to the next frame or loop back to the start
        if self.current_step <= 1:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.homescreen_frames)
            self.root.after(50, self.show_homescreen)
        else:
            self.show_story1()

    def storyline_step(self):
        """Execute the current step in the storyline."""
        if self.current_step < len(self.storyline_steps):
            self.storyline_steps[self.current_step]()  # Call the function for the current step
            self.current_step += 1  # Move to the next step
            #print(self.current_step)
        else:
            self.pause_timer()
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
                if self.button_mode and serialdata == "Button":  # check button
                    self.button_press()
                if not self.button_mode and len(serialdata) == 5:  # check RFID
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

    def timer(self):
        if self.timer_status == True:
            print(self.time_left)
            """Update the countdown timer on the canvas."""
            if self.time_left > 0:
                self.time_left -= 1
                self.canvas.itemconfig(self.time_text, text=f"Time Left: {self.time_left}s")
                self.root.after(1000, self.timer)
            else:
                self.check_level_status()
        else:
            print("timer not enabled")
    
    def pause_timer(self):
        self.timer_status = False 

    def resume_timer(self):
        self.timer_status = True

    def check_level_status(self):
        """Check if the current level is complete."""
        if self.rfid_count < self.rfid_targets[self.level]:
            if self.level == 1:
                self.show_level1fail() 
            if self.level == 2:
                self.show_level2fail()
        else:
            print(f"Level {self.level} complete!")
            self.level_up()

    def level_up(self):
        """Move to the next level."""
        if self.level < 2:
            self.level += 1
            self.rfid_count = 0  # Reset RFID count for the next level
            self.pause_timer()
            print(f"Level {self.level} reached. Scanning {self.rfid_targets[self.level]} RFIDs.")
            self.root.after(3000, self.storyline_step)
        else:
            print("All levels completed.")
            #self.thankyou3()  # Show the final thank you screen
    
    def on_space_press(self, event):
        """Manual skip to the next storyline step."""
        print("Manual skip")
        self.storyline_step()





    def show_kelp1(self):
        """Display kelp image 1."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp1)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False
        

    def show_kelp2(self):
        """Display kelp image 2."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp2)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_kelp3(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp3)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_kelp4(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp4)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_kelp5(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp5)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_kelp6(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp6)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_kelp7(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp7)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_kelp8(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.kelp8)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = False

    def show_level1(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.level1)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = True

    def show_level2(self):
        """Display kelp image 3."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.level2)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = True

    def show_level1fail(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.level1fail)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = True

    def show_level2fail(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.level2fail)
        self.play_sound("sounds/villager_idle3.ogg")
        self.button_mode = True

    def show_failscreen1(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.failscreen1)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_failscreen2(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.failscreen2)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story1(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story1)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story2(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story2)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story3(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story3)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story4(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story4)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story5(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story5)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story6(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story6)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story7(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story7)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story8(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story8)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story9(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story9)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_story10(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.story10)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_instruct1(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.instruct1)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_instruct2(self):
        """Display the introduction screen."""
        self.resume_timer()
        self.time_left = 60 #time reset to 60 after each level 
        self.time_text = self.canvas.create_text(960, 960, text=f"Time Left: {self.time_left}s", font=("Comic Sans", 50), fill="magenta")
        """Display the kelp prompt."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.instruct2)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True
        self.timer()
    
    def show_instruct3(self):
        """Display the introduction screen."""
        self.canvas.itemconfig(self.image_on_canvas, image=self.instruct3)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_instruct4(self):
        """Display the introduction screen."""
        self.resume_timer()
        self.canvas.itemconfig(self.image_on_canvas, image=self.instruct4)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_fact1(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.fact1)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_fact2(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.fact2)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_fact3(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.fact3)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_fact4(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.fact4)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_fact5(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.fact5)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_fact6(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.fact6)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True

    def show_thankyou1(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.thankyou1)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True
        self.pause_timer()

    def show_thankyou2(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.thankyou2)
        self.play_sound("sounds/Villager_idle1.ogg")
        self.button_mode = True
        self.pause_timer()



# Start the application
if __name__ == "__main__":
    StorylineApp()

