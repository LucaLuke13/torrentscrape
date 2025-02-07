import csv
import json
import sys

# Check if the CSV file is provided
if len(sys.argv) != 2:
    print("Usage: python parse_csv.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

# Read the CSV file
with open(filename, 'r') as file:
    reader = csv.reader(file, delimiter=';')
    result = []

    for row in reader:
        if row and row[0].startswith('AS'):
            try:
                asn = int(row[0][2:])  # Remove 'AS' and convert to integer
                name = row[1].split(',')[0]  # Remove country code if present
                result.append({"name": name, "asn": asn})
            except ValueError:
                print(f"Skipping invalid ASN format: {row[0]}")
                continue

# Convert to JSON
json_output = json.dumps(result, indent=4)

# Print the JSON output
print(json_output)
