#! /usr/bin/python3
#
# openhabsma - Support for Bluetooth enabled SMA inverters and send to openhab rest API
# Copyright (C) 2023 Lee Charlton 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# imports
import argparse
import re
# import my packages
import package1.smabluetooth

VERSION_STRING = "SMA Bluetooth JSON. Version: 1.0.0 Date: 30 Oct 2025"
VALIDACVOLTS = 300.0  # Validates the inverter a.c. voltage
VALIDTEMPERATURE = 0.0 # Validates  the inverter temperature
PATTERN = re.compile(r"^([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$") # Regex pattern for validating bluetooth address

# Functions
# Connect and logon to inverter
def connect_and_logon(inverter_bluetooth, password, timeout):
    conn = package1.smabluetooth.Connection(inverter_bluetooth)
    conn.hello()
    conn.logon(password,timeout)
    return conn

# Validate inverter values
def validate_inverter_value (value_type, value):
    
        if (value_type== "acvolts"):
            if (value > VALIDACVOLTS): return False            # Inverter asleep
        if (value_type == "temperature"):
            if (value == VALIDTEMPERATURE): return False       # Inverter asleep
        return True

# MAIN
def main():
# Initialize
    message = "Success"
    code = 0

# Check Args
    if (args.btaddr is None) or (args.password is None):
        code = 2
        message = "Bluetooth address and password are required"
    elif (len(args.btaddr) != 17):
        code = 3
        message = "Bluetooth address is not the correct length"
    elif not PATTERN.match(args.btaddr):
        code = 3
        message = "Bluetooth address is not in the correct format"

    # Open connection to inverter and get data 
    if (code == 0):

        if (args.test == True):
            # Test mode - use hardcoded values
            dtime = "231 Oct 2025 13:40:13 GMT Standard Time Daily"
            daily = 1234
            ttime = "31 Oct 2025 13:40:13 GMT Standard Time Daily"
            total = 42555205
            wtime = "31 Oct 2025 13:40:13 GMT Standard Time Daily"
            watts = 345
            tetime = "31 Oct 2025 13:40:13 GMT Standard Time Daily"
            temp = 2588
            vtime = "31 Oct 2025 13:40:13 GMT Standard Time Daily"
            acvolts = 23099
            message = "Test mode values used"
        else:
            try:
                sma = connect_and_logon(args.btaddr, password= bytes(args.password, 'utf-8'), timeout=900)
                dtime, daily = sma.daily_yield()
                ttime, total = sma.total_yield()
                wtime, watts = sma.spot_power() 
                tetime, temp = sma.spot_temp()
                vtime, acvolts = sma.spot_voltage()

                # Check values in valid range
                if (not(validate_inverter_value("acvolts", acvolts/100)) or not(validate_inverter_value("temperature", temp/100))):
                    message = "Inverter values out of range, inverter may be asleep"
                    code = 1

            # Catch exceptions
            except Exception as e: 
                code = 4
                message = "Exception: %s" % str(e)

    if (code == 0):
        # Json {"code" : 0, "message" : "xyz", "data" : {"daily" : xxx, "total" : xxx, "watts" : xxx, "temperature" : xx.x, "acvolts" : xx.x, "time" : "xxx"}}
        if (not args.readable): # json print (default)
            print("{\"code\" : %d, \"message\" : \"%s\", \"DATA\" : {\"daily\" : %d, \"total\" : %d, \"watts\" : %d, \"temperature\" : %.2f, \"acvolts\" : %.2f,  \"time\" : \"%s\"}}" % (code, message, daily, total, watts, temp/100, acvolts/100, (package1.datetimeutil.format_time(dtime))))

        if (args.readable):    # readable print  
            print("Status: %s" % message)  
            print("\t\tAt %s Daily generation was:\t %d Wh" % (package1.datetimeutil.format_time(dtime), daily))
            print("\t\tAt %s Total generation was:\t %d Wh" % (package1.datetimeutil.format_time(ttime), total))
            print("\t\tAt %s Spot Power is:\t\t %d W" % (package1.datetimeutil.format_time(wtime), watts))
            print("\t\tAt %s Spot Temperature is:\t %.2f °C" % (package1.datetimeutil.format_time(tetime), temp/100))
            print("\t\tAt %s Spot AC Voltage is:\t %.2f V" % (package1.datetimeutil.format_time(vtime), acvolts/100))        

    if (code != 0):
        if (not args.readable): # json print (default)
                    print("{\"code\" : %d, \"message\" : \"%s\"}" % (code, message))
        if (args.readable):    # readable print    
                    print("Error: %s" % message)
    

if __name__ == "__main__":
        
#Command line options        
    parser = argparse.ArgumentParser(description=VERSION_STRING,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-b", "--btaddr",                         help="the bluetooth address of the inverter e.g. 00:80:25:XX:XX:XX", type=str)
    parser.add_argument("-p", "--password",                       help="password for the inverter", type=str)
    parser.add_argument("-r", "--readable", action="store_true",  help=" off (default) output results in json format, on output in human readable format")
    parser.add_argument("-t", "--test",     action="store_true",  help=" test mode - use hardcoded values rather than connecting to inverter")
    parser.add_argument("-v", "--version",  action="store_true",  help="report version only, main() doesn't run")
    args = parser.parse_args()
    config = vars(args)
    if args.version : 
        print (VERSION_STRING)
        exit()
    main()

    

        







