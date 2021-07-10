---
title: PI Memorization
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

신동들이 원주율을 외우는 방법 중 하나로, 숫자를 몇 자리 이상 끊어 외우는 방법이 있다. 이들은 3자에서 5자까지 끊어 외우며, 가능하면 5555나 123 같이 쉬운 조각들이 많이 등장하는 방법을 택하곤 한다. 

이 때, 각 조각들의 난이도는 다음과 같다.

1. 모든 숫자가 같을 때(333, 5555) 난이도: 1
1. 숫자가 1씩 단조 증가하거나 감소할 때(23456, 3210) 난이도: 2
1. 두 개의 숫자가 번갈아 가며 등장할 때(323, 53535) 난이도: 4
1. 숫자가 등차수열을 이룰 때(147, 8642) 난이도: 5
1. 그 외의 경우 난이도: 10

주어진 값마다 최소의 난이도를 출력하는 프로그램을 작성하면 된다.

1. 첫 줄은 테스트 케이스의 수 C (C <= 50)
1. 각 테스트 케이스는 8글자 이상 10000글자 이하의 숫자

## Solving

이 문제를 푸는 완전 탐색 알고리즘은 주어진 수열을 쪼개는 모든 방법을 하나씩 만들고, 그 중 난이도의 합이 가장 작은 조합을 찾아내면 된다. 각 재귀 함수는 한 번 호출될 때마다 하나하나 시도하며 나머지 수열을 재귀적으로 호출한다. 첫 조각의 길이는 3, 4, 5 중 하나이며 각 경우마다 하나씩의 부분 문제를 푼풀어야 한다. 각 부분 문제에 대해 최적해를 구했다면, 전체 문제의 최적해는 다음과 같다.

- 길이 3인 조각의 난이도 +3글자 제외하고 나머지 수열에 대한 최적해
- 길이 4인 조각의 난이도 +4글자 제외하고 나머지 수열에 대한 최적해
- 길이 5인 조각의 난이도 +5글자 제외하고 나머지 수열에 대한 최적해

나머지 수열의 최적해를 구할 때 앞의 부분을 어떻게 쪼갰는지 중요하지 않다. 따라서 **최적 부분 구조**가 성립한다는 것을 알 수 있다.

이 알고리즘에는 최대 n개의 부분 문제가 있고, 각 부분 문제를 해결하는데 최대 3개의 부분 문제가 있다. 따라서 시간 복잡도는 $O(n)$이다.

```cpp
const int INF=987654321;
string N;
int cache[10002];
int classify(int a,int b){
    string M = N.substr(a,b - a + 1);
    // 첫 글자로만 이루어진 문자열과 같으면 1
    if(M == string(M.size(),M[0])){
        return 1;
    }
    bool progressive = true;
    // 등차수열 체크
    for(int i=0;i < M.size() - 1;i++){
        if(M[i+1] - M[i] != M[1] - M[0]){
            progressive = false;
        }
    }
    // 등차수열이며 단조 증가할 경우 2
    if(progressive && abs(M[1] - M[0]) == 1){
        return 2;
    }

    // 두 수가 번갈아 등장하는지 확인
    bool alternating = true;
    for(int i=0;i<M.size()-2;i++){
        if(M[i] != M[i+2]){
            alternating = false;
        }
    }
    // 두 수가 번갈아 등장한다면 4
    if(alternating){
        return 4;
    }
    // 등차수열인 경우 5
    if(progressive){
        return 5;
    }
    // 그 외 10
    return 10;
}

int memorize(int begin){
    // base case
    if(begin == N.size()){
        return 0;
    }
    int &ret = cache[begin];
    if(ret != -1){
        return ret;
    }
    ret = INF;
    // 3에서 5까지 
    for(int L=3;L<=5;L++){
        // begin + L 이 N의 크기보다 작은 경우
        if(begin + L <= N.size()){
            // 재귀 호출하여 최소 값을 얻는다.
            ret = min(ret,memorize(begin + L) + classify(begin,begin + L - 1));
        }
    }
    return ret;
}
```

## References
- [PI](https://www.algospot.com/judge/problem/read/PI)