from __future__ import print_function
import requests as requests
import csv


def get_farmers():
    farmers = []
    for i in range(1):
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
                            print(farmer)
                            farmers.append(farmer)

    with open('farmers.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["ID", "cooldownUntil"])
        for farmer in farmers:
            csv_writer.writerow([farmer['id'], farmer['cooldownUntil']])


if __name__ == '__main__':
    get_farmers()
