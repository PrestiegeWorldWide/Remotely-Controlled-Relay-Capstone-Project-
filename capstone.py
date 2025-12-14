import serial
import time
import datetime
import os
import sys
import json
import hmac
import hashlib
import base64
import urllib.parse
import serial #non base package, import this
import paho.mqtt.client as mqtt #non base package, import this

# --- Configuration ---
IOTHUB_HOSTNAME = "borg.azure-devices.net"  # HostName=
DEVICE_ID = "thispc"  # DeviceId=
DEVICE_KEY = "HslNQV8/pOb8FKYkEbfxpWCquDncjVTRtNl1bMJGPRc="  # SharedAccessKey=
SAS_TTL = 3600
LINUX_SERIAL_PORT = '/dev/ttyACM0'
WINDOWS_SERIAL_PORT = 'COM4'
BAUD_RATE = 9600
SERIAL_TIMEOUT = 3
SERIAL_CONFIGURATION = [WINDOWS_SERIAL_PORT, BAUD_RATE] #first element is port, second element is buad rate.

ser = serial.Serial(SERIAL_CONFIGURATION[0], SERIAL_CONFIGURATION[1], timeout=1)


def generate_sas_token(hostname, device_id, key, ttl=SAS_TTL):
    resource_uri = f"{hostname}/devices/{device_id}"
    resource_uri_encoded = urllib.parse.quote(resource_uri.lower(), safe='')
    expiry = int(time.time()) + ttl
    string_to_sign = f"{resource_uri_encoded}\n{expiry}".encode("utf-8")
    key_bytes = base64.b64decode(key)
    signature = hmac.HMAC(key_bytes, string_to_sign, hashlib.sha256).digest()
    signature_encoded = urllib.parse.quote(
        base64.b64encode(signature), safe=''
    )
    sas_token = (
        f"SharedAccessSignature sr={resource_uri_encoded}"
        f"&sig={signature_encoded}&se={expiry}"
    )
    return sas_token

# DO NOT UPDATE THIS
def create_mqtt_client():
    sas_token = generate_sas_token(IOTHUB_HOSTNAME, DEVICE_ID, DEVICE_KEY)
    client_id = DEVICE_ID
    username = f"{IOTHUB_HOSTNAME}/{DEVICE_ID}/?api-version=2020-09-30"
    password = sas_token
    
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(username=username, password=password)
    client.tls_set()  # use system CAs
    client.connect(IOTHUB_HOSTNAME, port=8883)
    return client


def sendPayload(payload_in):
    # TODO: Your code goes here!
    print("🚀 Starting Arduino to Azure IoT Hub Bridge...")
    
    client = create_mqtt_client()

    #Connects to Azure IoT Hub  
    client = create_mqtt_client()
    client.loop_start()
    
    #Define MQTT topic
    topic = f"devices/{DEVICE_ID}/messages/events/"
    
    #Main data streaming loop
    try:
        while True:
            payload = json.dumps(payload_in, indent=4)
            print(payload)
            result = client.publish(topic, payload)
            status = result[0]
            if status == mqtt.MQTT_ERR_SUCCESS:
                print(f"✅ payload sent to {IOTHUB_HOSTNAME}")
                break
            else:
                print("⚠️ Publish failed with status", status)
            time.sleep(1)
    
    except Exception as e:
        print(e)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting cleanly.")

    finally:
        print("terminating mqtt connection.")
        client.loop_stop()
        client.disconnect()


def send_Serial_Data(relay_number_char, relay_state_char):
    """
    Description:
        The purpose of this funtion is to send a two symbol command to the arduino via serial 
        to the Arduino's buffer.
    Parameters:
        [1] relay_number_char: (type: string) this should be a number between "1" and "8".
        [2] relay_state_char: (type: string) must be a "0" (relay OFF) or "1" (relay ON).
    Returns:
        This function does not return.
    Raises:
        This function will raise an Exception in the event of a keyboard interupt or incorrect parameter
        type or a connection error.
    """
    if not (isinstance(relay_number_char, str) and isinstance(relay_state_char, str)):
       raise Exception("Invalid parameter type, must be type string!")

    command_string = relay_number_char + relay_state_char + '\n'
    command_bytes = command_string.encode('utf-8')

    try:
        ser.write(command_bytes)
        print(f"Sent command: {command_string.strip()}")

    except serial.SerialException as e:
        print(f"Error connecting or communicating over serial: {e}")
        print("Please check if the correct port is specified and if the Arduino is connected.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def recieve_Serial_Data():
    """
    Description:
        The purpose of this funtion is to recieve a line of icoming data from pyserial's buffer and 
        decode it into a usable utf-8 string.
    Parameters:
        This function does not take in parameters. The serial connection is configured with the
        SERIAL_CONFIGURATION variable.
    Returns:
        This function returns the decoded line as type string.
    Raises:
        This function will raise an Exception in the event of a keyboard interupt or other type of error.
    """

    try:
        if ser.in_waiting > 0: 
            raw_line = ser.readline()
            decoded_byte = raw_line.decode('utf-8', errors='ignore').strip()
            print(f"Recievd byte: {decoded_byte}")
            return decoded_byte

    except KeyboardInterrupt:
        print("\n--- Program terminated by user ---")
        ser.close()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ser.close()
    return None


def Querry_Usr():
    """
    Description:
        The purpose of this funtion is to Querry the user with an options menu in the terminal.
        The numeric selection will be wrtiten to program variables using input(). The outputs from this
        function will be sent to the arduino as parameters for the updateRelay() function.
    Parameters:
        This function does not take in parameters.
    Returns:
        [1] usr_relay_number (type: string) this is the number that selects the relay.
        [2] usr_relay_state (type: string) this is the state to be applied to the relay.
        This function returns the input as two strings.
    Raises:
        This function will raise an Exception if the user input is the wrong type. The function will loop
        repeatedly until a valid input is recieved or a keyboard interupt is detected.
    """
    while True:
        try:
            print("""
                Select a relay to enable:
                [1] Relay 1
                [2] Relay 2
                [3] Relay 3
                [4] Relay 4
                [5] Relay 5
                [6] Relay 6
                """)
            usr_relay_number = input('Enter Number:') 
            
            if usr_relay_number == "exit":
                sys.exit()
            if int(usr_relay_number) > 6 or int(usr_relay_number) < 1:
                raise Exception("Enter a number between 1 and 8!")

            print("""
                Select a relay to enable:
                [0] Relay Off
                [1] Relay On
                """)

            usr_relay_state = input('Enter Number:') 
            if usr_relay_state == "exit":
                sys.exit()
            if usr_relay_state != "1"  and usr_relay_state != "0":
                raise Exception("Enter a 0 or a 1!")

            return usr_relay_number, usr_relay_state
        
        except KeyboardInterrupt:
            print("\n--- Program terminated by user ---")


def generatePayload(ACKcode, description="None"):
    """
    Description:
        This function breaks the acknowlegement code into two segments. The relay state variable is
        selected conditionaly based on wether the state part of the code is a 1 or 0.
    Parameters:
        [1] ACKCode (type: string) The input that contains the relay code and the state code.
        [2] Description (type: string) An optional description, defaults to "None". 
    Returns:
        Disctionary containing several key value pairs.
    Raises:
        Nothing.
    """
    ACKcode = "ACK:51"
    code = ACKcode.split(':')[1]
    relayNumber = "CR" + code[0]
    relayState = "On" if code[1] == '1' else "Off"
    #description conditionals go here

    current_time = str(datetime.datetime.now())
    return {'Device_ID': DEVICE_ID, 'DateTime': current_time, 'relay': relayNumber, 'state_changed_to': relayState, 'description': description}

if __name__ == "__main__":
    """note: recieve_Serial_data should be running constantly, 
    EXCEPT when an event from the queue needs to be sent by send_Serial_Data()"""

try:
    while True:
        relay_Number, relay_State = Querry_Usr()
        send_Serial_Data(relay_Number, relay_State)
        time.sleep(0.1)

        returnedByteString = recieve_Serial_Data()
        generated_payload = generatePayload(returnedByteString)
        sendPayload(generated_payload)

except KeyboardInterrupt:
    print("\nClosing serial port.")
finally:
    if ser.is_open:
        ser.close()
