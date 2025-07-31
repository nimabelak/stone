import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
from PIL import Image
import os
from customtkinter import CTkImage
from cameraCapture import CameraCapture
from segmentation_window import SegmentationWindow

# Set the appearance mode and color theme for the application
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Load the drop image icon used in the drag-and-drop area
drop_image = Image.open("drop_image.png")

import ctypes
try:
    # Windows 10 build 19045 compatibility
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass



class App(TkinterDnD.Tk):
    """
    Main application window that combines image selection and processing functionality.
    
    This is the primary application window that provides all functionality in a single interface:
    - Image selection via drag-and-drop, file browser, or camera
    - Image preview and processing controls
    - Integrated workflow without separate windows
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the main application window with integrated image selection.
        """
        super().__init__(*args, **kwargs)
        self.geometry("1000x800")
        self.title("Stone App")
        
        # Initialize state variables
        self.dialog_open = False
        self.current_image_path = None

        # Create main scrollable container
        self.main_frame = ctk.CTkScrollableFrame(self, width=950, height=750)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title label
        self.title_label = ctk.CTkLabel(self.main_frame, text="Stone App", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(0, 20))

        # Create drag-and-drop area
        self.create_drop_zone()

        # Selected image display area
        self.selected_image = ctk.CTkLabel(self.main_frame, text="")
        self.selected_image.pack(pady=20)

        # Image control buttons (initially hidden)
        self.image_control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.image_control_frame.pack(pady=10)
        self.image_control_frame.pack_forget()

        # Delete button - removes selected image
        self.delete_btn = ctk.CTkButton(self.image_control_frame, text="Delete", 
                                       fg_color="#D83C3C", hover_color="#B63030", 
                                       command=self.clear_image)
        self.delete_btn.pack(side="left", padx=10)

        # Start processing button
        self.start_btn = ctk.CTkButton(self.image_control_frame, text="Start Processing", 
                                      command=self.start_processing)
        self.start_btn.pack(side="left", padx=10)

    def create_drop_zone(self):
        """
        Create the drag-and-drop zone with browse and camera buttons.
        """
        # Create canvas for drag-and-drop area with dashed border
        self.canvas = ctk.CTkCanvas(self.main_frame, width=600, height=300, 
                                   highlightthickness=4, highlightbackground="gray")
        self.canvas.pack(pady=40)
        self.canvas.configure(bg="#212121" if ctk.get_appearance_mode() == "Dark" else "#EBEBEB")
        
        # Draw dashed rectangle border
        self.canvas.create_rectangle(10, 10, 600, 300, dash=(6, 4), outline="#888", width=2)

        # Create frame inside canvas for drop zone content
        self.drop_frame = ctk.CTkFrame(self.canvas, fg_color="transparent", width=580, height=280)
        self.canvas.create_window(300, 150, window=self.drop_frame)

        # Create and configure drop zone image icon
        self.my_image = ctk.CTkImage(light_image=drop_image, dark_image=drop_image, size=(60, 60))

        # Drop zone image label
        self.drop_image_label = ctk.CTkLabel(self.drop_frame, image=self.my_image, text="")
        self.drop_image_label.pack(pady=(20, 5))


        # Button frame for Browse and Camera buttons
        button_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        button_frame.pack(pady=(5, 10))

        # Browse button - opens file dialog
        self.browse_button = ctk.CTkButton(button_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=0, padx=6)

        # Camera button - opens camera capture window
        self.camera_button = ctk.CTkButton(button_frame, text="Camera", command=self.open_camera)
        self.camera_button.grid(row=0, column=1, padx=6)

        # Register drag-and-drop functionality
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.on_drop)

    def browse_file(self):
        """
        Open file browser dialog to select an image.
        
        This method opens a file dialog for image selection,
        prevents multiple dialogs from opening simultaneously,
        and handles the selected file.
        """
        if not self.dialog_open:
            self.dialog_open = True
            self.browse_button.configure(state="disabled")
            try:
                # Open file dialog with image file filters
                file_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
                )
                if file_path:
                    self.show_image(file_path)
            finally:
                # Reset dialog state regardless of outcome
                self.dialog_open = False
                self.browse_button.configure(state="normal")

    def open_camera(self):
        """
        Open the camera capture window.
        
        This method creates a new CameraCapture window and passes
        the show_image method as the callback for captured images.
        """
        CameraCapture(self, self.show_image)

    def on_drop(self, event):
        """
        Handle drag-and-drop events.
        
        This method processes files dropped onto the drop zone,
        closes any open dialogs, and displays the dropped image.
        
        Args:
            event: Drop event containing file data
        """
        # Close any open dialog
        if self.dialog_open:
            self.dialog_open = False
            self.browse_button.configure(state="normal")
        
        # Extract file path from drop event
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.show_image(file_path)

    def show_image(self, path):
        """
        Display the selected image in the main window.
        
        This method loads and displays an image, validates the file format,
        and shows/hides the control buttons accordingly.
        
        Args:
            path: File path of the image to display
        """
        # Check if file has valid image extension
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            # Load and resize image
            img = Image.open(path)
            img.thumbnail((600, 600))  # Resize to fit display
            ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)

            # Display image in label
            self.selected_image.configure(image=ctk_img, text="")
            self.selected_image.image = ctk_img  # Keep reference to prevent garbage collection
            self.current_image_path = path
            
            # Show control buttons
            self.image_control_frame.pack(pady=10)
        else:
            # Display error message for invalid format
            self.selected_image.configure(text="Invalid image format", image="")
            self.selected_image.image = None
            # Hide control buttons
            self.image_control_frame.pack_forget()

    def clear_image(self):
        """
        Clear the currently displayed image.
        
        This method removes the displayed image, clears the image path,
        and hides the control buttons.
        """
        self.selected_image.configure(image="", text="")
        self.selected_image.image = None
        self.current_image_path = None
        self.image_control_frame.pack_forget()

    def start_processing(self):
        """
        Start the image processing workflow.

        Opens the segmentation window for stone boundary extraction.
        """
        if self.current_image_path:
            # Open the segmentation window
            segmentation_window = SegmentationWindow(
                self,
                self.current_image_path,
                on_delete_callback=self.clear_image
            )
        else:
            # Show error if no image is selected
            import tkinter.messagebox as messagebox
            messagebox.showerror("No Image", "Please select an image first.")


if __name__ == "__main__":
    """
    Application entry point.
    
    Creates and runs the main application window.
    """
    app = App()
    app.mainloop()
