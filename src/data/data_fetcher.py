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
	trains = []
	
	visits = (
        data
        .get("ServiceDelivery", {})
        .get("StopMonitoringDelivery", {})
        .get("MonitoredStopVisit", [])
    )

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

	return _annotate_and_filter_trains(sorted(trains, key=lambda t: t['expected_arrival'])[:2])

def _annotate_and_filter_trains(trains: list) -> list:
	now_dt = datetime.datetime.now(datetime.timezone.utc)
	for t in trains:
		expected = t.get('expected_arrival')
		if not expected:
			t['minutes'] = 0
			t['_secs_until'] = float('inf')
			continue
		secs = (expected - now_dt).total_seconds()
		mins = int(secs // 60) if secs > 0 else 0
		t['minutes'] = mins
		t['_secs_until'] = secs

	filtered = [t for t in trains if t.get('_secs_until', 0) >= -20]
	return filtered