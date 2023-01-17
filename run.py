#!/usr/bin/env python3

# s2m watchdog

from subprocess import call, check_call
from time import sleep
import logging, os, sys

try:
    deps = os.path.join(os.path.dirname(os.path.realpath(__file__)), "deps.txt")
    check_call(["pip3", "install", "-r", deps])
except:
    logging.error("You will need to install the requirements, try...\n\n pip3 install -r deps.txt")

from libs.system_info import get_hostname

hostname = get_hostname()

filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "s2m.py")

restart_timer = 2


def start_system2mqtt(envfile):
    try:
        logging.info("Starting '{}' script: '{}'".format(hostname, filepath))
        call("{} {}".format(filepath, envfile), shell=True)
        logging.info("Watchdog PID: {}".format(os.getpid()))
    except Exception as e:
        logging.error(e)
        # Script crashed, lets restart it!
        logging.error("Script crashed! Restarting in {} seconds".format(restart_timer))
        handle_crash(envfile)


def handle_crash(envfile):
    sleep(restart_timer)
    start_system2mqtt(envfile)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        start_system2mqtt(sys.argv[1])
    else:
        config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "s2m.conf")
        start_system2mqtt(config)
