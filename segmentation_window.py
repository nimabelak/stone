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
    - View an image of a stone within a fixed display area.
    - Adjust segmentation parameters in real-time using sliders.
    - Manually deselect/reselect contours by clicking on them.
    - Toggle between the boundary view and a binary mask view.
    - Save the current slider values as the new default for future sessions.
    """

    def __init__(self, master, image_path, on_delete_callback=None):
        """
        Initialize the segmentation window.
        """
        super().__init__(master)
        self.title("Stone Segmentation")
        self.geometry("1200x800")

        self.image_path = image_path
        self.on_delete_callback = on_delete_callback
        self.original_image = None
        self.processed_image = None
        self.mask = None

        # --- Contour selection variables ---
        self.all_contours = []
        self.active_contour_indices = []
        self.display_scale = 1.0
        self.display_offset_x = 0
        self.display_offset_y = 0

        self.show_mask_var = ctk.BooleanVar(value=False)

        # Default parameters for segmentation
        self.default_params_file = "segmentation_defaults.json"
        self.load_default_parameters()

        self.load_image()
        self.create_ui()
        self.update_segmentation()

        # Window properties
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_default_parameters(self):
        """Load default segmentation parameters from a JSON file."""
        # Min Contour Area is now a fixed value, not a configurable parameter.
        default_values = {
            "blur_kernel": 5,
            "threshold_value": 127,
            "erosion_iterations": 2,
            "dilation_iterations": 2,
        }
        try:
            if os.path.exists(self.default_params_file):
                with open(self.default_params_file, 'r') as f:
                    loaded_params = json.load(f)
                    # Ensure old area threshold in file doesn't cause issues
                    loaded_params.pop("contour_area_threshold", None)
                    default_values.update(loaded_params)
        except Exception as e:
            print(f"Error loading default parameters: {e}")
        self.params = default_values

    def save_default_parameters(self):
        """Save the current slider values as the new defaults."""
        try:
            # Min Contour Area is no longer saved as it's a fixed value.
            current_params = {
                "blur_kernel": self.blur_var.get(),
                "threshold_value": self.threshold_var.get(),
                "erosion_iterations": self.erosion_var.get(),
                "dilation_iterations": self.dilation_var.get(),
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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(main_frame, text="Stone Segmentation", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.create_image_display(content_frame)
        self.create_controls(content_frame)
        self.create_bottom_buttons(main_frame)

    def create_image_display(self, parent):
        """Create the image display area and bind the click event."""
        self.image_frame = ctk.CTkFrame(parent)
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.image_frame.grid_propagate(False)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self.image_frame, text="Loading...")
        self.image_label.grid(row=0, column=0, sticky="nsew")
        self.image_label.bind("<Button-1>", self.on_image_click)

    def create_controls(self, parent):
        """Create the parameter control panel on the right side."""
        controls_frame = ctk.CTkFrame(parent, width=300)
        controls_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        controls_frame.pack_propagate(False)

        controls_title = ctk.CTkLabel(controls_frame, text="Segmentation Parameters", font=ctk.CTkFont(size=16, weight="bold"))
        controls_title.pack(pady=(10, 10))

        switch_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(0, 15), padx=10)
        mask_switch = ctk.CTkSwitch(switch_frame, text="Show Mask", variable=self.show_mask_var, command=self.display_result)
        mask_switch.pack(anchor="w")

        self.create_parameter_sliders(controls_frame)

        default_btn = ctk.CTkButton(controls_frame, text="Set as Default", command=self.save_default_parameters)
        default_btn.pack(pady=20, side="bottom")

    def create_parameter_sliders(self, parent):
        """Create a set of sliders for adjusting segmentation parameters."""
        self.blur_var = ctk.DoubleVar(value=self.params["blur_kernel"])
        self.create_slider(parent, "Blur Kernel Size", self.blur_var, 1, 65, 2)
        
        self.threshold_var = ctk.DoubleVar(value=self.params["threshold_value"])
        self.create_slider(parent, "Threshold Value", self.threshold_var, 0, 255, 1)

        self.erosion_var = ctk.DoubleVar(value=self.params["erosion_iterations"])
        self.create_slider(parent, "Erosion Iterations", self.erosion_var, 0, 45, 1)
        
        self.dilation_var = ctk.DoubleVar(value=self.params["dilation_iterations"])
        self.create_slider(parent, "Dilation Iterations", self.dilation_var, 0, 45, 1)
        
        # --- Min Contour Area slider has been removed ---

    def create_slider(self, parent, label, variable, min_val, max_val, step):
        """Helper function to create a labeled slider with a value display."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5, padx=10)
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x")
        label_widget = ctk.CTkLabel(top_frame, text=label)
        label_widget.pack(side="left")

        format_str = "{:.2f}" if step < 1 else "{:.0f}"
        value_label = ctk.CTkLabel(top_frame, text=format_str.format(variable.get()))
        value_label.pack(side="right")
        
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, variable=variable, number_of_steps=int((max_val - min_val) / step))
        slider.pack(fill="x", pady=(0, 10))

        def on_slider_change(value):
            value_label.configure(text=format_str.format(float(value)))
            self.update_segmentation()
        variable.trace_add("write", lambda *args: on_slider_change(variable.get()))

    def create_bottom_buttons(self, parent):
        """Create the 'Delete Image' and 'Start' buttons at the bottom."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        delete_btn = ctk.CTkButton(button_frame, text="Delete Image", fg_color="#D83C3C", hover_color="#B63030", command=self.delete_image)
        delete_btn.pack(side="left")
        start_btn = ctk.CTkButton(button_frame, text="Start", command=self.start_next_step)
        start_btn.pack(side="right")

    def update_segmentation(self):
        """Run segmentation, reset active contours, and update the display."""
        if self.original_image is None: return
        try:
            blur_kernel = int(self.blur_var.get())
            if blur_kernel % 2 == 0: blur_kernel += 1
            
            # Get parameter values from the UI
            params = {
                "image": self.original_image,
                "blur_kernel": blur_kernel,
                "threshold_val": int(self.threshold_var.get()),
                "erosion_iter": int(self.erosion_var.get()),
                "dilation_iter": int(self.dilation_var.get()),
                "min_area": 50000  # <-- Hardcoded value as requested
            }

            self.all_contours = self.segment_stone(**params)
            self.active_contour_indices = list(range(len(self.all_contours)))
            self.generate_processed_images()
            self.display_result()
        except Exception as e:
            print(f"Error in segmentation: {e}")

    def segment_stone(self, image, blur_kernel, threshold_val, erosion_iter, dilation_iter, min_area):
        """
        Perform segmentation using area, returning filtered contours.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
        _, thresh = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY)
        kernel = np.ones((3, 3), np.uint8)
        if erosion_iter > 0: thresh = cv2.erode(thresh, kernel, iterations=erosion_iter)
        if dilation_iter > 0: thresh = cv2.dilate(thresh, kernel, iterations=dilation_iter)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by the fixed minimum area
        return [c for c in contours if cv2.contourArea(c) > min_area]

    def generate_processed_images(self):
        """Generate the mask and result image based on the currently active contours."""
        active_contours = [self.all_contours[i] for i in self.active_contour_indices]
        self.mask = np.zeros_like(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY))
        if active_contours:
            cv2.drawContours(self.mask, active_contours, -1, 255, -1)
        self.processed_image = self.original_image.copy()
        if active_contours:
            cv2.drawContours(self.processed_image, active_contours, -1, (57, 255, 20), 3)

    def on_image_click(self, event):
        """Handles clicks on the image to select/deselect contours."""
        if self.display_scale == 0: return # Avoid division by zero
        original_x = (event.x - self.display_offset_x) / self.display_scale
        original_y = (event.y - self.display_offset_y) / self.display_scale

        for i, contour in enumerate(self.all_contours):
            if cv2.pointPolygonTest(contour, (original_x, original_y), False) >= 0:
                if i in self.active_contour_indices:
                    self.active_contour_indices.remove(i)
                else:
                    self.active_contour_indices.append(i)
                self.generate_processed_images()
                self.display_result()
                break

    def display_result(self):
        """Display the result, resized to a fixed box, and store scale/offset info."""
        if self.processed_image is None or self.mask is None: return
        try:
            image_bgr = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR) if self.show_mask_var.get() else self.processed_image
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            
            MAX_WIDTH, MAX_HEIGHT = 800, 700
            img_height, img_width = image_rgb.shape[:2]

            scale = min(MAX_WIDTH / img_width, MAX_HEIGHT / img_height) if img_width > 0 and img_height > 0 else 1
            if scale > 1.0: scale = 1.0

            new_width, new_height = int(img_width * scale), int(img_height * scale)

            self.display_scale = scale
            self.display_offset_x = (self.image_frame.winfo_width() - new_width) / 2
            self.display_offset_y = (self.image_frame.winfo_height() - new_height) / 2

            pil_image = Image.fromarray(image_rgb)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))

            self.image_label.configure(image=ctk_image, text="")
            self.image_label.image = ctk_image
        except Exception as e:
            print(f"Error displaying result: {e}")

    def delete_image(self):
        if self.on_delete_callback: self.on_delete_callback()
        self.destroy()

    def start_next_step(self):
        messagebox.showinfo("Next Step", "Next step functionality will be implemented later.")

    def on_close(self):
        self.destroy()