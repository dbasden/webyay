#!/usr/bin/env python3

import logging
from dataclasses import dataclass

@dataclass
class RadioState:
    vfo_a: int = 7100000
    vfo_b: int = 7100000

@dataclass
class CATCommand:
    cmd: bytes
    param: bytes

    def __bytes__(self):
        return cmd+param+b';'

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
