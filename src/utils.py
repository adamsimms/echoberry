import os
import signal
import subprocess


def kill_process_by_name(proc_name):
    """Fallback cleanup for orphaned processes not tracked by the app."""
    try:
        result = subprocess.run(
            ["pgrep", "-x", proc_name],
            capture_output=True,
            text=True,
            check=False,
        )
        pids = [int(pid) for pid in result.stdout.splitlines() if pid.strip()]
    except FileNotFoundError:
        pids = _find_pids_fallback(proc_name)

    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _find_pids_fallback(proc_name):
    p = subprocess.Popen(["ps", "-A"], stdout=subprocess.PIPE)
    out, _ = p.communicate()
    pids = []
    for line in out.decode().splitlines():
        if proc_name in line:
            pids.append(int(line.split(None, 1)[0]))
    return pids


def stop_processes(processes):
    for proc in processes:
        if proc.poll() is not None:
            continue
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
