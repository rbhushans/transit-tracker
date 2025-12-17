import datetime
import time
from .. import config
import requests
import json

def fetch_trains():
	now_utc = datetime.datetime.now(datetime.timezone.utc)

	# mock data
	if config.DEBUG:
		if not hasattr(fetch_trains, "debug_trains"):
			fetch_trains.debug_trains = [
				{'expected_arrival': now_utc + datetime.timedelta(minutes=3)},
				{'expected_arrival': now_utc + datetime.timedelta(minutes=8)},
			]
			fetch_trains.last_tick = time.time()

		# decrement every 15 seconds
		if time.time() - fetch_trains.last_tick >= 15:
			for t in fetch_trains.debug_trains:
				mins = int((t['expected_arrival'] - now_utc).total_seconds() // 60) - 1
				if mins < 0:
					mins = 8
				t['expected_arrival'] = now_utc + datetime.timedelta(minutes=mins)
			fetch_trains.last_tick = time.time()

		return sorted(
			fetch_trains.debug_trains,
			key=lambda t: int((t['expected_arrival'] - now_utc).total_seconds() // 60)
		)

	# real API path 
	resp = requests.get(config.API_URL)
	resp.raise_for_status()
	data = json.loads(resp.content.decode("utf-8-sig"))
	print("API Response:", data)
	trains = []
	
	visits = (
        data
        .get("ServiceDelivery", {})
        .get("StopMonitoringDelivery", {})
        .get("MonitoredStopVisit", [])
    )
	print("Visits:", visits)

	for visit in visits:
		journey = visit.get("MonitoredVehicleJourney", {})
		destination = journey.get("DestinationName")
		
		if config.DESTINATION_NAME:
			# robust compare
			if not destination or destination.strip().lower() != config.DESTINATION_NAME.strip().lower():
				continue
		call = journey.get("MonitoredCall", {})
		exp_time = call.get("ExpectedArrivalTime")

		if exp_time:
			dt = datetime.datetime.fromisoformat(exp_time.replace("Z", "+00:00"))
			trains.append({'expected_arrival': dt, 'destination': destination})
			
	print("Trains:", trains)

	return sorted(trains, key=lambda t: t['expected_arrival'])[:2]

