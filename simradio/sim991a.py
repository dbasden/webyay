#!/usr/bin/env python3

import logging
from dataclasses import dataclass

@dataclass
class RadioState:
    vfo_a: int = 7100000
    vfo_b: int = 7100000
    vfo:   int = 0
    tuner: int = 1

# Commands that don't take parameters but are SET requests to the radio
EMPTY_SET_COMMANDS = set(b'AB BA'.split(b' '))


class BadCommand(ValueError):
    pass

@dataclass
class CATCommand:
    cmd: bytes
    param: bytes

    # TODO: Add helpers to make reading/writing param easier

    def __bytes__(self):
        return self.cmd+self.param+b';'

    def is_read_cmd(self):
        '''returns True if the command is a read request TO the radio
        '''
        # For now, anything that doesn't have a parameter
        return self.param is None and self.param not in EMPTY_SET_COMMANDS

    @classmethod
    def from_bytes(cls, msg: bytes):
        msglen = len(msg)
        if msglen < 3:
            raise ValueError('CAT Command must be at least 3 bytes')
        if msg[-1:] != b';':
            raise ValueError('No terminal ; in CAT command')
        cmd = msg[:2]
        param = msg[2:-1] if msglen > 3 else None
        return cls(cmd=cmd, param=param)


class SimYaesu991A(object):
    def __init__(self):
        self.state = RadioState()

    def handle_message(self, msg):
        cmd = CATCommand.from_bytes(msg.encode('UTF-8'))
        logging.info(cmd)
        if cmd.is_read_cmd():
            return self.handle_read_cmd(cmd)
        return self.handle_set_cmd(cmd)

    def handle_read_cmd(self, msg):
        if msg.cmd == b'ID':
            return CATCommand(cmd = msg.cmd, param=b'0670')
        elif msg.cmd == b'AC':  # ANTENNA TUNER CONTROL
            resp = "%03d" % self.state.tuner
            assert len(resp) == 3
            return CATCommand(cmd = msg.cmd, param=resp.encode('utf-8')) 

    def handle_set_tuner(self, msg):
        tstate = msg.param[2] - ord('0')
        if msg.param[:2] != b'00' or tstate > 2:
            raise BadCommand(msg)
        self.state.tuner = tstate
        response = self.handle_read_cmd(msg)
        ## FIXME: Tuning should take a few seconds unless very HI SWR
        # (todo: add emulation of different SWR antenna and too-high-to-TX)
        # Immediately pull out of "tuning" into "tuned"
        if self.state.tuner == 2:
            self.state.tuner = 1
        return response

    def handle_set_cmd(self, msg):
        if msg.cmd == b'AB': # VFO-A to VFO-B
            self.state.vfo = 1

        elif msg.cmd == b'BA': # VFO-B to VFO-A
            self.state.vfo = 0

        elif msg.cmd == b'AC': # ANTENNA TUNER CONTROL
            return self.handle_set_tuner(msg)
