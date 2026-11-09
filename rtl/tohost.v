`timescale 1ns/1ps
// tohost.v -- pass/fail reporting at 0x1000_F000. LOCKED: do not modify.
//
// Connect `we` to "a store to 0x1000_F000 is happening this cycle" and `wdata`
// to the store data. Writing 1 means PASS; writing an odd value n means FAIL
// with code n >> 1 (for riscv-tests, the number of the failing test case).
//
// In simulation it prints the result and ends the run. In hardware it keeps the
// last value in `value` and raises `done`, so you can show it on the LEDs.

module tohost (
    input  wire        clk,
    input  wire        rst,
    input  wire        we,
    input  wire [31:0] wdata,
    output reg  [31:0] value,
    output reg         done
);
    always @(posedge clk) begin
        if (rst) begin
            value <= 32'd0;
            done  <= 1'b0;
        end else if (we) begin
            value <= wdata;
            done  <= 1'b1;
`ifndef SYNTHESIS
            if (wdata == 32'd1)
                $display("\n*** TOHOST: PASS");
            else
                $display("\n*** TOHOST: FAIL code=%0d (raw 0x%08h)", wdata >> 1, wdata);
            $finish;
`endif
        end
    end
endmodule
