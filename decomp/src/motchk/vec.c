// ddrmotchkDll - vector store helpers

typedef unsigned int u32;
typedef float f32;

typedef struct {
    f32 x, y, z;
} Vec;

extern struct {
    u32 flags;
    u32 unk4;
    Vec vecA; // 0x8
    Vec vecB; // 0x14
} lbl_1_bss_1E8;

void fn_1_CA4(Vec *v) {
    lbl_1_bss_1E8.vecA = *v;
    lbl_1_bss_1E8.flags |= 1;
}

void fn_1_CE4(Vec *v) {
    lbl_1_bss_1E8.vecB = *v;
    lbl_1_bss_1E8.flags |= 1;
}
