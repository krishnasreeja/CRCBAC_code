
import os
import csv
from pymongo import MongoClient

# Establish a connection to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["CRBAC_Policies"]

# Specify the path to the folder containing the files
folder_path = r"D:\Mongo_DB\CRBAC_GRT_POLICY_FILES\Policy_files_role_ctx"

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    # Check if the file is a regular file
    
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        # Read the contents of the file
        with open(file_path, "r") as file:
            # Parse the CSV file
            reader = csv.DictReader(file)
            records = [record for record in reader]
        # Remove the ".csv" extension from the filename
        collection_name = os.path.splitext(filename)[0]

        # Use the filename (without the ".csv" extension) as the collection name
        collection = db[collection_name]


        # # Use the filename as the collection name
        # collection = db[filename]

        # Insert the records into the collection
        collection.insert_many(records)

        # Create a compound index on ID and Capability fields
        collection.create_index([("Role", 1), ("Context", 1)])

print("Files uploaded successfully with compound index on role and Context.")

# below is code to delete collection in mongodb and then by abov code u can upload into mongodb

# import pymongo

# # Connect to MongoDB
# client = pymongo.MongoClient("mongodb://localhost:27017")

# # Choose the database
# db = client["CRBAC_Policies"]

# # List all collections in the database
# collections = db.list_collection_names()

# # Filter collections that start with "GRT_Role_ctx_policy"
# target_collections = [coll for coll in collections if coll.startswith("GRT_Role_ctx_policy")]

# # Delete the target collections
# for collection_name in target_collections:
#     db[collection_name].drop()

# print(f"Deleted {len(target_collections)} collections.")
