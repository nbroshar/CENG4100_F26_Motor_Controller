# program.tcl -- load build/top.bit onto a Basys 3 connected over USB.
# Usage (from the repo root):
#   vivado -mode batch -source scripts/program.tcl
# Optional argument: a different .bit file.

set root [file normalize [file join [file dirname [info script]] ..]]
set bit  [file join $root build top.bit]
if {[llength $argv] > 0} { set bit [file normalize [lindex $argv 0]] }
if {![file exists $bit]} { error "Bitstream not found: $bit (run scripts/build.tcl first)" }

open_hw_manager
connect_hw_server
open_hw_target
set dev [lindex [get_hw_devices xc7a35t*] 0]
if {$dev eq ""} { error "No XC7A35T found. Is the Basys 3 plugged in and switched on?" }
current_hw_device $dev
refresh_hw_device -update_hw_probes false $dev
set_property PROGRAM.FILE $bit $dev
program_hw_devices $dev
puts "Programmed $dev with $bit"
close_hw_target
disconnect_hw_server
close_hw_manager
