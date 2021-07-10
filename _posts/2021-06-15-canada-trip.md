---
title: Canada Trip
author: Beomsu Lee
category: [Algorithm, Dicision Problem]
tags: [dicision problem]
math: true
mermaid: true
---

## Problem

캐나다의 1번 고속도로는 세계에서 가장 긴 고속도로 중 하나이며, 캐나다의 동쪽 끝에서 서쪽 끝까지 있는 모든 주요 도시를 연결한다. 이 고속도로에는 $N$개의 주요 도시를 지나치는데, 각 도시까지의 남은 거리를 표시하는 표지판이 많다. $i$번째 도시까지의 거리를 나타내는 표지판은 도시에 도착하기 $M_i$미터 전부터 도시에 도착할 때까지 $G_i$미터 간격으로 설치되어 있다. 예를 들어 $M_0=500$이고 $G_0=50$이라 하면 11개의 표지판을 순서대로 보게된다. 

시작점으로부터 각 도시까지의 거리를 $L_i$라 하고 $M_i$, $G_i$가 주어질 때, 시작점으로부터 보게되는 $K$번째 표지판의 위치를 계산하는 프로그램을 구현하면 된다.

1. 입력의 첫 줄에는 테스트 케이스의 수 $T(T<=50)$
1. 각 테스트 케이스의 첫 줄에는 도시의 수 $N(1<=N<=5000)$과 $K(1<=K<=2^31-1)$이 주어짐
1. 그 후 $N$줄에 각 3개의 정수로 $L_i, M_i, G_i(1<=G_ii<=M_i<=L_i<=8030000))$가 주어지며, $M_i$는 항상 $G_i$의 배수

## Solving

"$K$번째 표지판의 위치는 어디인가?"라는 문제를 다음과 같이 바꾸었다.

> decision($x$) = 시작점부터 $x$미터 지점까지 가며 $K$개 이상의 표지판을 만날 수 있는가?

원하는 답이 $D$라면 `decision()`이 참을 반환하는 첫 번째 지점일 것이다. 즉, `decision(D-1)=false`이며 , `decision(D)=true`여야 한다.

`decision(x)`을 구현하기 위해 [0, $x$]에 출현하는 모든 표지판의 개수를 세어 보자. $i$번째 도시까지의 거리를 나타내는 표지판은 [$L_i$ - $M_i$, $L_i$]구간에 출현하므로, 두 구간이 닿지 않는 경우 $x < L_i - M_i$에서는 표지판을 볼 수 없다. 이외의 경우 [0, $x$]구간과 [$L_i - M_i$, $L_i$]구간이 겹치는 길이는 다음과 같다.

> min(x, $L_i$) - ($L_i - M_i$)

이를 $G_i$로 나눈고 1을 더하면 $i$번째 도시까지의 거리를 나타내는 표지판을 몇개나 보는지 알 수 있다. 도시의 수는 최대 5000개이므로 각 도시를 순회하며 표지판의 수를 더해주면 된다. 

`decision()`의 수행시간은 $O(n)$이 된다.

```cpp
int n, k;
int l[5000], m[5000], g[5000];

bool decision(int x){
    int signs = 0;
    for(int i=0;i<n;i++){
        // 표지판이 있을 경우
        if(x >= l[i] - m[i]){
            // 모든 표지판을 더한다.
            int min_val = min(x,l[i]);
            signs += (min_val - (l[i]-m[i])) / g[i] + 1;
        }
    }
    // 모든 표지판을 더한것이 k보다 크면 true 반환
    return signs >= k;
}
```

이분법을 이용해 `optimize()` 함수를 구현한다. 

```cpp
int optimize(){
    int lo=0, hi=8030000;
    while(lo + 1 < hi){
        int mid = (lo + hi) / 2; 
        if(decision(mid)){
            hi = mid;
        }else{
            lo = mid;
        }
    }
    return hi;
}
```

##### Resources
- [CANADATRIP](https://algospot.com/judge/problem/read/CANADATRIP)