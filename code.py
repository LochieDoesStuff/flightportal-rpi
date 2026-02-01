import time
import requests
import json
import epd2in13b_V4
from PIL import Image,ImageDraw,ImageFont

try:
    from secrets import secrets
except ImportError:
    print("Secrets including geo are kept in secrets.py, please add them there!")
    raise


# How often to query fr24 - quick enough to catch a plane flying over, not so often as to cause any issues, hopefully
QUERY_DELAY=30
#Area to search for flights, see secrets file
BOUNDS_BOX=secrets["bounds_box"]

#URLs
FLIGHT_SEARCH_HEAD="https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
FLIGHT_SEARCH_TAIL="&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=1"
FLIGHT_SEARCH_URL=FLIGHT_SEARCH_HEAD+BOUNDS_BOX+FLIGHT_SEARCH_TAIL
# Deprecated URL used to return less JSON than the long details URL, but can give ambiguous results
# FLIGHT_DETAILS_HEAD="https://api.flightradar24.com/common/v1/flight/list.json?&fetchBy=flight&page=1&limit=1&maxage=14400&query="

# Used to get more flight details with a fr24 flight ID from the initial search
FLIGHT_LONG_DETAILS_HEAD="https://data-live.flightradar24.com/clickhandler/?flight="

# Request headers
rheaders = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
     "cache-control": "no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
     "accept": "application/json"
}

# Don't think I will need these! 
# Some memory shenanigans - the matrixportal doesn't do great at assigning big strings dynamically. So we create a big static array to put the JSON results in each time.
#json_size=14336
#json_bytes=bytearray(json_size)
   
# Populate the labels, then scroll longer versions of the text
#def display_flight():

# Blank the display when a flight is no longer found
#def clear_flight():
    

# Take the flight ID we found with a search, and load details about it
def get_flight_details(fn):
    try:
        details_response = requests.get(FLIGHT_LONG_DETAILS_HEAD + fn, headers=rheaders, timeout=10)
        details_response.raise_for_status()
        flight_data = details_response.json()
    except requests.RequestException as e:
        print(f" Failed to fetch flight details: {e}")
        exit(1)
    return(flight_data)
    

# Look at the byte array that fetch_details saved into and extract any fields we want
def parse_details_json(fn):

    #global json_bytes

    try:
        # get the JSON from the bytes
        long_json=fn

        # Some available values from the JSON. Put the details URL and a flight ID in your browser and have a look for more.

        flight_number=long_json["identification"]["number"]["default"]
        #print(flight_number)
        flight_callsign=long_json["identification"]["callsign"]
        aircraft_code=long_json["aircraft"]["model"]["code"]
        aircraft_model=long_json["aircraft"]["model"]["text"]
        #aircraft_registration=long_json["aircraft"]["registration"]
        airline_name=long_json["airline"]["name"]
        #airline_short=long_json["airline"]["short"]
        airport_origin_name=long_json["airport"]["origin"]["name"]
        airport_origin_name=airport_origin_name.replace(" Airport","")
        airport_origin_code=long_json["airport"]["origin"]["code"]["iata"]
        #airport_origin_country=long_json["airport"]["origin"]["position"]["country"]["name"]
        #airport_origin_country_code=long_json["airport"]["origin"]["position"]["country"]["code"]
        #airport_origin_city=long_json["airport"]["origin"]["position"]["region"]["city"]
        #airport_origin_terminal=long_json["airport"]["origin"]["info"]["terminal"]
        airport_destination_name=long_json["airport"]["destination"]["name"]
        airport_destination_name=airport_destination_name.replace(" Airport","")
        airport_destination_code=long_json["airport"]["destination"]["code"]["iata"]
        #airport_destination_country=long_json["airport"]["destination"]["position"]["country"]["name"]
        #airport_destination_country_code=long_json["airport"]["destination"]["position"]["country"]["code"]
        #airport_destination_city=long_json["airport"]["destination"]["position"]["region"]["city"]
        #airport_destination_terminal=long_json["airport"]["destination"]["info"]["terminal"]
        #time_scheduled_departure=long_json["time"]["scheduled"]["departure"]
        #time_real_departure=long_json["time"]["real"]["departure"]
        #time_scheduled_arrival=long_json["time"]["scheduled"]["arrival"]
        #time_estimated_arrival=long_json["time"]["estimated"]["arrival"]
        #latitude=long_json["trail"][0]["lat"]
        #longitude=long_json["trail"][0]["lng"]
        #altitude=long_json["trail"][0]["alt"]
        #speed=long_json["trail"][0]["spd"]
        #heading=long_json["trail"][0]["hd"]


        if flight_number:
            print("Flight is called "+flight_number)
        elif flight_callsign:
            print("No flight number, callsign is "+flight_callsign)
        else:
            print("No number or callsign for this flight.")


        # Set up to 6 of the values above as text for display_flights to put on the screen
        # Short strings get placed on screen, then longer ones scroll over each in sequence

        global label1_short
        global label1_long
        global label2_short
        global label2_long
        global label3_short
        global label3_long

        label1_short=flight_number
        label1_long=airline_name
        label2_short=airport_origin_code+"-"+airport_destination_code
        label2_long=airport_origin_name+"-"+airport_destination_name
        label3_short=aircraft_code
        label3_long=aircraft_model

        if not label1_short:
            label1_short=''
        if not label1_long:
            label1_long=''
        if not label2_short:
            label2_short=''
        if not label2_long:
            label2_long=''
        if not label3_short:
            label3_short=''
        if not label3_long:
            label3_long=''

        print("\n" + "="*50)
        print("FLIGHT DETAILS REPORT")
        print("="*50)
        print(f"  Flight Number: {flight_number or 'N/A'}")
        print(f"  Callsign: {flight_callsign or 'N/A'}")
        print(f"  Airline: {airline_name or 'N/A'}")
        print(f"  Route (IATA): {airport_origin_code} → {airport_destination_code}")
        print(f"  Route (Name): {airport_origin_name or 'N/A'} → {airport_destination_name or 'N/A'}")
        print(f"  Aircraft: {aircraft_code or 'N/A'} ({aircraft_model or 'N/A'})")
        print("="*50)


        # optional filter example - check things and return false if you want

        # if altitude > 10000:
        #    print("Altitude Filter matched so don't display anything")
        #    return False

    

    except (KeyError, ValueError,TypeError) as e:
        print("JSON error")
        print (e)
        return False


    return True


# Look for flights overhead
def get_flights():
    try:
        response = requests.get(FLIGHT_SEARCH_URL, headers=rheaders, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f" Failed to fetch flight list: {e}")
        exit(1)

    flight_id = None
    for key, value in data.items():
        if key not in ["version", "full_count"] and len(value) > 13:
            flight_id = key
            break
    if not flight_id:
        print(" No flights found in the search area.")
        exit(1)
    print(f" Found flight: {flight_id}")
    return flight_id

def display_flight():
    #Init fonts
    font20 = ImageFont.truetype('ush_font.ttc', 20)
    font18 = ImageFont.truetype('ush_font.ttc', 18)
    #Init Screen
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.Clear()
    time.sleep(1)
    #Draw image? Idk I'm mostly guessing here
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 250*122
    HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 250*122
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)
    drawblack.text((10, 0), label1_short, font = font20, fill = 0)
    drawblack.text((10, 30), label2_short, font = font20, fill = 0)
    drawblack.text((10, 60), label2_short, font = font20, fill = 0)
    epd.display(epd.getbuffer(HBlackimage))
    time.sleep(2)
    # Sleep Display
    epd.sleep()




# Actual doing of things - loop forever quering fr24, processing any results and waiting to query again
'''
#checkConnection()

#last_flight=''
#while True:

    #checkConnection()

#    w.feed()

    #print("memory free: " + str(gc.mem_free()))

    #print("Get flights...")
    flight_id=get_flights()
#    w.feed()
    

    if flight_id:
        if flight_id==last_flight:
            print("Same flight found, so keep showing it")
        else:
            print("New flight "+flight_id+" found, clear display")
            clear_flight()
            if get_flight_details(flight_id):
#                w.feed()
#                gc.collect()
#                if parse_details_json():
#                    gc.collect()
#                    plane_animation()
#                    display_flight()
#                else:
#                    print("error parsing JSON, skip displaying this flight")
#            else:
#                print("error loading details, skip displaying this flight")
#            
#            last_flight=flight_id
#    else:
#        #print("No flights found, clear display")
#        clear_flight()
    
#    time.sleep(5)


#    for i in range(0,QUERY_DELAY,+5):
#        time.sleep(5)
#        w.feed()
#    gc.collect()
'''
flight_id=get_flights()
flight_json=get_flight_details(flight_id)
parse_details_json(flight_json)
display_flight()