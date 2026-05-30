import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check what sources are available
from vnstock3 import Vnstock, Listing

# Check Listing
try:
    listing = Listing(source='VCI')
    print("Listing.VCI:", dir(listing))
except Exception as e:
    print("Listing VCI error:", e)

# Try Finance instead
from vnstock3 import Finance
try:
    f = Finance(symbol='VNM')
    print("Finance:", dir(f))
except Exception as e:
    print("Finance error:", e)
