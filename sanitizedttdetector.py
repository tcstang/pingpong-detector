#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import pdb
import json
import requests
import time

GPIO_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, GPIO.PUD_DOWN)

TIME_BETWEEN_SESSIONS = 180 # 3 minutes between sessions
CHIME_URL = ""
WEB_SERVICE = ""

class TableTennisSessionDetector:
    def __init__(self):
        self.current_state = GPIO.LOW
        self.previous_state = GPIO.LOW
        self.session_time = None
    
    def get_time(self):
        """ returns time in seconds """
        return int(time.time())

    def send_notification(self, message):
        """ sends a message to CHIME_URL webhook """
        payload = { 
            "Content": message
            }
        headers = {
            "Content-Type": "application/json"
            }
        response = requests.post(CHIME_URL, headers=headers, data=json.dumps(payload))
        print(response.status_code)

    def notify_in_use(self):
        self.send_notification("Table is now in use :(")
        payload = {
                "Status": 1
                }
        requests.post(WEB_SERVICE, data=json.dumps(payload))

    def notify_free(self):
        self.send_notification("Table is no longer in use!")
        payload = {
                "Status": 0
                }
        requests.post(WEB_SERVICE, data=json.dumps(payload))
    
    def is_session_active(self):
        if self.current_state == GPIO.LOW and self.get_time() > session_time + TIME_BETWEEN_SESSIONS:
            return True
        else:
            return False

    def is_new_session(self):
        if self.current_state == GPIO.HIGH and self.previous_state == GPIO.LOW and self.get_time() > session_time + TIME_BETWEEN_SESSIONS:
            return True
        else:
            return False
    
    def run_forever(self):
        while True:
            time.sleep(1)
            self.current_state = GPIO.input(GPIO_PIN)

            if self.current_state == GPIO.HIGH:
                """ update time whenever session is detected """
                self.session_time = self.get_time()

            if self.current_state != self.previous_state:
                if self.current_state == GPIO.HIGH:
                    self.previous_state = self.current_state
                    self.notify_in_use()
                else:
                    if self.get_time() > self.session_time + TIME_BETWEEN_SESSIONS:
                        """ only reset previous state after timeout """
                        self.previous_state = self.current_state
                        self.notify_free()
        
if __name__ == "__main__":
    detector = TableTennisSessionDetector()
    detector.run_forever()
