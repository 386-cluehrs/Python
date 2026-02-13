from worldfinder.get_countries import get_countries

def country_check(city_name):
    # Get list of countries containing a city
    country = get_countries(city_name) # Replace cityName with the actual city name
    return country