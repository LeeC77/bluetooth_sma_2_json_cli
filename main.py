import os
import sys
import json
import time
import requests  # pip install requests
import socket
# import this
# BT addr for SMA inverter 00:80:25:2F:E8:19

##### import my packages
#import package1.progress
import package1.smabluetooth


DEFAULT_CONFIG_FILE = os.path.expanduser("~/sma.json") # Windows
#DEFAULT_CONFIG_FILE = os.path.expanduser("./sma.json") # Debian
# Running on Debian
#Debian RFCOMM Bluetooth fix Protocol not supported
#	https://github.com/mathoudebine/homeassistant-timebox-mini/issues/5
#https://support.plugable.com/t/bluetooth-home-automation-switch-btaps1-raspberry-pi-error/8554
#		https://forums.raspberrypi.com//viewtopic.php?p=521067#p521067
# >> sudo apt-get update
# >> sudo apt-get install bluez minicom bluez-utils
# If bluez-utils doesn’t exist then make sure bluz and minicom are installed
# Bluez PNAT is not needed and breaks things, so edit main.conf:
# >> sudo nano /etc/bluetooth/main.conf
# In general add the following:
#   DisablePlugins = pnat
# Reboot the pi

# Functions
# Connect and logon to inverter
def connect_and_logon(inverter_bluetooth, password, timeout):
    conn = package1.smabluetooth.Connection(inverter_bluetooth)
    conn.hello()
    conn.logon(password,timeout)    # pass password here 
    return conn

# Send results to openHAB funcs
# Total Generated today so far
def send_to_openHAB(value,openhab_IPport,openhab_key, type):
    URL= "http://" + openhab_IPport +"/rest/items/"
    if (type == "total today"): 
        URL = URL + "SolarEnergyGeneratedToday"
        value = value / 1000
    if (type == "total energy"):
        URL = URL + "SolarTotalEnergyGenerated"
        value = value /1000000
    if (type == "spot power"):
        URL = URL + "SolarInverterSpotPower"
    if (type == "spot temperature"):
        URL = URL + "SolarInverterSpotTemp"
        value = value / 100
    headers = {
        'accept': '*/*',
        'Content-Type': 'text/plain',
    }
    data = str(value)
    response = requests.post(
#        'http://192.168.1.11:8080/rest/items/EnergyGeneratedToday',
        URL,
        headers=headers,
        data=data,
        auth=(openhab_key, ''),
    )
    return 0


def main():

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

    #System: name,Inverter: name, bluetooth,serial, password 
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
    if "openhab" in alljson:
        ohjson = alljson["openhab"]
        openhab_key = ohjson.get("apikey")
        openhab_IPport=ohjson.get("IPport")
        print ("Inverter:")
        print ("\t\tName: " + inverter_name)
        print ("\t\tSerial: " + inverter_serial)
        print ("\t\tBluetooth address: " + inverter_bluetooth)
        
        
    print("Trying BT address: " + inverter_bluetooth )

    #Open connectin to inverter get data and send to OpenHAB

    try:
        sma = connect_and_logon(inverter_bluetooth, password= bytes(inverter_password, 'utf-8'), timeout=900)
        dtime, daily = sma.daily_yield()
        send_to_openHAB(daily,openhab_IPport, openhab_key,"total today") # Send Data to openHAB REST interface
        print("\t\tAt %s Daily generation was:\t %d Wh" % (package1.datetimeutil.format_time(dtime), daily))
        ttime, total = sma.total_yield()
        send_to_openHAB(total,openhab_IPport, openhab_key, "total energy") # Send Data to openHAB REST interface
        print("\t\tAt %s Total generation was:\t %d Wh" % (package1.datetimeutil.format_time(ttime), total))
    #### LC ##
        wtime, watts = sma.spot_power() 
        print("\t\tAt %s Spot Power is:\t\t %d W" % (package1.datetimeutil.format_time(wtime), watts))
        send_to_openHAB(watts,openhab_IPport, openhab_key, "spot power") # Send Data to openHAB REST interface
        tetime, temp = sma.spot_temp()
        print("\t\tAt %s Spot Temperature is:\t %.2f °C" % (package1.datetimeutil.format_time(tetime), temp/100))
        send_to_openHAB(temp,openhab_IPport, openhab_key, "spot temperature") # Send Data to openHAB REST interface    
        
        
    except Exception as e:
        print ("Error  contacting  inverter: %s" % e, file =  sys.stderr)
        
    print ("Done: " + inverter_bluetooth)
    
starttime = time.time()
while True:
    print("tick")
    main()
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))







