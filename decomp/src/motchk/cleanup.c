// ddrmotchkDll - module cleanup

typedef unsigned int u32;

extern int fn_800CA3E4(void);
extern void fn_800CA40C(int arg0);

extern volatile u32 lbl_1_bss_8;
extern volatile u32 lbl_1_bss_10;

void fn_1_3060(void) {
    if (fn_800CA3E4() == 2) {
        fn_800CA40C(0);
    }
    lbl_1_bss_10 = 0;
    lbl_1_bss_8 = 0;
}
