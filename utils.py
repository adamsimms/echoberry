import signal
import subprocess
import os


def kill_process_by_name(proc_name):
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.decode().splitlines():
        if proc_name in line:
            pid = int(line.split(None, 1)[0])
            print('Found PID({}) of `{}`, killing...'.format(pid, proc_name))
            os.kill(pid, signal.SIGKILL)
