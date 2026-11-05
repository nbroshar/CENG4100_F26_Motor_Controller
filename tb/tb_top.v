// tb_top.v -- system testbench for the locked `top` module.
// Owned by the Verification role. Used by scripts/sim.py for riscv-tests and
// C programs. It:
//   - drives the 100 MHz clock and holds btnC (reset) for 20 cycles,
//   - prints every byte the design sends on RsTx (115200 baud, 8N1),
//   - optionally sends the bytes of uart_in.txt on RsRx, as if typed,
//   - stops after +max_cycles=N clock cycles (default 2,000,000).
// The run normally ends when the design writes to tohost (rtl/tohost.v).

`timescale 1ns/1ps

module tb_top;
    reg         clk  = 1'b0;
    reg         btnC = 1'b1;
    reg         btnU = 1'b0, btnL = 1'b0, btnR = 1'b0, btnD = 1'b0;
    reg  [15:0] sw   = 16'h0000;
    reg         RsRx = 1'b1;
    wire [15:0] led;
    wire [6:0]  seg;
    wire        dp;
    wire [3:0]  an;
    wire        RsTx;

    top dut (
        .clk(clk), .btnC(btnC), .btnU(btnU), .btnL(btnL), .btnR(btnR), .btnD(btnD),
        .sw(sw), .led(led), .seg(seg), .dp(dp), .an(an), .RsRx(RsRx), .RsTx(RsTx)
    );

    always #5 clk = ~clk;   // 100 MHz

`ifdef DUMP
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_top);
    end
`endif

    // Reset, then a cycle limit so a hung design cannot run forever.
    integer max_cycles;
    integer cycle = 0;
    initial begin
        if (!$value$plusargs("max_cycles=%d", max_cycles))
            max_cycles = 2000000;
        repeat (20) @(posedge clk);
        btnC = 1'b0;
    end
    always @(posedge clk) begin
        cycle = cycle + 1;
        if (cycle >= max_cycles) begin
            $display("\n*** TIMEOUT after %0d cycles (no write to tohost)", cycle);
            $finish;
        end
    end

    // UART monitor: decode RsTx and print characters.
    localparam real BIT_NS = 1.0e9 / 115200.0;
    reg [7:0] rx_char;
    integer   b;
    initial begin
        wait (btnC == 1'b0);
        forever begin
            @(negedge RsTx);
            #(BIT_NS * 1.5);
            for (b = 0; b < 8; b = b + 1) begin
                rx_char[b] = RsTx;
                #(BIT_NS);
            end
            $write("%c", rx_char);
            $fflush;
        end
    end

    // UART driver: if uart_in.txt exists, type its bytes into RsRx.
    // Like a person at a terminal, it waits until the design has stopped
    // transmitting (RsTx idle for 20 bit times) before each keystroke, so a
    // one-byte receive buffer is never overrun by the test bench itself.
    localparam integer IDLE_CYCLES = 20 * 868;
    integer fd, ch, k, idle;
    task wait_tx_quiet;
        begin
            idle = 0;
            while (idle < IDLE_CYCLES) begin
                @(posedge clk);
                idle = RsTx ? idle + 1 : 0;
            end
        end
    endtask
    initial begin
        fd = $fopen("uart_in.txt", "r");
        if (fd != 0) begin
            wait (btnC == 1'b0);
            ch = $fgetc(fd);
            while (ch != -1) begin
                wait_tx_quiet;
                RsRx = 1'b0;                   // start bit
                #(BIT_NS);
                for (k = 0; k < 8; k = k + 1) begin
                    RsRx = ch[k];
                    #(BIT_NS);
                end
                RsRx = 1'b1;                   // stop bit
                #(BIT_NS);
                ch = $fgetc(fd);
            end
            $fclose(fd);
        end
    end
endmodule
