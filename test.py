import customtkinter, time
import PIL

customtkinter.set_appearance_mode("System")  
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("400x240")

def button_function():
    print("button pressed")

# Load the image with PIL first
#image = PIL.Image.open("add_friends.png")

# Use CTkButton with CTkImage
button = customtkinter.CTkButton(
    master=app, 
    text="CTkButton", 
    command=button_function,
    #image=customtkinter.CTkImage(light_image=image, dark_image=image)
)
#button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
button.pack(pady=20)

app.mainloop()
