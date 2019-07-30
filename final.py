import CIMIS
import TimerTask
import datetime
import time
import DHT
import LCD
import RPi.GPIO as GPIO
import MotionSensor
import switch
import _thread
from threading import Timer
import os
import json


base_dir = os.getcwd()
minute_data_path=os.path.join(base_dir,"minute_data.txt")
hour_data_path=os.path.join(base_dir,"hour_data.txt")

try:
    os.remove(minute_data_path)
    os.remove(hour_data_path)
except:
    pass

GPIO.setwarnings(False)

watering=switch.get_switch_status()

local_data={}
avg_data={}
local_hly_eto={}

cur_local_tmp=None
cur_local_hum=None

#two msg that will be showed on LCD
msg1='Water:on' if watering else 'Water:off'
msg2=None

hour_id=0 
left_hour=24
already_water=0
start_hour=datetime.datetime.now().hour

PF=1.0 #for grass
SF=200 #according to project specification
IE=0.75 #according to suggestion
water_per_hour=1020 #according to project specification
water_per_sec=water_per_hour/60/60

def write_minute_data(line):
    with open(minute_data_path,"a") as f:
        f.write(line)
def write_hour_data(line):
    with open(hour_data_path,"a") as f:
        f.write(line)

write_minute_data('\n'+datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+'\n')

#the function to get require water amount of the day by given Et0
def get_require_water(eto):
    return (eto*PF*SF*0.62)/IE

#get the amount of water needed for this hour
def get_water_for_hour(eto,already_water):
    water_for_day=(eto*PF*SF*0.62)/IE-already_water
    water_for_hour=water_for_day/left_hour
    return water_for_hour

def get_water_seconds(water_for_hour):
    water_seconds=water_for_hour/water_per_sec
    return water_seconds

def get_cur_hour():
    return datetime.datetime.now().hour

def open_water(after_seconds=0):
    t=Timer(after_seconds,switch.turn_on)

#this function will be called after an hour has passed
#the device will start water for given seconds
def _watering(seconds):
    print("Start water for %.2f seconds"%seconds)
    watered_sec=0
    if seconds<=0:return
    switch.turn_on()
    start_water_time=datetime.datetime.now()
    checking=False
    reopen_timer=None #a timer that will reopen the switch
    global watering
    while watered_sec<seconds:
        time.sleep(1)
        #if the device is not waiting people and there is a people pass by
        #stop watering
        if not checking and MotionSensor.check_people():
            watering=False
            checking=True
            switch.turn_off()
            reopen_timer=Timer(60,switch.turn_on)
        #if the device is waiting people and the people has leaved
        #open the switch imedaiately
        if checking and not MotionSensor.check_people():
            watering=True
            checking=False
            reopen_timer.cancel()
            switch.turn_on()
        if watering:watered_sec+=(datetime.datetime.now()-start_water_time).seconds
    switch.turn_off()

#start a new thread to water
def start_watering(seconds):
    _thread.start_new_thread(_watering,(seconds,))

#update the message that will show on LCD
def update_msg1(cur_local_tmp,cur_local_hum):
    global msg1
    global watering
    if watering:
        msg1="T:%.2f,H:%.2f,W:On"%(cur_local_tmp,cur_local_hum)
    else:
        msg1="T:%.2f,H:%.2f,W:Off"%(cur_local_tmp,cur_local_hum)
    write_minute_data(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+' '+msg1+'\n')

def update_msg2(CIMIS_tmp,CIMIS_hum,CIMIS_Eto,local_eto,water_saving):
    global msg2
    msg2="C:t:%.1f,h:%.1f,e:%.1f;le:%.1f;ws:%.1f"%\
        (CIMIS_tmp,CIMIS_hum,CIMIS_Eto,
        local_eto,water_saving)
    hly_dict={'C_tmp':CIMIS_tmp,'C_hum':CIMIS_hum,'C_Eto':CIMIS_Eto,\
        'local_Eto':local_eto,'water_saving':water_saving}
    write_minute_data('\n'+datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+'\n')
    write_hour_data(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+' '+json.dumps(hly_dict)+'\n')

#update local data(local temperature, local humidity) for minute
def update_local_data(*argc, **argv):
    dht=DHT.get_dht()
    if dht is None:return
    global hour_id
    if hour_id not in local_data.keys():local_data[hour_id]=[dht]
    else:local_data[hour_id].append(dht)
    
    #if it is the first hour, the avg_tmp and avg_hum
    #will be the average of all the data attain until now
    prev_hour_id=hour_id-1
    if prev_hour_id<0:
        sum_tmp=0
        sum_hum=0
        cur_hour_len=len(local_data[hour_id])
        if cur_hour_len<=0:return
        for (tmp,hum) in local_data[hour_id]:
            sum_tmp+=tmp
            sum_hum+=hum
        cur_local_tmp=sum_tmp/cur_hour_len
        cur_local_hum=sum_hum/cur_hour_len
        avg_data[hour_id]=(cur_local_tmp,cur_local_hum)
        update_msg1(cur_local_tmp,cur_local_hum)

#update local data(local temperature, local humidity) for hour
def update_local_th():
    global hour_id
    prev_hour_id=hour_id-1
    #get the avg data of the last hour
    if prev_hour_id >=0:
        sum_tmp=0
        sum_hum=0
        prev_hour_len=len(local_data[prev_hour_id])
        for (tmp,hum) in local_data[prev_hour_id]:
            sum_tmp+=tmp
            sum_hum+=hum
        cur_local_tmp=sum_tmp/prev_hour_len
        cur_local_hum=sum_hum/prev_hour_len
        avg_data[prev_hour_id]=(cur_local_tmp,cur_local_hum)
        update_msg1(cur_local_tmp,cur_local_hum)

#function that updates Et0 hourly
def update_eto(*argc, **argv):
    
    global hour_id
    hour_id+=1
    update_local_th()
    CIMIS_data=CIMIS.get_data()#get data from CIMIS
    prev_hour_id=hour_id-1
    local_tmp,local_hum=avg_data[prev_hour_id]
    rate1,rate2=local_tmp/CIMIS_data[CIMIS.AirTmp],CIMIS_data[CIMIS.RelHum]/local_hum
    CIMIS_data[CIMIS.Eto]=0.2#temp
    local_eto=CIMIS_data[CIMIS.Eto]*rate1*rate2#get local Et0
    local_hly_eto[prev_hour_id]=local_eto
    #update msg on LCD
    update_msg2(CIMIS_data[CIMIS.AirTmp],CIMIS_data[CIMIS.RelHum],\
        CIMIS_data[CIMIS.Eto],local_eto,\
        get_require_water(CIMIS_data[CIMIS.Eto])-get_require_water(local_eto))
    print("CIMIS: tmp:%.1f, hum:%.1f, eto:%.1f\nlocal_eto:%.1f water_saving:%.1f"%\
        (CIMIS_data[CIMIS.AirTmp],CIMIS_data[CIMIS.RelHum],CIMIS_data[CIMIS.Eto],
        local_eto,get_require_water(CIMIS_data[CIMIS.Eto])-get_require_water(local_eto)))

    global already_water,left_hour
    left_hour-=1
    water_for_hour=get_water_for_hour(local_eto,already_water)
    already_water+=water_for_hour#update already water amount
    start_watering(get_water_seconds(water_for_hour))#start watering
    if left_hour<=0:
        left_hour=24
        already_water=0

if __name__=='__main__':
    #update tmp and hum and record it every minute
    TimerTask.create_job_per_minute(update_local_data,1)
    #update eto and start watering every hour
    TimerTask.create_job_per_hour(update_eto,1)
    while True:
        #update msg on LCD every 5 seconds
        LCD.display_row1(msg1)
        if msg2 is not None:LCD.display_row2(msg2)
        time.sleep(5)