
# xor time grant transfer revok done complety  , CRBAC_Device.py main code for crbac grt

import aiocoap.resource as resource
import aiocoap
import asyncio
import csv
# from aiocoap import Context, Message, PUT, error
from pymongo import MongoClient
import time
from bigtree import Node
# from collections import deque
import logging

# MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["CRBAC_Policies"] # policy
    # db = client["CBAC"] # policy
    
    # Check if the collection exists   
    if "GRT_dev500_R100_20ctx" not in db.list_collection_names() or "GRT_Role_ctx_policy500" not in db.list_collection_names():
        logging.error("Required collection does not exist.")
        exit()
except Exception as e:
    logging.error("Failed to connect to MongoDB: %s", e)
    exit()

# Class Authentication
class Authentication(resource.Resource):
    def __init__(self):
        super().__init__()
  
    def xor_decode(self, data):
            key = "1dcdbff4c6fb0d47e6bea745d3033bad4c8b2166ff6c1408b2bd52a162a594d6" 
            decoded_data = []
            for i in range(len(data)):
                decoded_char = chr(ord(data[i]) ^ ord(key[i % len(key)]))
                decoded_data.append(decoded_char)
            return ''.join(decoded_data)
    
    def xor_encode(self, data):
        key = "1dcdbff4c6fb0d47e6bea745d3033bad4c8b2166ff6c1408b2bd52a162a594d6" 
        encoded_data = []
        for i in range(len(data)):
            encoded_char = chr(ord(data[i]) ^ ord(key[i % len(key)]))
            encoded_data.append(encoded_char)
        return ''.join(encoded_data)


    async def render_put(self, request):
        try:
            
            decoded_payload =self.xor_decode(request.payload.decode())
            response_payload = await self.process_input_data(decoded_payload)
              
            # Perform XOR decoding using the secret key
            encoded_payload = self.xor_encode(response_payload)
            return aiocoap.Message(code=aiocoap.CHANGED, payload=encoded_payload.encode())   
    
        except Exception as e:
            logging.error("Error processing input data: %s", e)
            return aiocoap.Message(code=aiocoap.INTERNAL_SERVER_ERROR)
        
    async def process_input_data(self, input_data):
        processing_time = []  # Initialize an empty list to store processing times
        pipeline_time=[]
        permission_time=[]
        Role_execution_time=[]
        # permission_start_t1 = []
        # tree_finl_tim=[]
        # Split input data into lines
        input_lines = input_data.strip().split("\n")
        result_lines = []
        for line in input_lines:
            # print(".line is ", line)
            try:
                # Get the current time (t2)
                # time_t2 = time.strftime("%H:%M:%S")
                # print("t2 in servber",time_t2)

                # Extract the received time (t1) from the input line
                parts = line.split(",")
                t1 = parts[-1].strip()  # Assuming the last element is the time
                # print("t1 from client",t1)

                # Calculate the time difference (t2 - t1) Specify the time delay threshold (1 second )
                # time_diff = float(current_time) - float(t1)  # Convert t1 to float
                # time_delay = 1

                if t1:
                    # start_time = time.perf_counter()  # Record start time
                    # parts = parts[:-1]  # Remove the time from the parts list

                    if parts[3] == "AC":
                        request_id, context, capability, request_type, time_t = parts
                        print("enterd to AC")           
                        role_pipeline = [
                            {"$match": {"Id": request_id, "Context": context}},
                            {"$project": {"Role": 1}}
                        ]
                        role_result = db.throughput_file1.aggregate(role_pipeline) 
                        role = next(role_result)["Role"] if role_result.alive else None
                        if role:
                            # Check if capability exists for role and context and retrieve permission
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
                                # print(f"Access: {permission}")
                                result_lines.append(f"Permission: {permission}")
                            else:
                                # print("Deny: No capability matched")
                                result_lines.append("Deny: No capability")
                        else:
                            # print("Deny: No role matched")
                            result_lines.append("Deny: No role ")
                        for line in result_lines:
                            print(line)
                        return result_lines
                    elif len(parts) == 7:
                        idn, ctxn, cap_n, idt, ctxt, request_type, time_t = parts
                        # print("entered in to 7parts")
                        # pipeline_time= time.perf_counter()  # Record end time
                # processing_time = (end_time - start_time) * 1e6  # Calculate permission evaluation time

                        role_pipeline = [
                            {
                                "$match": {
                                    "$or": [
                                        {"$and": [{"Id": idn}, {"Context": ctxn}]},
                                        {"$and": [{"Id": idt}, {"Context": ctxt}]}
                                    ]
                                }
                            },
                            {"$project": {"Id": 1, "Role": 1}}
                        ]

                        role_result = list(db.GRT_dev500_R100_20ctx.aggregate(role_pipeline))

                        
                        # print("pipline1 time is ",pipeline_time)
                        # print("role re is ",role_pipeline)
                        roles = {}
                        
                        for document in role_result:
                            
                            user_id = document["Id"]
                            role = document["Role"]
                            roles[user_id] = role
                        role_n = roles.get(idn)
                        role_t = roles.get(idt)
                        # pipe_end_time= time.perf_counter()
                        # pipeline_time=(pipe_end_time-pipeline_time) *1e3
                        # print("pipline time is...............................,,,> ",pipeline_time)
                        # print("roles retruved and roles are ",role_n,role_t)
                        # Check if roles exist for idn and idt
                        if role_n and role_t:
                            # print(f"Role_n: {role_n}, Role_t: {role_t}")
                            result_lines.append(f"Role_n: {role_n}, Role_t: {role_t}")
                            if request_type == "Gtype":
                                # print("entred into Gtype")
                                # start_time = time.perf_counter()  # Record the start time
                                if grant_revoke(role_t, role_n):
                                    # end_time = time.perf_counter()  # Record the end time
                                    # Role_execution_time = (end_time - start_time)*1e3
                                    # print(f"Execution time for grant_revoke...........: {Role_execution_time} milli seconds")                              
                                    # print("Role hierarchy condition is satisfied after fyntion returned")
                                    result_lines.append("Role hierarchy satisfied")
                                    # Pipeline to match role, context, and check capability and permission
                                    permission_start_t1=time.perf_counter()
                                    pipeline_permission = [
                                        {
                                            "$match": {
                                                "Role": role_t,
                                                "Context": ctxt,
                                                "Capability": cap_n,
                                                "Permission": "allow"
                                            }
                                        }
                                    ]
                                    permission_result = db.GRT_Role_ctx_policy4000.aggregate(pipeline_permission)
                                    if permission_result.alive:                                    
                                        # print("Capability matched and permission is allow")
                                        result_lines.append("Capability matched,permission:allow")                                    
                                        # Capability and permission matched, add a new record for role_n
                                        new_permission = {
                                            "Role": role_n,
                                            "Context": ctxn,
                                            "Capability": cap_n,
                                            "Permission": "allow"
                                        }
                                        db.GRT_Role_ctx_policy4000.insert_one(new_permission)
                                        print("New record granted for ",role_n)# for role_n
                                        
                                        
                                    else:
                                        print("Capability not matched or permission is not allow")
                                        result_lines.append("Capability not matched or permission is not allow")
                                    
                                else:
                                    # print("Role hierarchy condition is not satisfied")
                                    result_lines.append("Role hierarchy condition is not satisfied")
                                    return result_lines
                                # permission_t2=time.perf_counter()
                                # permission_time=(permission_t2-permission_start_t1)*1e3
                                # print(f"time to get permission and add/ grant operation.................. {permission_time}")
                                         
                            elif request_type == "T":
                                # print("entered in to Ttype")
                                permission_start_t1=time.perf_counter() 
                                # Pipeline to check if the capability already exists with "allow" permission for role_t
                                pipeline = [
                                    {
                                        "$match": {
                                            "Role": role_n,
                                            "Context": ctxn,
                                            "Capability": cap_n,
                                            "Permission": "allow"
                                        }
                                    },
                                    {
                                        "$limit": 1
                                    }
                                ]

                                existing_record = list(db.GRT_Role_ctx_policy5000.aggregate(pipeline))
                                if existing_record:
                                    # print(" Capability already exists, no transfer needed.",existing_record)
                                    result_lines.append(" cant transfer")
                                else:
                                    # print("Capability doesn't exist, proceed with transfer.")
                                    # result_lines.append("Capability doesn't exist, transfer.")
                                    # start_time = time.perf_counter()  # Record the start time
                                    if transfer_capability(role_n, role_t):
                                        # end_time = time.perf_counter()  # Record the end time
                                        # Role_execution_time = (end_time - start_time)*1e3
                                        # print("Capability transfer condition is true to transfer")
                                        # result_lines.append(" transfer condition true ")                                    
                                        update_filter = { # Update the existing record in permission_p collection for role_t  
                                            "Role": role_t,
                                            "Context": ctxt,
                                            "Capability": cap_n,
                                            "Permission": "allow"
                                        }
                                        update_data = {
                                            "$set": {
                                                "Role": role_n
                                            }
                                        }
                                        db.GRT_Role_ctx_policy5000.update_one(update_filter, update_data)
                                        
                                        # print("Existing record updated for role_t")
                                        result_lines.append("Role transferred")
                                        
                                    else:
                                        print("Capability transfer condition is not satisfied")

                                        result_lines.append("Capability transfer condition is not satisfied")
                                        return result_lines
                                    # permission_t2=time.perf_counter()
                                    # permission_time=(permission_t2-permission_start_t1)*1e3
                                   
                                    
                                
                                    
                            elif request_type == "D": # request to delete or revoke
                                # start_time = time.perf_counter()  # Record the start time
                                if grant_revoke(role_t, role_n):
                                    # end_time = time.perf_counter()  # Record the end time
                                    # Role_execution_time = (end_time - start_time)*1e3
                               
                                    # print("Capability can be revoked, condition satisfied")
                                    # result_lines.append("Cap can be revoked")
                                    # permission_start_t1=time.perf_counter()
                                    # Construct the pipeline to match the existing record
                                    pipeline = [
                                        {"$match": {"Role": role_n, "Context": ctxn, "Capability": cap_n, "Permission": "allow"}}
                                    ]

                                    # Execute the pipeline and check if the capability exists
                                    matching_record = db.GRT_Role_ctx_policy500.aggregate(pipeline)

                                    if matching_record:
                                        # Delete the existing record for role_n
                                        db.GRT_Role_ctx_policy500.delete_one({"Role": role_n, "Context": ctxn, "Capability": cap_n, "Permission": "allow"})
                                        print("revoked")
                                        result_lines.append(" revoked")
                                    else:
                                        print("Capability does not exist for role_n")
                                        result_lines.append("Capability does not exist for role_n")

                                else:
                                    print("Capability revoke condition is not satisfied")
                                    result_lines.append("Capability revoke condition is not satisfied")

                            else:
                                print("Deny: Invalid request type")
                                result_lines.append("Deny: Invalid request type")

                        else:
                            print("Deny: No roles matched")
                            result_lines.append("Deny: No roles matched")
                    else:
                        # Invalid request type
                        print("Deny: Required parameters missing or invalid request type")
                        result_lines.append("Deny: Required parameters missing or invalid request type")
                    
                else:
                    print("timedelay not satisfgied")
                    return result_lines  
                # permission_t2=time.perf_counter()
                # permission_time=(permission_t2-permission_start_t1)*1e3
                # print(f"time to get permission and revoke/delete operation.................. {permission_time}")
                
            

                # end_time = time.perf_counter()  # Record end time
                # processing_time = (end_time - start_time) * 1e3  # Calculate permission evaluation time
                
                # print("Processing time is: ", processing_time)
                # header = ['role_retrivl', 'tree', 'permi_add', 'processing_Time']
                # Append response time to CSV file
                with open("processing_time.csv", "a", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    # writer.writerow(header)  # Add header line
                    writer.writerow([pipeline_time,Role_execution_time,permission_time, processing_time])
                          


            except Exception as e:
                logging.error("Error processing input line: %s", e)
        t2 =time.strftime("%H:%M:%S")
        response_payload = "\n".join(result_lines) + f"\nT2: {t2}"
        return response_payload

class RoleCapabilityTree(Node):
    def __init__(self, name, capabilities=None):
        super().__init__(name)
        self.capabilities = capabilities or []
tree_finl_tim=[]
def get_level(node, role, level=0):
    if node.name == role:
        return level

    for child in node.children:
        result = get_level(child, role, level + 1)
        if result is not None:
            return result

    return None

def transfer_capability(role_n, role_t):
    # print("role_t and role n", role_t, role_n)
    # Check the level of role_n and role_t
    level_t = get_level(root, role_t)
    level_n = get_level(root, role_n)

    # Check if both roles are in the same level
    if level_n is not None and level_t is not None and level_n == level_t:
      
        # print(f"Transfer capability from {role_t} to {role_n} successful.")
        return role_n, role_t
    else:
        print("Cannot transfer capability. Roles are not in the same level.")
        return None 
# tre_t=time.perf_counter()
def grant_revoke( role_t, role_n):
    
    if is_parent(role_t, role_n):
        # print(f"Role hierarchy condition is satisfied  {role_t} parent of {role_n} ")
        return True
    else:
        print("Role hierarchy condition failed.............")
        return False
    # tre_t2=time.perf_counter()
    # tree_finl_tim=(tre_t-tre_t2)*1e6
    # print("tree funcyio time..........>",tree_finl_tim)
    # return tree_finl_tim

def is_parent(role_t, role_n):
      
    # Traverse the tree structure and compare the roles
    # Assuming 'root' is the root node of the tree
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node.name == role_t:
            # print("..........rolet",role_t)
            # Check if role_n is a child of role_t
            for child in node.children:
                if child.name == role_n:
                    
                    return True
        queue.extend(node.children)
    
    return False
# Create the tree structure
root = RoleCapabilityTree("root")
r1 = RoleCapabilityTree("R1"); r2 = RoleCapabilityTree("R2") ; r3 = RoleCapabilityTree("R3") ; r4 = RoleCapabilityTree("R4"); r5 = RoleCapabilityTree("R5")
r6 = RoleCapabilityTree("R6"); r7 = RoleCapabilityTree("R7"); r8 = RoleCapabilityTree("R8"); r9 = RoleCapabilityTree("R9"); r10 = RoleCapabilityTree("R10")
r11 = RoleCapabilityTree("R11"); r12 = RoleCapabilityTree("R12"); r13 = RoleCapabilityTree("R13"); r14 = RoleCapabilityTree("R14"); r15 = RoleCapabilityTree("R15")
r16 = RoleCapabilityTree("R16");r17 = RoleCapabilityTree("R17");r18 = RoleCapabilityTree("R18"); r19 = RoleCapabilityTree("R19");r20 = RoleCapabilityTree("R20")
r21 = RoleCapabilityTree("R21");r22 = RoleCapabilityTree("R22");r23 = RoleCapabilityTree("R23");r24 = RoleCapabilityTree("R24");r25 = RoleCapabilityTree("R25")
r26 = RoleCapabilityTree("R26");r27 = RoleCapabilityTree("R27");r28 = RoleCapabilityTree("R28");r29 = RoleCapabilityTree("R29");r30 = RoleCapabilityTree("R30")
r31 = RoleCapabilityTree("R31");r32 = RoleCapabilityTree("R32");r33 = RoleCapabilityTree("R33");r34 = RoleCapabilityTree("R34");r35 = RoleCapabilityTree("R35");
r36 = RoleCapabilityTree("R36");r37 = RoleCapabilityTree("R37");r38 = RoleCapabilityTree("R38");r39 = RoleCapabilityTree("R39");r40 = RoleCapabilityTree("R40");
r41 = RoleCapabilityTree("R41");r42 = RoleCapabilityTree("R42");r43 = RoleCapabilityTree("R43");r44 = RoleCapabilityTree("R44");r45 = RoleCapabilityTree("R45");
r46 = RoleCapabilityTree("R46");r47 = RoleCapabilityTree("R47");r48 = RoleCapabilityTree("R48");r49 = RoleCapabilityTree("R49");r50 = RoleCapabilityTree("R50");
r51 = RoleCapabilityTree("R51");r52 = RoleCapabilityTree("R52");r53 = RoleCapabilityTree("R53");r54 = RoleCapabilityTree("R54");r55 = RoleCapabilityTree("R55");
r56 = RoleCapabilityTree("R56");r57 = RoleCapabilityTree("R57");r58 = RoleCapabilityTree("R58");r59 = RoleCapabilityTree("R59");r60 = RoleCapabilityTree("R60");
r61 = RoleCapabilityTree("R61");r62 = RoleCapabilityTree("R62");r63 = RoleCapabilityTree("R63");r64 = RoleCapabilityTree("R64");r65 = RoleCapabilityTree("R65");
r66 = RoleCapabilityTree("R66");r67 = RoleCapabilityTree("R67");r68 = RoleCapabilityTree("R68");r69 = RoleCapabilityTree("R69");r70 = RoleCapabilityTree("R70");
r71 = RoleCapabilityTree("R71");r72 = RoleCapabilityTree("R72");r73 = RoleCapabilityTree("R73");r74 = RoleCapabilityTree("R74");r75 = RoleCapabilityTree("R75");
r76 = RoleCapabilityTree("R76");r77 = RoleCapabilityTree("R77");r78 = RoleCapabilityTree("R78");r79 = RoleCapabilityTree("R79");r80 = RoleCapabilityTree("R80");
r81 = RoleCapabilityTree("R81");r82 = RoleCapabilityTree("R82");r83 = RoleCapabilityTree("R83");r84 = RoleCapabilityTree("R84");r85 = RoleCapabilityTree("R85");
r86 = RoleCapabilityTree("R86");r87 = RoleCapabilityTree("R87");r88 = RoleCapabilityTree("R88");r89 = RoleCapabilityTree("R89");r90 = RoleCapabilityTree("R90");
r91 = RoleCapabilityTree("R91");r92 = RoleCapabilityTree("R92");r93 = RoleCapabilityTree("R93");r94 = RoleCapabilityTree("R94");r95 = RoleCapabilityTree("R95")
r96 = RoleCapabilityTree("R96");r97 = RoleCapabilityTree("R97");r98 = RoleCapabilityTree("R98");r99 = RoleCapabilityTree("R99");r100 = RoleCapabilityTree("R100")

root.children = [r1, r2, r3, r4, r5];r1.children = [r6, r7, r8, r9, r10];r2.children = [r11, r12, r13, r14, r15];r3.children= [r16, r17, r18, r19, r20]
r4.children= [r21, r22, r23, r24, r25];r5.children = [r26, r27, r28, r29, r30];r6.children = [r31,  r32] ;r7.children = [r33, r34];r8.children = [r35, r36]
r9.children = [r37, r38];r10.children = [r39, r40];r11.children = [r41, r42, r43];r12.children = [r44, r45, r46];r13.children = [r47, r48, r49]
r14.children = [r50, r51, r52];r15.children = [r53, r54, r55];r16.children = [r56, r57, r58];r17.children = [r59, r60, r61];r18.children = [r62, r63, r64]
r19.children = [r65, r66, r67];r20.children = [r68, r69, r70];r21.children = [r71, r72, r73];r22.children = [r74, r75, r76];r23.children = [r77, r78, r79]
r24.children = [r80, r81, r82];r25.children = [r83, r84, r85];r26.children = [r86, r87, r88];r27.children = [r89, r90, r91];r28.children = [r92, r93, r94]
r29.children = [r95, r96, r97];r30.children = [r98, r99, r100]


# Inherit capabilities using level-order traversal with priority handling
# root.inherit_capabilities()

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
        asyncio.Task(aiocoap.Context.create_server_context(root, bind=('localhost', 5683)))
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    main()