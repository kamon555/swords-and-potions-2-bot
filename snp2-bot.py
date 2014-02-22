import glob
import os
import random
import signal
import sys
import time

def signal_handler(signum, frame):
	print "Now exiting..."
	exit()

signal.signal(signal.SIGINT, signal_handler)

# Environment setup
os.chdir(os.path.dirname(__file__))
sys.path.append(r"C:\automa\library.zip")
from automa.api import *

Config.wait_interval_secs = 0.1 

# Figure out which window to use
switch_to('Edgebee')

# Global definitions go here
employees = glob.glob("employees/*.png")

# Array of things that should always be clicked
alwaysClick = [
	"buttons/closebtn.png", 
	"buttons/closecomponentmissing.png", 
	"buttons/closeitemselect.png", 
	"buttons/closeitembroken.png",
	"buttons/ok.png", 
	"buttons/next.png", 
	"buttons/start.png"
]

customers = glob.glob("customers/*.png")
suggest = "customer-interactions/suggest.png"
customerInteractions = [
	"customer-interactions/buy.png",
	"customer-interactions/sell.png",
	"customer-interactions/thanks.png",
	suggest,
	"customer-interactions/refuse.png",
	"customer-interactions/sorry.png"
]

sleep_for = [
	"buttons/start.png",
	"buttons/next.png",
	"buttons/done.png"
]

# Returns whether the given image was clicked 
def clickImage(img, similarity = 0.7):
	
	# Determine if we're going to sleep after click
	sleepy = 0
	if img in sleep_for:
		sleepy = 1.5
	
	# Convert to an image
	if not isinstance(img, Image):
		img = Image(img, similarity)
		
	# Search for the image
	found = img.exists()
	print "checking " + str(img)
	if found:
		print "found image " + str(img)
		try:
			click(img)
			
			# Handle customer suggestions
			if img == Image(suggest, similarity):
				suggestSomething()
			
			if sleepy:
				time.sleep(sleepy)
		except Exception as e:
			print e
			print "couldn't click it"
			found = False
	return found

# Attempts to interact with an employee
def employeeInteraction():
	
	# Checks whether an item was built
	def wasBuilt():
		return not (clickImage("buttons/ok.png") or clickImage("buttons/closecomponentmissing.png"))
	
	# Check for employees
	found = False
	for img in employees:
		if clickImage(img):
			found = True
			# Attempt to build something that we're out of
			outOf = find_all(Image("out-of-stock.png"))
			while len(outOf):
				if clickImage(outOf.pop()) and wasBuilt():
					break
			# Otherwise attempt to build a random item
			lvlTargets = find_all(Image("lvl-target.png"))
			random.shuffle(lvlTargets)
			while len(lvlTargets):
				if clickImage(lvlTargets.pop()) and wasBuilt():
					break
					
	return found

# Attempts to interact with customers
def customerInteraction():
	found = False
	# Search for customer
	for img in customers:
		if clickImage(img):
			if not Image("customer-interactions/check-if-opened.png").exists():
				continue
			found = True
			# Interact with customer
			for img in customerInteractions:
				if clickImage(img, 0.95):
					break
	return found

# Attempts to suggest an item to the customer
def suggestSomething():
	
	# Otherwise attempt to build a random item
	lvlTargets = find_all(Image("lvl-target.png"))
	while len(lvlTargets):
		target = lvlTargets.pop()
		if clickImage(target):
			return

# Main script execution
print "Now starting..."

while True:
	
	# Keep clicking on employees when available
	while employeeInteraction():
		pass
	
	# Keep clicking on customers when available
	while customerInteraction():
		continue # Search for employees again after helping customers
		pass
	
	# Check for other buttons and such only if nothing else matched
	for img in alwaysClick:
		clickImage(img)
	
	while clickImage("buttons/done.png"):
		pass