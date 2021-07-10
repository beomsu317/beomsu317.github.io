---
title:  Enigma 2017 Crackme 0 Writeup
author: Beomsu Lee
category: [Reversing]
tags: [reversing]
math: true
mermaid: true
---

어제 Binary Ninja 사용 에디션을 구매했고 이것을 테스트하길 원해서 reverse engineering challenge를 찾아봤다. reverse engineering에 소질이 있기 때문에 난 간단한 enigma 2017 CTF의 crackme 0을 선택하기로 했다. 제공된 C 소스코드를 볼 수 있었는데, 이미 소스가 있다면 reverse engineering이 무슨 소용인가? 소스코드를 화이트해커에게 남겨두지 않을럐?

## Static analysis with Binary Ninja

우선 첫째로, 나의 좋은 친구 Binary Ninja를(이제부터 Binja)를 불태우고 바이너리를 둘러보기 시작했다. `main()`이외의 3개의 흥미로운 함수를 가지고 있다.

- wrong()
- decrypt()
- fromhex()

`wrong()`부터 시작해보자.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_0.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_0.png)

그 과정을 죽이는 것 외에 별로 도움이 되지 않는다. XREF 섹션에서 그것이 메인으로부터 2번 호출되는 것을 볼 수 있다. 

![2020-06-04-Enigma-2017-Crackme-0-Writeup_1.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_1.png)

revese engineering 중 프로그램이 어떻게 작동하는지, 그리고 더 중요한 것은, 프로그램이 작동하기 위한 조건이 무엇인지를 어느정도 밝혀줄 수 있기 때문에, `wrong()`같은 실패함수들이 언제 호출되는지를 보는 것이 항상 중요하다. 구체적으로 살펴봐야 할 것은 `wrong()` 같은 함수가 호출되었을 때이다. 전에 말했듯 이것은 2번 호출된다: 1번째는 fromhex() 반환된 직후이다. 

![2020-06-04-Enigma-2017-Crackme-0-Writeup_2.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_2.png)

그리고 2번째는 흥미로운`memcmp()` 호출 직후이다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_3.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_3.png)

하지만 깔끔하게 처리하자, 모든 CTF는 2년전에 끝나 우리는 경쟁하지 않는다. `fromhex()` 함수를 열고 확인해볼 시간이다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_4.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_4.png)

이런, 난 잡자기 읽이 엉망이 되는게 싫어... 데카르트적 논리 접근법으로 가자. 우리는 작은 block들로 나누면 여기서 무슨 일이 벌어지는지 알 수 있을 것이다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_5.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_5.png)

`fromhex()`의 block이 하는 일은 함수가 호출된 직후 필수적으로 stack를 세팅하고, 입력 문자열의 길이 확인을 위해 C 함수 `strlen()`을 호출한다. stack의 어느 영역이 어떤 변수를 가리키는지 이해하기 쉽게 이미 Binja의 변수이름을 바꿨다. 호출 규칙에 따르면, 함수가 반환될 때 리턴 값을 EAX에 넣는데, `strlen()` 반환 직후 EAX에 있는 값이 `EBP-0x10`에 위치한 로컬 변수에 복사되는 것을 알 수 있다. 만약 mapnage에서 `strlen()`을 확인해보면 다음과 같은 정보를 찾을 수 있다. 

![2020-06-04-Enigma-2017-Crackme-0-Writeup_6.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_6.png)

그래서... `strlen()`은 인자로 전달한 문자열의 길이를 되돌려준다. 흥미롭다, 사실 대부분의 경우 프로그래머는 문자열의 길이가 정확한지 확인하기도 한다! 따라서 우리는 `strlen()` 호출되고 난 직후에 문자열의 길이와 고정 값을 비교하는 명령을 찾을 것이라고 가정할 수 있다. 그리고 그런 일이 일어난다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_7.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_7.png)

난 여기서 무슨 일이 일어나는지 확실히 이해하는데 시간이 좀 걸렸기 때문에 코드에 주석을 달았다. 이유는 모르겠지만 `CMP EAX, 0x20`로 문자열 길이를 직접 확인하는 대신, 프로그램은 먼저 `SAR EAX, 0x1` 명령을 사용해 문자열 길이를 2개로 나눈 다음 `CMP EAX, 0x10`을 수행한다.

EDIT: 안녕, 여기 미래에서 마지막이야. 나는 post 작성을 거의 마무리한 후에 마침내 내가 흥미로운 것을 발견하지 못하도록 소스코드를 살펴보기로 결정했는데, 그 프로그램이 이렇게 할 이유가 있다는 것이 밝혀졌다: 소스코드에는 다음과 같은 라인이 있었다. 

```c
int len = strlen(input);
  //can't decode hex string with odd number of characters
  if (len&1) {
    return 1;
  }
  //make sure len/2 is the size we are looking for
  if (len>>1 != SECSIZE) {
    return 2;
  }
```

그래서 여기서 일어나고 있는 일은 먼저 문자열이 짝수로 되어 있는지(`len&1`는 AND와 0x1, 그리므로 맨 오른쪽 bit가 1인지 0인지 확인) 확인한 다음 `len`을 2로 나누어 `SECSIZE`(코드에서 16으로 정의되는 것)와 동일한지 확인한다. 이제 지난 post로 돌아가자.

`fromhex()`의 나머지 부분을 보면 우리가 입력하는 시리얼 넘버가 유효한 16진수 문자열인지 확인하는 것이 목적인 것 같다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_8.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_8.png)

또한 `fromhex()`에서 입력에 16진수 값이 아니거나 입력 문자열이 32자 길이가 아닌 경우 매번 0이 아닌 값이 리턴되는 것을 확인할 수 있다. 이것은 흥미롭다, `main()`은 `fromhex()`의 리턴 값을 점검하고(`TEST EAX, EAX`), 만약 0이 아니면 `wrong()` block으로 점프한다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_9.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_9.png)

`JE 0x80486B3` 명령의 주소는 `wrong()`으로 이끄는 코드 block 중 하나이다.

좋다, 지금까지 우리가 아는 것을 정리해보자.

- 프로그램은 인자로 문자열을 받기 원한다.
- 문자열은 정확히 32자를 포함해야 한다.
- charset은 [a-z0-9]이다.
- 위의 요구사항을 준수하지 않을 시 `wrong()`으로 이어진다.
- `fromhex()` 함수는 위의 점검의 일부를 담당한다.

이제 프로그램이 어떻게 동작하는지 이해했으므로 더 흥미로운(대게 더 무서운) 함수 decrypt()로 넘어갈 수 있다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_10.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_10.png)

무슨 친구인지 알아? 더 안좋은 건 나도 봤어, 이건 화면에도 잘 맞잖아! 다른 거 알려줄까? 정적인 어셈블리 코드를 보는게 약간 지루해졌는데 좋은 친구 GDB를 이용해 이 함수의 작동 방식을 분석해보는건 어때? GDB에 대한 명령 집합인 GEF를 사용해 많은 기능을 추가하고 컬러 코드 등을 사용해 출력을 더 나은 방식으로 포맷할 것이다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_11.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_11.png)

이것을 해독해보자. 스크린샷을 보면

1. `disassemble decrypt`를 통한 `decrypt()` 함수 디스어셈블
2. `break *decrypt`를 통한 decrypt 시작에 breakpoint 설정
3. `r aabbccddeeffaabbccddeeffaabbccdd`를 통한 32자의 문자열로 프로그램 실행

예상대로 실행은 `decrypt()` 바로 시작에 중단되었다. 위에 정의한 모든 필요조건들을 준수하고 `fromhex()`를 통과하도록 프로그램에게 인자로 준 문자열을 볼 수 있고, 그렇지 않다면 프로그램은 입력이 잘못되었다고 말했을 것이고 심지어 `decrypt()`에 도달하지 못했을 것이다. 그런 말을 듣는 것은 그 함수를 통해 우리의 입력에 어떤 일이 일어나는지 보자. 몇 라운드 동안 그것이 그것의 일을 하도록 내버려 둔 후 주소 0x8049a97이 `decrypt()` 안에 있는 다음 명령을 2번 이상 호출되고 있는 것을 알아냈다. 

```
movzx  eax, BYTE PTR [eax+0x8049a97]
add    edx, 0x8049a97
mov    BYTE PTR [eax+0x8049a97], dl
lea    edx, [eax+0x8049a97]
```

어떤 문자열을 조작하는 것 같은데, 함수를 "decrypt"라고 하니 말이된다. 그 주소에서 무엇을 찾을 수 있는지 확인해보자.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_12.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_12.png)

그것은 예상 밖의 일이었다. 그 함수는 우리의 입력 문자열을 한 번에 2글자씩 byte block으로 변환하는 것 같다. 이것은 일리가 있다. 생각해보자: 우리의 입력은 32 byte이고 charset은 16진수와 동일한 문자 집합인 [a-z0-9]이다. 만약 `decrypt()`가 byte로 변경하면 우리는 16byte를 가지게 되고, 모든 byte는 우리가 입력한 2개의 문자들로 만들어진다. 또한 이 주소는 이름이 `buffer`이다. 왜 이렇게 친근하지?

![2020-06-04-Enigma-2017-Crackme-0-Writeup_13.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_13.png)

맞다! "흥미로운" 호출은 `memcmp()`이라고 전에 말한 것을 기억하는가? 이것은 `buffer` 변수와 `secret` 변수를 비교하는 것처럼 보인다. `decrypt()`로 돌아가 `buffer`가 어떻게 변하는지 보자. 함수의 마지막에 breakpoint를 걸고 프로그램 실행을 다시 할 것이며, 이번에는 `00112233445566778899aabbccddeeff`를 입력으로 주겠다. 

![2020-06-04-Enigma-2017-Crackme-0-Writeup_14.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_14.png)

이제 진짜 깔끔해졌다! 스크린샷의 밑 부분에 입력은 우리가 원하는 대로 파싱됐다. 

```
0xffffcd01:	"00112233445566778899aabbccddeeff"
```

요렇게

```
0x8049a97 <buffer>:	0xff	0xee	0xdd	0xcc	0xbb	0xaa	0x99	0x88
0x8049a9f <buffer+8>:	0x77	0x66	0x55	0x44	0x33	0x22	0x11	0x00
```

우리는 `memcmp()` C 함수가 3가지 인자를 취하는 것을 알고있다.

1. 메모리 `str1`의 block 포인터
2. 다른 메모리 `str2`의 block 포인터
3. 개수 `n`

그것이 하는 일은 기본적으로 메모리 `str1`과 `str2`의 2 block 중 첫 번째 `n` byte를 비교하는 것이다. 다음과 같은 값을 반환할 수 있다.

- `str1`이 `str2`보다 작으면 0보다 작다.
- `str1`이 `str2`보다 크면 0보다 크다.
- 두 값이 같다면 0과 같다.

따라서 어셈블리를 보면 `memcmp()` 호출 전 3개의 인자를 stack에 push하고 그것들은 number 0x10, `secret`의 주소, `buffer`의 주소이다. calling convention 알기 때문에 인자들은 stack에 역순으로 push 되고 number는 확인할 byte의 크기이고,  `secret`과 `buffer`는 비교될 2개의 메모리 블록이라는 것을 안다. 그리고 `JNE 0x80486e5`에서 판단해보면 `buffer`와 `secret`은 "That is correct!" 문자열을 출력하기 위해 같아햐 한다.

이제 우리가 기억할 수 있는 모든 것을 알고서, `secret`이 어떻게 생겼는지 보자. GDB에서 main을 디스어셈블하여 `buffer`가 push 되기 전에 어떤 주소가 push 되는지 보고 `memcmp()`를 호출하면 `secret`의 주소를 찾을 수 있다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_15.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_15.png)

완벽하다. 이제 우리는 다시 입력하여 제대로 파싱되게 하면된다. `secret`의 값을 아는 것은 이것으로부터 거꾸로 써서 다음과 같이 얻을 수 있다.

```
0x8049a74 <secret>:	0x37	0x39	0x37	0x65	0x61	0x66	0x32	0x35
0x8049a7c <secret+8>:	0x31	0x63	0x32	0x37	0x65	0x61	0x64	0x32
```

이렇게

```
32646165373263313532666165373937
```

이제 `./crackme_0 32646165373263313532666165373937` 실행하면 다음과 같은 출력을 얻을 수 있다.

![2020-06-04-Enigma-2017-Crackme-0-Writeup_16.png](/assets/img/angr/2020-06-04-Enigma-2017-Crackme-0-Writeup_16.png)

좋아, 이제 솔직하게 말할게. 나는 notso.pro이고 이것은 실제로 그렇게 되지 않았다. 그래서 나는 어떻게 일이 실제로 진행되는지 간단히 설명하겠다.

```
What's all this mess?
WTF am I still doing here?!
FUCK!
FUCK!
FUCK!
Ehi look there's a string there!
It's not the serial!
FUCK!
FUCK!
FUCK!
This shit doesn't work!
FUCK!
FUCK!
FUCK!
I really suck at this!
FUCK!
FUCK!
FUCK!
Wait a minute, my input is translated to this stuff?
So that's how it works uh?
Great I solved it!! Now, how does this shit work?
```

그렇다. 이것이다. 내가 이것을 해결했을 때 새벽 4시라고 말하는걸 잊었나? 그래, 내 인생은 좀 거지같아.

## References

- [Enigma 2017 Crackme 0 Writeup](https://blog.notso.pro/2019-03-13-Enigma2017-Crackme0-writeup/)