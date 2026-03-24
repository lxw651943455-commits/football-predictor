"""Test the prediction flow to verify it takes 20-40 seconds"""

import requests
import json
import time

# Start time
start = time.time()

print("="*60)
print("TESTING PREDICTION FLOW")
print("="*60)
print("Sending request to http://127.0.0.1:8000/api/predict")
print()

# Send request
response = requests.post(
    'http://127.0.0.1:8000/api/predict',
    headers={'Content-Type': 'application/json'},
    json={
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "league": "La Liga",
        "home_odds": 2.10,
        "draw_odds": 3.40,
        "away_odds": 3.60
    },
    timeout=120
)

elapsed = time.time() - start

print()
print("="*60)
print(f"RESPONSE RECEIVED in {elapsed:.2f} seconds")
print("="*60)

if response.status_code == 200:
    data = response.json()
    print(f"Data source: {data.get('realtime_data_summary', {}).get('data_source', 'unknown')}")
    print(f"Home injuries: {data.get('realtime_data_summary', {}).get('home_injuries_count', 0)}")
    print(f"H2H matches: {data.get('realtime_data_summary', {}).get('h2h_matches_count', 0)}")
    print(f"Predicted score: {data.get('predicted_score')}")
    print(f"Winner: {data.get('predicted_winner')}")
    print()

    if elapsed < 10:
        print("WARNING: Prediction completed too fast!")
        print("Expected: 20-40 seconds")
        print("Actual: {:.2f} seconds".format(elapsed))
        print()
        print("This suggests CSV fallback was used instead of simulated real-time data.")
    elif 15 <= elapsed <= 40:
        print("SUCCESS: Prediction completed in expected time range!")
    else:
        print(f"Unexpected timing: {elapsed:.2f} seconds")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
