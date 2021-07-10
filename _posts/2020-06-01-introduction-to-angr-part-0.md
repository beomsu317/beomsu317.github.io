---
title:  Introduction to angr Part 0
author: Beomsu Lee
category: [Binary Analysis, Angr]
tags: [binary analysis, angr]
math: true
mermaid: true
---

나에겐 휴식이 필요하다. 꼭 필요하다. 하지만 CTF에서 angr 사용법을 배우지 못했다면 휴가를 가는 이유가 있을까? 잠깐, 너 지금 휴가 안 갈 이유가 없다고 말하는 거야? 음, 안됐네, 내가 이 시리즈를 시작히기 전에 미리 말해줬어야지.

농담을 뒤로하고(농담이 아니였다...) angr를 사용하는 방법에 관한 미니 시리즈가 될 것이다. 나는 최근에 angr를 배우고 사용하는 것을 시작했기 떄문에 더 잘 배우기 위해 [Feynman technique](https://fs.blog/2012/04/feynman-technique/)을 적용하기 위해 참고 자료로 이 글을 쓰고 있다. angr의 기본을 가르치기 위한 몇개의 challenge들을 포함하고 있는 [angr_ctf](https://github.com/jakespringer/angr_ctf)에 있는 멋진 자료들을 사용할 것이다.

하지만 시작하기 전에 angr가 뭐냐?

### Feynman technique

1. Choose a concept you want to learn about
2. Pretend you are teaching it to a student in grade 6
3. Identify gaps in your explanation; Go back to the source material, to better understand it.
4. Review and simplify (optional)

# Introduction

angr 개발자들의 말을 인용하면

> angr는 바이너리를 분석하기 위한 파이썬 프레임워크이다. 정적, 동적인 symbolic("concolic") 분석과 다양한 작업에 적용할 수 있도록 해준다.

이것은 기능성이 형편없고 학습이 어렵지만, 이는 특징의  양이 아니라 학습 자료의 부족이나 논리 정연한 학습 경로의 부족 떄문이다. 실제로 많은 CTF writeup 같은 것들이 많이 있지만 학습자 입장에서 그 이상은 많지 않다.

angr로 돌아가서, 언뜻 보기에 빛나는 것은 symbolic execution engine이다. 간단하게 얘기하자면, symbolic execution은 실제로 실행시키지 않고 입력을 특정 코드 경로를 알아내기 위해 프로그램을 분석하는 것을 의미한다. 가장 흔한 예로 문자열 입력을 받고 runtime에 문자열과 입력을 비교한 내용을 출력하는 프로그램이다. symbolic execution은 프로그램을 분석하여 방적식처럼 다뤄 방정식을 풀고 올바른 입력 문자열이 무엇인지 알려준다. 

angr_ctf repo에 symbolic execution의 흥미로운 set이 있으니 학문적인 부분은 너에게 맡기겠다. symbolic execution을 통해 너가 알아야 할 것은 프로그램의 어떤 부분(이 경우 입력)은 구체적인 값이 아니라 고등학교 방정식의 "x" 처럼 상징적인 것이기 때문에 symbolic execution이라고 하는 것이다. 우리는 실행 경로가 "constrain" 심볼이라고 말한다.

```c
int x;
scanf("%d", &x);

if ((x > 1) && (x < 10)) {
	puts("Success!!");
} 

else {
	puts("Fail.");
}
```

이 코드에서 `if` 문은 변수 x의 값을 제약한다. 우리는 "Success" 문자열로 이끄는 코드 경로에 흥미가 있다고 하자. 이를 취하려면 `x`는 1보다 크고 10보다 작아햐 하며, 이것이 성공 실행 경로에 필요한 제약이라는 것을 알고있다. symbolic execution engine은 symbol(그리스 문자 람다 λ)을 inject하고 실행을 거꾸로 하여 그 제약조건에 맞는 λ의 값을 찾는다.

여기서 강조하고자 하는것은 명시적으로 지시되지 않는 한 symbolic execution engine은 프로그램을 실행하지 않는다는 사실이다. symbolic execution은 코드의 모든 분기를 평가하기 때문에, 이것은 분기가 많은 큰 프로그램을 분석한다면 우리는 소위 "path explosion"이라고 불리는 것을 가질 수 있고, 어떤 경우에는 모든 것을 분석하는데 필요한 시간이 우주의 열사병이 걸리는 시간보다 더 클 수 있다는 것을 의미한다. (스포일러, 수십억년) 이는 모든 지점이 symbolic execution engine이 분석해야 하는 state의 양을 2배로 늘리기 때문에 발생한다.

## 00_angr_find

자 이제 우리의 손을 더럽힐 시간이다. 위의 ctf 레포지토리를 복사해라. 여기에 18개의 챌린지와 18개의 scaffoldXX.py 파일을 찾을 수 있으며, 도전과제에 대한 skeleton solutions들을 포함하고 있다. 1번째 도전과제는 00__angr__find이다. 이것은 문자열을 입력하여 그것이 맞는지 아닌지를 출력하는 꽤 간단한 바이너리이다. 앞서 지적한 바와 같이, "Good Job." 문자열로 이어지는 코드 경로에 흥미가 있다. 

![2020-06-01-Introduction-to-angr-Part-0_0.png](/assets/img/angr/2020-06-01-Introduction-to-angr-Part-0_0.png)

전형적인 접근 방법은 `complex_function()`을 열고 리버스 엔지니어링을 한다. 하지만 좋은 아이디어처럼 보이지 않는다.

![2020-06-01-Introduction-to-angr-Part-0_1.png](/assets/img/angr/2020-06-01-Introduction-to-angr-Part-0_1.png)

손으로 완료될 수 있지만

1. 이것은 지루하다.
2. CPU를 쓰지 않는다면 무슨 소용인가?
3. 우리는 게으르다.
4. 우리는 시간이 많지 않다.
5. angr

그래서 scaffold00.py 파일을 보자. (주석들을 다 편집했다.)

```python
import angr
import sys

def main(argv):
  path_to_binary = ???
  project = angr.Project(path_to_binary)
  initial_state = project.factory.entry_state()
  simulation = project.factory.simgr(initial_state)
  
  print_good_address = ???
  simulation.explore(find=print_good_address)
  
  if simulation.found:
    solution_state = simulation.found[0]
    print solution_state.posix.dumps(sys.stdin.fileno())
  
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

그것을 한 줄씩 분석해 우리가 어떻게 편집해서 해결책을 찾을 수 있는지 이해해보자.

```python
import angr
import sys
```

지금까지 좋다, angr과 sys 라이브러리는 import 한다. sys는 출력되는 stdout을 분석하기위해 필요하다.

```python
def main(argv):
  path_to_binary = ??? # (1)
  project = angr.Project(path_to_binary) # (2)
  initial_state = project.factory.entry_state() # (3)
  simulation = project.factory.simgr(initial_state) # (4)
```

여기 프로그램은 스크립트의 main() 함수를 선언한다. (1)은 해당 스크립트가 바이너리 프로그램을 찾을 수 있는 위치를 선언해준다. 그 후 (2)에  Project 객체의 생성하며, 이 바이너리에서 angr가 시작한다. (3) 스크립트는 프로그램의 entry point 지점의 state(snapshot 같은)를 생성하고 마침내 (4)에서 simgr() 함수에 initial_state를 인자로 넣어 호출함으로써 Simulation Manager 객체를 생성한다. 그것이 의미하는 것은 기본적으로 symbolic execution engine에게 프로그램의 entry point 부터 symoblic execution을 시작하라고 지시하는 것이다. 첫번째로 우리는 (1) 번째 라인을 편집하고 바이너리를 찾을 수 있도록 말해줄 것이다.

```python
path_to_binary = "./00_angr_find" # (1)
```

좋다. 다음 라인으로 가자.

```python
print_good_address = ??? (1)
simulation.explore(find=print_good_address) # (2)
```

이 라인들은 중요하다. `print_food_address` 변수는 "Good Job"을 출력하도록 이끄는 블록의 주소를 가지고 있다. 그리고 우리는 디스어셈블러를 통해 찾을 수 있다. (나는 바이너리 닌자로, 평소처럼)

![2020-06-01-Introduction-to-angr-Part-0_2.png](/assets/img/angr/2020-06-01-Introduction-to-angr-Part-0_2.png)

강조된 주소로 ???를 편집해보자. (2)에서 우리는 기본적으로 "재귀적으로 프로그램 트리를 보고 만약 이 주소로 가는 방법을 찾았으면 나에게 말해주지 않으시겠습니까?" 라고 engine에게 말하고 있으며. 그가 좋은 사람이기 때문에, angr는 이것을 해 줄 것이다. 스크립트의 마지막 줄까지.

```python
if simulation.found: # (1)
    solution_state = simulation.found[0] # (2)
    print solution_state.posix.dumps(sys.stdin.fileno()) # (3)
  
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

(1)에서 스크립트는 변수 `print_good_address`에서 이전에 정의된 주소로 도달하는 모든 state를 포함하는 목록이 실제로 어떤 것이 포함되어 있는지 점검한다. 경우에 따라 올바른 경로로 가는 입력값이 (2) `solution_state`에 할당되고 (3)에서 해당 입력값을 출력한다. 나머지 라인들은 원하는 주소에 도달하지 않은 경우 스크립트에서 호출하고 마지막 2줄은 이 스크립트를 실행한다.

현재 스크립트는 실행할 준비가 되었고, 이것은 "Good Job"을 출력하는 문자열을 출력해야 한다.

![2020-06-01-Introduction-to-angr-Part-0_3.png](/assets/img/angr/2020-06-01-Introduction-to-angr-Part-0_3.png)

그래, 내가 좀 속여서 출력을 좀 더 이쁘게 포맷했는데, 내가 프로그램을 실행하여 angr의 출력을 주면 원하는 결과를 얻을 수 있다는 것을 알 수 있다. 마지막 스크립트는 다음과 같다.

```python
import angr
import sys

def main(argv):
  path_to_binary = "./00_angr_find" # path of the binary program
  project = angr.Project(path_to_binary)
  initial_state = project.factory.entry_state()
  simulation = project.factory.simgr(initial_state)

  print_good_address = 0x8048678  # :integer (probably in hexadecimal)
  simulation.explore(find=print_good_address)
  
  if simulation.found:
    solution_state = simulation.found[0]
    solution = solution_state.posix.dumps(sys.stdin.fileno())
    print("[+] Success! Solution is: {}".format(solution.decode("utf-8")))
  
  else:
    raise Exception('Could not find the solution')

if __name__ == '__main__':
  main(sys.argv)
```

그리고 이것이 이 1번째 파트의 전부이다. 다음에 우리는 경로 폭발 문제에 대한 해결책을 찾고, 프로그램 내부에 주입할 symbolic buffer를 만드는 방법을 볼 것이다. cya!

##### Resources 
- [Introduction to angr Part 0](https://blog.notso.pro/2019-03-20-angr-introduction-part0/)