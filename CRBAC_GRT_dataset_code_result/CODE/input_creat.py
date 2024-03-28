# # import csv
# # import random

# # # Function to read CSV file and return rows as a list
# # def read_csv(filename):
# #     with open(filename, 'r') as file:
# #         reader = csv.reader(file)
# #         return list(reader)

# # # Function to write data to CSV file
# # def write_to_csv(filename, data):
# #     with open(filename, 'w', newline='') as file:
# #         writer = csv.writer(file)
# #         writer.writerows(data)

# # # Read data from file1.csv
# # file1_data = read_csv('devices1000_roles200.csv')

# # # Read data from file2.csv
# # file2_data = read_csv('Policy10000.csv')

# # # Create a new list to store mapped rows from file2_data
# # mapped_rows = []

# # # Iterate over each row in file2_data
# # for row2 in file2_data:
# #     role2, context2, capability, permission = row2
# #     if context2 == 'context':
# #         # Skip header row in file2.csv
# #         continue

# #     for row1 in file1_data:
# #         id1, role1, context1 = row1[0], row1[1], row1[2]
# #         if role1 == role2 and context1 == context2:
# #             # Append the corresponding id from file1_data to file2_data
# #             mapped_row = row2 + [id1]
# #             mapped_rows.append(mapped_row)
# #             break

# # # Shuffle the mapped rows
# # random.shuffle(mapped_rows)

# # # Select a random set of 200 rows from mapped_rows
# # final_rows = random.sample(mapped_rows, 200)

# # # Write the final_rows to file2_mapped.csv
# # write_to_csv('file2_mapped.csv', final_rows)

# # print("Mapping of role and context fields with corresponding id is complete.")
# # print("Final CSV file 'file2_mapped.csv' with 200 randomly selected rows has been created.")

# import csv

# # Function to read CSV file and return rows as a list
# def read_csv(filename):
#     with open(filename, 'r') as file:
#         reader = csv.reader(file)
#         return list(reader)

# # Function to write data to CSV file
# def write_to_csv(filename, data):
#     with open(filename, 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerows(data)

# # Read data from file1.csv
# file1_data = read_csv('Device1K_Rolectx100.csv')

# # Read data from file2.csv
# file2_data = read_csv('p_Res1000.csv') ##############

# # Create a new list to store mapped rows from file2_data
# mapped_rows = []

# # Iterate over each row in file2_data
# for row2 in file2_data:
#     role2, context2, capability, permission = row2
#     if context2 == 'context':
#         # Skip header row in file2.csv
#         continue

#     for row1 in file1_data:
#         id1, role1, context1 = row1[0], row1[1], row1[2]
#         if role1 == role2 and context1 == context2:
#             # Append the corresponding role, context, capability, permission, and id from file1_data to file2_data
#             mapped_row = [id1, context2, capability,"AC", "t"]
#             mapped_rows.append(mapped_row)
#             break


#     if len(mapped_rows) == 201:
#         # Break the loop if 201 rows are reached
#         break

# filename="Res_10.csv" ################
# # Write the mapped_rows to file2_mapped.csv
# # Modify the header to include "type" and "time_t"
# header = ['Id', 'Context', 'Capability', 'type', 'time_t']
# mapped_rows.insert(0, header)


# write_to_csv(filename, mapped_rows)

# print("Mapping of role, context, capability fields with corresponding id, role, and context is complete.")
# print(f"Final CSV file {filename} with mapped rows has been created.")


import csv

# Function to read CSV file and return rows as a list
def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        return list(reader)

# Function to write data to CSV file
def write_to_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Read data from file1.csv
file1_data = read_csv('GRT_dev500_R100_20ctx.csv')

# Read data from file2.csv
file2_data = read_csv('GRT_Role_ctx_policy4500.csv')

# Create a new list to store mapped rows from file2_data
mapped_rows = []

# Iterate over each row in file2_data
for row2 in file2_data:
    role2, context2, capability, permission = row2
    if context2 == 'context':
        # Skip header row in file2.csv
        continue

    for row1 in file1_data:
        id1, role1, context1 = row1[0], row1[1], row1[2]
        if role1 == role2 and context1 == context2:
            # Append the corresponding role, context, capability, permission, and id from file1_data to file2_data
            mapped_row = [role2, context2, capability, permission, id1, role1, context1]
            mapped_rows.append(mapped_row)
            break
filename="GRT_G4500.csv"
# Write the mapped_rows to file2_mapped.csv
write_to_csv(filename, mapped_rows)

print("Mapping of role, context, capability fields with corresponding id, role, and context is complete.")
print(f"Final CSV file {filename} with mapped rows has been created.")
