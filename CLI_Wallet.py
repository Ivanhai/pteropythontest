#!/usr/bin/env python3
import socket, configparser, getpass, os, platform, sys, time, json, datetime
from signal import signal, SIGINT
from pathlib import Path

try: # Check if requests is installed
	import requests
except:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Requests не установлен. Кошелек попробует его установить. Команда для ручной установки: python3 -m pip install requests.")
	os.system("pip3 install requests")
try: # Check if colorama is installed
	from colorama import init, Fore, Back, Style
except:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Requests не установлен. Кошелек попробует его установить. Команда для ручной установки: python3 -m pip install requests.")
	os.system("pip3 install colorama")
try: # Check if replitdb is installed
	import replitdb
except:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "replitdb не установлен. Кошелек попробует его установить. Команда для ручной установки: python3 -m pip install replitdb.")
	os.system("pip3 install replitdb")

timeout = 5 # Socket timeout
VER = 1.7
res = "https://mhcoin.s3.filebase.com/Server.txt" # Serverip file
config = configparser.ConfigParser()
pcusername = getpass.getuser() # Username
platform = str(platform.system()) + " " + str(platform.release()) # Platform information
s = socket.socket()

def title(title):
	if os.name == 'nt':
		os.system("title "+title)
	else:
		print('\33]0;'+title+'\a', end='')
		sys.stdout.flush()

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
	print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "See you soon!")
	try:
		s.send(bytes("CLOSE", encoding="utf8"))
	except:
		pass
	os._exit(0)
signal(SIGINT, handler) # Enable signal handler

while True: # Grab data grom GitHub section
	try:
		res = requests.get(res, data = None) #Use request to grab data from raw github file
		if res.status_code == 200: #Check for response
			content = res.content.decode().splitlines() #Read content and split into lines
			pool_address = content[0] #Line 1 = pool address
			pool_port = content[1] #Line 2 = pool port
			try: # Try to connect
				s.connect((str(pool_address), int(pool_port)))
				s.settimeout(timeout)
				SERVER_VER = s.recv(3).decode()

				jsonapi = requests.get("http://mhcoin.duckdns.org/api.json", data = None) # Use request to grab data from raw github file
				if jsonapi.status_code == 200: # Check for reponse
					content = jsonapi.content.decode() # Read content and split into lines
					contentjson = json.loads(content)
					ducofiat = float(contentjson["Duco price"])
				else:
					ducofiat = 0.0025 # If json api request fails, wallet will use this value
				break # If connection was established, continue
    
			except: # If it wasn't, display a message
				print(Style.RESET_ALL + Fore.RED + "Не удалось подключится к серверу.\nПовторная попытка через 15 секунд.")
				time.sleep(15)
				os.execl(sys.executable, sys.executable, *sys.argv)
		else:
			print("Retrying connection...")
			time.sleep(0.025) # Restart if wrong status code
    
	except:
		print(Style.RESET_ALL + Fore.RED + " Не удалось получить IP Сервера.\nЗакрытие кошелька через 15 секунд.")
		time.sleep(15)
		os._exit(1)

while True:
	title("MHCoin CLI Wallet")
	if not Path("CLIWallet_config.cfg").is_file(): # Initial configuration section
		print("Первый запуск кошелька MHCoin\n")
		print("Выбери опцию: ")

		choice = input("  1 - Войти\n  2 - Создать аккаунт\n  3 - Выйди\n")
		if int(choice) <= 1:
			client = replitdb.Client()
			username = client.view("username")
			password = client.view("password")

			s.send(bytes("LOGI," + str(username) + "," + str(password), encoding="utf8"))
			loginFeedback = s.recv(64).decode().split(",")
			if loginFeedback[0] == "OK":
				print(Style.RESET_ALL + Fore.YELLOW + "Удачный вход.")

				config['wallet'] = {"username": username, "password": password}
	
				with open("CLIWallet_config.cfg", "w") as configfile: # Write data to file
					config.write(configfile)
			else:
				print(Style.RESET_ALL + Fore.RED + "Не удалось войти, причина: " + Style.BRIGHT + str(loginFeedback[1]))
				time.sleep(15)
				os._exit(1)

		if int(choice) == 2:
			username = input(Style.RESET_ALL + Fore.YELLOW + "Введи username: " + Style.BRIGHT)
			password = input(Style.RESET_ALL + Fore.YELLOW + "Введи пароль: " + Style.BRIGHT)
			pconfirm = input(Style.RESET_ALL + Fore.YELLOW + "Подтверди пароль: " + Style.BRIGHT)
			email = input(Style.RESET_ALL + Fore.YELLOW + "Введи свой email: " + Style.BRIGHT)
			if password == pconfirm:
				while True:
					s.send(bytes("REGI," + str(username) + "," + str(password) + "," + str(email), encoding="utf8"))
					regiFeedback = s.recv(256).decode().split(",")

					if regiFeedback[0] == "OK":
						print(Style.RESET_ALL + Fore.YELLOW + Style.BRIGHT + "Успешно создал новый аккаунт.")
						break
					elif regiFeedback[0] == "NO":
						print(Style.RESET_ALL + Fore.RED + 
							"\nНе удалось создать аккаунт, причина: " + Style.BRIGHT + str(regiFeedback[1]))
						time.sleep(15)
						os._exit(1)

		if int(choice) >= 3:
			os._exit(0)

	else: # If config already exists, load from it
		while True:
			config.read("CLIWallet_config.cfg")
			username = config["wallet"]["username"]
			password = config["wallet"]["password"]

			s.send(bytes("LOGI," + str(username) + "," + str(password), encoding="utf8"))
			loginFeedback = s.recv(128).decode().split(",")
			if loginFeedback[0] == "OK":
				os.remove("CLIWallet_config.cfg")
				break
			else:
				print(Style.RESET_ALL + Fore.RED + "Не удалось войти, причина: " + Style.BRIGHT + str(loginFeedback[1]))
				time.sleep(15)
				os._exit(1)

		while True:
			while True:
				s.send(bytes("BALA", encoding="utf8"))
				try:
					balance = round(float(s.recv(256).decode()), 8)
					balanceusd = round(float(balance) * float(ducofiat), 6)
					break
				except:
					pass
			print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "\nMHCoin CLI Wallet")
			print(Style.RESET_ALL + Fore.YELLOW + "Твой баланс: " + Style.BRIGHT + str(balance) + " MHCoin")
			print(Style.RESET_ALL + Fore.YELLOW + "Напиши `help`, чтоб узнать все доступные команды")
			command = input(Style.RESET_ALL + Fore.WHITE + "MHCoin CLI $ " + Style.BRIGHT)
			if command == "refresh":
				continue

			elif command == "send":
				recipient = input(Style.RESET_ALL + Fore.WHITE + "Введи получателей' username: " + Style.BRIGHT)
				amount = input(Style.RESET_ALL + Fore.WHITE + "Введи сумму для перевода: " + Style.BRIGHT)
				s.send(bytes("SEND,deprecated,"+str(recipient)+","+str(amount), encoding="utf8"))
				while True:
					message = s.recv(1024).decode()
					print(Style.RESET_ALL + Fore.BLUE + "Ответ сервера: " + Style.BRIGHT + str(message))
					break

			elif command == "changepass":
				oldpassword = input(Style.RESET_ALL + Fore.WHITE + "Введи твой пароль: " + Style.BRIGHT)
				newpassword = input(Style.RESET_ALL + Fore.WHITE + "Введи новый пароль: " + Style.BRIGHT)
				s.send(bytes("CHGP,"+  str(oldpassword) + "," + str(newpassword), encoding="utf8"))
				while True:
					message = s.recv(1024).decode()
					print(Style.RESET_ALL + Fore.BLUE + "Ответ сервера: " + Style.BRIGHT + str(message))
					break

			elif command == "exit":
				print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "\nВыхожу из кошелька.")
				try:
					s.send(bytes("CLOSE", encoding="utf8"))
				except:
					pass
				os._exit(0)

			elif command == "userinfo":
				s.send(bytes("STAT", encoding="utf8"))
				while True:
					message = s.recv(1024).decode()
					break
				print(Style.RESET_ALL + Fore.BLUE + "Server message: " + Style.BRIGHT + str(message))

			elif command == "about":
				print(Style.RESET_ALL + Fore.WHITE + "MHCoin CLI Кошелек создан с любовью сообществом Duino-Coin, а я воспользовался открытым кодом :D")
				print(Style.RESET_ALL + Fore.WHITE + "Версия: "+str(VER))
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "https://t.me/joinchat/S1TCw6SLQjn_8Enf")

			elif command == "logout":
				os.remove("CLIWallet_config.cfg")
				os.execl(sys.executable, sys.executable, *sys.argv)

			else:
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "Доступные команды:")
				print(Style.RESET_ALL + Fore.WHITE + " help - Показывает данное сообщение")
				print(Style.RESET_ALL + Fore.WHITE + " refresh - Обновить баланс")
				print(Style.RESET_ALL + Fore.WHITE + " send - Отправить MHCoin другому пользователю")
				print(Style.RESET_ALL + Fore.WHITE + " userinfo - Выдает информацию о аккаунте")
				print(Style.RESET_ALL + Fore.WHITE + " changepass - Сменить пароль")
				print(Style.RESET_ALL + Fore.WHITE + " exit - Выходит из кошелька MHCoin")
				print(Style.RESET_ALL + Fore.WHITE + " about - Показывает информацию о MHCoin Wallet")
				print(Style.RESET_ALL + Fore.WHITE + " logout - Выходит из данного аккаунта")
