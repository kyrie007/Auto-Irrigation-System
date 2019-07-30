import RPi.GPIO as GPIO

_relay_pin=16
GPIO.setup(_relay_pin,GPIO.OUT)
switch_on=False
GPIO.output(_relay_pin,False)

def get_switch_status():
    global switch_on
    return switch_on

def turn_on():
    global switch_on
    if switch_on:return
    switch_on=True
    GPIO.output(_relay_pin,True)

def turn_off():
    global switch_on
    if not switch_on:return
    switch_on=False
    GPIO.output(_relay_pin,False)
