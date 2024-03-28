# import threading
# import aiocoap
# import time
# import asyncio
# import csv

# async def send_request(client_id):
#     context = await aiocoap.Context.create_client_context()
#     payload = "Id33,ctx19,res1_read,AC" 
    			
#  # Modify with your desired input request
#     request = aiocoap.Message(code=aiocoap.PUT, payload=payload.encode())
#     request.set_request_uri('coap://localhost/auth')

#     try:
#         # start_time = time.time()  # Record start time
#         start_time = time.perf_counter() 

#         response = await context.request(request).response

#         end_time = time.perf_counter()   # Record end time micro sec
#         response_time =  (end_time - start_time) * 1e6
       

#         print(f"Client {client_id} received response with threads: {response.payload.decode()}")
#         print(f"Threading Response time for client {client_id}: {response_time} micro seconds")
#         with open('client_response_time_555.csv', 'a', newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow([client_id, response_time])

#         return response_time
       
#     except Exception as e:
#         print(f"Client {client_id} encountered an error: {str(e)}")


# def main():
    
#     threads = []
#     for client_id in range(1, 10):
#         thread = threading.Thread(target=asyncio.run, args=(send_request(client_id),))
#         threads.append(thread)
#         thread.start()

#     for thread in threads:
#         thread.join()

# if __name__ == "__main__":
#     main()

import threading
import aiocoap
import time
import asyncio
import csv

start_time = 0
end_time = 0

async def send_request(client_id):
    global start_time, end_time

    context = await aiocoap.Context.create_client_context()
    payload = "Id33,ctx19,res1_read,AC"

    request = aiocoap.Message(code=aiocoap.PUT, payload=payload.encode())
    request.set_request_uri('coap://localhost/auth')

    try:
        response = await context.request(request).response

        # print(f"Client {client_id} received response: {response.payload.decode()}")
        return response

    except Exception as e:
        print(f"Client {client_id} encountered an error: {str(e)}")


def main():
    global start_time, end_time
    
    start_time = time.perf_counter()  # Record start time

    threads = []
    for client_id in range(1, 11):
        thread = threading.Thread(target=asyncio.run, args=(send_request(client_id),))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.perf_counter()  # Record end time
    total_response_time = (end_time - start_time) * 1e6  # Calculate total response time in microseconds
    with open('client_response_time_555.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([total_response_time])
    print(f"Total response time for all requests: {total_response_time} microseconds")


if __name__ == "__main__":
    main()

