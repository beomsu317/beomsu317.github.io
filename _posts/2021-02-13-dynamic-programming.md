---
title:  Dynamic Programming
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

동적 계획법은 큰 문제를 여러 개의 하위 문제로 나누어 풀고, 이것을 결합하여 최종적으로 목표를 달성하는 알고리즘이다. 

## Overwrapping Subproblems

분할 정복과 비슷하게 하위 문제들로 나누고 결합하는 방식이다. 동적 계획법은 주로 하위 문제들이 반복적으로 일어나는 경우 사용한다. 한 번 계산된 하위 문제들이 테이블에 저장되며 다시 계산될 필요가 없다. 따라서 하위 문제들이 중복되지 않으면 동적 계획법은 쓸모가 없어지게 된다.

예시로 피보나치 수열이 존재한다. 다음과 같이 피보나치 수열을 재귀를 통해 계산한다고 가정해보자.

```cpp
#include <iostream>

int fibo(int n){
    if(n <= 2){
        return 1;
    }
    return fibo(n-1)+fibo(n-2);
}

int main(){
    printf("%d\n",fibo(5));
}
```

다음과 같은 순서로 계산되며 `fibo(3)`이 2번 호출되었다. 만약 `fibo(3)`의 계산이 저장되어 있다면 저장된 값을 재사용하여 계산적인 코스트를 줄일 수 있다.

1. fibo(5)
1. fibo(4) + fibo(3)
1. (fibo(3) + fibo(2)) + (fibo(2) + fibo(1))
1. ((fibo(2) + fibo(1)) + (fibo(1) + fibo(0))) + ((fibo(1) + fibo(0)) + fib(1))
1. (((fibo(1) + fibo(0)) + fibo(1)) + (fibo(1) + fibo(0))) + ((fibo(1) + fibo(0)) + fibo(1))

값을 저장하는 방법에 따라 Memoization(Top Down), Tabulation(Buttom Up)으로 분류할 수 있다.

### Memoization(Top Down)

메모제이션은 룩업 테이블을 NIL로 초기화 후 하위 문제들을 해결할 때 룩업 테이블을 먼저 확인한다. 미리 계산된 값이 있다면 그 값을 반환하고 아니면 나중에 재사용할 수 있도록 값을 룩업 테이블에 저장한다.

```cpp
#include <iostream>
#define NIL -1

int lookup[100];

void _init(){
    for(int i=0;i<sizeof(lookup)/sizeof(int);i++){
        lookup[i] = NIL;
    }
}

int fibo(int n){
    if(lookup[n] != -1){
        if(n <= 2){
            lookup[n] = 1;
        }else{
            lookup[n] = fibo(n-1)+fibo(n-2);
        }
        return lookup[n];
    }
}

int main(){
    _init();
    printf("%d\n",fibo(5));
    return 0;
}
```

### Tabulation(Bottom Up)

타뷸레이션은 하위 문제들을 풀어나가면서 큰 목표를 달성하는 것이다. 다음은 타뷸레이션 버전의 피보나치 수열을 구하는 코드이다.

```cpp
#include <iostream>

int fibo(int n){
    int f[n+1] = {};
    f[0]=0;
    f[1]=1;
    for(int i=2;i<=n;i++){
        f[i] = f[i-1] + f[i-2];
    }
    return f[n];
}

int main(){
    printf("%d\n",fibo(5));
    return 0;
}
```

메모제이션과 타뷸레이션은 모두 하위 문제를 푸는 방식이다. 메모제이션의 테이블은 요구에 의해 채워지지만 타뷸레이션은 처음부터 시작해 하나씩 채워간다. 타뷸레이션과 다르게 메모제이션의 룩업 테이블은 필수적으로 채워지지 않는다.

## Optimal Substructure

최단 경로 문제는 최적 부분 구조(Optimal Substructure)의 특성이다. 
- 만약 u에서 v로 이동하는데 x를 거쳐야 한다면 
- u에서 x로, x에서 v로 가야한다.

u -> v 로 가기위해 x 가 존재한다. 

반면에 최장 경로 문제는 최적 부분 구조의 특성이 아니다. 다음 그래프의 q 와 t 사이 최단 경로는 `q -> r -> t` 또는 `q -> s -> t` 이다. 하지만 최장 경로는 `q -> r -> t` 이다. 그런데 q 와 r 사이 최장 경로는 `q -> r` 이 아닌 `q -> s -> t -> r` 이 된다. 따라서 최장 경로를 찾는 문제는 최적 부분 구조의 특성을 가지지 않으며 하위 문제들의 결과로부터 큰 문제의 해를 언제나 만들 수 없다는 사실을 보여준다.

```
q -- r
|    |
s -- t
```

##### Resources
- [Dynamic Programming](https://www.geeksforgeeks.org/dynamic-programming/)
- [Memoization](https://en.wikipedia.org/wiki/Memoization)