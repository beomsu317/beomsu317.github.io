--- 
title: Course Withdrawal
author: Beomsu Lee
category: [Algorithm, Dicision Problem]
tags: [dicision problem]
---

## Problem

백준이네 학교에서는 장학금을 학생의 중간고사 등수와 기말고사 등수에 따라 배정한다. 어떤 학생이 듣는 $i$번째 과목의 수강생 수가 $c_i$라 하자. 그리고 이 학생은 $i$번째 과목 중간고사 등수가 $r_i$라 하면, 이 학생의 중간고사 누적 등수는 다음과 같다.

$$
cumulativeRank = {\frac {\sum r_i} {\sum c_i}}
$$

예를 들어, 수강생이 각각 150, 200, 15명인 세 개의 과목을 듣는데, 각각 100, 10, 5등을 했다면 학생의 누적 등수는 다음과 같다.

$$
(100 + 10 + 5) / (150 + 200 + 15) = 115 / 365 = 0.315
$$

수강 철회를 하면 철회한 과목은 중간고사의 누적 등수 계산에 들어가지 않게 된다. 따라서 수강 철회를 해도 남은 과목이 $k$개 이상이라면 장학금을 받을 수 있다. 백준이가 적절히 과목을 철회했을 때 얻을 수 있는 최소 누적 등수를 계산하는 프로그램을 작성하면 된다.

1. 입력의 첫 줄에는 테스트 케이스의 수 $T(T<=50)$
1. 각 테스트 케이스의 첫 줄에는 수강하는 과목의 수 $n(1<=n<=1000)$과 남겨둬야 할 과목의 수 $k(1<=k<=n)$
1. 다음 줄에는 $n$개의 정수 쌍 $(r_i,c_i)$가 순서대로 주어짐$(1<=r_i<=c_i<=1000)

## Solving

이 문제를 다음과 같이 정의하였다.

> dicision(x) = 적절히 과목들을 철회해 누적 등수 x 이하가 될 수 있을까?

이 때 `decision()`은 과목들의 집합 [0,...,n-1]의 모든 부분집합 중 크기가 $k$ 이상이며, 다음 조건을 만족하는 $S$가 있는지를 찾아야 한다.

$$
{\frac {\sum_{j \in S} r_j} { \sum_{j \in S} c_j } } <= x
$$

부등호 좌변의 분모를 오른쪽으로 넘기고 정리하면 다음 식을 얻을 수 있다.

$$
0 <= x \cdot {\sum_{j \in S} c_j } - {\sum_{j \in S} r_j } = {\sum_{j \in S} {(x \cdot c_j - r_j)} } 
$$


$x \cdot c_j - r_j = v=j$라 하자. 그럼 `decision(x)`는 실수 배열 $v$가 주어질 때, 이 중 $k$개 이상을 선택해 그 합을 0 이상으로 만들 수 있는지의 문제로 바뀌게 된다. 이것은 $v$를 정렬한 후 가장 큰 $k$개의 원소를 더해 쉽게 풀이할 수 있다.

```cpp
int n, k;
int r[1000], c[1000];

bool decision(double average){
    // v를 구한다.
    vector<double> v;
    for(int i=0;i<n;i++){
        v.push_back(average * c[i] - r[i]);
    }
    // 정렬
    sort(v.begin(),v.end());

    double sum = 0;
    // 가장 큰 원소 k개의 합이 0 이상이라면, 최대 k개의 합은 항상 0 이상인 것을 이용 == 탐욕법
    for(int i=n-k;i<n;i++){
        sum += v[i];
    }
    return sum >= 0;
}
```

`decision()`은 정렬과 두 개의 선형 반복문으로 구성되어 있기 때문에 $O(n \log n)$의 시간 복잡도를 갖는다. 

```cpp
// 얻을 수 있는 최소의 누적 등수를 계산
double optimize(){
    // 누적 등수는 [0,1] 범위의 실수
    double lo = 0, hi = 1;
    for(int i=0;i<100;i++){
        double mid = (lo + hi) / 2;
        // 누적 등수 mid를 달성할 수 있나?
        if(decision(mid)){
            hi = mid;
        }else{
            lo = mid;
        }
    }
    return lo;
}
```


##### Resources
- [WITHDRAWAL](https://algospot.com/judge/problem/read/WITHDRAWAL)