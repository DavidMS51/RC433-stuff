# David Saul 2016 433 status new timeclock 2016
#
# display element of s/w is based on 2014 Adafruit Industries code Author: Tony DiCola
# Switch elements of code and 433 drivers by lexruee  - github.com/lexruee/pi-switch-python

#code assume 	- RC433 transmitter is connnector to GPIO17 pin
#		- I2C display connect to default IC2 channel [ GPIO 2 and 3 ] pins

from subprocess import Popen, PIPE	# for sunrise / set code

import time
from time import sleep

import datetime                 # for real time
from datetime import datetime   # for real time numbers

import pi_switch		# for 433 switch code

import Adafruit_GPIO.SPI as SPI	# for display code
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import socket			# for ip display
import fcntl
import struct

import random

#functions

def create_switch(addr, channel):	#creates a switch of type B
  switch = pi_switch.RCSwitchB(addr, channel)
  switch.enableTransmit(0) # use WiringPi pin 0 <=> GPIO17
  return switch


def toggle(switch):	#toggles a switch on and off
  switch.switchOn()
  time.sleep(1)
  switch.switchOff()
  time.sleep(1)

def get_sun_rise_set():	#return todays sunrise / set times as hh:mm
	p = Popen(['/usr/local/bin/sunwait','-p','51.72N','.6502W'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        output = p.stdout.read()
#        print output
        stpos =  output.find("rises")
#        print stpos
        rise = output[stpos+6:stpos+8]+':'+output[stpos+8:stpos+11]
        set  = output[stpos+21:stpos+23]+':'+output[stpos+23:stpos+25]
#	print
#        print 'rises = ',rise
#        print 'sets = ',set
#	print

	return rise,set

def day_len():		# calc minutes between 00:00 and sunset
	rt,st = get_sun_rise_set()		#convert set times to integers
	rise_hr = int(st[0:2])
	rise_mi = int(st[3:5])
	rise_tot = (rise_hr*60)+rise_mi	#calc minutes between 00:00 and sunset
#        print 'set_tot = ',rise_tot	

	return rise_tot

def rise_len():          # calc minutes between 00:00 and sunrise
        rt,st = get_sun_rise_set()              #convert set times to integers
        rise_hr = int(rt[0:2])
        rise_mi = int(rt[3:5])
        rise_tot = (rise_hr*60)+rise_mi #calc minutes between 00:00 and sunrise
#        print 'rise_tot = ',rise_tot   

        return rise_tot

def disp_wel():			#display welcome message
	draw.text((0,0),'Time Switch',  font=font20, fill=255)
	draw.text((0,20),'Rev 1',  font=font20, fill=255)	
	disp.image(image)
        disp.display()
 
	return

def get_ip_address(ifname):	#get ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def disp_IP(time):		#get and display IP of RPI for time
	try:
		IP = get_ip_address('eth0')
	except:
		IP = 'xxx.xxx.xxx.xxx'
	print
	print 'Current IP is', IP
	print
	draw.text((0,45),IP,  font=font15, fill=255)
	disp.image(image)
        disp.display()	
	sleep(time)		#wait for time and then clear
	disp.clear()
	disp.display()
	return

def disp_date():		#update date display
				# this will clear the date area of the display [only]
	day = str(datetime.now().strftime('%-d'))	#sort out date format string to ddd,no,mmm
	date = datetime.now().strftime('%a ') + day + datetime.now().strftime(' %b')
	draw.rectangle((77,0,77,15),fill = 0)		#clear the date display area only
	draw.text((75,0),date,  font=font10, fill=255)   #display it
	disp.image(image)
        disp.display()

	return

def disp_sunrise_set():		#update sunrise / set dispay
				# note this does not clear the display first

	rise,set = get_sun_rise_set()
	draw.text((0, 24),'Sunrise / set = '+rise+' / '+set,  font=font10, fill=255)
	disp.image(image)
	disp.display()	

	print 'sunrise today = ', rise
	print 'sunset today = ', set
	print
	return

def clear_disp():			# Clear complete display buffer.
					# does not re-display
	draw.rectangle((0,0,128,64),fill = 0)
#	disp.image(image)
#	disp.display()

def status(text):
	draw.rectangle((0,45,128,64),fill = 0)
	draw.text((0,45),text,  font=font15, fill=255)   #display it
       	disp.image(image)
       	disp.display()

# Setup and wellcome
print
print
print 'Setting up please wait ....'

# Display setup code setup to work with 128*64 I2C display

# Raspberry Pi pin configuration:
RST = 24        # this is not actually used with with 4 pin displays but the setup needs is to work
                # make sure this line is not being used by anything else !

# define correct display type [128x64 display with hardware I2C]
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

disp.set_contrast(0)    # set display to min brightness

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Set up range of font sizes from standard Pi setup fonts
font20 = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Thin.ttf', 20)
font15 = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Thin.ttf', 15)
font10= ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Thin.ttf',10)

# define switch codes for RC switches
ad = [[4,4],[4,3],[4,2],[3,1],[2,4]]
switches = [ad[0],ad[1],ad[2],ad[3],ad[4]]
switches = [ create_switch(p,q) for (p,q) in switches ]

#defing verbose title
title = ['bedroom 1','Landing','Living Room', 'Hall', 'Bedroom 2']

# define timer data

# on data - sunset + x minutes - as integer
on_data = [-30,1,-60,10,120]
on_data_today = [0,0,0,0,0]   # daily on with todays random elements

# off data - off time  HH:MM as a string
off_data_text = ['02:00','02:20','01:30','sunrise','00:30']
off_data = [0,0,0,0,0]	# minutes from midnight equivelent 		
off_data_today = [0,0,0,0,0]  # daily offs with todays random elements

# creat off_data
print 'Off data calculated as   (9999 = sunrise)'
for i in range (0,len(off_data_text)):
	if off_data_text[i] == 'sunrise':
		off_data[i] = 9999 
	else:
		off_data[i] = (60*(int(off_data_text[i][0:2]))+(int(off_data_text[i][3:6])))

	print '     ', title[i] , off_data[i]

# rand - variation time element in minutes - as integer
rand_time = [30,30,30,30,30]	# rand element is +/- this number
rand_time_today = [0,0,0,0,0]	# daily working random elements

#setup clock variables
timetm = datetime.now().strftime('%H:%M:%S')
time = timetm
top = 0 

# show welcome display and IP address for a couple of seconds
disp_wel()
disp_IP(4)

#clear the display
clear_disp()

# flag first run to setup initial variables 
first_run = True


while True:
	while time == timetm:		# make sure loop only executes once a second
                time = datetime.now().strftime('%H:%M:%S')
                sleep(.25)

	# daily updates  [ and used for initial setup ] 
	if time == "00:00:01" or first_run == True:
		print
		print '---------------------------------------------'
		print "New day maker for ",
		print  datetime.now().strftime('%d %B %Y')
		print
		# get new day light lengths
		set_tot = day_len()
		rise_tot = rise_len()	
		#clear the display and update date and rise / set times
		clear_disp()
		disp_sunrise_set()
		disp_date()

		print 'Daylight length for today = ',set_tot,'minutes'
		print 'Time to sunrise for today = ',rise_tot,'minutes'
		print
		print 'Updating random on time elements'
		for i in range (0,len(on_data)):
			ran_temp = (random.randint((-1*rand_time[i]),rand_time[i]))	# calc random element
			on_data_today[i] = on_data[i]+set_tot + ran_temp	# add random element to sunset time and offset
			print '     ',title[i],'time delta today =', ran_temp,'('+str(on_data_today[i])+')' # display it
		print
                print 'Updating random off time elements'
                for i in range (0,len(off_data)):
			ran_temp = (random.randint((-1*rand_time[i]),rand_time[i]))	#calc random element
			if off_data[i] == 9999:		# check for special sunrise off case
				off_data_today[i] = rise_tot + ran_temp	 # add random element to sunrise time
			else:
        	                off_data_today[i] = off_data[i] + ran_temp	# add random element to off time
                        print '     ',title[i],'time delta today =', ran_temp,'('+str(off_data_today[i])+')'	# display it
                print

		


        # Sort out and update of time display
        timex = timetm
        timetm = time
        # clear time bit of display
        draw.text((0, top), timex, font=font20, fill=0)
        # redraw time
        draw.text((0, top), time, font=font20, fill=255)
        # update diplay buffer
        disp.image(image)
        disp.display()

	# calc current time in minutes
        min_tot = (60*int(datetime.now().strftime('%H')))+int(datetime.now().strftime('%M'))


#	Start-up Power control logic- this only runs at start-up
#	this is to provide a immediate status catch up following a power cut
#	Yes I know it is quick and dirtly, will tidy up one day
#	It assumes lights all go on before midnight and off after middnight [ but before midday ] 
#	This is not a bullet proof as the regular routine - it only makes 2 attemps to turn on / off 

	if first_run == True:
		first_run = False	# make certain first run flag cleared
		if min_tot > 720:	# Check to see if time is after 12 [ midday ] - check of missed on's
			print 'running start-up check if any controller should be on'
			for i in range (0,len(switches)):               # set for max no of channels
	                        if min_tot > on_data_today[i]:
        	                        print switches[i],'  '+title[i],' On at ', datetime.now().strftime('%H:%M')
                	                status(title[i]+' ON')
                        	        switches[i].switchOn()  # turn on channel
                                	sleep(.4)
	                                switches[i].switchOn()  # have another go for luck
		else:		#assume it is morning check for missed offs
			for i in range (0,len(switches)):               # set for max no of channels
                        	if min_tot > off_data_today[i]:
                                	print switches[i],'  '+title[i],' Off at ', datetime.now().strftime('%H:%M')
	                                status(title[i]+' OFF')
        	                        switches[i].switchOff()  # turn off channel
                	                sleep(.4)
                        	        switches[i].switchOff()  # have another go for luck



#	General Power control logic  - this runs each day

#	print 'min_tot = ',min_tot
#	print datetime.now().strftime('%S')
	if datetime.now().strftime('%S') == '10':	#check for new minute, if yes run check
#		print				#debug only
#		min_tot=input('min_tot test ')	#debug only
#		print				#debug only

		# check for on's
		for i in range (0,len(switches)):		# set for max no of channels
			#check time is within 5 minutes of on time, if so ex turn on command
			if min_tot > on_data_today[i] and min_tot < (on_data_today[i]+6):
				print switches[i],'  '+title[i],' On at ', datetime.now().strftime('%H:%M')
				status(title[i]+' ON')
				switches[i].switchOn()	# turn on channel
				sleep(.4)
				switches[i].switchOn()	# have another go for luck

		# check for off's
		for i in range (0,len(switches)):               # set for max no of channels
                        #check off time is within 5 minutes of on time, if so ex turn off command
                        if min_tot > off_data_today[i] and min_tot < (off_data_today[i]+6):
                                print switches[i],'  '+title[i],' Off at ', datetime.now().strftime('%H:%M')
				status(title[i]+' OFF')
                                switches[i].switchOff()  # turn off channel
                                sleep(.4)
                                switches[i].switchOff()  # have another go for luck





#dummy switch control for testing and demo
	
#	sec = int(datetime.now().strftime('%S'))

#  for switch in switches:
#    toggle(switch)

#	if sec == 1 or sec == 30:
#		switches[1].switchOn()
#		status('Hall on')

#	if sec == 10 or sec == 40:
#		switches[1].switchOff()
#		status('Hall off')


#	if sec == 15 or sec == 45:
#        	switches[0].switchOn()
#		status('Bedroom on')

#        if sec == 25 or sec == 55:
#        	switches[0].switchOff()
#		status('Bedroom  off')


