import requests
import json
import sys

API_URL = "http://localhost:5000/api"

def print_response(resp):
    """Print the response details nicely formatted"""
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except:
        print(resp.text)
    print()

def get_all_carriers():
    """Get all carriers"""
    print("===== Getting all carriers =====")
    resp = requests.get(f"{API_URL}/carriers")
    print_response(resp)

def get_carrier(carrier_id):
    """Get a specific carrier"""
    print(f"===== Getting carrier {carrier_id} =====")
    resp = requests.get(f"{API_URL}/carriers/{carrier_id}")
    print_response(resp)

def add_carrier():
    """Add a new carrier"""
    print("===== Adding a new carrier =====")
    new_carrier = {
        "Name": "Battle Cruiser",
        "ID": "ABC-123",
        "Position": "Sol",
        "Owner": "TestUser",
        "Owner_Discord": "TestUser#1234",
        "Docking": "Everyone",
        "Inara": "https://inara.cz/elite/station/example/",
        "Market": {
            "Needs": {
                "Tritium": {
                    "Amount": 500,
                    "Price": 40000
                }
            },
            "Sells": {
                "Gold": {
                    "Amount": 1000,
                    "Price": 50000
                }
            }
        },
        "Cargo": {
            "Ore": 50,
            "Metal": 100
        },
        "Tritium": 2000
    }
    resp = requests.post(f"{API_URL}/carriers", json=new_carrier)
    print_response(resp)
    return "ABC-123"

def update_carrier(carrier_id):
    """Update a carrier"""
    print(f"===== Updating carrier {carrier_id} =====")
    update_data = {
        "Name": "Updated Battle Cruiser",
        "Position": "Alpha Centauri"
    }
    resp = requests.put(f"{API_URL}/carriers/{carrier_id}", json=update_data)
    print_response(resp)

def update_market(carrier_id):
    """Update a carrier's market"""
    print(f"===== Updating carrier {carrier_id} market =====")
    market_data = {
        "Needs": {
            "Tritium": {
                "Amount": 1000,
                "Price": 45000
            },
            "Platinum": {
                "Amount": 500,
                "Price": 250000
            }
        },
        "Sells": {
            "Gold": {
                "Amount": 2000,
                "Price": 48000
            },
            "Painite": {
                "Amount": 100,
                "Price": 300000
            }
        }
    }
    resp = requests.put(f"{API_URL}/carriers/{carrier_id}/market", json=market_data)
    print_response(resp)

def delete_carrier(carrier_id):
    """Delete a carrier"""
    print(f"===== Deleting carrier {carrier_id} =====")
    resp = requests.delete(f"{API_URL}/carriers/{carrier_id}")
    print_response(resp)

if __name__ == "__main__":
    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("Fleet Carrier API Test Script")
        print("Usage:")
        print("  python api-test.py                     - Run all tests")
        print("  python api-test.py get                 - Get all carriers")
        print("  python api-test.py get <carrier_id>    - Get specific carrier")
        print("  python api-test.py add                 - Add a test carrier")
        print("  python api-test.py update <carrier_id> - Update a carrier")
        print("  python api-test.py market <carrier_id> - Update carrier market")
        print("  python api-test.py delete <carrier_id> - Delete a carrier")
        sys.exit(0)
    
    # Parse command line arguments for specific tests
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "get" and len(sys.argv) > 2:
            get_carrier(sys.argv[2])
        elif command == "get":
            get_all_carriers()
        elif command == "add":
            add_carrier()
        elif command == "update" and len(sys.argv) > 2:
            update_carrier(sys.argv[2])
        elif command == "market" and len(sys.argv) > 2:
            update_market(sys.argv[2])
        elif command == "delete" and len(sys.argv) > 2:
            delete_carrier(sys.argv[2])
        else:
            print("Invalid command. Use --help for usage information.")
    else:
        # Run all tests in sequence
        print("Running all API tests")
        get_all_carriers()
        
        # First, check if QFY-3XN exists
        get_carrier("QFY-3XN")
        
        # Add a new carrier for testing
        new_id = add_carrier()
        
        # Update the new carrier
        update_carrier(new_id)
        
        # Update the market
        update_market(new_id)
        
        # Get the updated carrier
        get_carrier(new_id)
        
        # Delete the test carrier
        delete_carrier(new_id)
        
        print("API tests completed!")
