#!/usr/bin/env python

from unifi.controller import Controller
import time
import datetime
import math
import argparse
# import pytz

# local_tz = pytz.timezone('Europe/Berlin')

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--controller", help="specifies host of the controller")
parser.add_argument("-u", "--user", help="specifies username for controller access")
parser.add_argument("-p", "--password", help="specifies password for controller access")

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
    with open ('unifi.log', 'a') as file:
        file.write(data)
        file.write('\n')

def get_last_timestamp():
    try:
        with open ('unifitimestamp.cfg', 'r+') as file:
            timestamp = file.readline()
            if timestamp:
                return int(timestamp)
    except:
        return 0

def set_timestamp(timestamp):
    with open ('unifitimestamp.cfg', 'w') as file:
        file.write('%s\n' % str(timestamp))

def unixtimestamp_to_datetime(timestamp):
    mytime = datetime.datetime.fromtimestamp(timestamp/1000)
    mytime.replace(microsecond = (timestamp % 1000) * 1000)
    return mytime

c = Controller(args.controller, args.user, args.password)
aps = c.get_aps()
users = c.get_users()
clients = c.get_clients()

storedtimestamp = unixtimestamp_to_datetime(get_last_timestamp())
message = {}
for event in c.get_events():

    timestamp = unixtimestamp_to_datetime(event['time'])
    logprefix = "%s unifi " % (timestamp.strftime("%b %d %H:%M:%S"))
    if (timestamp > storedtimestamp) or (storedtimestamp == 0):
        # Cheeck if event is not an AP Connect/Disconnect Event and collect
        # user data (AP Events don't have a user key in data.)
        if event.has_key('user'):
            for user in users:
                if event['user'] == user['mac']:
                    if user.has_key('hostname'):
                        clienthost = "Client_host = %s, " % (user['hostname'])
                    else:
                        clienthost = ''
                    for client in clients:
                        ip = ''
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
            ap_name = event['ap_name']
            ap_mac = event['ap']
            message[event['time']] = "%sAP %s (%s) was connected" % (logprefix, ap_name, ap_mac)
        elif event['key'] == "EVT_AP_Disconnected":
            ap_name = event['ap_name']
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
            ap_name = event['ap_name'] if (event.has_key('ap_name')) else '';
            ap_mac = event['ap']
            admin = event['admin']
            message[event['time']] = "%sAP %s (%s) was restarted by %s" % (logprefix, ap_name, ap_mac, admin)
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
for stats in c.get_statistics(time.time(), 3800):
    if stats.has_key('num_sta'):
	Traff = stats['bytes'] if (stats.has_key('bytes')) else 0
	tx_Pa = stats['tx_packets'] if (stats.has_key('tx_packets')) else 0
        tx_By = stats['tx_bytes'] if (stats.has_key('tx_bytes')) else 0
        tx_Er = stats['tx_errors'] if (stats.has_key('tx_errors')) else 0
        tx_Re = stats['tx_retries'] if (stats.has_key('tx_retries')) else 0
        rx_Pa = stats['rx_packets'] if (stats.has_key('rx_packets')) else 0
        rx_By = stats['rx_bytes'] if (stats.has_key('rx_bytes')) else 0
        rx_Fr = stats['rx_frags'] if (stats.has_key('rx_frags')) else 0
        logdata = "%sstatistics: Stations_connected = %s, Traffic = %s, tx_Packets = %s, tx_Bytes = %s, tx_Errors = %s, tx_Retries= %s, rx_Packets = %s, rx_Bytes = %s, rx_Frags = %s" % (logprefix, stats['num_sta'], Traff, tx_Pa, tx_By, tx_Er, tx_Re, rx_Pa, rx_By, rx_Fr)
        write_to_logfile(logdata)
	break
