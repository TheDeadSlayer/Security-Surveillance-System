# Security-Surveillance-System
A security surveillance system consisting of 3 main parts:
- Locking System
- Surveillance System
- Android Application

All networking and communications between the systems are done through an active firebase Realtime Database.

There are STL files for 3D designed enclosures for the system.


# Locking System
An arduino controlled locking system that requires a correct password and fingerprint to unlock the door.
A raspberry pi connected to the system interfaces with a Real-time DB to detect any password changes from the android app.

To setup:
- Upload FingerFinal.ino to arduino 
- Connect raspberry pi to arudino via USB
- In Connection.py , make sure line 56 is '/dev/ttyACM1' or '/dev/ttyACM0' depending on the USB port arduino is connected to
- Run Connection.py 


# Surveillance System:
A raspberry pi controlled system that streams video feed locally and over the internet.
An Open-CV script using YOLO-V4 runs on an opposite PC to run a person detetction algorithm, it communicates with the system through the Realtime DB to let it to know that an intruder is detected and send 5 photos of the intruder to cloud storage.

The system consists of:
- A nightvision camera mounted to 2 servo motors of full 360 movement
- A PIR motion sensor and an Ultrasonic sensor 
- A sound detection module 
- A DHT11 tempreture and hummidty sensor 
- A buzzer to act as an alarm

The alarm activates when motion is detected within 1 meter and a person is detected by the Open-CV script.

To setup:
- Setup MJPEG streamer on Raspberry Pi
- Setup pigpiod on Raspberry Pi
- Type "sudo pigpiod"
- Run cameraServer.py
- Run servoServer.py
- Run survey.py


# Android Application
The android application acts as the main interface for the user to the system.

App repo: https://github.com/InterVam/The-Observer

Through the application the user can:
- Create an account and log in 
- View sensor outputs
- Arm and disarm the system
- View camera feed and control camera
- View online feed
- Change locking system password
- View detected intruder photos taken by the camera



