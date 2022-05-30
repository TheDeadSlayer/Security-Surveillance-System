import serial
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

cred = credentials.Certificate('/home/slayer/Desktop/control-servo-ad71e-firebase-adminsdk-m7js7-30b806c788.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://control-servo-ad71e-default-rtdb.europe-west1.firebasedatabase.app/'
})

passCode=""
msg=""

def listener(event):
    # print(event.event_type)  # can be 'put' or 'patch'
    msg=""
    if(event.path=="/Locking System Password"):  # relative to the reference, it seems
        print(event.data)
        passCode=event.data
        passCode=passCode+'.'
        b=bytes(passCode,'utf-8')
        ser.write(b)
        
        if ser.in_waiting > 0:
            msg=ser.readline().decode('utf-8').rstrip()
            while(msg!="ACK"):
                    ser.write(b)
                    if ser.in_waiting > 0:
                        msg=ser.readline().decode('utf-8').rstrip()
                
                
ref = db.reference("/")

UserRef = db.reference("/Control")

# Retrive code base on SystemID

def intialPass():
    Users = UserRef.get()
    for key,value in Users.items():
        if(value["SystemID"] == 69420):
            passCode= value["Locking System Password"]
            passCode=passCode+'.'
            b=bytes(passCode,'utf-8')
            ser.write(b)
            print(value["Locking System Password"])

# Listens to DB for updates based on certain value   




if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    ser.reset_input_buffer()

Users = UserRef.get()
for key,value in Users.items():
    if(value["SystemID"] == 69420):
        UserRef.child(key).listen(listener)

while True:
    msg=""



    if ser.in_waiting > 0:
        msg=ser.readline().decode('utf-8').rstrip()
        if(msg=="Verify Code"):
            intialPass()
    

    time.sleep(1)
