# build.tcl -- synthesize, implement and write a bitstream for the Basys 3.
#
# Usage (from the repo root):
#   vivado -mode batch -source scripts/build.tcl -tclargs sw/build/demo
# The argument is a folder holding the memory images for the program to bake
# into the bitstream (imem.mem + dmem.mem, or mem.mem). Default: sw/build/demo.
#
# Outputs:
#   build/top.bit                 bitstream
#   reports/utilization.rpt       post-route utilization
#   reports/utilization_hier.rpt  utilization per module
#   reports/timing.rpt            timing summary (10 worst paths)
#   reports/summary.txt           one-screen summary for RESOURCES.md

set root [file normalize [file join [file dirname [info script]] ..]]
set part xc7a35tcpg236-1

set prog_dir [file join $root sw build demo]
if {[llength $argv] > 0} { set prog_dir [file normalize [lindex $argv 0]] }

set work [file join $root build synth]
set rpt  [file join $root reports]
file mkdir $work $rpt

# Copy memory images next to the run so $readmemh("imem.mem", ...) finds them.
set mems {}
foreach m {imem.mem dmem.mem mem.mem} {
    set src [file join $prog_dir $m]
    if {[file exists $src]} {
        file copy -force $src [file join $work $m]
        lappend mems [file join $work $m]
    }
}
if {[llength $mems] == 0} {
    puts "WARNING: no memory images found in $prog_dir; memories will be empty."
}
cd $work

# Sources: every .v / .sv under rtl/
set vfiles [concat [glob -nocomplain [file join $root rtl *.v]] \
                   [glob -nocomplain [file join $root rtl * *.v]]]
set svfiles [concat [glob -nocomplain [file join $root rtl *.sv]] \
                    [glob -nocomplain [file join $root rtl * *.sv]]]
if {[llength $vfiles]}  { read_verilog $vfiles }
if {[llength $svfiles]} { read_verilog -sv $svfiles }
foreach m $mems { read_mem $m }
read_xdc [file join $root constraints basys3.xdc]

synth_design -top top -part $part
opt_design
place_design
route_design

report_utilization -file [file join $rpt utilization.rpt]
report_utilization -hierarchical -file [file join $rpt utilization_hier.rpt]
report_timing_summary -max_paths 10 -file [file join $rpt timing.rpt]
report_drc -file [file join $rpt drc.rpt]

# One-screen summary for the resource ledger, pulled from the utilization report.
set util [report_utilization -return_string]
proc util_used {text label} {
    # Matches table rows such as "| Slice LUTs | 1234 | 0 | ... | 20800 | 5.93 |"
    if {[regexp -line "^\\|\\s*${label}\\s*\\|\\s*(\[0-9.\]+)" $text -> used]} { return $used }
    return "n/a"
}
set wns "n/a"
set paths [get_timing_paths -max_paths 1 -nworst 1 -setup -quiet]
if {[llength $paths]} { set wns [get_property SLACK [lindex $paths 0]] }
set summary [join [list \
    "Program images : $prog_dir" \
    "Slice LUTs     : [util_used $util {Slice LUTs\*?}] / 20800" \
    "  LUT as memory: [util_used $util {LUT as Memory}]" \
    "Flip-flops     : [util_used $util {Slice Registers}] / 41600" \
    "BRAM tiles     : [util_used $util {Block RAM Tile}] / 50" \
    "DSPs           : [util_used $util {DSPs}] / 90" \
    "WNS (ns)       : $wns   (negative = timing NOT met at the constrained clock)" \
    "Full details   : reports/utilization.rpt, reports/timing.rpt"] "\n"]
set fh [open [file join $rpt summary.txt] w]
puts $fh $summary
close $fh
puts $summary

write_bitstream -force [file join $root build top.bit]
puts "Bitstream: [file join $root build top.bit]"
