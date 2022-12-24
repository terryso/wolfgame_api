from __future__ import print_function

import os

import pytz as pytz
import requests as requests
import csv
from datetime import datetime


def get_farmers():
    farmers = []
    for i in range(101):
        x = requests.get(f'https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{i + 1}').json()
        characters = x['characters']
        print(f'getting community {i + 1} farmers...')
        for c in characters:
            c_type = c['type']
            action = c['action']
            if c_type == "SHEEP" and action:
                a_type = action['type']
                if a_type == 'COLLECTING':
                    data = action['data']
                    farmer_effects = data['farmerEffects']
                    if farmer_effects:
                        for farmer_effect in farmer_effects:
                            farmer = {
                                "id": farmer_effect["farmer"]["id"],
                                "cooldownUntil": farmer_effect["farmer"]["cooldownUntil"]
                            }
                            # print(farmer)
                            farmers.append(farmer)

    farmers = sorted(farmers, key=lambda e: e.__getitem__('cooldownUntil'), reverse=False)
    with open('farmers.csv', 'w', newline='') as csvfile:
        today = datetime.now(tz=pytz.UTC)
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["Last Update", f"{today} (UTC)"])
        csv_writer.writerow(["Token ID", "Cooldown Until"])
        for farmer in farmers:
            csv_writer.writerow([farmer['id'], farmer['cooldownUntil']])


def push_to_github():
    os.system('./push_to_github.sh')


if __name__ == '__main__':
    get_farmers()
    push_to_github()
