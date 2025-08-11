import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import os
from tkinter import messagebox


class SegmentationWindow(ctk.CTkToplevel):
    """
    A window for interactive image segmentation to define stone boundaries.

    This window allows users to:
    - View an image of a stone.
    - Adjust segmentation parameters in real-time using sliders.
    - See the resulting stone boundary updated live.
    - Toggle between the boundary view and a binary mask view.
    - Save the current slider values as the new default for future sessions.
    - Delete the image and return to the main selection screen.
    """

    def __init__(self, master, image_path, on_delete_callback=None):
        """
        Initialize the segmentation window.

        Args:
            master: The parent widget (main application window).
            image_path (str): The file path of the image to be processed.
            on_delete_callback (callable, optional): A function to call when the image is deleted.
        """
        super().__init__(master)
        self.title("Stone Segmentation")
        self.geometry("1200x800")

        self.image_path = image_path
        self.on_delete_callback = on_delete_callback
        self.original_image = None
        self.processed_image = None
        self.mask = None

        # --- State variable for the new "Show Mask" switch ---
        self.show_mask_var = ctk.BooleanVar(value=False)

        # Default parameters for segmentation
        self.default_params_file = "segmentation_defaults.json"
        self.load_default_parameters()

        # Load and prepare the image
        self.load_image()

        # Create the UI
        self.create_ui()

        # Initial segmentation is triggered by the window configure event
        # to ensure widgets have dimensions.
        self.bind("<Configure>", self.on_window_configure)

        # Window properties
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_default_parameters(self):
        """Load default segmentation parameters from a JSON file or set hardcoded defaults."""
        default_values = {
            "blur_kernel": 5,
            "threshold_value": 127,
            "erosion_iterations": 2,
            "dilation_iterations": 2,
            "contour_area_threshold": 1000
        }

        try:
            if os.path.exists(self.default_params_file):
                with open(self.default_params_file, 'r') as f:
                    loaded_params = json.load(f)
                    # Update defaults with loaded values
                    default_values.update(loaded_params)
        except Exception as e:
            print(f"Error loading default parameters: {e}")

        self.params = default_values

    def save_default_parameters(self):
        """Save the current slider values as the new defaults in the JSON file."""
        try:
            current_params = {
                "blur_kernel": self.blur_var.get(),
                "threshold_value": self.threshold_var.get(),
                "erosion_iterations": self.erosion_var.get(),
                "dilation_iterations": self.dilation_var.get(),
                "contour_area_threshold": self.area_var.get()
            }

            with open(self.default_params_file, 'w') as f:
                json.dump(current_params, f, indent=4)

            messagebox.showinfo("Success", "Default parameters saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save parameters: {e}")

    def load_image(self):
        """Load the image from the specified path using OpenCV."""
        try:
            self.original_image = cv2.imread(self.image_path)
            if self.original_image is None:
                raise ValueError(f"Could not load image from path: {self.image_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.destroy()

    def create_ui(self):
        """Create the main user interface layout."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(main_frame, text="Stone Segmentation",
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 10))

        # Content frame (horizontal layout)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Left side - Image display
        self.create_image_display(content_frame)

        # Right side - Controls
        self.create_controls(content_frame)

        # Bottom buttons
        self.create_bottom_buttons(main_frame)

    def create_image_display(self, parent):
        """Create the image display area."""
        self.image_frame = ctk.CTkFrame(parent)
        self.image_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Image display label
        self.image_label = ctk.CTkLabel(self.image_frame, text="Loading...")
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

    def create_controls(self, parent):
        """Create the parameter control panel on the right side."""
        controls_frame = ctk.CTkFrame(parent, width=300)
        controls_frame.pack(side="right", fill="y", padx=(10, 0))
        controls_frame.pack_propagate(False)

        # Controls title
        controls_title = ctk.CTkLabel(controls_frame, text="Segmentation Parameters",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        controls_title.pack(pady=(10, 10))

        # --- "Show Mask" Switch ---
        switch_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(0, 15), padx=10)
        mask_switch = ctk.CTkSwitch(
            switch_frame,
            text="Show Mask",
            variable=self.show_mask_var,
            command=self.display_result  # Update view when toggled
        )
        mask_switch.pack(anchor="w")

        # Create parameter sliders
        self.create_parameter_sliders(controls_frame)

        # Set as Default button
        default_btn = ctk.CTkButton(controls_frame, text="Set as Default",
                                    command=self.save_default_parameters)
        default_btn.pack(pady=20, side="bottom")

    def create_parameter_sliders(self, parent):
        """Create a set of sliders for adjusting segmentation parameters."""
        # Blur Kernel Size
        self.blur_var = ctk.DoubleVar(value=self.params["blur_kernel"])
        self.create_slider(parent, "Blur Kernel Size", self.blur_var, 1, 65, 2)

        # Threshold Value
        self.threshold_var = ctk.DoubleVar(value=self.params["threshold_value"])
        self.create_slider(parent, "Threshold Value", self.threshold_var, 0, 255, 1)

        # Erosion Iterations
        self.erosion_var = ctk.DoubleVar(value=self.params["erosion_iterations"])
        self.create_slider(parent, "Erosion Iterations", self.erosion_var, 0, 45, 1)

        # Dilation Iterations
        self.dilation_var = ctk.DoubleVar(value=self.params["dilation_iterations"])
        self.create_slider(parent, "Dilation Iterations", self.dilation_var, 0, 45, 1)

        # Contour Area Threshold
        self.area_var = ctk.DoubleVar(value=self.params["contour_area_threshold"])
        self.create_slider(parent, "Min Contour Area", self.area_var, 100, 50000, 100)

    def create_slider(self, parent, label, variable, min_val, max_val, step):
        """Helper function to create a labeled slider with a value display."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5, padx=40)

        # Top row for label and value
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x")

        # Label
        label_widget = ctk.CTkLabel(top_frame, text=label)
        label_widget.pack(side="left")

        # Value display
        value_label = ctk.CTkLabel(top_frame, text=f"{variable.get():.0f}")
        value_label.pack(side="right")

        # Slider
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val,
                               variable=variable, number_of_steps=int((max_val - min_val) / step))
        slider.pack(fill="x", pady=(0, 10))

        # Update value display and segmentation when slider changes
        def on_slider_change(value):
            value_label.configure(text=f"{float(value):.0f}")
            self.update_segmentation()

        variable.trace_add("write", lambda *args: on_slider_change(variable.get()))

    def create_bottom_buttons(self, parent):
        """Create the 'Delete Image' and 'Start' buttons at the bottom."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        # Delete Image button
        delete_btn = ctk.CTkButton(button_frame, text="Delete Image",
                                   fg_color="#D83C3C", hover_color="#B63030",
                                   command=self.delete_image)
        delete_btn.pack(side="left")

        # Start button (placeholder for next step)
        start_btn = ctk.CTkButton(button_frame, text="Start",
                                  command=self.start_next_step)
        start_btn.pack(side="right")

    def on_window_configure(self, event=None):
        """Handle window resize events to re-render the image."""
        # This is called once on startup and on every resize.
        # We unbind to prevent it from firing excessively, then re-bind after a delay.
        self.unbind("<Configure>")
        self.update_segmentation()
        self.after(100, lambda: self.bind("<Configure>", self.on_window_configure))

    def update_segmentation(self):
        """Run the segmentation algorithm with the current parameters and display the result."""
        if self.original_image is None:
            return

        try:
            # Get current parameter values
            blur_kernel = int(self.blur_var.get())
            threshold_val = int(self.threshold_var.get())
            erosion_iter = int(self.erosion_var.get())
            dilation_iter = int(self.dilation_var.get())
            min_area = int(self.area_var.get())

            # Ensure blur kernel is odd
            if blur_kernel % 2 == 0:
                blur_kernel += 1

            # Process the image
            self.mask, self.processed_image = self.segment_stone(
                self.original_image, blur_kernel, threshold_val,
                erosion_iter, dilation_iter, min_area
            )

            # Display the result
            self.display_result()

        except Exception as e:
            print(f"Error in segmentation: {e}")

    def segment_stone(self, image, blur_kernel, threshold_val, erosion_iter, dilation_iter, min_area):
        """
        Perform stone segmentation using a series of computer vision operations.

        Returns:
            tuple: A tuple containing:
                - mask (np.array): Binary mask of the stone (white on black).
                - result_image (np.array): Original image with the stone boundary highlighted.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)

        # Apply binary threshold
        _, thresh = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY)

        # Morphological operations to clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        if erosion_iter > 0:
            thresh = cv2.erode(thresh, kernel, iterations=erosion_iter)
        if dilation_iter > 0:
            thresh = cv2.dilate(thresh, kernel, iterations=dilation_iter)

        # Find contours of the objects
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area to remove small noise
        filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]

        # Create the final mask
        mask = np.zeros_like(gray)
        if filtered_contours:
            cv2.drawContours(mask, filtered_contours, -1, 255, -1) # -1 fills the contour

        # Create result image with highlighted boundaries
        result = image.copy()
        if filtered_contours:
            # --- Use a brighter, thicker line for the boundary ---
            cv2.drawContours(result, filtered_contours, -1, (57, 255, 20), 3)

        return mask, result

    def display_result(self):
        """
        Display the segmentation result (either boundary or mask) in the image label.
        The image is resized to fit the available space in the UI.
        """
        if self.processed_image is None or self.mask is None:
            return

        try:
            # --- Decide which image to display based on the switch ---
            if self.show_mask_var.get():
                # If showing mask, convert the single-channel mask to a 3-channel BGR image
                image_to_display_bgr = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
            else:
                # Otherwise, show the processed image with the boundary
                image_to_display_bgr = self.processed_image

            # Convert from OpenCV's BGR to PIL's RGB format
            image_rgb = cv2.cvtColor(image_to_display_bgr, cv2.COLOR_BGR2RGB)

            # --- Resize image to fit the display frame dynamically ---
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
            
            if frame_width < 50 or frame_height < 50: # Avoid division by zero on startup
                return

            img_height, img_width = image_rgb.shape[:2]

            # Calculate scaling factor to maintain aspect ratio
            scale = min(frame_width / img_width, frame_height / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            # Create a CTkImage from the resized PIL image
            pil_image = Image.fromarray(image_rgb)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))

            # Update the label
            self.image_label.configure(image=ctk_image, text="")
            self.image_label.image = ctk_image  # Keep a reference to prevent garbage collection

        except Exception as e:
            print(f"Error displaying result: {e}")
            # This can happen if the window is closed while processing
            pass

    def delete_image(self):
        """Handle the 'Delete Image' button click."""
        if self.on_delete_callback:
            self.on_delete_callback()
        self.destroy()

    def start_next_step(self):
        """Handle the 'Start' button click (placeholder for future functionality)."""
        messagebox.showinfo("Next Step", "Next step functionality will be implemented later.")

    def on_close(self):
        """Handle the window close event."""
        self.destroy()
