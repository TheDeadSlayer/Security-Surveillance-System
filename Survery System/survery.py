from fileinput import filename
import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
import psutil
import firebase_admin
from firebase_admin import credentials, initialize_app, storage
from firebase_admin import credentials
from firebase_admin import db
import os
import json
import socket

#Establishing DB connection
cred = credentials.Certificate('/home/deadslayer/Desktop/control-servo-ad71e-firebase-adminsdk-m7js7-7e0980703a (1).json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://control-servo-ad71e-default-rtdb.europe-west1.firebasedatabase.app/',
    'storageBucket': 'control-servo-ad71e.appspot.com'
})


#initialize_app(cred, )
armed=0

# def listener(event):
#     global armed
#     # print(event.event_type)  # can be 'put' or 'patch'
#     if(event.path=="/arm"):  
#         print(event.data)
#         armed=event.data

ref = db.reference("/")

UserRef = db.reference("/Control")

#Send URL to DB
gw = os.popen("ip -4 route show default").read().split()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((gw[2], 0))
ipaddr = s.getsockname()[0]
gateway = gw[2]
host = socket.gethostname()
ipaddr1="http://"+ipaddr+"/?action=stream"
ipaddr2="http://"+ipaddr+"/stream_simple.html"
UserRef.child("-N03tDv1MvVoC7OG1mir").update({"url":ipaddr1})
UserRef.child("-N03tDv1MvVoC7OG1mir").update({"url2":ipaddr2})


GPIO.setwarnings(False)

#pin Numbers

trigPin = 23 
echoPin = 24
pirPin=27
buzzPin=25
micPin=22

#Setting up pins

GPIO.setmode(GPIO.BCM)
GPIO.setup(trigPin,GPIO.OUT)
GPIO.setup(echoPin,GPIO.IN)
GPIO.setup(pirPin,GPIO.IN)
GPIO.setup(buzzPin,GPIO.OUT)
GPIO.setup(micPin,GPIO.IN)

#Intialzing DHT11
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
sensor = adafruit_dht.DHT11(board.D17)


#Intializing ultrasonic
GPIO.output(trigPin, False)
time.sleep(2)

#flags
sonicFlag=0
pirFlag=0
cvFlag=0
screenshotFlag=0
shotNum=0
soundFlag=0

Users = UserRef.get()
# for key,value in Users.items():
#         UserRef.child(key).listen(listener)
# for key,value in Users.items():

# MIC detection
def callback(channel):
    global soundFlag
    soundFlag=1
    print("Sound Detected")
    for key,value in Users.items():
        UserRef.child(key).update({"soundFlag":1})

GPIO.add_event_detect(micPin, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(micPin, callback)  # assign function to GPIO PIN, Run function on change   

#Main LOOP
try:
    while True:

        armed=UserRef.child("-N03tDv1MvVoC7OG1mir").child("arm").get()
        if armed==0:
            sonicFlag=0
            pirFlag=0
            cvFlag=0
            screenshotFlag=0
            soundFlag=0
            for key,value in Users.items():
                UserRef.child(key).update({"alarm":"no"})
                UserRef.child(key).update({"pir":"no"})
                UserRef.child(key).update({"cvflag":0})
                UserRef.child(key).update({"soundFlag":0})
            GPIO.output(buzzPin, False)

        elif armed==1:
            #Get openCV reading
            cvFlag=UserRef.child("-N03tDv1MvVoC7OG1mir").child("cvflag").get()
            shotNum=UserRef.child("-N03tDv1MvVoC7OG1mir").child("screenshot").get()
            #Ultrasonic 
            GPIO.output(trigPin, True)
            time.sleep(0.00001)
            GPIO.output(trigPin, False)

            while GPIO.input(echoPin)==0:
                pulse_start = time.time()
            while GPIO.input(echoPin)==1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance+1.15, 2)

            if(distance<100):
                sonicFlag=1
    
            print ("Ultrasonic distance:",distance,"cm") # send distance here

            for key,value in Users.items():
                UserRef.child(key).update({"ultrasonic":str(distance)})

            #PIR
            detect = GPIO.input(pirPin)
            if detect == 1:
                print("Intruder detected")  # send Distance here
                pirFlag = 1
                for key, value in Users.items():
                    UserRef.child(key).update({"pir": "yes"})
                time.sleep(0.05)

            if cvFlag==1 and screenshotFlag==0:
                for i in range (5):
                        string= 'ffmpeg -f MJPEG -y -i http://localhost/?action=stream -r 1 -vframes 1 -q:v 1 snapshot'+str(shotNum)+str(i)+'.jpg'
                        os.system(string)
                        fileName ="snapshot" +str(shotNum)+str(i)+".jpg"
                        print(fileName)
                        bucket = storage.bucket()
                        blob = bucket.blob(fileName)
                        blob.upload_from_filename(fileName)
                        time.sleep(0.25)
                        detect = GPIO.input(pirPin)
                        if detect == 1:
                            print("Intruder detected")  # send Distance here
                            pirFlag = 1
                            for key, value in Users.items():
                                UserRef.child(key).update({"pir": "yes"})
                            time.sleep(0.05)
                
                screenshotFlag=1
                shotNum+=1
                UserRef.child("-N03tDv1MvVoC7OG1mir").update({"screenshot":shotNum})



            #Activate alarm
            if sonicFlag==1 and pirFlag==1 and armed==1 and cvFlag==1: 
                for key,value in Users.items():
                    UserRef.child(key).update({"alarm":"yes"})
                GPIO.output(buzzPin, True)


        #DHT11
        try:
            temp = sensor.temperature
            humidity = sensor.humidity
            print("Temperature: {}*C   Humidity: {}% ".format(temp, humidity)) #send temp here
            for key,value in Users.items():
                UserRef.child(key).update({"dhtT":str(temp)})
                UserRef.child(key).update({"dhtH":str(humidity)})

        except RuntimeError as error:
            #print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            sensor.exit()
            raise error

        time.sleep(2.0)


except KeyboardInterrupt:
     GPIO.cleanup()