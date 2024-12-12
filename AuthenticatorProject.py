#Libraries Imported

import cv2
import numpy as np
import sys
import os
import tkinter as tk
import skimage as ski
import pyodbc
from tkinter import *
from tkinter import messagebox
import threading
import random
import pickle
import time

face_casecade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


#Database Connection:
server = 'MERX_LAPT\SQLEXPRESS'
database = 'Authentication'


connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no'
conn = pyodbc.connect(connection_string)
cursor= conn.cursor()

#User Creation GUI 
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
   
    #Submit user into the database
    def submit_user():
        firstname = entry_firstname.get()
        lastname = entry_lastname.get()
        email = entry_email.get()
        username = entry_username.get()
        password = entry_password.get()
        
        #Code to push the information into the Database: (Need to have userID automatically increase)
        cursor.execute("INSERT INTO [User] (Username, PasswordHash, FirstName, LastName, Email) OUTPUT INSERTED.UserID VALUES(?,?,?,?,?)", (username, password, firstname, lastname, email)
        )
        userID = cursor.fetchone()[0]
        conn.commit()


        facial_collection(userID)
        fingerprint_path = capture_fingerprint(userID)
        fingerprint_enrollment(userID, fingerprint_path)
        messagebox.showinfo("Success", "User registered successfully!")

        for entry in[entry_username, entry_password, entry_firstname, entry_lastname, entry_email]:
            entry.delete(0, tk.END)

    tk.Button(register_window, text="Register", command=submit_user).grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    register_window.mainloop()

#Method to collect the facial data of the user
def facial_collection(userID):
    # Access the camera
    cap = cv2.VideoCapture(0)
    time.sleep(2)  # Allow camera to initialize
    if not cap.isOpened():
        print("Failed to access camera.")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = 0
    face_data = []

    print("Starting face data collection. Please look into the camera.")

    while count < 5:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            continue  # Retry capturing the frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face_data.append(face)
            count += 1
            print(f"Collected face {count}/5")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Save only the required number of faces
            if count >= 5:
                break

        cv2.imshow("Face Collection", frame)

        # Press 'q' to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    if count >= 5:
        # Insert face data into the database
        try:
            serialized_faces = pickle.dumps(face_data)
            cursor.execute(
                "INSERT INTO Facial (UserID, FacialData) VALUES (?, ?)",
                (userID, serialized_faces)
            )
            conn.commit()
            print("Facial data successfully collected and stored in the database!")
        except Exception as e:
            print(f"Failed to store facial data: {e}")
    else:
        print("Facial data collection incomplete.")

def capture_fingerprint(user_id):
    cap = cv2.VideoCapture(0) 
    if not cap.isOpened(): 
        print("Failed to access camera.") 
        return None 
        
    print("Please place your finger in front of the camera.")

    fingerprint_path = None
    
    while True: 
        ret, frame = cap.read() 
        if not ret: 
            print("Failed to capture image.")
            break 

        cv2.imshow("Capture Fingerprint", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): 
        # Save the fingerprint image when 'q' is pressed 
            fingerprint_path = f"fingerprint_{user_id}.jpg"
            cv2.imwrite(fingerprint_path, frame)
            break 
    
    cap.release() 
    cv2.destroyAllWindows() 
    return fingerprint_path


def fingerprint_enrollment(user_id, fingerprint_path):
    if not fingerprint_path or not os.path.exists(fingerprint_path):
        print("Fingerprint file not found. Enrollment failed")
        return

    with open(fingerprint_path, "rb") as f: 
        fingerprint_image = f.read()

    serialized_fingerprint = pickle.dumps(fingerprint_image)

    cursor.execute("INSERT INTO Fingerprint (UserID, FingerprintData) VALUES (?, ?)", (user_id, serialized_fingerprint))
    conn.commit()
    print("Fingerprint data successfully collected and stored in the database!")

def finger_validate(user_id):
    captured_fingerprint = capture_fingerprint(user_id)
    if capture_fingerprint is None:
        print ("Failed to capture fingerprint.")
        return 
    
    if not isinstance(captured_fingerprint, np.ndarray):
        print("Failed to capture fingerprint.")
        return 
    
    try:
        gray_image = cv2.cvtColor(captured_fingerprint, cv2.COLOR_BGR2GRAY)
    except cv2.error as e:
        print("Failed to convert image to grayscale.")
        return 

    captured_fingerprint_gray = cv2.cvtColor(captured_fingerprint, cv2.COLOR_BGR2GRAY)

    cursor.execute("SELECT FingerprintData FROM Fingerprint WHERE UserID = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        print("No fingerprint data found.")
        return False
    
    stored_fingerprint_data = pickle.loads(result[0])
    stored_fingerprint = cv2.imdecode(np.frombuffer(stored_fingerprint_data, np.uint8), cv2.IMREAD_GRAYSCALE)

    captured_fingerprint_resized = cv2.resize(captured_fingerprint_gray, (stored_fingerprint.shape[1], stored_fingerprint.shape[0]))
    difference = cv2.norm(captured_fingerprint_resized, stored_fingerprint, cv2.NORM_L2)    

    if difference < 1000:
        return True
    else:
        return False


def face_validate(user_id):
    #User will be prompted to validate their face by capturing their face and comparing it with the data stored in the database
    cap = cv2.VideoCapture(0)
    time.sleep(2)
    valid = False

    cursor.execute("SELECT FacialData FROM Facial WHERE UserID = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        print("No facial data found.")
        return False

    stored_faces = pickle.loads(result[0])

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access camera.")
            break

        gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
        faces = face_casecade.detectMultiScale(gray, 1.3,5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]

            # Compare the face with the stored faces
            for stored_face in stored_faces:
                stored_face = cv2.resize(stored_face, (w, h))
                difference = cv2.norm(face, stored_face, cv2.NORM_L2)

                #Threshold value to determine if faces match
                if difference < 1000:
                    valid = True
                    break
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imshow("Face Validation", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or valid:
            break   
    
    cap.release()
    cv2.destroyAllWindows()

#GUI to validate user with username and biometrics
def validate_user_gui():
    register_window = tk.Tk()
    register_window.title("User Log In")
    register_window.geometry("400x300")

    entry_username = tk.Entry(register_window)

    tk.Label(register_window, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    entry_username = tk.Entry(register_window)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    def validate_biometrics():
        username = entry_username.get()
        cursor.execute("SELECT UserID FROM [User] WHERE Username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            print("User not found.")
            return
        user_id = result[0]
        face_validate(user_id)
        finger_validate(user_id)

        if face_validate(user_id) and finger_validate(user_id):
            messagebox.showinfo("Success", "User authenticated successfully!")
        else:
            messagebox.showerror("Error", "User not authenticated.")

    tk.Button(register_window, text="Log In", command=validate_biometrics).grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    register_window.mainloop()

#Button and GUI Creation
root = Tk()
root.geometry('1000x1000')
btn = Button (root, text = 'Register Profile', command = user_creation_gui)
btn2 = Button (root, text = "Log in", command= validate_user_gui)
btn3 = Button (root, text="Exit", command = root.quit)
btn.place(x = 500, y = 0)
btn2.place(x= 0, y = 0)
btn3.place(x=900, y = 0)

root.mainloop()

