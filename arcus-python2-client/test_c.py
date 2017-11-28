from __future__ import absolute_import
from arcus import *
from arcus_mc_node import ArcusMCNodeAllocator
from arcus_mc_node import EflagFilter
import datetime, time, sys

import random

#enable_log()

import logging
logging.basicConfig()


timeout = 10

# client which use arcus memcached node & default arcus transcoder
client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))

print '### connect to client'
client.connect("172.17.0.3:2181", "studio-cloud")

def itoh(i):
    return '0x' + ('0'*(6-len(h))) + h[2:].upper()

ret = client.get('test:%d' % n)
print ret.get_result()

or i in xrange(0, 20):
	flag = 1
	print itoh(flag)
	ret = client.bop_insert('test:btree_eflag', i, flag, itoh(flag))
	print ret.get_result()

#ret = client.bop_get('test:btree_eflag', (0, 20), EflagFilter('EFLAG & 0x00ff == 0x0001'))
ret = client.bop_get('test:btree_eflag',(0,20), EflagFilter('EFLAG & 0x00FF == 0x0001'))
print ret.get_result()
result = ret.get_result()

client.disconnect()
