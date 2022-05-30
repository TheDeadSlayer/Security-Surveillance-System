import RPi.GPIO as GPIO
import pigpio
import time

Hservo = 2
Vservo= 3
Hangle=1100
Vangle=1750
pwm=''
pwm2=''

def setup():
    global Hservo
    global Vservo
    global Hangle
    global Vangle
    global pwm
    global pwm2
    
    Hservo = 2
    Vservo= 3

    Hangle=1100
    Vangle=1750
    
    pwm = pigpio.pi() 
    pwm2 = pigpio.pi() 
    pwm.set_mode(Hservo, pigpio.OUTPUT)
    pwm2.set_mode(Vservo, pigpio.OUTPUT)
    
    pwm.set_PWM_frequency( Hservo, 50 )
    pwm2.set_PWM_frequency( Vservo, 50 )
    time.sleep( 1 )

    pwm.set_servo_pulsewidth(Hservo,Hangle)
    pwm2.set_servo_pulsewidth(Vservo,Vangle)

def right():
    global Hangle
    if (Hangle>500):
        Hangle-=25
        pwm.set_servo_pulsewidth(Hservo,Hangle)

def left():
    global Hangle
    if (Hangle<1800):
        Hangle+=25
        pwm.set_servo_pulsewidth(Hservo,Hangle)

def up():
    global Vangle
    if (Vangle<2500):
        Vangle+=50
        pwm2.set_servo_pulsewidth(Vservo,Vangle)

def down():
    global Vangle
    if (Vangle>1750):
        Vangle-=50
        pwm2.set_servo_pulsewidth(Vservo,Vangle)

def initial():
    global Hangle
    global Vangle
    pwm.set_servo_pulsewidth(Hservo,1100)
    pwm2.set_servo_pulsewidth(Vservo,1750)
    Hangle=1100
    Vangle=1750