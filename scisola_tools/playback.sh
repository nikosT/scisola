
#!/bin/bash

# a simple script/skeleton for playback mini-seeds back to seedlink service, in order to calculate MTs for past events
# msrepack can be downloaded and installed from https://ds.iris.edu/ds/nodes/dmc/software/downloads/libmseed/

# create "stream.lst"
# example
# 2014-06-25 09:20:00;2014-06-25 09:30:00;*.*..???

# creates one multiplexed mseed file
scart -dv --list stream.lst /home/sysop/seiscomp3/acquisition/archive > all.mseed

# repack to 512 sectors
msrepack -a -R 512 -o tmp.mseed all.mseed

# sort by time (in order to run seedlink playback)
scmssort -E tmp.mseed > all.mseed.sorted

# seicomp3 gui (scconfig)
# module -> seedlink -> enable msrtsimul
# save and restart

# rename in case you want to restore the buffer
# or 
# delete /home/sysop/seiscomp3/var/lib/seedlink/buffer folder
# in order to flush seedlink ringbuffer
mv  /home/sysop/seiscomp3/var/lib/seedlink/buffer  /home/sysop/seiscomp3/var/lib/seedlink/buffer_old
# or
rm -rf /home/sysop/seiscomp3/var/lib/seedlink/buffer

# "historic" keeps date-time of mseed file
# "s" 10000 speeds up putting miniseed to seedlink ringbuffer
/home/sysop/seiscomp3/bin/seiscomp exec msrtsimul -m historic -s 10000 all.mseed.sorted
