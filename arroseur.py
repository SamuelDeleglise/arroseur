import RPi.GPIO as g
import time
from functools import partial
import time
from threading import Timer
import json
import os.path as osp

PATH = osp.dirname(__file__)
TIME = 0.003
def measure(out_pin, in_pin, n_av=100):
	g.setmode(g.BCM)
	g.setup(out_pin, g.OUT)
	g.setup(in_pin, g.IN)
	total = 0
	for i in range(n_av):
		tic = time.time()
		g.output(out_pin, 1)
		g.wait_for_edge(in_pin, g.RISING, timeout=1000)
		total+=time.time() - tic
		time.sleep(TIME)
		tic = time.time()
		g.output(out_pin, 0)
		g.wait_for_edge(in_pin, g.FALLING, timeout=1000)
		total+=time.time()- tic
		time.sleep(TIME)
	return total*1./(2*n_av)


class Arroseur(object):
    _channels = [16, 22, 17, 18, 21]
    def __init__(self):
        self.n_channels = len(self._channels)
        self.timer = [None]*self.n_channels
        self.on_time = [0]*self.n_channels
        self.load_on_times()
        self.start_time = [0]*self.n_channels
        self.on_state = [0]*len(self._channels)
        g.cleanup()
        g.setmode(g.BCM)
        for ch in xrange(len(self._channels)):
            g.setup(self._channels[ch], g.OUT)
            self.set_state(ch, 0)
	    
    def load_on_times(self):
        try:
            with open(osp.join(PATH, "on_times.json"), 'r') as f:
                self.on_time = json.loads(f.read())
        except IOError:
            pass
    
    def save_on_times(self):
        with open(osp.join(PATH, "on_times.json"), 'w') as f:
            f.write(json.dumps(self.on_time))

    def set_state(self, index, state):
        self.on_state[index] = state
        g.output(self._channels[index], state)


    def get_state(self, index):
	return self.on_state[index]

    def get_states(self):
        return self.on_state

    def set_on_time(self, index, on_time_s):
       """sets motor index to on for the specified amount of seconds"""
       if self.timer[index] is not None:
           self.timer[index].cancel()
       self.timer[index] = Timer(on_time_s, 
                                partial(self.set_state, 
                                        index=index,
                                        state=0))
       self.timer[index].start()
       self.set_state(index, 1)
       self.start_time[index] = time.time()
       self.on_time[index] = on_time_s
       self.save_on_times()

    def get_remaining_time(self, index):
        """Returns on_time if motor is off, otherwise, 
        returns the remaining on_time"""
        if self.on_state[index]:
            return int(self.on_time[index] - (time.time() - \
                                     self.start_time[index]))
        else:
            return int(self.on_time[index])

    def get_channel_names(self):
        try:
            with open(osp.join(PATH, "channel_names.json"), "r") as f:
                return json.loads(f.read())
        except IOError:
            return ["Channel " + str(i) for i in xrange(self.n_channels)]
    
    def set_channel_name(self, index, name):
        names = self.get_channel_names()
        names[index] = name
        with open(osp.join(PATH, "channel_names.json"), "w") as f:
            return f.write(json.dumps(names))
    

ARROSEUR = Arroseur()
