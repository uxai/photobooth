"""
March 7, 2024
Photo booth created by Matthew Talebi
This file sets up a server and reads in the webcam to create and simulate a photobooth
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread 
import numpy as np
import cv2, sys
import serial

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

message = ""
face_detected = False
img = None
webCam = False
photo_mode = "color"

if(len(sys.argv)>1):
   try:
      print("I'll try to read your image");
      img = cv2.imread(sys.argv[1])
      if img is None:
         print("Failed to load image file:", sys.argv[1])
   except:
      print("Failed to load the image are you sure that:", sys.argv[1],"is a path to an image?")
else:
   try:
      print("Trying to open the Webcam.")
      cap = cv2.VideoCapture(0)
      if cap is None or not cap.isOpened():
         raise("No camera")
      webCam = True
   except:
      img = cv2.imread("../data/test.jpg")
      print("Using default image.")


ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mytopsecretkey'
socketio = SocketIO(app)

# Function borrowed from
# https://medium.com/dataseries/designing-image-filters-using-opencv-like-abode-photoshop-express-part-2-4479f99fb35
def sepia_filter(img):
   img = np.array(img, dtype=np.float64) # converting float to prevent loss
   img = cv2.transform(img, np.matrix([[0.272, 0.535, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]]))
   img[np.where(img > 255)] = 255
   img = np.array(img, dtype=np.uint8)
   return img


def read_from_port(ser):
   while(True):
      if webCam:
         ret, img = cap.read()

      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      faces = face_cascade.detectMultiScale(gray, 1.3, 5)

      if (len(faces) > 0):
         ser.write(b'T')
      else:
         ser.write(b'F')

      # Change mode of photo based on user input
      @socketio.on('GRAYSCALE')
      def grayscale():
         global photo_mode
         photo_mode = "grayscale"

      @socketio.on('SEPIA')
      def sepia():
         global photo_mode
         photo_mode = "sepia"

      @socketio.on('COLOR')
      def color():
         global photo_mode
         photo_mode = "color"

      if photo_mode == "grayscale":
         img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      if photo_mode == "sepia":
         img = sepia_filter(img)

      for (x,y,w,h) in faces:
         message = str(ser.readline())[2]
         if message == 'S':
            cv2.imwrite('image.png', img)

      if webCam:
         cv2.imshow('Photo booth (press q to quit.)',img)
         if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
      else:
         break
   cv2.destroyAllWindows()

# Setup webserver
thread = Thread(target=read_from_port, args=[ser])
thread.start()
print(thread)

@app.route('/')
def index():
   return render_template('index.html')

@socketio.on('connect')
def test_connect():
   print("Client connected")
   emit('my response', {'data': 'connected'}) 

@socketio.on('disconnect')
def test_disconnect():
   print("Client disconnected")

if __name__ == '__main__':
   app.run(host='0.0.0.0', threaded=True)
   socketio.run(app)
