import os
import sys
import json
import time
import requests  # pip install requests
import argparse


##### import my packages
#import package1.progress
import package1.smabluetooth

VERSION_STRING = "SMA Bluetooth to openHAB rest API.\n\rVersion: 1.1 Date: 05 Mar 2023"
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

# To create executable
# https://pyinstaller.org/en/stable/usage.html#options 
# >> pip install pyinstaller
# >> pyinstaller main.py -n openhabsma
# to run it 
# >> .\dist\openhabsma\openhabsma [-help]

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
    if args.file:
        configfile = args.file
        if verbose: print("overriding default config file location")
    else:configfile=None

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
        if verbose:
            print ("System name: " + system_name)
            print ("Inverter:")
            print ("\t\tName: " + inverter_name)
            print ("\t\tSerial: " + inverter_serial)
            print ("\t\tBluetooth address: " + inverter_bluetooth)
            print ("\t\tOpenHab URL: " + openhab_IPport)
            print ("\t\tKeys and Passwords not shown.")
        
        
    if verbose: print("Trying BT address: " + inverter_bluetooth )

# Open connectin to inverter get data and send to OpenHAB

    try:
        sma = connect_and_logon(inverter_bluetooth, password= bytes(inverter_password, 'utf-8'), timeout=900)
        
        dtime, daily = sma.daily_yield()
        ttime, total = sma.total_yield()
        wtime, watts = sma.spot_power() 
        tetime, temp = sma.spot_temp()
        
# Report values verbose
        if verbose: 
            print("\t\tAt %s Daily generation was:\t %d Wh" % (package1.datetimeutil.format_time(dtime), daily))
            print("\t\tAt %s Total generation was:\t %d Wh" % (package1.datetimeutil.format_time(ttime), total))
            print("\t\tAt %s Spot Power is:\t\t %d W" % (package1.datetimeutil.format_time(wtime), watts))
            print("\t\tAt %s Spot Temperature is:\t %.2f °C" % (package1.datetimeutil.format_time(tetime), temp/100))
          
# Send values to openHAB REST interface        
        if not(args.openhab_off):
            if verbose: print("exporting to openHAB API")
            send_to_openHAB(daily,openhab_IPport, openhab_key,"total today")
            send_to_openHAB(total,openhab_IPport, openhab_key, "total energy")
            send_to_openHAB(watts,openhab_IPport, openhab_key, "spot power")
            send_to_openHAB(temp,openhab_IPport, openhab_key, "spot temperature")
        else:
            if verbose: print("Skipping openHAB API export")
        
    except Exception as e:
        print ("Error contacting inverter: %s" % e, file =  sys.stderr)
        
    if ((not(verbose)) & (not(args.silent))): print ("Done: \t%s, %dWh, %dMWh, %dW, %.2f°C," %(package1.datetimeutil.format_time(dtime),daily,total/1000000,watts,temp/100))
    
starttime = time.time()
go_interval = 30

if __name__ == "__main__":
        
#Command line options        
    parser = argparse.ArgumentParser(description="SMA Inverter Bluetooth  to openHAB rest API",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--continuous",                           help="run continously checking every x second. x > 10. e.g. py openhabsma.py - c 90", type=int, )
    parser.add_argument("-v", "--verbose",      action="store_true",    help="increase verbosity")
    parser.add_argument("-f", "--file",                                 help="path to and .jsn configuration filename. e.g py openhabsma.py -f ./test/sma.json", type=str)
    parser.add_argument("-o", "--openhab_off",  action="store_true",    help="turns off rest sends to openHAB")
    parser.add_argument("-s", "--silent",       action="store_true",    help="completely silent running. -s overrides -v ")
    parser.add_argument("--version",            action="store_true",    help="report version only, main() doesn't run")
    parser.add_argument("-l", "--logfile",                              help="TO DO: log to file, for now use pipe. Windows example: py openhabsma.py -o > temp.txt")
    args = parser.parse_args()
    config = vars(args)
    if args.version : 
        print (VERSION_STRING)
        exit()
    verbose = args.verbose
# Override verbose if in silent
    if args.silent == True: verbose = False
# Report running mode
    if verbose: print(config)    
    else: 
        if not(args.silent):print("Runnig quietly")
# Run once or continuously
    if args.continuous :
        if args.continuous >= 10 :
            go_interval = args.continuous
            if verbose: print("Running once every %d seconds" % (go_interval))
            while True:
                main()
                time.sleep(go_interval - ((time.time() - starttime) % go_interval))
        else :
            print ("value provided for CL option -continuous incorrect")
    else:
            main()

        







