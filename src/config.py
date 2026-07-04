# flag to disable network fetches, and use mock data 
DEBUG = False

# API fetch URL for SFMTA transit data
API_KEY = "YOUR_API_KEY" # IMPORTANT - DO NOT COMMIT
AGENCY = "SF"
STOP_CODE = "15194"
# optional: filter by destination name. Set to None to disable
DESTINATION_NAME = "King St & 4th St"
API_URL = f"https://api.511.org/transit/StopMonitoring?api_key={API_KEY}&agency={AGENCY}&stopcode={STOP_CODE}"

# How often we refresh the data (seconds). Transit data has strict rate limits.
REFRESH_INTERVAL = 120

# How often we redraw the screen while awake (seconds). Every refresh wears the
# e-paper panel, so keep this as large as the progress-bar smoothness allows.
DRAW_INTERVAL = 15

# Do a full (ghost-clearing) refresh only every Nth data fetch. Full refreshes
# flash and wear the panel faster than partial refreshes, so now that partials
# are ghost-free we space the full refreshes out. 1 = full refresh every fetch.
FULL_REFRESH_EVERY_N_FETCHES = 2

# Safety net: force a full refresh after this many consecutive partial refreshes,
# in case something stops the fetch-driven full refresh above from happening. At
# a 15s draw interval this is ~5 min; normal operation is driven by the setting
# above, not this.
MAX_PARTIAL_REFRESHES = 20

# The maximum number of minutes to show for incoming trains on the train animation
MAX_TRAIN_MINUTES = 10

HEADER_LABEL = "N"
HEADER_DESTINATION_LABEL = "downtown"
