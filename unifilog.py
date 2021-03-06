#!/usr/bin/env python

from unifi.controller import Controller
import time
import datetime
import math
import argparse
import sys
# import pytz

# local_tz = pytz.timezone('Europe/Berlin')

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--controller", help="host of the UniFi-controller (unifi)", default="unifi")
parser.add_argument("-u", "--user", help="username for controller access (ubnt)", default="ubnt")
parser.add_argument("-p", "--password", help="password for controller access (ubnt)", default="ubnt")
parser.add_argument("-f", "--file", help="output file for log messages (unifi.log)", default="unifi.log")
parser.add_argument("-t", "--timestamp", help="timestamp file (unifitimestamp.cfg)", default="unifitimestamp.cfg")
args = parser.parse_args()

def get_ap_hostname(mac):
    for ap in aps:
        if ap['mac'] == mac:
            return ap['name']

def duration_time_format(seconds):
    delay = datetime.timedelta(seconds= seconds)
    if (delay.days >= 2):
        out = str(delay).replace(" days, ", ":")
    elif (delay.days == 1):
        out = str(delay).replace(" day, ", ":")
    else:
        out = "0:" + str(delay)
    outAr = out.split(':')
    outAr = ["%02d" % (int(float(x))) for x in outAr]
    out   = ":".join(outAr)
    return out

def write_to_logfile(data):
    with open (args.file, 'a') as file:
        file.write(data)
        file.write('\n')

def get_last_timestamp():
    try:
        with open (args.timestamp, 'r+') as file:
            timestamp = file.readline()
            if timestamp:
                return int(timestamp)
    except:
        return 0

def set_timestamp(timestamp):
    with open (args.timestamp, 'w') as file:
        file.write('%s\n' % str(timestamp))

def unixtimestamp_to_datetime(timestamp):
    mytime = datetime.datetime.fromtimestamp(timestamp/1000)
    mytime.replace(microsecond = (timestamp % 1000) * 1000)
    return mytime


try:
    chost = args.controller
    c = Controller(chost, args.user, args.password)
except Exception:
    logdata = "%s %s Connection error to host = %s, error = %s" % (time.strftime("%b %d %H:%M:%S"), chost, chost, sys.exc_info()[1])
    write_to_logfile(logdata)
    sys.exit()

try:
    aps = c.get_aps()
except Exception:
    logdata = "%s %s Connection error to host = %s, error = %s" % (time.strftime("%b %d %H:%M:%S"), chost, chost, sys.exc_info()[1])
    write_to_logfile(logdata)
    sys.exit()

users = c.get_users()
clients = c.get_clients()
storedtimestamp = unixtimestamp_to_datetime(get_last_timestamp())
message = {}
for event in c.get_events():

    timestamp = unixtimestamp_to_datetime(event['time'])
    logprefix = "%s %s " % (timestamp.strftime("%b %d %H:%M:%S"), chost)
    if (timestamp > storedtimestamp) or (storedtimestamp == 0):
        # Check if event is not an AP Connect/Disconnect Event and collect
        # user data (AP Events don't have a user key in data.)
        ip = ''
	clienthost=''
        if event.has_key('user'):
            for user in users:
                if event['user'] == user['mac']:
                    if user.has_key('hostname'):
                        clienthost = "Client_host = %s, " % (user['hostname'])
                    else:
                        clienthost = ''
                    for client in clients:
                        if event['user'] == client['mac']:

                            ip = "Client_IP = %s " % (client['ip']) if (client.has_key('ip')) else '';
            clientmac = "Client_MAC = %s, " % (event['user'])

        if event['key'] == "EVT_WU_Roam":
            from_ap = "roams from_AP = %s, " % (get_ap_hostname(event['ap_from']))
            to_ap = "to_AP = %s, " % (get_ap_hostname(event['ap_to']))

            from_channel = "from_channel = %s " % (event['channel_from'])
            to_channel = "to_channel = %s" % (event['channel_to'])
            message[event['time']] = "%s%s%s%s%s%s%s%s" % (logprefix, clienthost, clientmac, ip, from_ap, from_channel, to_ap,  to_channel)
        elif event['key'] == "EVT_WU_RoamRadio":
            ap_name = "at_AP = %s " % (get_ap_hostname(event['ap']))
            from_channel = "roams from_channel = %s " % (event['channel_from'])
            to_channel = "to_channel = %s" % (event['channel_to'])
            message[event['time']] = "%s%s%s%s%s%s%s" % (logprefix, clienthost, clientmac, ip, ap_name, from_channel, to_channel)
        elif event['key'] == "EVT_AP_Connected":
            ap_name = event['ap_name'] if (event.has_key('ap_name')) else ''
            ap_mac = event['ap']
            message[event['time']] = "%sAP %s (%s) was connected" % (logprefix, ap_name, ap_mac)
        elif event['key'] == "EVT_AP_Disconnected":
            ap_name = event['ap_name'] if (event.has_key('ap_name')) else ''
            ap_mac = event['ap']
            message[event['time']] = "%sAP %s (%s) was disconnected" % (logprefix, ap_name, ap_mac)
        elif event['key'] == "EVT_WU_Connected":
            ap_name = "at-AP = %s, " % (get_ap_hostname(event['ap']))
            ssid = "has connected to SSID = %s, " % (event['ssid'])
            channel = "to_channel = %s" % (event['channel'])
            message[event['time']] = "%s%s%s%s%s%s%s" % (logprefix, clienthost, clientmac, ip, ssid, ap_name, channel)
        elif event['key'] == "EVT_WU_Disconnected":
            ap_name = "from-AP = %s, " % (get_ap_hostname(event['ap']))
            ssid = "has disconnected from SSID = %s, " % (event['ssid'])
            duration = "Usage: duration = %s, " % (duration_time_format(event['duration']))
            totalbytes = "volume = %s" % event['bytes']
            message[event['time']] = "%s%s%s%s%s%s%s" %(logprefix, clienthost, clientmac, ip, ssid, duration, totalbytes)
        elif event['key'] == "EVT_AP_Restarted":
            ap_name = event['ap_name'] if (event.has_key('ap_name')) else ''
            ap_mac = event['ap']
            admin = event['admin']
            message[event['time']] = "%sAP %s (%s) was restarted by %s" % (logprefix, ap_name, ap_mac, admin)
        elif event['key'] == "EVT_AP_Adopted":
            ap_name = get_ap_hostname(event['ap'])
            ap_mac = event['ap']
            admin = event['admin']
            message[event['time']] = "%sAdoption of AP = %s (%s) by %s" % (logprefix, ap_name, ap_mac, admin)
        elif event['key'] == "EVT_AP_UpgradeScheduled":
            ap_name = get_ap_hostname(event['ap'])
            ap_mac = event['ap']
            admin = event['admin']
            message[event['time']] = "%sUpgrade of AP = %s (%s) was scheduled by %s" % (logprefix, ap_name, ap_mac, admin)
        elif event['key'] == "EVT_AP_Upgraded":
            ap_name = get_ap_hostname(event['ap'])
            ap_mac = event['ap']
            version_from = event['version_from']
            version_to = event['version_to']
            message[event['time']] = "%sAP = %s (%s) was upgraded from AP_old = %s to AP_new = %s" % (logprefix, ap_name, ap_mac, version_from, version_to)
        elif event['key'] == "EVT_AP_Lost_Contact":
            ap_name = get_ap_hostname(event['ap'])
            ap_mac = event['ap']
            message[event['time']] = "%sAP = %s (%s) was disconnected" % (logprefix, ap_name, ap_mac)
        else:
            message[event['time']] = "%s MSG %s %s" % (logprefix, event['key'], event['msg'])

# if logdata is generated, sort it and prepare it for logfile storage
# Then update Timestamps in unifitimestamp.cfg file.
if message:
    # message.sort()
    logdata = '\n'.join(sorted(message.values()))
    write_to_logfile(logdata)
    maxkey = max(message.keys(), key=int)
    set_timestamp(maxkey)

#
# get some statistics...
logprefix = "%s %s " % (time.strftime("%b %d %H:%M:%S"), chost)
for stats in c.get_statistics(time.time(), 7400):
    if stats.has_key('num_sta'):
	#not in 4.x,5.x#Traff = stats['bytes'] if (stats.has_key('bytes')) else 0
	Traff = stats['wlan_bytes'] if (stats.has_key('wlan_bytes')) else 0
	#not in 4.x#tx_Pa = stats['tx_packets'] if (stats.has_key('tx_packets')) else 0
        #not in 4.x#tx_By = stats['tx_bytes'] if (stats.has_key('tx_bytes')) else 0
        #not in 4.x#tx_Er = stats['tx_errors'] if (stats.has_key('tx_errors')) else 0
        #not in 4.x#tx_Re = stats['tx_retries'] if (stats.has_key('tx_retries')) else 0
        #not in 4.x#rx_Pa = stats['rx_packets'] if (stats.has_key('rx_packets')) else 0
        #not in 4.x#rx_By = stats['rx_bytes'] if (stats.has_key('rx_bytes')) else 0
        #not in 4.x#rx_Fr = stats['rx_frags'] if (stats.has_key('rx_frags')) else 0

	# get APs connected/disconnected from healh status, new in 4.x
	for hea in c.get_health():
            ap_act = hea['num_ap'] if (hea.has_key('num_ap')) else 0
	    ap_disc = hea['num_disconnected'] if (hea.has_key('num_disconnected')) else 0
	    ap_users = hea['num_user'] if (hea.has_key('num_user')) else 0
	    # new in 4.x, 5.x:
	    tx_By = hea['tx_bytes-r'] if (hea.has_key('tx_bytes-r')) else 0
	    rx_By = hea['rx_bytes-r'] if (hea.has_key('rx_bytes-r')) else 0
            #3.x-version#logdata = "%sstatistics: Stations_connected = %s, Traffic = %s, tx_Packets = %s, tx_Bytes = %s, tx_Errors = %s, tx_Retries = %s, rx_Packets = %s, rx_Bytes = %s, rx_Frags = %s, h_APs = %s, h_APdisc = %s, h_Users = %s" % (logprefix, stats['num_sta'], Traff, tx_Pa, tx_By, tx_Er, tx_Re, rx_Pa, rx_By, rx_Fr, ap_act, ap_disc, ap_users)
            logdata = "%sstatistics: Stations_connected = %s, Traffic = %s, tx_Bytes = %s, rx_Bytes = %s, APs_act = %s, APs_disc = %s, AP_Clients = %s" % (logprefix, stats['num_sta'], Traff, tx_By, rx_By, ap_act, ap_disc, ap_users)
            write_to_logfile(logdata)
	    break

    break
