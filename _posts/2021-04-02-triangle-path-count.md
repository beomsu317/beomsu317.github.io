---
title: Triangle Path Count
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

```
9
5 7
1 3 2 
3 5 5 6
```

위와 같이 삼각형 모양으로 배치된 자연수들이 있다. 맨 위 숫자부터 한 번에 한 칸씩 아래로 내려가는 경로를 만드는데 아래 줄로 갈 때마다 바로 아래 숫자 또는 오른쪽 아래 숫자로 내려갈 수 있다.

이 때 숫자의 합의 가장 큰 경로는 하나가 아니라 여러개일 수 있다. 예를 들어 {9, 7, 2, 6}과 {9, 7, 3, 5}의 합이 같고 최대인 경우이다. 삼각형이 주어질 때 합이 최대인 경로의 개수를 구하면 된다.

1. 입력의 첫 줄은 테스트 케이스 C(C <= 50)
1. 각 테스트 케이스의 첫 줄은 삼각형의 크기 n(2 <= n <= 100)
1. 그 후 n줄에는 각 1개 ~ n개의 숫자로 삼각형의 각 가로줄에 있는 숫자가 왼쪽부터 주어지며 각 숫자는 1 이상 1000 이하의 자연수

## Solving

2개의 다른 동적 계획법을 이용해 풀이가 가능하다. (0,0)에서 시작하는 최대 경로는 (1,1)으로 내려가며 (1,1)에서 시작하는 최대 경로는 두 칸에서 만들 수 있는 최대 경로의 합이 동일하기 때문에, 어느 쪽으로 내려가도 최대 경로를 만들 수 있다. 이 두 위치에서 시작하는 최단 경로의 개수를 더한 것이 (1,1)에서 시작하는 최대 경로의 개수가 된다.

```
24
13  15
6  8  8
3  5  5  6
```

이를 점화식으로 표현하면 다음과 같다.

$ count(y,x) = max(count(y+1,x),(path(y+1,x) > path(y+1,x+1))) $
$ ~~~~~~~~~~~~~~~~~~~~~~~~ max(count(y+1,x),(path(y+1,x) < path(y+1,x+1))) $
$ ~~~~~~~~~~~~~~~~~~~~~~~~ max(count(y+1,x)+count(y+1,x+1),(path(y+1,x)==path(y+1,x+1))) $

먼저 `path()`에서 최대 합을 재귀로 구현한다.

```cpp
int cache[100][100];
int path(int y,int x){
    if(y >= n){
        return 0;
    }
    // 메모제이션
    int &ret = cache[y][x];
    if(ret != -1){
        return ret;
    }
    // 합의 최대를 구한다.
    ret = max(path(y+1,x),path(y+1,x+1)) + triangle[y][x];
    return ret;
}
```

그 후 `count()`에서 구해진 최대 합을 이용해 재귀 호출하여 경로의 수를 구하면 된다.

```cpp
// 삼각형의 깊이
int n;
// 삼각형
vector<vector<int>> triangle;
int countCache[100][100];
int count(int y,int x){
    if(y == n-1){
        return 1;
    }
    // 메모제이션
    int &ret = countCache[y][x];
    if(ret != -1){
        return ret;
    }
    ret = 0;
    // y+1, x 의 합이 y+1, x+1 합보다 큰 경우
    if(path(y+1,x) >= path(y+1,x+1)){
        ret += count(y+1,x);
    }
    // y+1, x 의 합이 y+1, x+1 합보다 작은 경우
    if(path(y+1,x) <= path(y+1,x+1)){
        ret += count(y+1,x+1);    
    }
    return ret;
}
```


##### Resources
- [TRIPATHCNT](https://www.algospot.com/judge/problem/read/TRIPATHCNT)