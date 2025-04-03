class F1API:
    """api to get f1 data n stuff"""
    
    def __init__(self):
        """setup the api client"""
        self.base_url = "http://ergast.com/api/f1"
        self.session = requests.Session()
    
    def get_current_drivers(self):
        """get info about all the drivers rn"""
        try:
            response = self.session.get(f"{self.base_url}/current/drivers.json")
            response.raise_for_status()
            data = response.json()
            
            drivers = {}
            for driver in data['MRData']['DriverTable']['Drivers']:
                drivers[driver['givenName'] + ' ' + driver['familyName']] = {
                    'number': int(driver.get('permanentNumber', 0)),
                    'team': driver.get('team', 'Unknown')
                }
            return drivers
        except:
            # if api fails return some example data
            return {
                'Max Verstappen': {'number': 1, 'team': 'Red Bull Racing'},
                'Lewis Hamilton': {'number': 44, 'team': 'Mercedes'},
                'Charles Leclerc': {'number': 16, 'team': 'Ferrari'},
                'Lando Norris': {'number': 4, 'team': 'McLaren'},
                'Carlos Sainz': {'number': 55, 'team': 'Ferrari'},
                'Sergio Perez': {'number': 11, 'team': 'Red Bull Racing'},
                'George Russell': {'number': 63, 'team': 'Mercedes'},
                'Fernando Alonso': {'number': 14, 'team': 'Aston Martin'},
                'Oscar Piastri': {'number': 81, 'team': 'McLaren'},
                'Lance Stroll': {'number': 18, 'team': 'Aston Martin'},
                'Esteban Ocon': {'number': 31, 'team': 'Alpine'},
                'Pierre Gasly': {'number': 10, 'team': 'Alpine'},
                'Alexander Albon': {'number': 23, 'team': 'Williams'},
                'Logan Sargeant': {'number': 2, 'team': 'Williams'},
                'Yuki Tsunoda': {'number': 22, 'team': 'Visa Cash App RB'},
                'Daniel Ricciardo': {'number': 3, 'team': 'Visa Cash App RB'},
                'Valtteri Bottas': {'number': 77, 'team': 'Stake F1 Team'},
                'Zhou Guanyu': {'number': 24, 'team': 'Stake F1 Team'},
                'Kevin Magnussen': {'number': 20, 'team': 'Haas F1 Team'},
                'Nico Hulkenberg': {'number': 27, 'team': 'Haas F1 Team'}
            }
    
    def get_current_constructors(self):
        """get info about all the teams rn"""
        try:
            response = self.session.get(f"{self.base_url}/current/constructors.json")
            response.raise_for_status()
            data = response.json()
            
            constructors = {}
            for constructor in data['MRData']['ConstructorTable']['Constructors']:
                constructors[constructor['name']] = {
                    'nationality': constructor.get('nationality', 'Unknown'),
                    'first_race': constructor.get('firstRace', 'Unknown')
                }
            return constructors
        except:
            # if api fails return some example data
            return {
                'Red Bull Racing': {'nationality': 'Austrian', 'first_race': '2005'},
                'Mercedes': {'nationality': 'German', 'first_race': '1970'},
                'Ferrari': {'nationality': 'Italian', 'first_race': '1950'},
                'McLaren': {'nationality': 'British', 'first_race': '1966'},
                'Aston Martin': {'nationality': 'British', 'first_race': '2021'},
                'Alpine': {'nationality': 'French', 'first_race': '2021'},
                'Williams': {'nationality': 'British', 'first_race': '1978'},
                'Visa Cash App RB': {'nationality': 'Italian', 'first_race': '2006'},
                'Stake F1 Team': {'nationality': 'Swiss', 'first_race': '1993'},
                'Haas F1 Team': {'nationality': 'American', 'first_race': '2016'}
            }
    
    def get_driver_standings(self):
        """get where all the drivers are in the championship"""
        try:
            response = self.session.get(f"{self.base_url}/current/driverStandings.json")
            response.raise_for_status()
            data = response.json()
            
            standings = {}
            for standing in data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
                driver_name = standing['Driver']['givenName'] + ' ' + standing['Driver']['familyName']
                standings[driver_name] = {
                    'position': int(standing['position']),
                    'points': float(standing['points']),
                    'wins': int(standing['wins'])
                }
            return standings
        except:
            # if api fails return some example data
            return {
                'Lando Norris': {'position': 1, 'points': 43, 'wins': 2},
                'Oscar Piastri': {'position': 2, 'points': 36, 'wins': 0},
                'Max Verstappen': {'position': 3, 'points': 35, 'wins': 0},
                'Lewis Hamilton': {'position': 4, 'points': 30, 'wins': 0},
                'Charles Leclerc': {'position': 5, 'points': 20, 'wins': 0},
                'Carlos Sainz': {'position': 6, 'points': 20, 'wins': 0},
                'Sergio Perez': {'position': 7, 'points': 17, 'wins': 0},
                'George Russell': {'position': 8, 'points': 12, 'wins': 0},
                'Fernando Alonso': {'position': 9, 'points': 4, 'wins': 0},
                'Lance Stroll': {'position': 10, 'points': 4, 'wins': 0}
            }
    
    def get_constructor_standings(self):
        """get where all the teams are in the championship"""
        try:
            response = self.session.get(f"{self.base_url}/current/constructorStandings.json")
            response.raise_for_status()
            data = response.json()
            
            standings = {}
            for standing in data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
                constructor_name = standing['Constructor']['name']
                standings[constructor_name] = {
                    'position': int(standing['position']),
                    'points': float(standing['points']),
                    'wins': int(standing['wins'])
                }
            return standings
        except:
            # if api fails return some example data
            return {
                'McLaren': {'position': 1, 'points': 79, 'wins': 2},
                'Red Bull Racing': {'position': 2, 'points': 52, 'wins': 0},
                'Mercedes': {'position': 3, 'points': 42, 'wins': 0},
                'Ferrari': {'position': 4, 'points': 40, 'wins': 0},
                'Aston Martin': {'position': 5, 'points': 8, 'wins': 0},
                'Alpine': {'position': 6, 'points': 0, 'wins': 0},
                'Williams': {'position': 7, 'points': 0, 'wins': 0},
                'Visa Cash App RB': {'position': 8, 'points': 0, 'wins': 0},
                'Stake F1 Team': {'position': 9, 'points': 0, 'wins': 0},
                'Haas F1 Team': {'position': 10, 'points': 0, 'wins': 0}
            }
    
    def get_race_results(self):
        """get what happened in all the races this season"""
        try:
            response = self.session.get(f"{self.base_url}/current/results.json")
            response.raise_for_status()
            data = response.json()
            
            results = {}
            for race in data['MRData']['RaceTable']['Races']:
                race_name = race['raceName']
                results[race_name] = {'results': {}}
                
                for result in race['Results']:
                    driver_name = result['Driver']['givenName'] + ' ' + result['Driver']['familyName']
                    results[race_name]['results'][driver_name] = {
                        'position': int(result['position']),
                        'points': float(result['points']),
                        'status': result['status']
                    }
            return results
        except:
            # if api fails return some example data
            return {
                'Australia': {
                    'results': {
                        'Lando Norris': {'position': 1, 'points': 25, 'status': 'Finished'},
                        'Oscar Piastri': {'position': 2, 'points': 18, 'status': 'Finished'},
                        'Max Verstappen': {'position': 3, 'points': 15, 'status': 'Finished'},
                        'Lewis Hamilton': {'position': 4, 'points': 12, 'status': 'Finished'},
                        'Charles Leclerc': {'position': 5, 'points': 10, 'status': 'Finished'},
                        'Carlos Sainz': {'position': 6, 'points': 8, 'status': 'Finished'},
                        'Sergio Perez': {'position': 7, 'points': 6, 'status': 'Finished'},
                        'George Russell': {'position': 8, 'points': 4, 'status': 'Finished'},
                        'Fernando Alonso': {'position': 9, 'points': 2, 'status': 'Finished'},
                        'Lance Stroll': {'position': 10, 'points': 1, 'status': 'Finished'}
                    }
                },
                'China': {
                    'results': {
                        'Lando Norris': {'position': 1, 'points': 25, 'status': 'Finished'},
                        'Oscar Piastri': {'position': 2, 'points': 18, 'status': 'Finished'},
                        'Lewis Hamilton': {'position': 3, 'points': 15, 'status': 'Finished'},
                        'Max Verstappen': {'position': 4, 'points': 12, 'status': 'Finished'},
                        'Charles Leclerc': {'position': 5, 'points': 10, 'status': 'Finished'},
                        'Carlos Sainz': {'position': 6, 'points': 8, 'status': 'Finished'},
                        'Sergio Perez': {'position': 7, 'points': 6, 'status': 'Finished'},
                        'George Russell': {'position': 8, 'points': 4, 'status': 'Finished'},
                        'Fernando Alonso': {'position': 9, 'points': 2, 'status': 'Finished'},
                        'Lance Stroll': {'position': 10, 'points': 1, 'status': 'Finished'}
                    }
                }
            }
    
    def get_qualifying_results(self):
        """get how everyone did in qualifying"""
        try:
            response = self.session.get(f"{self.base_url}/current/qualifying.json")
            response.raise_for_status()
            data = response.json()
            
            results = {}
            for race in data['MRData']['RaceTable']['Races']:
                race_name = race['raceName']
                results[race_name] = {'results': {}}
                
                for result in race['QualifyingResults']:
                    driver_name = result['Driver']['givenName'] + ' ' + result['Driver']['familyName']
                    results[race_name]['results'][driver_name] = {
                        'position': int(result['position']),
                        'q1': result.get('Q1', ''),
                        'q2': result.get('Q2', ''),
                        'q3': result.get('Q3', '')
                    }
            return results
        except:
            # if api fails return some example data
            return {
                'Australia': {
                    'results': {
                        'Max Verstappen': {'position': 1, 'q1': '1:16.819', 'q2': '1:16.387', 'q3': '1:15.915'},
                        'Lewis Hamilton': {'position': 2, 'q1': '1:16.941', 'q2': '1:16.604', 'q3': '1:16.223'},
                        'Charles Leclerc': {'position': 3, 'q1': '1:17.090', 'q2': '1:16.665', 'q3': '1:16.277'},
                        'Lando Norris': {'position': 4, 'q1': '1:17.055', 'q2': '1:16.673', 'q3': '1:16.315'},
                        'Carlos Sainz': {'position': 5, 'q1': '1:17.081', 'q2': '1:16.677', 'q3': '1:16.357'}
                    }
                },
                'China': {
                    'results': {
                        'Max Verstappen': {'position': 1, 'q1': '1:16.819', 'q2': '1:16.387', 'q3': '1:15.915'},
                        'Lewis Hamilton': {'position': 2, 'q1': '1:16.941', 'q2': '1:16.604', 'q3': '1:16.223'},
                        'Charles Leclerc': {'position': 3, 'q1': '1:17.090', 'q2': '1:16.665', 'q3': '1:16.277'},
                        'Lando Norris': {'position': 4, 'q1': '1:17.055', 'q2': '1:16.673', 'q3': '1:16.315'},
                        'Carlos Sainz': {'position': 5, 'q1': '1:17.081', 'q2': '1:16.677', 'q3': '1:16.357'}
                    }
                }
            }
    
    def get_current_cars(self):
        """get info about how fast each car is rn"""
        try:
            # this would normally call some api to get car performance data
            # but for now we'll just return some example data
            return {
                'Red Bull Racing': {
                    'aero_efficiency': 0.85,
                    'power_unit_reliability': 0.9,
                    'tire_management': 0.8,
                    'downforce_level': 0.85,
                    'car_development': 0.8,
                    'race_pace': 0.85,
                    'qualifying_pace': 0.8,
                    'reliability': 0.9
                },
                'Mercedes': {
                    'aero_efficiency': 0.8,
                    'power_unit_reliability': 0.85,
                    'tire_management': 0.75,
                    'downforce_level': 0.8,
                    'car_development': 0.75,
                    'race_pace': 0.8,
                    'qualifying_pace': 0.75,
                    'reliability': 0.85
                },
                'Ferrari': {
                    'aero_efficiency': 0.75,
                    'power_unit_reliability': 0.8,
                    'tire_management': 0.7,
                    'downforce_level': 0.75,
                    'car_development': 0.7,
                    'race_pace': 0.75,
                    'qualifying_pace': 0.7,
                    'reliability': 0.8
                },
                'McLaren': {
                    'aero_efficiency': 0.9,
                    'power_unit_reliability': 0.95,
                    'tire_management': 0.85,
                    'downforce_level': 0.9,
                    'car_development': 0.85,
                    'race_pace': 0.9,
                    'qualifying_pace': 0.85,
                    'reliability': 0.95
                },
                'Aston Martin': {
                    'aero_efficiency': 0.7,
                    'power_unit_reliability': 0.75,
                    'tire_management': 0.65,
                    'downforce_level': 0.7,
                    'car_development': 0.65,
                    'race_pace': 0.7,
                    'qualifying_pace': 0.65,
                    'reliability': 0.75
                },
                'Alpine': {
                    'aero_efficiency': 0.65,
                    'power_unit_reliability': 0.7,
                    'tire_management': 0.6,
                    'downforce_level': 0.65,
                    'car_development': 0.6,
                    'race_pace': 0.65,
                    'qualifying_pace': 0.6,
                    'reliability': 0.7
                },
                'Williams': {
                    'aero_efficiency': 0.6,
                    'power_unit_reliability': 0.65,
                    'tire_management': 0.55,
                    'downforce_level': 0.6,
                    'car_development': 0.55,
                    'race_pace': 0.6,
                    'qualifying_pace': 0.55,
                    'reliability': 0.65
                },
                'Visa Cash App RB': {
                    'aero_efficiency': 0.55,
                    'power_unit_reliability': 0.6,
                    'tire_management': 0.5,
                    'downforce_level': 0.55,
                    'car_development': 0.5,
                    'race_pace': 0.55,
                    'qualifying_pace': 0.5,
                    'reliability': 0.6
                },
                'Stake F1 Team': {
                    'aero_efficiency': 0.5,
                    'power_unit_reliability': 0.55,
                    'tire_management': 0.45,
                    'downforce_level': 0.5,
                    'car_development': 0.45,
                    'race_pace': 0.5,
                    'qualifying_pace': 0.45,
                    'reliability': 0.55
                },
                'Haas F1 Team': {
                    'aero_efficiency': 0.45,
                    'power_unit_reliability': 0.5,
                    'tire_management': 0.4,
                    'downforce_level': 0.45,
                    'car_development': 0.4,
                    'race_pace': 0.45,
                    'qualifying_pace': 0.4,
                    'reliability': 0.5
                }
            }
        except:
            return {}
    
    def get_current_tracks(self):
        """get info about all the tracks this season"""
        try:
            response = self.session.get(f"{self.base_url}/current.json")
            response.raise_for_status()
            data = response.json()
            
            tracks = {}
            for race in data['MRData']['RaceTable']['Races']:
                track_name = race['raceName']
                tracks[track_name] = {
                    'type': 'circuit',  # default to circuit
                    'length': 5.0,      # default length
                    'turns': 15,        # default number of turns
                    'straights': 5,     # default number of straights
                    'elevation_changes': 0.5,  # default elevation changes
                    'grip_level': 0.5,  # default grip level
                    'overtaking_opportunities': 0.5,  # default overtaking opportunities
                    'weather_sensitivity': 0.5  # default weather sensitivity
                }
            return tracks
        except:
            # if api fails return some example data
            return {
                'Monaco': {
                    'type': 'street_circuit',
                    'length': 3.337,
                    'turns': 19,
                    'straights': 3,
                    'elevation_changes': 0.8,
                    'grip_level': 0.6,
                    'overtaking_opportunities': 0.2,
                    'weather_sensitivity': 0.7
                },
                'Silverstone': {
                    'type': 'circuit',
                    'length': 5.891,
                    'turns': 18,
                    'straights': 6,
                    'elevation_changes': 0.6,
                    'grip_level': 0.8,
                    'overtaking_opportunities': 0.7,
                    'weather_sensitivity': 0.5
                }
            }
    
    def get_weather_data(self, track_name, race_date):
        """get weather info for the race"""
        try:
            # this would normally call some weather api
            # but for now we'll just return some example data
            return {
                'temperature': 25.0,
                'humidity': 0.6,
                'wind_speed': 10.0,
                'rain_probability': 0.2
            }
        except:
            return {
                'temperature': 25.0,
                'humidity': 0.6,
                'wind_speed': 10.0,
                'rain_probability': 0.2
            } 