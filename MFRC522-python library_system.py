#! /usr/bin/env python
# -*- coding: utf-8 -*-
# python2.7

import RPi.GPIO as GPIO
import MFRC522
import signal
import mysql.connector
import time
import socket
import threading

continue_reading = False
iloop = True
x_id = None
count1 = 0
count2 = 0
countcp = 0
loop  = True
list = []
rcvint = 0
oneloop = False
rcvcheck = False

def end_read(signal,frame):
    global continue_reading
    global iloop
    global thread
    print "\nCtrl+C captured, ending read."
    continue_reading = False
    iloop = False
    GPIO.cleanup()

# socket--------------------------------------------------------------------------------------------------------------------------------------------------------------
UDP_IP = "****.****.****.****"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

class prosess (threading.Thread):
    def run(self):
        global rcvint
        while True:
            rcvint,addr = sock.recvfrom(1024) 

t1 = prosess()
t1.setDaemon(True)
t1.start()
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example."
print "Press Ctrl-C to stop."
print "Waiting for command..."

while iloop:

        if rcvint == "1":
            print "Read uid execute."
            oneloop = True
            continue_reading = True
        elif rcvint == "2":
            print "Read bid execute."
            rcvcheck = True
            continue_reading = True
        else:
            continue_reading = False

        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while continue_reading:

            if rcvcheck == True:
                if rcvint == "3":
                    continue_reading = False
                    rcvint = 0
                    count1 = 0
                    count2 = 0
                    countcp = 0
                    list = []
                    rcvcheck = False
                    print "Ending read."
                    print "Waiting for command..."
                    break

            # Scan for cards    
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    
            # Get the UID of the card
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                x_id = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
                countcp = count2
                loop = True
                while count2 != 0:
                    if x_id == list[count2 - 1]:
                        loop = False
                        count2 = count2 - 1
                    else:
                        count2 = count2 - 1
                else:
                    count2 = countcp

                    if loop:

                        # If we have the UID, continue
                        if status == MIFAREReader.MI_OK:

                            #if a card is found
                            print "Card detected."

                            # Print UID
                            print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
                            list.insert(count1 + 1,x_id)
                            count1 = count1 + 1
                            count2 = count1

                            # This is the default key for authentication
                            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
                            # Select the scanned tag
                            MIFAREReader.MFRC522_SelectTag(uid)

                            # Authenticate
                            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

                            # Check if authenticated
                            if status == MIFAREReader.MI_OK:
                                MIFAREReader.MFRC522_Read(8)
                                MIFAREReader.MFRC522_StopCrypto1()
                            else:
                                print "Authentication error."

                            if __name__ == '__main__':

                                # driverimport
                                con = mysql.connector.connect(host='****.****.****.****', user='****', password='****', database='****', charset='utf8', buffered=True)
                                cur = con.cursor()

                                # insert
                                cur.execute('insert into nowloading (x_id) values (%s)',(x_id,))

                                con.commit()
                                # quit
                                cur.close()
                                con.close()

                                # beep sound
                                GPIO.setmode(GPIO.BOARD)
                                GPIO.setup(10, GPIO.OUT)
                                GPIO.output(10, True)
                                time.sleep(0.1)
                                GPIO.output(10, False)

                            if oneloop == True:
                                continue_reading = False
                                oneloop = False
                                rcvint = 0
                                count1 = 0
                                count2 = 0
                                countcp = 0
                                list = []
                                print "Ending read."
                                print "Waiting for command..."
                            else:
                                print "Waiting for next book..."


