import click

import logging
import math
import json
import threading
import RPi.GPIO as GPIO

import aqi

from signal import pthread_kill, SIGTSTP
from time import sleep

from xmlrpc.server import SimpleXMLRPCServer

import xmlrpc.client

"""
Simple client/server to count sensor clicks and compute wind speed.

"""

HALL_EFFECT_GPIO = 20 # in BCM
SPEED_POLLING_INTERVAL = 10 # seconds

cnt = 0

r = 10 # cm, the radius of the spinner
rpm = 0

c = 2 * r * math.pi # cm

struct = {}

def compute(rpm, pi=SPEED_POLLING_INTERVAL):
    return dict(kph=rpm * c * 60 / 100000,
             mph=(rpm * c * 60 / 100000) * 0.621371,
             mps=rpm * c / 6000,
             rpm=rpm)


def count(*a, **k):
    global cnt
    cnt = cnt + 1
    # print("tick")

def interval(*a, **k):
    global rpm, cnt, struct
    while True:
        struct = aqi.get()
        rpm = cnt * (60 / SPEED_POLLING_INTERVAL)
        struct['meterological']['windspeed'] = compute(rpm)
        cnt = 0
        sleep(SPEED_POLLING_INTERVAL)

def serve():
    return struct


@click.group()
def cli():
    """
Simple client/server to count sensor clicks and compute wind speed.

"""
    pass


@cli.command()
@click.option('-f', '--foreground', default=False)
def start(foreground=False):
    "Start the counting daemon."
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    logging.debug("start ok")
    with SimpleXMLRPCServer(('localhost', 8000)) as server:

        logging.debug("setup server")
        server.register_function(serve)

        
        logging.info("create thread")
        T = threading.Thread(target=interval, daemon=True)

        # GPIO.setmode(GPIO.BOARD) # etc
        logging.info("setup pins")
        GPIO.setup(HALL_EFFECT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


        logging.debug("setup callback")
        GPIO.add_event_detect(HALL_EFFECT_GPIO, GPIO.FALLING, callback=count, bouncetime=10)

        logging.info("starting sensor")
        T.start()

        logging.info("starting server")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            logging.error("stopping server")
            GPIO.cleanup()

            logging.info("cleaning up")
            pthread_kill(T.ident, SIGTSTP)
            
            logging.error("waiting to stop")
            T.join()


        


@cli.command()
def get():
    "Get the computed wind speed from the last 10 seconds."
    srv = xmlrpc.client.ServerProxy('http://localhost:8000')
    print(json.dumps(srv.serve()))




if __name__ == '__main__':
    cli()
