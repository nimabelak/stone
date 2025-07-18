
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
import tkinter
import os
import PIL
from customtkinter import CTkImage
from customtkinter.windows.widgets.image.ctk_image import CTkImage


ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")

drop_image = PIL.Image.open("drop_image.png")

# Image Browse / Drag and Drop Window
class ImageSelectWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("1000x600")
        self.title("Select an Image")
        self.dialog_open = False
        # Frame with dashed border (simulated)
        self.canvas = ctk.CTkCanvas(self, width=450, height=200, highlightthickness=4, highlightbackground="gray")
        self.canvas.pack(pady=40)
        self.canvas.configure(bg=self._apply_appearance_mode(self._fg_color))
        self.canvas.create_rectangle(10, 10, 450, 200, dash=(6, 4), outline="#888", width=2 , )

        # Create inner frame inside the canvas (this is a child of self.canvas)
        self.drop_frame = ctk.CTkFrame(self.canvas, fg_color="transparent", width=420, height=180)
        self.canvas.create_window(225, 100, window=self.drop_frame)

        # Convert PIL image to CTkImage
        self.my_image = ctk.CTkImage(light_image=drop_image, dark_image=drop_image, size=(60, 60))
        
        # Place the image itself in the drop frame
        self.drop_image_label = ctk.CTkLabel(self.drop_frame, image=self.my_image, text="")
        self.drop_image_label.pack(pady=(20, 5)) # top padding: 20 , bottom padding : 5
        
        # Place the text label under the image
        self.text_label = ctk.CTkLabel(self.drop_frame, text="Drop your Image here", text_color="#888")
        self.text_label.pack(pady=(5, 20))

        self.browse_button = ctk.CTkButton(self.drop_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=(10, 0))

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)

        # Where image will be shown
        self.selected_image = ctk.CTkLabel(self, text="")
        self.selected_image.pack(pady=1)


        # Make window appear on top
        self.set_window_on_top()

    def browse_file(self):
        if not self.dialog_open:
            self.dialog_open = True
            self.browse_button.configure(state="disabled")
            try:
                file_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")],
                    #parent=self,  # Keep dialog modal to Toplevel, optional
                )
                if file_path:
                    self.show_image(file_path)
            finally:
                self.dialog_open = False
                self.browse_button.configure(state="normal")

                
    def on_drop(self, event):
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.show_image(file_path)

    def show_image(self, path):
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img = PIL.Image.open(path)
            img.thumbnail((800, 800))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)

            self.selected_image.configure(image=ctk_img, text="")
            self.selected_image.image = ctk_img  # Keep reference
        else:
            self.selected_image.configure(text="Invalid image format", image=None)
            self.selected_image.image = None

    def set_window_on_top(self):
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))  # Remove topmost after brief delay


class App(TkinterDnD.Tk):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x600")
        self.button_1 = ctk.CTkButton(self, text="open select image window", command=self.open_toplevel)
        self.button_1.pack(side="top", padx=20, pady=20)
        self.title("Stone App")
        self.image_select_window = None

     def open_toplevel(self):
        if self.image_select_window is None or not self.image_select_window.winfo_exists():
            self.image_select_window = ImageSelectWindow(self)  # create window and set it to ImageSelectWindow
            self.image_select_window.focus()
        else:
            self.image_select_window.focus() # if window exists focus it




app = App()
app.mainloop()
