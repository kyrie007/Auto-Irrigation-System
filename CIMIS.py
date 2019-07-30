import requests
import json
import datetime

AirTmp='AirTmp'
RelHum='RelHum'
Eto='Eto'

today=datetime.date.today() 
yesterday=datetime.date.today()-datetime.timedelta(1)

print('today is '+today.strftime('%Y-%m-%d'))
print('yesterday is '+yesterday.strftime('%Y-%m-%d')+'\n')

url='http://et.water.ca.gov/api/data?appKey={appKey}&targets=75&\
startDate={startDate}&endDate={endDate}&\
dataItems=hly-air-tmp,hly-rel-hum,hly-eto'

def _get_CIMIS_data(date):
    assert(isinstance(date,datetime.date))
    info={'appKey':'d200ee5b-f6b2-47ee-af4b-000c178221e1',
        'startDate':date,'endDate':date}
    # retrive the json string with the nessary info
    r=requests.post(url.format(**info))
    try:
        jsonDict=json.loads(r.text)
    except:
        return None #in case the code fail to attain online data
    data_raw=jsonDict['Data']['Providers'][0]['Records']
    
    data={}
    for item in data_raw:
        data[int(item['Hour'])//100]={AirTmp:None if item['HlyAirTmp']['Value'] is \
            None else float(item['HlyAirTmp']['Value']),
        RelHum:None if item['HlyRelHum']['Value'] is \
            None else float(item['HlyRelHum']['Value']),
        Eto:None if item['HlyEto']['Value'] is \
            None else float(item['HlyEto']['Value'])}

    return data

data_yesterday=_get_CIMIS_data(yesterday) #save the data of yesterday
data_today=_get_CIMIS_data(today)

MAX_CIMIS_RETRY_TIMES=5 #Retries of trying to access CIMIS data

def get_data():
    global today, yesterday
    today=datetime.date.today()
    yesterday=datetime.date.today()-datetime.timedelta(1)
    CurHour=datetime.datetime.now().hour

    #try to retrive data from CIMIS with MAX_CIMIS_RETRY_TIMES retries
    data=None
    for i in range(MAX_CIMIS_RETRY_TIMES):
        data=_get_CIMIS_data(today)
        if data is not None:break
    global data_today
    if data is None:
        print('Fail to attain data from CIMIS')
        data=data_today #if fail to get data use the one retrived last time
    else: data_today=data

    #try to get the data of the nearest hour
    #if fail to get it use the data of yesterday of the same hour
    item=None
    for i in range(CurHour-1,0,-1):
        if data[i][AirTmp] is not None and\
        data[i][RelHum] is not None and\
        data[i][Eto] is not None:
            item=data[i]
    if item is None: item=data_yesterday[CurHour] #if fail to get
    return item

if __name__=='__main__':
    
    data_today=_get_CIMIS_data(today)
    get_data()
    for key,item in data_today.items():
        print(str(key)+':'+str(item))
    for key,item in data_yesterday.items():
        print(str(key)+':'+str(item))