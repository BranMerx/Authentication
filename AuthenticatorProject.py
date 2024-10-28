#Libraries Imported
import sys
sys.path.append("C:\Program Files\FPBioimage\FPBioimage-4.5.0.exe")

import cv2
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

#Button and GUI Creation
root = Tk()
root.geometry('1000x1000')
btn = Button (root, text = 'Register Profile', command = root.destroy)
btn2 = Button (root, text = "Log in")
btn3 = Button (root, text="Exit")
btn.pack(side='top')
btn2.pack(side='top')
btn3.pack(side = 'top')

root.mainloop()

def facial_collection():
    pass

def finger_collection():
    pass


def user_creation():
    pass


def face_validate():
    pass

def finger_validate():
    pass

