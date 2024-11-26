import requests
import configparser
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    handler = RotatingFileHandler('get_title.log', maxBytes=1_000_000,backupCount=3)
    handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(handler)

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return []

def filter_and_log_titles(data, keywords):
    filetered_titles = []
    type_counts = {"string":0, "integer":0, "other": 0}

    for item in data:
        title = item.get('title', '')
        if not keywords or any(keyword in title for keyword in keywords):
            filetered_titles.append(title)
            title_type = check_type(title)

            if title_type in type_counts:
                type_counts[title_type] += 1
            logging.info(f"Filtered Title: '{title}' (Type: {title_type})")
        
    
    logging.info(f"Type Counts: Strings = {type_counts['string']}, Integers = {type_counts['integer']},Others = {type_counts['other']}")
    return filetered_titles

def check_type(item):
    if isinstance(item, str):
        return "string"
    elif isinstance(item, int):
        return "integer"
    else:
        return "other"
    
def main():
    setup_logging() #initialize the logging

    #Load Configurations
    config_file = "dev.conf"
    config = load_config(config_file)

    #Fetch configurations
    url = config.get("api", "url")
    keywords = config.get("filter", "keyword").split(",")
    keywords = [kw.strip() for kw in keywords if kw.strip()]

    #Fetch data from the API
    logging.info(f"Fetching data from URL: {url}")
    data = fetch_data(url)

    if not data:
        logging.error("No data was retrieved. Exiting.")
        return
    
    if not keywords:
        logging.info("No valid keywords found. Fetching all the titles.")

    #Process the data from the API
    filtered_titles = filter_and_log_titles(data, keywords)

    #Log the total filtered titles
    if filtered_titles:
        logging.info(f"Found {len(filtered_titles)} filtered titles")
    else:
        logging.info("No titles found.")
    

if __name__ == "__main__":
    main()
    
