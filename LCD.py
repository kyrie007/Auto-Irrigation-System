#!/usr/bin/env python3

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from time import sleep
import _thread


PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
class LCD(object):
    MAX_FIXED_MSG_LEN=16
    def __init__(self): # 
        try:
            self.mcp = PCF8574_GPIO(PCF8574_address)
        except:
            try:
                self.mcp = PCF8574_GPIO(PCF8574A_address)
            except:
                print ('I2C Address Error!')
                exit(1)
        self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2,pins_db=[4,5,6,7], GPIO=self.mcp)
        self.mcp.output(3,1)
        self.lcd.begin(16,2)
        self.max_msg_len=0
        self.row1=None
        self.row2=None
        _thread.start_new_thread(self._scroll_looper,())

    def destroy(self):
        self.lcd.clear()

    def _scroll_looper(self,*argc):
        while True:
            if(self.max_msg_len>self.MAX_FIXED_MSG_LEN):self.lcd.DisplayLeft()
            sleep(0.5)

    def display_row1(self,msg='Default message'):
        # self.lcd.clear()
        self.lcd.setCursor(0,0)
        self.row1=msg
        self.lcd.message(msg)
        self.max_msg_len=max(len(msg),self.max_msg_len)

    def display_row2(self,msg='Default scrolling message'): # display scrolling message on the specific line
        # self.lcd.clear()
        self.lcd.setCursor(0,1)
        self.row2=msg
        self.lcd.message(msg)
        self.max_msg_len=max(len(msg),self.max_msg_len)
    
    def update_row1(self,msg='Default message'):
        if msg!=self.row1:self.display_row1(msg)
    def update_row2(self,msg='Default scrolling message'):
        if msg!=self.row2:self.display_row2(msg)


lcd=LCD()

def display_row1(msg):
    lcd.update_row1(msg)

def display_row2(msg):
    lcd.update_row2(msg)

if __name__ == '__main__':
    
    
    display_row1()
    display_row2()
    while True:
        display_row1()
        display_row2()
        sleep(2)