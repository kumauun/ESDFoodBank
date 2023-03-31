import requests
import json

base_url = "http://localhost:5005"

# Test creating a new order
new_order_data = {
    "region": 'North',
    "restaurant_id": 2,
    "restaurant_address": "123 Street",
    "restaurant_postalcode": 12345,
    "dish_id": 1,
    "quantity_check": True
}

response = requests.post(f"{base_url}/new_order", json=new_order_data)
print("New Order Response:", json.dumps(response.json(), indent=2))

# Test getting orders by region
get_order_data = {
    "user_type": "foodbank"
}
response = requests.get(f"{base_url}/get_order/Central", json=get_order_data)
print("Get Orders by Region Response:", json.dumps(response.json(), indent=2))

# Test getting self postings
get_self_postings_data = {
    "restaurant_id": 1
}
response = requests.get(f"{base_url}/get_self_postings", json=get_self_postings_data)
print("Get Self Postings Response:", json.dumps(response.json(), indent=2))

# Test updating order status to 'ordered'
update_order_data = {
    "order_id": 1,
    "status": "ordered",
    "foodbank_id": 2
}
response = requests.put(f"{base_url}/update_order_ordered", json=update_order_data)
print("Update Order to 'ordered' Response:", json.dumps(response.json(), indent=2))

# Test updating order status to 'accepted'
update_order_data = {
    "order_id": 1,
    "status": "accepted",
    "driver_id": 3
}
response = requests.put(f"{base_url}/update_order_accepted", json=update_order_data)
print("Update Order to 'accepted' Response:", json.dumps(response.json(), indent=2))

# Test updating order status to 'picked up'
update_order_data = {
    "order_id": 1,
    "status": "picked up"
}
response = requests.put(f"{base_url}/update_order_status", json=update_order_data)
print("Update Order to 'picked up' Response:", json.dumps(response.json(), indent=2))
