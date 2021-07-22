# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os

def trackBar(x):
	print(x)


def detect_and_predict_mask(frame, faceNet, maskNet,pos):
	# grab the dimensions of the frame and then construct a blob
	# from it
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (320, 320),
		(103.0+pos, 116.77, 123.68))
	#blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (103.93, 116.77, 123.68))
	#blobb1 = blob.reshape((3,300,-1))
	#blobb2 = blob.reshape(blob.shape[2],blob.shape[1]*blob.shape[3],1)
	#blobb3 = cv2.dnn.imagesFromBlob(blob)
	#cv2.imshow('Blob0',blobb1[0])
	#cv2.imshow('Blob01',blobb1[1])
	#cv2.imshow('Blob02',blobb1[2])
	#cv2.imshow('Blob2',blobb1)
	#cv2.imshow('Blob3',blobb3[0])
	
	# pass the blob through the network and obtain the face detections
	faceNet.setInput(blob)
	detections = faceNet.forward()
	#print(detections.shape[2])


	#-----------------------------------------------------------
	
	#-------------------------------------------------------------


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
		if confidence > 0.5:
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
			cv2.imshow('ROI',face)
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
		preds = maskNet.predict(faces, batch_size=4)

	# return a 2-tuple of the face locations and their corresponding
	# locations
	return (locs, preds)

# load our serialized face detector model from disk
prototxtPath = r"models/face_detector/deploy.prototxt"
weightsPath = r"models/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# load the face mask detector model from disk
maskNet = load_model(r"models/face_detector/maskdetectornew100.model")

# initialize the video stream
print("[INFO] starting video stream...")
vs = cv2.VideoCapture(0)
vs.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
infractores = 0
# loop over the frames from the video stream
cv2.namedWindow('Frame')
cv2.createTrackbar('m1','Frame',0,99,trackBar)
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	succ ,frame = vs.read()
	#frame = imutils.resize(frame, width=400)
	
	pos = cv2.getTrackbarPos('m1','Frame')
	pos = pos/100

	if succ and len(frame) != 0:

		# detect faces in the frame and determine if they are wearing a
		# face mask or not
		(locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet,pos)

		# loop over the detected face locations and their corresponding
		# locations
		for (box, pred) in zip(locs, preds):
			# unpack the bounding box and predictions
			(startX, startY, endX, endY) = box
			(mask, withoutMask) = pred
			# determine the class label and color we'll use to draw
			# the bounding box and text
			"""
			if mask > 0.5:
				label = "Mask"
				color = (0, 0, 0)
			if withoutMask > 0.5:
				label="No Mask"
				color = (0, 0, 255)
				infractores += 1
			"""
			label = "Mask" if mask > withoutMask else "No Mask"
			color = (255,0, 0) if label == "Mask" else (0, 0, 255)
			# display the label and bounding box rectangle on the output
			# frame
			cv2.putText(frame, "{0}: {1:.0f}".format(label,(100*max(mask,withoutMask))), (startX, startY - 10),
				cv2.FONT_HERSHEY_TRIPLEX, 2, color, 2)
			cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
		cv2.putText(frame, 'Total: {}'.format(len(preds)), (0,40),
			cv2.FONT_HERSHEY_TRIPLEX, 0.45, (255,0,0), 2)
		cv2.putText(frame, 'Infractores: {}'.format(infractores), (0,80),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,0,0), 2)
		# show the output frame
		
		cv2.imshow("Frame", frame)
		
		infractores = 0
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
	else:
		print("Error")
		break

# do a bit of cleanup
cv2.destroyAllWindows()
print("Video end")