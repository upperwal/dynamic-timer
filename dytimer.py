import time
import math
import hashlib

WAIT_FACTOR = 10
DUP_FACTOR = 1.6
ERR_WAIT_MAX = 3600

class DynamicTimer:
    def __init__(self, name, start=50):
        self.name = name
        self.wait_time = start
        self.start = start

        self.old_hash = ''

        self.time_since_last_update = 0
    
    def register_dup_data(self):
        old = self.wait_time
        self.time_since_last_update += self.wait_time
        self.wait_time = int(math.ceil((0.8 * self.wait_time + 0.2 * self.wait_time * DUP_FACTOR)))
        print('[DUP Inc] Changing WT from ' + str(old) + ' -> ' + str(self.wait_time) + ' sec [' + self.name + ']')

    def register_fresh_data(self):
        old = self.wait_time
        if self.time_since_last_update > 0:
            self.wait_time = int(0.8 * self.wait_time + 0.2 * self.time_since_last_update)
        else:
            self.wait_time = int(0.9 * self.wait_time)
            if self.wait_time < 2:
                self.wait_time = 2
        print('Changing WT from ' + str(old) + ' -> ' + str(self.wait_time) + ' sec [' + self.name + ']')
        self.time_since_last_update = 0

    def register_error(self):
        old = self.wait_time
        self.wait_time *= WAIT_FACTOR
        if self.wait_time > ERR_WAIT_MAX:
            self.wait_time = ERR_WAIT_MAX
            return
        print('[ERR Inc] Changing WT from ' + str(old) + ' -> ' + str(self.wait_time) + ' sec [' + self.name + ']')

    def reset(self):
        self.wait_time = self.start
    
    def wait(self):
        time.sleep(self.wait_time)
    
    def __str__(self):
        return 'wait[' + str(self.wait_time) + ' sec] - since[' + str(self.time_since_last_update) + ']'
    
    def is_duplicate(self, data):
        new_hash = hashlib.md5(data).hexdigest()
        if self.old_hash == new_hash:
            self.register_dup_data()
            return True
        else:
            self.old_hash = new_hash
            return False