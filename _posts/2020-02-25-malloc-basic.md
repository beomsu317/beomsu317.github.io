---
title: Malloc Basic
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, malloc]
math: true
mermaid: true
---
## Arena

`malloc()`에서 메모리 영역과 메모리 관리 부분을 arena라고 한다.

### Main Arena

malloc.c 에서 `struct malloc_state` 구조체를 사용하는 변수이다.

```c
static struct malloc_state main_arena =
{
  .mutex = _LIBC_LOCK_INITIALIZER,
  .next = &main_arena,
  .attached_threads = 1
};
```

### malloc_state 구조체

할당된 chunk들을 관리하는 구조체이다.

```c
struct malloc_state
{
  /* Serialize access.  */
  mutex_t mutex;

  /* Flags (formerly in max_fast).  */
  int flags;

  /* Fastbins */
  mfastbinptr fastbinsY[NFASTBINS];

  /* Base of the topmost chunk -- not otherwise kept in a bin */
  mchunkptr top;

  /* The remainder from the most recent split of a small request */
  mchunkptr last_remainder;

  /* Normal bins packed as described above */
  mchunkptr bins[NBINS * 2 - 2];

  /* Bitmap of bins */
  unsigned int binmap[BINMAPSIZE];

  /* Linked list */
  struct malloc_state *next;

  /* Linked list for free arenas.  Access to this field is serialized
    by free_list_lock in arena.c.  */
  struct malloc_state *next_free;

  /* Number of threads attached to this arena.  0 if the arena is on
    the free list.  Access to this field is serialized by
    free_list_lock in arena.c.  */
  INTERNAL_SIZE_T attached_threads;

  /* Memory allocated from the system in this arena.  */
  INTERNAL_SIZE_T system_mem;
  INTERNAL_SIZE_T max_system_mem;
};
```

## Chunk

### Chunk Type

1. allocated chunk
2. free chunk
3. top chunk
4. last remainder chunk

allocated, free chunk는 `malloc_chunk` 구조체를 이용해 필요한 정보를 저장한다.

```c
/*
  -----------------------  Chunk representations -----------------------
*/

/*
  This struct declaration is misleading (but accurate and necessary).
  It declares a "view" into memory allowing access to necessary
  fields at known offsets from a given base. See explanation below.
*/

struct malloc_chunk {
  INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
  INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */

  struct malloc_chunk* fd;         /* double links -- used only if free. */
  struct malloc_chunk* bk;

  /* Only used for large blocks: pointer to next larger size.  */
  struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
  struct malloc_chunk* bk_nextsize;
};
```

### Allocated Chunk

**allocated 최소 크기**

- 32 bit : 16 byte
- 64 bit : 32 byte
- prev_size : 이전 chunk가 해제되면, 이 필드에 이전 chunk의 크기가 저장된다. 이전 chunk가 할당되면, 이 필드에 이전 chunk의 사용자 데이터가 저장된다.
- size : 이 필드는 Allocated chunk의 크기를 저장하며, 필드의 맨 끝 3Bit는 flag 정보
- PREV_INUSE[P] : 이 비트는 이전 chunk가 할당되면 설정
- IS_MMAPPED[M] : 이 비트는 현재 chunk가 mmap을 통해 할당되면 설정
- NON_MAIN_ARENA[A] : 이 비트는 현재 chunk가 thread arena에 위치되면 설정

```c
// Allocated chunk
#include <stdio.h>
#include <stdlib.h>
 
void main(){
    char *heap = malloc(8);
    printf("Heap Addr : %p\n",heap);
    free(heap);
}
```

```
gdb-peda$ vmmap
Start              End                Perm  Name
...
0x00602000         0x00623000         rw-p  [heap]
...
gdb-peda$ x/24gx 0x00602000
0x602000:   0x0000000000000000                    0x0000000000000021 <- header(16 byte)
0x602010:   0x0000000000000000 <- user data(8 byte)   0x0000000000000000 <- Next chunk(8 byte)
0x602020:   0x0000000000000000                        0x0000000000020fe1
```

|Chunk|Size of Chunk|
|:---:|:---:|
|fast chunk|32 bit(16 ~ 64 byte), 64 bit(32 ~ 128 byte)|
|small chunk|Size of User Data < 512 byte|
|large chunk|Size of User Data >= 512 byte|

### Free Chunk

- prev_size : free chunk는 연속으로 붙어 있을 수 없다. 각 청크를 해제하는 경우 하나의 단일 free chunk로 결합되어 항상 해제된 chunk의 이전 청크를 할당하고 있어 prev_size는 이전 청크의 사용자 데이터를 저장하고 있음
- size : Free chunk의 크기를 저장한다. 필드의 맨 끝 3Bit는 flag 정보
- fd(forward pointer): 동일한 Bin의 다음 Free Chunk Address 저장
- bk(backward pointer): 동일한 Bin의 이전 Free Chunk Address 저장

```c
#include <stdio.h>
#include <stdlib.h>
 
void main(){
        char *heap1 = malloc(128);
        char *tmp2 = malloc(8);
        char *heap2 = malloc(128);
        char *tmp3 = malloc(8);
        char *heap3 = malloc(128);
        char *tmp1 = malloc(8);
 
        printf("Free chunk : %p\n",heap2);
        free(heap1);
        free(heap2);
        free(heap3);
        getchar();
}
```

```
gdb-peda$ r
Starting program: /root/pwnable/malloc/free 
Free chunk : 0x6020c0
^C
Program received signal SIGINT, Interrupt.
gdb-peda$ x/24gx 0x6020c0-0x10
0x6020b0:   0x0000000000000000                  0x0000000000000091 <- header(16 byte) header(16) + heap_size(128) + PREV_INUSE(1) = 0x91
0x6020c0:   0x0000000000602000 <- fk(heap1)     0x0000000000602160 <- bk(heap2) 
0x6020d0:   0x0000000000000000                  0x0000000000000000
...
```

### Top Chunk

top chunk는 arena의 가장 상위 영역에 있는 chunk이다. top chunk는 bin에 포함되지 않는다. top chunk는 PREV_INUSE flag가 설정된다. top chunk의 크기가 사용자가 요청한 크기보다 큰 경우 top chunk는 2개로 분리된다.

- user chunk(사용자가 요청한 크기)
- remainder chunk(나머지 크기)

reamiander chunk는 새로운 top chunk가 된다. top chunk의 크기가 사용자가 요청한 크기보다 작은 경우 syscall을 사용하여 top chunk의 크기를 증가시킨다.

- sbrk(main arena)
- mmap(thread arena)

## Bin

free로 해제된 chunk들을 관리하기 위한 연결리스트, 해제된 chunk의 크기에 따라 분류하여 관리된다.

- fast bin : free chunk는 서로 인접해 있어도 하나의 단일 free chunk로 병합되지 않음
- small, large bin : 2개의 free chunk는 서로 인접할 수 없고, free chunk가 서로 인접할 경우 단일 free chunk로 병합됨

|Bins|Fast Bin|Small Bin|Large Bin|Unsorted Bin|
|:---:|:---:|:---:|:---:|:---:|
|Chunk Type|Fast Chunk|Small Chunk|Large Chunk|Small, Large Chunk|
|Sizeo of Chunk|16 ~ 80 byte|512 byte 이하|512 byte 이상|제한 없음(Free Chunk만 가능)|
|Bin Number|10|62|63|1|

### malloc_state

- fastbinsY : `fast bin`을 관리
- bins : `unsorted bin`, `small bin`, `large bin`을 관리(총 126개의 bin)
    1. index 1 : unsorted bin
    2. index 2 ~ 63 : small bin
    3. index 64 ~ 126 : large bin

### Fast Bin

LIFO 방식이며 10개의 bin을 사용한다. 해제된 fast chunk를 보관하고 single-linked list로 관리된다. bin은 fast bin이 처리하는 메모리의 최대 크기 "global_max_fast"에 의해 결정된다. * 32bit : 최소 크기 16 byte 부터 24, 32, 40, 48, 56, 64 byte 까지 * 64 bit : 최소 크기 32 byte 부터 48, 64, 80, 96, 112, 128 byte 까지

```c
#include <stdio.h>
#include <stdlib.h>

void main(){
        char *heap = malloc(0x10);
        char *heap1 = malloc(0x20);
        char *heap2 = malloc(0x30);
        char *heap3 = malloc(0x40);
        char *heap4 = malloc(0x50);
        char *heap5 = malloc(0x60);
        char *heap6 = malloc(0x70);

        printf("Heap Addr : %p\n",heap);
        printf("Heap Addr : %p\n",heap1);
        printf("Heap Addr : %p\n",heap2);
        printf("Heap Addr : %p\n",heap3);
        printf("Heap Addr : %p\n",heap4);
        printf("Heap Addr : %p\n",heap5);
        printf("Heap Addr : %p\n",heap6);

        free(heap);
        free(heap1);
        free(heap2);
        free(heap3);
        free(heap4);
        free(heap5);
        free(heap6);
}
```

```
Starting program: /root/pwnable/malloc/fastbin 
Heap Addr : 0x602010
Heap Addr : 0x602030
Heap Addr : 0x602060
Heap Addr : 0x6020a0
Heap Addr : 0x6020f0
Heap Addr : 0x602150
Heap Addr : 0x6021c0
...
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x602000 --> 0x0
(0x30)     fastbin[1]: 0x602020 --> 0x0
(0x40)     fastbin[2]: 0x602050 --> 0x0
(0x50)     fastbin[3]: 0x602090 --> 0x0
(0x60)     fastbin[4]: 0x6020e0 --> 0x0
(0x70)     fastbin[5]: 0x602140 --> 0x0
(0x80)     fastbin[6]: 0x6021b0 --> 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x602640 (size : 0x209c0) 
       last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

### Small Bin

FIFO 방식이며 62개의 bin을 가지고 있다. 해제된 small chunk를 보관하며 doubly-linked list이다. 512byte 미만의 크기를 가지는 chunk를 위한 bin이다. 최소 크기 16 byte 부터 24, 32, 48, … 504 byte 까지 총 62개의 bin을 가지고 있다. 2개의 free chunk가 서로 인접해 있을 수 없고 2개의 free chunk가 인접할 경우 하나의 free chunk로 병합된다.

32bit 시스템은 MALLOC_ALIGNMENT는 8이고, SIZE_SZ는 4이다. * MIN_LARGE_SIZE는 512((64 - 0) * 8)이다.

64bit 시스템은 MALLOC_ALIGNMENT는 16이고,SIZE_SZ는 8이다. * MIN_LARGE_SIZE는 1024((64 * 0) * 16)이다.

즉, 32bit 시스템에서 small bin의 범위는 16~504byte(64*8-8)이며 64bit에서는 32~1008byte이다.

### Large Bin

63개의 bin을 가지며 해제된 large chunk를 보관한다. doubly-linked list구조로 되어 있다. 512byte 이상의 크기를 가지는 chunk를 위한 bin이며 다양한 크기의 chunk가 저장되기 때문에 bin 내부에서 적당한 크기의 chunk를 찾기 쉽도록 내림차순으로 정렬하여 저장한다. 가장 앞쪽이 가장 큰 chunk, 가장 뒤쪽이 가장 작은 chunk이다. fd_nextsize와 bk_nextsize를 사용하여 크기 순으로 정렬, 동일한 chunk끼리 연결되지 않는다. 2개의 free chunk가 서로 인접해 있을 수 없고 2개의 free chunk가 인접할 경우 하나의 free chunk로 병합된다.

### 128KB 이상의 큰 메모리

- `mmap()` 시스템 콜을 이용해 별도의 메모리 영역을 할당 후 chunk를 생성
- 해당 크기의 chunk들은 bin에 속하지 않음
- 해당 chunk들은 IS_MMAPED flag 설정
- 해당 영역이 free될 경우 `mummap()`을 호출해 해당 메모리 영역 해제

### Unsorted Bin

해제된 small, large Chunk를 우선적으로 보관하는 bin, 크기와 상관없이 저장하기 때문에 메모리 할당과 반환 속도가 빠르다. 1개의 bin이며 doubly-linked list와 FIFO 방식을 사용한다. free된 chunk는 unsorted bin에 보관되며, 메모리 할당 시 동일한 크기의 영역을 다시 요청하는 경우 해당 영역 재사용한다. 검색된 chunk는 바로 재할당 되거나 원래의 bin으로 돌아간다. 즉, 해제한 chunk를 재사용하기 위해 chunk 해제 후 곧바로 동일한 크기의 chunk를 생성해야 한다.

```c
#include <stdio.h>
#include <stdlib.h>
 
void main(){
        char *heap = malloc(8);
        char *heap2 = malloc(128);
        char *heap3 = malloc(8);
 
        free(heap2);
        getchar();
}
```

```
gdb-peda$ b*main+62
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
                  top: 0x6020d0 (size : 0x20f30) 
       last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x602020 (size : 0x90) <- unsorted bin
```

## References
- [01.Malloc - glibc(ptmalloc2)](https://www.lazenca.net/pages/viewpage.action?pageId=1147929)
- [[glibc] 동적 메모리 관리 (1)](http://egloos.zum.com/studyfoss/v/5206220)
- [Heap 영역 정리](https://tribal1012.tistory.com/141)