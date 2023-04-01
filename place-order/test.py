import requests
import json

base_url = "http://127.0.0.1:5009"



order_data = {
        "order_id": 8,
        "foodbank_id": 5,
        "restaurant_id": 2,
        "restaurant_name": "tikus",
        "region": "West",
        "dish_name": "cheese"
    }

response = requests.put("http://127.0.0.1:5009/place_order", json=order_data)
print("New Order Response:", json.dumps(response.json(), indent=2))
if response.status_code == 200:
    print("Test passed")
else:
    print("Test failed")
# def test_load_orders():
#     print("Testing: Load Orders")

#     foodbank_id = "1"
#     response = requests.get(base_url + f"/load_orders/{foodbank_id}")
#     result = response.json()

#     print("Status code:", response.status_code)
#     print("Response:", json.dumps(result, indent=2))
#     print("----\n")

