#
#	PICO TC-08
#	module for windows machines
# 	based on
# 	* https://www.picotech.com/support/topic10247.html
#	* https://github.com/picotech/picosdk-c-sharp-examples/blob/master/usbtc08/USBTC08Imports.cs
#	* https://github.com/picotech/picosdk-c-sharp-examples/blob/master/usbtc08/USBTC08CSConsole/USBTC08CSConsole.cs
#	* https://www.picotech.com/download/manuals/usb-tc08-thermocouple-data-logger-programmers-guide.pdf
# 
#	


import ctypes
import time


class usb_tc08():
	def __init__(self):
		try:
			self.USBTC08_MAX_CHANNELS = 9 # channel 0 is the cold/internal channel and 1-8 are the other channels => 9 total
			self.USBTC08_UNITS_CENTIGRADE = 0 # because not all 0s are equal	

			self._dll = ctypes.WinDLL("usbtc08")
			
			self._handle = self._dll.usb_tc08_open_unit()
			if self._handle == 0:
				raise Exception("Unable to open device!")

			self._dll.usb_tc08_set_mains(self._handle, 0) # 50Hz mains noise rejection
			for channel in range(self.USBTC08_MAX_CHANNELS): # set all channels up as type K theromocouple. Disable using "DisableChannel" routine
				if channel == 0:
					self._dll.usb_tc08_set_channel(self._handle, channel, ord('K')) # always enable channel 0
				else:
					self._dll.usb_tc08_set_channel(self._handle, channel, ord(' '))
				# print("channeel {} is now enabled".format(channel))

		except Exception as e:
			print("Unknown error occured!\n", e)
			raise
	#end __ini__


	def __del__(self):
		# automatically cleans up
		self.StopStreaming()
		self._dll.usb_tc08_close_unit(self._handle)
	#end __del__


	def GetLastError(self):
		ret = self._dll.usb_tc08_get_last_error(self._handle)
		# TODO: translate error codes to human readable ones
		return ret


	def EnableChannels(self, channels):
		# enable channels
		for chan in channels:
			self._dll.usb_tc08_set_channel(self._handle, chan, ord('K'))

	
	def DisableChannels(self, channels):
		# Disabling them reduces read-out time
		for chan in channels:
			if chan != 0:
				self._dll.usb_tc08_set_channel(self._handle, chan, ord(' ')) # disable channels


	def GetSingle(self, channels):				
		try:
			values = (ctypes.c_float * (self.USBTC08_MAX_CHANNELS))()
			self._dll.usb_tc08_get_single(self._handle, ctypes.byref(values), 0, self.USBTC08_UNITS_CENTIGRADE)
			# for i,v in enumerate(values):
			# 	print("values[{}]: = {}".format(i, v))

			ret_values = {}
			for c in channels:
				# ret_values.append([c, values[c]])
				ret_values[c] = values[c]
			return ret_values

		except Exception as e:
			print("Error: ", e)
	#end Get Single


	def StartStreaming(self, sample_rate):
		min_interval = self._dll.usb_tc08_get_minimum_interval_ms(self._handle)
		if min_interval > sample_rate:
			sample_rate = min_interval
		
		self._dll.usb_tc08_run(sample_rate)
		return sample_rate
	#end Start Streaming


	def StopStreaming(self):
		self._dll.usb_tc08_stop(self._handle)
	#end Stop Streaming

	def GetStreamingData(self):
		# TODO: implement
		# not implemented; GetSingle is sufficient for now (not a lot of difference in Streaming time)
		pass



# ______________________________

if __name__ == "__main__":
	print("Hello world?!")

	picolog = usb_tc08()
	# picolog.DisableChannels(range(1, 6)) # disable 6-8
	picolog.EnableChannels(range(1, 6))
	
	tick = time.perf_counter()
	values = picolog.GetSingle([1, 2, 3, 6, 7]) # read channels 1-5
	tock = time.perf_counter() - tick
	print("Done in {:.3f} seconds".format(tock)) # for benchmarks
	for chan,val in values.items():
		print("Channelz: {} => Value: {:.2f}°C".format(chan, val))

	interval = picolog.StartStreaming(100e-3) # not fully implemented; sorry
	print("Streaming @ {:.2f} seconds".format(interval))