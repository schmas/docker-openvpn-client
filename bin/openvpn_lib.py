#!/usr/bin/python3 -u
import errno
import json
import os
import os.path
import re
import signal
import stat
import sys

KILL_PROCESS_TIMEOUT = 5
KILL_ALL_PROCESSES_TIMEOUT = 5

LOG_LEVEL_ERROR = 1
LOG_LEVEL_WARN = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3

SHENV_NAME_WHITELIST_REGEX = re.compile('[^\w\-_\.]')

log_level = LOG_LEVEL_INFO

terminated_child_processes = {}


class AlarmException(Exception):
    pass


def error(message):
    if log_level >= LOG_LEVEL_ERROR:
        sys.stderr.write("*** %s\n" % message)


def warn(message):
    if log_level >= LOG_LEVEL_WARN:
        sys.stderr.write("*** %s\n" % message)


def info(message):
    if log_level >= LOG_LEVEL_INFO:
        sys.stderr.write("*** %s\n" % message)


def debug(message):
    if log_level >= LOG_LEVEL_DEBUG:
        sys.stderr.write("*** %s\n" % message)


def ignore_signals_and_raise_keyboard_interrupt(signame):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    raise KeyboardInterrupt(signame)


def raise_alarm_exception():
    raise AlarmException('Alarm')


def listdir(path):
    try:
        result = os.stat(path)
    except OSError:
        return []
    if stat.S_ISDIR(result.st_mode):
        return sorted(os.listdir(path))
    else:
        return []


def is_exe(path):
    try:
        return os.path.isfile(path) and os.access(path, os.X_OK)
    except OSError:
        return False


def import_envvars(clear_existing_environment=True, override_existing_environment=True):
    if not os.path.exists("/etc/container_environment"):
        return
    new_env = {}
    for envfile in listdir("/etc/container_environment"):
        name = os.path.basename(envfile)
        with open("/etc/container_environment/" + envfile, "r") as f:
            # Text files often end with a trailing newline, which we
            # don't want to include in the env variable value. See
            # https://github.com/phusion/baseimage-docker/pull/49
            value = re.sub('\n\Z', '', f.read())
        new_env[name] = value
    if clear_existing_environment:
        os.environ.clear()
    for name, value in new_env.items():
        if override_existing_environment or not name in os.environ:
            os.environ[name] = value


def export_envvars(to_dir=True):
    if not os.path.exists("/etc/container_environment"):
        return
    shell_dump = ""
    for name, value in os.environ.items():
        if name in ['HOME', 'USER', 'GROUP', 'UID', 'GID', 'SHELL']:
            continue
        if to_dir:
            with open("/etc/container_environment/" + name, "w") as f:
                f.write(value)
        shell_dump += "export " + sanitize_shenvname(name) + "=" + shquote(value) + "\n"
    with open("/etc/container_environment.sh", "w") as f:
        f.write(shell_dump)
    with open("/etc/container_environment.json", "w") as f:
        f.write(json.dumps(dict(os.environ)))


_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search


def shquote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"


def sanitize_shenvname(s):
    return re.sub(SHENV_NAME_WHITELIST_REGEX, "_", s)


# Waits for the child process with the given PID, while at the same time
# reaping any other child processes that have exited (e.g. adopted child
# processes that have terminated).
def waitpid_reap_other_children(pid):
    global terminated_child_processes

    status = terminated_child_processes.get(pid)
    if status:
        # A previous call to waitpid_reap_other_children(),
        # with an argument not equal to the current argument,
        # already waited for this process. Return the status
        # that was obtained back then.
        del terminated_child_processes[pid]
        return status

    done = False
    status = None
    while not done:
        try:
            # https://github.com/phusion/baseimage-docker/issues/151#issuecomment-92660569
            this_pid, status = os.waitpid(pid, os.WNOHANG)
            if this_pid == 0:
                this_pid, status = os.waitpid(-1, 0)
            if this_pid == pid:
                done = True
            else:
                # Save status for later.
                terminated_child_processes[this_pid] = status
        except OSError as e:
            if e.errno == errno.ECHILD or e.errno == errno.ESRCH:
                return None
            else:
                raise
    return status


def stop_child_process(name, pid, signo=signal.SIGTERM, time_limit=KILL_PROCESS_TIMEOUT):
    info("Shutting down %s (PID %d)..." % (name, pid))
    try:
        os.kill(pid, signo)
    except OSError:
        pass
    signal.alarm(time_limit)
    try:
        try:
            waitpid_reap_other_children(pid)
        except OSError:
            pass
    except AlarmException:
        warn("%s (PID %d) did not shut down in time. Forcing it to exit." % (name, pid))
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            waitpid_reap_other_children(pid)
        except OSError:
            pass
    finally:
        signal.alarm(0)


def run_command_killable(*argv):
    filename = argv[0]
    status = None
    pid = os.spawnvp(os.P_NOWAIT, filename, argv)
    try:
        status = waitpid_reap_other_children(pid)
    except BaseException as s:
        warn("An error occurred. Aborting.")
        stop_child_process(filename, pid)
        raise
    if status != 0:
        if status is None:
            error("%s exited with unknown status\n" % filename)
        else:
            error("%s failed with status %d\n" % (filename, os.WEXITSTATUS(status)))
        sys.exit(1)


def run_command_killable_and_import_envvars(*argv):
    run_command_killable(*argv)
    import_envvars()
    export_envvars(False)


def kill_all_processes(time_limit):
    info("Killing all processes...")
    try:
        os.kill(-1, signal.SIGTERM)
    except OSError:
        pass
    signal.alarm(time_limit)
    try:
        # Wait until no more child processes exist.
        done = False
        while not done:
            try:
                os.waitpid(-1, 0)
            except OSError as e:
                if e.errno == errno.ECHILD:
                    done = True
                else:
                    raise
    except AlarmException:
        warn("Not all processes have exited in time. Forcing them to exit.")
        try:
            os.kill(-1, signal.SIGKILL)
        except OSError:
            pass
    finally:
        signal.alarm(0)


def run_files_from_dir(directory, script_args=None):
    for name in listdir(directory):
        filename = os.path.join(directory, name)
        if is_exe(filename):
            info("Running %s %s ..." % (filename, ' '.join(script_args)))
            run_command_killable_and_import_envvars(filename, *script_args)
