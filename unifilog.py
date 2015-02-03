#!/usr/bin/env python

from unifi.controller import Controller
import time
import datetime
import math
import argparse
import pytz

local_tz = pytz.timezone('Europe/Berlin')

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--controller", help="specifies host of the controller")
parser.add_argument("-u", "--user", help="specifies username for controller access")
parser.add_argument("-p", "--password", help="specifies password for controller access")
parser.add_argument("-a", "--getall", help="fetches the complete event data from controller", action="store_true")

args = parser.parse_args()

def utc_to_local(utc_dt):

    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt

def convertSize(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def get_ap_hostname(mac):
    for ap in aps:
        if ap['mac'] == mac:
            return ap['name']

def duration_time_format(seconds):
    delay = datetime.timedelta(seconds= seconds)
    if (delay.days > 0):
        out = str(delay).replace(" days, ", ":")
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
                return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f\n")
    except:
        return datetime.datetime.now() - datetime.timedelta(minutes= 10)


def set_timestamp():
    with open ('unifitimestamp.cfg', 'w') as file:
        file.write('%s\n' % str(datetime.datetime.now()))

c = Controller(args.controller, args.user, args.password)
aps = c.get_aps()
users = c.get_users()
clients = c.get_clients()
log = []

storedtimestamp = get_last_timestamp().replace(tzinfo=local_tz);
# storedtimestamp = storedtimestamp

for event in c.get_events():
    timestamp = utc_to_local(datetime.datetime.strptime(event['datetime'], "%Y-%m-%dT%H:%M:%SZ"))
    logprefix = "%s unifi " % (timestamp.strftime("%b %d %H:%M:%S"))
    if timestamp >= ( timestamp if (args.getall) else storedtimestamp):
        # Cheeck if event is not an AP Connect/Disconnect Event and collect
        # user data (AP Events don't have a user key in data.)
        if event.has_key('user'):
            for user in users:
                if event['user'] == user['mac']:
                    if user.has_key('hostname'):
                        clienthost = "Client-host = %s, " % (user['hostname'])
                    else:
                        clienthost = ''
                    for client in clients:
                        ip = ''
                        if event['user'] == client['mac']:

                            ip = "Client-IP = %s " % (client['ip']) if (client.has_key('ip')) else '';
            clientmac = "Client-MAC = %s, " % (event['user'])

        if event['key'] == "EVT_WU_Roam":
            from_ap = "roams from-AP = %s, " % (get_ap_hostname(event['ap_from']))
            to_ap = "to-AP = %s, " % (get_ap_hostname(event['ap_to']))

            from_channel = "from-channel = %s " % (event['channel_from'])
            to_channel = "to-channel = %s" % (event['channel_to'])

            log.append("%s%s%s%s%s%s%s%s" % (logprefix, clienthost, clientmac, ip, from_ap, from_channel, to_ap,  to_channel))
        elif event['key'] == "EVT_WU_RoamRadio":
            ap_name = "at-AP = %s " % (get_ap_hostname(event['ap']))
            from_channel = "roams from-channel = %s " % (event['channel_from'])
            to_channel = "to-channel = %s" % (event['channel_to'])
            log.append("%s%s%s%s%s%s%s" % (logprefix, clienthost, clientmac, ip, ap_name, from_channel, to_channel))
        elif event['key'] == "EVT_AP_Connected":
            ap_name = event['ap_name']
            ap_mac = event['ap']
            log.append("%s AP %s (%s) was connected" % (logprefix, ap_name, ap_mac))
        elif event['key'] == "EVT_AP_Disconnected":
            ap_name = event['ap_name']
            ap_mac = event['ap']
            log.append("%s AP %s (%s) was disconnected" % (logprefix, ap_name, ap_mac))
        elif event['key'] == "EVT_WU_Connected":
            ap_name = "at-AP = %s, " % (get_ap_hostname(event['ap']))
            ssid = "has connected to SSID = %s, " % (event['ssid'])
            channel = "to-channel = %s" % (event['channel'])
            log.append("%s%s%s%s%s%s%s" % (logprefix, clienthost, clientmac, ip, ssid, ap_name, channel))
        elif event['key'] == "EVT_WU_Disconnected":
            ap_name = "from-AP = %s, " % (get_ap_hostname(event['ap']))
            ssid = "has disconnected from SSID = %s, " % (event['ssid'])
            duration = "Usage: duration = %s, " % (duration_time_format(event['duration']))
            totalbytes = "volume = %s" % convertSize(event['bytes'])
            log.append("%s%s%s%s%s%s%s" %(logprefix, clienthost, clientmac, ip, ssid, duration, totalbytes))
        else:
            log.append("%s MSG %s %s" % logprefix, event['key'], event['msg'])

# if logdata is generated, sort it and prepare it for logfile storage
# Then update Timestamps in unifitimestamp.cfg file.
if log:
    log.sort(key=lambda x: datetime.datetime.strptime(str.join(' ', x.split(None)[0:3]), "%b %d %H:%M:%S"))
    logdata = '\n'.join(log)
    write_to_logfile(logdata)
    set_timestamp()
