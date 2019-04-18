#!/usr/bin/python

import subprocess
import datetime
import os
import time

def chmod(permission, file_path, tag=None):
    cmd = "chmod %s %s" % (permission, file_path)
    run_command(cmd, tag=tag)

def cp(file_path, destination_path, tag=None):
    cmd = "cp %s %s" % (file_path, destination_path)
    run_command(cmd)

def cd(destination, tag=None):
    cmd = "cd %s" % destination
    run_command(cmd, tag=tag)

def mv(source, destination, tag=None):
    cmd = "mv %s %s" % (source, destination)
    run_command(cmd, tag=tag) 

def mkdir(dir_path, tag=None):
    cmd = "mkdir %s" % dir_path
    run_command(cmd, tag=tag)

def run_command_capture_output(cmd, tag=None, env=None):
    print cmd
    p = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        shell=True
    )
    out = p.stdout.read()
    err = p.stderr.read()
    return out, err

def run_command(cmd, tag=None, env=None):
    """
    If the environment is set up correctly, this  runs the 'run_command' bash function that should be 
    exported to the current shell.  'run_command' will add an entry in the command log and execute 
    the command.
    Args:
        cmd: command-line command
        tag: a short identifier for the command
    """
    print "Running: %s" % cmd
    if 'LOG_COMMANDS' in os.environ.keys():
        subprocess.call("run_command \"%s\" \"%s\"" % (cmd, tag), shell=True, env=env)
    else:
        subprocess.call(cmd, shell=True, env=env)

def run_command_with_retry(cmd, max_attempts=5, pause=0, tag=None, env=None):
    success = False
    attempts = 0
    while success == False and attempts < max_attempts:
        succeeded = True
        try:
            if 'LOG_COMMANDS' in os.environ.keys():
                subprocess.check_call("run_command \"%s\" \"%s\"" % (cmd, tag), shell=True, env=env)
            else:
                subprocess.check_call(cmd, shell=True, env=env)
        except subprocess.CalledProcessError as e:
            succeeded = False
        success = succeeded
        if not success:
            time.sleep(pause)   
        attempts += 1 
    return success

def run_command_in_background(cmd, env=None):
    print "(%s) Running in background: %s" % (datetime.datetime.now().strftime("%A %B %d %H:%M:%S %Z %Y"), cmd)
    os.system("%s &" % cmd)

def run_command_checked(cmd, env=None):
    print "(%s) Running: %s" % (datetime.datetime.now().strftime("%A %B %d %H:%M:%S %Z %Y"), cmd)
    try:
        subprocess.check_call(cmd, shell=True, env=env)
    except subprocess.CalledProcessError, e:
        raise Exception("Command was terminated or failed:\n%s" % cmd)

