import aiohttp
import pandas as pd
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class F1DataScraper:
    def __init__(self):
        self.base_url = "http://ergast.com/api/f1"
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    async def collect_data(self):
        """Collect F1 race data from Ergast API"""
        try:
            # Get last 5 years of race results
            current_year = datetime.now().year
            years = range(current_year - 5, current_year + 1)
            
            all_races = []
            async with aiohttp.ClientSession() as session:
                for year in years:
                    races = await self._fetch_year_data(session, year)
                    all_races.extend(races)
            
            # Convert to DataFrame and save
            df = pd.DataFrame(all_races)
            df.to_csv(f"{self.data_dir}/latest_race_data.csv", index=False)
            logger.info(f"Successfully collected {len(df)} race records")
            
        except Exception as e:
            logger.error(f"Error collecting data: {str(e)}")
            raise

    async def _fetch_year_data(self, session, year):
        """Fetch race data for a specific year"""
        url = f"{self.base_url}/{year}/results.json"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    races = []
                    
                    for race in data['MRData']['RaceTable']['Races']:
                        for result in race['Results']:
                            races.append({
                                'year': year,
                                'race_name': race['raceName'],
                                'driver_name': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                                'position': result['position'],
                                'points': result['points'],
                                'constructor': result['Constructor']['name'],
                                'grid': result['grid'],
                                'laps': result['laps'],
                                'status': result['status']
                            })
                    return races
                else:
                    logger.warning(f"Failed to fetch data for year {year}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching data for year {year}: {str(e)}")
            return []

    def preprocess_data(self):
        """Preprocess the collected data"""
        try:
            df = pd.read_csv(f"{self.data_dir}/latest_race_data.csv")
            
            # Convert position to numeric, handling DNF/DNS
            df['position'] = pd.to_numeric(df['position'], errors='coerce')
            
            # Create features
            df['finished_race'] = df['status'] == 'Finished'
            df['points'] = pd.to_numeric(df['points'])
            
            # Calculate driver form (last 3 races)
            df = df.sort_values(['driver_name', 'year', 'race_name'])
            df['recent_points'] = df.groupby('driver_name')['points'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)
            
            # Save preprocessed data
            df.to_csv(f"{self.data_dir}/preprocessed_data.csv", index=False)
            logger.info("Successfully preprocessed data")
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise 