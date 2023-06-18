import os
import sys
import argparse
import logging
import pandas as pd

from remappings import remap_time, remap_perciption, remap_wind, remap_temperature, remap_cloudcover

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

DATA_FOLDER = os.path.join('..', 'data')
BIKE_RENTALS_FILE = 'tripdata_connected.csv'
WEATHER_FILE = 'weather_data.csv'
RENTAL_COLUMNS = ['Ride_Id', 'Rideable_Type', 'Started_At', 'Ended_At',
       'Start_Station_Name', 'Start_Station_Id', 'End_Station_Name',
       'End_Station_Id', 'Start_Lat', 'Start_Lng', 'End_Lat', 'End_Lng',
       'Member_Casual', 'Ride_Length', 'Day_Of_The_Week', 'Day']
WEATHER_COLUMNS = ['time', 'temperature_2m (°C)', 'precipitation (mm)', 'cloudcover (%)',
       'windspeed_10m (km/h)', 'latitude', 'longitude', 'elevation',
       'utc_offset_seconds', 'timezone', 'timezone_abbreviation']


def load_rentals_data(filename=BIKE_RENTALS_FILE, data_folder=DATA_FOLDER):
    """Load the rentals data from the data folder"""
    rentals_data_path = os.path.join(data_folder, filename)
    return pd.read_csv(rentals_data_path)


def load_weather_data(filename=WEATHER_FILE, data_folder=DATA_FOLDER):
    """Load the weather data from the data folder"""
    weather_data_path = os.path.join(data_folder, filename)
    return pd.read_csv(weather_data_path, encoding="Windows-1250", sep=";", decimal=",")


def check_columns(df, columns):
    """Check if all columns are present in the dataframe"""
    if set(columns).issubset(set(df.columns)):
        return True
    else:
        return False
    

def create_time_df(df: pd.DataFrame) -> pd.DataFrame:
    df_time = df[['Ride_Id', 'Ride_Length', 'Started_At', 'Ended_At', 'Day']].copy()

    df_time['Started_At'] = pd.to_datetime(df_time['Started_At'], format='%m/%d/%Y %H:%M')
    df_time['Ended_At'] = pd.to_datetime(df_time['Ended_At'], format='%m/%d/%Y %H:%M')
    df_time['Date'] = df_time['Started_At'].dt.date
    df_time['Duration'] = (df_time['Ended_At'] - df_time['Started_At']).dt.total_seconds() // 60
    df_time['Duration'].astype(int)
    df_time['Time_Of_The_Day'] = df_time['Started_At'].dt.hour.apply(remap_time)

    df_time = df_time[['Ride_Id', 'Ride_Length', 'Duration', 'Time_Of_The_Day', 'Day', 'Date']]
    df_time.dropna(inplace=True)
    return df_time


def create_weather_df(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Create a dataframe with weather data
    '''
    df_weather = pd.DataFrame()
    weather_cols = ['Time', 'Temperature', 'Precipitation', 'Wind_Speed', 'Cloudcover', 'Latitude', 'Longitude']
    df_weather[weather_cols] = df[[
        'time', 'temperature_2m (°C)', 'precipitation (mm)', 'windspeed_10m (km/h)', 'cloudcover (%)', 'latitude', 'longitude'
        ]].copy()
    df_weather['Time'] = pd.to_datetime(df_weather['Time'], format='%Y-%m-%d %H:%M:%S')

    float_cols = ['Temperature', 'Precipitation', 'Wind_Speed', 'Cloudcover', 'Latitude', 'Longitude']
    df_weather[float_cols] = df_weather[float_cols].replace(',', '.', regex=True).astype(float)

    df_weather['Date'] = df_weather['Time'].dt.date
    df_weather['Precipitation'] = df_weather['Precipitation'].apply(remap_perciption)
    df_weather['Wind_Speed'] = df_weather['Wind_Speed'].apply(remap_wind)
    df_weather['Temperature'] = df_weather['Temperature'].apply(remap_temperature)
    df_weather['Cloudcover'] = df_weather['Cloudcover'].apply(remap_cloudcover)
    df_weather.dropna(inplace=True)

    return df_weather


def main():
    bike_rentals = load_rentals_data(BIKE_RENTALS_FILE)
    weather = load_weather_data(WEATHER_FILE)
    logger.info("Data loaded successfully")

    if check_columns(bike_rentals, RENTAL_COLUMNS):
        logger.info("Rental columns are present")
    elif check_columns(weather, WEATHER_COLUMNS):
        logger.info("Weather columns are present")
    else:
        logger.error("Columns are mismatched")
        sys.exit(1)

    df_time = create_time_df(bike_rentals)
    logger.info("Time dataframe created successfully")
    df_location = bike_rentals[['Ride_Id', 'Start_Station_Id', 'End_Station_Id']].copy()
    df_location.dropna(inplace=True)
    df_stations = bike_rentals[['Start_Station_Id', 'Start_Station_Name', 'Start_Lat', 'Start_Lng']].copy()
    df_stations = df_stations.drop_duplicates(subset=['Start_Station_Id'])
    df_stations.dropna(inplace=True)
    df_types = bike_rentals[['Ride_Id', 'Rideable_Type', 'Member_Casual']].copy()
    df_types.dropna(inplace=True)

    df_weather = create_weather_df(weather)
    logger.info("Weather dataframe created successfully")

    SAVE_DATA_TO = 'data'
    os.makedirs(SAVE_DATA_TO, exist_ok=True)
    df_time.to_csv(os.path.join(SAVE_DATA_TO, 'time.csv'), index=False)
    df_location.to_csv(os.path.join(SAVE_DATA_TO, 'location.csv'), index=False)
    df_stations.to_csv(os.path.join(SAVE_DATA_TO, 'stations.csv'), index=False)
    df_types.to_csv(os.path.join(SAVE_DATA_TO, 'types.csv'), index=False)
    df_weather.to_csv(os.path.join(SAVE_DATA_TO, 'weather.csv'), index=False)
    logger.info("Dataframes saved successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV Parser')
    parser.add_argument('-d', '--data_folder', help='Data folder path', default=None)
    parser.add_argument('-r', '--rentals', help='CSV file path for rentals')
    parser.add_argument('-w', '--weather', help='CSV file path for weather')
    args = parser.parse_args()

    if args.data_folder:
        BIKE_RENTALS_FILE = args.rentals
    if args.data_folder:
        WEATHER_FILE = args.weather
    
    main()
