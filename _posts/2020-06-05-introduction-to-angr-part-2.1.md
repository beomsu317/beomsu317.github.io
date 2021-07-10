---
title:  Introduction to angr Part 2.1
author: Beomsu Lee
tags: [angr]
---

[Enigma 2017 Crackme 0 Writeup](https://beomsu317.github.io/2020-06-04/Enigma-2017-Crackme-0-Writeup)

이전 포스트에서 말했듯이 우리는 우리가 지금까지 angr _ctf에서 보아온 것과 다른 리버스 엔지니어링 challenge에 대해 angr를 테스트했을 것이다. 나는 게으른 사람이기 때문에 새로운 바이너리를 완벽하게 분석하길 원하지 않아서 위의 post에서 본 것을 선택했다. 이것을 읽지 않았다면, 이것을 철처히 검토하지 않을 것이니 지금 당장 읽고, angr를 사용해 해결하는 다른 접근법을 보여주겠다. 그러나 먼저 이 challenge를 해결하기 위해 알아야 할 것을 재점검 해보자.

![2020-06-05-Introduction-to-angr-Part-2.1_0.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_0.png)

보다시피 우리가 관심없는 코드 경로(`wrong()`)를 빨간색으로, 녹색에는 우리가 관심 있는 코드 경로("That is Correct!")를, 파란색에는 angr가 분석을 시작할 명령으로 강조했다. 모든 주소를 `wrong()`으로 가져오는 대신, 함수의 주소를 사용하여 함수에 도달하는 모든 state를 drop하면 된다. `fromhex()`를 보고 관심없는 경로를 배제할 수 있는지 확인해보자. 또한 입력의 결핍에 대해 불평하고 프로그램을 즉시 종료하는 것이기에 `0x8048670` 시작하는 코드 경로를 피해야 한다.

![2020-06-05-Introduction-to-angr-Part-2.1_1.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_1.png)

이전에 봤듯이, `fromhex()`는 입력은 받은 값에 따라 다른 값을 리턴할 것이다. 하지만 main()의 이 코드를 통해 `EAX`가 0으로 리턴되는 state만 관심이 있다.

![2020-06-05-Introduction-to-angr-Part-2.1_2.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_2.png)

기본적으로 `JE` 명령은 `JZ`(a.k.a 0이면 점프) 명령과 같다. 바로 직전의 `TEST EAX, EAX` 명령은 만약 `EAX`가 0이면 `EFLAGS` 레지스터의 zero flag를 세팅한다. `JE`나 `JZ` 명령은 zero flag가 세팅되어있을 경우 특정 경로로 점프하는데, 따라서 우리는 오직 0이 `EAX`에 저장되는 코드 경로에만 관심이 있다. 이를 알고 우리는 `fromhex()`로 돌아가 0이 반환되는 것 이외의 다른 어떤 것이든 이르는 모든 코드 경로를 메모할 수 있다.

![2020-06-05-Introduction-to-angr-Part-2.1_3.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_3.png)

![2020-06-05-Introduction-to-angr-Part-2.1_4.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_4.png)

좋다. 이제 우리가 관심어하는 모든 코드 경로와 피하고 싶은 코드 경로가 생겼으니, 우리의 symbolic buffer를 어디에 둘지 보자.

![2020-06-05-Introduction-to-angr-Part-2.1_5.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_5.png)

스크린샷에서 `fromhex()` 호출 전 입력값의 포인터가 stack에 push 되는 것을 볼 수 있고 이것은 우리가 기본적으로 입력 문자열을 우리가 원하는 어디든 저장할 수 있다는 것을 의미하고, 그리고 우리가 선택한 주소(stack에 어떤 주소가 될 수 있음)를 `EAX`에 넣으면 프로그램이 나머지를 처리할 것이다. 걱정마라. 우리는 곧 그것을 어떻게 하는지 볼 것이다.

지금까지 알고 있는 것을 보자.

1. `0x8048692`에서 시작할 것이며, `fromhex()`가 호출되기 바로 전 `PUSH EAX`의 주소다.
2. 주소가 `0x80486d3`에 도달하면, "That is correct!"를 출력하는 코드 블록이 시작된다.
3. 관심없는 코드 경로인 주소들은 `0x8048541`, `0x8048624`, `0x8048599`, `0x8048585`, `0x8048670`
4. 우리의 문자열을 가리키는 포인터가 `EAX`에 저장되는 것을 알고있다.
5. 케익은 거짓이다.

스크립트를 작성할 수 있고, 먼저 필요한 라이브러리를 가져오는 것부터 시작한다.

```python
import angr
import claripy
```

다음 우리의 `main()`과 우리가 필요한 변수들을 정의한다. 이것과 함께 angr의 초기 상태를 정의한다.

```python
def main():
    path_to_binary = "./crackme_0"
    project = angr.Project(path_to_binary)

    start_addr    = 0x8048692 # address of "PUSH EAX" right before fromhex()
    avoid_addr    = [0x8048541, 0x8048624, 0x8048599, 0x8048585, 0x8048670] # addresses we want to avoid
    success_addr  = 0x80486d3 # address of code block leading to "That is correct!"
    initial_state = project.factory.blank_state(addr=start_addr)
```

이제 우리의 bitvector를 메모리에 저장하고 그것의 주소를 `EAX`에 넣을 시간이다. 편리하게도 angr는 그것을 다음 함수들을 통해 쉽게 만들어준다.

```python
initial_state.memory.store(fake_password_address, password) # store symbolic bitvector to the address we specified before
initial_state.regs.eax = fake_password_address # put address of the symbolic bitvector into eax
```

이후에 simulation을 시작하고 angr가 지정한 코드 경롤를 찾도록 한다.

```python
simulation = project.factory.simgr(initial_state)
simulation.explore(find=success_addr, avoid=avoid_addr)
```

그리고 해결책이 있는지 확인하고 출력을 할 시간이다.

```python
if simulation.found:
    solution_state = simulation.found[0]

    solution = solution_state.solver.eval(password, cast_to=bytes) # concretize the symbolic bitvector
    print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
    
else: print("[-] Bro, try harder.")
```

완성된 스크립트이다.

```python
import angr
import claripy

def main():
    path_to_binary = "./crackme_0"
    project = angr.Project(path_to_binary)

    start_addr   = 0x8048692 # address of "PUSH EAX" right before fromhex()
    avoid_addr   = [0x8048541, 0x8048624, 0x8048599, 0x8048585] # addresses we want to avoid
    success_addr = 0x80486d3 # address of code block leading to "That is correct!"
    initial_state = project.factory.blank_state(addr=start_addr)
    
    password_length = 32               # amount of characters that compose the string
    password = claripy.BVS("password", password_length * 8) # create a symbolic bitvector
    fake_password_address = 0xffffcc80 # random address in the stack where we will store our string

    initial_state.memory.store(fake_password_address, password) # store symbolic bitvector to the address we specified before
    initial_state.regs.eax = fake_password_address # put address of the symbolic bitvector into eax

    simulation = project.factory.simgr(initial_state)
    simulation.explore(find=success_addr, avoid=avoid_addr)

    if simulation.found:
        solution_state = simulation.found[0]

        solution = solution_state.solver.eval(password, cast_to=bytes) # concretize the symbolic bitvector
        print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
    
    else: print("[-] Bro, try harder.")
    
if __name__ == '__main__':
  main()
```

이것을 실행하고 테스트해 볼 시간이다.

![2020-06-05-Introduction-to-angr-Part-2.1_6.png](/assets/img/angr/2020-06-05-Introduction-to-angr-Part-2.1_6.png)

동작했다! 좋아! 이것은 우리에게 6초 남짓만에 solution을 제공했다. 오늘은 여기까지이다. 다음 angr tutorial에서 보자.

##### Resources

- [Introduction to angr Part 2.1](https://blog.notso.pro/2019-04-03-angr-introduction-part2.1/)