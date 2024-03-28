#takes f1 and csv creaye and upload f2 (file gen by Dev_role_policy_algorithem)
import csv
import random
from pymongo import MongoClient

def generate_policy_file(input_file, output_file, num_rows):
    roles = set()  # Set to store unique roles and contexts
    capabilities = []  # List to store generated capabilities
    permissions = ['allow'] * int(num_rows * 0.8) + ['deny'] * int(num_rows * 0.2)  # Generate permissions (80% allow, 20% deny)
    random.shuffle(permissions)
    
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            role, context = row[1], row[2]  # Extract role and context from each row
            if (role, context) not in roles:
                roles.add((role, context))  # Add unique role-context pairs to the set
           
    resources = [f'res{i}_' for i in range(1, 501)]  # Generate a list of resource names
    while len(capabilities) < num_rows:
        for role, context in roles:
            resource = random.choice(resources)  # Randomly select a resource name
            random_num = random.random()
            if random_num < 0.3:
                capability = f'{resource}read'
                capabilities.append([role, context, capability])  # Add capability to the list
            elif random_num < 0.6:
                capability = f'{resource}exe'
                capabilities.append([role, context, capability])  # Add capability to the list
            else:
                capability = f'{resource}write'
                capabilities.append([role, context, capability])  # Add capability to the list
                capability = f'{resource}exe'
                capabilities.append([role, context, capability])  # Add capability to the list
    random.shuffle(capabilities)  # Shuffle the capabilities list
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Role', 'Context', 'Capability', 'Permission'])  # Write the header row
        for capability, permission in zip(capabilities, permissions):
            writer.writerow(capability + [permission])  # Write each capability and its corresponding permission
    print(f"{num_rows} rows added to the policy file.")
    print(f"Number of unique role-context pairs: {len(roles)},Number of capabilities added:{len(capabilities)}")
def upload_to_mongodb(data, collection_name):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["CRBAC_Policies"]
    if collection_name in db.list_collection_names():
        db[collection_name].drop()
    collection = db[collection_name]
    collection.insert_many(data)
    print(f"Data uploaded to collection: {collection_name} in database: {db.name}")
input_file =  r"D:\Mongo_DB\CRBAC_GRT_POLICY_FILES\GRT_dev500_R100_20ctx.csv"#D:\Mongo_DB\3D_datasets\G4_dev_role_ctx_files
output_file = r"D:\Mongo_DB\CRBAC_GRT_POLICY_FILES\GRT_Role_ctx_policy4500.csv"  
collection_name = "GRT_Role_ctx_policy4500"
num_rows = 4500
print("Generating policy file...")
generate_policy_file(input_file, output_file, num_rows)
print("Policy file generated.")
# generate_policy_file(input_file, output_file, num_rows)

data = []
with open(output_file, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        data.append({"Role": row[0], "Context": row[1], "Capability": row[2], "Permission": row[3]})
if len(data) == num_rows:
    print("CSV file created.")

    print("Uploading data to MongoDB...")
    upload_to_mongodb(data, collection_name)
    print("Data uploaded to MongoDB.")
else:
    print("CSV file not created.")
    print("Data not uploaded to MongoDB.")

# upload_to_mongodb(data, collection_name)







# #takes f1 and csv creaye and upload f2 (file gen by Dev_role_policy_algorithem)


# import csv
# import random
# from pymongo import MongoClient

# def generate_policy_file(input_file, output_file, num_rows):
#     roles = set()  # Set to store unique roles and contexts
#     capabilities = []  # List to store generated capabilities
#     permissions = ['allow'] * int(num_rows * 0.8) + ['deny'] * int(num_rows * 0.2)  # Generate permissions (80% allow, 20% deny)
#     random.shuffle(permissions)
    
#     # Read the input file to extract roles and contexts
#     with open(input_file, 'r') as file:
#         reader = csv.reader(file)
#         next(reader)  # Skip the header row
#         for row in reader:
#             role, context = row[1], row[2]  # Extract role and context from each row
#             if (role, context) not in roles:
#                 roles.add((role, context))  # Add unique role-context pairs to the set
#             # roles.add((role, context))  # Add unique role and context to the set
    
#     resources = [f'res{i}_' for i in range(1, 201)]  # Generate a list of resource names
    
#     # Generate capabilities until the desired number of rows is reached
#     while len(capabilities) < num_rows:
#         for role, context in roles:
       
#             resource = random.choice(resources)  # Randomly select a resource name
            
#             random_num = random.random()
#             if random_num < 0.3:
#                 # Role can have only "read" action
#                 capability = f'{resource}read'
#                 capabilities.append([role, context, capability])  # Add capability to the list
#             elif random_num < 0.6:
#                 # Role can have "read" and "execute" actions
#                 # capability = f'{resource}read'
#                 # capabilities.append([role, context, capability])  # Add capability to the list
#                 capability = f'{resource}exe'
#                 capabilities.append([role, context, capability])  # Add capability to the list
#             else:
#                 # Role can have all three actions
#                 # capability = f'{resource}read'
#                 # capabilities.append([role, context, capability])  # Add capability to the list
#                 capability = f'{resource}write'
#                 capabilities.append([role, context, capability])  # Add capability to the list
#                 capability = f'{resource}exe'
#                 capabilities.append([role, context, capability])  # Add capability to the list

#     random.shuffle(capabilities)  # Shuffle the capabilities list

#     # Write the capabilities and permissions to the output file
#     with open(output_file, 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(['Role', 'Context', 'Capability', 'Permission'])  # Write the header row
#         for capability, permission in zip(capabilities, permissions):
#             writer.writerow(capability + [permission])  # Write each capability and its corresponding permission
    
#     print(f"{num_rows} rows added to the policy file.")
#     #  print(f"{num_rows} rows added to the policy file.")
#     print(f"Number of unique role-context pairs: {len(roles)}")
#     print(f"Number of capabilities added: {len(capabilities)}")
# def upload_to_mongodb(data, collection_name):
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["CRBAC_3DPolicies"]
    
#     # Drop the collection if it exists
#     if collection_name in db.list_collection_names():
#         db[collection_name].drop()
    
#     # Create a new collection and insert the data
#     collection = db[collection_name]
#     collection.insert_many(data)
#     print(f"Data uploaded to collection: {collection_name} in database: {db.name}")

# input_file =  r"D:\Mongo_DB\3D_datasets\G4_dev_role_ctx_files\G4_DRe100_R20.csv"    #D:\Mongo_DB\3D_datasets\G4_dev_role_ctx_files
# # filename =  r"D:\Mongo_DB\3D_datasets\policyfiles\G3_pC20_R20.csv"   D:\Mongo_DB\3D_datasets\G3_dev_role_ctx_files    #********************************
# output_file = r"D:\Mongo_DB\3D_datasets\G4_policyfiles\G4_pRe200_R20.csv"  
# collection_name = "G4_pRe100_R20"
# num_rows = 5000
# print("Generating policy file...")
# generate_policy_file(input_file, output_file, num_rows)
# print("Policy file generated.")
# # generate_policy_file(input_file, output_file, num_rows)

# data = []
# with open(output_file, 'r') as file:
#     reader = csv.reader(file)
#     next(reader)  # Skip the header row
#     for row in reader:
#         data.append({"Role": row[0], "Context": row[1], "Capability": row[2], "Permission": row[3]})
# if len(data) == num_rows:
#     print("CSV file created.")

#     print("Uploading data to MongoDB...")
#     upload_to_mongodb(data, collection_name)
#     print("Data uploaded to MongoDB.")
# else:
#     print("CSV file not created.")
#     print("Data not uploaded to MongoDB.")

# # upload_to_mongodb(data, collection_name)
