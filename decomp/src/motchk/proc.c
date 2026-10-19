// ddrmotchkDll - process creation

typedef unsigned int u32;

extern void *fn_8000D780(void *func, u32 prio, u32 stackSize, int arg3, void *arg4);
extern void fn_8000E00C(void *proc, void *callback);

extern void *lbl_1_bss_0;
extern void *lbl_1_bss_248;

void fn_1_25E4(void);
void fn_1_2BA8(void);

void fn_1_2C64(void) {
    lbl_1_bss_0 = fn_8000D780(fn_1_25E4, 0x2001, 0x2000, 0, lbl_1_bss_248);
    fn_8000E00C(lbl_1_bss_0, fn_1_2BA8);
}
