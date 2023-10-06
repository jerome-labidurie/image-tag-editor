from tkinter import *
from tkinter import filedialog
from tkinter import font
from PIL import ImageTk, Image
from tkinter.scrolledtext import ScrolledText

from pathlib import Path

from tkinter.filedialog import *
import tkinter as tk
import os

import argparse
import logging as log

text = ""
image_extensions = {"jpg", "png", "JPG"}

# get cmdline options
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--images',
                    help="input directory with images dataset",
                    default=Path.cwd())
parser.add_argument('-e', '--extensions',
                    help="add file extensions to load (default: %s)" % (" ".join(image_extensions)),
                    default=image_extensions,
                    nargs='+')
parser.add_argument('-v', '--verbose',
                    action='count',
                    help="increase verbosity",
                    default=0)
args = parser.parse_args()

# init logging for verbosity
# Level    value verbose
# CRITICAL  50
# ERROR     40
# WARNING   30    0
# INFO      20    1 -v
# DEBUG     10    2 -vv
# NOTSET     0
log_level = log.WARNING - 10 * args.verbose
log.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

image_dir = args.images
image_extensions = image_extensions.union(set(args.extensions))

log.debug("Very Verbose output. level=%d" % (log_level))
log.debug ("Will load files ending by %s" % (", ".join(image_extensions)))

image_files = [f for f in os.listdir(image_dir) if f.endswith(tuple(image_extensions))]
image_names = [file[:-4] for file in image_files]
text_file_paths = [os.path.join(image_dir, image_file[:-4] + '.txt') for image_file in image_files]

log.info ("Found %d images in %s" % (len (image_files), image_dir) )
log.debug (str(image_files))

images = []
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    img = Image.open(image_path)
    images.append(img)

# Create a variable to keep track of the current image
current_image = None

# Create a variable to keep track of the current image index
current_image_index = 0

canvas = tk.Tk()
canvas.grid()
# canvas.geometry("1448x768") # no predefined size, will take what's inside size
canvas.title("tag editor")
canvas.config(bg='white')

def select_image (index):
    global current_image_index
    save_text_file(text_file_paths[current_image_index])
    current_image_index = index
    log.debug("selected from carousel: " + str(index))
    update_image()

# source https://blog.teclado.com/tkinter-scrollable-frames/
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self,*args, **kwargs)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=self.scrollbar.set)
        canvas.pack(side="left", fill="both", expand=False)
        self.scrollbar.pack(side="right", fill="y")
    def bind_mouse (self, widget):
        # with Windows OS
        widget.bind("<MouseWheel>", self.mouse_wheel)
        # with Linux OS
        widget.bind("<Button-4>", self.mouse_wheel)
        widget.bind("<Button-5>", self.mouse_wheel)
    def mouse_wheel(self,event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            print("-" + self.scrollbar.get())

        if event.num == 4 or event.delta == 120:
            print("+" + self.scrollbar.get())


# create images "carousel"
image_scroll = ScrollableFrame(canvas, width=64)
# image_scroll.grid_propagate(0)
image_scroll.grid(row=0, column=0, padx=2, pady=2,sticky="nsew")
image_scroll.buttons = []
# image_scrollbar=Scrollbar(image_scroll, orient="vertical")
# image_scrollbar.config (command=image_scroll.yview)
# image_scrollbar.pack(side = RIGHT, fill = Y)

# image_scrollbar.grid(row=0, column=1, sticky="ns", rowspan=len(image_files))
for idx in range(0,len(image_files)):
    fimg = image_files[idx]
    log.debug ("btn for " + fimg + " in " + str(idx))
    img = Image.open(os.path.join(image_dir,fimg)).resize((64, 64), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    btn = tk.Button(image_scroll.scrollable_frame, image=img, borderwidth=0, highlightthickness=0,
                 command=lambda i=idx: select_image(i))
    btn.image = img
    # btn.grid (column=0, row=idx)
    btn.pack (side=TOP)
    image_scroll.bind_mouse (btn)
    image_scroll.buttons.append(btn)

# label for image display
label = Label(canvas)
label.grid(row=0,column=1,sticky="nsew")

# Create frame to hold the text editor and buttons
text_frame = Frame(canvas, bg = "#1e1319")
text_frame.grid(row=0, column=2, sticky="nsew")

# make re-sizable
canvas.rowconfigure(0, weight=1)
canvas.columnconfigure(0, weight=0)
canvas.columnconfigure(1, weight=0)
canvas.columnconfigure(2, weight=1)

text_frame.rowconfigure(0, weight=1)
text_frame.columnconfigure(0, weight=0)
text_frame.columnconfigure(1, weight=1)


def create_text_file(text, file_path):
    with open(file_path, "w") as file:
        file.write(text)

def update_text_file(text, file_path):
    with open(file_path, "w") as file:
        file.write(text)



# Function to update the image displayed in the
def update_image():
    global current_image
    if current_image:
        canvas.delete(current_image)
    img = images[current_image_index]

    current_text_file = text_file_paths[current_image_index]
    clearFile()

    if os.path.exists(current_text_file):
        load_text_file(current_text_file)
    else:
        text = ""
        create_text_file("", current_text_file)
        log.info ("created " + image_names[current_image_index] + ".txt")

    # resize image, but keep ratio
    width = 512
    ratio = width / float(img.size[0])
    height = int (float(img.size[1]) * ratio)
    log.info ("resize image for display to %dx%d with ratio %.2f" % (width, height, ratio) )

    img = img.resize((width, height), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    label.configure(image=img)
    label.image = img  # Keep a reference to the image



# Bind the arrow keys to change the current image
def on_key_press(event):
    global current_image_index
    current_text_file = text_file_paths[current_image_index]
    if event.keysym == 'Prior':
        save_text_file(current_text_file)
        current_image_index -= 1
        current_image_index = (current_image_index + len(images)) % len(images)
    elif event.keysym == 'Next':
        save_text_file(current_text_file)
        current_image_index += 1
        current_image_index %= len(images)
    update_image()

canvas.bind("<Prior>", on_key_press)
canvas.bind("<Next>", on_key_press)


def load_text_file(file):
    with open(file, "r") as f:
        content = f.read()
    entry.insert(INSERT, content)

def save_text_file(file):
    text = str(entry.get(1.0,END)).rstrip("\n\r")
    print (text)
    with open(file, "w") as f:
        f.write(text)

def clearFile():
    entry.delete(1.0, END)

def saveFileButton():
    new_file = asksaveasfile(mode = 'w', filetypes = [('text files', '.txt')])
    if new_file is None:
        return
    text = str(entry.get(1.0,END)).rstrip("\n\r")
    new_file.write(text)
    new_file.close()

def openFileButton():
    file = askopenfile(mode = 'r', filetypes = [('text files', '*.txt')])
    if file is not None:
        content = file.read()
        entry.insert(1.0, content)

def clearFileButton():
    entry.delete(1.0, END)

def saveAndExitButton():
    current_text_file = text_file_paths[current_image_index]
    save_text_file(current_text_file)
    exit()


# Create a top frame to hold the buttons
button_frame = Frame(text_frame, bg="#1e1319")
button_frame.grid(row=1, column=1, sticky="se")

# for c in range(0,5):
#     button_frame.columnconfigure(c, weight=1)

b5 = Button(button_frame, text="  Save and Exit  ", bg = "#4f2d3f", command = saveAndExitButton)
b4 = Button(button_frame, text="  Exit  ", bg = "#4f2d3f", command = exit)
b3 = Button(button_frame, text="  Clear  ", bg = "#4f2d3f", command = clearFileButton)
b2 = Button(button_frame, text="  Save  ", bg = "#4f2d3f", command = saveFileButton)
b1 = Button(button_frame, text="  Open  ", bg = "#4f2d3f", command = openFileButton)

b5.grid(row=1, column=4, padx=10, pady=20, sticky="E")
b4.grid(row=1, column=3, padx=20, pady=20, sticky="E")
b3.grid(row=1, column=2, padx=20, pady=20, sticky="E")
b2.grid(row=1, column=1, padx=20, pady=20, sticky="E")
b1.grid(row=1, column=0, padx=20, pady=20, sticky="E")

entry = Text(text_frame, wrap = WORD, bg = "#281b22", fg="#d8adc3", insertbackground="yellow", font = ("poppins", 15))
entry.grid(row=0,column=1,sticky="nsew", padx=10, pady=10)

update_image()
canvas.mainloop()
