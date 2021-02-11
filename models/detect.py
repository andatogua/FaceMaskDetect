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

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    list_persons = pyqtSignal(int,int,int)
    #============= detect functions ============================================================================
    def detect_and_predict_mask(self,frame, faceNet, maskNet):
        # grab the dimensions of the frame and then construct a blob
        # from it
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (320, 320),
            (104.0, 177.0, 123.0))

        # pass the blob through the network and obtain the face detections
        faceNet.setInput(blob)
        detections = faceNet.forward()
        #print(detections.shape)

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
            preds = maskNet.predict(faces, batch_size=32)

        # return a 2-tuple of the face locations and their corresponding
        # locations
        return (locs, preds)

    # load our serialized face detector model from disk
    path_base = os.getcwd()
    prototxtPath = os.path.join(path_base,r"models\face_detector\deploy.prototxt")
    weightsPath = os.path.join(path_base,r"models\face_detector\res10_300x300_ssd_iter_140000.caffemodel")
    faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model from disk
    path_model = os.path.join(path_base,r"models\mask_detector.model")
    maskNet = load_model(path_model)


    #============= detect functions ============================================================================

    #============= main functions ============================================================================

    def run(self):
        """
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
        """
        dt = 0
        faces_mask= 0
        faces_without_mask = 0
        self.ThreadActive = True
        # initialize the video stream
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        while self.ThreadActive:
            frame = vs.read()
            frame = imutils.resize(frame, width=800)

            # detect faces in the frame and determine if they are wearing a
            # face mask or not
            (locs, preds) = self.detect_and_predict_mask(frame, self.faceNet, self.maskNet)

            """
            if len(preds) == dt:
                pass
            elif len(preds) > 0:
                if len(preds) > dt:
                    print(" Enviando det" + str(len(preds)))
                    dt = len(preds)
                else:
                    print("det" + str(len(preds)))
                    dt = len(preds)
            else:
                dt = 0
                print("no det")
            """                
            
            


            # loop over the detected face locations and their corresponding
            # locations
            for (box, pred) in zip(locs, preds):
                # unpack the bounding box and predictions
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred

                # determine the class label and color we'll use to draw
                # the bounding box and text
                label = "Mask" if mask > withoutMask else "No Mask"
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

                # include the probability in the label
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                # display the label and bounding box rectangle on the output
                # frame
                if withoutMask > mask:
                    faces_without_mask += 1
                    cv2.putText(frame, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            Image = cv2.flip(Image,1)
            FlippedImage = cv2.flip(Image, 1)
            ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(860, 640, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(Pic)
            faces_mask = len(preds) - faces_without_mask
            self.list_persons.emit(len(preds),faces_without_mask,faces_mask)

            if faces_without_mask > dt:
                print("enviando a DB")
            dt = faces_without_mask                

            faces_without_mask = 0

    


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