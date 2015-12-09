"""
Decoder for RDT BUFR files

Based on FM 94 BUFR edition 3 as found in WMO306_vl2_BUFR3_Spec_en.pdf

"""

from bufrdec import decode, decode_file, decode_all, Section0, Section1v3, Section1v4, Section2, Section3, Section4, Section5, Message

__title__ = 'bufrpy'
__author__ = 'Tuure Laurinolli / FMI'
__version__ = "0.2.1"
__copyright__ = 'Copyright 2013 Finnish Meteorological Institute'

__all__ = ["decode", "decode_file", "decode_all", "Section0", "Section1v3", "Section1v4", "Section2", "Section3", "Section4", "Section5", "Message"]
