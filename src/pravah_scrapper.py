import requests
import threading
import traceback

from dytimer import DynamicTimer

bot_url = 'http://127.0.0.1:8080/hubot/notif'

class Scrapper:
    def __init__(self, name='', verbose=True, default_timeout=10, default_timer=10):
        super().__init__()

        self.name = name
        self.session = requests.Session()
        self.thread = []
        self.verbose = verbose
        self.default_timeout = default_timeout
        self.default_timer = default_timer

        try:
            self.login(self.session)
            self.log('Login Success', mtype='info')
        except Exception as e:
            self.log(e)
            exit()
    
    def login(self, session):
        pass
    
    def before_step(self, session):
        pass

    def step(self, session, thread=None):
        pass

    def start(self):
        self.log('Starting ' + self.name + ' scrapper', mtype='info')
        data = self.before_step(self.session)
        if len(self.thread) == 0:
            self.loop({
                'name': self.name,
                'data': data,
                'timer': DynamicTimer(self.name, self.default_timer)
            })
        else:
            for t in self.thread[1:]:
                threading.Thread(target=self.loop, args=(t,)).start()
            self.loop(self.thread[0])
    
    def loop(self, thread):
        while(True):
            try:
                self.step(self.session, thread)
                thread['timer'].wait()
            except Exception as e:
                self.log('[name:' + self.name + '/thread:' + thread['name'] + '] Err: ' + str(e))
                traceback.print_exc()
                thread['timer'].wait()
                pass
    
    def add_thread_execution(self, thread_name, thread_data):
        self.thread.append({
            'name': thread_name,
            'data': thread_data,
            'timer': DynamicTimer(thread_name, 10)
        })
    
    def log(self, msg, mtype='error', post_to_bot=True):
        if self.verbose:
            print('[' + mtype + '/' + self.name + ']: ' + str(msg))
            if mtype == 'error':
                traceback.print_exc()
        try:
            if post_to_bot:
                requests.post(bot_url, json={'type': mtype, 'msg': str(msg)})
        except:
            pass

    def get(self, url, **kwargs):
        kwargs.setdefault('timeout', self.default_timeout)
        return self.session.get(url, **kwargs)
    
    def post(self, url, data=None, json=None, **kwargs):
        kwargs.setdefault('timeout', self.default_timeout)
        return self.session.post(url, data, json, **kwargs)



