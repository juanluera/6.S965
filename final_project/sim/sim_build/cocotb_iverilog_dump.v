module cocotb_iverilog_dump();
initial begin
    $dumpfile("/Users/j_luera/Documents/Angel Escuela/6.S965/final_project/sim/sim_build/arctan.fst");
    $dumpvars(0, arctan);
end
endmodule
