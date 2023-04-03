import requests
import json

order_data = {
        "order_id": 7,
        
       
    }

response = requests.put("http://accept-order:5009/delivered_order", json=order_data)
print("New Order Response:", json.dumps(response.json(), indent=2))
if response.status_code == 200:
    print("Test passed")
else:
    print("Test failed")