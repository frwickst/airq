#-*- coding:utf-8 -*-

"""
Copyright (C) 2013 - Frank Wickström <frwickst@gmail.com>
Distributed under the BSD license, see LICENSE.txt

airq.py is a web scraper for http://www.ilmanlaatu.fi/

Requirements:
* Mechanize
* PyQuery

Usage:

a = AirQ(rs="430", ss="186") # Turku = 430, Turun kauppatori = 186
sensors = a.getSensors() # Get sensors
values = a.getSensorValues() # Get sensor values
print values # Prints the values

for sensor in sensors: # For all sensors 
	print sensor, ' : ' ,values[sensor]['current'] # Print the sensor and its current value

""" 

import mechanize
from pyquery import PyQuery as PQ

import logging
import time
import datetime

DEBUG = True

if DEBUG:
	logging.basicConfig(level=logging.INFO)
else:
	logging.basicConfig(level=None)
logger = logging.getLogger("AirQ")

def datetimeInGMT2():
	t = time.time()
	
	if time.localtime(t).tm_isdst and time.daylight:
		offset = time.altzone
	else:
		offset = time.timezone
		
	return datetime.datetime.fromtimestamp(t+(7200+offset))

class AirQ():
	def __init__(self, **kwargs):
		logger.info("Initializing AirQ")
		self.br = mechanize.Browser() # Browser
		self.br.set_handle_robots(False)

		# Get these values from the URL of the station you want to monitor
		self.networkID = kwargs.get('as', 'Suomi')
		self.cityID = kwargs.get('rs', False)
		self.stationID = kwargs.get('ss', False)
		
		self.sensors = False
		self.sensorValues = False
					
		logger.info("AirQ initializes")
		
	def getSensors(self):
		logger.info("Getting sensors")

		if self.cityID and self.stationID:
			url = "http://www.ilmanlaatu.fi//ilmanyt/nyt/ilmanyt.php?as="+self.networkID+"&rs="+self.cityID+"&ss="+self.stationID
			self.br.open(url)
			response = self.br.response()
			
			q = PQ(response.read())
			self.sensors = [PQ(option).val() for option in q('#parametrilista option')]

			return self.sensors
		else:
			logger.error("No city or station set")
			return False
	
	def getSensorValues(self, sensors = False):
		logger.info("Getting sensors values")
		
		if self.sensors and not sensors:
			sensors = self.sensors
		
		if sensors:
			now = datetimeInGMT2()
			hour = str(now.hour-1)
			pv = now.strftime("%Y%m%d"+hour+"00")
			results = {}
			
			for sensor in sensors:
				logger.info("Getting info from sensor: "+sensor)
				results[sensor] = {}
				url = "http://www.ilmanlaatu.fi/toiminnallisuus/kartta_alku.php?network="+self.networkID+"&pickedStation="+self.stationID+"&imageMapId="+self.cityID+"&param="+sensor+"&time="+pv

				self.br.open(url)
				response = self.br.response()
				
				if sensor == "stationindex":
					q = PQ(response.read())

					results[sensor]['current'] = q('area').attr('onmouseover')
					if results[sensor]['current']:
							results[sensor]['current'] = results[sensor]['current'].split(',')[-1].strip("');")
					else:
							results[sensor]['current'] = None

					
				else:
					results[sensor]['hours'] = {}
					url = "http://www.ilmanlaatu.fi/php/table/observationsInTable.php?step=3600&today=1&timesequence=23&time="+now.strftime("%Y%m%d%H")+"&station="+self.stationID
					self.br.open(url)
					response = self.br.response()
					
					q = PQ(response.read())
					hours = q('table:first tr')[1:] # First entry is the header
					
					if hours:
						for tr in hours:
							results[sensor]['hours'][PQ(tr[0]).text()] = PQ(tr[1]).text()
		
						if not PQ(hours[-1][1]).text():
							logger.info("No value for the current hour yet, getting last value")
							for i in range (1,now.hour):
								if PQ(hours[-1-i][1]).text():
									current = PQ(hours[-1-i][1]).text()
									break
						else:
							current = PQ(hours[-1][1]).text()
							
						results[sensor]['current'] = current
					else:
						results[sensor]['current'] = None
						logger.info("Can't get values! Day has probably change, and the list is empty.")
						
			self.sensorValues = results
			return results
			
		else:
			logger.error("No sensors at the current location")
			return False
