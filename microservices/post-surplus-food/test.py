import requests
import json

# Set up test data
data_passed= {
    'restaurant_id': 11,
    'dish_name': 'pizzamozzarella'
}

# Start the services first before running this test

# Test the complex microservice
#response = requests.get(f"http://localhost:5001/get_restaurant/{restaurant_id}")
response = requests.post('http://localhost:5007/post_food', json=data_passed)
print("New Order Response:", json.dumps(response.json(), indent=2))

if response.status_code == 200:
    print("Test passed")
else:
    print("Test failed")
# Check the response message


# Check that the order was added to the order management microservice


# Check that the foodbank was notified

