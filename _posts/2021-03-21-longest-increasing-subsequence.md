---
title: Longest Increasing Subsequence
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---


## Problem

수열 A가 주어졌을 때 가장 긴 증가하는 부분 수열을 구하는 프로그램을 작성하면 된다. 예를 들어 수열 A={1,2,1,3,2,5}인 경우 가장 긴 증가하는 부분 수열은 {1,2,3,5}이며 길이는 4이다. 

1. 첫째 줄엔 수열 A의 크기 N (1 <= N <= 1000)
1. 둘째 줄엔 수열 A를 이루고 있는 $A_i$가 주어짐 (1 <= $A_i$ <= 1000)

## Solving

간단하게 표현하면 seq는 다음 2가지 중 하나가 된다.

1. 원래 주어진 수열 
1. 원래 주어진 수열의 원소 seq\[i\]에 대해, S\[i+1 ...\] 부분 수열에서 seq\[i\]보다 큰 수들만을 포함하는 부분 수열

별도의 기저 사례가 없이, 뒤에 더 이을 숫자가 없는데도 for 문을 순회한다. 이 때 재귀 호출하지 않기 때문에 1을 반환한다. $O(n)$ 만큼의 부분 문제를 갖고 전체 $O(n^2)$의 시간 복잡도를 갖는다.

```cpp
int cache[1001];
int solve(vector<int> &seq,int idx){    
    // -1에서 시작할 경우을 고려
    int &ret = cache[idx + 1];
    if(ret != -1){
        return ret;
    }
    ret = 1;
    for(int i = idx + 1;i < seq.size();i++){
        // idx가 -1이거나 seq[idx]가 seq[i]보다 큰 경우
        if(idx == -1 || seq[idx] < seq[i]){
            // 재귀 호출을 통해 길이를 더해간다.
            ret = max(ret,solve(seq,i) + 1);
        }
    }
    return ret;
}
```

`solve(seq,-1);`를 호출하여 가장 긴 증가하는 부분 수열을 구할 수 있다. 0이 아닌 -1인 이유는 전체 길이도 포함시켜야 하기 때문이다.

## References
- [가장 긴 증가하는 부분 수열](https://www.acmicpc.net/problem/11053)