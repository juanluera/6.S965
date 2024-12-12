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

  parameter int PI_15 = 102943;
 
  logic m00_axis_tvalid_reg, m00_axis_tlast_reg;
  logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata_reg;
  logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb_reg;

  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger0;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger1;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger2;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger3;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger4;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger5;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger6;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger7;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger8;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger9;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger10;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger11;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger12;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger13;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger14;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger15;

  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger00;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger1_0;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger20;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger30;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger40;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger50;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger60;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger70;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger80;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger90;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger100;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger110;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger120;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger130;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger140;
  // logic signed [C_M00_AXIS_TDATA_WIDTH-1 : 0] debugger150;
  

  
  

   // PIPELINE stage registers 
  logic signed [(C_S00_AXIS_TDATA_WIDTH/2)-1:0] x_pipe [ITERATIONS-1:0];
  logic signed [(C_S00_AXIS_TDATA_WIDTH/2)-1:0] y_pipe [ITERATIONS-1:0];
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
        atan_lut[0]  = 16'h6487;  // atan(2^0)
        atan_lut[1]  = 16'h3B58;  // atan(2^-1)
        atan_lut[2]  = 16'h1F5B;  // atan(2^-2)
        atan_lut[3]  = 16'h0FEA;  // atan(2^-3)
        atan_lut[4]  = 16'h07FD;  // atan(2^-4)
        atan_lut[5]  = 16'h03FF;  // atan(2^-5)
        atan_lut[6]  = 16'h01FF;  // atan(2^-6)
        atan_lut[7]  = 16'h00FF;  // atan(2^-7)
        atan_lut[8]  = 16'h007F;  // atan(2^-8)
        atan_lut[9]  = 16'h003F;  // atan(2^-9)
        atan_lut[10] = 16'h001F;  // atan(2^-10)
        atan_lut[11] = 16'h000F;  // atan(2^-11)
        atan_lut[12] = 16'h0007;  // atan(2^-12)
        atan_lut[13] = 16'h0003;  // atan(2^-13)
        atan_lut[14] = 16'h0001;  // atan(2^-14)
        atan_lut[15] = 16'h0000;  // atan(2^-15)
    end

  // assign debugger0 = phase[0];
  // assign debugger1 = phase[1];
  // assign debugger2 = phase[2];
  // assign debugger3 = phase[3];
  // assign debugger4 = phase[4];
  // assign debugger5 = phase[5];
  // assign debugger6 = phase[6];
  // assign debugger7 = phase[7];
  // assign debugger8 = phase[8];
  // assign debugger9 = phase[9];
  // assign debugger10 = phase[10];
  // assign debugger11 = phase[11];
  // assign debugger12 = phase[12];
  // assign debugger13 = phase[13];
  // assign debugger14 = phase[14];
  // assign debugger15 = phase[15];

  // assign debugger00 = y_pipe[0];
  // assign debugger1_0 = y_pipe[1];
  // assign debugger20 = y_pipe[2];
  // assign debugger30 = y_pipe[3];
  // assign debugger40 = y_pipe[4];
  // assign debugger50 = y_pipe[5];
  // assign debugger60 = y_pipe[6];
  // assign debugger70 = y_pipe[7];
  // assign debugger80 = y_pipe[8];
  // assign debugger90 = y_pipe[9];
  // assign debugger100 = y_pipe[10];
  // assign debugger110 = y_pipe[11];
  // assign debugger120 = y_pipe[12];
  // assign debugger130 = y_pipe[13];
  // assign debugger140 = y_pipe[14];
  // assign debugger150 = y_pipe[15];
  

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
            if ((x_in < 0 ) && (y_in< 0)) begin
              x_pipe[0] <= -x_in;
              y_pipe[0] <= -y_in;
              phase[0] <= -PI_15;
            end else if ((x_in < 0 ) && (y_in >= 0)) begin
              x_pipe[0] <= -x_in;
              y_pipe[0] <= -y_in;
              phase[0] <= PI_15;
            end else begin
              x_pipe[0] <= x_in;
              y_pipe[0] <= y_in;
              phase[0] <= '0;
            end
            
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
                x_pipe[i] <= x_pipe[i-1] + (y_pipe[i-1] >>> i-1);
                y_pipe[i] <= y_pipe[i-1] - (x_pipe[i-1] >>> i-1);
                phase[i] <= phase[i-1] + atan_lut[i-1];
              end else begin
                x_pipe[i] <= x_pipe[i-1] - (y_pipe[i-1] >>> i-1);
                y_pipe[i] <= y_pipe[i-1] + (x_pipe[i-1] >>> i-1);
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