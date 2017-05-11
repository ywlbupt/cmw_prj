#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

ue_struct = namedtuple("ue_struct",['BAND','CH_UL','CH_DL','BW'])

LTE_BW_5="B050"
LTE_BW_10="B100"
LTE_BW_20="B200"
LOW_CHANNEL = 0
MID_CHANNEL = 1
HIGH_CHANNEL = 2

