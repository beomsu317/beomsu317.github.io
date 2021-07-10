---
title:  Introduction to angr Part 2
author: Beomsu Lee
tags: [angr]
---

구글에서 글쓴이의 block과 blank 페이지의 공포와 싸우는 방법을 검색하는 것? 확인해봐. 이번엔 정말 어떻게 시작해야 할지 모르겠다. 내가 정신이 없어서 그런 것 같은데 바로 봐보자.

마지막 post에 우리는 angr를 이용해 레지스터에 symbolic bitvector를 inject하는것과 원하지 않는 코드 경로들을 피하는 법을 배웠으나, 우리는 뻔뻔하게도 함수 중간에 착지하지 않고 처음부터 함수를 위한 stack frame을 구성해야 한다. 이 post에선 (희망스럽게) 이것을 어떻게 하는지 배운다.

## 04_angr_symbolic_stack

첫째로 도전과제를 보자.

![2020-06-03-Introduction-to-angr-Part-2_0.png](/assets/img/angr/2020-06-03-Introduction-to-angr-Part-2_0.png)

괜찮아. 여기는 나쁘지 않네. `handle_user()` 함수로 넘어가자.

![2020-06-03-Introduction-to-angr-Part-2_1.png](/assets/img/angr/2020-06-03-Introduction-to-angr-Part-2_1.png)

angr가 너무 좋아할 이쁜 "복잡한" 포맷스트링을 봐. 또 scanf()를 호출하기 전에 프로그램은 `[EBP - 0x10]`과 `[EBP - 0xc]`라는 2개의 지역변수를 stack에 push한다.

![2020-06-03-Introduction-to-angr-Part-2_2.png](/assets/img/angr/2020-06-03-Introduction-to-angr-Part-2_2.png)

그럼, 표준 angr 바이너리 도전? 별로 그렇지 않다. 변수들은 이전 post와 다르게 레지스터가 아닌 stack에 저장되어 있고, 프로그램을 망치지 않고 symbolic buffer를 push 하기위해 stack에 마법을 걸어야한다. 지금까지 알고 있는 내용을 다시 정리해보자.

1. `main()`은 `handle_user()`를 호출한다.
2. `handle_user()`는 복잡한 포맷스트링과 함께 `scanf()`를 호출한다.
3. scanf()는 handle_user()에 `[EBP - 0x10]`, `[EBP - 0xc]` 2개의 값을 넣는다.
4. 인생은 거지같고 난 인터넷에서 멍청한 짓 하지말고 일을 구해야 할 것 같다.

어쨌든, 이제 바이너리가 어떻게 하는지 확실하게 이해했다. skeleton solution을 보자. scaffold04.py (단순함을 위해 대부분의 주석을 편집했다.)

```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)

  start_address = ???
  initial_state = project.factory.blank_state(addr=start_address)
  
  initial_state.regs.ebp = initial_state.regs.esp

  password0 = claripy.BVS('password0', ???)
  ...

  padding_length_in_bytes = ???  # :integer
  initial_state.regs.esp -= padding_length_in_bytes

  initial_state.stack_push(???)  # :bitvector (claripy.BVS, claripy.BVV, claripy.BV)
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

    solution0 = solution_state.se.eval(password0)
    ...

    solution = ???
    print solution
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

바로 변경하는 것 대신에, 전략을 세우자. 우리는 angr가 어디서 시작할지 결정해야 한다. `scanf()`를 건너뛰어야 하기 때문에, 우리는 `0x8048697` 명령이 위치한 곳에서 시작할 것이다. `scanf()`가 반환 후 stack을 clear하기 때문에 scanf() 명령 바로 뒤 `ADD ESP, 0x10`을 건너뛰게되며, 우리는 그것을 부르지 않기 때문에 아무것도 clear 할 필요가 없다.

![2020-06-03-Introduction-to-angr-Part-2_3.png](/assets/img/angr/2020-06-03-Introduction-to-angr-Part-2_3.png)

이제 우리는 inject 할 symbolic vectors의 정확한 위치를 알아내기 위해 건너뛴 모든 명령어들이 어떻게 stack를 조작하는지 알아야한다. 우리는 inject 할 2 값이  `[EBP- 0x10]`, `[EBP - 0xc]`에 위치하기 때문에 이것들을 push하기 전 stack에 패딩을 해야하지만 우선 메모리에서 `EBP`를 가리켜야 할 위치를 알려야 한다. 이렇게 하기 위해 우리는 (생략한) prologue 함수가 하는 일을 "angr"로 할 것이다: `MOV EBP, ESP`. 이후에 stack pointer를 감소시키고 우리의 값을 push 할 것이다. 하지만 정확히 얼만큼의 패딩이 필요할까?

우리는 2 값중 가장 낮은 값이 `[EBP - 0xc]` 위치에 있는것을 알지만, 4byte 값이기 때문에 다음 주소를 차지할 것이다: `| 0xc | 0xb | 0xa | 0x9 |`. 이것은 stack에 1번째 값과 2번째 값을 push하기 전 8byte 패딩이 필요한 것을 의미한다. 값을 stack에 push 한 후 우리는 시작할 준비가 되어 있어야 한다. 스크립트를 어떻게 변경할지 보자.

```python
def main(argv):
  path_to_binary = "04_angr_symbolic_stack"
  project = angr.Project(path_to_binary)

  start_address = 0x8048697
  initial_state = project.factory.blank_state(addr=start_address)
```

여기에서 특별한 것은 없다. 평소처럼 `path_to_binary` 변수를 update 하고 `state_address`를 이전에 봤던 `scanf()` 함수의 stack를 정리하는 명령 다음 명령 값으로 설정한다. 이제 stack에서 작업을 해야 할 시간인데, 우선 `MOV EBP, ESP` 명령을 angr의 방법을 사용하여 수행할 것이다. 

```python
initial_state.regs.ebp = initial_state.regs.esp
```

이후에 우리의 symbolic 값들을 stack에 push 하기 전 패딩을 제공하기 위해 stack pointer(stack은 아래로 확장되므로 실제로 stack의 크기를 늘리고 있다.)의 값을 8만큼 감소시킬 것이다.

```python
padding_length_in_bytes = 0x08
initial_state.regs.esp -= padding_length_in_bytes
```

이제 symbloic bitvectors를 생성하고 stack에 push 할 시간이다. 프로그램이 2개의 unsigned integer 값(`%u %u` 형식 문자열)을 예상하므로, symbloic bitvectors는 32bit가 될 것이다. 이는 x86 아키텍쳐의 unsigned integer 크기이다.

```python
password0 = claripy.BVS('password0', 32)
password1 = claripy.BVS('password1', 32)

initial_state.stack_push(password0) 
initial_state.stack_push(password1)
```

이후에 나머지들은 이전의 스크립트와 동일하다. 단지 symbolic bitvectors를 해결하고 출력하기만 하면된다.

```python
if simulation.found:
  solution_state = simulation.found[0]
  solution0 = (solution_state.solver.eval(password0))
  solution1 = (solution_state.solver.eval(password1))

  print("[+] Success! Solution is: {0} {1}".format(solution0, solution1))
else:
  raise Exception('Could not find the solution')
```

최종적인 스크립트이다.

```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = "04_angr_symbolic_stack"
  project = angr.Project(path_to_binary)

  start_address = 0x8048697
  initial_state = project.factory.blank_state(addr=start_address)

  initial_state.regs.ebp = initial_state.regs.esp
  
  password0 = claripy.BVS('password0', 32)
  password1 = claripy.BVS('password1', 32)

  padding_length_in_bytes = 0x08
  initial_state.regs.esp -= padding_length_in_bytes

  initial_state.stack_push(password0)  
  initial_state.stack_push(password1) 
  

  simulation = project.factory.simgr(initial_state)

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    #print(stdout_output)
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

    solution0 = (solution_state.solver.eval(password0))
    solution1 = (solution_state.solver.eval(password1))

    print( solution0, solution1)
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

![2020-06-03-Introduction-to-angr-Part-2_4.png](/assets/img/angr/2020-06-03-Introduction-to-angr-Part-2_4.png)

멋지다. 효과가 있다! angr가 어떻게 작동하는지 알아내기 시작했다, 아마 다음엔 실제 CTF에 적용되는 것을 볼 수 있을거야. 이 포스트는 여기서 끝이다. 다음 포스트에서 보자.

##### Resources
- [Introduction to angr Part 2](https://blog.notso.pro/2019-03-26-angr-introduction-part2/)