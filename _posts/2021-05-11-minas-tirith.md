---
title: Minas Tirith
author: Beomsu Lee
math: true
mermaid: true
tags: [greedy algorithm]
---

## Problem

미나스 아노르엔 반지름이 8킬로나 되는 거대한 원형 성벽, 람마스 에코르가 있다. 도시를 감싸는 성벽에는 $n$개의 초소가 배치되어 있다. 각 초소들은 해당 위치를 중심으로 반지름 $r_i$의 원 내부를 감시할 수 있으며 초소$(y_i,x_i)$는 불규칙적으로 배치되어 있고, 각 초소마다 감시할 수 있는 범위는 $r_i$이다. 각 테스트 케이스마다 필요한 최소의 병사 위치를 출력하는 프로그램을 만들면 된다. 

1. 입력의 첫 줄에는 테스트 케이스 $c(c <= 50)$
1. 각 테스트 케이스의 첫 줄에는 초소의 개수 $n(1 <= n <= 100)$
1. 그 후 $n$줄에 각 3개의 실수로 각 초소의 위치 $y_i,x_i$와 감시 범위 $r_i$가 주어짐

## Solving

각 초소가 감시할 수 있는 구간을 호로 갖는 부채꼴 중심각을 $[begin,end]$ 형태의 폐구간으로 표현해보자.

![modeling](/assets/img/greedy-algorithm/minas-tirith-01.png)

$begin$과 $end$를 구하기 위해선 $loc$과 $range$를 추가로 더 계산해야 한다. $range$는 초소에서 감시할 수 있는 범위가 $loc$좌우로 얼마나 되는가를 나타낸다. 따라서 $begin$과 $end$는 $loc$에서 $range$를 -, + 하여 구할 수 있다.

$loc$은 표준 삼각 함수인 $atan2$를 통해 구할 수 있다. $atan2$는 $x$, $y$를 입력받아 각도를 $[-\pi,\pi]$ 구간 내의 값으로 반환한다.

$loc=atan2(y,x)$

$range$의 값도 쉽게 구할 수 있다. 

![modeling2](/assets/img/greedy-algorithm/minas-tirith-02.png)

초소의 감시 범위는 $r$이고 $r$을 2등분 한 점에서 원점까지 선을 그으면 2개의 직각 삼각형을 얻을 수 있다. 

$\sin ({\frac {range} 2}) = {\frac {\frac r 2} {8} } $

위의 식을 이용해 $\theta$는 $asin({\frac r 2} \cdot {\frac 1 8})$로 구할 수 있다.

$range = 2 \cdot asin({\frac r {16}})$

이렇게 전체 원을 감시할 수 있는지 여부는 선택한 초소의 감시 영역의 합집합이 $[0,2 \pi]$를 완전히 덮는지를 판단해 알 수 있다. 다음과 같이 $begin, end$를 구한 결과를 `ranges`에 저장한다. $atan2$의 반환 값은 $[- \pi, \pi]$이므로 `fmod()`를 이용해 강제로 $[0,2 \pi]$로 바꾸지만, `ranges`에 들어가는 값은 $[0,2 \pi]$를 벗어날 수 있다는 점을 유의해야 한다.

```cpp
const double pi = 2.0 * acos(0);
const int INF = 987654321;
int n;
double y[100],x[100],r[100];
pair<double,double> ranges[100];
void convertToRange(){
    for(int i=0;i<n;i++){
        double loc = fmod(2*pi + atan2(y[i],x[i]),2*pi);
        double range = 2.0 * asin(r[i] / 2.0 / 8.0);
        ranges[i] = make_pair(loc - range,loc + range);
    }
    sort(ranges,ranges+n);
}
```

이제 원을 잘라 선형으로 만들어 풀이가 가능하다.

```
        |- - - - -|
|- - - - - -|       |- - - - -|
|--------------------------------|
0                               2 pi
```

각 구간의 시작 위치를 오름차순으로 정렬해 놓으면 `solveLinear()`를 더 효율적으로 구현할 수 있다.

```cpp
int solveCircular(){
    int ret = INF;
    // 각 구간을 오름차순으로 정렬
    sort(ranges,ranges+n);
    // 0을 덮는 구간 선택
    for(int i=0;i<n;i++){
        if(ranges[i].first <= 0 || ranges[i].second >= 2*pi){            
            double begin = fmod(ranges[i].second + 2*pi,2*pi);
            double end = fmod(ranges[i].first + 2*pi,2*pi);
            ret = min(ret, 1 + solveLinear(begin,end));
        }
    }
    return ret;
}
```

`solveLinear()`는 $begin$과 $end$가 주어질 때, 구간 중 최소 몇 개를 선택해야 이를 전부 덮을 수 있을지를 반환한다. 

```cpp
int solveLinear(double begin,double end){
    int used = 0, idx =0;
    // 덮지 못한 선분이 있는 경우 계속함
    while(begin < end){
        double maxCover = -1;
        // begin 보다 이전에 시작하는 구간 중 가장 늦게 끝나는 구간 선택
        while(idx < n && ranges[idx].first <= begin){
            maxCover = max(maxCover,ranges[idx].second);
            idx++;
        }
        // 덮을 구간이 없는 경우
        if(maxCover <= begin){
            return INF;
        }
        // 덮은 구간을 잘라냄
        begin = maxCover;
        used++;
    }
    return used;
}
```

##### Resources
- [MINASTIRITH](https://www.algospot.com/judge/problem/read/MINASTIRITH)