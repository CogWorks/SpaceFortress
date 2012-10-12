class Timer(object):
    
    def __init__(self, time_source):
        self.time = time_source
        self.start_time = self.time()
        self.cumtime = 0
        self.paused = False
        
    def pause(self):
        self.cumtime = self.elapsed()
        self.paused = True
        
    def unpause(self):
        self.paused = False
        self.start_time = self.time()
        
    def elapsed(self):
        if self.paused:
            return self.cumtime
        else:
            return self.cumtime + self.time() - self.start_time
        
    def reset(self):
        """resets timer to current time"""
        self.cumtime = 0
        self.start_time = self.time()
        
    def check(self):
        pass