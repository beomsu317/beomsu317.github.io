---
title: String Join
author: Beomsu Lee
category: [Algorithm, Greedy Algorithm]
tags: [algorithm, greedy algorithm]
math: true
mermaid: true
---

## Problem

$n$개의 문자열을 순서와 상관없이 합쳐 한 개의 문자열로 만들어야 한다. 이 때 전체 비용이 최소가 되는 프로그램을 만들면 된다. 예를 들어 {al,go,spot}이 있을 때 al + go(2 + 2 = 4)를 합치고 이를 spot(4 + 4 = 8)과 합치면 총 12의 비용이 드는 것이다.

1. 입력의 첫 줄에는 테스트 케이스의 수 $c(c <= 50)$
1. 각 테스트 케이스의 첫 줄에는 문자열의 수 $n(1 <= n <= 100)$
1. 각 테스트 케이스의 둘째 줄에는 $n$개의 정수로 각 문자열의 길이가 주어지며 문자열의 길이는 1000 이하

## Solving

항상 가장 짧은 두 개의 문자열을 합치면 탐욕 알고리즘을 통한 구현이 가능하다. 두 문자열을 합치고 나면 나머지 문자열들은 항상 최소 비용을 써서 합치는 것이 이득이며 이 알고리즘이 항상 최적의 방법을 찾아낸다는 것을 알 수 있다.

```cpp
int n,num[100];
int strcat(){
    // 우선순위 큐 생성 및 대입
    priority_queue<int, vector<int>,greater<int> > pq;
    for(int i=0;i<n;i++){
        pq.push(num[i]);
    }

    int ret = 0;
    // pq의 크기가 1이 될 때까지 반복
    while(pq.size() > 1){
        int min1 = pq.top(); pq.pop();
        int min2 = pq.top(); pq.pop();
        pq.push(min1 + min2);
        ret += min1 + min2;
    }

    return ret;
}
```

## References
- [STRJOIN](https://www.algospot.com/judge/problem/read/STRJOIN)