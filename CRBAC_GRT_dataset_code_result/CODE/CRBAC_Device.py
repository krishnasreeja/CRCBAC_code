# CRBAC_Gateway_Grant_transfer.py grnat transfer revok xor time done completly
import asyncio
import csv
import time
import psutil
from aiocoap import Context, Message, PUT, error
import os
pid = os.getpid()
Eelec = 50.0  # Energy consumption rate for transmitting one bit (nJ/bit)
Eamp = 0.1   # Energy consumption rate for power amplifier (nJ/bit/m^2)
d = 1.0     
handshakeDuration = -1
sendMsgSize_bytes = -1
receiveMsgSize_bytes = -1

hash_secret_key = "1dcdbff4c6fb0d47e6bea745d3033bad4c8b2166ff6c1408b2bd52a162a594d6"
def xor_encode(data, key):
    encoded_data = []
    for i in range(len(data)):
        encoded_char = chr(ord(data[i]) ^ ord(key[i % len(key)]))
        encoded_data.append(encoded_char)
    return ''.join(encoded_data)
def xor_decode(data, key):
        decoded_data = []
        for i in range(len(data)):
            decoded_char = chr(ord(data[i]) ^ ord(key[i % len(key)]))
            decoded_data.append(decoded_char)
        return ''.join(decoded_data)

async def read_input_data(file_path):
    # Read input data from the CSV file
    with open(file_path, 'r', encoding="utf-8-sig") as file:
        csv_reader = csv.reader(file, delimiter='\t')
        next(csv_reader)  # Skip the header line
        input_data = '\n'.join(['\t'.join(row) for row in csv_reader])
  
    return input_data


async def send_coap_request(input_data):
    try:
        context = await Context.create_client_context()   
        current_time = time.strftime("%H:%M:%S") # Get the current time (t1)
        # Modify the input data to include the time (t1)
        parts = input_data.split('\t')
        parts.append(current_time)
        input_data = ','.join(parts)
     
        # XOR encode the input line with the secret_key
        encoded_line = xor_encode(input_data, hash_secret_key)
        payload=encoded_line.encode()
        sendMsgSize_bytes = len(payload)
        # print(f"sent msg payload size is .......{sendMsgSize_bytes} bytes")
        memory_before = psutil.Process(pid).memory_info().rss
        start_time = time.perf_counter()
        request = Message(code=PUT, payload=encoded_line.encode(), uri="coap://localhost/auth")
        response = await context.request(request).response
        end_time = time.perf_counter()
        memory_after = psutil.Process(pid).memory_info().rss
        memory_used = memory_after - memory_before
        response_time = (end_time - start_time) * 1e3
        # print("input data is ",input_data)
        handshakeDuration=  0
        receiveMsgSize_bytes =len(response.payload)     # Get the size of the sent message
        sendEnergy = (Eelec * sendMsgSize_bytes) + (Eamp * sendMsgSize_bytes * d * d)
        receiveEnergy = Eelec * receiveMsgSize_bytes
        totalEnergy = sendEnergy + receiveEnergy
        memory_used_KB=memory_used / 1024
        return response, response_time,totalEnergy, memory_used_KB,handshakeDuration ,sendMsgSize_bytes, receiveMsgSize_bytes,sendEnergy,receiveEnergy
        
    except error.RequestTimedOut:
        print("CoAP request timed out.")
    except error.RequestCancelled:
        print("CoAP request cancelled.")
    except error.RequestError as e:
        print("CoAP request error:", e)
    except Exception as e:
        print("An error occurred:", e)

def process_response(response):
    if response is None:
        print("No response received.")
        return

    response_payload = response.payload.decode()
    decode_response = xor_decode(response_payload, hash_secret_key)
    response_lines = decode_response.split('\n') 
    print("response ", response_lines)   
        
async def main():
    
    # Specify the path to your input CSV file
    csv_file = r"D:\Mongo_DB\CRBAC_GRT_POLICY_FILES\transfer_10.csv" 
    input_data = await read_input_data(csv_file)
    
    header = ['Response Time(MS)',' Energy consumption (in nJ)','Memory utilization (in KB) ','handshakeDuration(MS)','Communication_cost(bytes)','receiveMsgSize_bytes','sendEnergy(nJ)','receiveEnergy(nJ)']
    with open("client_response_time_555.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)  # Add header line
        for line in input_data.split('\n'):
           
            response, response_time,totalEnergy,memory_used_KB,handshakeDuration,sendMsgSize_bytes, receiveMsgSize_bytes,sendEnergy,receiveEnergy = await send_coap_request(line)
            process_response(response)
            writer.writerow([response_time,totalEnergy, memory_used_KB,handshakeDuration, sendMsgSize_bytes, receiveMsgSize_bytes,sendEnergy,receiveEnergy])
            # print("Response time is....... ", response_time)
            # print(f"handshake duration: { handshakeDuration } milliseconds")
            # print(f"memory usage: {memory_used_KB }  KB")
            # print("Communication cost (send message size):", sendMsgSize_bytes, "bytes")
            # print(f"receive msg size is .........{receiveMsgSize_bytes} bytes")
            # print("Sending Energy:", sendEnergy, "nJ")
            # print("Receiving Energy:", receiveEnergy, "nJ")
            # print("Total Energy:", totalEnergy, "nJ")



            

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
