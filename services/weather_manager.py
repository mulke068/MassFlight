
from math import cos, pi, sin, asin, sqrt, radians
import requests
import csv
from regex import regex
import logging

LOG = logging.getLogger(__name__)


class WeatherManager:
    def __init__(self):
        self.data = {}
        self.stations = []
        self.station_code = None
        self.station_data = {}
        self.weather = {}

        self.init()
    
    def init(self):
        self._load_stations()
    
    def get(self, lat, lon):
        
        self.station_code , distance = self._find_station(lat, lon)
        # data is a csv file :
        # ELLX;06;590;Luxembourg / Luxembourg;;Luxembourg;6;49-37N;006-13E;49-37N;006-13E;376;379;P
        
        # after station ist found
        if self.station_code is not None:
            self.station_data = requests.get(f'https://tgftp.nws.noaa.gov/data/observations/metar/stations/{self.station_code}.TXT') # Lux sation ELLX for testing

            # extract the formated data 
            # get something like this : 
            # "
            # 2025/11/28 09:50
            # ELLX 280950Z 18006KT 0100 R24/0325N FG VV001 04/04 Q1018 NOSIG
            # "

            self.weather = "...."

    def _convert_DM_to_DD(self, dm: str) -> float:
        """This Function converts DM(degrees minutes) to DD(decimal degrees)

        Decimal Degrees = degrees + (minutes/60) + (seconds/3600)

        """
        reg = regex.match(r"(\d+)-(\d+)([NSWE])", dm)

        if not reg:
            return None

        degrees = int(reg.group(1))
        minutes = int(reg.group(2))
        direction = reg.group(3)

        if direction == "S" or direction == "W": 
            return (degrees + (minutes/60)) * -1
        else:
            return degrees + (minutes/60)
        
            
    def _load_stations(self):
        
        stations_req = requests.get("https://tgftp.nws.noaa.gov/data/nsd_cccc.txt")

        stations_req.raise_for_status()

        for station in stations_req.text.split("\n"):
            parts = station.split(";")

            if len(parts) < 9:
                continue
            
            station_code = parts[0]
            station_name = parts[3]
            station_country = parts[5]
            lat_str = parts[7]
            lon_str = parts[8]
                
            lat_station = self._convert_DM_to_DD(lat_str)
            lon_station = self._convert_DM_to_DD(lon_str)
                
            if lat_station is None or lon_station is None:
                continue

            self.stations.append([
                    lat_station,
                    lon_station,
                    station_code,
                    station_name,
                    station_country
                ])
    
    def _find_station(self, target_lat, target_lon):
        nearest_station = 999999
        station_code = None
        
        for station in self.stations:
            
            distance = self._haversine_distance(target_lat, target_lon, station[0], station[1])

            if distance < nearest_station:
                nearest_station = distance
                station_code = station[2]
        
        return station_code, nearest_station



    def _haversine_distance(self, lat1, lon1, lat2, lon2) -> float:
        # https://en.wikipedia.org/wiki/Radian
        # https://en.wikipedia.org/wiki/Haversine_formula
        
        # d = r * theta
        
        r = 6371 # Earth radius in km
        
        # degree to radian
        lat1, lon1, lat2, lon2 = [x * (pi / 180) for x in [lat1, lon1, lat2, lon2]]

        # haversine formula
        delta_phi = lat2 - lat1
        delta_lambda = lon2 - lon1

        haversine = (1 - cos(delta_phi) + cos(lat1) * cos(lat2) * (1 - cos(delta_lambda))) / 2

        theta = 2 * asin(sqrt(haversine))
        
        return r * theta



if __name__ == "__main__":
    wm = WeatherManager()

    # wm._load_stations()
    # print(wm.stations)
    # data = wm._find_station(49.8157635,6.1315139999999815)
    data = wm.get(49.8157635,6.1315139999999815) # Luxembourg
    print(data)
    # res = wm._haversine_distance(38.898,-77.037,49.818,6.134)
    # print(res)
    

    # print(wm._convert_DMS_to_DD("50-37N"))
