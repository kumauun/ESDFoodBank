import requests
import json

# Set up test data
data_passed= {
    'restaurant_id': '7',
    'dish_name': 'rellarellarella'
}


# Start the services first before running this test

# Test the complex microservice
#response = requests.get(f"http://localhost:5001/get_restaurant/{restaurant_id}")
response = requests.post('http://localhost:5100/post_food', json=data_passed)

# Check the response message


# Check that the order was added to the order management microservice


# Check that the foodbank was notified

