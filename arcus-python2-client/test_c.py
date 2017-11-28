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
	h = hex(i)
	if len(h) % 2 == 1:
		h = '0x0%s' % h[2:].upper()
	else:
		h = '0x%s' % h[2:].upper()
	return h

n = 1000
e = 'hi i am'
ret = client.set('test:%d' % n, e, timeout)
print ret.get_result()

ret = client.get('test:%d' % n)
print ret.get_result()


#ret = client.bop_create('test:btree_eflag', ArcusTranscoder.FLAG_INTEGER, timeout)
#print ret.get_result()

#for i in xrange(0, 300):
#        flag = random.randint(200,300)
#	ret = client.bop_insert('test:btree_eflag', i, i, itoh(i))

#ret = client.bop_get('test:btree_eflag', (0, 300), EflagFilter('EFLAG & 0x002A == 0x0000'))
#ret = client.bop_get('test:btree_eflag',(0,20))
#print ret.get_result()
#result = ret.get_result()

client.disconnect()
