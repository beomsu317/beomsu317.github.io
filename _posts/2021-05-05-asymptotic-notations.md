---
title: Asymptotic Notations
author: Beomsu Lee
category: [Algorithm, Asymptotic Analysis]
tags: [algorithm, asymptotic notations]
math: true
mermaid: true
---

점근 표기법은 알고리즘의 시간 복잡도를 나타낸다. 다음 3개의 점근 표기법은 주로 알고리즘의 시간 복잡도를 나타내는데 사용한다.

## $\Theta$ Notation

![AlgoAnalysis-1](/assets/img/algorithm/AlgoAnalysis-1.png)

세타 표기법은 함수 위와 아래서 바운드 되기 때문에 정확한 점근적 행동을 정의한다. 식의 세타 표기법을 얻는 간단한 방법은 낮은 차수의 항을 삭제하고 상수를 무시하는 것이다. 예를 들면 다음과 같다.

$ 3n^3 + 6n^2 + 6000 = \Theta (n^3) $

낮은 차수의 항을 버리는 것은 문제가 되지 않는다. $\Theta (n^3)$는 관련된 상수에 관계 없이 $\Theta (n^2)$보다 높은 값이 가지기 때문이다. 

주어진 함수 $g(n)$에 대해, 함수 집합을 $\Theta (g(n))$로 나타낸다.

> $\Theta (g(n))$ = { $f(n)$ : there exist positive constants c1, c2 and n0 such that 0 <= $c1*g(n)$ <= $f(n)$ <= $c2*g(n)$ for all n >= n0 } 


위 정의는, $f(n)$이 $g(n)$의 세타라면, $f(n)$의 값은 항상 $c1g(n)$과 $c2g(n)$ 사이에 있음을 의미한다($n >= n0$). 세타의 정의는 또한 $n0$보다 큰 값의 경우 $f(n)$이 음수가 아니여야 한다.

## Big O Notation

![AlgoAnalysis-2](/assets/img/algorithm/AlgoAnalysis-2.png)

Big O 표기법은 알고리즘의 상한을 정의하며, 함수 위에서 바운드된다. 선택 정렬을 예로 들면, Best Case에서 선형 시간이 걸리고, Worst Case에서는 제곱의 시간이 걸린다. 따라서 삽입 정렬의 시간 복잡도는 $O(n^2)$이라고 할 수 있다. $O(n^2)$는 선형 시간도 포함된다. 

선택 정렬의 시간 복잡도를 나타내기 위해 세타 표기법을 사용하면, Worst, Best Cases 2가지를 사용해야 한다.

1. 선택 정렬의 Worst Case 시간 복잡도는 $\Theta (n^2)$
1. 선택 정렬의 Best Case 시간 복잡도는 $\Theta (n)$

Big O 표기법은 알고리즘의 상한 시간 복잡도를 알고 있을 때 유용하다. 단순히 알고리즘을 살펴봄으로써 상한을 쉽게 찾을 수 있다.

> $O(g(n))$ = { $f(n)$: there exist positive constants $c$ and $n0$ such that $0 <= f(n) <= c*g(n)$ for all $n >= n0$ }


## $\Omega$ Notation

![AlgoAnalysis-3](/assets/img/algorithm/AlgoAnalysis-3.png)

Big O 표기법은 함수의 상한 바운드만 제공한다면, Omega 표기법은 하한 바운드만을 제공한다. Omega 표기법은 알고리즘의 하한 시간 복잡도를 알 경우 유용하다. 알고리즘의 Best Case 성능이 보통 유용하지 않으며, Omega 표기법도 3가지 표기법 중 가장 적게 사용된다.

주어진 함수 $g(n)$에 대해, 함수 집합을 $\Omega (g(n))$로 나타낸다.

> $\Omega (g(n))$ = { $f(n)$: there exist positive constants $c$ and $n0$ such that $0 <= c*g(n) <= f(n)$ for all $n >= n0$ }


선택 정렬을 예로 들면, 시간 복잡도는 $\Omega (n)$이지만, 일반적으로 Worst Case의 경우와 때로는 평균적인 경우에 관심이 있기 때문에 삽입 정렬에 대한 유용한 정보는 아니다.

## Properties of Asymptotic Notations

이 3가지 표기법에 대한 속성을 알아보자.

### General Properties

$f(n)$이 $O(g(n))$이면 $a*f(n)$도 $O(g(n))$이다. 세타와 오메가 표기법도 이 속성을 만족한다. 

### Transitive Properties

$f(n)$이 $O(g(n))$이고 $g(n)$이 $O(h(n))$이라면 $f(n) = O(h(n))$이다. 세타와 오메가 표기법도 이 속성을 만족한다.

### Reflexive Properties

$f(n)$이 주어지면 $f(n)$은 $O(f(n))$이다. $f(n)$의 최대 값은 $f(n)$ 자체가 될 것이다. 따라서 $x=f(n), y=O(f(n))$은 항상 반사적 관계로 연결된다. 세타와 오메가 표기법도 이 속성을 만족한다.

### Symmetric Properties

$f(n)$이 $\theta (g(n))$이면 $g(n)$은 $\theta (f(n))$이다. 이 속성은 세타 표기법만 만족한다.

### Transpose Symmetric Properties

$f(n)$이 $O(g(n))$이면 $O(g(n))$은 $\omega (f(n))$이다. 이 속성은 $O, \theta$만 만족한다.

### Some More Properties

$f(n)= O(g(n)), f(n) = \omega (g(n))$이면, $f(n) = \theta (g(n))$이다.

$f(n) = O(g(n)), d(n)=O(e(n))$이면 $f(n) + d(n) = O(max(g(n),e(n)))$이다.

$f(n) = O(g(n)), d(n)=O(e(n))$이면 $f(n) \cdot d(n) = O(g(n) \cdot e(n))$이다.


## References
- [Asymptotic Notations](https://www.geeksforgeeks.org/analysis-of-algorithms-set-3asymptotic-notations/)
