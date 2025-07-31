import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import os
from tkinter import messagebox


class SegmentationWindow(ctk.CTkToplevel):
    """
    Segmentation window for stone boundary extraction and parameter adjustment.
    
    This window provides tools for:
    - Automatic stone boundary detection
    - Real-time parameter adjustment via sliders
    - Live preview of segmentation results
    - Saving default parameters
    """
    
    def __init__(self, master, image_path, on_delete_callback=None):
        """
        Initialize the segmentation window.
        
        Args:
            master: Parent window
            image_path: Path to the image to process
            on_delete_callback: Callback function when "Delete Image" is clicked
        """
        super().__init__(master)
        self.title("Stone Segmentation")
        self.geometry("1200x800")
        
        self.image_path = image_path
        self.on_delete_callback = on_delete_callback
        self.original_image = None
        self.processed_image = None
        self.mask = None
        
        # Default parameters for segmentation
        self.default_params_file = "segmentation_defaults.json"
        self.load_default_parameters()
        
        # Load and prepare the image
        self.load_image()
        
        # Create the UI
        self.create_ui()
        
        # Initial segmentation
        self.update_segmentation()
        
        # Window properties
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_default_parameters(self):
        """Load default segmentation parameters from file or set defaults."""
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
        """Save current parameters as defaults."""
        try:
            current_params = {
                "blur_kernel": self.blur_var.get(),
                "threshold_value": self.threshold_var.get(),
                "erosion_iterations": self.erosion_var.get(),
                "dilation_iterations": self.dilation_var.get(),
                "contour_area_threshold": self.area_var.get()
            }
            
            with open(self.default_params_file, 'w') as f:
                json.dump(current_params, f, indent=2)
            
            messagebox.showinfo("Success", "Default parameters saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save parameters: {e}")

    def load_image(self):
        """Load and prepare the image for processing."""
        try:
            # Load image using OpenCV
            self.original_image = cv2.imread(self.image_path)
            if self.original_image is None:
                raise ValueError("Could not load image")
            
            # Convert BGR to RGB for display
            self.original_image_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.destroy()

    def create_ui(self):
        """Create the user interface."""
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
        image_frame = ctk.CTkFrame(parent)
        image_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Image display label
        self.image_label = ctk.CTkLabel(image_frame, text="Loading...")
        self.image_label.pack(pady=20, expand=True)

    def create_controls(self, parent):
        """Create the parameter control panel."""
        controls_frame = ctk.CTkFrame(parent, width=300)
        controls_frame.pack(side="right", fill="y", padx=(10, 0))
        controls_frame.pack_propagate(False)
        
        # Controls title
        controls_title = ctk.CTkLabel(controls_frame, text="Segmentation Parameters", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        controls_title.pack(pady=(10, 20))
        
        # Create parameter sliders
        self.create_parameter_sliders(controls_frame)
        
        # Set as Default button
        default_btn = ctk.CTkButton(controls_frame, text="Set as Default", 
                                   command=self.save_default_parameters)
        default_btn.pack(pady=20)

    def create_parameter_sliders(self, parent):
        """Create sliders for adjusting segmentation parameters."""
        # Blur Kernel Size
        self.blur_var = ctk.DoubleVar(value=self.params["blur_kernel"])
        self.create_slider(parent, "Blur Kernel Size", self.blur_var, 1, 15, 2)
        
        # Threshold Value
        self.threshold_var = ctk.DoubleVar(value=self.params["threshold_value"])
        self.create_slider(parent, "Threshold Value", self.threshold_var, 0, 255, 1)
        
        # Erosion Iterations
        self.erosion_var = ctk.DoubleVar(value=self.params["erosion_iterations"])
        self.create_slider(parent, "Erosion Iterations", self.erosion_var, 0, 10, 1)
        
        # Dilation Iterations
        self.dilation_var = ctk.DoubleVar(value=self.params["dilation_iterations"])
        self.create_slider(parent, "Dilation Iterations", self.dilation_var, 0, 10, 1)
        
        # Contour Area Threshold
        self.area_var = ctk.DoubleVar(value=self.params["contour_area_threshold"])
        self.create_slider(parent, "Min Contour Area", self.area_var, 100, 10000, 100)

    def create_slider(self, parent, label, variable, min_val, max_val, step):
        """Create a labeled slider with value display."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        # Label
        label_widget = ctk.CTkLabel(frame, text=label)
        label_widget.pack(anchor="w")
        
        # Value display
        value_label = ctk.CTkLabel(frame, text=f"{variable.get():.0f}")
        value_label.pack(anchor="e")
        
        # Slider
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, 
                              variable=variable, number_of_steps=int((max_val-min_val)/step))
        slider.pack(fill="x", pady=(5, 10))
        
        # Update value display and segmentation when slider changes
        def on_slider_change(value):
            value_label.configure(text=f"{value:.0f}")
            self.update_segmentation()
        
        variable.trace_add("write", lambda *args: on_slider_change(variable.get()))

    def create_bottom_buttons(self, parent):
        """Create bottom navigation buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Delete Image button
        delete_btn = ctk.CTkButton(button_frame, text="Delete Image", 
                                  fg_color="#D83C3C", hover_color="#B63030",
                                  command=self.delete_image)
        delete_btn.pack(side="left", padx=(0, 10))
        
        # Start button (placeholder for next step)
        start_btn = ctk.CTkButton(button_frame, text="Start", 
                                 command=self.start_next_step)
        start_btn.pack(side="right")

    def update_segmentation(self):
        """Update the segmentation based on current parameters."""
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
        Perform stone segmentation using computer vision techniques.
        
        Returns:
            mask: Binary mask of the stone
            result_image: Processed image with stone highlighted
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
        
        # Apply threshold
        _, thresh = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY)
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        
        # Erosion
        if erosion_iter > 0:
            thresh = cv2.erode(thresh, kernel, iterations=erosion_iter)
        
        # Dilation
        if dilation_iter > 0:
            thresh = cv2.dilate(thresh, kernel, iterations=dilation_iter)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # Create mask
        mask = np.zeros_like(gray)
        if filtered_contours:
            cv2.drawContours(mask, filtered_contours, -1, 255, -1)
        
        # Create result image
        result = image.copy()
        
        # Highlight the stone boundaries
        if filtered_contours:
            cv2.drawContours(result, filtered_contours, -1, (0, 255, 0), 2)
        
        return mask, result

    def display_result(self):
        """Display the segmentation result."""
        if self.processed_image is None:
            return
        
        try:
            # Convert BGR to RGB
            result_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            height, width = result_rgb.shape[:2]
            max_size = 500
            
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
            
            resized = cv2.resize(result_rgb, (new_width, new_height))
            
            # Convert to PIL Image and then to PhotoImage
            pil_image = Image.fromarray(resized)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update the label
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error displaying result: {e}")

    def delete_image(self):
        """Handle delete image button click."""
        if self.on_delete_callback:
            self.on_delete_callback()
        self.destroy()

    def start_next_step(self):
        """Handle start button click (placeholder for next step)."""
        messagebox.showinfo("Next Step", "Next step functionality will be implemented later.")

    def on_close(self):
        """Handle window close event."""
        self.destroy()
