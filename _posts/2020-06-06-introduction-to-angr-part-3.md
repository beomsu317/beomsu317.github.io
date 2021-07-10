---
title:  Introduction to angr Part 3
author: Beomsu Lee
math: true
mermaid: true
tags: [angr]
---

나는 휴일이 필요하다. 나 여기서 뭐하고 있지? 새벽 5시에 무심코 컴퓨터를 켜고, 내가 실제로 무언가를 배우고 있다고 생각하도록 나 자신을 속였다. 나는 달리거나(?) 악기를 연주하는걸 배우거나(??) 일반사람처럼 자야할 것이다. bytecode를 읽고 파이썬 같은 것을 쓰는 동안 프로그래밍 방식으로 자신을 해치는 방법에 대해 post를 하나 더 써보는 건 어떨까? 맞다. 일하러 가자.

지난 시간에 간단한 CTF challenge를 사용하여 배웠다. 이번 시간은 angr를 통해 메모리를 조작하는 방법과 더 복잡한 `scanf()` 시나리오를 헤쳐나갈 것이다. 우리는 또한 유명한 `malloc()`을 어떻게 다루는지 볼 것이다.

## 05_angr_symbolic_memory

`scaffold05.py`를 편집하기 전에 Binja를 통해 바이너리를 보자. `main()`이다.

![2020-06-06-Introduction-to-angr-Part-3_0.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_0.png)

행운스럽게도 너무 복잡하지 않네, 해부해보자. 1번째 블록은 stack를 설정하고 `scanf()`를 호출하는 것을 볼 수 있다. 그것이 포맷스트링과 포맷스트링에 의존하는 다수의 인자를 입력하는 것으로 알고있다. 여기서 사용되는 calling convention(cdecl)은 함수의 인자들이 오른쪽에서 왼쪽으로 stack에 push 해야 함을 지시한다, 따라서 `scanf()` 호출 직전 stack에 마지막으로 push된 파라미터는 포맷스트링 자체일 것이다. 이 경우 `%8s %8s %8s %8s`이다. 

포맷스트링에 기반하여 4개의 인자가 있는것을 추론할 수 있고, 실제로 4개의 주소들이 포맷스트링 이전 stack에 push된다. 전에 말했듯이, 인자들은 stack에 거꾸로 push되고, 1번째 push되는 주소는 4번째 `%8s`라는 의미이다. 흥미롭게도 Binja는 `user_input`이 포맷스트링 바로 직전에 있는 3개의 주소를 다른 사용자 입력으로 인식하지 못했기 때문에 이러한 현상이 발생한다고 말한다.

![2020-06-06-Introduction-to-angr-Part-3_1.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_1.png)

이 4개의 주소들을 메모하자(표시된 3개 및 `user_input`의 주소 `0xA1BA1C0`). 이제 바이너리가 8byte 길이의 문자열을 입력으로 받는 것을 알았다, 어떻게 조작되는지 보자.

![2020-06-06-Introduction-to-angr-Part-3_2.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_2.png)

여기서 우리는 반복이 시작되는 것을 볼 수 있다: 0x0은 `[EBP - 0xc]`의 지역변수에 할당되고, 이 변수의 내용은 `0x1f`(31 in decimal)과 비교되며, 만약 변수가 `0x1f`보다 작거나 같다면 다음 코드로 점프한다.

![2020-06-06-Introduction-to-angr-Part-3_3.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_3.png)

보이는가? 반복이. 블록의 마지막에 변수 `[EBP - 0xc]`는 1 증가한다. 이것은 반복문이 `0x0`부터 `0x1f`까지 수행된다는 의미이다. 0부터 31까지 32번의 반복이 있다. 말이 된다. 뭔가 우리의 입력에 반복되고 있으며, 32byte로 구성되어 있다(4개의 8byte 길이). 기본적으로 이 반복이 하는 일은 우리의 입력에 있는 모든 byte를 취급하고 그것에 `complex_function()`를 적용하는 것이다. 그럼 `complex_function()`을 보자.

![2020-06-06-Introduction-to-angr-Part-3_4.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_4.png)

리버싱에 너무 많은 시간을 잃지 말고, 우리는 그것이 우리 byte에 일련의 바이너리가 수학적인 연산을 하고 리턴되는 것을 확인할 수 있다. 강조된 코드 블록에 주의를 기울이면 이 함수가 branch하여 "Try again."을 출력하는 것을 알 수 있고, 어떤 경우에는 프로세스를 종료하는 경우를 볼 수 있다. 우리는 그렇게 하기 싫기 때문에 나중에 angr오 이 branch를 피해야 하는 것을 기억해야 한다. `main()`으로 돌아가 반복문이 끝나면 어떤 일이 일어나는지 보자.

![2020-06-06-Introduction-to-angr-Part-3_5.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_5.png)

그리고 여기에 키가 있다: 우리의 입력, 조작 후, `"NJPURZPCDYEAXCSJZJMPSOMBFDDLHBVN"` 문자열과 비교한다. 만약 2 문자열이 같다면 "Good Job."이 출려되고, 다르면 `complex_function()`과 같이 "Try again."을 출력한다. 지금까지 아는 것을 빠르게 정리해보면

1. 바이너리는 8byte 길이의 문자열을 입력받고
2. 문자열은 다음 주소들에 존재하고 `0xA1BA1C0`, `0xA1BA1C8`, `0xA1BA1D0`, `0xA1BA1D8`
3. 반복문을 통해 `complex_function()`을 조작하고
4. 반복문의 출력은 `"NJPURZPCDYEAXCSJZJMPSOMBFDDLHBVN"`와 비교하고
5. 2개 문자열이 같다면 "Good Job."을 출력하고
6. `complex_function()`과 `main()`은 "Try again."으로 이어질 수 있고
7. 셔터 아일랜드의 레오나르도 다빈치는 미친 사람이고 그는 모든 것을 상상하고 있었다.

좋다. 우리는 해결하기 위한 충분한 정보를 가지고 있다. scaffold5.py를 열어보자.

```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)

  start_address = ???
  initial_state = project.factory.blank_state(addr=start_address)

  password0 = claripy.BVS('password0', ???)
  ...

  password0_address = ???
  initial_state.memory.store(password0_address, password0)
  ...

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return ???

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return ???

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution0 = solution_state.se.eval(password0,cast_to=str)
    ...
    solution = ???

    print solution
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

평소처럼 대부분의 주석들을 간결하게 하기 위해 생략했다. `main()`부터 시작하자.

```python
def main():
  path_to_binary = "05_angr_symbolic_memory"
  project = angr.Project(path_to_binary) # (1)

  start_address = 0x8048601
  initial_state = project.factory.blank_state(addr=start_address) # (2)

  password0 = claripy.BVS('password0', 64) # (3)
  password1 = claripy.BVS('password1', 64)
  password2 = claripy.BVS('password2', 64)
  password3 = claripy.BVS('password3', 64)
```

project를 설정(1)하고 초기 state를 설정(2)하는 것으로 시작한다. `scanf()`가 호출되고 이에 부속물인 `ADD ESP, 0x20`을 호출한 직후 `MOV DWORD [EBP - 0xC]`의 주소에서 시작하는 점에 주목해라. blank state를 설정한 후 우리의 입력을 대신할 4개의 symbolic bitvectors(3)를 만든다. 문자열이 8byte이기 때문에 크기는 64bit라는 점에 유의해라.

```python
password0_address = 0xa1ba1c0 # (1)
initial_state.memory.store(password0_address, password0) # (2)
initial_state.memory.store(password0_address + 0x8,  password1) # (3)
initial_state.memory.store(password0_address + 0x10, password2)
initial_state.memory.store(password0_address + 0x18, password3) 

simulation = project.factory.simgr(initial_state) # (4)
```

1번째 symbolic bitvector가 저장(2)될 주소(1)를 정의한다. 다른 3개의 symbolic bitvectors는 각각 `password0_address + 0x8`(3), `+0x10`, `+0x18`인 `0xA1BA1C8`, `0xA1BA1D0`, `0xA1BA1D8`에 저장되어야 한다. 이후 앞서 설정한 blank state의 simulation manager를 호출한다(4).

```python
def is_successful(state): # (1)
  stdout_output = state.posix.dumps(sys.stdout.fileno())
  if b'Good Job.\n' in stdout_output:
    return True
  else: return False

def should_abort(state): # (2)
  stdout_output = state.posix.dumps(sys.stdout.fileno())
  if b'Try again.\n' in stdout_output:
    return True
  else: return False

simulation.explore(find=is_successful, avoid=should_abort) # (3)
```

여기서 우리는 "Good Job."로 이어지는 코드 블록의 주소와 "Try again."로 이어지는 두 코드 블록의 주소를 주목해 볼 수도 있었지만, 프로그램의 출력을 확인하고 이전 포스트에서 했던 것처럼 angr가 state를 drop 할 것인지 아닌지(3)를 단순하게 2개의 함수(1), (2)를 정의할 수 있다. 다음 우리는 simulation을 시작하고 원하는 코드 경로를 검색한다.(3)

```python
if simulation.found:
  solution_state = simulation.found[0] # (1)

  solution0 = solution_state.solver.eval(password0,cast_to=bytes) # (2)
  solution1 = solution_state.solver.eval(password1,cast_to=bytes)
  solution2 = solution_state.solver.eval(password2,cast_to=bytes)
  solution3 = solution_state.solver.eval(password3,cast_to=bytes)
    
  solution = solution0 + b" " + solution1 + b" " + solution2 + b" " + solution3 # (3)

  print("[+] Success! Solution is: {}".format(solution.decode("utf-8"))) # (4)
else:
  raise Exception('Could not find the solution')
```

이제 원하는 코드 경로에 도달한 state가 있는지 확인(1)하고, symbolic bitvectors(2)를 실제 문자열로 구체화하여(실제로 그것들은 byte이고, 문자열로 디코드하여 출력할 것임), 그것을 합쳐서(3), 결국 해결책을 출력한다.(4) 여기 완성된 스크립트이다.

```python
import angr
import claripy
import sys

def main():
  path_to_binary = "05_angr_symbolic_memory"
  project = angr.Project(path_to_binary)

  start_address = 0x8048601
  initial_state = project.factory.blank_state(addr=start_address)

  password0 = claripy.BVS('password0', 64)
  password1 = claripy.BVS('password1', 64)
  password2 = claripy.BVS('password2', 64)
  password3 = claripy.BVS('password3', 64)

  password0_address = 0xa1ba1c0
  initial_state.memory.store(password0_address, password0)
  initial_state.memory.store(password0_address + 0x8,  password1)
  initial_state.memory.store(password0_address + 0x10, password2)
  initial_state.memory.store(password0_address + 0x18, password3)
  

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Good Job.\n' in stdout_output:
      return True
    else: return False

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Try again.\n' in stdout_output:
      return True
    else: return False

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution0 = solution_state.solver.eval(password0,cast_to=bytes)
    solution1 = solution_state.solver.eval(password1,cast_to=bytes)
    solution2 = solution_state.solver.eval(password2,cast_to=bytes)
    solution3 = solution_state.solver.eval(password3,cast_to=bytes)
    
    solution = solution0 + b" " + solution1 + b" " + solution2 + b" " + solution3

    print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main()
```

실행해 보고 이것이 동작하는지 봐!

![2020-06-06-Introduction-to-angr-Part-3_6.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_6.png)

바로 그거다, 하나 쓰러졌다! 우리가 간다. 그리고 우리의 다음 trick을 위해... `06_angr_symbolic_dynamic_memory`.

## 06_angr_symbolic_dynamic_memory

이 challenge는 stack 대신 `malloc()`을 통해 heap에 문자열을 할당하는 것을 제외하곤 이전 것과 크게 다르지 않다. 프로그램을 보자.

![2020-06-06-Introduction-to-angr-Part-3_7.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_7.png)

다른 challenge와 거의 비슷하다. `main()`을 블록 단위로 분석해보자.

![2020-06-06-Introduction-to-angr-Part-3_8.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_8.png)

2개의 버퍼를 `malloc()`을 통해 할당하는 것을 알 수 있고(파란색과 초록으로 강조된), 두개 모두 9byte 크기이다. `malloc()` 호출 전 push 된 것을 보면, 이 함수는 할당하는 버퍼의 크기인 파라미터만 필요로 하고 `EAX`를 통해 버퍼의 주소를 반환한다고 추론할 수 있다.

사실, 두개 모두 호출된 직후 `EAX`에는 `buffer0`과 `buffer1`로 Binja에서 식별되는 2개의 메모리 영역에 복사되는 것을 볼 수 있다. 이메모리 영역은 각각 `0xABCC8A4`, `0xABCC8AC`에 위치한다.

빨간색 부분을 보면 `scanf()`는 8자의 2문자열로 된 2개의 주소를 쓴다.(문자열의 마지막을 알기 위해 NULL byte를 더한다, 그래서 `malloc()`이 9byte를 할당하고 모두 `memset()`하여 9byte가 NULL byte가 되도록 했다.)

계속 가보자.

![2020-06-06-Introduction-to-angr-Part-3_9.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_9.png)

여기 빨간색안에 이전 것과 매우 비슷한 패턴을 볼 수 있다: 지역변수 `[EBP - 0xc]`는 0x0으로 설정되고 0x7과 동일한지 여부를 확인하기 위해 비교된다. 사실에 근거해 판단해보면

1. 두개의 문자열은 8자(9번째 NULL byte 제외한)
2. 0부터 7까지 8번의 반복
3. 다음 코드 블록의 마지막 명령은 `[EBP - 0xc]`를 1씩 증가

![2020-06-06-Introduction-to-angr-Part-3_10.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_10.png)

여기 2 문자열의 byte를 반복하는 또 다른 반복이 있다고 안전하게 가정할 수 있다. 더욱이, 이전의 코드 블록을 유심히 보면, `[EBP - 0xC]`를 인덱스로 사용하여 반복할 때마다 문자열의 n번째 byte를 로드하고 각 문자열 마다 2번씩 `complex_function()`을 수행하는 것을 알 수 있다.

`complex_function()`을 볼 시간이다.

![2020-06-06-Introduction-to-angr-Part-3_11.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_11.png)

평소처럼 수학적인 연산이다. 이전 challenge와 같이, "Try again." 블록이 있다. `main()`의 둘째 부분으로 돌아가 반복이 끝나면 무슨일이 일어나는지 확인해보자.

![2020-06-06-Introduction-to-angr-Part-3_12.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_12.png)

`main()`의  이 섹션에는 `buffer0`과 `buffer1`이 가리키는 것을 두 개의 다른 문자열과 비교하고, 동일하다면 프로그램은 "Good Job."을 출력하고, 다르면 "Try again."을 출력한다. 전형적인 angr_ctf 행위이다. solution을 만들기 시작하기 전 리버스 엔지니어링을 통해 이해한 것들을 정리해보자.

1. 프로그램은 2개의 9byte 버퍼를 heap 영역에 `malloc()`으로 할당하고 0으로 만든다.
2. 2개의 문자열을 `%8s %8s` 포맷 스트링과 함께 `scanf()`를  통해 입력받는다.
3. 8번 cycle의 반복
4. 매 반복마다 2개의 문자열의 n번째 byte를 `complex_function()`을 통해 "encrypts"
5. 조작 후 2개의 문자열은 다른 문자열과 비교된다.
6. 같으면 win, 다르면 lose
7. 우리는 아직 일반 상대성이론과 양자역학을 통일시키는 모든 것에 대한 이론을 가지고 있지 않다.

scaffold06.py를 보자.

```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)

  start_address = ???
  initial_state = project.factory.blank_state(addr=start_address)

  password0 = claripy.BVS('password0', ???)
  ...

  fake_heap_address0 = ???
  pointer_to_malloc_memory_address0 = ???
  initial_state.memory.store(pointer_to_malloc_memory_address0, fake_heap_address0, endness=project.arch.memory_endness)
  ...

  initial_state.memory.store(fake_heap_address0, password0)
  ...

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return ???

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return ???

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution0 = solution_state.se.eval(password0,cast_to=str)
    ...
    solution = ???

    print solution
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

skeleton solution을 가지고 있고, 이 형식에 맞춰 넣어보자.

```python
def main():
  path_to_binary = "./06_angr_symbolic_dynamic_memory"
  project = angr.Project(path_to_binary) # (1)

  start_address = 0x8048699 
  initial_state = project.factory.blank_state(addr=start_address) # (2)

  password0 = claripy.BVS('password0', 64) # (3)
  password1 = claripy.BVS('password1', 64)
```

우리는 통상적인 변수를 설정하고 angr로 프로젝트를 만드는 것(1)으로 시작한다. 그리고 어디서 시작할 것인지, 이에 따라 state를 설정할 것인지를 결정(2)한다. `scanf()` 호출 이후의 명령인 `MOV DWORD [EBP - 0xC], 0x0`를 가리키고 있는 `0x8048699`에서 시작한다. 나중에 스크립트에서 다룰 것이기 때문에 기본적으로 모든 `malloc()`을 건너뛴다. 이후 64bit 크기(8byte * 8)의 2개의 symbolic bitvector를 초기화한다.(3)  다음 부분.

```python
fake_heap_address0 = 0xffffc93c # (1)
pointer_to_malloc_memory_address0 = 0xabcc8a4 # (2)
fake_heap_address1 = 0xffffc94c # (3)
pointer_to_malloc_memory_address1 = 0xabcc8ac # (4)

initial_state.memory.store(pointer_to_malloc_memory_address0, fake_heap_address0, endness=project.arch.memory_endness) # (5)
initial_state.memory.store(pointer_to_malloc_memory_address1, fake_heap_address1, endness=project.arch.memory_endness) # (6)

initial_state.memory.store(fake_heap_address0, password0) # (7)
initial_state.memory.store(fake_heap_address1, password1) # (8)
```

이것이 중요하다. angr는 실제로 바이너리를 "실행"하지 않아, 실제 할당된 heap의 메모리 영역이 필요하지 않다. 따라서 가짜의 주소를 사용해도 된다. 우리가 할 것은 stack의 2개의 주소를 선택하는 것과 (1)(3) 또한 `buffer0`과 `buffer1`의 주소를 `pointer_malloc_address0`과 `pointer_malloc_address1` 변수에 저장했다.(2)(4) 

이후 angr에게 2개의 가짜 주소들을 `buffer0`과 `buffer1`에 저장하라고 했는데(5)(6), 여기서 바이너리가 실행되면 `malloc()`로 반환된 주소를 저장했을 것이다. 결국 우리는 2개의 symbolic bitvectors를 2개의 가짜 주소에 저장했다(7)(8). 이제 마법이 보이니?

```
BEFORE:
buffer0 -> malloc()ed address 0 -> string 0
buffer1 -> malloc()ed address 1 -> string 1

AFTER:
buffer0 -> fake address 0 -> symbolic bitvector 0
buffer1 -> fake address 1 -> symbolic bitvector 1
```

기본적으로 `buffer0`과 `buffer1`을 가리키는 주소를 우리가 선택한 주소와 symbolic bitvector를 저장한 주소로 대체했다. 이 시점에서 나머지 스크립트 부분은 매우 간단하다.

```python
simulation = project.factory.simgr(initial_state) # (1)

def is_successful(state): # (2)
  stdout_output = state.posix.dumps(sys.stdout.fileno())
  if b'Good Job.\n' in stdout_output:
    return True
  else: return False

def should_abort(state): # (3)
  stdout_output = state.posix.dumps(sys.stdout.fileno())
  if b'Try again.\n' in stdout_output:
    return True
  else: return False

simulation.explore(find=is_successful, avoid=should_abort) # (4)

if simulation.found:
  solution_state = simulation.found[0]

  solution0 = solution_state.solver.eval(password0, cast_to=bytes) # (5)
  solution1 = solution_state.solver.eval(password1, cast_to=bytes)

  print("[+] Success! Solution is: {0} {1}".format(solution0.decode('utf-8'), solution1.decode('utf-8'))) # (6)
else:
  raise Exception('Could not find the solution')
```

simulation을 초기화하고(1), 우리가 원하는 코드 블록을 찾고 원하지 않는 코드 블록을 피할 책임이 있는 2개의 함수를 정의하고(2)(3), simulation을 explore하여 코드 경로를 찾고(4), 만약 실수하지 않고 solution을 찾는데 성공했다면, 2개의 bitvector들을 구체화하고(5), solution을 출력한다(6). 여기 완성된 스크립트이다.

```python
import angr
import claripy
import sys

def main():
  path_to_binary = "./06_angr_symbolic_dynamic_memory"
  project = angr.Project(path_to_binary)

  start_address = 0x8048699
  initial_state = project.factory.blank_state(addr=start_address)

  password0 = claripy.BVS('password0', 64)
  password1 = claripy.BVS('password1', 64)

  fake_heap_address0 = 0xffffc93c
  pointer_to_malloc_memory_address0 = 0xabcc8a4
  fake_heap_address1 = 0xffffc94c
  pointer_to_malloc_memory_address1 = 0xabcc8ac
  initial_state.memory.store(pointer_to_malloc_memory_address0, fake_heap_address0, endness=project.arch.memory_endness)
  initial_state.memory.store(pointer_to_malloc_memory_address1, fake_heap_address1, endness=project.arch.memory_endness)

  initial_state.memory.store(fake_heap_address0, password0)
  initial_state.memory.store(fake_heap_address1, password1)
  
  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Good Job.\n' in stdout_output:
      return True
    else: return False

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Try again.\n' in stdout_output:
      return True
    else: return False

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution0 = solution_state.solver.eval(password0, cast_to=bytes)
    solution1 = solution_state.solver.eval(password1, cast_to=bytes)

    print("[+] Success! Solution is: {0} {1}".format(solution0.decode('utf-8'), solution1.decode('utf-8')))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main()
```

테스트 해보고 무슨 일이 일어나는지 보자.

![2020-06-06-Introduction-to-angr-Part-3_13.png](/assets/img/angr/2020-06-06-Introduction-to-angr-Part-3_13.png)

무결점. 이것이 이 파트의 모두다. 평소보다 길었지만 모두 가치있는 시간이라고 생각한다. 다음 post에서 보자.


##### Resources 
- [Introduction to angr Part 3](https://blog.notso.pro/2019-04-10-angr-introduction-part3/)