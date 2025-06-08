# system2mqtt
Send system info to mqtt

Send cpu, memory, disk usage to mqtt periodically.

just clone the repo, alter the config file and run it with python3

it will attempt to create a python virtual environment and install required dependencies and then run.

see the below config example with notes at the bottom.

```
COMPUTER_NAME=MyTestComputer1                   # Required: 

##### UNCOMMENT ANY BELOW OPTIONS AS REQUIRED

#LOG_DIR=path/to/my/logs                         ### Optional: default: ./logs
#LOG_FILENAME=system2mqtt.log                    ### Optional: default: system2mqtt.log 
#OLD_LOG_FILENAME=old_system2mqtt.log            ### Optional: default: old_system2mqtt.log 
#DEBUG_LOG=True                                  ### Optional: default: False

#PUBLISH_PERIOD=30                               ### Optional: default: 30 (seconds)
#MQTT_BASE_TOPIC=system2mqtt/MyTestComputer1     ### Optional: default: system2mqtt/<COMPUTER_NAME>
#MQTT_HOST=192.168.0.14                          ### Optional: default: localhost
#MQTT_USER=myusername                            ### Optional: default: None
#MQTT_PASSWORD=mypassword                        ### Optional: default: None

#PROCPATH=/path/to/proc                          ### Optional: default: /proc (linux only, in case /proc is somewhere else)

#ARGON=True                                      ### Optional: default: False (Get info from pi argon case)

##### Proxmox
#PVE_SYSTEM=False                                ### Optional: default: False (Set to true if computer is running proxmox)

##### Below options are required if PVE_SYSTEM is set to true
#PVE_NODE_NAME=pve                               ### Default: pve                            
#PVE_HOST=192.168.0.7                            ### Default: localhost
#PVE_USER=root@pam                               ### Default: root@pam
#PVE_PASSWORD=mysooperdoopersecretpassword123


###### rename or copy this file (to be called) s2m.conf or pass its path as an argument when calling run.py
#### example: python3 system2mqtt/run.py path/to/my/s2m.conf (some info may only be available if run with elevated privileges)
```

A docker image is also available [here](https://hub.docker.com/repository/docker/optimusgreen/system2mqtt) but is only currently available for access to proxmox api rather than bare metal local system.

This has currently only been tested on linux/macos.