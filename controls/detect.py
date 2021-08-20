import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os

from datetime import datetime

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage,int,int,int,np.ndarray)
    list_persons = pyqtSignal(int,int,np.ndarray,str)
    error = pyqtSignal()
    #============= detect functions ============================================================================
    def detect_and_predict_mask(self,frame, faceNet, maskNet):
        # grab the dimensions of the frame and then construct a blob
        # from it
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (720, 720)), 1.0, (512, 512), (104.0, 177.0, 123.0))

        # pass the blob through the network and obtain the face detections
        faceNet.setInput(blob)
        detections = faceNet.forward()

        # initialize our list of faces, their corresponding locations,
        # and the list of predictions from our face mask network
        faces = []
        locs = []
        preds = []

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the detection
            confidence = detections[0, 0, i, 2]
            # filter out weak detections by ensuring the confidence is
            # greater than the minimum confidence
            if confidence > 0.9:
                # compute the (x, y)-coordinates of the bounding box for
                # the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
		
                # ensure the bounding boxes fall within the dimensions of
                # the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
				if startX > w or startX == endX:
					startX = w - 50
				if startY > h:
					startY = h - 50
		

                # extract the face ROI, convert it from BGR to RGB channel
                # ordering, resize it to 224x224, and preprocess it
                face = frame[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                # add the face and bounding boxes to their respective
                # lists
                faces.append(face)
                locs.append((startX, startY, endX, endY))

        # only make a predictions if at least one face was detected
        if len(faces) > 0:
            # for faster inference we'll make batch predictions on *all*
            # faces at the same time rather than one-by-one predictions
            # in the above `for` loop
            faces = np.array(faces, dtype="float32")
            preds = maskNet.predict(faces, batch_size=2)

        # return a 2-tuple of the face locations and their corresponding
        # locations
        return (locs, preds)

    # load our serialized face detector model from disk
    path_base = os.getcwd()
    prototxtPath = os.path.join(path_base,r"models/face_detector/deploy.prototxt")
    weightsPath = os.path.join(path_base,r"models/face_detector/res10_300x300_ssd_iter_140000.caffemodel")
    faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model from disk
    path_model = os.path.join(path_base,r"models/face_detector/maskdetectornew100.model")
    maskNet = load_model(path_model)


    #============= detect functions ============================================================================

    #============= main functions ============================================================================

    def run(self):

        dt = 0
        faces_mask= 0
        faces_without_mask = 0
		color=(0,0,0)
		label=""
        
        dt_temp = 0
        ni = 0
        flag = 0
        send = False

        self.ThreadActive = True
        # initialize the video stream
        print("[INFO] starting video stream...")
        #vs = VideoStream(src=0).start()
        vs = cv2.VideoCapture(0)
        vs.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not vs.isOpened():
            print("error")
            self.error.emit()
        while self.ThreadActive:
            #print(vs.get(cv2.CAP_PROP_FPS))
            success,frame = vs.read()
            if success:
                #frame = imutils.resize(frame, width=800)
                # detect faces in the frame and determine if they are wearing a
                # face mask or not
                (locs, preds) = self.detect_and_predict_mask(frame, self.faceNet, self.maskNet)

                # loop over the detected face locations and their corresponding
                # locations
                for (box, pred) in zip(locs, preds):
                    # unpack the bounding box and predictions
                    (startX, startY, endX, endY) = box
                    (mask, withoutMask) = pred

                    # determine the class label and color we'll use to draw
                    # the bounding box and text
                    #if mask > 0.01:
                    #    label = "Mask"
                    #    color = (0, 255, 0)
                    if withoutMask > 0.9 and mask < 0.01:
                        label="No Mask"
                        color = (0, 0, 255)
                        faces_without_mask += 1

            
		            # display the label and bounding box rectangle on the output
		            # frame
                        cv2.putText(frame, label, (startX, startY - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
                
                if faces_without_mask > 3:
                    cv2.rectangle(frame,(0,0),(1280,720),(0,0,255),10)
                    cv2.putText(frame, "Excedido el número de personas sin mascarilla", (20, 700),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,255), 1)

                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                Image = cv2.flip(Image,1)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1030, 660, Qt.KeepAspectRatio)
                faces_mask = len(preds) - faces_without_mask
                self.ImageUpdate.emit(Pic,len(preds),faces_without_mask,faces_mask,FlippedImage)

                

                #add
                if faces_without_mask > 0:
                    if len(preds) > dt:
                        dt = len(preds)
                    if faces_without_mask > ni:
                        dt = len(preds)
                        ni = faces_without_mask
                        img_temp = FlippedImage
                        send = True
                        name = str(datetime.now())
                    flag = 0
                else:
                    flag += 1

                if flag == 30 and send:
                    self.list_persons.emit(dt,ni,img_temp,name)
                    dt = 0
                    ni = 0
                    flag = 0
                    send = False

                #
                faces_without_mask = 0
                
            else:
                self.error.emit()
                self.stop
        

    


    def stop(self):
        self.ThreadActive = False
        self.quit()

    #============= main functions ============================================================================

    #============= others functions =========================================
    def _persons(self,pred):
        self.list_person = pred

    def _return_persons(self,pred):
        return len(self.list_person)
    #============= others functions =========================================
