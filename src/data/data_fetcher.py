import datetime
import time
from .. import config
import requests
import xml.etree.ElementTree as ET

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
	print("API response:", resp.text)
	
	root = ET.fromstring(resp.text)
	print("ROOT", root)

	trains = []
	for visit in root.findall(".//MonitoredStopVisit"):
		call = visit.find(".//MonitoredCall")
		exp = call.find("ExpectedArrivalTime")
		if exp is not None and exp.text:
			dt = datetime.datetime.fromisoformat(exp.text.replace("Z", "+00:00"))
			trains.append({'expected_arrival': dt})
			
	print("Fetched trains:", trains)

	return sorted(trains, key=lambda t: t['expected_arrival'])[:2]

