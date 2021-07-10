---
title: Joined Longest Increasing Subsequence
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---


## Problem

어떤 수열에서 0개 이상의 숫자르 지운 결과를 원 수열의 부분 수열이라고 하며 중복된 숫자가 없고 오름차순으로 정렬된 부분 수열을 증가 부분 수열이하고 한다. 두 개의 정수 수열 A와 B에서 각각 증가 부분 수열을 얻은 뒤 이들을 크기 순서대로 합친 것을 합친 증가 부분 수열이라고 하고, 이 중 가장 긴 수열을 Joined Longest Increasing Subsequence라 하자. 예를 들어 '1 3 4 7 9'는 '1 9 4'와 '3 7 4'의 JLIS이다. A와 B가 주어졌을 때 JLIS의 길이는 계산하는 프로그램을 만들면 된다.

1. 입력의 첫 줄은 테스트 케이스 c (1 <= c <= 50)
1. 각 테스트 케이스의 첫 줄은 A, B의 길이 n, m
1. 다음 줄부턴 n개의 정수로 A 원소, 그 다음 줄은 m개의 정수로 B의 원소
1. 모든 원소들은 32비트 부호 있는 정수에 저장할 수 있다.

## Solving

seq1\[idx1\]와 seq2\[idx2\] 중 작은 쪽이 앞에 오는 경우 이 증가 부분 수열의 다음 숫자는 seq1\[idx1 + 1\] 이후 또는 seq2\[idx2 + 1\] 이후 수열 중 max(seq\[idx1\],seq\[idx2\])보다 큰 수 중 하나가 된다. 그리고 seq1\[i\]를 다음 숫자로 선택할 경우 합친 증가 부분 수열의 최대 길이는 1 + solve(i,idx2)가 된다.

앞의 내용이 어떻게 되더라도 뒤에 값은 영향을 받지 않으므로 **최적 부분 구조**에 해당한다.

```cpp
const long long NEGINF = numeric_limits<long long>::min();
int cache[1001][1001];
int solve(vector<int> &seq1,vector<int> &seq2,int idx1,int idx2){
    // 메모제이션
    int &ret = cache[idx1+1][idx2+1];
    if(ret != -1){
        return ret;
    }
    // seq1[idx1], seq2[idx2]가 이미 존재하므로 2
    ret = 2;

    // seq1[idx1]과 seq2[idx2] 중 큰 값을 찾는다.
    long long a = (idx1 == -1 ? NEGINF : seq1[idx1]);
    long long b = (idx2 == -1 ? NEGINF : seq2[idx2]);
    long long max_element = max(a,b);

    // 다음 원소를 찾는다.
    for(int i = idx1 + 1;i < seq1.size();i++){
        if(max_element < seq1[i]){
            ret = max(ret,solve(seq1,seq2,i,idx2) + 1);
        }
    }
    for(int i = idx2 + 1;i < seq2.size();i++){
        if(max_element < seq2[i]){
            ret = max(ret,solve(seq1,seq2,idx1,i) + 1);
        }
    }
    return ret;
}
```

##### Resources
- [JLIS](https://www.algospot.com/judge/problem/read/JLIS)