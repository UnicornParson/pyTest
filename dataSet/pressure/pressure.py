#!/usr/bin/env python3
import serial
import time
import psycopg2
import os
import sys
from datetime import datetime, timezone

PortSpeed = 115200
DevicePort = '/dev/ttyUSB0'

class EventProcessor:
    def __init__(self):
        self.con = None
        self.cur = None
        self.count = 0
        self.logcount = 100
        
    def processEvent(self, e: str):
        if not self.con or not self.cur:
            print("no connection")
            return
        # 26.20@100562@63.97@78.50
        # readTemperature @ readPressure @ readAltitude @ realaltitude
        data = e.split("@")
        # print(data)
        dt = datetime.now(timezone.utc)
        q = "INSERT INTO public.pressure (temperature, pressure, altitude, realaltitude, dt) VALUES(%s, %s, %s, %s, '%s');" % (data[0],  data[1],  data[2],  data[3],  dt)
        self.cur.execute(q)
        self.con.commit()
        self.count += 1
        if self.count >= self.logcount:
            print("%d records ok" % self.logcount)
            self.count = 0
        
        
    def start(self) -> bool:
        self.con = psycopg2.connect(
                  database="dataset", 
                  user="******", 
                  password="******!", 
                  host="127.0.0.1", 
                  port="5432"
                )
        self.cur = self.con.cursor() 
        print("Database opened successfully")
        return bool(self.con) and bool(self.cur)
        
    def stop(self) -> bool:
        if self.con:
            self.cur = None
            self.con.close()
            self.con = None
        return True
      
      
processor = EventProcessor()

def main() -> int:
    print("try to open %s" % DevicePort)
    ser = serial.Serial(DevicePort, PortSpeed, timeout=10)
    ser.reset_input_buffer()
    print("device ready")
    while True:
        
        line = ser.readline().decode('utf-8').rstrip()
        if line:
            processor.processEvent(line)
        else:
            print("wait...")
            time.sleep(1)
    

if __name__ == '__main__':
    while True:
        print("restart %s" % datetime.now(timezone.utc))
        try:
            if not processor.start():
                print("cannot start EventProcessor")
                time.sleep(1)
                continue
            main()
        except KeyboardInterrupt:
            print('Interrupted')
            processor.stop()
            sys.exit(0)
        except Exception as e:
            print("exception %s" % str(e))
            processor.stop()
            time.sleep(1)
            continue

