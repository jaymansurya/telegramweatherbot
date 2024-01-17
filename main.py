import os
import telebot
import requests
import logging
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

BOT_TOKEN = os.environ.get('YOUR_BOT_TOKEN')  # Replace with your actual bot token
WEATHER_TOKEN = os.environ.get('YOUR_WEATHER_TOKEN')  # Replace with your actual OpenWeatherMap API token
POLLING_TIMEOUT = None
bot = telebot.TeleBot(BOT_TOKEN)

config = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'short': {
            'format': '%(asctime)s %(levelname)s %(message)s',
        },
        'long': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'plugins': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello, what do you want to search for? I can tell you what the weather is like anywhere in the world as well temperature and humidity.\n To start, attach a location or send me the name of a city and country.')

@bot.message_handler(commands=['weather'])
def send_weather(message):
    location = 'Enter a Location: '
    sent_message = bot.send_message(message.chat.id, location, parse_mode='Markdown')
    bot.register_next_step_handler(sent_message, fetch_weather)

@bot.message_handler(commands=['wind'])
def send_wind_info(message):
    location = 'Enter a Location for Wind Information: '
    sent_message = bot.send_message(message.chat.id, location, parse_mode='Markdown')
    bot.register_next_step_handler(sent_message, fetch_wind_info)

@bot.message_handler(commands=['temp'])
def send_temperature_info(message):
    location = 'Enter a Location for Temperature Information: '
    sent_message = bot.send_message(message.chat.id, location, parse_mode='Markdown')
    bot.register_next_step_handler(sent_message, fetch_temperature_info)

@bot.message_handler(commands=['humidity'])
def send_humidity_info(message):
    location = 'Enter a Location for Humidity Information: '
    sent_message = bot.send_message(message.chat.id, location, parse_mode='Markdown')
    bot.register_next_step_handler(sent_message, fetch_humidity_info)

def location_handler(message):
    geolocator = Nominatim(user_agent="my_app")
    try:
        location_data = geolocator.geocode(message.text)
        if location_data:
            latitude = round(location_data.latitude, 2)
            longitude = round(location_data.longitude, 2)
            logger.info("Latitude '%s' and Longitude '%s' found for location '%s'", latitude, longitude, message.text)
            return latitude, longitude
        else:
            logger.warning('Location not found for input: %s', message.text)
            bot.send_message(message.chat.id, 'Location not found. Please enter a valid location.')
    except Exception as e:
        logger.exception('Error in location_handler: %s', str(e))
        bot.send_message(message.chat.id, 'An error occurred while processing your request.')

def get_weather(latitude, longitude):
    url = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}'.format(latitude, longitude, WEATHER_TOKEN)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.exception('Error in get_weather: %s', str(e))
        return None

def fetch_weather(message): 
    latitude, longitude = location_handler(message)
    if latitude and longitude:
        weather = get_weather(latitude, longitude)
        if weather:
            data = weather['list']
            data_2 = data[0]
            info = data_2['weather']
            data_3 = info[0]
            description = data_3['description']
            weather_message = f'*Weather:* is {description}\n'
            bot.send_message(message.chat.id, 'Here\'s the weather!')
            bot.send_message(message.chat.id, weather_message, parse_mode='Markdown')

def fetch_wind_info(message): 
    latitude, longitude = location_handler(message)
    if latitude and longitude:
        weather = get_weather(latitude, longitude)
        if weather:
            wind_speed = weather['list'][0]['wind']['speed']
            wind_message = f'*Wind Speed:* {wind_speed} m/s\n'
            bot.send_message(message.chat.id, 'Here\'s the wind information!')
            bot.send_message(message.chat.id, wind_message, parse_mode='Markdown')

def fetch_temperature_info(message): 
    latitude, longitude = location_handler(message)
    if latitude and longitude:
        weather = get_weather(latitude, longitude)
        if weather:
            temperature = round(weather['list'][0]['main']['temp'] - 273.15, 2)
            temperature_message = f'*Temperature:* {temperature} °C\n'
            bot.send_message(message.chat.id, 'Here\'s the temperature information!')
            bot.send_message(message.chat.id, temperature_message, parse_mode='Markdown')

def fetch_humidity_info(message): 
    latitude, longitude = location_handler(message)
    if latitude and longitude:
        weather = get_weather(latitude, longitude)
        if weather:
            humidity = weather['list'][0]['main']['humidity']
            humidity_message = f'*Humidity:* {humidity}%\n'
            bot.send_message(message.chat.id, 'Here\'s the humidity information!')
            bot.send_message(message.chat.id, humidity_message, parse_mode='Markdown')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == "__main__":
    try:
        bot.polling(none_stop=True, timeout=POLLING_TIMEOUT)
    except Exception as e:
        logger.exception('Error in polling: %s', str(e))
                           