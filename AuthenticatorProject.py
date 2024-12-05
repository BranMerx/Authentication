#Libraries Imported

import cv2
import numpy as np
import sys
import os
import tkinter as tk
import skimage as ski
import pyodbc
from tkinter import *
import threading
import random
import pickle

face_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


neurotec_path = "C:\\Program Files\\Neurotechnology\\Neurotec Biometric SDK 11.2\\Bin\\Win64_x64"
if neurotec_path not in sys.path:
    sys.path.append(neurotec_path)

os.environ['NEUROTEC_PATH'] = neurotec_path


from NeurotecSDK import NFRecord, NFTemplate, NFinger
from NeurotecSDK import NBiometricClient
from NeurotecSDK import NBuffer

client = NBiometricClient()
finger = NFinger()

#Database Connection:
server = 'MERX_LAPT\SQLEXPRESS'
database = 'Authentication'


connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no'
conn = pyodbc.connect(connection_string)
cursor= conn.cursor()

#Methods defined:
def user_creation_gui():
    register_window = tk.Tk()
    register_window.title("User Registration")
    register_window.geometry("400x300")

    entry_firstname = tk.Entry(register_window)
    entry_lastname = tk.Entry(register_window)
    entry_email = tk.Entry(register_window)
    entry_username = tk.Entry(register_window)
    entry_password = tk.Entry(register_window, show="*")

        # Labels and Entry Fields
    tk.Label(register_window, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    entry_firstname = tk.Entry(register_window)
    entry_firstname.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    entry_lastname = tk.Entry(register_window)
    entry_lastname.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
    entry_email = tk.Entry(register_window)
    entry_email.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Username:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    entry_username = tk.Entry(register_window)
    entry_username.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(register_window, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    entry_password.grid(row=4, column=1, padx=10, pady=5)
   
    #Submit function
    def submit_user():
        firstname = entry_firstname.get()
        lastname = entry_lastname.get()
        email = entry_email.get()
        username = entry_username.get()
        password = entry_password.get()
        
        #Code to push the information into the Database: (Need to have userID automatically increase)
        cursor.execute("INSERT INTO [User] (Username, PasswordHash, FirstName, LastName, Email) OUTPUT INSERTED.UserID VALUES(?,?,?,?,?)", (username, password, firstname, lastname, email)
        )
        conn.commit()

        cursor.execute("SELECT SCOPE_IDENTITY()")
        userID = cursor.fetchone()[0]

        facial_collection(userID)
        finger_collection(userID)

        for entry in[entry_username, entry_password, entry_firstname, entry_lastname, entry_email]:
            entry.delete(0, tk.END)

    tk.Button(register_window, text="Register", command=submit_user).grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    register_window.mainloop()

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

        #Insert Fface data into the database
        serialized_faces = pickle.dumps(face_data)
        cursor.execute(
            "INSERT INTO Face (UserID, FaceData) VALUES (?, ?)",
            (userID, serialized_faces)
        )
        conn.commit()

def capture_fingerprint():
    try:
        print("Please place your finger on the scanner.")
        status = client.capture(finger)
        if status.is_error:
            print("Error capturing fingerprint:", status)
            return None
        return finger.get_template()
    except Exception as e:
        print("Error capturing fingerprint:", e)
        return None


def finger_collection(user_id):
    print("Collecting fingerprint...")
    capture = capture_fingerprint()
    if capture is not None:
        template_data = capture.get_data().to_byte_array()
        finger_id = random.randint(1000, 2000)
        cursor.execute(
            "INSERT INTO Finger (FingerID, UserID, FingerData) VALUES (?, ?, ?)",
            (finger_id, user_id, template_data)
        )
        conn.commit()
        print("Fingerprint successfully collected!")
    else:
        print("Fingerprint collection failed.")
        

def face_validate():
    #User will be prompted to validate their face by capturing their face and comparing it with the data stored in the database
    cap = cv2.VideoCapture(0)
    valid = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access camera.")
            break

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

def finger_validate(user_id):
    cursor.execute("SELECT FingerData FROM Finger WHERE UserID = ?", (user_id,))
    stored_finger_data = cursor.fetchall()
    for data in stored_finger_data:
        stored_template = NFTemplate(NBuffer.from_bytes(data[0]))
        if client.verify(finger.get_template(), stored_template):
            return True
    return False




#Button and GUI Creation
root = Tk()
root.geometry('1000x1000')
btn = Button (root, text = 'Register Profile', command = user_creation_gui)
btn2 = Button (root, text = "Log in", command= validate_user)
btn3 = Button (root, text="Exit", command = root.quit)
btn.place(x = 500, y = 0)
btn2.place(x= 0, y = 0)
btn3.place(x=900, y = 0)

root.mainloop()

