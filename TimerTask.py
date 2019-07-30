from threading import Timer
import _thread
import time
import schedule
import datetime

def _schedule_runner():
    while True:
        schedule.run_pending()
        time.sleep(1)

_thread.start_new_thread(_schedule_runner,())

def create_job_per_minute(job, interval, *argc, **argv):
    def _job_thread():
        _thread.start_new_thread(job,(argc,argv))
    schedule.every(interval).minutes.do(_job_thread)
def create_job_per_sec(job, interval, *argc, **argv):
    def _job_thread():
        _thread.start_new_thread(job,(argc,argv))
    schedule.every(interval).seconds.do(_job_thread)
def create_job_per_hour(job, interval, *argc, **argv):
    def _job_thread():
        _thread.start_new_thread(job,(argc,argv))
    schedule.every(interval).hours.do(_job_thread)

if __name__=='__main__':
    testDict={0:1}
    testDict2={0:1}
    def _print_datetime(*argc, **argv):
        _testDict=argc[0][0]
        _testDict[1]=2
        print(datetime.datetime.now())
    create_job_per_sec(_print_datetime,2,testDict,testDict2)
    while True:
        time.sleep(2)