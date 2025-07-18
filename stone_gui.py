import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import os
import cv2
import tempfile
from customtkinter import CTkImage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

drop_image = Image.open("drop_image.png")

import ctypes
try:
    # Windows 10 build 19045 compatibility
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass


# Webcam Capture Window
class CameraCapture(ctk.CTkToplevel):
    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Camera")
        self.geometry("700x560")
        self.on_submit = on_submit

        #Set the frame in which camera feed is shown.
        self.frame_label = ctk.CTkLabel(self, text="Loading camera…")
        self.frame_label.pack(pady=10)

        # Create button bar for capture, retake, and submit buttons.
        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(pady=8)
        self.capture_btn = ctk.CTkButton(btn_bar, text="Capture", command=self.capture_frame)
        self.capture_btn.grid(row=0, column=0, padx=4)
        self.retake_btn = ctk.CTkButton(btn_bar, text="Retake", state="disabled", command=self.retake)
        self.retake_btn.grid(row=0, column=1, padx=4)
        self.submit_btn = ctk.CTkButton(btn_bar, text="Submit", state="disabled", command=self.submit)
        self.submit_btn.grid(row=0, column=2, padx=4)

        # Open the webcam. If it fails, display an error message. Otherwise, start streaming.
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.frame_label.configure(text="Could not open webcam.")
            return

        # Initialize variables for captured frame and streaming state.
        self.captured_frame = None
        self.streaming = True
        self.after(15, self._update_stream)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Set the window to the top of the screen. This is to ensure that the webcam feed is visible.        
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    # Update the camera feed.
    def _update_stream(self):
        if self.streaming:
            ret, frame = self.cap.read()
            if ret:
                # Convert the Frame for Display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(frame_rgb).resize((640, 480))
                self._tk_img = ImageTk.PhotoImage(img_pil)
                self.frame_label.configure(image=self._tk_img, text="")
        if self.winfo_exists():
            self.after(15, self._update_stream)

    # Capture the current frame from the webcam and stop streamning.
    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        self.captured_frame = frame.copy()
        self.streaming = False

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb).resize((640, 480))
        self._tk_img = ImageTk.PhotoImage(img_pil)
        self.frame_label.configure(image=self._tk_img)

        self.capture_btn.configure(state="disabled")
        self.retake_btn.configure(state="normal")
        self.submit_btn.configure(state="normal")

    # Reset the captured frame and start streaming.
    def retake(self):
        self.captured_frame = None
        self.streaming = True
        self.capture_btn.configure(state="normal")
        self.retake_btn.configure(state="disabled")
        self.submit_btn.configure(state="disabled")

    # Save the captured frame to a temporary file and call the on_submit callback. Then close the window.    
    def submit(self):
        if self.captured_frame is None:
            return
        tmp_path = os.path.join(tempfile.gettempdir(), "captured_image.png")
        cv2.imwrite(tmp_path, self.captured_frame)
        self.on_submit(tmp_path)
        self._on_close()

    def _on_close(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.destroy()
    


# Image Browse / Drag and Drop Window
class ImageSelectWindow(ctk.CTkToplevel):
    def __init__(self, master, on_submit_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("1000x600")
        self.title("Select an Image")
        self.dialog_open = False
        self.on_submit_callback = on_submit_callback
        

        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=950, height=550 , bg_color="#fff")
        self.scrollable_frame.pack(fill="both", expand=True)

        # Create a dashed drag and drop frame with an icon and 2 buttons (Browse and Camera)
        self.canvas = ctk.CTkCanvas(self.scrollable_frame, width=450, height=200, highlightthickness=4, highlightbackground="gray")
        self.canvas.pack(pady=40)
        self.canvas.configure(bg=self._apply_appearance_mode(self._fg_color))
        self.canvas.create_rectangle(10, 10, 450, 200, dash=(6, 4), outline="#888", width=2)

        self.drop_frame = ctk.CTkFrame(self.canvas, fg_color="transparent", width=420, height=180)
        self.canvas.create_window(225, 100, window=self.drop_frame)

        self.my_image = ctk.CTkImage(light_image=drop_image, dark_image=drop_image, size=(60, 60))

        self.drop_image_label = ctk.CTkLabel(self.drop_frame, image=self.my_image, text="")
        self.drop_image_label.pack(pady=(20, 5))

        self.text_label = ctk.CTkLabel(self.drop_frame, text="Drop your Image here", text_color="#888")
        self.text_label.pack(pady=(5, 10))

        button_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        button_frame.pack(pady=(5, 10))

        self.browse_button = ctk.CTkButton(button_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=0, padx=6)

        self.camera_button = ctk.CTkButton(button_frame, text="Camera", command=self.open_camera)
        self.camera_button.grid(row=0, column=1, padx=6)

        # Register the drop frame for drag and drop (using tkinterdnd2)
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.on_drop)

        self.selected_image = ctk.CTkLabel(self.scrollable_frame, text="")
        self.selected_image.pack(pady=1)

        
        self.image_control_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.image_control_frame.pack(pady=5)
        self.image_control_frame.pack_forget()

        self.delete_btn = ctk.CTkButton(self.image_control_frame, text="Delete", fg_color="#D83C3C", command=self.clear_image)
        self.submit_btn = ctk.CTkButton(self.image_control_frame, text="Submit", command=self.submit_image)

        self.delete_btn.pack(side="left", padx=10)
        self.submit_btn.pack(side="left", padx=10)

        # Set the window to the top of the screen. This is to ensure that the webcam feed is visible.        
        self.set_window_on_top()
        self.current_image_path = None

    # Browse for an image file (supports multiple image formats)
    def browse_file(self):
        if not self.dialog_open:
            self.dialog_open = True
            self.browse_button.configure(state="disabled")
            try:
                file_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
                )
                if file_path:
                    self.show_image(file_path)
            finally:
                self.dialog_open = False
                self.browse_button.configure(state="normal")

    # Open the camera window for capturing an image.    
    def open_camera(self):
        CameraCapture(self, self.show_image)

    # Handle the drop event for drag and drop
    def on_drop(self, event):
        # Close any open dialog
        if self.dialog_open:
            self.dialog_open = False
            self.browse_button.configure(state="normal")
        
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.show_image(file_path)

    # Show the selected image in the window
    def show_image(self, path):
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            img = Image.open(path)
            img.thumbnail((800, 800))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)

            self.selected_image.configure(image=ctk_img, text="")
            self.selected_image.image = ctk_img
            self.current_image_path = path
            self.image_control_frame.pack(pady=5)
        else:
            self.selected_image.configure(text="Invalid image format", image="")
            self.selected_image.image = None
            self.image_control_frame.pack_forget()

    def clear_image(self):
        self.selected_image.configure(image="", text="")
        self.selected_image.image = None
        self.current_image_path = None
        self.image_control_frame.pack_forget()

    def submit_image(self):
        if self.current_image_path:
            self.on_submit_callback(self.current_image_path)
            self.destroy()

    def set_window_on_top(self):
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

# Main Application Window
class App(TkinterDnD.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x600")
        self.title("Stone App")
        self.image_select_window = None
        self.current_image_path = None

        # button to open the image select window. This button is used to select an image from file system or camera(webcam)       
        self.button_1 = ctk.CTkButton(self, text="Open Select Image Window", command=self.open_toplevel)
        self.button_1.pack(pady=20)

        # Main Image Display
        self.main_image = ctk.CTkLabel(self, text="")
        self.main_image.pack(pady=10)

        # Main Buttons Frame
        self.main_buttons = ctk.CTkFrame(self, fg_color="transparent")
        self.start_btn = ctk.CTkButton(self.main_buttons, text="Start Processing", command=self.start_processing)
        self.delete_btn = ctk.CTkButton(self.main_buttons, text="Delete", fg_color="#D83C3C", hover_color="#B63030", command=self.clear_main_image)

    # Open the image select window if it does not exist or is closed. Otherwise, focus on the existing window.    
    def open_toplevel(self):
        if self.image_select_window is None or not self.image_select_window.winfo_exists():
            self.image_select_window = ImageSelectWindow(self, self.display_main_image)
            self.image_select_window.focus()
        else:
            self.image_select_window.focus()

    # Display the selected image in the main window.
    def display_main_image(self, path):
        img = Image.open(path)
        img.thumbnail((500, 500))
        ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)
        self.main_image.configure(image=ctk_img, text="")
        self.main_image.image = ctk_img
        self.current_image_path = path
        self.main_buttons.pack(pady=10)
        self.start_btn.pack(side="left", padx=10)
        self.delete_btn.pack(side="left", padx=10)

    #dummy function for start_processing button
    def start_processing(self):
        print("Processing started...")

    # Clear the main image and hide the main buttons.
    def clear_main_image(self):
        self.main_image.configure(image="", text="")
        self.main_image.image = None
        self.current_image_path = None
        self.main_buttons.pack_forget()

if __name__ == "__main__":
    app = App()
    app.mainloop()
