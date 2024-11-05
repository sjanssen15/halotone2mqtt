import asyncio
import websockets
import json
import base64
import binascii
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import json
import paho.mqtt.client as mqtt
import socket
import argparse
import time
from datetime import datetime

# Args
parser = argparse.ArgumentParser(description="MQTT Connection information")
parser.add_argument("printerip", type=str, help="The 3D printer IP address")
parser.add_argument("printerpass", type=str, help="The 3D printer password")
parser.add_argument("mqtt_topic", type=str, help="MQTT topic")
parser.add_argument("mqtt_user", type=str, help="MQTT username")
parser.add_argument("mqtt_password", type=str, help="MQTT user password")
parser.add_argument("mqtt_ip", type=str, help="MQTT broker IP")
parser.add_argument("mqtt_port", type=int, help="MQTT broker port")
args = parser.parse_args()

# Start
print(f"{datetime.now()} - Starting")
print(f"{datetime.now()} - Printer IP: {args.printerip}")
print(f"{datetime.now()} - MQTT broker: {args.mqtt_ip}")
print(f"{datetime.now()} - MQTT topic: {args.mqtt_topic}")
print(f"{datetime.now()} ----------------------------------------------")

# functions
## Get printer data
def get_printer_status(ip, password):
    wsuri = "ws://{}:18188".format(ip)
    key_hex = "6138356539643638"

    # Verify if device is online
    def is_device_online(ip, port=18188, timeout=2):
        try:
            # Create a socket and set a timeout
            with socket.create_connection((ip, port), timeout=timeout):
                return True  # Connection succeeded, device is online
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False  # Connection failed, device is likely offline

    # Usage example
    if is_device_online(ip):
        # Generate token
        def des_encrypt(password, key):
            cipher = DES.new(key, DES.MODE_ECB)
            padded_password = pad(password.encode('utf-8'), DES.block_size)
            encrypted = cipher.encrypt(padded_password)
            return base64.b64encode(encrypted).decode('utf-8')

        # Example usage
        key = binascii.unhexlify(key_hex)
        token = des_encrypt(password, key)

        # Generate message
        data = {
            "cmd": "GET_PRINT_STATUS",
            "token": token
        }
        message = json.dumps(data, indent=2)

        # Get status
        async def sent():
            async with websockets.connect(wsuri) as websocket:
                await websocket.send(message)
                response = await websocket.recv()

                loadjson = json.loads(response)
                if loadjson["printStatus"] == "PRINT_GENERAL":
                    return('{"bottomExposureNum":"0","curSliceLayer":"0","delayLight":"0","eleSpeed":"0","filename":"","initExposure":"0","layerThickness":"0","printExposure":"0","printHeight":"0","printRemainTime":"0","printStatus":"Ready to print","resin":"0","sliceLayerCount":"0"}')
                elif loadjson["printStatus"] == "PRINT_COMPLETE":
                    return('{"bottomExposureNum":"0","curSliceLayer":"0","delayLight":"0","eleSpeed":"0","filename":"","initExposure":"0","layerThickness":"0","printExposure":"0","printHeight":"0","printRemainTime":"0","printStatus":"Print Complete","resin":"0","sliceLayerCount":"0"}')
                else:
                    return response

        output = asyncio.get_event_loop().run_until_complete(sent())
        return output
    else:
        return("offline")

# Send payload to MQTT broker
while True:
    current_timestamp = datetime.now()
    # Initialize MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    # Connect to the broker
    client.username_pw_set(args.mqtt_user, args.mqtt_password)
    client.connect(args.mqtt_ip, args.mqtt_port)

    json_payload = get_printer_status(args.printerip,args.printerpass)
    
    if json_payload == "offline":
        print(f"{current_timestamp} - Printer is not reachable or offline, retrying in 10 seconds")
        json_payload = '{"bottomExposureNum":"0","curSliceLayer":"0","delayLight":"0","eleSpeed":"0","filename":"","initExposure":"0","layerThickness":"0","printExposure":"0","printHeight":"0","printRemainTime":"0","printStatus":"Offline","resin":"0","sliceLayerCount":"0"}'
        
    # Publish JSON payload to the specified topic    
    client.publish(args.mqtt_topic, json_payload)
    print(f"{current_timestamp} - Published offline message to {args.mqtt_topic}")
    # Disconnect after publishing
    client.disconnect()

    time.sleep(10)