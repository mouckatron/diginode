#! /usr/bin/env python

import re
import subprocess
import RPi.GPIO as GPIO
import sys
import time
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient

fanduty = 50
aim_temp = 37.5
via_mqtt = True

fanpin = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(fanpin, GPIO.OUT)
pi_pwm = GPIO.PWM(fanpin, 1000)
pi_pwm.start(fanduty)

influx_client = InfluxDBClient(url='http://localhost:8086', token="-gePSnb83Eq28xUGuX-ry-MHVbDZFdpC5OmfjgNH4M2J4dLgg59Oyc8uifMS4ie-_oNTrPZeGjEMroxA_J_4gQ==", org="CentralOps")
influx_write_client = influx_client.write_api()

temp_re = re.compile('[^0-9.]')
def get_temp():
    result = subprocess.run("sensors | grep temp1 | cut -d: -f2", shell=True, capture_output=True)
    temp = temp_re.sub('', result.stdout.decode('utf-8').strip())
    return float(temp)

def inc_fan(fanduty):
    if fanduty < 100:
        fanduty += 1
    pi_pwm.ChangeDutyCycle(fanduty)
    return fanduty

def dec_fan(fanduty):
    if fanduty > 1:
        fanduty -= 1
    pi_pwm.ChangeDutyCycle(fanduty)
    return fanduty

def on_message(client, userdata, message):
    global fanduty, influx_write_client

    temp = float(message.payload.decode("utf-8"))
    if temp < aim_temp:
        fanduty = dec_fan(fanduty)
    else:
        fanduty = inc_fan(fanduty)

    influx_write_client.write('CentralOps', 'CentralOps', ["fan_pwm pwm={value} {timestamp}".format(
        value=fanduty,
        timestamp=time.time_ns())])

    print("{} {:.2} {}".format(temp, (temp - aim_temp), fanduty))


if __name__ == '__main__':
    if via_mqtt:
        client = mqtt.Client("fan_speed")
        client.on_message=on_message
        client.connect("localhost")
        client.loop_start()
        client.subscribe("hosts/centralops/sensors/cpu_temp")
        while True:
            time.sleep(10)

    else:
        while True:
            temp = get_temp()

            if temp < aim_temp:
                fanduty = dec_fan(fanduty)
            else:
                fanduty = inc_fan(fanduty)

            print("{} {:.2} {}".format(temp, (temp - aim_temp), fanduty))

            time.sleep(5)

