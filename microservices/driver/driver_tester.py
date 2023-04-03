import requests
import json

base_url = "http://driver:5003"

# Test create_driver
data = {
    "driver_name": "Test Driver",
    "phone_number": "1234578",
    "region": "Central",
    "availability": True
}

# response = requests.post(f"{base_url}/new_driver", json=data)
# print("Test create_driver:", response.json())

# Test get_driver_by_id
driver_id = 1
response = requests.get(f"{base_url}/get_driver/{driver_id}")
print(f"Test get_driver_by_id for driver_id {driver_id}:", response.json())

# Test get_driver_region_availaibility
region = "Central"
response = requests.get(f"{base_url}/get_available_driver_region/{region}")
print(f"Test get_driver_region_availaibility for region {region}:", response.json())

# Test update_driver_status
driver_id = 1
response = requests.put(f"{base_url}/update_driver_status/{driver_id}")
print(f"Test update_driver_status for driver_id {driver_id}:", response.json())

# Test update_driver_region
driver_id = 1
data = {"region": "North"}
response = requests.put(f"{base_url}/update_driver_region/{driver_id}", json=data)
print(f"Test update_driver_region for driver_id {driver_id}:", response.json())
