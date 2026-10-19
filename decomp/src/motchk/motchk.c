// ddrmotchkDll - motion-check module: main task + helpers

typedef unsigned char u8;
typedef short s16;
typedef unsigned int u32;
typedef float f32;

typedef struct {
    f32 x, y, z;
} Vec;

// DOL (Hudson engine) imports
extern void fn_8005F5A0(void);
extern void fn_800450F8(int arg0, int arg1, int arg2);
extern u8 fn_80045374(void);
extern void HuPrcSleep(void);
extern int fn_800CA3E4(void);
extern void fn_800CA40C(int arg0);
extern void fn_80039DAC(int arg0, int arg1);
extern void fn_8000DAB4(void *ptr);
extern volatile s16 lbl_80191592;

extern void *lbl_1_bss_248;

void fn_1_798(void) {
    fn_8005F5A0();
}

void fn_1_7B8(void) {
    fn_800450F8(1, 0, 10);
    while (fn_80045374() != 0) {
        HuPrcSleep();
    }
    while (*(volatile s16 *)&lbl_80191592 == 0) {
        HuPrcSleep();
    }
    fn_800450F8(2, 0, 10);
    while (fn_80045374() != 0) {
        HuPrcSleep();
    }
    if (fn_800CA3E4() == 2) {
        fn_800CA40C(100);
    }
    fn_80039DAC(1, 1);
    fn_8000DAB4(lbl_1_bss_248);
    for (;;) {
        HuPrcSleep();
    }
}
