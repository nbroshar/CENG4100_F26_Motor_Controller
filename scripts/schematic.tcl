# schematic.tcl -- draw the RTL schematic of one module and save it as a PDF.
#
# Run it in the Vivado window (not batch mode), with no project open
# (File > Close Project). In the Tcl Console at the bottom of the window:
#
#     cd {C:/Users/yourname/Documents/your-team-repo}
#     set top datapath
#     source scripts/schematic.tcl
#
# Change "datapath" to the module you want to see: alu, regfile, top, ...
# Run it again after you change the Verilog; it reloads every file.
#
# It reads every .v file in rtl/ and rtl/*/, elaborates the design without
# synthesizing it (you see adders, multiplexers and registers as written),
# opens the schematic and saves build/schematic/<top>.pdf.

if {![info exists top]} { set top datapath }
set part xc7a35tcpg236-1
set root [pwd]

set files [concat [glob -nocomplain [file join $root rtl *.v]] \
                  [glob -nocomplain [file join $root rtl * *.v]]]
if {[llength $files] == 0} {
    error "No Verilog found in [file join $root rtl]. cd to the repo folder first."
}

# Start clean, so running the script twice doesn't load files twice.
catch { close_design }
catch { close_project }

foreach f $files { read_verilog $f }

synth_design -rtl -top $top -part $part -name rtl_1

set out [file join $root build schematic]
file mkdir $out
set pdf [file join $out $top.pdf]
# Vivado opens the full schematic by itself after elaborating. Save that one;
# only if there's no schematic open, open one first.
if {[catch { write_schematic -force -format pdf -orientation landscape $pdf }]} {
    if {[catch { show_schematic [concat [get_cells] [get_ports]] } msg]} {
        puts "Could not open a schematic ($msg). Use Vivado's window, not batch mode."
        return
    }
    write_schematic -force -format pdf -orientation landscape $pdf
}
puts "Schematic of $top saved to $pdf"