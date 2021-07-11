---
title: Fastbin dup
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, fastbin dup]
math: true
mermaid: true
---

## Description

fastbins는 free chunk를 single list로 관리한다. 동일한 크기의 fast chunk 여러개가 해제되면, chunk의 fd 영역을 이용해 관리한다.

## Conditions

- 공격자에 의해 동일한 크기의 fast chunk의 할당과 해제가 자유로워야 한다.
- 공격자에 의해 해제된 fast chunk를 한 번 더 해제할 수 있어야 한다.(Double Free Bug)

### Exploit plan

1. 동일한 크기의 fast chunk 3개 생성
2. 첫 번째 fast chunk 해제
3. 두 번째 fast chunk 해제
4. 첫 번째 fast chunk 해제
5. 같은 크기의 heap을 3개 할당
    - 1번째 heap 영역과 3번째 heap 영역의 주소가 같다!

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
 
int main()
{
        int *buf1 = malloc(112);
        int *buf2 = malloc(112);
        int *buf3 = malloc(112);
 
        free(buf1);
        free(buf2);
        free(buf1);
 
        int *buf4 = malloc(112);
        int *buf5 = malloc(112);
        int *buf6 = malloc(112);
}
```

3번째 Free 다음 fastbin 구조

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x602000 --> 0x602080 --> 0x602000 (overlap chunk with 0x602000(freed) )
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x602180 (size : 0x20e80) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

buf4 malloc 후 구조

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x602080 --> 0x602000 --> 0x602080 (overlap chunk with 0x602080(freed) )
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x602180 (size : 0x20e80) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

buf5 malloc 후 구조

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x602000 --> 0x602080 --> 0x602000 (overlap chunk with 0x602000(freed) )
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x602180 (size : 0x20e80) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

buf6 malloc 후 구조

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x602080 --> 0x602000 --> 0x602080 (overlap chunk with 0x602080(freed) )
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                top: 0x602180 (size : 0x20e80) 
    last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x0
```

fastbinsY의 변화
* 0x602000 -\> 0x602080 -\> 0x602000 -\> 0x602080

## References

- [fastbin_dup[English]](https://www.lazenca.net/pages/viewpage.action?pageId=51970213)
- [\[번역글\]힙 오버플로우를 통한 fastbin 컨트롤](https://bpsecblog.wordpress.com/2016/08/31/translate_fastbin/)
- [\[HITCON Training\] lab12 / Fastbin attack - 1](https://bachs.tistory.com/entry/HITCON-Training-lab12-Fastbin-Attack?category=961837)