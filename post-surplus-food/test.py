import requests
import json

# Set up test data
data_gave = ("food", 2)
'''restaurant_data = {
    "restaurant_name": "Test Restaurant",
    "restaurant_address": "123 Test St",
    "phone_number": "555-1234",
    "region": "Test Region"
}
foodbank_data = {
    "phone_number": "555-5678"
}
order_data = {
    "restaurant_phone_number": "555-1234",
    "restaurant_name": "Test Restaurant",
    "restaurant_address": "123 Test St",
    "region": "Test Region",
    "status": "pending"
}
'''
# Start the services first before running this test

# Test the complex microservice
response = requests.post('http://localhost:5100/post_food', data= data_gave)
print(response.status_code)
# Check the response status code
assert response.status_code == 200

# Check the response message
response_message = json.loads(response.content)
assert response_message == {"code": 200, "message": "Surplus food posted successfully."}

# Check that the order was added to the order management microservice
result = requests.get('http://localhost:5005/orderManagement/get_orders')
assert result.status_code == 200
orders = json.loads(result.content)['data']
print(f"Orders: {orders}")

# Check that the foodbank was notified
result = requests.get('http://localhost:5002/foodbank/get_foodbanks')
assert result.status_code == 200
foodbanks = json.loads(result.content)['data']
print(f"Foodbanks: {foodbanks}")
