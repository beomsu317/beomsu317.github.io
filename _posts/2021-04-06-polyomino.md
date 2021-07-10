---
title: Polyomino
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

정사각형의 변들을 서로 완전하게 붙여놓은 도형을 폴리오미노라 한다. n개의 정사각형으로 구성된 폴리오미노들을 만들려고 하는데, 이 중 세로로 단조(monotone)인 폴리오미노의 수가 몇 개인지 계산하는 프로그램을 만들면 된다. 세로로 단조란 어떤 가로줄도 폴리오미노를 두 번 이상 교차하지 않는다는 뜻이다.

![polyomino](/assets/img/problem-solving/polyomino.png)

1. 입력의 첫 줄은 테스트 케이스 C(1 <= C <= 50)
1. 각 테스트 케이스는 폴리오미노를 구성할 정사각형의 수 n(1 <= n <= 100)

## Solving

세로 단조임으로 가로줄에 포함된 정사각형들은 일렬로 연속되어 있다. 따라서 각 가로줄마다 몇 개의 정사각형을 넣을지 결정하여 폴리오미노를 만들 수 있다.

첫 번째 줄에 하나의 정사각형만 들어간다면 다음과 같은 2가지 방법밖에 없다. 

![polyomino2](/assets/img/problem-solving/polyomino2.png)

경우의 수를 계산하기 위해선 나머지 사각형으로 만든 폴리오미노의 첫 번째 줄의 정사각형의 수 별로 폴리오미노의 수를 반환받아야 한다. 

>poly(n, first) = n개의 정사각형을 포함하되, 첫 줄에 first개의 정사각형이 들어가는 폴리오미노의 수

다음과 같은 식으로 표현할 수 있다.

$ poly(n - first,1) + poly(n - first, 2) + ... + poly(n - first, n - first) $

이 때 두 번째 줄에 있는 정사각형의 수에 따라 이들을 붙일 수 있는 방법의 수가 정해진다. 첫 줄에 1개의 정사각형이 있고, 나머지 사각형이 2라면 
**1 + 2 - 1 (first + second - 1)**이 성립한다. 따라서 위의 식에 각 항마다 폴리오미노들을 붙일 수 있는 방법의 수를 곱해 주면 다음과 같은 식을 얻을 수 있다.

$ first * poly(n - first, 1) + (first + 1) * poly(n - first, 2) + ... + (n - 1) * poly(n - first, n - first)  $

이 때 n, first 각각 0 ~ 100 범위 내 정수이므로 다음 점화식을 통해 메모제이션을 구현할 수 있다.

$ poly(n, first) = \sum_{second=1}^{n - first} (first + second - 1) * poly(n - first, second) $

가능한 n과 first의 조합의 수는 $ O(n^2) $이고, poly()를 한 번 계산하는 데는 $ O(n) $의 시간이 들기 때문에 전체 시간 복잡도는 $ O(n^3) $이 된다.

```cpp
int MOD = 10 * 1000 * 1000;
int cache[101][101];
int poly(int n,int first){
    if(n == first) return 1;
    int &ret = cache[n][first];
    if(ret != -1){
        return ret;
    }
    int ret = 0;
    for(int second = 1 ; second <= n - first ; second++){
        // 첫 째 사각형과 나머지 사각형의 조합의 수 계산
        int add = second + first - 1;
        // 나머지 사각형에 대해 나온 값들은 곱함
        add *= poly(n - first,second);
        add %= MOD;
        ret += add;
        ret %= MOD;
    }
    return ret;
}
```

메인 쪽에서도 1부터 n까지 결과를 더해줘야 한다.

```cpp
for(int i=1;i<=n;i++){
    sum += poly(n,i);
    sum %= MOD;
}
```

##### Resources
- [POLY](https://www.algospot.com/judge/problem/read/POLY)