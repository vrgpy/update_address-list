# update_address-list
Updates a Mikrotik RouterOS Access List based on a list of IP ranges

## Operation
The script reads a SourceFile containing a list of IP addresses/ranges and updates an Access List in a Mikrotik router.

The Access Lists is read and compared with the SourceFile and only the changes are applied to the router using the Mikrotik REST API.

### API
The Mikrotik REST API details are documented in Mikrotik Wiki
See: https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API


#### API Service
To enable the API access the router should have the www-ssl or www service enabled.
For production, only the www-ssl service is recommended.

#### User Permissions
The user used in the API call should have these allowed policies:
- read
- write
- api
- rest-api

This is configured in the user group definition in / System / Users / Groups /

### RouterOS v7
In winbox the Address Lists are configured in :
 - for IPv4 in: IP / Firewall / Address List
 - for IPv6 in: IPV6 / Firewall / Address List


### Usage
    usage: update_address-list [-h] [-i IPVer] [-c ConfigFile] [-v] SourceFile AddressList
    
    Updates a Mikrotik Router address-list based on a file containg a list of IP ranges
    
    positional arguments:
      SourceFile            file with IP addreses to load
      AddressList           name of the Address List
    
    options:
      -h, --help            show this help message and exit
      -i IPVer, --ipver IPVer
                            version of IP for the Address List. Default=4
      -c ConfigFile, --config ConfigFile
                            Specify configuration file. Default= ~/.update_address-list.json
      -v, --verbose         increase logging level
    
    Tested with Mikrotik RouterOS version 7.18.1


#### SourceFile
The sourcefile is a text file with one record per line. The addresses can be anything the ROS command "/ip/firewall/address-list/add" accept.


#### ConfigFile
By default the config file is stored in:  ~/.update_address-list.json
The content is a JSON formatted dictionary:

    { "endpoint":
      {
         "url":       "https://router.domain/rest",
         "tlsverify": "True",
         "username":  "api",
         "password":  "my-very-secure-password"
      }
    }

if you have a custom CA file that you can't add to your operating system, you can set the tlsverify parameter to the path to the certificate file.
Optionally you can set the tlsverify to "False" during develompent.
