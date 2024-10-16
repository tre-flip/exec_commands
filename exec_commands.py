#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import importlib.util
from functools import partial

CMDS_VAR_NAME = "CMDS"

cmd_cache = dict()


# Don't litter the directrory tree with .pyc files.
sys.dont_write_bytecode = True


def _file_read_variable(var_name, filepath):
    """
    Read a variable from a python file, return a tuple (filepath, variable_value)
    if the file was read correctrly and the variable was found.
    Otherwise, return None.
    """
    spec = importlib.util.spec_from_file_location("tmp_module", filepath)
    if spec:
        file_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(file_module)
        var_value = file_module.__dict__.get(var_name)
        return (filepath, var_value) if var_value else None


file_read_cmds = partial(_file_read_variable, CMDS_VAR_NAME)


def read_cmds(dir):
    """
    Read all the values of a variable CMDS accross all files under dir.
    """
    files = filter(Path.is_file, Path(dir).rglob("*"))
    result = []
    for f in files:
        var = file_read_cmds(f)
        var and result.append(var)
    return sorted(result)


def exec_cmd(cmd):
    """
    Execute a shell command
    """
    if cmd_cache.get(cmd):
        print(f'Команда "{cmd}" уже выполнялась.')
    else:
        os.system(cmd)
        cmd_cache[cmd] = True


def exec_cmd_tuple(cmd_tuple):
    """
    Execute a list of commands from a tuple (file_path, commands_list) in a subshell
    """
    _, cmds = cmd_tuple
    for cmd in cmds:
        exec_cmd(cmd)


def help():
    """
    Print help for this program.
    """
    info = f"""
    Traverse a directory tree DIR and execute echo commands contained
    in {CMDS_VAR_NAME} accross all .py files in it.

    Usage: exec_commands.py DIR
    """
    print(info)


def main():
    # This script has just one simple argument, no need for argparse
    if len(sys.argv) != 2:
        help()
        sys.exit(1)
    dir = Path(sys.argv[1])
    if not Path.is_dir(dir):
        help()
        sys.exit(1)
    cmd_tuples = read_cmds(dir)
    for tup in cmd_tuples:
        exec_cmd_tuple(tup)


if __name__ == "__main__":
    main()
