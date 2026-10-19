// ddrmotchkDll - module init (called from REL _prolog)

typedef unsigned int u32;

extern void *fn_8003A080(int arg0, u32 size);
extern void fn_8005A5AC(void *ptr);
extern void *fn_8003A32C(void *arg0, int arg1, int arg2, int arg3, int arg4, void *func);
extern void *fn_8000D780(void *func, u32 prio, u32 stackSize, int arg3, void *arg4);
extern void fn_80025270(int arg0, int arg1, int arg2);

extern void *lbl_1_bss_248;

void fn_1_1A0(void);
void fn_1_798(void);
void fn_1_7B8(void);
void fn_1_868(void);
void fn_1_1270(void);

void fn_1_A0(void) {
    void *ret;

    lbl_1_bss_248 = fn_8003A080(2, 0x2000);
    fn_8005A5AC(lbl_1_bss_248);
    ret = fn_8003A32C(lbl_1_bss_248, 2, 0, 0, -1, fn_1_1A0);
    ret = fn_8003A32C(lbl_1_bss_248, 1, 0, 0, -1, fn_1_798);
    fn_8000D780(fn_1_7B8, 0x2003, 0x1000, 0, lbl_1_bss_248);
    fn_8000D780(fn_1_1270, 0x2002, 0x3000, 0, lbl_1_bss_248);
    fn_80025270(0, 0, 0);
    fn_1_868();
}
