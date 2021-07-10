---
title:  Introduction to angr Part 1
author: Beomsu Lee
category: [Binary Analysis, Angr]
tags: [binary analysis, angr]
math: true
mermaid: true
---

이 시리즈의 [zeroth part](https://blog.notso.pro/2019-03-20-angr-introduction-part0/)에서 간단한 바이너리의 매우 기본적인 symbolic execution 하는 방법을 배웠다. 이 시간에는 symbolic bitvectors와 원하지 않는 state를 피하여 실행 시간을 줄이는 방법에 대해 말해볼 것이다. 

01_angr_avoid 도전은 기본적으로 첫번째 도전과 동일하므로 생략할 것이다. 단, 여러분이 피하고 싶은 분기도 명시해야 한다: angr의 `explore()` 함수는 코드의 주소로 avoid 인자를 지정할 수 있지만 분석하기 싫다면, 걱정마라, 곧 알게 될거야. 

## 02_angr_find_condition

이 도전과제는 angr에게 무엇을 프로그램 자체의 산출물에 기반하여 피하거나 유지되어야 하는지를 어떻게 말해야 될것인가에 대해 가르쳐준다. 디스에셈블러로 바이너리를 열면 수많은 block의 "Good Job." 또는 "Try again."을 출력하는 블록을 볼 수 있다. 그래서 이 블록들의 모든 시작 주소들을 확인하는 것은 NO NO 이다. 운좋게도 우리는 stdout의 출력에 기반하여 state를 유지하거나 버리도록 angr에게 말할 수 있다. scaffold02.py를 열고 무엇이 포함되어 있는지 확인해보자.

```python
import angr
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)
  initial_state = project.factory.entry_state()
  simulation = project.factory.simgr(initial_state)

  # Define a function that checks if you have found the state you are looking
  # for.
  def is_successful(state):
    # Dump whatever has been printed out by the binary so far into a string.
    stdout_output = state.posix.dumps(sys.stdout.fileno())

    # Return whether 'Good Job.' has been printed yet.
    # (!)
    return ???  # :boolean

  # Same as above, but this time check if the state should abort. If you return
  # False, Angr will continue to step the state. In this specific challenge, the
  # only time at which you will know you should abort is when the program prints
  # "Try again."
  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return ???  # :boolean

  # Tell Angr to explore the binary and find any state that is_successful identfies
  # as a successful state by returning True.
  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]
    print solution_state.posix.dumps(sys.stdin.fileno())
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

처음 4줄을 보면 거의 scaffold00.py와 거의 비슷하다. 우리가 분석할 바이너리의 경로를 줘 path_to_binary 변수를 편집하자.

```python
path_to_binary = "./02_angr_find_condition"
```

이제 `is_successful()` 함수를 볼 것이다. 이 함수가 해야하는 것은 "Good Job." 문자열을 출력하도록 이끄는 입력값의 state를 확인하고 true 또는 false를 반환해야 한다. 우리가 편집할 수 있다는 것을 알고있다. 

```python
def is_successful(state):
	stdout_output = state.posix.dumps(sys.stdout.fileno()) # (1)
    if b'Good Job.' in stdout_output: # (2)
    	return True # (3)
    else: return False
```

(1)에서 우리는 출력되는 stdout을 stdout_output 변수에 넣을 것이다. 이것은 문자열이 아니라 byte 객체인 것을 기억해라. 이는 (2)에서 'Good Job.' 대신 b'Good Job.'을 사용하여 'Good Job.'이라는 문자열이 출력되었는지 확인해야 하는 것을 의미한다. (3)에서는 우리가 원하는 문자열을 얻었을 때 True를 반환하고 이 경우가 아니면 False를 반환한다. 이제 우리가 원하지 않는 경로에 도달했을 때 출력되는 "Try again." 문자열로 같은 작업을 해야 한다.

```python
def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())   
    if b'Try again.' in  stdout_output:
      return True
    else: return False
```

보다시피 `is_successful()` 함수와 사실상 동일하다.

두 개의 함수들을 정의한 후에 angr의 마력을 발휘하여 그에게 우리가 관심있는 경로와 피해야할 경로를 말해줘야 한다.

```python
simulation.explore(find=is_successful, avoid=should_abort)
```

관심이 있거나 피하고 싶은 특정 주소(예: 내가 다루지 않은 주소)를 이미 정확히 지목한 경우, find 및 avoid 인수는 주소(또는 목록)가 될 수 있다. 이 경우 우리는 흥미로운 문자열을 출력하는 많은 state가 있기 떄문에 2가지 함수를 사용했다. 

그 후에 결과를 확인하고 우리가 원하는 것을 얻었는지 봐야 할 시간이다. 나는 더 이쁘게 출력하기 위해 print statement를 수정했다. 

```python
if simulation.found:
    solution_state = simulation.found[0]
    solution = solution_state.posix.dumps(sys.stdin.fileno())
    print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))

  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

이 코드는 정확이 scaffold00.py와 같다. 이것은 state가 "Good Job." 문자열에 도달한 상태가 있는지 확인하고 원하는 코드 경로로의 입력값(1개 이상이 될 수 있다, `simulation.found[0]`은 1번째 값) 중 하나을 출력한다. 여기 해결책 스크립트이다.

```python
import angr
import sys

def main(argv):
  path_to_binary = "./02_angr_find_condition"
  project = angr.Project(path_to_binary)
  initial_state = project.factory.entry_state()
  simulation = project.factory.simgr(initial_state)
  
  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Good Job.' in stdout_output:
      return True
    else: return False

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
   
    if b'Try again.' in  stdout_output:
      return True
    else: return False

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]
    solution = solution_state.posix.dumps(sys.stdin.fileno())
    print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))

  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

![2020-06-02-Introduction-to-angr-Part-1_0.png](/assets/img/angr/2020-06-02-Introduction-to-angr-Part-1_0.png)

이겼다. 하지만 특정 avoid를 지정하지 않고 find로만 스크립트를 실행했다면 무엇이 달라졌을까? 이 도전에 전혀 지장이 없는 아주 작은 프로그램이기 때문에 많이 달라지지 않는다. 그럼 더 복잡한 프로그램은 어떨까? 이전에 말한 heat death of the universe에 대한 내용을 기억하는가?  다음 도전으로 가자. 

## 03_angr_symbolic_registers

이 도전들을 아기걸음이다. 이제 우리는 실제로 angr 가지고 걷기 시작할 것이다. 하지만 첫째로 비밀을 말해줄 것이다: angr는 scanf로 호출되는 "복잡한" 포맷의 문자열들을 처리하지 못한다. 알겠다. 알겠다. 기다려봐라. 푹 빠져라. 응, 엉덩이가 아파. 하지만 우리는 symbolic 값들을 레지스터를 통해 주입하는 방법을 배울 기회로 삼을 수 있고, 우리는 빌어먹을 그럴 것이다. 

하지만 첫째로, 우리가 해결해야할 `main()` 함수를 보자. 

```c
undefined4 main(void)
{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18;
  undefined8 uVar4;
  
  printf("Enter the password: ");
  uVar4 = get_user_input();
  iVar1 = complex_function_1((int)uVar4);
  iVar2 = complex_function_2(local_18);
  iVar3 = complex_function_3((int)((ulonglong)uVar4 >> 0x20));
  if (((iVar1 == 0) && (iVar2 == 0)) && (iVar3 == 0)) {
    puts("Good Job.");
  }
  else {
    puts("Try again.");
  }
  return 0;
}
```

`get_user_input()` 함수와 `get_user_input()`의 출력물을 조작하는 3개의 함수 `complex_function_1(), complex_function_2(), complex_function_3()`가 있다. 이 특별한 함수들의 내용을 보고 입력을 어떻게 파싱하는지 보자.

```c
undefined8 get_user_input(void)
{
  int in_GS_OFFSET;
  undefined4 local_1c;
  undefined local_18 [4];
  undefined4 local_14;
  int local_10;
  
  local_10 = *(int *)(in_GS_OFFSET + 0x14);
  __isoc99_scanf("%x %x %x",&local_1c,local_18,&local_14);
  if (local_10 != *(int *)(in_GS_OFFSET + 0x14)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return CONCAT44(local_14,local_1c);
}
```

angr의 최고의 적  "복잡한" 포맷스트링이 있다. `scanf()` 함수가 호출되기 전 "%x %x %x"를 stack에 push한다. 이것은 16진수의 값을 입력으로 받는다는 의미이다. 다음 스크린샷을 보자.

![2020-06-02-Introduction-to-angr-Part-1_1.png](/assets/img/angr/2020-06-02-Introduction-to-angr-Part-1_1.png)

보이는가? 3개의 값이 EAX, EBX, EDX에 들어간다! 이것에 주목하는 것이 좋을것이다. 이제 우리는 입력이 어떻게 파싱되는지 파악했으니, scaffold03.py 스크립트를 보자.

```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = argv[1]
  project = angr.Project(path_to_binary)

  # Sometimes, you want to specify where the program should start. The variable
  # start_address will specify where the symbolic execution engine should begin.
  # Note that we are using blank_state, not entry_state.
  # (!)
  start_address = ???  # :integer (probably hexadecimal)
  initial_state = project.factory.blank_state(addr=start_address)

  # Create a symbolic bitvector (the datatype Angr uses to inject symbolic
  # values into the binary.) The first parameter is just a name Angr uses
  # to reference it.
  # You will have to construct multiple bitvectors. Copy the two lines below
  # and change the variable names. To figure out how many (and of what size)
  # you need, dissassemble the binary and determine the format parameter passed
  # to scanf.
  # (!)
  password0_size_in_bits = ???  # :integer
  password0 = claripy.BVS('password0', password0_size_in_bits)
  ...

  # Set a register to a symbolic value. This is one way to inject symbols into
  # the program.
  # initial_state.regs stores a number of convenient attributes that reference
  # registers by name. For example, to set eax to password0, use:
  #
  # initial_state.regs.eax = password0
  #
  # You will have to set multiple registers to distinct bitvectors. Copy and
  # paste the line below and change the register. To determine which registers
  # to inject which symbol, dissassemble the binary and look at the instructions
  # immediately following the call to scanf.
  # (!)
  initial_state.regs.??? = password0
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

    # Solve for the symbolic values. If there are multiple solutions, we only
    # care about one, so we can use eval, which returns any (but only one)
    # solution. Pass eval the bitvector you want to solve for.
    # (!)
    solution0 = solution_state.se.eval(password0)
    ...

    # Aggregate and format the solutions you computed above, and then print
    # the full string. Pay attention to the order of the integers, and the
    # expected base (decimal, octal, hexadecimal, etc).
    solution = ???  # :string
    print solution
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

좋다. 우선 첫째로, 이전에 했던 것처럼 바이너리의 경로를 설정하자. 그 후에 이번에는 `scanf()` 을 건너뛰고 싶기 때문에 프로그램 처음부터 시작하고 싶지 않다고 angr에게 말해야 한다. `start_address`가 `scanf()` 호출 직후에 명령 중 하나일 것이라고 생각하는 것은 당연하지만, 이는 우리가 ADD, ESP 0x10 명령어부터 시작한다는 것을 의미하며, NO BUENO는 이 명령이 `scanf()`에 의해 남겨진 더미를 치우고 우리는 `scanf()`를 전혀 호출하지 않기 때문이다.

함수가 전혀 호출되지 않으면 함수 호출 후 스택을 정리할 필요가 없다. 

이것은 또한 우리가 stack를 정리하지 않고 건너뛰고 바로 다음 명령인 0x08048937에 위치한 `MOV ECX, DWORD [EBP - 0x18]` **으로 start_address를 설정한다는 것을 의미한다. 당신 것은 변경될 수 있으니 이것을 처리해라.

편집: 안녕! 여기 미래에서 마지막이야. 모든 재미를 망치고 싶진 않지만, 어떻게 말할 수 있을까... 그 주소에서 angr를 시작한다면, 우리가 그 중간에 그 함수를 망치고 프로그램이 그것을 좋아하지 않기 때문에 그것은 효과가 없을 것이다. 그런 일을 하려면 당신이 먼저 stack을 설정해야 하는데 나는 너무 게을러 할 수 없다. (어쨌든 튜토리얼 다음 파트에서 할 것이다) 이것이 동작하게 하려면, `get_user_input()` 호출된 후 0x8048980에 위치한 `MOV DWORD [EBP - 0x14], EAX` 명령부터 분석을 시작했다. 이것은 단지 함수만 건너뛸 뿐이며 직접적으로 레지스터의 값을 설정하는 것이기 때문에 아무것도 변하지 않는다.

```python
start_address = 0x8048980
initial_state = project.factory.blank_state(addr=start_address)
```

entry_state() 대신 blank_state()를 사용한다는 것에 유의해라. addr=start_address를 blank_state()로 전달함으로써 우리는 그 특정 주소의 새로운 state를 생성해달라고 말하는 것이다.

이제, `get_user_input()`은 우리의 입력을 파싱하여 3개의 레지스터에 넣었다는 것을 기억하는가? 그렇다. 이제 프로그램에서 우리가 원하는 곳을 갈 수 있도록 그 입력을 만들어야 할 시간이다. 이렇게 하기위해 우리는 3개의 symbolic bitvector를 생성해야 한다. 주석에 언급되었듯이, symbolic bitvector는 프로그램에 symbolic 값을 inject 하기 위한 데이터 타입이다. 이것들은 angr가 풀어나갈 방적식의 "x"가 될 것이다. 우리는 claripy를 사용하여 `BVS()` 함수를 통해 3개의 bitvectors를 만들것이다. 이 함수는 2개의 인자를 취급한다: 1번째는 angr가 참조하기 위한 bitvector의 이름인 반면에 2번째는 bitvector 자신의 bits size이다. symbolic 값들이 레지스터에 저장되고 레지스터는 32bit long이기 때문에 bitvectors 도 32 bits이다.

```python
password_size_in_bits = 32
password0 = claripy.BVS('password0', password_size_in_bits)
password1 = claripy.BVS('password1', password_size_in_bits)
password2 = claripy.BVS('password2', password_size_in_bits)
```

자. 이제 우리는 3개의 sybolic bitvectors를 생성했고 그것들을 `EAX`, `EBX`, `EDX`에 넣을 차례이다. 이전에 생성한  `initial_state`를 수정하고 레지스터의 내용을 업데이트 한다. 다행히도, angr는 아주 현명한 방법을 제공한다.

```python
initial_state.regs.eax = password0
initial_state.regs.ebx = password1
initial_state.regs.edx = password2
```

자, 이전에 했던 거와 마찬가지로 우리는 `find`와 `avoid`를 정의한다.

```python
simulation = project.factory.simgr(initial_state) 

def is_successful(state):
  stdout_output = state.posix.dumps(sys.stdout.fileno())
  if b'Good Job.\n' in stdout_output:
    return True
  else: return False

def should_abort(state):
  stdout_output = state.posix.dumps(sys.stdout.fileno())
  if b'Try again.\n' in  stdout_output:
    return True
  else: return False 

simulation.explore(find=is_successful, avoid=should_abort)
```

자, 모든 것이 준비되었고, 해결책을 출력할 부분을 준비해야 할 시간이다. (해결책이 있기 때문에? 그치?)

```python
if simulation.found:
    solution_state = simulation.found[0]

    # Solve for the symbolic values. If there are multiple solutions, we only
    # care about one, so we can use eval, which returns any (but only one)
    # solution. Pass eval the bitvector you want to solve for.
    # (!) NOTE: state.se is deprecated, use state.solver (it's exactly the same).
    solution0 = format(solution_state.solver.eval(password0), 'x') # (1)
    solution1 = format(solution_state.solver.eval(password1), 'x')
    solution2 = format(solution_state.solver.eval(password2), 'x')

    # Aggregate and format the solutions you computed above, and then print
    # the full string. Pay attention to the order of the integers, and the
    # expected base (decimal, octal, hexadecimal, etc).
    solution = solution0 + " " + solution1 + " " + solution2 # (2)
    print("[+] Success! Solution is: {}".format(solution))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

좋아, 이제 조금 설명을 하겠다: (1)에서 이전에 inject 한 3가지 symbolic 값에 대한 solver 엔진의 `eval()` 함수를 호출한다. `format()`은 자동적으로 앞에 붙여진 "0x" 값을 지운다. (2)에선 3개의 해결책을 1개의 문자로 합치고, 그것을 출력한다. 여기 완성된 해결책이다. (주석 없이)

```python
import angr
import claripy
import sys

def main(argv):
  path_to_binary = "./03_angr_symbolic_registers"
  project = angr.Project(path_to_binary)

  start_address = 0x08048980  # address right after the get_input function call
  initial_state = project.factory.blank_state(addr=start_address)

  password_size_in_bits = 32
  password0 = claripy.BVS('password0', password_size_in_bits)
  password1 = claripy.BVS('password1', password_size_in_bits)
  password2 = claripy.BVS('password2', password_size_in_bits)

  initial_state.regs.eax = password0
  initial_state.regs.ebx = password1
  initial_state.regs.edx = password2

  simulation = project.factory.simgr(initial_state) 

  def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Good Job.\n' in stdout_output:
      return True
    else: return False

  def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    if b'Try again.\n' in  stdout_output:
      return True
    else: return False 

  simulation.explore(find=is_successful, avoid=should_abort)

  if simulation.found:
    solution_state = simulation.found[0]

    solution0 = format(solution_state.solver.eval(password0), 'x')
    solution1 = format(solution_state.solver.eval(password1), 'x')
    solution2 = format(solution_state.solver.eval(password2), 'x')

    solution = solution0 + " " + solution1 + " " + solution2  # :string
    print("[+] Success! Solution is: {}".format(solution))
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

![2020-06-02-Introduction-to-angr-Part-1_2.png](/assets/img/angr/2020-06-02-Introduction-to-angr-Part-1_2.png)

좋아. 그리고 컴퓨터 과학이 어떻게 이루어지는지 알아? 다음 게시판에서 stack frame을 구성하고 기능 중간에 점프하는 방법에 대해 알아볼거야. 

##### Resources
- [Introduction to angr Part 1](https://blog.notso.pro/2019-03-25-angr-introduction-part1/)