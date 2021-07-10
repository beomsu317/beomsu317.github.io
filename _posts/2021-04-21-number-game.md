---
title: Number Game
author: Beomsu Lee
tags: [dynamic programming]
---

## Problem

n개의 정수를 일렬로 늘어놓은 게임판을 가지고 2명이 시작한다. 각 참가자는 자기 차례마다 다음 두 가지 일 중 하나를 선택해 수행해야 한다.

- 게임판의 왼쪽 끝에 있는 숫자나 오른쪽 끝의 숫자를 가져간다. 가져간 숫자는 게임판에서 지워진다.
- 게임판에 두 개 이상 숫자가 있을 때, 왼쪽 끝에서 2개 혹은 오른쪽 끝에서 2개를 지운다.

게임은 숫자가 모두 없어지면 끝나며, 각 참가자의 점수는 자신들이 가져간 숫자의 합이다. 두 사람 모두 최선을 다할 때, 두 사람의 최종 점수 차이는 얼마인지 구하는 프로그램을 만들면 된다.

1. 입력의 첫 줄은 테스트 케이스의 수 C(C <= 50)
1. 각 테스트 케이스의 첫 줄에는 게임판의 길이 n(1 <= n <= 50)
1. 그 다음 줄에 n개의 정수로 게임판의 숫자들이 순서대로 주어지며 각 숫자는 -1,000에서 1,000 사이 정수

## Solving

`play(state)`라는 형태의 함수가 있다고 가정하자. `state`는 게임판의 남은 수들이며, (이번 차례의 참가자의 점수) - (다른 참가자의 점수)의 최대치를 반환한다.

예를 들어, 서하랑 현우가 게임을 한다고 하자. 이번이 서하 차례인 경우 4가지 동작들을 하나하나 해보면서 `play()`를 호출하면, 각 경우에 대해 (현우 점수) - (서하 점수)를 얻을 수 있다. 원하는 값은 (서하 점수) - (현우 점수)이니, 각 경우의 부호를 뒤집으면 값을 구할 수 있다.

게임의 상태를 표현하기 위해 현재 남은 숫자들 중 맨 왼쪽과 맨 오른쪽 숫자의 위치를 사용한다. 그럼 다음과 같은 점화식을 얻을 수 있다.

$$
play(left,right) = max
\cases{
board[left]-play(left+1,right) \\
board[right]-play(left,right-1) \\
-play(left+2,right) & (right - left >= 1) \\
-play(left,right-2) & (right - left >= 1) \\
}
$$

반환 값이 -1인 경우도 있기 때문에 -50,000 ~ 50,000 범위 밖의 `EMPTY`를 구현해 이용한다. 이렇게 구현한 경우 $ O(n^2) $의 부분 문제를 갖고 있고 각각 계산하는데 $ O(1) $ 시간이 걸리기 때문에 $ O(n^2) $ 시간이 걸린다.

```cpp
const int EMPTY=-987654321;
int n;
int board[50], cache[50][50];
int play(int left,int right){
    // base case : 모든 수가 다 없어졌을 때
    if(left > right)
        return 0;
    // 메모제이션
    int &ret = cache[left][right];
    if(ret != EMPTY)
        return ret;
    // 수를 가져가는 경우
    ret = max(board[left] - play(left + 1, right),board[right] - play(left,right - 1));
    // 수를 없애는 경우
    if(right - left + 1 >= 2){
        ret = max(ret,-play(left,right - 2));
        ret = max(ret,-play(left + 2,right));
    }
    return ret;
}
```


##### Resources
- [NUMBERGAME](https://www.algospot.com/judge/problem/read/NUMBERGAME)