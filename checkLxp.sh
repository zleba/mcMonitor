#for i in $(seq -f "%04g" 1 500); do
# ssh -o ConnectTimeout=10 -o PreferredAuthentications=gssapi-with-mic,gssapi -o GSSAPIAuthentication=yes -o StrictHostKeyChecking=no -o LogLevel=quiet lxplus$i.cern.ch "(screen -list | head -1 | grep -q 'There is a screen on') && hostname && screen -list"
#done

for i in `seq -w  800`
do
    ssh -o "StrictHostKeyChecking no" -T lxplus$i "screen -list" & 
done
wait
