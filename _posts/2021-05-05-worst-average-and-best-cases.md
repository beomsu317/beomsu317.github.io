---
title: Worst / Average / Best Cases
author: Beomsu Lee
category: [Algorithm]
tags: [algorithm]
math: true
mermaid: true
---

이 절에선 선형 탐색을 점근 분석을 통해 예를 들어보겠다. 알고리즘 분석하기 위한 3가지 방법이 있다.

1. The Worst Case
1. Average Case
1. Best Case

```cpp
// C++ implementation of the approach
#include <bits/stdc++.h>
using namespace std;
  
// Linearly search x in arr[].
// If x is present then return the index,
// otherwise return -1
int search(int arr[], int n, int x)
{
    int i;
    for (i = 0; i < n; i++) {
        if (arr[i] == x)
            return i;
    }
    return -1;
}
  
// Driver Code
int main()
{
    int arr[] = { 1, 10, 30, 15 };
    int x = 30;
    int n = sizeof(arr) / sizeof(arr[0]);
    cout << x << " is present at index "
         << search(arr, n, x);
  
    getchar();
    return 0;
}
  
// This code is contributed
// by Akanksha Rai
```

## Ouput

```
30 is present at index 2
```

## Worst Case Analysis

Worst Case 분석은 알고리즘의 실행 시간 상한을 계산한다. 명령어의 개수가 최대로 실행되는지를 알아야 한다. 선형 탐색의 경우, Worst Case는 요소가 배열에 없는 경우이다. x가 없는 경우 $search()$ 함수는 $arr[]$의 모든 요소를 하나하나 비교하게 된다. 그러므로 선형 탐색의 시간 복잡도는 $\Theta(n)$이 된다.

## Average Case Analysis

Average Case 분석은 모든 입력할 수 있는 값들을 가지고 해당 값들에 대해 컴퓨팅 시간을 계산한다. 모든 계산된 값들을 더하고 그 수 만큼 나누면 평균을 구할 수 있다. 케이스의 분포를 알거나 예측할 수 있어야 한다. 모든 케이스가 선형 탐색의 경우 균일하게 분포되어 있다고 가정하면($arr[]$에 $x$가 없는 경우도 포함), 모든 케이스를 더하고 $n+1$로 나누면 된다. 다음은 Average Case의 시간 복잡도이다.

$$
\begin{multline}
Average Case Time \cr
\shoveleft = \frac {\sum_{i=1}^{n+1} \Theta(i)}{(n+1)} \cr
\shoveleft = \frac {\Theta((n+1)(n+2)/2)}{(n+1)} \cr
\shoveleft = \Theta(n)
\end{multline}
$$

## Best Case Analysis

Best Case 분석은 알고리즘의 실행 시간 하한을 계산한다. 최소의 명령어 개수가 실행되는 케이스를 알아야한다. 선형 탐색의 경우 Best Case는 $x$가 처음에 존재하는 것이다. 따라서 시간 복잡도는 $\Theta (1)$이다. 

일부 알고리즘의 경우 모든 케이스들이 점근적으로 동일하다. Worst, Best 케이스가 없는 경우인데 예로 병합 정렬이 있다. 병합 정렬은 모든 케이스에 대해 $ \Theta (n\log n)$이다. 대부분의 다른 정렬 알고리즘은 Worst, Best 케이스를 가진다. 예를 들어, 퀵소트의 경우 Worst Case는 주어진 배열이 이미 정렬되어 있는 경우이며, Best Case는 Pivot이 항상 절반으로 나누는 경우이다. 선택 정렬의 경우 Worst Case는 배열이 거꾸로 정렬되어 있는 경우이며, Best Case는 정렬된 경우이다.

##### Resources
- [Worst, Average and Best Cases](https://www.geeksforgeeks.org/analysis-of-algorithms-set-2-asymptotic-analysis/)
