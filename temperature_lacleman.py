import requests
import telebot
import os
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO
)

locations = {
    "Genève, Bains des Pâquis": "https://www.badi-info.ch/_temp/leman-geneve.htm",
    "Buchillon": "https://www.badi-info.ch/_temp/leman.htm",
    "Évian-les-Bains": "https://www.badi-info.ch/_temp/leman-evian.htm",
    "Montreux": "https://www.badi-info.ch/_temp/leman-montreux.htm",
    "Morges": "https://www.badi-info.ch/_temp/leman-morges.htm",
    "Nyon": "https://www.badi-info.ch/_temp/leman-nyon.htm",
    "Pully": "https://www.badi-info.ch/_temp/leman-pully.htm",
    "Thonon-les-bains": "https://www.badi-info.ch/_temp/leman-thonon.htm",
    "Vevey": "https://www.badi-info.ch/_temp/leman-vevey.htm",
    "Villeneuve Plage": "https://www.badi-info.ch/_temp/leman-villeneuve.htm"
}

# Função para extrair temperatura e data de uma URL
def extract_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
    
    soup = BeautifulSoup(response.content, 'html.parser')
    temperature = soup.find('b', id='t6').text
    data = soup.find('td', class_='td3').find('small').text.split(' ›')[0]
    
    return temperature, data

# Inicializa o bot do Telegram
bot = telebot.TeleBot(os.getenv("bot_key"))

# Handler para o comando '/start' ou '/help'
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Envia uma mensagem de boas-vindas e instruções
    bot.reply_to(message, """\
Bem-vindo ao bot de informações de temperatura do Lago Léman!
Para ver a temperatura atual de uma localização, digite /temperatura ou /t seguido pelo número da localização desejada.
Exemplo: /temperatura 1 para Genève, Bains des Pâquis. Digite /localizacao ou /l para saber ter acesso a listagem de localizações.
Lista de Localizações:
1. Genève, Bains des Pâquis
2. Buchillon
3. Évian-les-Bains
4. Montreux
5. Morges
6. Nyon
7. Pully
8. Thonon-les-bains
9. Vevey
""")

# Handler para o comando '/temperatura'
@bot.message_handler(commands=['temperatura', 't'])
def send_temperature(message):
    try:
        # Extrai o número da localização do comando recebido
        location_index = int(message.text.split()[1])
        
        # Verifica se o índice está dentro dos limites
        if 1 <= location_index <= len(locations):
            # Obtém a localização e URL correspondente
            selected_location = list(locations.keys())[location_index - 1]
            logging.info(f"Usuário {message.from_user.username} verificou a temperatura de {selected_location}")
            selected_url = locations[selected_location]
            
            # Extrai a temperatura e a data
            temperature, data = extract_data(selected_url)
            
            # Envia a resposta com a temperatura e data
            bot.reply_to(message, f"Localização: {selected_location}\n"
                                  f"Temperatura: {temperature}°C\n"
                                  f"Data: {data}")
        else:
            bot.reply_to(message, "Escolha inválida. Por favor, entre um número de 1 a 9 correspondente à localização desejada.")
    except IndexError:
        logging.warning(f"Usuário {message.from_user.username} gerou IndexError")
        bot.reply_to(message, "Por favor, use o comando /temperatura seguido pelo número da localização desejada.")
    except ValueError:
        logging.warning(f"Usuário {message.from_user.username} gerou ValueError")
        bot.reply_to(message, "Por favor, use um número válido após o comando /temperatura.")
    except Exception as err:
        logging.error(f"Usuário {message.from_user.username} gerou Exception: {str(err)}")
        bot.reply_to(message, "erro técnico, por favor tente mais tarde.")

# Handler para o comando '/localizacao'
@bot.message_handler(commands=['localizacao', 'l'])
def send_local(message):
    logging.info(f"Usuário {message.from_user.username} verificou a localização")
    bot.reply_to(message, """\
Aqui está a listagem de localizações. Para ver a temperatura atual de uma localização, digite /temperatura seguido pelo número da localização desejada.
1. Genève, Bains des Pâquis
2. Buchillon
3. Évian-les-Bains
4. Montreux
5. Morges
6. Nyon
7. Pully
8. Thonon-les-bains
9. Vevey
""")


# Inicia o bot
if __name__ == "__main__":
    logging.info("Inicializando BOT")
    bot.polling()