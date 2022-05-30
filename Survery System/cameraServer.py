import os
import time
import firebase_admin
from firebase_admin import credentials, initialize_app, storage
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate('/home/deadslayer/Desktop/control-servo-ad71e-firebase-adminsdk-m7js7-7e0980703a (1).json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://control-servo-ad71e-default-rtdb.europe-west1.firebasedatabase.app/',
})

flag=1
onflag=0

def listener(event):
    global onflag
    # print(event.event_type)  # can be 'put' or 'patch'
    if(event.path=="/flag"):  
        print(event.data)
        onflag=event.data

ref = db.reference("/")
UserRef = db.reference("/Control")
Users = UserRef.get()
onflag=UserRef.child("-N03tDv1MvVoC7OG1mir").child("flag").get()
for key,value in Users.items():
        UserRef.child(key).listen(listener)


while True:
    if(flag==1 and onflag==0):
        os.system ('sudo ./mjpg_streamer -i "./input_uvc.so -f 20 -r 1280x720 -n -y" -o "./output_http.so -w ./www -p 80"')
        flag=2
    elif(flag==2 and onflag==1):
        os.system ('sudo ./mjpg_streamer -i "./input_uvc.so -f 10 -r 640x320 -n -y" -o "./output_http.so -w ./www -p 80"')
        flag=1





