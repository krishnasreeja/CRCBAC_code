# import aiocoap.resource as resource
# import aiocoap
# import asyncio
# import csv
# from aiocoap import Context, Message, PUT, error
# from pymongo import MongoClient
# import time
# import logging
# # MongoDB connection
# try:
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["CRBAC_Policies"] # policy  #CRBAC_3DPolicies  # CRBAC_Policies
    
#     # Check if the collection exists
    
#     if "throughput_file1" not in db.list_collection_names() or "p1k_rolectx_res10" not in db.list_collection_names():#################### change device1000_40roles
#         logging.error("Required collection does not exist.")
#         exit()
# except Exception as e:
#     logging.error("Failed to connect to MongoDB: %s", e)
#     exit()   
# class Authentication(resource.Resource): # Class Authentication
#     def __init__(self):
#         super().__init__()
#     async def render_put(self, request):
#         try:
#             response_payload = await self.process_input_data(request.payload.decode())
#             return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload.encode())
#         except Exception as e:
#             logging.error("Error processing input data: %s", e)
#             return aiocoap.Message(code=aiocoap.INTERNAL_SERVER_ERROR)
#     async def process_input_data(self,input_data):
      
#         result_lines = []  # Process each input line
#         # for line in input_lines:
#         try:
#             start_time = time.perf_counter()  # Record start time
#             parts = input_data.split(",")
#             # print("parts....",parts)
#             request_id, context, capability, request_type = parts
            
#             # if  parts[3] == "AC":
#             if request_type == "AC":                 
#                 role_pipeline = [
#                     {"$match": {"Id": request_id, "Context": context}},
#                     {"$project": {"Role": 1}}
#                 ]
#                 role_result = db.throughput_file1.aggregate(role_pipeline) ############################################
#                 role = next(role_result)["Role"] if role_result.alive else None
#                 if role:    # print(f"Role: {role}, Context: {context}, Capability: {capability}")   
#                     permission_pipeline = [    
#                         {"$match": {"Role": role, "Context": context}},
#                         {"$project": {"Capability": 1, "Permission": 1}}
#                     ]
#                     capability_result = db.p1k_rolectx_res10.aggregate(permission_pipeline) #######################################
                
#                     permission = None
#                     # print(".................entered")
#                     for document in capability_result:
#                         # print("............",document,capability_result)
                        
#                         if document.get("Capability") == capability:
                            
#                             permission = document.get("Permission")
                            
#                             break

#                     if permission:
#                         # print(f"Access: {permission}")
#                         result_lines.append(f"Permission: {permission}")
#                     else:
#                         # print("Deny: No capability matched")
#                         result_lines.append("Deny: No capability")

#                 else:
#                     # print("Deny: No role matched")
#                     result_lines.append("Deny: No role ")
#                 for line in result_lines:
#                     print(line)         
                                
#             else:
#                 # Invalid request type
#                 print("Invalid request type")
#                 result_lines.append("Invalid request type")
            
#             end_time = time.perf_counter()  # Record end time
#             processing_time = (end_time - start_time) * 1e6  # Calculate permission evaluation time

#             # Append response time to CSV file
#             with open("processing_time.csv", "a", newline="") as csvfile:
#                 writer = csv.writer(csvfile)
#                 # writer.writerow([role_time, processing_time])
#                 writer.writerow([processing_time])

#         except Exception as e:
#             logging.error("Error processing input line: %s", e)
#         t2 = "t2"
        
#         response_payload = "\n".join(result_lines) + f"\nT2: {t2}"
#         return response_payload

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("coap-server")
# logger.setLevel(logging.INFO)
# logger.propagate = False  # Disable propagation to prevent duplicate logs

# def main():
#     try:
#         print("CoAP server started.")
#         root = resource.Site()  # Resource tree creation
#         authResource = Authentication()
#         root.add_resource(['auth'], authResource)
#         asyncio.Task(aiocoap.Context.create_server_context(root, bind=('localhost', 5683)))
#         asyncio.get_event_loop().run_forever()
#     except KeyboardInterrupt:
#         pass
#     finally:
#         client.close()

# if __name__ == "__main__":
#     main()
import aiocoap.resource as resource
import aiocoap
import asyncio
import csv
from aiocoap import Context, Message, PUT, error
from pymongo import MongoClient
import time
import logging
import concurrent.futures
# MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["CRBAC_Policies"] # policy  #CRBAC_3DPolicies  # CRBAC_Policies
    
    # Check if the collection exists
    
    if "throughput_file1" not in db.list_collection_names() or "p1k_rolectx_res10" not in db.list_collection_names():#################### change device1000_40roles
        logging.error("Required collection does not exist.")
        exit()
except Exception as e:
    logging.error("Failed to connect to MongoDB: %s", e)
    exit() 
class Authentication(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_put(self, request):
        try:
            response_payload = await self.process_input_data(request.payload.decode())
            return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload.encode())
        except Exception as e:
            logging.error("Error processing input data: %s", e)
            return aiocoap.Message(code=aiocoap.INTERNAL_SERVER_ERROR)

    async def process_input_data(self, input_data):
        result_lines = []
        try:
            start_time = time.perf_counter()
            parts = input_data.split(",")
            request_id, context, capability, request_type = parts

            if request_type == "AC":
                role_pipeline = [
                    {"$match": {"Id": request_id, "Context": context}},
                    {"$project": {"Role": 1}}
                ]
                role_result = db.throughput_file1.aggregate(role_pipeline)
                role = next(role_result)["Role"] if role_result.alive else None

                if role:
                    permission_pipeline = [
                        {"$match": {"Role": role, "Context": context}},
                        {"$project": {"Capability": 1, "Permission": 1}}
                    ]
                    capability_result = db.p1k_rolectx_res10.aggregate(permission_pipeline)

                    permission = None
                    for document in capability_result:
                        if document.get("Capability") == capability:
                            permission = document.get("Permission")
                            break

                    if permission:
                        result_lines.append(f"Permission: {permission}")
                    else:
                        result_lines.append("Deny: No capability")

                else:
                    result_lines.append("Deny: No role")

                for line in result_lines:
                    print(line)

            else:
                print("Invalid request type")
                result_lines.append("Invalid request type")

            end_time = time.perf_counter()
            processing_time = (end_time - start_time) * 1e6

            with open("processing_time.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([processing_time])

        except Exception as e:
            logging.error("Error processing input line: %s", e)

        t2 = "t2"
        response_payload = "\n".join(result_lines) + f"\nT2: {t2}"
        return response_payload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coap-server")
logger.setLevel(logging.INFO)
logger.propagate = False  # Disable propagation to prevent duplicate logs

def main():
    try:
        print("CoAP server started.")
        root = resource.Site()  # Resource tree creation
        authResource = Authentication()
        root.add_resource(['auth'], authResource)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            loop.set_default_executor(executor)

            asyncio.ensure_future(aiocoap.Context.create_server_context(root, bind=('localhost', 5683)))

            loop.run_forever()

    except KeyboardInterrupt:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    main()
