import requests

# Replace this with the URL of your Flask application
flask_url = "http://restaurant:5001/"

# Replace this with the ID of the restaurant you want to retrieve
restaurant_id = 2

# Make an HTTP GET request to the /get_restaurant/<restaurant_id> endpoint
response = requests.get(f"{flask_url}/get_restaurant/{restaurant_id}")
print(response.status_code)
# Check if the request was successful
if response.status_code == 200:
    # Extract the restaurant information from the response
    restaurant_data = response.json()["data"]
    print("Restaurant information:")
    print(f"ID: {restaurant_data['restaurant_id']}")
    print(f"Name: {restaurant_data['restaurant_name']}")
    print(f"Phone number: {restaurant_data['phone_number']}")
    print(f"Address: {restaurant_data['restaurant_address']}")
    print(f"Region: {restaurant_data['region']}")
else:
    # Print an error message if the restaurant was not found
    error_message = response.json()["message"]
    print(f"Error: {error_message}")
