#!/usr/bin/env python3

import subprocess
import time
import re
import logging

if __name__ == '__main__':
    reader = open('/var/tmp/monitor_battery.log', 'r')
    data = list(reader)
    reader.close()
    if len(data) >= 600:
        writer = open('/var/tmp/monitor_battery.log', 'w')
        for line in data[300:]:
            writer.write(line)
        writer.close()

    command = ['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0']
    ans = subprocess.check_output(command).decode()
    p = re.compile('percentage: *\d\d%')
    ans = p.findall(ans)[0][11:].strip()

    logger = logging.getLogger('monitor_battery')
    hdlr = logging.FileHandler('/var/tmp/monitor_battery.log')
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    logger.info('%s;%s' % (time.time(), ans))
