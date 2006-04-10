from __future__ import division

"""
Classes to support nib files
--------------------------------------

:Author: Bob Harris (rsharris@bx.psu.edu)
:Version: $Revision: $

A nib sequence is a sequence of DNA, using the 10 character alphabet A,C,G,T,N
(upper and lower case).  The file is packed as 4 bits per character.

nib file format:

   Fields can be in big- or little-endian format;  they must match the endianess
   of the magic number.

   offset 0x00: 6B E9 3D 3A   big endian magic number (3A 3D E9 6B => little endian)
   offset 0x04: xx xx xx xx   length of data sequence (counted in characters)
   offset 0x08:  ...          data sequence;  most significant nybble in each
                              byte is first in sequence
"""

from bx.seq.seq import SeqFile
import sys, struct, string, math

NIB_MAGIC_NUMBER = 0x6BE93D3A
NIB_MAGIC_NUMBER_SWAP = 0x3A3DE96B
NIB_MAGIC_SIZE = 4
NIB_LENGTH_SIZE = 4
NIB_I2C_TABLE = "TCAGNXXXtcagnxxx"

class NibFile(SeqFile):

    def __init__(self, file, revcomp=False, name="", gap=None):
        SeqFile.__init__(self,file,revcomp,name,gap)

        self.byte_order = ">"
        magic = struct.unpack(">L", file.read(NIB_MAGIC_SIZE))[0]
        if (magic != NIB_MAGIC_NUMBER):
            if magic == NIB_MAGIC_NUMBER_SWAP: self.byte_order = "<"
            else: raise "Not a NIB file"
        self.magic = magic
        self.length = struct.unpack("%sL" % self.byte_order, file.read(NIB_LENGTH_SIZE))[0]

    def raw_fetch(self, start, length):
        # Read block of bytes containing sequence
        block_start = int(math.floor(start / 2))
        block_end = int(math.floor((start + length - 1) / 2))
        block_len = block_end + 1 - block_start
        self.file.seek(NIB_MAGIC_SIZE + NIB_LENGTH_SIZE + block_start)
        result = []
        raw = self.file.read(block_len)
        data = struct.unpack("%s%dB" % (self.byte_order, block_len), raw)
        # Translate to character representation
        for value in data:
            result.append(NIB_I2C_TABLE[ (value >> 4) & 0xF ])
            result.append(NIB_I2C_TABLE[ (value >> 0) & 0xF ])
        # Trim if start / end are odd
        if start & 1: del result[ 0 ]
        if (start + length) & 1: del result[ -1 ]
        # Return as string
        return string.join(result, '')
