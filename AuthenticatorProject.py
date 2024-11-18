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
import random

face_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'harcascade_frontalface_default.xml')
finger_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'harcascade_finger.xml')


#Database Connection:
server = 'MERX_LAPT\SQLEXPRESS'
database = 'Authentication'


connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no'
conn = pyodbc.connect(connection_string)
cursor= conn.cursor()

#Methods defined:
def user_creation():
    username = input("Please Set Up Username: ")
    password = input("Please Set Up Password: ")
    firstname = input("Please Enter Your First Name: ")
    lastname = input("Please Enter Your Last Name: ")
    email = input("Please Enter Your Email: ")
    password = input("Please Enter Your Password: ")
    userID = int(random.randint(1, 1000))   #Randomly generated userID


    #Code to push the information into the Database: (Need to have userID automatically increase)
    cursor.execute(f"INSERT INTO Users (UserID, Username, Password, FirstName, LastName, Email) VALUES ('{userID}', '{username}', '{password}', '{firstname}', '{lastname}', '{email}')")
    conn.commit()


    facial_collection()
    finger_collection()

def facial_collection():
    #After the user has been created, the user will be prompted to collect their facial data
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

            #Store the face data in the database and associate it with the user created
            cursor.execute(f"INSERT INTO FaceData (UserID, FaceData) VALUES ('{userID}', '{face_data}')")

def finger_collection():
    #After the user has been created, the user will be prompted to collect their finger data
    cap = cv2.VideoCapture(0)
    count = 0

    while count < 5:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fingers = finger_casecade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in fingers:
            finger = gray[y:y+h, x:x+w]
            finger_data.append(finger)

            #Store the finger data in the database and associate it with the user created
            cursor.execute(f"INSERT INTO FingerData (UserID, FingerData) VALUES ('{userID}', '{finger_data}')")

        

def face_validate():
    #User will be prompted to validate their face by capturing their face and comparing it with the data stored in the database
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
        faces = face_casecade.detectMultiScale(gray, 1.3,5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]

            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        cv2.imshow("Face Validation", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def finger_validate():
    #user will be prompted to validate their finger by capturing their finger and comparing it with the data stored in the database
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
        fingers = finger_casecade.detectMultiScale(gray, 1.3,5)

        for (x, y, w, h) in fingers:
            finger = gray[y:y+h, x:x+w]

            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
        cv2.imshow("Finger Validation", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            

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

