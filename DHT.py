import RPi.GPIO as GPIO
import time
import datetime
import Freenove_DHT as DHT


DHTPin = 29     #define the pin of DHT11

MAX_READ_RETRIES=20

def get_cur_hour():
    return datetime.datetime.now().hour

dht = DHT.DHT(DHTPin)
def get_dht():
    chk = dht.readDHT11()# try to get tmp and hum
    #try for 10 times else print error
    for i in range(10):
        chk = dht.readDHT11()
        #read DHT11 and get a return value. 
        #Then determine whether data read is normal according to the return value.
        if (chk is dht.DHTLIB_OK):      
            
            print("Local: Temperature:%.2f, Humidity:%.2f\n\n"%(dht.temperature*1.8+32,dht.humidity))
            return (dht.temperature*1.8+32,dht.humidity)
        time.sleep(1)
    print("Read Local Tmp and Hum Failed!!!!!")
    return None

    
if __name__ == '__main__':
    while True:
        get_dht()
        time.sleep(1)