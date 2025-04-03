import requests
import json
from datetime import datetime, timedelta

class F1API:
    """Class to interact with the Ergast F1 API and fetch real F1 data."""
    
    def __init__(self):
        self.base_url = "http://ergast.com/api/f1"
        self.current_year = datetime.now().year
    
    def fetch_from_api(self, endpoint):
        """Fetch data from the Ergast API."""
        try:
            url = f"{self.base_url}/{endpoint}.json"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching data from API: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception when fetching data: {e}")
            return None
    
    def get_current_drivers(self):
        """Get all drivers for the current season."""
        drivers_data = self.fetch_from_api(f"{self.current_year}/drivers")
        
        if drivers_data and 'MRData' in drivers_data and 'DriverTable' in drivers_data['MRData']:
            drivers = {}
            for driver in drivers_data['MRData']['DriverTable']['Drivers']:
                driver_name = f"{driver['givenName']} {driver['familyName']}"
                drivers[driver_name] = {
                    'id': driver['driverId'],
                    'number': int(driver.get('permanentNumber', 0)) or 1,
                    'team': driver.get('constructor', 'Unknown')
                }
            return drivers
        return {}
    
    def get_current_constructors(self):
        """Get all constructors for the current season."""
        constructors_data = self.fetch_from_api(f"{self.current_year}/constructors")
        
        if constructors_data and 'MRData' in constructors_data and 'ConstructorTable' in constructors_data['MRData']:
            constructors = {}
            for constructor in constructors_data['MRData']['ConstructorTable']['Constructors']:
                constructors[constructor['name']] = {
                    'id': constructor['constructorId'],
                    'nationality': constructor['nationality']
                }
            return constructors
        return {}
    
    def get_race_results(self):
        """Get race results for the current season."""
        results_data = self.fetch_from_api(f"{self.current_year}/results")
        
        if results_data and 'MRData' in results_data and 'RaceTable' in results_data['MRData']:
            race_results = {}
            for race in results_data['MRData']['RaceTable']['Races']:
                race_name = race['raceName']
                race_results[race_name] = {
                    'date': race['date'],
                    'results': {}
                }
                
                for result in race['Results']:
                    driver_name = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
                    position = int(result['position']) if result['position'] != 'NC' else 20
                    race_results[race_name]['results'][driver_name] = {
                        'position': position,
                        'points': float(result.get('points', 0)),
                        'status': result.get('status', 'Finished')
                    }
            return race_results
        return {}
    
    def get_constructor_standings(self):
        """Get constructor standings for the current season."""
        standings_data = self.fetch_from_api(f"{self.current_year}/constructorStandings")
        
        if standings_data and 'MRData' in standings_data and 'StandingsTable' in standings_data['MRData']:
            constructor_standings = {}
            if 'StandingsLists' in standings_data['MRData']['StandingsTable'] and standings_data['MRData']['StandingsTable']['StandingsLists']:
                for standing in standings_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']:
                    constructor_name = standing['Constructor']['name']
                    constructor_standings[constructor_name] = {
                        'position': int(standing['position']),
                        'points': float(standing['points']),
                        'wins': int(standing.get('wins', 0))
                    }
            return constructor_standings
        return {}
    
    def get_driver_standings(self):
        """Get driver standings for the current season."""
        standings_data = self.fetch_from_api(f"{self.current_year}/driverStandings")
        
        if standings_data and 'MRData' in standings_data and 'StandingsTable' in standings_data['MRData']:
            driver_standings = {}
            if 'StandingsLists' in standings_data['MRData']['StandingsTable'] and standings_data['MRData']['StandingsTable']['StandingsLists']:
                for standing in standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
                    driver_name = f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}"
                    driver_standings[driver_name] = {
                        'position': int(standing['position']),
                        'points': float(standing['points']),
                        'wins': int(standing['wins']),
                        'team': standing['Constructors'][0]['name'] if standing.get('Constructors') else 'Unknown'
                    }
            return driver_standings
        return {}
    
    def get_qualifying_results(self):
        """Get qualifying results for the current season."""
        qualifying_data = self.fetch_from_api(f"{self.current_year}/qualifying")
        
        if qualifying_data and 'MRData' in qualifying_data and 'RaceTable' in qualifying_data['MRData']:
            qualifying_results = {}
            for race in qualifying_data['MRData']['RaceTable']['Races']:
                race_name = race['raceName']
                qualifying_results[race_name] = {
                    'date': race['date'],
                    'results': {}
                }
                
                for result in race['QualifyingResults']:
                    driver_name = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
                    position = int(result['position'])
                    qualifying_results[race_name]['results'][driver_name] = {
                        'position': position,
                        'q1': result.get('Q1', ''),
                        'q2': result.get('Q2', ''),
                        'q3': result.get('Q3', '')
                    }
            return qualifying_results
        return {}
    
    def get_historical_data(self, year=None):
        """Get historical data for a specific year."""
        if year is None:
            year = self.current_year - 1
        
        historical_data = {
            'drivers': self.get_current_drivers(),
            'constructors': self.get_current_constructors(),
            'race_results': self.get_race_results(),
            'constructor_standings': self.get_constructor_standings(),
            'driver_standings': self.get_driver_standings(),
            'qualifying_results': self.get_qualifying_results()
        }
        return historical_data 