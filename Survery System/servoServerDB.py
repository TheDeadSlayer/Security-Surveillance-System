import serial
import time
import firebase_admin
import servoFinal as servo
from firebase_admin import credentials
from firebase_admin import db
import json
import os

cred = credentials.Certificate('/home/deadslayer/Desktop/control-servo-ad71e-firebase-adminsdk-m7js7-7e0980703a (1).json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://control-servo-ad71e-default-rtdb.europe-west1.firebasedatabase.app/'
})

servo.setup()
ctr=['up','down','right','left']
Hmsg=""
Vmsg=""
Imsg=""
Lmsg=""

def listener(event):
    global Hmsg
    global Vmsg
    global Imsg
    global Lmsg
    # print(event.event_type)  # can be 'put' or 'patch'
    if(event.path=="/Hstring"):  
        print(event.data)
        Hmsg=event.data
    if(event.path=="/Vstring"):  
        print(event.data)
        Vmsg=event.data
    if(event.path=="/Initial"):  
        print(event.data)
        Imsg=event.data
    if(event.path=="/flag"):
        print(event.data)
        Lmsg="yes"

                           
ref = db.reference("/")

UserRef = db.reference("/Control")



Users = UserRef.get()
for key,value in Users.items():
        UserRef.child(key).listen(listener)

try:
    while True:
        if Hmsg ==ctr[2]:
            servo.right()
            print ('Going Right: ',servo.Hangle)
        
        elif Hmsg ==ctr[3]:
            servo.left()
            print ('Going Left: ',servo.Hangle)
        else:
            Hmsg=""

        if Vmsg == ctr[0]:
            servo.up()
            print ('Going up: ',servo.Vangle)

        elif Vmsg== ctr[1]:
            servo.down()
            print ('Going Down: ',servo.Vangle)
        else:
            Vmsg=""
        
        if(Imsg=="yes"):
            servo.initial()
            Imsg=""

        if(Lmsg=="yes"):
            os.system('sudo killall mjpg_streamer')
            time.sleep(1) 
            Lmsg=""

        time.sleep(0.05)

except KeyboardInterrupt:
     print("done")
