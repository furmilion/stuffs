import std.io;
import std.core;
#define lshift <<
#define rshift >>
#define and &
#define or |
#define xor ^
#define less <
#define greater >

#define PRINT_OUTPUT

// Chip types
//#define MPCM
str PCM_TYPES_NAMES[4] = {"8-bit", "12-bit", "invalid", "invalid"};
enum PCM_TYPES : u8 {
    PCM_8BIT,
    PCM_12BIT,
    PCM_INVALID,
    PCM_INVALID
};
#define MU5
#ifdef MU5
#define SAMPLE_COUNT 512
#endif

//std::print("e {}",std::core::get_endian());
std::core::set_endian(1);
//std::print("e {}",std::core::get_endian());

/*
fn byteswap(u128 x) {
    u8   size   = sizeof(x);
    u128 og     = u128(x);
    u128 new    = 0;
    std::print("input size       {:}", size);
    std::print("input num        {:}", x) ;
    std::print("input num casted {:}", og);
    for (u8 byte = 0, byte < size, u8 shart) {
        std::print("{}", byte);
        new or= (og >> (size - byte));
        byte++;
    }
    return new;
};
*/

fn pow2(u32 x) {
    if (x less 1) { return 1; }
    else if (x == 1) { return 2; }
    else { return 2 lshift x; }
};

struct SampleData {
    u24 sample_length = parent.sample_length xor 65535 [[comment("Sample length (samples)"), name("Sample length (samples)")]];
    //u24 dat_len;
    if (parent.sample_fmt == PCM_TYPES::PCM_8BIT) {
        u16 dat_len = sample_length;
    }
    else if (parent.sample_fmt == PCM_TYPES::PCM_12BIT) {
        //u24 dat_len = (sample_length * 3)/2;
        u24 dat_len = sample_length * 1.5;
    }/*
    else if (parent.sample_fmt == PCM_TYPES::PCM_16BIT) {
        dat_len = sample_length * 2;
    }*/
    else if (parent.sample_fmt == PCM_TYPES::PCM_INVALID) {
        u24 dat_len = 1;
    }
    
    #ifdef PRINT_OUTPUT
    std::print("========== INSTRUMENT ==========");
    std::print("Sample start:       {}", parent.sample_start);
    std::print("Sample bytelength:  {}", dat_len);
    std::print("Sample length:      {}", parent.sample_length xor 65535);
    std::print("Sample end:         {}", parent.sample_start + sample_length);
    std::print("Sample loop start:  {}", parent.sample_loop_start);
    std::print("Format:             {}", PCM_TYPES_NAMES[parent.sample_fmt]);
    std::print("Attack rate:        {}", (parent.inst_ad1 lshift 4) and 4);
    std::print("Decay 1 rate:       {}", parent.inst_ad1 and 4);
    std::print("Sustain level:      {}", parent.inst_ad1 and 4);
    std::print("Decay 2 rate:       {}", parent.inst_ad1 lshift 4);
    std::print("Release rate:       {}", parent.inst_ad1 lshift 4);
    std::print("Rate correction:    {}", parent.inst_ad1 and 4);
    std::print("LFO speed:          {}", parent.inst_vib_str_and_lfo_spd and 3);
    std::print("Vibrato strength:   {}", parent.inst_vib_str_and_lfo_spd lshift 3);
    std::print("AM strength:        {}", parent.inst_am_str and 3);
    std::print("");
    #endif
    
    u8 data[dat_len];
};

struct Instrument {
  u24 sample_start_and_fmt    [[comment("Sample start and Sample format"), name("Sample start and Sample format")]];
  u16 sample_loop_start       [[comment("Sample loop point start"),        name("Sample loop point start")       ]];
  u16 sample_length           [[comment("Sample length"),                  name("Sample length")                 ]];
  u8 inst_vib_str_and_lfo_spd [[comment("Vibrato strength and LFO speed"), name("Vibrato strength and LFO speed")]];
  u8 inst_ad1                 [[comment("Attack and Decay 1"),             name("Attack and Decay 1")            ]];
  u8 inst_d2s                 [[comment("Decay 2 and Sustain level"),      name("Decay 2 and Sustain level")     ]];
  u8 inst_rrc                 [[comment("Release and Rate correction"),    name("Release and Rate correction")   ]];
  u8 inst_am_str              [[comment("Amplitude modulation strength"),  name("Amplitude modulation strength") ]];
  
  #ifdef MU5
  u24 sample_start = sample_start_and_fmt and 0x1FFFFF   [[comment("Sample start"),  name("Sample start") ]]; // mu5 uses only 21 address pins
  #endif
  #ifndef MU5
  u24 sample_start = sample_start_and_fmt and 0x3FFFFF   [[comment("Sample start"),  name("Sample start") ]];
  #endif
  
  u8 sample_fmt = (sample_start_and_fmt lshift 22) and 3 [[comment("Sample format"), name("Sample format")]];
  
  if ((sample_start + (65535 xor sample_length)) greater pow2(22)) {
    sample_start = 0;
    sample_length = 65535;
  }
  
  if (sample_start greater pow2(22)) {
    sample_start = 0;
    sample_length = 65535;
  }
  
  SampleData sample @ sample_start;
    
};

struct InstTable {
};

struct MultiPCMBank {
    u24 table_start [[comment("Instrument Table and Sample format"), name("Instrument Table and Sample format")]]; //  3/12
    u16 pad1        [[comment("Padding"), name("Padding")]];                                                       //  5/12
    u16 table_len   [[comment("Table length"), name("Table length")]];                                                                                                //  7/12
    u24 pad2        [[comment("Padding"), name("Padding")]];                                                       // 10/12
    u16 pad3        [[comment("Padding"), name("Padding")]];                                                       // 12/12
    u16 table_len_ = table_len xor 0xFFFF [[comment("Table length (actual)"), name("Table length (actual)")]];
    std::print("table len {:}", table_len);
    std::print("table len xord {:}", table_len_);
    std::print("insts {:}", table_len_/12);
    std::print("sizeof {:}", sizeof(table_len_));
    Instrument instruments[(table_len_/12) - 1];
};
#ifndef SAMPLE_COUNT
MultiPCMBank bank @ 0;
#endif
#ifdef SAMPLE_COUNT
Instrument instruments[SAMPLE_COUNT] @ 0;
#endif