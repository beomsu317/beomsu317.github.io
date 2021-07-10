---
title: Packing for Travel
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

여행일 떠나기 전 캐리어 부피만큼의 물건들을 가져갈 수 있다. 각 물건들은 절박도를 가지고 있으며 이 절박도를 최대화할 수 있는 방법을 구현하면 된다.

1. 입력의 첫 줄에는 테스트 케이스 C(1 <= C <= 50)
1. 각 테스트 케이스의 첫 줄에는 가져가고 싶은 물건의 수 N(1 <= N <= 100)과 캐리어의 용량 W(1 <= W <= 1000)
1. 그 이후 N줄에 순서대로 물건의 정보, 물건의 정보는 이름, 부피, 절박도 순으로 주어지며 이름은 1글자 이상 20글자 이하이며 부피와 절박도는 1000 이하의 자연수

## Solving

먼저 완전 탐색 알고리즘을 구현한 후 동적 계획법을 이용한다. `pack(capacity, ittem)`을 구현해 캐리어 용량이 capacity만큼 남았을 때 item 이후의 물건들을 싸서 얻을 수 있는 최대 절박도를 구한다. 다음과 같이 구현한 경우 부분 문제의 수는 $ O(nw) $이며, 각 부분 문제를 해결하는데 상수 시간이면 충분하므로 이 알고리즘의 전체 시간 복잡도는 $ O(nw)$ 이다.

```cpp
int n,w;
int cache[1001][100];
int volume[100],need[100];
string name[100];
int pack(int capacity,int item){
    // base case
    if(item == n) return 0;
    // memozation
    int &ret = cache[capacity][item];
    if(ret != -1){
        return ret;
    }
    ret = 0;
    // item 가져가지 않는 경우
    ret = pack(capacity,item + 1);
    if(capacity >= volume[item]){
        // item 가져가는 경우 최대 절박도를 반환
        ret = max(ret,pack(capacity - volume[item],item + 1) + need[item]);
    }
    return ret;
}
```

부분 문제에 선택지가 2개 밖에 없기 때문에 따로 선택을 저장하지 않고도 답을 역추적 할 수 있다. 부분 문제에서 item을 선택 했는지를 알고 싶으면 `pack(capacity,item)`과 `pack(capacity,item+1)`이 같은지 비교하면 된다. 만약 두 값이 같다면(절박도가 같다면) 선택하지 않았다는 뜻이므로 item + 1로 넘어가면 된다.

```cpp
void reconstruct(int capacity,int item,vector<string> &picked){
    if(item == n) return;
    // item 선택되지 않았을 경우
    if(pack(capacity,item) == pack(capacity,item + 1)){
        reconstruct(capacity,item + 1,picked);
    }else{
        // 선택될 경우
        picked.push_back(name[item]);
        reconstruct(capacity - volume[item],item + 1,picked);
    }
}
```

## References
- [PACKING](https://www.algospot.com/judge/problem/read/PACKING)