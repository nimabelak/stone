import customtkinter as ctk
from PIL import Image
from PIL import ImageTk
import os
import cv2
import tempfile


class CameraCapture(ctk.CTkToplevel):
    """
    A camera capture window that allows users to preview, capture, retake and submit images.
    
    This class creates a toplevel window with live camera feed, capture functionality,
    and the ability to retake or submit captured images.
    
    Args:
        master: Parent window
        on_submit: Callback function to handle the submitted image path
    """
    
    def __init__(self, master, on_submit):
        """
        Initialize the camera capture window.
        
        Args:
            master: Parent window
            on_submit: Callback function called when image is submitted
        """
        super().__init__(master)
        self.title("Camera")
        self.geometry("700x560")
        self.on_submit = on_submit

        # Create label to display camera feed or status messages
        self.frame_label = ctk.CTkLabel(self, text="Loading camera…")
        self.frame_label.pack(pady=10)

        # Create button bar with capture, retake, and submit buttons
        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(pady=8)
        
        # Capture button - takes a snapshot of current camera feed
        self.capture_btn = ctk.CTkButton(btn_bar, text="Capture", command=self.capture_frame)
        self.capture_btn.grid(row=0, column=0, padx=4)
        
        # Retake button - allows user to retake the photo (initially disabled)
        self.retake_btn = ctk.CTkButton(btn_bar, text="Retake", state="disabled", command=self.retake)
        self.retake_btn.grid(row=0, column=1, padx=4)
        
        # Submit button - submits the captured image (initially disabled)
        self.submit_btn = ctk.CTkButton(btn_bar, text="Submit", state="disabled", command=self.submit)
        self.submit_btn.grid(row=0, column=2, padx=4)

        # Initialize camera capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.frame_label.configure(text="Could not open webcam.")
            return

        # Initialize camera state variables
        self.captured_frame = None  # Stores the captured frame
        self.streaming = True       # Controls whether camera is streaming
        
        # Start the camera stream update loop
        self.after(15, self._update_stream)
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Set the window to the top of the screen
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    def _update_stream(self):
        """
        Update the camera stream display.
        
        This method runs continuously to update the live camera feed.
        It reads frames from the camera and displays them in the label.
        """
        if self.streaming:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB for PIL compatibility
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image and resize for display
                img_pil = Image.fromarray(frame_rgb).resize((640, 480))
                # Convert to PhotoImage for tkinter display
                self._tk_img = ImageTk.PhotoImage(img_pil)
                # Update the label with the new frame
                self.frame_label.configure(image=self._tk_img, text="")
        
        # Schedule next update if window still exists
        if self.winfo_exists():
            self.after(15, self._update_stream)

    def capture_frame(self):
        """
        Capture the current camera frame.
        
        This method captures the current frame, stops streaming,
        and enables the retake and submit buttons.
        """
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # Store the captured frame
        self.captured_frame = frame.copy()
        # Stop streaming to freeze the display
        self.streaming = False

        # Display the captured frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb).resize((640, 480))
        self._tk_img = ImageTk.PhotoImage(img_pil)
        self.frame_label.configure(image=self._tk_img)

        # Update button states
        self.capture_btn.configure(state="disabled")
        self.retake_btn.configure(state="normal")
        self.submit_btn.configure(state="normal")

    def retake(self):
        """
        Allow user to retake the photo.
        
        This method clears the captured frame, resumes streaming,
        and resets button states to allow capturing again.
        """
        self.captured_frame = None
        self.streaming = True
        
        # Reset button states
        self.capture_btn.configure(state="normal")
        self.retake_btn.configure(state="disabled")
        self.submit_btn.configure(state="disabled")

    def submit(self):
        """
        Submit the captured image.
        
        This method saves the captured frame to a temporary file
        and calls the callback function with the file path.
        """
        if self.captured_frame is None:
            return
            
        # Save captured frame to temporary file
        tmp_path = os.path.join(tempfile.gettempdir(), "captured_image.png")
        cv2.imwrite(tmp_path, self.captured_frame)
        
        # Call the callback function with the image path
        self.on_submit(tmp_path)
        
        # Close the camera window
        self._on_close()

    def _on_close(self):
        """
        Handle window close event.
        
        This method properly releases the camera resource
        and destroys the window.
        """
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.destroy()