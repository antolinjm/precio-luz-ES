from datetime import date
import requests
import pandas as pd

from telegram import Bot
from tabulate import tabulate


TOKEN = "token" #Retrieve this token from @botfather
group_id = "-xxxxxxxxxx" #This is the id of the group where the bot is going to post


def send_message_to_telegram(text):
    bot_token = TOKEN
    chat_id = group_id 
    base_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    payload = {
        'chat_id': group_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(base_url, data=payload)
    return response.json()


#Get current date
formatted_date = date.today().strftime("%Y-%m-%d")

#Get weekday in name format
day = today.weekday()
days = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

######################
#### Request data ####
######################

response = requests.get('https://api.esios.ree.es/archives/70/download_json?locale=es&date=' + formatted_date)

print('Data downloaded correctly')

data_json = response.json()


#Normalize data and convert to pandas dataframe
data = pd.DataFrame(data_json['PVPC'])
data = data[['Dia', 'Hora', 'PCB']]

data['PCB'] = data['PCB'].str.replace(',', '.').astype(float) / 1000

data = data.reset_index(drop=True)
#data = data.set_index('Hora')

min_pcb_row = data[data['PCB'] == data['PCB'].min()]
max_pcb_row = data[data['PCB'] == data['PCB'].max()]

hour_with_lowest_pcb = min_pcb_row['Hora'].iloc[0]
hour_with_highest_pcb = max_pcb_row['Hora'].iloc[0]

average_price = data['PCB'].mean()

#Visit link for formatting options
#https://core.telegram.org/bots/api#formatting-options

#Emoji list available here: https://symbl.cc/en/emoji/
#Copy and paste Unicode code

intro = "*Fecha*: " + formatted_date + " ("+ days[day].lower() + ") \n"
a = "\U00002705  *La hora más barata es*: " + hour_with_lowest_pcb + " a " + str(round(min_pcb_row['PCB'].iloc[0],3)) + "€\KWh"
b = "\U0000274C  *La hora más cara es*: " + hour_with_highest_pcb + " a " + str(round(max_pcb_row['PCB'].iloc[0],3)) + "€\KWh"
c = "       *El precio medio del día es*: " + str(round(average_price,3)) + "€\KWh"

lines = [intro, a, b, c]
text = '\n'.join(lines)

message_list = [text]


for i in message_list:
    message = i
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={group_id}&parse_mode=Markdown&text={message}"
    requests.get(url).json() # this sends the message
    print("mensajes enviados")
    

    
data.columns = ['Día', 'Hora', '€/KWh']

    
table_string = tabulate(data, headers='keys', tablefmt='grid')
send_message_to_telegram("```\n" + table_string + "\n```")  # Surrounding with ``` for code block formatting in Markdown.
print("tabla enviada")
