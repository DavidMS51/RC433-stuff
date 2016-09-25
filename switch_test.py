import pi_switch
from time import sleep
address_group = 2 # Address group (1..4)
channel = 4 # Channel (1..4)

switch = pi_switch.RCSwitchB(address_group, channel)
switch.enableTransmit(0) # use WiringPi pin 0 <=> GPIO17

while True:
	switch.switchOn()
	sleep(2)
	switch.switchOff()
	sleep(2)
