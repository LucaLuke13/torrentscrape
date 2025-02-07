import json
import requests
import ipaddress
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PEER_API_KEY = os.getenv("PEER_API_KEY")
PEER_API_HOST = os.getenv("PEER_API_HOST")

# Load ASN data from JSON file
with open("asns.json", "r") as f:
    asns = json.load(f)

def get_prefixes_for_asn(asn):
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}&starttime=2020-12-12T12:00"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [prefix['prefix'] for prefix in data['data']['prefixes']]
    else:
        print(f"Failed to get prefixes for ASN {asn}")
        return []

def extract_ips_from_prefix(prefix):
    try:
        network = ipaddress.ip_network(prefix, strict=False)
        if isinstance(network, ipaddress.IPv6Network):
            return []
        return list(network.hosts())
    except ValueError:
        print(f"Invalid prefix: {prefix}")
        return []

def torrents_for_ip(ip):
    url = f"https://{PEER_API_HOST}/history/peer?ip={ip}&key={PEER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data for {ip}: {response.status_code}")
        return None

# Generate filename with current date
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
output_file = f"results_{current_date}.json"

results = []

# Load existing results if the file exists
try:
    with open(output_file, "r") as f:
        results = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    results = []

# Process ASNs
for asn_info in asns:
    name = asn_info["name"]
    asn = asn_info["asn"]
    print(f"\nProcessing ASN: {name} (ASN {asn})")
    prefixes = get_prefixes_for_asn(asn)
    for prefix in prefixes:
        print(prefix)
        ips = extract_ips_from_prefix(prefix)
        print(len(ips))
        for ip in ips:
            try:
                result = torrents_for_ip(ip)
                if result and 'contents' in result and len(result['contents']) > 0:
                    print('🚨⚠️⚠️🚨 Found something for', ip)
                results.append(result)
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=4)
            except Exception as e:
                print(f"Could not fetch {ip}: {e}")

print("Processing complete. Results saved to", output_file)
