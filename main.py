import os
import sys
import json
import requests  # pip install requests
import socket
# import this
# BT addr for SMA inverter 00:80:25:2F:E8:19

from package1 import void  # just checking  syntax
import package1.progress
import package1.smabluetooth


DEFAULT_CONFIG_FILE = os.path.expanduser("~/sma.json")

def connect_and_logon():
    conn = package1.smabluetooth.Connection(inverter_bluetooth)
    conn.hello()
    conn.logon()
    return conn

# oh.RestAccess.of5h9ZabNVJlsIzjxJnA1tT0kH2JF2uP1dqfSRzG5pwm7w8OyUAuRQdlj0xKV4tB8ST300euUkqWG8O6qnBMQ
def send_to_openHAB_day():
    headers = {
        'accept': '*/*',
        'Content-Type': 'text/plain',
    }

    data = str(daily/1000)

    response = requests.post(
        'http://192.168.1.11:8080/rest/items/EnergyGeneratedToday',
        headers=headers,
        data=data,
        auth=('oh.RestAccess.of5h9ZabNVJlsIzjxJnA1tT0kH2JF2uP1dqfSRzG5pwm7w8OyUAuRQdlj0xKV4tB8ST300euUkqWG8O6qnBMQ', ''),
    )
        
    return 0

def send_to_openHAB_total():
    headers = {
        'accept': '*/*',
        'Content-Type': 'text/plain',
    }

    data = str(total/1000000)

    response = requests.post(
        'http://192.168.1.11:8080/rest/items/TotalEnergyGenerated',
        headers=headers,
        data=data,
        auth=('oh.RestAccess.of5h9ZabNVJlsIzjxJnA1tT0kH2JF2uP1dqfSRzG5pwm7w8OyUAuRQdlj0xKV4tB8ST300euUkqWG8O6qnBMQ', ''),
    )
        
    return 0

#Get configuration from file
# load the .json file
configfile=None

if configfile is None:
            configfile = DEFAULT_CONFIG_FILE
if isinstance(configfile, str):
    f = open(configfile, "r")
else:
    f = configfile
    
alljson = json.load(f)
# fetch parameters form Json

#Syste: name,Inverter: name, bluetooth,serial, password 
if "system name" in alljson:
    sysjson = alljson["system name"]
    system_name = sysjson.get("name")
    print("System name: " + system_name)
if "inverter" in alljson:
    invjson = alljson["inverter"]
    inverter_name = invjson.get("name")
    inverter_bluetooth = invjson.get("bluetooth")
    inverter_serial = invjson.get("serial")
    inverter_password = invjson.get("password")
    print ("Inverter:")
    print ("\t\tName: " + inverter_name)
    print ("\t\tSerial: " + inverter_serial)
    print ("\t\tBluetooth address: " + inverter_bluetooth)
    
    
package1.progress.progress_function(inverter_bluetooth,1)

#Open connectin to inverter get data and send to OpenHAB

try:
    sma = connect_and_logon()
    dtime, daily = sma.daily_yield()
    send_to_openHAB_day()
    print("\t\tDaily generation at %s: %d Wh" % (package1.datetimeutil.format_time(dtime), daily))
    ttime, total = sma.total_yield()
    send_to_openHAB_total()
    print("\t\tTotal generation at %s: %d Wh" % (package1.datetimeutil.format_time(ttime), total))
    
    
except Exception as e:
    print ("Error  contacting  inverter: %s" % e, file =  sys.stderr)
    
package1.progress.progress_function(inverter_bluetooth,2)
# Send Data to openHAB REST interface







