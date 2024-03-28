

from bigtree import Node, print_tree
from collections import deque
import asyncio
import csv
import json
import time
import aiocoap
import hashlib
import aiocoap.resource as resource
from aiocoap import *
# import sys
import logging
from pymongo import MongoClient
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["CRBAC_Policies"]
    # Check if the collection exists   
    if "rct1" not in db.list_collection_names() or "rct2" not in db.list_collection_names():
        logging.error("Required collection does not exist.")
        exit()
except Exception as e:
    logging.error("Failed to connect to MongoDB: %s", e)
    exit()

class NodeWithPriority(Node):
    def __init__(self, name, capabilities=None):
        super().__init__(name)
        self.capabilities = capabilities or []

    def inherit_capabilities(self):
        queue = deque([self])
        while queue:
            current_node = queue.popleft()
            parent_capabilities = current_node.capabilities
            for child in current_node.children:
                queue.append(child)
                for child_capability, child_priority in child.capabilities:
                    found = False
                    for parent_capability, parent_priority in parent_capabilities:
                        if child_capability == parent_capability:
                            found = True
                            if child_priority > parent_priority:
                                parent_capabilities.remove((parent_capability, parent_priority))
                                parent_capabilities.append((child_capability, child_priority))
                            break
                    if not found:
                        parent_capabilities.append((child_capability, child_priority))

    def build_tree(self):
        # Create the tree structure
        rg1 = NodeWithPriority("RG1", capabilities=[("c3", 2), ("c4", 1)])
        rg2 = NodeWithPriority("RG2", capabilities=[("c5", 1), ("c6", 3)])
        r1 = NodeWithPriority("R1", capabilities=[("c1", 3), ("c2", 1)])
        r2 = NodeWithPriority("R2", capabilities=[("c1", 1), ("c2", 2)])
        r3 = NodeWithPriority("R3", capabilities=[("c1", 2), ("c2", 1)])
        r4 = NodeWithPriority("R4", capabilities=[("c1", 3), ("c2", 2)])
        r5 = NodeWithPriority("R5", capabilities=[("c7", 3), ("c1", 5)])
        r6 = NodeWithPriority("R6", capabilities=[("c7", 3), ("c1", 6)])
        r7 = NodeWithPriority("R7", capabilities=[("c9", 3), ("c1", 5)])
        r8 = NodeWithPriority("R8", capabilities=[("c10", 3), ("c1", 7)])
        r9 = NodeWithPriority("R9", capabilities=[("c11", 3), ("c1", 8)])
        r10 = NodeWithPriority("R10", capabilities=[("c12", 3), ("c1", 3)])
        r11 = NodeWithPriority("R11", capabilities=[("c13", 1), ("c1", 2)])
        r12 = NodeWithPriority("R12", capabilities=[("c14", 2), ("c1", 3)])
        r13 = NodeWithPriority("R13", capabilities=[("c15", 3), ("c1", 3)])
        r14 = NodeWithPriority("R14", capabilities=[("c16", 2), ("c1", 6)])
        r15 = NodeWithPriority("R15", capabilities=[("c17", 1), ("c1", 4)])
        r16 = NodeWithPriority("R16", capabilities=[("c18", 3), ("c1", 6)])
        r17 = NodeWithPriority("R17", capabilities=[("c19", 5), ("c1", 3)])
        r18 = NodeWithPriority("R18", capabilities=[("c20", 3), ("c1", 6)])
        r19 = NodeWithPriority("R19", capabilities=[("c21", 3), ("c1", 6)])
        r20 = NodeWithPriority("R20", capabilities=[("c22", 4), ("c1", 6)])
        r21 = NodeWithPriority("R21", capabilities=[("c23", 2), ("c1", 3)])
        r22 = NodeWithPriority("R22", capabilities=[("c24", 2), ("c1", 6)])
        r23 = NodeWithPriority("R23", capabilities=[("c25", 2), ("c1", 6)])
        r24 = NodeWithPriority("R24", capabilities=[("c26", 1), ("c1", 5)])
        r26 = NodeWithPriority("R26", capabilities=[("c27", 3), ("c1", 6)])
        r27 = NodeWithPriority("R27", capabilities=[("c28", 3), ("c1", 2)])
        r28 = NodeWithPriority("R28", capabilities=[("c29", 3), ("c1", 3)])
        r29 = NodeWithPriority("R29", capabilities=[("c30", 3), ("c1", 3)])
        r30 = NodeWithPriority("R30", capabilities=[("c31", 3), ("c1", 4)])

        self.children = [rg1, rg2]
        rg1.children = [r1, r2]
        rg2.children = [r3, r4, r24]
        r1.children = [r5, r6,r14,r18]
        r2.children = [r7, r8,r15,r19]
        r3.children = [r9, r10,r16,r20]
        r4.children = [r11, r12,r13,r17,r21,r22,r23]
        r24.children = [r26,r27, r28,r29,r30]
        # Inherit capabilities using level-order traversal with priority handling
        self.inherit_capabilities()

    def get_level(self, role, node, level=0):
        # print("sorte..level...............")
        if node.name == role:
            return level
        for child in node.children:
            result = self.get_level(role, child, level + 1)
            if result is not None:
                return result
        return None

    def get_id(self, role, context):
        with open('rct1.csv', 'r') as user_file:
            reader = csv.reader(user_file)
            for i, row in enumerate(reader):
                if (row[1], row[2]) == (role, context):
                    return i
        return None

    def get_priority(self, role, capability, node):
        
        if node.name == role:
            for cap, priority in node.capabilities:
                if cap == capability:
                    return priority
        for child in node.children:
            result = self.get_priority(role, capability, child)
            if result is not None:
                return result
        return None

    def sort_requests(self, requests):
        for i in range(len(requests)):
            for j in range(len(requests) - 1):
                # print("sorte.................")
                role1, context1, capability1 = requests[j]
                role2, context2, capability2 = requests[j+1]
                level1 = self.get_level(role1, self)
                level2 = self.get_level(role2, self)
                priority1 = self.get_priority(role1, capability1, self)
                priority2 = self.get_priority(role2, capability2, self)
                
                if level1 > level2 or (level1 == level2 and priority1 > priority2):
                    requests[j], requests[j+1] = requests[j+1], requests[j]
                elif level1 == level2 and priority1 == priority2:
                    user_id1 = self.get_id(role1, context1)
                    user_id2 = self.get_id(role2, context2)
                    if user_id1 < user_id2:
                        requests[j], requests[j+1] = requests[j+1], requests[j]
        return requests
root = NodeWithPriority("root")
root.build_tree()
class ConflictResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_post(self, request):
        input_payload = request.payload.decode('utf-8')  # receives at timestamp t2
        inputData = input_payload.split('\n')
        # print("inp data",inputData)
        # print("Number of Input Lines:", len(inputData))
        processed_data = self.process_input_data(inputData)  # Process the input data
        t2 = str(int(time.time() * 1000))
        # Create the response payload
        response_payload = {
            'result': processed_data     }
        # Encode the response payload
        encoded_payload = json.dumps(response_payload).encode('utf-8')
        # Send the response to the client
        return aiocoap.Message(payload=encoded_payload)

    def query_mongodb(self, id_value, context_value, capability_value):
        # Assuming you have a MongoDB collection named "rct1"
        collection = db["rct1"]
        pipeline = [
        {"$match": {"ID": id_value, "Context": context_value}},
        {"$project": {"_id": 0, "Role": 1, "Context": 1, "Capability": capability_value}}  ]
        # Execute the pipeline and return the result
        result = list(collection.aggregate(pipeline)) 
        # print("pipline1...",result)
        return result# return list(collection.aggregate(pipeline))

    def match_sorted_results(self, sorted_results):
        matched_data = []
        for role, context, capability in sorted_results:
            # Construct a pipeline for matching and projecting
            pipeline = [
                {"$match": {"Role": role, "Context": context, "Capability": capability}},
                {"$project": {"_id": 0, "Role": 1, "Context": 1, "Capability": 1, "Permission": 1}}
            ]
            
            # Query "rct2" collection using the constructed pipeline
            permission_data = list(db["rct2"].aggregate(pipeline))
            
            # Append the permission data to the matched_data list
            matched_data.append(permission_data)
            # Extract only values from the MongoDB result and return
        pipline2_data = [tuple(e.values()) for item in matched_data for e in item]
        # print("matchd data.....",pipline2_data)
        return pipline2_data
    def process_matched_results(self, matched_results):
        final_result = []
        allow_found = False
        
        for role, context, capability, permission in matched_results:
            if not allow_found:
                if permission == "allow":
                    final_result.append((role, context, capability, permission))
                    allow_found = True
                else:
                    final_result.append((role, context, capability, "deny"))
            else:
                final_result.append((role, context, capability, "deny"))
        
        return final_result
    def process_input_data(self, input_data):
        processed_data = []
        for line in input_data:
            processed_line = line.split(',')  # Split each line by comma
            id_value = processed_line[0]
            context_value = processed_line[1]
            capability_value = processed_line[2]
            result_from_mongodb = self.query_mongodb(id_value, context_value, capability_value)         
            processed_data.append(result_from_mongodb)
        
        # Extract only values from the MongoDB result and return
        result_values = [tuple(d.values()) for item in processed_data for d in item]
        
        # Sort the result_values using the sort_requests function from Code A
        sorted_result = root.sort_requests(result_values)
        # print("sorted res are .....",sorted_result)
        # Match the sorted results in the "rct2" collection and project permission values
        matched_results = self.match_sorted_results(sorted_result)
        # print("matched results....",matched_results)
        # Process the matched results to determine final permissions
        final_result = self.process_matched_results(matched_results)
        # print("final results....",final_result)
        
        return final_result

        
        # return matched_results
        
        # return sorted_result
async def main():
    root = resource.Site()
    root.add_resource(('auth',), ConflictResource())

    # Specify the IP address and port for the server to bind to
    host = '127.0.0.1'  # Use '0.0.0.0' to bind to all available network interfaces
    port = 5683  # Specify a valid port number

    # Create a CoAP server context and bind it to the specified address
    context = await Context.create_server_context(root, bind=(host, port))

    print("Server started and waiting for requests...")

    # Run the server until interrupted
    await asyncio.Future()



# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
