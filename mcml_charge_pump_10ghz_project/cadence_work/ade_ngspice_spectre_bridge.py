#!/usr/bin/python
"""Truthful ADE simulator adapter: Virtuoso netlist -> host ngspice -> PSF.

This command occupies the local placeholder 'spectre' path only because ADE L
invokes that name. It does not claim to be or include Cadence Spectre.
"""
from __future__ import print_function
import json
import os
import socket
import sys
import time

SOCKET = '/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/ade_bridge.sock'

if any(a in ('-v', '-V', '-version') for a in sys.argv[1:]):
    print('ADE ngspice bridge 1.0 (NOT Cadence Spectre)')
    sys.exit(0)

args = sys.argv[1:]
raw_dir = '../psf'
log_file = '../psf/spectre.out'
netlist = 'input.scs'
i = 0
while i < len(args):
    arg = args[i]
    if arg in ('-raw', '+raw', '-log', '+log'):
        if i + 1 >= len(args):
            print('ADE ngspice bridge: missing value for ' + arg, file=sys.stderr)
            sys.exit(2)
        if arg in ('-raw', '+raw'):
            raw_dir = args[i+1]
        else:
            log_file = args[i+1]
        i += 2
        continue
    if not arg.startswith(('-', '+')) and arg.endswith('.scs'):
        netlist = arg
    i += 1

request = {
    'netlist': os.path.abspath(netlist),
    'raw_dir': os.path.abspath(raw_dir),
    'log_file': os.path.abspath(log_file),
}
try:
    # Do not leave an old waveform available when a new run fails.
    old = os.path.join(request['raw_dir'], 'tran.tran')
    if os.path.isfile(old):
        os.unlink(old)
    for attempt in range(10):
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.settimeout(240)
        try:
            connection.connect(SOCKET)
            break
        except socket.error:
            connection.close()
            if attempt == 9:
                raise
            time.sleep(0.5)
    connection.sendall((json.dumps(request) + '\n').encode('utf-8'))
    data = ''
    while '\n' not in data:
        part = connection.recv(8192)
        if not part:
            raise IOError('host bridge closed without a result')
        data += part
    connection.close()
    reply = json.loads(data.split('\n', 1)[0])
    if not reply.get('ok'):
        raise RuntimeError(reply.get('error', 'unknown host bridge error'))
    print('ADE ngspice bridge completed: %s, stop=%s, rows=%s; NOT Cadence Spectre' % (reply['mode'], reply['stop'], reply['rows']))
except Exception as exc:
    message = 'ADE ngspice bridge FAILED: %s\n' % exc
    print(message, file=sys.stderr)
    directory = os.path.dirname(request['log_file'])
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    with open(request['log_file'], 'w') as stream:
        stream.write(message)
        stream.write('This is not a Cadence Spectre run. No valid waveform was produced.\n')
    sys.exit(1)
