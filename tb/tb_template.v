// tb_template.v -- pattern for a self-checking unit testbench.
// Copy to tb/tb_<module>.v, rename the module to tb_<module>, and run with:
//     python scripts/sim.py --tb tb_<module>
// The runner looks for "ALL TESTS PASSED" in the output.
// Add --vcd to record a waveform in build/sim/wave.vcd (keep the DUMP block
// below, with the module name changed to match).
//
// Rules for a good unit testbench:
//   1. Write the expected values yourself (from the RISC-V spec), BEFORE
//      asking the AI to generate the module or the test.
//   2. Every check compares against an expected value. No "eyeball the
//      waveform" tests.
//   3. Include edge cases: zero, -1, the most negative number, x0 as a
//      destination, shift amounts of 0 and 31.

`timescale 1ns/1ps

module tb_template;
    integer errors = 0;
    integer checks = 0;

`ifdef DUMP
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_template);
    end
`endif

    // Compare a 32-bit result against the expected value.
    task check32(input [255:0] name, input [31:0] got, input [31:0] expected);
        begin
            checks = checks + 1;
            if (got !== expected) begin
                errors = errors + 1;
                $display("FAIL %0s: got 0x%08h, expected 0x%08h", name, got, expected);
            end
        end
    endtask

    // Example device under test: replace with your module.
    reg  [31:0] a, b;
    wire [31:0] sum = a + b;

    initial begin
        a = 32'd2;          b = 32'd3;          #1; check32("2 + 3",        sum, 32'd5);
        a = 32'hFFFF_FFFF;  b = 32'd1;          #1; check32("-1 + 1 wraps", sum, 32'd0);
        a = 32'h7FFF_FFFF;  b = 32'd1;          #1; check32("overflow",     sum, 32'h8000_0000);

        if (errors == 0)
            $display("ALL TESTS PASSED (%0d checks)", checks);
        else
            $display("%0d of %0d CHECKS FAILED", errors, checks);
        $finish;
    end
endmodule
