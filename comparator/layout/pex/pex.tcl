gds read /foss/designs/comparator/layout/strongarm.gds
load strongarm
select top cell
extract path .
extract all
ext2spice lvs
ext2spice cthresh 0.005
ext2spice -o strongarm_pex.spice
quit -noprompt
