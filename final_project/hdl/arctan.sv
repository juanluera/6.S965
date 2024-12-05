module arctan #
	(
		parameter integer C_S00_AXIS_TDATA_WIDTH	= 32,
		parameter integer C_M00_AXIS_TDATA_WIDTH	= 32,
        parameter integer ITERATIONS = 16
	)
	(
		// Ports of Axi Slave Bus Interface S00_AXIS
		input wire  s00_axis_aclk, s00_axis_aresetn,
		input wire  s00_axis_tlast, s00_axis_tvalid,
		input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
		input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1: 0] s00_axis_tstrb,
		output logic  s00_axis_tready,
 
		// Ports of Axi Master Bus Interface M00_AXIS
		input wire  m00_axis_aclk, m00_axis_aresetn,
		input wire  m00_axis_tready,
		output logic  m00_axis_tvalid, m00_axis_tlast,
		output logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
		output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb
	);
 
  logic m00_axis_tvalid_reg, m00_axis_tlast_reg;
  logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata_reg;
  logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb_reg;
 
  
  
  

   // PIPELINE stage registers 
  logic signed [(C_S00_AXIS_TDATA_WIDTH)-1:0] x_pipe [ITERATIONS-1:0];
  logic signed [(C_S00_AXIS_TDATA_WIDTH)-1:0] y_pipe [ITERATIONS-1:0];
  logic signed [(C_S00_AXIS_TDATA_WIDTH)-1:0] phase [ITERATIONS-1:0];
  logic [ITERATIONS-1:0] valid_pipe, tlast_pipe;
  logic [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] strobe_pipe [ITERATIONS-1:0];

  // stops deadlock + handshaking
  assign s00_axis_tready = m00_axis_tready || ~valid_pipe[0];
  assign m00_axis_tvalid = valid_pipe[ITERATIONS-1];
  assign m00_axis_tlast = tlast_pipe[ITERATIONS-1];
  assign m00_axis_tstrb = strobe_pipe[ITERATIONS-1];

  logic signed [(C_S00_AXIS_TDATA_WIDTH/2)-1:0] atan_lut [ITERATIONS-1:0];

  initial begin
        atan_lut[0]  = 'hC90F;  // atan(2^0)
        atan_lut[1]  = 'h76B1;  // atan(2^-1)
        atan_lut[2]  = 'h3EB6;  // atan(2^-2)
        atan_lut[3]  = 'h1FD5;  // atan(2^-3)
        atan_lut[4]  = 'h0FFA;  // atan(2^-4)
        atan_lut[5]  = 'h07FF;  // atan(2^-5)
        atan_lut[6]  = 'h03FF;  // atan(2^-6)
        atan_lut[7]  = 'h01FF;  // atan(2^-7)
        atan_lut[8]  = 'h00FF;  // atan(2^-8)
        atan_lut[9]  = 'h007F;  // atan(2^-9)
        atan_lut[10] = 'h003F;  // atan(2^-10)
        atan_lut[11] = 'h001F;  // atan(2^-11)
        atan_lut[12] = 'h000F;  // atan(2^-12)
        atan_lut[13] = 'h0007;  // atan(2^-13)
        atan_lut[14] = 'h0003;  // atan(2^-14)
        atan_lut[15] = 'h0001;  // atan(2^-15)
    end


  // Input stage
  wire signed [(C_S00_AXIS_TDATA_WIDTH/2)-1:0] x_in = s00_axis_tdata[(C_S00_AXIS_TDATA_WIDTH/2)-1: 0];
  wire signed [(C_S00_AXIS_TDATA_WIDTH/2)-1:0] y_in = s00_axis_tdata[C_S00_AXIS_TDATA_WIDTH-1:(C_S00_AXIS_TDATA_WIDTH/2)];

  // Output phase and radius
  assign m00_axis_tdata = phase[ITERATIONS-1];
  

 
  always_ff @(posedge s00_axis_aclk)begin
    if (s00_axis_aresetn==0)begin
      for (int i = 0; i <= ITERATIONS; i++) begin
                x_pipe[i] <= '0;
                y_pipe[i] <= '0;
                phase[i] <= '0;
                valid_pipe[i] <= 1'b0;
                strobe_pipe[i] <= '0;
                tlast_pipe[i] <= 1'b0;
      end
     
    end else begin
      //only if there is room in either our registers...
      //or downstream consumer/slave do we update.
      if (s00_axis_tready)begin

        // Input stage
        if (s00_axis_tvalid) begin
            x_pipe[0] <= x_in;
            y_pipe[0] <= y_in;
            phase[0] <= '0;
            valid_pipe[0] <= 1'b1;
            tlast_pipe[0] <= s00_axis_tlast;
            strobe_pipe[0] <= s00_axis_tstrb;
        end else begin
            valid_pipe[0] <= 1'b0;
            tlast_pipe[0] <= 1'b0;
            strobe_pipe[0] <= '0;
        end
        // Pipeline stage
        for (int i = 1; i < ITERATIONS; i++) begin
            if (valid_pipe[i-1]) begin
              if (y_pipe[i-1] >= 0) begin
                x_pipe[i] <= x_pipe[i-1] + (y_pipe[i-1] >>> i);
                y_pipe[i] <= y_pipe[i-1] - (x_pipe[i-1] >>> i);
                phase[i] <= phase[i-1] + atan_lut[i-1];
              end else begin
                x_pipe[i] <= x_pipe[i-1] - (y_pipe[i-1] >>> i);
                y_pipe[i] <= y_pipe[i-1] + (x_pipe[i-1] >>> i);
                phase[i] <= phase[i-1] - atan_lut[i-1];
              end
              valid_pipe[i] <= valid_pipe[i-1];
              strobe_pipe[i] <= strobe_pipe[i-1];
              tlast_pipe[i] <= tlast_pipe[i-1];
            end else begin
              valid_pipe[i] <= 0;
              strobe_pipe[i] <= 0;
              tlast_pipe[i] <= 0;
            end
            

        end
        // m00_axis_tvalid_reg <= s00_axis_tvalid;
        // m00_axis_tlast_reg <= s00_axis_tlast;
        // m00_axis_tdata_reg <= s00_axis_tdata;
        // m00_axis_tstrb_reg <= s00_axis_tstrb;
      end
    end
  end
endmodule