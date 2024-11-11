#Libraries Imported

import cv2
import numpy as np
import os
import tkinter as tk
import skimage as ski
import pyodbc
from tkinter import *
from tkinter.ttk import *

face_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'harcascade_frontalface_default.xml')
finger_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'harcascade_finger.xml')

#Button and GUI Creation
root = Tk()
root.geometry('1000x1000')
btn = Button (root, text = 'Register Profile', command=facial_collection)
btn2 = Button (root, text = "Log in", command= face_validate)
btn3 = Button (root, text="Exit", command = root.quit)
btn.place(x = 500, y = 0)
btn2.place(x= 0, y = 0)
btn3.place(x=900, y = 0)


#Database Connection:
#conn = pyodbc.connect()

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
    faces = face_casecade.detectMultiScale(gray, 1.3,5)
    for(x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)
    cv2.imshow('Facial Recognition', frame)
    if cv2.waitKey(1)& 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

#Methods defined:
def facial_collection():
    pass

def finger_collection():
    pass


def user_creation():
    pass


def face_validate():
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2Gray)
    faces = face_casecade.detectMultiScale(gray, 1.3, 5)

def finger_validate():
    pass

#If Statements for each Button pushed:


root.mainloop()
