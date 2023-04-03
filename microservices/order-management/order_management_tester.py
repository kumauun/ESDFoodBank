import requests
import json

base_url = "http://docker.host.internal:5005"  # Update the port number if your microservice is running on a different port

# Test creating a new order
new_order_data = {
    "region": "Central",
    "foodbank_id": 3,
    "foodbank_phone_number": "123456789",
    "foodbank_address": "123 Foodbank St",
    "foodbank_name": "Foodbank 3",
    "restaurant_id": 1,
    "restaurant_phone_number": "987654321",
    "restaurant_address": "123 Restaurant St",
    "restaurant_name": "Restaurant 1",
    "driver_id": 2,
    "driver_phone_number": "123456789",
    "driver_name": "Driver 2",
    "dish_name": "pizzamozzarella",
    
}


response = requests.post(f"{base_url}/new_order", json=new_order_data)
print("New Order Response:", json.dumps(response.json(), indent=2))

# Test getting orders by region
# response = requests.get(f"{base_url}/get_order/Central")
# print("Get Orders by Region Response:", json.dumps(response.json(), indent=2))

# Test getting self postings
# response = requests.get(f"{base_url}/get_self_postings")
# print("Get Self Postings Response:", json.dumps(response.json(), indent=2))

# Test updating order status to 'ordered'
'''
update_order_data = {
    "order_id": 1,
    "status": "ordered"
}
response = requests.put(f"{base_url}/update_order_ordered", json=update_order_data)
print("Update Order to 'ordered' Response:", json.dumps(response.json(), indent=2))

# Test updating order status to 'accepted'
update_order_data = {
    "order_id": 1,
    "status": "accepted"
}
response = requests.put(f"{base_url}/update_order_accepted", json=update_order_data)
print("Update Order to 'accepted' Response:", json.dumps(response.json(), indent=2))

# Test updating order status
update_order_data = {
    "order_id": 1,
    "status": "picked up"
}
response = requests.put(f"{base_url}/update_order_status", json=update_order_data)
print("Update Order to 'picked up' Response:", json.dumps(response.json(), indent=2))
'''