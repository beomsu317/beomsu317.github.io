---
title: Quantization
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

양자(Quantization)화란 넓은 범위를 갖는 값들을 작은 범위를 갖는 값들로 근사해 표현함으로써 자료를 손실 압축하는 방법이다. 

1000 이하의 자연수들로 구성된 수열을 최대 S종류의 값만 사용하도록 양자화하는데, 이 때 양자화된 숫자는 원래 수열에 없는 숫자일 수도 있다. 예를 들어, 1 2 3 4 5 6 7 8 9 10을 2개의 숫자만을 써서 양자화하는 방법은 3 3 3 3 3 7 7 7 7 7 이 될 수도 있고, 1 1 1 1 1 10 10 10 10 10 이 될 수도 있다. 만약 1 2 3 4 5 를 1 1 3 3 3 으로 양자화하면 오차 제곱의 합은 0 + 1 + 0 + 1 + 4 = 6 이 된다. 수열과 S가 주어질 때, 가능한 오차 제곱의 합이 최소값을 구하는 프로그램을 만들면 된다.

1. 입력의 첫 줄은 테스트 케이스 C(1 <= C <= 50)
1. 각 테스트 케이스의 첫 줄에는 수열의 길이 N(1 <= N <= 100), 사용할 숫자의 수 S(1<= S <= 10)이 주어진다.
1. 그 다음 줄에 N개의 정수로 수열의 숫자들이 주어진다. 수열의 모든 수는 1000 이하의 자연수이다.

## Solving

주어진 수열을 정렬하면, 같은 숫자로 양자화되는 숫자들은 항상 인접해 있게 된다. 다음과 같이 s개의 묶음으로 나누면 쉽게 해결할 수 있다.

```
{1, 4, 6, 744, 755, 777, 890, 897, 902}
->
{1, 4, 6}, {744, 755, 777}, {890, 897, 902}
---------  ---------------  ---------------
    4            759              896
```

첫 묶음의 크기를 x라 하면, 나머지 n - x개의 숫자를 s - 1 개의 묶음으로 나누면 된다. 이 때, 나머지 s - 1 묶음의 오류 합이 최소여야 전체도 최소 오류이기 때문에, **최적 부분 구조** 또한 성립한다.

따라서 from 이후의 숫자들은 parts 개의 묶음으로 묶을 때, 최소 오류 제곱의 합을 반환하는 함수 `quantize(from, parts)`가 있다고 하면 parts 개의 묶음 중 1번째의 크기는 1이상 n - from 이하의 값이므로, 각각 계산하면 된다. 1번째 묶음의 크기가 size일 때 최소 오류는 `minError(from, from + size - 1) + quantize(from + size, parts - 1)`이 된다. 따라서 다음의 점화식을 만들 수 있으며 동적 계획법을 이용할 수 있다. 

`minError(a, b)`는 a번째 숫자부터 b번째 숫자까지 하나의 수로 표현했을 때의 최소 오류를 반환한다.

$ quantize(from, parts) = \overset{n-from}{\underset{size=1}{min}} [minError(from, from + size - 1) + quantize(from + size, parts + 1)] $

미분을 이용하면 길이 2 이상인 구간 수열 A\[a ... b\]에 대해 오차 제곱의 합을 최소화하는 m을 쉽게 찾을 수 있다. 다음은 m에 대한 2차식이다.

$ \sum_{i=a}^b ({A[i]} - m)^2 = (b - a + 1){m}^2 - 2(\sum_{i=a}^b {A[i]})m + \sum_{i=a}^b {A[i]}^2 $

2차항의 계수가 양수이므로 미분을 통해 최소점을 찾을 수 있다. m에 대해 미분한 후 0이 되는 점을 찾을 수 있다.

$ 2(b - a + 1)m - 2{\sum_{i=a}^b {A[i]}} = 0 $

따라서 m은 다음과 같다.

$ m = \frac {\sum_{i=a}^b {A[i]}}{b - a + 1} $

즉 모든 값의 평균을 사용하면 오차를 최소화할 수 있다는 것을 알 수 있다. 정수만을 사용할 수 있으므로 평균에 가장 가까운 정수, 곧 반올림한 값을 사용할 것이다.

$ O(1) $에 계산할 수 있는 부분 합을 구하는 방법을 사용한다. 우선 0부터 k까지의 부분 합을 구한다.

$ pSum[k] = \sum_{i=0}^k {A[i]} $

다음과 같은 식을 이용하면 A[a]부터 A[b]까지의 합을 구할 수 있다. a = 0 인 경우는 에외이다.

$ pSum[b] - pSum[a - 1] = \sum_{i=0}^b {A[i]} - \sum_{i=0}^{a-1} {A[i]} = \sum_{i=a}^b {A[i]}$

이것을 b - a + 1로 나누면 평균 m은 상수 시간에 구할 수 있다.

오차 제곱의 합을 구하는 식이며 여기서 $ {A[]}^2 $의 부분 합과 $ A[] $의 부분 합인데, 이들은 m과는 관련이 없으며, 따라서 한 번 더 부분합을 사용해 이 식을 $ O(1) $에 계산할 수 있다. 따라서 알고리즘의 전체 시간 복잡도는 부분 문제의 수 $ O(ns) $에 각 부분 문제의 답을 계산하는데 드는 시간 $ O(n) $을 곱한 $ O({n}^2s) $가 된다.

$ \sum_{i=a}^b ({A[i]} - m)^2 = (b - a + 1){m}^2 - 2m(\sum_{i=a}^b {A[i]}) + \sum_{i=a}^b {A[i]}^2 $

우선 `precalc()` 함수에서 부분합을 미리 계산한다.

```cpp
void precalc(){
    sort(A,A+n);
    pSum[0] = A[0];
    pSqSum[0] = A[0]*A[0];

    for(int i=1;i<n;i++){
        pSum[i] = pSum[i-1] + A[i];
        pSqSum[i] = pSqSum[i-1] + A[i]*A[i];
    }
}
```

위에서 구한 공식을 이용해 오차 제곱의 최소를 구한다.

```cpp
int minError(int lo,int hi){
    int sum = pSum[hi] - (lo == 0 ? 0 : pSum[lo - 1]);
    int sqSum = pSqSum[hi] - (lo == 0 ? 0 : pSqSum[lo - 1]);

    // 정수이므로 반올림
    int m = int(0.5 + (double)sum/(hi - lo + 1));

    int ret = sqSum - 2 * m * sum + m * m * (hi - lo + 1);
    return ret;
}
```

메모제이션을 구현하여 재귀 호출하면 제한시간 안에 정답을 구할 수 있다.

```cpp
const int INF = 987654321;
int n;
int A[101],pSum[101],pSqSum[101];
int cache[101][11];
int quantize(int from,int parts){
    // base case : 모든 숫자 양자화된 경우
    if(from == n){
        return 0;
    }
    // base case : 더 묶을 수 없는 경우
    if(parts == 0){
        return INF;
    }
    // 메모제이션
    int &ret = cache[from][parts];
    if(ret != -1){
        return ret;
    }
    ret = INF;
    // 조각의 길이를 변화시키며 최소치를 찾음
    for(int partSize = 1;from + partSize <= n; partSize++){
        int me = minError(from,from + partSize - 1);
        int qu = quantize(from + partSize,parts - 1);
        ret = min(ret, me+qu);
    }
    return ret;
}
```


## References
- [QUANTIZE](https://www.algospot.com/judge/problem/read/QUANTIZE)