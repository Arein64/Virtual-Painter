from tkinter import *
import cv2
import mediapipe as mp
import numpy as np
import pymongo
import cloudinary, cloudinary.api, cloudinary.uploader
import requests
from PIL import Image, ImageTk 
from io import BytesIO

client = pymongo.MongoClient("")
db = client["virtual_painter"]
cloudinary.config(
    cloud_name="",
    api_key="",
    api_secret=""
)
painting = None
mphands = mp.solutions.hands
hands = mphands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

def startcap():
    global painting
    cap = cv2.VideoCapture(0)
    painting = None
    while True:
        _, frame = cap.read()
        h,w,_ = frame.shape
        frame = cv2.flip(frame,1)

        if painting is None:
            painting = np.zeros_like(frame)

        imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imageRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                index = handLms.landmark[8]
                x, y = int(index.x * w), int(index.y * h)

                cv2.circle(painting,(x,y),1,(255,0,0),-1)
                cv2.circle(frame,(x,y),15,(255,0,0),-1)

        cv2.imshow("Painting", painting)
        cv2.imshow("Camera",frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite("painting.png",painting)
            result = cloudinary.uploader.upload("painting.png")
            collection = db["virtual_painter"]
            doc = {"image_url": result["secure_url"]}
            collection.insert_one(doc)  
            print(result["secure_url"])
            cap.release()
            cv2.destroyAllWindows()
            break

def view():
    new_win = Toplevel()
    new_win.title("Previous Projects")
    collection = db["virtual_painter"]
    images = collection.find({}, {"_id": 0, "image_url": 1})
    images = list(collection.find({}, {"_id": 0, "image_url": 1}))
    global i
    i = 0
    fwd = Button(new_win,text=">>",command=increment)
    fwd.pack()
    bck = Button(new_win,text="<<",command=backward)
    bck.pack()
    doc = images[i]
    url = doc["image_url"]
    response = requests.get(url)        
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    photo = ImageTk.PhotoImage(img)
    label = Label(new_win, image=photo)
    label.image = photo
    label.pack()
def increment():
    global i
    i+=1
    return i
def backward():
    global i
    i-=1
    return i
root = Tk()
root.title("Virtual Painter App")

button = Button(root, text="Start Capture", command=startcap)
button.pack(padx=20, pady=20)

button2 = Button(root, text= "See Previous Projects",command=view)
button2.pack(padx=20,pady=20)
root.mainloop()
