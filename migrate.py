import json

# Load snapshot.json data
try:
    with open('snapshot.json', 'r') as snapshot_file:
        snapshot_data = json.load(snapshot_file)
    print("snapshot.json loaded successfully.")
except Exception as e:
    print(f"Error loading snapshot.json: {e}")

# Extract IP addresses and device IDs from snapshot.json
snapshot_ips = {}
for device in snapshot_data.get('devices', []):
    device_id = device.get('id')
    device_ip = device.get('ip')
    if device_id and device_ip:
        snapshot_ips[device_id] = device_ip
    else:
        print(f"Skipping device with missing ID or IP: {device}")

print(f"Extracted {len(snapshot_ips)} devices from snapshot.json.")

# Load core.config_entries data
try:
    with open('core.config_entries', 'r') as config_file:
        config_entries = json.load(config_file)
    print("core.config_entries loaded successfully.")
except Exception as e:
    print(f"Error loading core.config_entries: {e}")

# Check the top-level structure of core.config_entries
print(f"Top-level keys in core.config_entries: {list(config_entries.keys())}")

# Initialize logging variables
updated = False
log_entries = []

# Iterate over entries in core.config_entries to find matching device_id
entries = config_entries.get("data", {}).get("entries", [])
print(f"Found {len(entries)} entries in core.config_entries.")

for i, entry in enumerate(entries):
    # Access the device_id within the nested 'data' object
    device_data = entry.get("data", {})
    device_id = device_data.get("device_id")
    title = entry.get("title")
    current_ip = device_data.get("host", "N/A")  # Assuming 'host' holds the IP address
    
    print(f"\nInspecting entry {i + 1}/{len(entries)}:")
    print(f"device_id: {device_id}, current IP: {current_ip}")
    
    if device_id in snapshot_ips:
        new_ip = snapshot_ips[device_id]
        print(f"Match found for {title} {device_id}. Updating IP from {current_ip} to {new_ip}.")
        device_data["host"] = new_ip  # Replace IP address in the nested data dictionary
        log_entries.append(f"Updated {title} {device_id}: {current_ip} -> {new_ip}")
        updated = True
    else:
        print(f"No match found for device_id {device_id}.")

# Write updated core.config_entries data back to the file if any changes were made
if updated:
    try:
        with open('core.config_entries', 'w') as config_file:
            json.dump(config_entries, config_file, indent=4)
        print("IP addresses updated successfully.")
        print("Log of updates:")
        print("\n".join(log_entries))
    except Exception as e:
        print(f"Error writing updated core.config_entries: {e}")
else:
    print("No matching device IDs found. No updates were made.")