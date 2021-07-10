---
title: Asymmetric Tiling
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

2 * n 크기의 직사각형을 2 * 1 크기의 타일로 채우려고 한다. 타일들은 서로 겹쳐선 안되고, 90도로 회전해서 사용할 수 있다. 단 이 타일링 방법은 좌우 대칭이여서는 안된다.

n이 주어질 때 가능한 비대칭 타일링 방법의 수를 계산하는 프로그램을 만들면 된다. 방법의 수는 매우 클 수 있으므로 1,000,000,007로 나눈 나머지를 출력한다.

1. 입력의 첫 줄은 테스트 케이스 C(1<= C <= 50)
1. 각 테스트 케이스는 사각형의 너비 n(1 <= n <= 100)

## Solving

조금만 생각해보면 비대칭 타일링을 쉽게 풀이할 수 있다. 단순히 전체 타일링 개수에서 대칭 타일링 개수를 빼면 비대칭 방법의 수를 알아낼 수 있다.

넓이가 홀수인 경우 정가운데 세로 타일 하나로만 덮여야하고, 짝수인 경우 정가운데 가로 2줄이 타일로 덮거나, 아예 덮지 않는 경우가 있다. 이렇게 양 쪽으로 나눈 뒤 한쪽 방법의 타일링 개수를 세면 대칭되는 타일링 개수를 세는 것이므로 이것을 전체 타일링 수에서 빼면된다.

![asymmetric-tiling-1](/assets/img/problem-solving/asymmetric-tiling-1.png)

타일링 함수는 [tiling2](https://beomsu317.github.io/tiling2/)에서 구현한 방법을 사용한다. 

MOD를 더하는 이유는 결과가 -가 되는 경우를 방지하기 위함이다. 이 문제의 시간 복잡도는 tiling2와 같은 $ O(n) $이다.

```cpp
int asymmetric(int width){
    // 홀수인 경우 전체 타일링 개수(width)에서 width/2 한 개수를 빼고 MOD 연산
    if(width % 2 == 1){
        return (tiling(width) - tiling(width/2) + MOD) % MOD;
    }
    // 짝수인 경우 전체 타일링 개수(width)에서
    int ret = tiling(width);
    // 정가운데 가로 2줄이 덮는 경우 대칭되는 타일링 개수 제외
    ret = (ret - tiling(width/2) + MOD) % MOD;
    // 덮지않는 경우 대칭되는 타일링 개수 제외
    ret = (ret - tiling(width/2 - 1) + MOD) % MOD;
    return ret;
}
```

대칭 타일을 빼는 것 말고도 직접 비대칭 타일의 개수를 구하는 방법도 있다. 

비대칭 타일은 다음과 같은 4개의 패턴 중 하나이다. 양쪽 끝이 대칭인 경우와, 양쪽 끝이 대칭이 아닌 경우가 있는데 양쪽 끝이 대칭인 경우에는 `asymmetric2()`를 재귀 호출하여 해결하고 비대칭인 경우 `tiling()` 함수를 사용해 결과를 얻으면 된다.

![asymmetric-tiling-2](/assets/img/problem-solving/asymmetric-tiling-2.png)

```cpp
int asymmetric2(int width){
    if(width <= 2){
        return 0;
    }
    int &ret = cache2[width];
    if(ret != -1){
        return ret;
    }
    ret = asymmetric2(width - 2) % MOD;
    ret = (ret + asymmetric2(width - 4)) % MOD;
    ret = (ret + tiling(width - 3)) % MOD;
    ret = (ret + tiling(width - 3)) % MOD;
    return ret;
}
```

##### Resources
- [ASYMTILING](https://www.algospot.com/judge/problem/read/ASYMTILING)