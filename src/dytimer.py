import time
import math
import hashlib
import schedule
import pytz
import json

from datetime import datetime, timedelta
from deepdiff import DeepDiff

WAIT_FACTOR = 10
DUP_FACTOR = 1.6
ERR_WAIT_MAX = 3600

class DynamicTimer:
    def __init__(self, name, start=50):
        self.name = name
        self.wait_time = start
        self.start = start

        self.cycle = 0
        self.old_hash = {}
        self.old_text = {}
        self.force_sleep = 0

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
            self.cycle += 1
            if self.cycle == 1:
                return
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
        if self.force_sleep != 0:
            print('Force stop init.')
            time.sleep(self.force_sleep)
            self.force_sleep = 0
            print('Force stop breaking.')
            return
        schedule.run_pending()
        print('sleeping... [' + self.name + '] for [' + str(self.wait_time) + ' sec]')
        time.sleep(self.wait_time)
    
    def __str__(self):
        return 'wait[' + str(self.wait_time) + ' sec] - since[' + str(self.time_since_last_update) + ']'
    
    def is_duplicate(self, data, tag='default', check_json_deep=False):
        new_hash = hashlib.md5(data).hexdigest()
        if tag not in self.old_hash:
            self.old_hash[tag] = new_hash
            self.old_text[tag] = data
            return False
        
        if self.old_hash[tag] == new_hash:
            self.register_dup_data()
            return True
        else:
            if check_json_deep:
                a = json.loads(self.old_text[tag])
                b = json.loads(data)
                diff_val = DeepDiff(a, b, ignore_order=True)
                print(diff_val)
                if not diff_val:
                    self.register_dup_data()
                    return True
            self.old_hash[tag] = new_hash
            self.old_text[tag] = data
            return False
    
    def enable_force_stop_bw_time(self, stop_at, stop_till, timezone='Asia/Kolkata'):
        
        to_zone = pytz.timezone(timezone)

        stop_time = datetime.strptime(stop_at, '%H:%M')
        till_time = datetime.strptime(stop_till, '%H:%M')

        local_now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(to_zone)
        
        stop_temp = local_now
        stop_temp = stop_temp.replace(hour = stop_time.hour)
        stop_temp = stop_temp.replace(minute = stop_time.minute)

        till_temp = stop_temp + timedelta(seconds=(till_time - stop_time).seconds)

        def job():
            self.force_sleep = (till_temp - local_now).seconds
            print('Force Stop for: ' + str(self.force_sleep) + ' secs')
        schedule.every().day.at(stop_at).do(job)
    
    def disable_force_stop_bw_time(self):
        self.force_sleep = 0


