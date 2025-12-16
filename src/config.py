# flag to disable network fetches, and use mock data 
DEBUG = True

# API fetch URL for SFMTA transit data
API_KEY = "YOUR_API_KEY" # IMPORTANT - DO NOT COMMIT
AGENCY = "SF"
STOP_CODE = "15194"
API_URL = f"https://api.511.org/transit/StopMonitoring?api_key={API_KEY}&agency={AGENCY}&stopcode={STOP_CODE}"

# How often we refresh the data (seconds). Transit data has strict rate limits.
REFRESH_INTERVAL = 75  

# The maximum number of minutes to show for incoming trains on the train animation
MAX_TRAIN_MINUTES = 10

HEADER_N_LABEL = "N"
HEADER_DESTINATION_LABEL = "downtown"
