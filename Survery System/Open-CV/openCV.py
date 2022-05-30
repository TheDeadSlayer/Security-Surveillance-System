import numpy as np
import cv2
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import os
import sys

cred = credentials.Certificate('C:\\Users\\shahw\\Desktop\\openCV\\control-servo-ad71e-firebase-adminsdk-m7js7-b5ed95e10d.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://control-servo-ad71e-default-rtdb.europe-west1.firebasedatabase.app/'
})


ref = db.reference("/")

UserRef = db.reference("/Control")
armed=UserRef.child("-N03tDv1MvVoC7OG1mir").child("arm").get()
ip=UserRef.child("-N03tDv1MvVoC7OG1mir").child("url").get()

run=1
def listener(event):
    global armed
    global cap
    global ip
    # print(event.event_type)  # can be 'put' or 'patch'
    if(event.path=="/arm"):  
        print(event.data)
        armed=event.data
    if(event.path=="/url"):  
        print(event.data)
        ip=event.data
    
    if(event.path=="/flag"):  
        print(event.data)
        os.execl(sys.executable, sys.executable, *sys.argv)


net=cv2.dnn.readNet('C:\\Users\\shahw\\Desktop\\openCV\\yolov4.weights','C:\\Users\\shahw\\Desktop\\openCV\\yolov4.cfg')


classes = []
with open("C:\\Users\\shahw\\Desktop\\openCV\\coco.names","r") as f:
    classes = [line.strip() for line in f.readlines()]


layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

colors= np.random.uniform(0,255,size=(len(classes),3))

cap = cv2.VideoCapture(ip)
font = cv2.FONT_HERSHEY_PLAIN
starting_time= time.time()
frame_id = 0
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

Users = UserRef.get()
for key,value in Users.items():
        UserRef.child(key).listen(listener)

disarmFlag=0

try:
    while True:
        if armed==0:
            disarmFlag=0

        _,frame= cap.read()  
        frame_id+=1

        height,width,channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame,0.00392,(320,320),(0,0,0),True,crop=False)   

        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids=[]
        confidences=[]
        boxes=[]
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    center_x= int(detection[0]*width)
                    center_y= int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)
                    x=int(center_x - w/2)
                    y=int(center_y - h/2)

                    boxes.append([x,y,w,h])
                    confidences.append(float(confidence)) 
                    class_ids.append(class_id) 

        indexes = cv2.dnn.NMSBoxes(boxes,confidences,0.4,0.6)

        for i in range(len(boxes)):
            if i in indexes:
                x,y,w,h = boxes[i]
                label = str(classes[class_ids[i]])
                confidence= confidences[i]
                color = colors[class_ids[i]]
                if(label=='person'):
                    if(confidence>0.5 and armed==1 and disarmFlag==0):
                            UserRef.child("-N03tDv1MvVoC7OG1mir").update({"cvflag":1})
                            disarmFlag=1
                    cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
                    cv2.putText(frame,label+" "+str(round(confidence,2)),(x,y+30),font,1,(255,255,255),2)
                
        elapsed_time = time.time() - starting_time
        fps=frame_id/elapsed_time
        cv2.putText(frame,"FPS:"+str(round(fps,2)),(10,50),font,2,(0,0,0),1)

        cv2.imshow("Image",frame)
        key = cv2.waitKey(1)

        if key == 27: 
            break;

except KeyboardInterrupt:
     print("done")
    
cap.release()    
cv2.destroyAllWindows()   