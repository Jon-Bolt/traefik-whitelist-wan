#!/usr/bin/env python3

import json
import os
import signal
import sys
import threading
import time
import requests

CONFIG_PATH = os.environ.get('CONFIG_PATH', os.getcwd())

class GracefulExit:
    def __init__(self):
        self.kill_now = threading.Event()
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("🛑 Stopping main thread...")
        self.kill_now.set()

def get_wan_ip():
    try:
        response = requests.get('https://api.ipify.org')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"😡 Error fetching WAN IP: {e}")
        return None

def write_yaml_to_file(ip_address, filename="ip-allow-middleware.yml"):
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
        print(f"✅ Updated {file_path}")
    except IOError as e:
        print(f"😡 Error writing to file: {e}")

def update_ip(previous_ip, last_change_time):
    global last_unchanged_hour 

    wan_ip = get_wan_ip()
    if wan_ip and wan_ip != previous_ip:
        write_yaml_to_file(wan_ip)
        return wan_ip, time.localtime()
    else:
        if not wan_ip:
            print("⚠️ Skipping update due to API error. Retrying in next interval.")
        else:
            current_hour = time.localtime().tm_hour
            if current_hour != last_unchanged_hour:
                last_change_formatted = time.strftime("%Y-%m-%d %H:%M:%S", last_change_time) if last_change_time else "N/A"
                print(f"ℹ️ WAN IP hasn't changed (last change: {last_change_formatted}). Skipping update.")
                last_unchanged_hour = current_hour 
        return previous_ip, last_change_time

if __name__ == '__main__':
    if sys.version_info < (3, 5):
        raise Exception("🐍 This script requires Python 3.5+")

    interval_seconds = int(os.environ.get('UPDATE_INTERVAL_SECONDS', 3600))
    previous_ip = None
    last_unchanged_hour = None
    last_change_time = None

    if (len(sys.argv) > 1 and sys.argv[1] == "--repeat"):
        print(f"🕰️ Updating YAML file every {interval_seconds} seconds")
        next_time = time.time()
        killer = GracefulExit()
        while True:
            previous_ip, last_change_time = update_ip(previous_ip, last_change_time)
            if killer.kill_now.wait(interval_seconds):
                break
    else:
        update_ip(previous_ip, last_change_time)