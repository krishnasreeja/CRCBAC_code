
import csv
import random

def generate_data(id_range, role_range, context_range):
    ids = random.sample(range(1, id_range + 1), id_range)  
    roles = [f"R{j}" for j in range(1, role_range + 1)]
    contexts = [f"ctx{k}" for k in range(1, context_range + 1)]

    data = []
    for idx, id in enumerate(ids, 1):
        num_roles = random.randint(3, 5)  # Randomly select a number of roles between 3 and 5 (inclusive)
        selected_roles = random.sample(roles, num_roles)
        random.shuffle(contexts)
        selected_contexts = contexts[:num_roles]  # Assign the shuffled contexts to the selected roles
        for role, context in zip(selected_roles, selected_contexts):
            data.append({"Id": f"Id{idx}", "Role": role, "Context": context})

    return data

# def write_to_csv(file_path, data):
#     # random.shuffle(data)  # Shuffle the data rows
#     with open(file_path, 'w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=["Id", "Role", "Context"])
#         writer.writeheader()
#         writer.writerows(data)

# data = generate_data(1000, 20, 20)
# file_path = r"D:\Mongo_DB\3D_datasets\G3_Role20_C20.csv"
# write_to_csv(file_path, data)






def write_to_csv(filename, data):
    # random.shuffle(data)  # Shuffle the data rows
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Id", "Role", "Context"])
        writer.writeheader()
        writer.writerows(data)
data = generate_data(500, 100, 20) # id, role, ctx
filename =  r"D:\Mongo_DB\CRBAC_GRT_POLICY_FILES\GRT_dev500_R100_20ctx.csv"     #D:\Mongo_DB\3D_datasets\G4_dev_role_ctx_files  
# D:\Mongo_DB\3D_datasets\G5_dev_role_ctx_files\G5_DC200.csv
write_to_csv(filename, data)  # Write the data to CSV

print(f"{len(data)} rows added to the '{filename}' file")


#above with row cout u can chk hw many rows it exaclty adds and modfy below code to that count

# import csv
# import random

# def generate_data(id_range, role_range, context_range):
#     ids = random.sample(range(1, id_range + 1), id_range)  # Select unique IDs from the range, shuffling the IDs
#     roles = [f"R{j}" for j in range(1, role_range + 1)]
#     contexts = [f"ctx{k}" for k in range(1, context_range + 1)]

#     data = []
#     for idx, id in enumerate(ids, 1):
#         num_roles = random.randint(3, 5)  # Randomly select a number of roles between 3 and 5 (inclusive)
#         selected_roles = random.sample(roles, num_roles)
#         random.shuffle(contexts)
#         selected_contexts = contexts[:num_roles]  # Assign the shuffled contexts to the selected roles
#         for role, context in zip(selected_roles, selected_contexts):
#             data.append({"Id": f"Id{idx}", "Role": role, "Context": context})

#     return data

# def write_to_csv(filename, data):
#     random.shuffle(data)  # Shuffle the data rows
#     with open(filename, 'w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=["Id", "Role", "Context"])
#         writer.writeheader()
#         writer.writerows(data)

# row_count = 5000
# data = generate_data(1000, 20, 20)

# # data = generate_data(10, 6, 6)
# data = data[:row_count]  # Truncate the data to the desired row count

# write_to_csv("f1.csv", data)  # Write the truncated data to CSV

# print(f"{row_count} rows added to the CSV file.")


# # Check if all generated IDs exist in the CSV
# generated_ids = [f"Id{i}" for i in range(1, len(data) + 1)]
# csv_ids = set()

# with open("f1.csv", 'r') as file:
#     reader = csv.reader(file)
#     next(reader)  # Skip the header row
#     for row in reader:
#         csv_ids.add(row[0])

# if generated_ids <= csv_ids:
#     print("All generated IDs exist in the CSV.")
# else:
#     print("Some generated IDs are missing in the CSV.")