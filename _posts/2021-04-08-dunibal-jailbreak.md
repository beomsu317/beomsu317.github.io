---
title: Dr. Dunibal's Jailbreak
author: Beomsu Lee
math: true
mermaid: true
tags: [dynamic programming]
---

## Problem

살인마 두니발 박사가 감옥에서 탈출했다. n개 마을들이 있는 지도에서 d일이 지난 후 두니발 박사가 임의의 선택한 마을에 있을 확률을 계산하는 프로그램을 만들면 된다.

1. 입력의 첫 줄에는 테스트 케이스의 수 c(1 <= c <= 50)
1. 각 테스트 케이스의 첫 줄에는 마을의 수 n(2 <= n <= 50), 지난 일 수 d(1 <= d <= 100), 교도소가 있는 마을의 번호 p(0 <= p <= n)
1. 다음 줄부터 n 개의 정수로 행렬이 주어짐
1. 그 다음 줄에는 확률을 계산할 마을의 수 t(1 <= t <= n)
1. 그 다음 줄에는 t개의 정수로 확률을 계산할 마을의 번호 q(0 <= q < n)

## Solving

`deg[]`에 미리 계산해둔 값을 담으면 쉽게 확률을 계산할 수 있다.

```cpp
for(int i=0;i<n;i++){
    for(int j=0;j<n;j++){
        deg[i] += connected[i][j];
    }
}
```

`path`를 인자로 받아 계산을 하는 완전 탐색 알고리즘이다. 이대로 구현한다면 메모제이션 적용이 어렵다. 

```cpp
int n, d, p, t, q;
int connected[51][51], deg[51];
double search(vector<int> &path){
    // d일이 지난 경우
    if(path.size() == d + 1){
        // q가 아니면 0.0 반환
        if(path.back() != q) return 0.0;
        double ret = 1.0;
        // path의 출현 확률을 계산
        for(int i = 0 ; i + 1 < path.size() ; i++){
            ret /= deg[path[i]];
        }
        return ret;
    }
    double ret = 0;
    for(int i = 0 ; i < n ;i++){
        // 연결된 마을이 있는 경우
        if(connected[path.back()][i]){
            // path에 마을 push 
            path.push_back(i);
            // search 재귀 호출하여 얻은 값의 반환 값을 더해준다.
            ret += search(path);
            path.pop_back();
        }
    }
    return ret;
} 
```

`path` 대신 현재 위치 `here`과 탈옥 후 지난 날짜 `days`를 재귀 호출에 전달하여 현재 위치에서 시작해 남은 날짜 동안 움직여 q에 도달할 확률을 구하는 방법으로 구현할 수 있다. 앞으로 하는 선택들의 확률을 구하는 방식으록 구현되는 것이다. 이렇게 구현할 경우 시간 복잡도는 $ O(n^2dt) $이다. 

$ search2(here, days) = \frac {\sum_{there \in adj(here)} search2(there,days+1)}{|adj[here]|} $

```cpp
int n, d, p, t, q;
int connected[51][51], deg[51];
double cache[51][101];
double search2(int here,int days){
    // d일인 경우 here이 q이면 1.0 반환
    if(days == d) return (here == q ? 1.0 : 0.0);
    double &ret = cache[here][days];
    if(ret != -1.0) return ret;
    ret = 0.0;
    for(int there = 0; there< n;there++){
        // 마을이 연결되어 있으면
        if(connected[here][there]){
            // 연결된 마을과 days에 +1하여 인자로 전달 후 반환값을 인접한 마을의 개수로 나눠주고 결과를 ret에 더함
            ret += search2(there,days+1) / deg[here];
        }
    }
    return ret;
}
```

하지만 이 방법보다 더 빠르게 구현할 수 있는 방법이 존재한다. 계산의 순서를 바꾸어 q부터 경로를 만들어 나가면 문제가 훨씬 간단해진다. `search3()`는 박사가 전날 어디 숨어있는지 결정하면서 확률을 계산해나간다. 이 때의 점화식은 다음과 같다. 

$ search3(here, days) = \sum_{there \in adj(here)} {\frac {1}{adj(there)}} search3(there,days-1) $

이렇게 구현한 경우 시간 복잡도는 $ O(n^2d) $가 된다.

```cpp
int n, d, p, t, q;
int connected[51][51], deg[51];
double cache[51][101];
double search3(int here,int days){
    // 0일인 경우
    if(days == 0) return (here == p ? 1.0 : 0.0);
    double &ret = cache[here][days];
    if(ret != -1.0) return ret;
    ret = 0.0;
    for(int i = 0;i < n;i++){
        if(connected[here][i]){
            ret += search3(i,days-1) / deg[i];
        }
    }
    return ret;
}
```

##### Resources
- [NUMB3RS](https://www.algospot.com/judge/problem/read/NUMB3RS)