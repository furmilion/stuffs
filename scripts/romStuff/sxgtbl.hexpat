#define get import
get std.io;
get std.core;
#define lshift <<
#define rshift >>
#define and &
#define or |
#define xor ^
#define less <
#define greater >
fn print(auto x, auto y) { std::print(x, y); };
struct TableType {
    u8 type;
    bool isEmbedded = type & 128;
    bool isEncrypted = type & 1;
};
struct Bank {
    char name[16];
    TableType tableType @ 31;
    if (tableType.isEmbedded) {
        u32 enbeddedTableOffset;
        u32 embeddedTableSize;
    } else { char fileName[15]; }
    u8   type;
    u32 dru_prg_map[4];
    
} ;

Bank bank @ 0;