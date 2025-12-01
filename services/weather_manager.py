import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path so Python can find 'config'
sys.path.append(parent_dir)


import json
from math import cos, pi, asin, sqrt
import os
import requests
from regex import regex
import logging

from config.others_config import CACHE_FILE, MAX_FETCH_ATTEMPTS

LOG = logging.getLogger(__name__)


class WeatherManager:
    def __init__(self):
        self.stations = []
        self.station_code = None
        self.station_distance = None
        self.station_data = None
        self.weather = {}

        # _find_station
        self.last_target_lat = None
        self.last_target_lon = None
        self.station_with_distance = []

        self._load_stations()
    
    def get(self, lat, lon) -> tuple[dict, int]: 
        """
        
        
        Args:
            lat (float): Latitude
            lon (float): Longitude

        Returns:
            dict: 
                -station: {time, code, distance}
                
                -wind: {direction, speed, gust, unit}
                
                -temperature: {value, dewpoint}
                
                -pressure: {value, unit}
            int:
                Number of closest station
        """
        
        req_station_data = None
        fetch_trys = 0
        # ELLX;06;590;Luxembourg / Luxembourg;;Luxembourg;6;49-37N;006-13E;49-37N;006-13E;376;379;P

        # self.station_code = "ELLX"
        # self.station_distance = 0
        
        try:
            for fetch_try in range(MAX_FETCH_ATTEMPTS):
                LOG.info("Requesting station data ... ")
                self.station_code , self.station_distance = self._find_station(lat, lon, fetch_try)
                LOG.info(f"Station code {self.station_code} distance {self.station_distance}")
                req = requests.get(f'https://tgftp.nws.noaa.gov/data/observations/metar/stations/{self.station_code}.TXT', timeout=10)
                LOG.info(req.status_code)
                if req.status_code == 200:
                    req_station_data = req
                    break
                fetch_trys += 1


            # station_data = "2025/11/28 09:50 ELLX 280950Z 14019G25MPS 0100 R24/0325N FG VV001 04/04 Q1018 NOSIG"
            # self.station_data = "2012/11/15 22:00 CWDL 152200Z VRB02KT 10SM BKN070 OVC080 M05/M05 A2969 RMK AC6AS2 -4.5/-7.0/0/0/0 70031 FINAL SKEDD OBS REP STN CLSNG SLP088"
            station_data = req_station_data.text

        except Exception as e:
            LOG.error(e)
            return None, fetch_trys

        # after station ist found
        if len(self.station_code) > 0:

            try:
                # Timestamp
                r_time = regex.search(r"([0-9]{6}Z)", station_data).group(1)
                if r_time:
                    date = r_time[0:2]
                    h = r_time[2:4]
                    m = r_time[4:6]
                    time = f"{date} {h}:{m}"

                LOG.info(time)
            except Exception as e:
                time = None
            
            # RMK = Remarks (every remark filtred out to not mess with some wird behavior)
            if 'RMK' in station_data:
                station_data = station_data.split('RMK',1)[0]
            
            self.station_data = station_data

            try:
                # Wind Data
                r_wind = regex.search(r"(\d{3}|VRB)(\d{2})(\w{1}\d{2})?(KT|MPS|KMH)", station_data)
            
                if r_wind:
                    direction = r_wind.group(1)
                    speed = r_wind.group(2)
                    gust = r_wind.group(3) if r_wind.group(3) else None
                    unit = r_wind.group(4)
                
                    self.weather["wind"] = {
                        "direction": direction,
                        "speed": speed,
                        "gust": gust,
                        "unit": unit
                    }
            
                LOG.info(f"Direction {direction}° Speed {speed}{unit} Gust {gust}{unit}")
            except Exception as e:
                self.weather["wind"] = None

            try:
                # Temperature Data
                r_temp = regex.search(r'(?<!R)(M?\d{2})/(M?\d{2})', station_data)
                if r_temp:
                    temp = r_temp.group(1).replace('M', '-')
                    dewpoint = r_temp.group(2).replace('M', '-')

                    self.weather["temperature"] = {
                        "value": temp,
                        "dewpoint": dewpoint
                    }
                
                LOG.info(f"Temperature {temp}°C Dewpoint {dewpoint}°C")
            except Exception as e:
                self.weather["temperature"] = None

            try:
                # Air Pressure (Altimeter)
                # Q = Matrix , A = Imperial
                r_qnh = regex.search(r'([AQ])(\d{4})', station_data)
                if r_qnh:
                    unit = r_qnh.group(1)
                    pressure = r_qnh.group(2)
                    if unit == 'A':
                        p1 = pressure[0:2]
                        p2 = pressure[2:4]
                        converted = f"{p1}.{p2}"
                        pressure = float(converted) * (3386.389/100)
                    unit = 'hPa'

                    self.weather["pressure"] = {
                        "value": pressure,
                        "unit": unit
                    }
            
                LOG.info(f"Pressure {pressure}{unit}")
            except Exception as e:
                self.weather["pressure"] = None
            
            self.weather["station"] = {
                "code": self.station_code,
                "distance": self.station_distance,
                "time": time,
            }

            return self.weather, fetch_trys
        else:
            return None, fetch_trys
        
            
    def _load_stations(self):
        
        if os.path.exists(CACHE_FILE):
            LOG.info("Loading stations from cache ... ")
            with open(CACHE_FILE, "r") as file:
                self.stations = json.load(file)
            return
        else:
            LOG.info("Requesting all stations ... ")
            self._fetch_stations()
            self._save_stations()

    
    def _fetch_stations(self):
        stations_req = requests.get("https://tgftp.nws.noaa.gov/data/nsd_cccc.txt")
        LOG.info(stations_req.status_code)

        stations_req.raise_for_status()

        parsed_stations = []
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

            parsed_stations.append([
                    lat_station,
                    lon_station,
                    station_code,
                    station_name,
                    station_country
                ])
        self.stations = parsed_stations
    
    def _save_stations(self):
        LOG.info("Saving stations to cache ... ")
        with open(CACHE_FILE, "w") as file:
            json.dump(self.stations, file, indent=4)
    
    
    # i want to add that i can say that it should use the 2second nearest
    def _find_station(self, target_lat, target_lon, n=0):
        # nearest_station = 999999
        station_code = None
        station_with_distance = []

        if self.last_target_lat != target_lat or self.last_target_lon != target_lon:
            self.last_target_lat = target_lat
            self.last_target_lon = target_lon

            for station in self.stations:
                distance = self._haversine_distance(target_lat, target_lon, station[0], station[1])
                # if distance < nearest_station:
                #     nearest_station = distance
                #     station_code = station[2]
                station_with_distance.append([distance, station[2]])
        
            self.station_with_distance = station_with_distance.sort(key=lambda x: x[0])
            # station_with_distance.sort()
        else:
            station_with_distance = self.station_with_distance

        station_code = station_with_distance[n][1]
        station_distance = station_with_distance[n][0]
        
        return station_code, station_distance 

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
    
    LOG.setLevel(logging.INFO)
    LOG.addHandler(logging.StreamHandler())
    
    wm = WeatherManager()

    # wm._load_stations()
    # print(wm.stations)
    # data = wm._find_station(49.8157635,6.1315139999999815)
    # print(data)
    # data = wm._find_station(49.8157635,6.1315139999999815,1)
    # print(data)
    # data = wm._find_station(49.8157635,6.1315139999999815,2)
    # print(data)
    
    # data = wm.get(49.8157635,6.1315139999999815) # Luxembourg
    # print(data) # // Station Code ELLX
    # delay(1000)
    # data = wm.get(48.846659, 2.349194) # Paris | Frankreich 
    # print(data)
    # delay(1000)
    data = wm.get(35.675978, 139.721296) # Tokio | Japan
    print(data)
    # delay(1000)
    # data = wm.get(-34.776794, -58.385598) # Buenos Aires | Argentinien
    # print(data)
    # res = wm._haversine_distance(38.898,-77.037,49.818,6.134)
    # print(res)
    
    

    # print(wm._convert_DMS_to_DD("50-37N"))
