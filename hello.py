import tkinter as tk
from tkinter import messagebox

#without class(basics)
# root = tk.Tk()
# root.geometry("400x300")
# root.title("test")

#introductions
# label = tk.Label(root, text="Hello World!", font=("Arial",20))
# label.pack(padx=20, pady=60)

# textbox = tk.Text(root, height=2 , width=30)
# textbox.pack(padx=20, pady=0)

# # myentry = tk.Entry(root)
# # myentry.pack()

# button = tk.Button(root, text="Click me!", font=("Arial",16))
# button.pack(padx=20, pady=20)

#grid
# label = tk.Label(root, text="Hello World!", font=("Arial",20))
# label.pack(padx=20, pady=60)

# textbox = tk.Text(root, height=2 , width=30)
# textbox.pack(padx=20, pady=0)

# buttonframe = tk.Frame(root)
# buttonframe.columnconfigure(0, weight=1)
# buttonframe.columnconfigure(1, weight=1)
# buttonframe.columnconfigure(2, weight=1)

# btn1 = tk.Button(buttonframe, text="1", font=("Arial",16))
# btn1.grid(row=0, column=0, sticky=tk.W+tk.E)

# btn2 = tk.Button(buttonframe, text="2", font=("Arial",16))
# btn2.grid(row=0, column=1, sticky=tk.W+tk.E)

# btn3 = tk.Button(buttonframe, text="3", font=("Arial",16))
# btn3.grid(row=0, column=2, sticky=tk.W+tk.E)

# btn4 = tk.Button(buttonframe, text="4", font=("Arial",16))
# btn4.grid(row=1, column=0, sticky=tk.W+tk.E)

# btn5 = tk.Button(buttonframe, text="5", font=("Arial",16))
# btn5.grid(row=1, column=1, sticky=tk.W+tk.E)

# btn6 = tk.Button(buttonframe, text="6", font=("Arial",16))
# btn6.grid(row=1, column=2, sticky=tk.W+tk.E)

# buttonframe.pack(fill="x")

#button placed anywhere
# anotherbutton = tk.Button(root, text="Click me!", font=("Arial",16))
# anotherbutton.place(x=200, y=150)



# root.mainloop()



#with class
class mygui:
    def __init__(self):
        self.root = tk.Tk()

        self.menubar = tk.Menu(self.root)
        
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="close", command=self.on_closing)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="close without question", command=exit)

        self.actionmenu = tk.Menu(self.menubar, tearoff=0)
        self.actionmenu.add_command(label="show message", command=self.show_message)

        
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Action", menu=self.actionmenu)
        self.root.config(menu=self.menubar)
        

        self.label = tk.Label(self.root, text="Hello World!", font=("Arial",20))
        self.label.pack(padx=10, pady=10)

        self.textbox = tk.Text(self.root, height=2 , font=("Arial",16))
        self.textbox.bind("<KeyPress>", self.shortcut)
        self.textbox.pack(padx=10, pady=10)


        self.check_state = tk.IntVar()

        self.check = tk.Checkbutton(self.root, text="I agree to the terms and conditions", font=("Arial",16)
                                    ,variable=self.check_state)
        self.check.pack(padx=10, pady=10)

        self.button = tk.Button(self.root, text="Click me!", font=("Arial",16), command=self.show_message)
        self.button.pack(padx=10, pady=10)

        self.clearbutton = tk.Button(self.root, text="Clear", font=("Arial",16), command=self.clear_textbox)
        self.clearbutton.pack(padx=10, pady=10)
        

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    def show_message(self):
        if self.check_state.get() == 0:
            print(self.textbox.get("1.0", tk.END))
        else:
            messagebox.showinfo(title="Message", message=self.textbox.get("1.0", tk.END))

    def clear_textbox(self):
        self.textbox.delete("1.0", tk.END)

    def shortcut(self, event):
        #### print(event)
        #### print(event.keysym)
        #### print(event.state)
        if event.state == 12 and event.keysym == "Return":
            self.show_message()

    def on_closing(self):
        if messagebox.askyesno(title="Quit?", message="Are you sure you want to quit?"):
            self.root.destroy()

        
mygui()