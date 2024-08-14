import requests
import os
import time
import logging

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_wan_ip():
    try:
        response = requests.get('https://api.ipify.org')
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching WAN IP: {e}")
        return None

def write_ip_to_file(ip_address, filename="ip-allow-middleware.yml"):
    config_folder = "/config"
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)

    file_path = os.path.join(config_folder, filename)
    yaml_content = f"""http:
  middlewares:
    local-vpn:
      ipAllowList:
        sourceRange:
          - "{ip_address}"
        ipStrategy: 
          depth: 1""" 

    try:
        with open(file_path, "w") as f:
            f.write(yaml_content)
        logging.info(f"Updated {file_path}")
    except IOError as e:
        logging.error(f"Error writing to file: {e}") 

if __name__ == "__main__":
    interval_seconds = int(os.environ.get('UPDATE_INTERVAL_SECONDS', 3600))
    previous_ip = None  # Store the previous IP address

    while True:
        wan_ip = get_wan_ip()
        if wan_ip and wan_ip != previous_ip:
            write_ip_to_file(wan_ip)
            previous_ip = wan_ip  # Update the previous IP
        else:
            if not wan_ip:
                logging.warning("Skipping update due to API error. Retrying in next interval.")
            else:
                logging.debug("WAN IP hasn't changed. Skipping update.")
        time.sleep(interval_seconds)
