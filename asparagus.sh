#!/bin/sh
# bot wrapper
this_dir="$(dirname "$0")"
cd "$this_dir" || exit 2

exec 1>>bot_output.log
exec 2>&1

relaunch_counter=0
while [ "$relaunch_counter" -lt 10 ] ; do
    relaunch_counter=$((1 + relaunch_counter))
    /usr/bin/env python3 ./asparagus.py
    sleep 5
done
exit 1