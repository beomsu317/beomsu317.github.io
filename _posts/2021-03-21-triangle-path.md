---
title: Triangle Path
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---


## Problem

삼각형 모양으로 배치된 자연수가 있으며 맨 위의 숫자부터 시작해, 한 번에 한 칸씩 아래로 내려가는 경로를 만든다. 경로는 아래로 내려갈 때마다 바로 아래 숫자나, 혹은 오른쪽 아래 숫자로 내려갈 수 있다. 이 때 모든 경로 중 숫자의 최대 합을 찾는 프로그램을 작성하면 된다.

1. 첫 줄에는 테스트 케이스의 수 C (C <= 50)
1. 각 테스트 케이스의 첫 줄은 삼각형의 크기 n (2 <= n <= 100)
1. 그 후 n줄에 각 1개 ~ n개의 숫자로 삼각형 각 가로줄에 있는 숫자가 왼쪽부터 주어짐 (각 숫자는 1 이상 100000 이하)

## Solving

전체 경로의 최대 합을 반환하는 것이 아니라 부분 경로의 최대 합을 반환하여 더 빠르게 수행할 수 있다. 

$ solve(y,x) = triangle[y][x] + max(solve(y+1,x),solve(y+1,x+1)) $

이 알고리즘에서 부분 문제의 수는 $O(n^2)$이고 각 부분 문제를 계산하는데 상수 시간밖에 안 걸리기 때문에 시간 복잡도는 $O(n^2)$이 된다.

```cpp
int cache[100][100];
int solve(vector<vector<int>> &tri,int y, int x){
    // 메모제이션
    int &ret = cache[y][x];
    if(ret != -1){
        return ret;
    }
    // base case
    if(y == (tri.size() - 1)){
        return tri[y][x];
    }
	// 바로 아래 또는 바로 아래 오른쪽 숫자와 비교 후 큰 숫자를 더함
    return ret = max(solve(tri,y+1,x),solve(tri,y+1,x+1)) + tri[y][x];
}
```

##### Resources
- [TRIANGLEPATH](https://www.algospot.com/judge/problem/read/TRIANGLEPATH)