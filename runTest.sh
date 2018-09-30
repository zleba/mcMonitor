#!/bin/bash

#campaign=Summer18
#kinit -R
cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o cookies/cookie.txt –krb
cern-get-sso-cookie -u  https://cms-gwmsmon.cern.ch/prodview  -o cookies/cookieMon.txt –krb
echo "cookies renwed"
#campaign=Summer18
for campaign in Summer17 Fall17 Summer18 Fall18 
do
echo samples/${campaign}.html
./getMCs.py  $campaign | sed 's/Using sso-cookie file cookies\/cookie.txt//'  | tail -n +2 > samples/${campaign}.html
done
