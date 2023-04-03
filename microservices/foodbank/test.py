import requests

# Replace this with the URL of your Flask application
flask_url = "http://foodbank:5002/"

# Replace this with the ID of the restaurant you want to retrieve
restaurant_id = 5

# Make an HTTP GET request to the /get_restaurant/<foodbank_id> endpoint
response = requests.get(f"{flask_url}/get_foodbank/<foodbank_id>")

# Check if the request was successful
if response.status_code == 200:
    # Extract the foodbank information from the response
    foodbank_data = response.json()["data"]
    print("Foodbank information:")
    print(f"ID: {foodbank_data['foodbank_id']}")
    print(f"Name: {foodbank_data['foodbank_name']}")
    print(f"Phone number: {foodbank_data['phone_number']}")
    print(f"Address: {foodbank_data['foodbank_address']}")
    print(f"Postal code: {foodbank_data['postal_code']}")
    print(f"Region: {foodbank_data['region']}")
else:
    # Print an error message if the restaurant was not found
    error_message = response.json()["message"]
    print(f"Error: {error_message}")
