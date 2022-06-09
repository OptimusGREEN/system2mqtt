
from subprocess import call
from time import sleep
import logging, os
from optilibs.system_info import Platform, get_hostname
from optilibs.secret import Secret
secret = Secret()

hostname = get_hostname()

filepath = os.path.join(os.path.dirname(__file__), "s2m.py")

restart_timer = 2


def start_system2mqtt():
    try:
        logging.info("Starting '{}' script: '{}'".format(hostname, filepath))
        call(filepath, shell=True)
        logging.info("Watchdog PID: {}".format(os.getpid()))
    except Exception as e:
        logging.error(e)
        # Script crashed, lets restart it!
        logging.error("Script crashed! Restarting in {} seconds".format(restart_timer))
        handle_crash()


def handle_crash():
    sleep(restart_timer)
    start_system2mqtt()


if __name__ == '__main__':
    start_system2mqtt()
