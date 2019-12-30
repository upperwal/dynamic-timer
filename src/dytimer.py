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
WAIT_MAX = 3600

class DynamicTimer:
    def __init__(self, name, start_wait_time=50, wait_time_min = 2, wait_time_max = WAIT_MAX):
        self.name = name
        self.wait_time = start_wait_time
        self.start = start_wait_time

        self.cycle = 0
        self.old_hash = {}
        self.old_text = {}
        self.force_sleep = 0
        self.wait_time_min = wait_time_min
        self.wait_time_max = wait_time_max

        self.time_since_last_update = 0
    
    def register_dup_data(self, penalty = DUP_FACTOR, penalty_weight = 0.2):
        old = self.wait_time
        self.time_since_last_update += self.wait_time
        new_time = int(math.ceil(((1 - penalty_weight) * self.wait_time + penalty_weight * self.wait_time * penalty)))
        self.wait_time = new_time
        self.check_min_max()
        print('[DUP Inc] Changing WT from ' + str(old) + ' -> ' + str(self.wait_time) + ' sec [' + self.name + ']')

    def register_fresh_data(self, early_hit_reward = 0.9, delay_hit_penalty = 0.2):
        old = self.wait_time
        if self.time_since_last_update > 0:
            self.wait_time = int((1 - delay_hit_penalty) * self.wait_time + delay_hit_penalty * self.time_since_last_update)
        else:
            self.cycle += 1
            if self.cycle == 1:
                return
            self.wait_time = int(early_hit_reward * self.wait_time)
        self.check_min_max()
        print('Changing WT from ' + str(old) + ' -> ' + str(self.wait_time) + ' sec [' + self.name + ']')
        self.time_since_last_update = 0

    def register_error(self, penalty_weight = WAIT_FACTOR):
        old = self.wait_time
        self.wait_time *= penalty_weight
        self.check_min_max()
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

    def check_min_max(self):
        if self.wait_time < self.wait_time_min:
            print('New time dropped below min time. Reverting to min time.')
            self.wait_time = self.wait_time_min
            return True
        elif self.wait_time > self.wait_time_max:
            print('New time is more than max wait time. Reverting to max time.')
            self.wait_time = self.wait_time_max
            return True
        return False
    
    def is_duplicate(self, data, tag='default', check_json_deep=False, update_dup = True):
        new_hash = hashlib.md5(data).hexdigest()
        if tag not in self.old_hash:
            self.old_hash[tag] = new_hash
            self.old_text[tag] = data
            return False
        
        if self.old_hash[tag] == new_hash:
            if update_dup:
                self.register_dup_data()
            return True
        else:
            if check_json_deep:
                a = json.loads(self.old_text[tag])
                b = json.loads(data)
                diff_val = DeepDiff(a, b, ignore_order=True)
                if not diff_val:
                    if update_dup:
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


