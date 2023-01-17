import os


def gethddtemp():
    # code by Jeff Curless : https://github.com/JeffCurless/argoneon
    outputobj = {}
    hddtempcmd = "/usr/sbin/smartctl"
    if os.path.exists(hddtempcmd):
        command = os.popen("lsblk | grep -e '0 disk' | awk '{print $1}'")
        tmp = command.read()
        command.close()
        alllines = [l for l in tmp.split("\n") if l]
        for curdev in alllines:
            if curdev[0:2] == "sd" or curdev[0:2] == "hd":
                def getSmart(smartCmd):
                    try:
                        command = os.popen(smartCmd)
                        smartctlOutRaw = command.read()
                    except Exception as e:
                        print(e)
                    finally:
                        command.close()
                    if 'Permission denied' in smartctlOutRaw and not smartCmd.startswith('sudo'):
                        return getSmart(f"sudo {smartCmd}")
                    if 'scsi error unsupported scsi opcode' in smartctlOutRaw:
                        return None
                    smartctlOut = [l for l in smartctlOutRaw.split('\n') if l]
                    for smartAttr in ["194", "190"]:
                        try:
                            line = [l for l in smartctlOut if l.startswith(smartAttr)][0]
                            parts = [p for p in line.replace('\t', ' ').split(' ') if p]
                            tempval = float(parts[9])
                            return tempval
                        except IndexError:
                            ...
                    for smartAttr in ["Temperature:"]:
                        try:
                            line = [l for l in smartctlOut if l.startswith(smartAttr)][0]
                            parts = [p for p in line.replace('\t', ' ').split(' ') if p]
                            tempval = float(parts[1])
                            return tempval
                        except IndexError:
                            ...
                    return None

                theTemp = getSmart(f"{hddtempcmd} -d sat -n standby,0 -A /dev/{curdev}")
                if theTemp:
                    outputobj[curdev] = theTemp
                else:
                    theTemp = getSmart(f"{hddtempcmd} -n standby,0 -A /dev/{curdev}")
                    if theTemp:
                        outputobj[curdev] = theTemp
    return outputobj
