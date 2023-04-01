import requests
import json

base_url = "http://127.0.0.1:5008"

def test_place_order():
    print("Testing: Place Order")

    order_data = {
        "order_id": 1,
        "foodbank_id": 1,
        "restaurant_id": 1,
        "restaurant_name": "Test Restaurant",
        "region": "North",
        "dish_name": "Sushi 10 px"
    }

    response = requests.post(base_url + "/place_order", json=order_data)
    result = response.json()

    print("Status code:", response.status_code)
    print("Response:", json.dumps(result, indent=2))
    print("----\n")

# def test_load_orders():
#     print("Testing: Load Orders")

#     foodbank_id = "1"
#     response = requests.get(base_url + f"/load_orders/{foodbank_id}")
#     result = response.json()

#     print("Status code:", response.status_code)
#     print("Response:", json.dumps(result, indent=2))
#     print("----\n")

if __name__ == "__main__":
    test_place_order()
    test_load_orders()
