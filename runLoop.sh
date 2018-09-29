#!/bin/bash

#campaign=Summer18
iIter=0
while(true)
do
    if((iIter % 20 == 0))
    then
        kinit -R
        cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o cookies/cookie.txt –krb
        cern-get-sso-cookie -u  https://cms-gwmsmon.cern.ch/prodview  -o cookies/cookieMon.txt –krb
        echo "cookies renwed"
    fi

    date
    hostname


    campaign=Fall18
    echo samples/${campaign}Temp.html
    ./getMCs.py $campaign | sed 's/Using sso-cookie file cookies\/cookie.txt//'  | tail -n +2 > samples/${campaign}Temp.html
    wc -l samples/${campaign}Temp.html
    #kinit -R
    #scp  samples/samplesNewTemp${campaign}.html  zlebcr@naf-cms.desy.de:~/www/samplesNew${campaign}.html
    #if Error while making a GET request
    size1=20
    size2=20
    nlines=10

    if  [ -f  samples/${campaign}Temp.html  ]; then
        size1=`grep -c "No JSON object could"  samples/${campaign}Temp.html `
        size2=`grep -c "Error while"  samples/${campaign}Temp.html `
        nlines=`wc -l  samples/${campaign}Temp.html | awk '{print $1}'`
    fi
    ((size=size1+size2))
    #if [  grep -q  "No JSON object could be decoded" samples/${campaign}Temp.html   -o $((size < 600))  ]
    echo Size is $size $nlines
    if [[ "$size" -lt "1" && "$nlines" -gt "550" ]]; then
        echo "OK, coppying"
        cp   samples/${campaign}Temp.html  samples/${campaign}.html
    else
        echo "problem"
    fi
    wc -l samples/${campaign}.html



    sleep 60
    ((++iIter))
done
