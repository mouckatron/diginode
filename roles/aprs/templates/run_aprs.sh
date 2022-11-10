#!/bin/bash

# Drive level into rig. Adjust if neccessary to get the ALC meter on your rig at around 30%.
OUTPUT_VOL='59%'

echo 'Initiating direwolf TNC...';
AUDIOCARD=$(aplay -l |grep -i 'USB Audio CODEC' |grep -o 'card [0-9]*')
if [ "$(echo ${AUDIOCARD} |wc -l)" -lt "1" ]; then
  echo 'Problem detecting USB audio card. Is the device plugged in?';
  read -p 'Hit Enter or close this terminal window.' k; #TODO: Only show these prompts when launched from desktop
  echo 'Exiting.';
  exit
fi
CARDNUM=$(echo ${AUDIOCARD} |cut -d' ' -f2)
echo 'Setting appropriate output volume level. If you find this is not driving your rig at the';
echo 'right level (should be about 30% on your rigs ALC meter) use alsamixer to adjust accordingly.';
echo 'You can also edit the OUTPUT_VOL variable at the top of this script for future runs.';
amixer -c ${CARDNUM} set PCM ${OUTPUT_VOL} > /dev/null

amixer -c ${CARDNUM} sset Mic,0 capture 2 > /dev/null

sudo sed -i '/ADEVICE/d' direwolf.conf
echo "ADEVICE plughw:$CARDNUM,0" >> direwolf.conf

echo;

direwolf -p -c /etc/direwolf/direwolf.conf &

echo;
echo "Direwolf has launched.";
echo 'When finished, hit Enter or close this terminal window.';
read k;

echo 'Cleaning up...';
sudo killall direwolf;
