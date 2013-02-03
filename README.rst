airq: a web scraper for http://www.ilmanlaatu.fi/
=========================================


Quickstart
==========

	>>> from airq import AirQ
	>>> a = AirQ(rs="430", ss="186") # Turku = 430, Turun kauppatori = 186
	>>> sensors = a.getSensors() # Get sensors
	>>> values = a.getSensorValues() # Get sensor values
	>>> print values # Prints the values

	>>> for sensor in sensors: # For all sensors 
	>>> 	print sensor, ' : ' ,values[sensor]['current'] # Print the sensor and its current value


