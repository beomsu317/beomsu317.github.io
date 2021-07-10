---
title: DARPA Grand Challenge
author: Beomsu Lee
tags: [dicision problem]
---

## Problem

DARPA Grand Challenge는 운전자 없는 차들을 인공지능으로 조작해 누가 먼저 결승에 도달하는지를 겨루는 대회이다. 2004년의 과제는 240km의 도로를 완주하는 것이었다. 이 경기를 $N$개의 카메라로 중계하려고 한다. 이 도로에 카메라를 설치할 수 있는 부분이 $M$군데 존재한다. 여기에 카메라를 배치해, 가장 가까운 두 카메라 간의 간격을 최대화하는 프로그램을 만들면 된다.

1. 입력의 첫 줄에는 테스트 케이스의 수 $C(<=50)$
1. 각 테스트 케이스의 첫 줄에는 카메라의 수 $N(<=100)$과 설치 가능한 중계소의 수 $M(N<=M<=200)
1. 그 다음 줄에는 $M$개의 실수로, 카메라를 설치할 수 있는 곳의 위치가 오름차순으로 주어짐

## Solving

결정 문제로 풀이할 경우 "최소 간격이 `gap`인 방법이 있는가?"가 아니라 "카메라들 간 최소 간격이 `gap` 이상인 방법이 있는가?"로 질문을 던져야 한다. 후자의 질문에 대한 대답을 통해 이분법으로 풀어 답을 정확하게 맞출 수 있다.

결정 문제를 통해 풀이한다면 다음과 같은 2개의 함수를 정의할 수 있다. 

> `decision(locations, cameras, gap)` = 카메라를 설치할 수 있는 위치 `locations`와 카메라의 수 `cameras`가 주어질 때, 이들을 배치해 모든 카메라의 간격이 `gap` 이상이 되면 참, 아니면 거짓을 반환

```cpp
bool decision(const vector<double>& location, int cameras,double gap){
    double limit = -1;
    int installed = 0;
    for(int i=0;i<location.size();i++){
        if(limit <= location[i]){
            installed++;
            limit = location[i] + gap;
        }
    }
    // 모든 카메라가 설치 되어있다면 참
    return installed >= cameras;
}
```

> `optimize(locations, cameras)` = 카메라를 설치할 수 있는 위치 `locations`와 카메라의 수 `cameras`가 주어질 때, 카메라 간 최소 간격의 최대치를 반환

```cpp
double optimize(const vector<double>& location, int cameras){
    double lo = 0, hi = 241;
    for(int i=0;i<100;i++){
        double mid = (lo + hi) / 2.0;
        // 간격이 mid 이상인 경우 답은 [mid,hi]에 있으며
        if(decision(location,cameras,mid)){
            lo = mid;
        // 간격이 mid 미만인 경우 답은 [lo,mid]에 있다.
        }else{
            hi = mid;
        }
    }
    return lo;
}
```

##### Resources
- [DARPA](https://www.algospot.com/judge/problem/read/DARPA)