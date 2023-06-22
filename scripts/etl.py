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
SAVE_DATA_TO = os.path.join('..', 'etl_tables')


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



def create_type_table(df) -> dict:
    i = 0
    content = {'Type_Id': [], 'Rideable_Type': [], 'Member_Casual': [], 'Type_Id_str': []}
    for bike_type in  df['Rideable_Type'].unique():
        for member_type in df['Member_Casual'].unique():
            content['Type_Id'].append(i)
            content['Rideable_Type'].append(bike_type)
            content['Member_Casual'].append(member_type)
            content['Type_Id_str'].append(bike_type + '_' + member_type)
            i += 1

    return content

def set_rental_type_id(rideable_type, member_type):
    if rideable_type == 'docked_bike':
        if member_type == 'casual':
            return 0
        else:
            return 1
    elif rideable_type == 'electric_bike':
        if member_type == 'casual':
            return 2
        else:
            return 3
    elif rideable_type == 'classic_bike':
        if member_type == 'casual':
            return 4
        else:
            return 5



def create_rental_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a dataframe with rental data

    :param df: dataframe with rental data
    :return: dataframe with rental data
    """
    df_rentals = df[['Ride_Id', 'Started_At', 'Ended_At', 'Start_Station_Id', 'End_Station_Id', 'Rideable_Type', 'Member_Casual']].copy()
    df_rentals['Started_At'] = pd.to_datetime(df_rentals['Started_At'], format='%m/%d/%Y %H:%M')
    df_rentals['Ended_At'] = pd.to_datetime(df_rentals['Ended_At'], format='%m/%d/%Y %H:%M')
    df_rentals['Date'] = df_rentals['Started_At'].dt.date
    df_rentals['Ride_Length'] = (df_rentals['Ended_At'] - df_rentals['Started_At']).dt.total_seconds() // 60
    df_rentals['Ride_Length'] = df_rentals['Ride_Length'].astype(int)
    df_rentals['Type_Id'] = df_rentals.apply(lambda x: set_rental_type_id(x['Rideable_Type'], x['Member_Casual']), axis=1)
    df_rentals = df_rentals[['Ride_Id', 'Date', 'Start_Station_Id', 'End_Station_Id', 'Ride_Length', 'Started_At', 'Type_Id']]
    df_rentals.dropna(inplace=True)
    return df_rentals


def create_time_df(df: pd.DataFrame) -> pd.DataFrame:
    df_time = df[['Ride_Id', 'Started_At', 'Ended_At', 'Day']].copy()
    df_time['Ended_At'] = pd.to_datetime(df_time['Ended_At'], format='%m/%d/%Y %H:%M')
    df_time['Started_At'] = pd.to_datetime(df_time['Started_At'], format='%m/%d/%Y %H:%M', errors='coerce')
    df_time.dropna(inplace=True)
    df_time['Date'] = df_time['Started_At'].dt.date
    df_time['Time_Of_The_Day'] = df_time['Started_At'].dt.hour
    df_time['Time_Of_The_Day'] = df_time['Started_At'].dt.hour.apply(remap_time)

    df_time = df_time[['Started_At', 'Time_Of_The_Day', 'Day']]
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





def create_location_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a dataframe with location data, merges start and end station location data
    returns unique station data
    :param df: dataframe with rental data
    :return: dataframe with location data
    """
    start_df = df[['Start_Station_Id', 'Start_Station_Name', 'Start_Lat', 'Start_Lng']].copy()
    start_df.columns = ['Station_Id', 'Station_Name', 'Lat', 'Lng']

    end_df = df[['End_Station_Id', 'End_Station_Name', 'End_Lat', 'End_Lng']].copy()
    end_df.columns = ['Station_Id', 'Station_Name', 'Lat', 'Lng']

    df_stations = pd.concat([start_df, end_df])
    df_stations = df_stations.drop_duplicates(subset=['Station_Id'])
    df_stations.dropna(inplace=True)
    logger.info('station df create succesfully.')
    return df_stations


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


    df_rentals = create_rental_df(bike_rentals)
    logger.info("Rental dataframe created successfully")
    df_time = create_time_df(bike_rentals)
    logger.info("Time dataframe created successfully")
    df_stations = create_location_df(bike_rentals)
    logger.info("Location dataframe created successfully")

    # creating types table
    df_types = pd.DataFrame(create_type_table(bike_rentals))

    df_weather = create_weather_df(weather)
    logger.info("Weather dataframe created successfully")

    # saving all df to csv files    
    logger.info('Saving data...')
    os.makedirs(SAVE_DATA_TO, exist_ok=True)
    df_rentals.to_csv(os.path.join(SAVE_DATA_TO, 'rentals.csv'), index=False)
    df_time.to_csv(os.path.join(SAVE_DATA_TO, 'time.csv'), index=False)
    df_stations.to_csv(os.path.join(SAVE_DATA_TO, 'stations.csv'), index=False)
    df_types.to_csv(os.path.join(SAVE_DATA_TO, 'types.csv'), index=False)
    df_weather.to_csv(os.path.join(SAVE_DATA_TO, 'weather.csv'), index=False)
    logger.info("Dataframes saved successfully")


if __name__ == "__main__":  
    main()
