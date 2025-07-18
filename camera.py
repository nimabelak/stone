import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import tempfile
import cv2
from customtkinter import CTkImage
from CTkMessagebox import CTkMessagebox  # <-- separate pip package: pip install CTkMessagebox


class CameraCapture(ctk.CTkToplevel):
    """A simple webcam capture window that lets the user
    preview, capture, retake and finally submit an image back to the caller."""

    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Camera")
        self.geometry("700x560")
        self.on_submit = on_submit

        # --- UI widgets --------------------------------------------------
        self.frame_label = ctk.CTkLabel(self, text="Loading camera…")
        self.frame_label.pack(pady=10)

        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(pady=8)
        self.capture_btn = ctk.CTkButton(btn_bar, text="Capture", command=self.capture_frame)
        self.capture_btn.grid(row=0, column=0, padx=4)
        self.retake_btn = ctk.CTkButton(btn_bar, text="Retake", state="disabled", command=self.retake)
        self.retake_btn.grid(row=0, column=1, padx=4)
        self.submit_btn = ctk.CTkButton(btn_bar, text="Submit", state="disabled", command=self.submit)
        self.submit_btn.grid(row=0, column=2, padx=4)

        # --- Camera ------------------------------------------------------
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.frame_label.configure(text="Could not open webcam :(")
            return

        self.captured_frame = None
        self.streaming = True
        self.after(15, self._update_stream)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _update_stream(self):
        if self.streaming:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(frame_rgb).resize((640, 480))
                self._tk_img = ImageTk.PhotoImage(img_pil)
                self.frame_label.configure(image=self._tk_img, text="")
        if self.winfo_exists():
            self.after(15, self._update_stream)

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

    def retake(self):
        self.captured_frame = None
        self.streaming = True
        self.capture_btn.configure(state="normal")
        self.retake_btn.configure(state="disabled")
        self.submit_btn.configure(state="disabled")

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


class ImageApp(TkinterDnD.Tk):
    """Main GUI application"""

    def __init__(self):
        super().__init__()
        self.title("Upload Image")
        self.geometry("620x650")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.image_path: str | None = None

        # Drag & Drop zone ------------------------------------------------
        self.canvas = ctk.CTkCanvas(self, width=480, height=220, highlightthickness=2)
        self.canvas.pack(pady=32)
        self.canvas.create_rectangle(12, 12, 468, 208, dash=(6, 4), outline="#888", width=2)

        self.drop_frame = ctk.CTkFrame(self.canvas, fg_color="transparent", width=440, height=200)
        self.canvas.create_window(240, 110, window=self.drop_frame)

        self.icon_lbl = ctk.CTkLabel(self.drop_frame, text="🖼️", font=ctk.CTkFont(size=36))
        self.icon_lbl.pack(pady=(22, 4))
        self.info_lbl = ctk.CTkLabel(self.drop_frame, text="Drag and drop an image here", font=ctk.CTkFont(size=15))
        self.info_lbl.pack()

        button_bar = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        button_bar.pack(pady=12)
        ctk.CTkButton(button_bar, text="Browse", command=self.browse_file).grid(row=0, column=0, padx=6)
        ctk.CTkButton(button_bar, text="Take Picture", command=self.open_camera).grid(row=0, column=1, padx=6)

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self._handle_drop)

        # Preview ---------------------------------------------------------
        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.pack(pady=18)

        # Action buttons --------------------------------------------------
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.start_btn = ctk.CTkButton(self.action_frame, text="Start Process", command=self.start_process)
        self.del_btn = ctk.CTkButton(self.action_frame, text="Delete Image", fg_color="#D83C3C", hover_color="#B63030", command=self.delete_image)

    # --------------------------- events --------------------------------
    def browse_file(self):
        path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")])
        if path:
            self.set_image(path)

    def open_camera(self):
        CameraCapture(self, self.set_image)

    def _handle_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path):
            self.set_image(path)

    def set_image(self, path: str):
        if not path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
            self.image_label.configure(text="Invalid image format", image=None)
            return
        try:
            img = Image.open(path)
        except Exception as exc:
            self.image_label.configure(text=f"Could not open image: {exc}", image=None)
            return

        img.thumbnail((400, 400))
        ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)
        self.image_label.configure(image=ctk_img, text="")
        self.image_label.image = ctk_img

        self.image_path = path
        self._show_action_buttons()

    def _show_action_buttons(self):
        self.action_frame.pack(pady=6)
        self.start_btn.pack(side="left", padx=6)
        self.del_btn.pack(side="left", padx=6)

    def delete_image(self):
        self.image_path = None
        self.image_label.configure(image=None, text="")
        self.image_label.image = None
        self.action_frame.forget()

    def start_process(self):
        CTkMessagebox(title="Info", message="Process would start here.")


if __name__ == "__main__":
    app = ImageApp()
    app.mainloop()
