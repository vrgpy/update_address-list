# update_address-list
Updates a Mikrotik RouterOS Access List based on a list of IP ranges


#### API
The API details are documented in Mikrotik Wiki
See: https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API

#### RouterOS v7
In RouterOS the Address lists are detailed :
 - for IPv4 in: IP/ Firewall / Address List
 - for IPv6 in IPV6 / Firewall
   / Address List

#### Credentials
By default the credentials are stored in:  ~/.update_address-list.json

    { "endpoint":
      {
         "url":       "https://router.domain/rest",
         "username":  "api",
         "password":  "my-very-secure-password"
      }
    }



#### Usage

    usage: update_address-list [-h] [-i IPVER] [-r ROUTER] [-v] SourceFile AddressList
    
    Updates a Mikrotik Router address-list based on a file containg a list of IP addreses
    
    positional arguments:
      SourceFile            file with IP addreses to load
      AddressList           name of the Address List
    
    options:
      -h, --help            show this help message and exit
      -i IPVER, --ipver IPVER
                            version of IP for the Address List. Default=4
      -r ROUTER, --router ROUTER
                            Specify Router API endpoint
      -v, --verbose         increase logging level
    
    Tested with Mikrotik RouterOS version 7.18.1

