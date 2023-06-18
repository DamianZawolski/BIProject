def remap_time(time):
    if time >= 5 and time < 12:
        return 'Morning'
    elif time >= 12 and time < 18:
        return 'Afternoon'
    elif time >= 18 and time < 22:
        return 'Evening'
    else:
        return 'Night'

def remap_perciption(perciption):
    if perciption == 0:
        return 'No'
    elif perciption < 2.5:
        return 'Light'
    elif perciption < 7.6:
        return 'Moderate'
    elif perciption < 50.8:
        return 'Heavy'
    else:
        return 'Violent'
    

def remap_wind(wind):
    if wind < 1.6:
        return 'Calm'
    elif wind < 5.5:
        return 'Light'
    elif wind < 11.1:
        return 'Moderate'
    elif wind < 19.8:
        return 'Fresh'
    elif wind < 28.5:
        return 'Strong'
    elif wind < 38.9:
        return 'Near Gale'
    elif wind < 49.6:
        return 'Gale'
    elif wind < 61.2:
        return 'Strong Gale'
    elif wind < 74.2:
        return 'Storm'
    else:
        return 'Violent Storm'
    

def remap_temperature(temperature):
    if temperature < -20:
        return 'Extreme Cold'
    elif temperature < -10:
        return 'Very Cold'
    elif temperature < 0:
        return 'Cold'
    elif temperature < 10:
        return 'Cool'
    elif temperature < 20:
        return 'Mild'
    elif temperature < 30:
        return 'Warm'
    elif temperature < 40:
        return 'Hot'
    else:
        return 'Very Hot'
    
    
def remap_cloudcover(cloud_cover):
    if cloud_cover == 0:
        return 'No'
    elif cloud_cover > 0 and cloud_cover < 10:
        return 'Few'
    elif cloud_cover >=10 and cloud_cover < 25:
        return 'Isolated'
    elif cloud_cover >=25 and cloud_cover < 50:
        return 'Scattered'
    elif cloud_cover >=50 and cloud_cover < 90:
        return 'Broken'
    else:  
        return 'Overcast'