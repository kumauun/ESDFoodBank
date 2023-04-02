import requests
import json

order_data = {
        "order_id": 25,
        
       
    }

response = requests.put("http://127.0.0.1:5102/order_delivered", json=order_data)
print("New Order Response:", json.dumps(response.json(), indent=2))
if response.status_code == 200:
    print("Test passed")
else:
    print("Test failed")