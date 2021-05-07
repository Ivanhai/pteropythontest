#!/usr/bin/env python3
import socket, hashlib, urllib.request
soc = socket.socket()

username = "httsmvkcom" 
UseLowerDiff = False # Set it to True to mine with lower difficulty

serverip = "https://mhcoin.s3.filebase.com/Pool.txt" # Serverip file
with urllib.request.urlopen(serverip) as content:
    content = content.read().decode().splitlines() #Read content and split into lines
pool_address = content[0] #Line 1 = pool address
pool_port = content[1] #Line 2 = pool port

# This section connects and logs user to the server
soc.connect((str(pool_address), int(pool_port))) # Connect to the server
server_version = soc.recv(3).decode() # Get server version
print("Версия сервера:", server_version)

# Mining section
while True:
    if UseLowerDiff:
        soc.send(bytes("JOB,"+str(username)+",MEDIUM", encoding="utf8")) # Send job request
    else:
        soc.send(bytes("JOB,"+str(username), encoding="utf8")) # Send job request
    job = soc.recv(1024).decode() # Get work from pool
    job = job.split(",") # Split received data to job (job and difficulty)
    difficulty = job[2]

    for result in range(100 * int(difficulty) + 1): # Calculate hash with difficulty
        ducos1 = hashlib.sha1(str(job[0] + str(result)).encode("utf-8")).hexdigest() # Generate hash
        if job[1] == ducos1: # If result is even with job
            soc.send(bytes(str(result)+",,Lite Miner", encoding="utf8")) # Send result of hashing algorithm to pool
            feedback = soc.recv(1024).decode() # Get feedback about the result
            if feedback == "GOOD": # If result was good
                print("[Accepted!] Решение:", result, "Сложность:", difficulty)
                break
            elif feedback == "BAD": # If result was bad
                print("[Rejected!!!] Решение:", result, "Сложность:", difficulty)
                break