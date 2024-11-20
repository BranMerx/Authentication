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
def user_creation_gui():
    username = entry_username.get()
    password = entry_password.get()
    firstname = entry_firstname.get()
    lastname = entry_lastname.get()
    email = entry_email.get()
    password = entry_password.get()
    userID = random.randint(1,1000)  #Randomly generated userID


    #Code to push the information into the Database: (Need to have userID automatically increase)
    cursor.execute(f"INSERT INTO Users (UserID, Username, Password, FirstName, LastName, Email) VALUES ('{userID}', '{username}', '{password}', '{firstname}', '{lastname}', '{email}')")
    conn.commit()


    facial_collection(userID)
    finger_collection(userID)

    for entry in[entry_username, entry_password, entry_firstname, entry_lastname, entry_email]:
        entry.delete(0, END)

    tk.messagebox.showinfo("Success", "User has been created successfully")
    
    register_window = tk.Tk()
    register_window.title("User Registration")
    register_window.geometry("400x300")

    # Labels and Entry Fields
    tk.Label(register_window, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
    entry_firstname = tk.Entry(register_window)
    entry_firstname.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
    entry_lastname = tk.Entry(register_window)
    entry_lastname.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky=W)
    entry_email = tk.Entry(register_window)
    entry_email.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Username:").grid(row=3, column=0, padx=10, pady=5, sticky=W)
    entry_username = tk.Entry(register_window)
    entry_username.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky=W)
    entry_password = tk.Entry(register_window, show="*")
    entry_password.grid(row=4, column=1, padx=10, pady=5)

    # Register Button
    tk.Button(register_window, text="Register", command=register_user).grid(row=5, column=0, columnspan=2, pady=10)

    register_window.mainloop()
#GUI window

def facial_collection(userID):
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
            count += 1
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
            cv2.imshow("Face Collection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cap.release()
        cv2.destroyAllWindows()

        #Insert Fface data into the database)
        facialID = int(random.randint(1000,2000))
        cursor.execute(f"INSERT INTO Facial (FacialID, UserID, Facialdata) VALUES ('{facialID}','{userID}', '{face_data}')")
        conn.commit()

def finger_collection():
    cap = cv2.VideoCapture(0)
    count = 0
    finger_data = []

    while count < 5:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        count += 1

        cv2.imshow("Finger Collection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

    #insert fingerprint data into the database
    FingerprintID = int(random.randint(2000,3000))
    cursor.execute(f"INSERT INTO Fingerprint (FingerprintID, UserID, Fingerprintdata) VALUES ('{FingerprintID}','{userID}', '{finger_data}')")
    conn.commit()
        

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
btn = Button (root, text = 'Register Profile', command = user_creation_gui())
btn2 = Button (root, text = "Log in", command= face_validate)
btn3 = Button (root, text="Exit", command = root.quit)
btn.place(x = 500, y = 0)
btn2.place(x= 0, y = 0)
btn3.place(x=900, y = 0)

root.mainloop()

