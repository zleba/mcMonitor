#!/bin/bash

#campaign=Summer18
#kinit -R
cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o cookies/cookie.txt –krb
cern-get-sso-cookie -u  https://cms-gwmsmon.cern.ch/prodview  -o cookies/cookieMon.txt –krb
echo "cookies renwed"
campaign=Fall18
echo samples/${campaign}Temp.html
./getMCs.py  $campaign | sed 's/Using sso-cookie file cookies\/cookie.txt//'  | tail -n +2 > samples/${campaign}.html
