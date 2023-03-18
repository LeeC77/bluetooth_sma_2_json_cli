# SMA Inverter (BlueTooth) to openHAB (REST)
This project collects data from an SMA Solar Inverter using BlueTooth and optionally publishes the values to the openHAB REST interface.
In my case I have a SMA Sunny Boy 3600TL Inverter and my openHAB installed on an RasPi 4 using openhabian. My  inverter  has been updated to FW3.25.05_SB3600TL-20 but there is no reason to suspect that this will not work with other SMA invertors or FWs.

<https://www.sma.de/en/service/downloads>

## Overview

The motivation for this project was to have a light weight solution that **did not require the installation of MQTT or SQL** like other solutions and can run silently on the same server RasPi  as my openHAB.

The project calls extensively on work done by others:

<https://github.com/SBFspot/SBFspot/tree/master/SBFspot>
<http://blog.jamesball.co.uk/2013/02/understanding-sma-bluetooth-protocol-in.html?q=SMA>
<https://github.com/dgibson/python-smadata2>

There has been previous discussion in the openHAB Community Forum on this subject and this may be of interest to some <https://community.openhab.org/t/example-on-how-to-access-data-of-a-sunny-boy-sma-solar-inverter/50963>

This project has also been extended using the openHAB HTTP Binding and DSL rules to **push solar values to the https://pvoutput.org/ using the addstatus.jsp API**

I came at this problem with the view of building on the limited knowledge and have learn't an awful lot on the way. I will attempt to be thorough with this documentation. There are  some additional un-validated resources in the resources directory that may be of use.

**If you are confident enough to find your own way through you can skip to 'About The Code' section.** else read on for hints.

### Starting Point
* An existing working openHAB 3.4.1 release build running on a RasPi 4 installed via openhabian (Debian)
* VS Code running on Windows
* Some basic knowledge of Python
* An ability to google round to solve your problems
* Python and build tools installed on windows for development / editing if you  need
* Python and build tools installed on the Debian environment of your openHAB 

### Some Cautions / Trouble Shooting 
* I used a RasPi 4 that has built in Bluetooth, not all RasPi have Bluetooth and may require a dongle, This has not  been tested.
* If you see __Debian RFCOMM Bluetooth fix Protocol not supported__, you may need to use the workaround for Bluez PNAT on RasPi see here: https://forums.raspberrypi.com//viewtopic.php?p=521067#p521067
________________________________

Debian RFCOMM Bluetooth fix Protocol not supported
https://github.com/mathoudebine/homeassistant-timebox-mini/issues/5
 https://support.plugable.com/t/bluetooth-home-automation-switch-btaps1-raspberry-pi-error/8554
		https://forums.raspberrypi.com//viewtopic.php?p=521067#p521067
```
    sudo apt-get update
    sudo apt-get install bluez minicom bluez-utils
```
If bluez-utils doesn’t exist then make sure bluez and minicom are installed
Bluez PNAT is not needed and breaks things, so edit main.conf:
```
sudo nano /etc/bluetooth/main.conf
```
In "general" add the following:

DisablePlugins = pnat

Reboot your RasPi
_____________

* Make sure you  have read all the available references and Googled around the subject before reaching for help, its so much more  satisfying.
* You should try to fully understand a command before you execute it or at least be prepared to fully accept any consequence; the responsibility is yours.

# Overview of the Development Environment

There are a few Python support packages needed, they are in the directory package1, these are called by the main() Python module in the project root directory. In addition a few modules will need to be installed in the Python environment using pip. The objective here is to either create an executable that runs in your chosen environment or to run the Python scripts directly via the Python interpreter installed on your operating system. Below we consider Windows 10 and Debian (Buster when I  wrote this).

## Windows 10
If you wish to edit, build or test the Python Code you will need to install Python in your windows environment and add the necessary extensions to VSCode.

Hints:

<https://www.python.org/downloads/>    -->to install Python 
```
    py get-pip.py
```
... to install the Python package manager.
you should add pip to the $PATH environment variable  to  help  save on absolute directory paths.

C:\Users\ [USER] \AppData\Local\Programs\Python\Python311\Scripts
### VSCode Local Extensions

In VSCode running on Windows install the the Python Extension Pack, you will need this for debug and testing.

## Debian (Buster)
On most Linux distributions Python comes pre-installed and/or available via the distribution's package managers. Install Python in Debian using apt-get

Hints:

```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python3 python3-dev
```

### VSCode Remote Extensions
You don't have to use your Windows installed VSCode to build and debug on Debian but if you do you will need to install the 'Remote development extension' and reinstall the Python Extension pack for the remote development environment.
<https://code.visualstudio.com/docs/remote/ssh-tutorial>

<https://learn.microsoft.com/en-gb/windows-server/administration/openssh/openssh_install_firstuse?tabs=gui>

## Python Packages

Your going to need the following Python packages 
```
    pip install requests
    pip install python-dateutil
    pip install pybluez
    pip install pyinstaller
```

Using Pyinstaller
<https://pyinstaller.org/en/stable/usage.html#options>

pyinstaller will be installed here: /home/openhabian/.local/bin/pyinstaller

for example to  build a standalone executable use
```
/home/openhabian/.local/bin/pyinstaller --onefile main.py -n openhabsma
```
___

# About The Code

Python 3.11.2
```
 Root:  
    main.py  
    sma.json  
     Ͱ package1  
        base.py  
        datetimeutil.py  
        smabluetooth.py  
```

sma.json is used to configure the openHab and inverter connection
```
{
    "openhab": {
        "apikey": "xxxxx",
        "IPport": "xxx.xxx.xxx.xxx:8080"
    },
    "system name": {
        "name": "My Inverter Farm"
    },
    "inverter": {
        "name": "Whatever name you want",
        "bluetooth": "00:80:25:XX:XX:XX",
        "serial": "2130XXXXXX",
        "password": "XXXXXXXX"
     }
    
}
```
Replace the values of the key value pairs 
* apikey with the an openHAB api key  <https://www.openhab.org/docs/configuration/apitokens.html>
* IPport with the IP address and port  number (usually 8080)
* bluetooth with thw inverter bluetooth inverter address, you may need to use a bluetooth snooping tool to find this.
* serial with the serial number of the inverter, you  can get this from your inverter paper work or  from the inverter display
* password with the Sunny Boy Explorer password.

Run the Python script  with 

Py main -h to  get  help.
```
py  main.py -h
usage: main.py [-h] [-c CONTINUOUS] [-v] [-f FILE] [-o] [-s] [--version] [-l LOGFILE]

SMA Bluetooth to openHAB rest API. Version: 1.1.1 Date: 12 Mar 2023

options:
  -h, --help            show this help message and exit
  -c CONTINUOUS, --continuous CONTINUOUS
                        run continously checking every x second. x > 10. e.g. py openhabsma.py - c 90 (default: None)
  -v, --verbose         increase verbosity (default: False)
  -f FILE, --file FILE  path to and .jsn configuration filename. e.g py openhabsma.py -f ./test/sma.json (default: None)
  -o, --openhab_off     turns off rest sends to openHAB (default: False)
  -s, --silent          completely silent running. -s overrides -v (default: False)
  --version             report version only, main() doesn't run (default: False)
  -l LOGFILE, --logfile LOGFILE
                        TO DO: log to file, for now use pipe. Windows example: py openhabsma.py -o > temp.txt (default: None)
```
typical usage maybe something like this 
```
py main.py -s  -f /etc/openhab/scripts/sma.json
```
or to test it out without connection to openHAB something like 
```
py main.py -v  -o
System name: My Inverter Farm
Inverter:
                Name: Whatever name you want
                Serial: 2130XXXXXX
                Bluetooth address: 00:80:25:XX:XX:XX
                OpenHab URL: XXX.XXX.XXX.XXX:8080
                Keys and Passwords not shown.
Trying BT address: 00:80:25:XX:XX:XX signal quality: 72.94 %
                At Sat, 18 Mar 2023 19:55:01 GMT Standard Time Daily generation was:     10307 Wh
                At Sat, 18 Mar 2023 18:32:57 GMT Standard Time Total generation was:     31162588 Wh
                At Sat, 18 Mar 2023 19:54:25 GMT Standard Time Spot Power is:            0 W
                At Sat, 18 Mar 2023 19:55:00 GMT Standard Time Spot Temperature is:      0.00 °C
                At Sat, 18 Mar 2023 19:54:25 GMT Standard Time Spot AC Voltage is:       655.35 V
Skipping openHAB API export
```
Similarly the same command line options can be used on the compiled executable. 

## OpenHAB Installation

In openHAB you will need the REST API exposed, the exec binding installed, the whitelist defined and the following things and items defined.
Follow the the openHAB binding documentation for the Exec binding.  
Copy the the executable or Python files into the openHAB scripts directory.
It is assumed below that the executable named 'openhabsma' for debian has been build or copied into the openHAB scripts directory and that a valid sma.json file is also in the scripts file. If the python files are used then modification to the below will be required.


```
# Whitelist
# SMA SunnyBoy reader
/etc/openhab/scripts/openhabsma -s -f /etc/openhab/scripts/sma.json

``` 
You will have to edit the Whitelist with sudo nano exec.whitelist
In the whitelist I  am using the standalone compiled Python application 'openhabsma' built with pyinstaller, see above.

```  
Thing exec:command:openhabSMA @"F2_Loft" [command="/etc/openhab/scripts/openhabsma -s -f /etc/openhab/scripts/sma.json", interval=0, timeout=10, autorun=false]

```  
You can either set the interval of the Thing  as zero  and call it  from a rule or  set it  to something like 60 and leave it  to repeat day and night. A DSL rule is defined further below to call the the script regularly.

```                                                            
Number    SolarEnergyGeneratedToday   "Solar Energy [%.2f kWh]"                     
Number    SolarTotalEnergyGenerated   "Gross Solar Energy [%.2f MWh]"               
Number    SolarInverterSpotPower      "Solar Energy Spot Power [%d W]"              
Number    SolarInverterSpotTemp       "Solar Spot Tempurature [%.2f °C]"           
Number    SolarInverterSpotACVoltage  "Solar Spot AC Voltage [%.2f V]"              
Switch    OpenHABSMAStart             "Run SMA data capture [%s]"               {channel="exec:command:openhabSMA:run"}
DateTime  OpenHABSMALastRun           "SMA capture time [%1$tA, %1$tH:%1$tM]"   {channel="exec:command:openhabSMA:lastexecution"}
String    OpenHABSMALastOut           "SMA capture result "                     {channel="exec:command:openhabSMA:output"}
Number    OpenHABSMALastExit          "SMA capture exit number"                 {channel="exec:command:openhabSMA:exit"}
```

The simple DSL rule below uses the Astro binding and items to trigger the executable once  a minute 
```
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

var Boolean solarDayTime = false

rule "Get Solar values"
    when
        Item onceAMinute changed to ON
    then
        val now =  ZonedDateTime.now()
        if ((now.isBefore((AstroSunDataRiseStart.state as DateTimeType).getZonedDateTime())) || (now.isAfter((AstroSunDataSetEnd.state as DateTimeType).getZonedDateTime()))){
            //the sun is down
            solarDayTime = false
            return
        } 
        //the sun is up
        solarDayTime = true
        OpenHABSMAStart.sendCommand(ON)
end
```  

# Project Extension: Export to PV.Out 

First make an account at pvoutput.org and get an API key: <https://pvoutput.org/help/managed_systems.html?highlight=api%20key>

Install the HTTP binding and create the following thing with your credentials: ApiKey and PVOutput system Id
``` 
Thing http:url:pvoutput "PVOutput.org" [
    baseURL = "https://pvoutput.org", commandMethod = "POST",
    headers = "X-Pvoutput-Apikey=xxxxxxxxxxxxxxxxxxxxxxx","X-Pvoutput-SystemId=XXXXX","X-Rate-Limit=1",
    refresh = 43200] {
        Channels:
        Type string : PVOutResponse "pvoutresponse" [stateTransformation="REGEX:.*<title>(.*?)<\\/title>.*", commandExtension="/service/r2/addstatus.jsp?%2$s"]
        //Type string : PVOutRate "pvrate" [stateExtension=""]
    }
``` 
Add the following DSL rule in the samee rule file as above.

``` 
rule "Upload to PVOutput"
    when
        Item testSwitch changed or
        Item onceAMinute changed to ON
    then
        if (! solarDayTime)return;                                       // if night don't  do anything
        var now =((ZonedDateTime.now().minute.intValue)-1) % 5
        if (now != 0) return;                                           // only continue if its 1,6,11,16,21 ... mins past the hour
        var testString = ""
        var sampleDateTime = (OpenHABSMALastRun.state as DateTimeType).getZonedDateTime
        testString = sampleDateTime.format(DateTimeFormatter.ofPattern("yyyyMMdd"))    // get date in the desired format
        testString = testString + "&t=" + sampleDateTime.format(DateTimeFormatter.ofPattern("HH:mm")).toString      // add the time in the desired format
        testString = String::format("d=%1$8s&v1=%2$d&v2=%3$d&v5=%4$.1f&v6=%5$.1f", testString, (1000*(SolarEnergyGeneratedToday.state as Number)).intValue(), (SolarInverterSpotPower.state as Number).intValue(), (SolarInverterSpotTemp.state as Number).floatValue, (SolarInverterSpotACVoltage.state as Number).floatValue)
        // Send to PVOutput.org
        PVOutResponse.sendCommand(testString)
end
``` 