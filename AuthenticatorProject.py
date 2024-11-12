#Libraries Imported

import cv2
import numpy as np
import os
import tkinter as tk
import skimage as ski
import pyodbc
from tkinter import *
from tkinter.ttk import *
import threading

face_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'harcascade_frontalface_default.xml')
finger_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'harcascade_finger.xml')


#Database Connection:
server = 'MERX_LAPT\SQLEXPRESS'
database = 'Authentication'
username = ''
password = ''

connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={'MERX_LAPT\SQLEXPRESS'};DATABASE={'Authentication'};UID={};PWD={}'
conn = pyodbc.connect(connection_string)

cursor = conn.cursor()

#Methods defined:
def user_creation():
    username = input("Please Set Up Username: ")
    password = input("Please Set Up Password: ")

    #Code to push the information into the Database: (Need to have userID automatically increase)

    facial_collection()
    finger_collection()

def facial_collection():
    cap = cv2.VideoCapture(0)
    count = 0
    face_data = []

    while count < 5:
        ret, frame = cap.read()
        gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
        faces = face_casecade.detectMultiScale(gray, 1.3,5) 

        for(x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face_data.append(face)

            #Store the face into the database

def finger_collection():
    cap = cv2.VideoCapture(0)
    count = 0

    while count < 5:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fingers = finger_casecade.detectMultiScale(gray, 1.3, 5)

        

def face_validate():
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

def finger_validate():
    pass

#Button and GUI Creation
root = Tk()
root.geometry('1000x1000')
btn = Button (root, text = 'Register Profile', command = user_creation)
btn2 = Button (root, text = "Log in", command= face_validate)
btn3 = Button (root, text="Exit", command = root.quit)
btn.place(x = 500, y = 0)
btn2.place(x= 0, y = 0)
btn3.place(x=900, y = 0)

root.mainloop()
