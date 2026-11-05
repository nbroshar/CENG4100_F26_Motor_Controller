// top.v -- board wrapper for the CENG 4100 RV32I capstone.
//
// LOCKED: the module name and port list must not change. They match
// constraints/basys3.xdc and tb/tb_top.v, so every team's design runs the same
// tests. Everything inside the module is yours: Core fills it in as the design
// grows (Lab 2 onward).
//
// What goes in here (teams fill this in as decisions are made):
//   - reset synchronizer for btnC (active high)
//   - clocking (D12): clock enable or MMCM
//   - the core, memories (D2, D3, D4) and peripherals, each in its own file
//     under rtl/ (at most one level of subfolders: scripts/build.tcl reads
//     rtl/*.v and rtl/*/*.v only)
//   - address decode per docs/memory_map.md
//   - the tohost module (rtl/tohost.v) at 0x1000_F000
//
// Memory images: load them by plain file name, e.g.
//   initial $readmemh("imem.mem", imem);
// scripts/sim.py and scripts/build.tcl copy the right images into the working
// directory before simulation and synthesis.

module top (
    input  wire        clk,     // 100 MHz
    input  wire        btnC,    // reset (active high); also BTN bit 0
    input  wire        btnU,    // BTN bit 4
    input  wire        btnL,    // BTN bit 3
    input  wire        btnR,    // BTN bit 2
    input  wire        btnD,    // BTN bit 1
    input  wire [15:0] sw,
    output wire [15:0] led,
    output wire [6:0]  seg,     // active low
    output wire        dp,      // active low, held off
    output wire [3:0]  an,      // active low
    input  wire        RsRx,    // UART receive (from PC)
    output wire        RsTx     // UART transmit (to PC)
);

    // Placeholder outputs so the empty design builds. Replace as you go.
    assign led  = 16'h0000;
    assign seg  = 7'h7F;
    assign dp   = 1'b1;
    assign an   = 4'hF;
    assign RsTx = 1'b1;          // UART idle is high

endmodule
