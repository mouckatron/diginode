#! /usr/bin/env python3

import sensors
import paho.mqtt.client as mqtt
import time
from influxdb_client import InfluxDBClient

mqtt_on = True
influx_on = True

if mqtt_on:
	mqtt_client = mqtt.Client("CentralOps")
	mqtt_client.connect("localhost")

if influx_on:
	influx_client = InfluxDBClient(url='http://localhost:8086', token="-gePSnb83Eq28xUGuX-ry-MHVbDZFdpC5OmfjgNH4M2J4dLgg59Oyc8uifMS4ie-_oNTrPZeGjEMroxA_J_4gQ==", org="CentralOps")
	influx_write_client = influx_client.write_api()

sensors.init()

def get_value():
    sensors.init()
    try:
        for chip in sensors.iter_detected_chips():
            if str(chip) == "cpu_thermal-virtual-0":
                for feature in chip:
                    if feature.label == "temp1":
                        return feature.get_value()
    finally:
        sensors.cleanup()

while True:
    value = get_value()
    print(value)

    if mqtt_on:
        mqtt_client.publish("hosts/centralops/sensors/cpu_temp", value)

    if influx_on:
        influx_write_client.write('CentralOps', 'CentralOps', ["cpu_temp temp={temp} {timestamp}".format(
            temp=value,
            timestamp=time.time_ns())])

    time.sleep(10)
