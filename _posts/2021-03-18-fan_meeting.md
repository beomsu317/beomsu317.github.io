---
title: Fan Meeting
author: Beomsu Lee
category: [Algorithm, Divide and Conquer]
tags: [algorithm, divide and conquer]
math: true
mermaid: true
---


## Problem

아이돌 그룹인 하이퍼시니어가 팬 미팅을 진행한다. 팬 미팅의 한 순서로, 참가한 팬들과 포옹을 하는 행사를 갖는다. 팬 미팅에 참석자들은 오른쪽부터 시작해 한 명씩 왼쪽으로 움직이며 포옹을 한다.

```
a b c d           a b c d
---------   ->  ---------
0 1 2 3 4       0 1 2 3 4
```

하지만 하이퍼시니어 남성 멤버들은 남성과 포옹하기 꺼려하여 남성과 남성끼리는 포옹하지 않는다. 팬이나 멤버 중 여성이 1명이라도 있다면 포옹을 하는 것이다.

1. 첫 줄에 테스트 케이스 C (C <= 20)
1. 테스트 케이스의 첫째 줄은 멤버의 성별을 나타내는 문자열 (ex. MMMFFF)
1. 테스트 케이스의 둘째 줄은 팬의 성별을 나타내는 문자열 (ex. FFFMMM)
1. 멤버와 팬의 수는 1 이상 200,000 이하의 정수이며 멤버는 항상 팬의 수 이하

## Solving

단순하게 풀이한다면 모든 방법의 수를 시뮬레이션 하는 것이다. 팬의 수를 N, 멤버의 수를 M이라 하면, 대략 O(NM-M^2)의 시간 복잡도를 가지게 되는데, 멤버와 팬의 수가 20만 가까이 되면 시간 내 풀기 어려워진다. 

하지만 이 문제를 곱셈으로 변형하게 되면 생각보다 쉽게 풀어낼 수 있다.

```
                          A2   A1   A0
         x B5   B4   B3   B2   B1   B0
         ------------------------------
                         A2B0 A1B0 A0B0
                    A2B1 A1B1 A0B1
               A2B2 A1B2 A0B2
          A2B3 A1B3 A0B3
     A2B4 A1B4 A0B4                  
A2B5 A1B5 A0B5
----------------------------------------
 C7   C6   C5   C4   C3   C2   C1   C0
```

$ C_i = A_0*B_i + A_1*B_{i-1} + A_1*B_{i-2} $

이 방식을 사용하여 일렬로 사람들의 성별을 1은 남자, 0은 여자로 표시한다. 남자와 남자와 포옹하지 않는 경우 1이상이 되며 나머지의 경우 0이 된다. 따라서 $ C_i $가 0이라면 모든 멤버가 포옹을 한 경우라고 할 수 있다.

일반적인 곱셈을 이용한다면 시간이 오래 걸릴 수 있으므로 [카라츠바 알고리즘](https://beomsu317.github.io/karatsuba/)을 이용할 것이다.

```cpp
int solve(const string &members, const string &fans)
{
    int N = members.size(), M = fans.size();
    vector<int> A(N), B(M);
    // A원소와 B원소의 순서가 바뀌여 있음
    for (int i = 0; i < N; i++) 
        A[i] = (members[i] =='M') ? 1 : 0;
    for (int i = 0; i < M; i++)
        B[M-i-1] = (fans[i] == 'M') ? 1 : 0;

    // 카라츠바 알고리즘을 이용해 곱셈
    vector<int> C = karatsuba(A, B);
    int res = 0;
    for (int i = N - 1; i < M; i++) {
        // 0인 경우 포옹
        if (C[i] == 0) res++;
    }
    return res;
}
```

##### Resources
- [FANMEETING](https://www.algospot.com/judge/problem/read/FANMEETING)