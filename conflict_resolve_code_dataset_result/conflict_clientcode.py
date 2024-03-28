
# import csv
# import asyncio
# import json
# from aiocoap import *
# import time

# async def read_input_csv(filename):
#     input_data = []
#     with open(filename, mode='r') as input_file:
#         reader = csv.reader(input_file)
#         for row in reader:
            
#             line = ",".join([row[0], row[1], row[2]])  # Append timestamp to each line
#             input_data.append(line)
#     return input_data

# async def send_coap_request(input_data, server_uri):
#     context = await Context.create_client_context()
    
#     try:
#         start_time = time.perf_counter()  # Record the start time
#         request = Message(code=POST, payload="\n".join(input_data).encode('utf-8'), uri=server_uri)
#         response = await context.request(request).response
#         end_time = time.perf_counter()  # Record the end time
#         processing_time = (end_time - start_time)*1e3
#         print("processing time is ...",processing_time)
        
#         # Decode the response payload
#         decoded_payload = response.payload.decode('utf-8')
        
#         # Parse the response payload as JSON
#         response_data = json.loads(decoded_payload)
        
#         # Extract the result and t2 timestamp from the response data
#         result = response_data['result']
#         # t2 = response_data['t2']
        
#         print("Result:", result)
#         # print("Timestamp t2:", t2)

#     except Exception as e:
#         print("Error:", e)

# def main():
#     input_csv_filename = 'data_rct10.csv'
#     server_uri = "coap://127.0.0.1/auth"
#     loop = asyncio.get_event_loop()
#     input_data = loop.run_until_complete(read_input_csv(input_csv_filename))
#     loop.run_until_complete(send_coap_request(input_data, server_uri))
    
# if __name__ == "__main__":
#     main()

# belo code with csv and calculation perameters

import csv
import asyncio
import json
import time
import os
from aiocoap import Context, Message, POST
import psutil
pid = os.getpid()
Eelec = 50.0  # Energy consumption rate for transmitting one bit (nJ/bit)
Eamp = 0.1   # Energy consumption rate for power amplifier (nJ/bit/m^2)
d = 1.0     
sendMsgSize_bytes = -1
receiveMsgSize_bytes = -1
async def read_input_csv(filename):
    input_data = []
    with open(filename, mode='r') as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            line = ",".join([row[0], row[1], row[2]])  # Append timestamp to each line
            input_data.append(line)
    return input_data

async def send_coap_request(input_data, server_uri):
    context = await Context.create_client_context()

    try:
        payload="\n".join(input_data).encode('utf-8')
        sendMsgSize_bytes = len(payload)
        # print(f"sent msg payload size is .......{sendMsgSize_bytes} bytes")
        start_time = time.perf_counter()  # Record the start time
        memory_before = psutil.Process(pid).memory_info().rss
        request = Message(code=POST, payload="\n".join(input_data).encode('utf-8'), uri=server_uri)
        response = await context.request(request).response
        end_time = time.perf_counter()  # Record the end time
        receiveMsgSize_bytes =len(response.payload)     # Get the size of the sent message
        # print(f"receive msg size is .........{receiveMsgSize_bytes} bytes")
        memory_after = psutil.Process(pid).memory_info().rss
        memory_used = memory_after - memory_before
        memory_used_kb= (memory_used / 1024)
        processing_time = (end_time - start_time) * 1e3
        sendEnergy = (Eelec * sendMsgSize_bytes) + (Eamp * sendMsgSize_bytes * d * d)
        receiveEnergy = Eelec * receiveMsgSize_bytes
        totalEnergy = sendEnergy + receiveEnergy

        # Decode the response payload
        decoded_payload = response.payload.decode('utf-8')

        # Parse the response payload as JSON
        response_data = json.loads(decoded_payload)

        # Extract the result and t2 timestamp from the response data
        result = response_data['result']
        # t2 = response_data['t2']

        print("Result:", result)
        # print("Timestamp t2:", t2)
        # print("processing time",processing_time)
        # print("  Bytes:", memory_used)
        # print("  Kilobytes (KB):", memory_used_kb)
        # print("  Megabytes (MB):", memory_used / (1024 * 1024))
        # print("Sending Energy:", sendEnergy, "nJ")
        # print("Receiving Energy:", receiveEnergy, "nJ")
        # print("Total Energy:", totalEnergy, "nJ")
        return processing_time, memory_used_kb,totalEnergy,sendEnergy,receiveEnergy  #Return processing time ,mem usage,energy consumption

    except Exception as e:
        print("Error:", e)

def write_processing_time_to_csv(processing_time, memory_used_kb ,totalEnergy ,sendEnergy,receiveEnergy ,output_csv_filename):
    header = ["Processing Time (ms)","memory_used(KB)","totalEnergy(nJ)","sendEnergy(nJ)","receiveEnergy(nJ)" ]
    with open(output_csv_filename, mode='a', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(header)
        writer.writerow([processing_time, memory_used_kb ,totalEnergy,sendEnergy,receiveEnergy ])

def main():
    input_csv_filename = 'data_rct30.csv'
    server_uri = "coap://127.0.0.1/auth"
    output_csv_filename = 'client_response_time_555.csv'  # Adjust the filename as needed

    loop = asyncio.get_event_loop()
    input_data = loop.run_until_complete(read_input_csv(input_csv_filename))
    processing_time, memory_used ,totalEnergy,sendEnergy,receiveEnergy   = loop.run_until_complete(send_coap_request(input_data, server_uri))
    write_processing_time_to_csv(processing_time, memory_used ,totalEnergy ,sendEnergy,receiveEnergy,output_csv_filename)

if __name__ == "__main__":
    main()
