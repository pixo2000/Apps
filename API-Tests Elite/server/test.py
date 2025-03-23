import requests
import json
import sys

API_URL = "http://localhost:5000/api"

def update_carrier(carrier_id):
    """Update a carrier"""
    print(f"===== Updating carrier {carrier_id} =====")
    update_data = {
        "Owner": "Updated 2Owner"
    }
    resp = requests.put(f"{API_URL}/carriers/{carrier_id}", json=update_data)
    print("Finished")

update_carrier("ABC-ADF")