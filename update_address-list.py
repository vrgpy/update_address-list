#!/usr/bin/python3

# Updates a Mikrotik router address-list based on a text file listing the addresses.

import os
import sys
import re
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# Print according to DebugLevel
def log(level, intext):
    header = datetime.now().strftime("%Y/%m/%d %H:%M:%S ") +'['+ level.upper() +'] '

    text=str(intext)

    if (level.upper()=='FATAL'):
        if DebugLevel>0: print(header + text)
    elif (level.upper()=='ERROR'):
        if DebugLevel>1: print(header + text)
    elif (level.upper()=='WARN'):
        if DebugLevel>2: print(header + text)
    elif (level.upper()=='INFO'):
        if DebugLevel>3: print(header + text)
    elif (level.upper()=='DEBUG'):
        if DebugLevel>4: print(header + text)
    elif (level.upper()=='TRACE'):
        if DebugLevel>5: print(header + text)

# Loglevel adjusting
DebugLevels = { 'OFF':0, 'FATAL':1, 'ERROR':2, 'WARN':3, 'INFO':4, 'DEBUG':5, 'TRACE':6 }   
# Default logging
DebugLevel = DebugLevels['WARN']


def getlist(str):
  outlst = []
  with open(str, "r") as f:
    for line in f:    
      addr=line.strip("\n")
      addr=addr.strip()
      if len(addr) >3:
        outlst.append(addr)

  return outlst


def mk_removelistitem(cfg, ids):
    
    url=  "{}/ip/firewall/address-list/remove".format(str(cfg['url']))
    userid= str(cfg['username'])
    passwd= str(cfg['password'])
    
    reqcnt= { 'success': 0, 'total': 0 }   
    for id in ids:
      data = { "numbers": id }
      
      resp = requests.post(url, auth= HTTPBasicAuth(userid, passwd), json= data, verify=cfg['tlsverify'])
      log('DEBUG', resp.text)

      reqcnt['total']= reqcnt['total'] +1      
      if resp.status_code == 200:
          reqcnt['success']= reqcnt['success'] +1
      
    return reqcnt


def mk_addlistaddress(cfg, listname, addresses):
    
    url=  "{}/ip/firewall/address-list/add".format(str(cfg['url']))
    userid= str(cfg['username'])
    passwd= str(cfg['password'])
    
    reqcnt= { 'success': 0, 'total': 0 }    
    for addr in addresses:
      data = { "list": listname, "address": addr }
      
      resp = requests.post(url, auth= HTTPBasicAuth(userid, passwd), json= data, verify=cfg['tlsverify'])
      log('DEBUG', resp.text)

      reqcnt['total']= reqcnt['total'] +1      
      if resp.status_code == 200:
          reqcnt['success']= reqcnt['success'] +1
      
    return reqcnt


def mk_getlist(cfg, listname):
    
    url=  "{}/ip/firewall/address-list/print".format(str(cfg['url']))
    userid= str(cfg['username'])
    passwd= str(cfg['password'])
    data = { ".query" : [ "list={}".format(listname) ], ".proplist": [ ".id", "address" ] }
    
    log('TRACE', "URL: {}".format(url))
    log('TRACE', "username: {}".format(cfg['username']))
    log('TRACE', "password: {}".format(cfg['password']))
    log('TRACE', "data: {}".format(data))

    resp = requests.post(url, auth= HTTPBasicAuth(userid, passwd), json= data, verify=cfg['tlsverify'])
    log('TRACE', resp.text)
    
    return json.loads(resp.text)


import argparse
import os


# Initialize parser
parser = argparse.ArgumentParser(
  prog='update_address-list',
  description='Updates a Mikrotik Router address-list based on a file containg a list of IP addreses',
  epilog='Tested with Mikrotik RouterOS version 7.18.1'
  )

parser.add_argument('SourceFile', help= 'file with IP addreses to load')
parser.add_argument('AddressList', help= 'name of the Address List')
parser.add_argument('-i', '--ipver', default="4", metavar='IPVer', help= 'version of IP for the Address List. Default=4')
parser.add_argument('-c', '--config', metavar='ConfigFile', help = 'Specify configuration file. Default= ~/.update_address-list.json')
parser.add_argument('-v', '--verbose', action='count', default=0, help= 'increase logging level')

args = parser.parse_args()

# Debug
DebugLevel = DebugLevel + args.verbose
log('INFO', "DebugLevel: {}".format(DebugLevel))

log('TRACE', str(args))


# Configuration file

ConfigFile = ''
if args.config == None:
  ConfigFile = '{}/.update_address-list.json'.format(os.getenv("HOME"))
  if not os.path.exists(ConfigFile):
    print("ERROR: A config file should be specified with -c option if the default configuration file doesn't exist")
    exit(-1)
else:
  ConfigFile = args.config

if re.search('^~/', ConfigFile):
  ConfigFile = re.sub(r'^~', os.getenv("HOME"), ConfigFile)  

if not os.path.exists(ConfigFile):
  print("ERROR: Can't find the configuration file \"{}\"".format(ConfigFile))
  exit(-1)
  
config =''
f = open(ConfigFile)
try:
  config = json.load(f)
except ValueError:
    print('ERROR: Loading JSON from configuration file has failed')
f.close()

# Basic validation
assert isinstance(config, dict), "Configuration file should be a JSON dictionary"
assert config['endpoint'] != None, "Configuration file: Endpoint not defined"
assert config['endpoint']['url'] != None, "Configuration file: Endpoint has no URL"
assert config['endpoint']['username'] != None, "Configuration file: Endpoint file has no username"
assert config['endpoint']['password'] != None, "Configuration file: Endpoint file has no password"
config['endpoint']['tlsverify'] = config['endpoint'].get('tlsverify', True)

# Load Source File
srclst=''
if os.path.exists(args.SourceFile):
  srclst = getlist(args.SourceFile)
else:
  log('FATAL', "The source file \"{}\" does not exist".format(args.SourceFile))
  print("ERROR: Can't find the source file \"{}\"".format(args.SourceFile))
  exit(1)
log('DEBUG',"Source file has {} records".format(len(srclst)))
log('TRACE', str(srclst))


# Get Router Access File
log('TRACE', "Router:")
rtrlst = mk_getlist(config['endpoint'], args.AddressList)
log('DEBUG',"Router Access List has {} records".format(len(rtrlst)))
log('TRACE', rtrlst)


toadd=[]
todel=[]
for row in rtrlst:
    
    found=False
    if row['address'] in srclst:
        found = True
    
    if not found:
        todel.append(row['.id'])
log('INFO', "{} records to delete".format(len(todel)))
log('TRACE', todel)

deleted= mk_removelistitem(config['endpoint'], todel)
if deleted['total'] >0:
  log('INFO', "{} records deleted".format(deleted['success']))

for line in srclst:
    found=False
    for item in rtrlst:
        if line == item['address']:
            found=True
            break
    if not found:
        toadd.append(line)
log('INFO', "{} records to add".format(len(toadd)))
log('TRACE', toadd)

added= mk_addlistaddress(config['endpoint'], args.AddressList, toadd)
if added['total'] >0:
  log('INFO', "{} records added".format(added['success']))

if (deleted['success'] == deleted['total']) and (added['success'] == added['total']):
    print("Address List \"{}\" updated".format(args.AddressList))
else:
    print("Errors ")