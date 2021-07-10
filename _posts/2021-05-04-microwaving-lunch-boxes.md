---
title: Microwaving Lunch Boxes
author: Beomsu Lee
tags: [greedy algorithm]
---

## Problem

도시락 업체에 $n$개의 여러 종류의 도시락을 주문했다. 캠핑장의 전자레인지는 하나뿐이고 $i$번째 도시락을 데우는데 $m_i$초가 걸리고 먹는데는 $e_i$초가 걸린다. 도시락을 나누어 데울 수 없고, 도시락을 다 데우는 대로 다른 사람을 기다리지 않고 먹기 시작한다. 이 때 점심을 먹는데 걸리는 시간을 최소화하는 프로그램을 만들면 된다.

1. 입력의 첫 줄은 테스트 케이스 $C(C <= 30)$
1. 각 테스트 케이스의 첫 줄에는 도시락의 수 $n(1 <= n <= 10000)$
1. 각 테스트 케이스의 둘째 줄에는 $n$개의 정수로 각 도시락을 데우는 데 걸리는 시간
1. 각 테스트 케이스의 셋째 줄에는 $n$개의 정수로 각 도시락을 먹는 데 걸리는 시간

## Solving

만약 데우는 시간이 동일한 돈가스가 있고 이보다 더 오래 걸리는 샤브샤브가 있다고 가정하자. 이 샤브샤브를 마지막에 데우면 점심시간이 먹는 시간의 차이만큼 길어지지만, 처음에 데우면 다른 도시락을 데우는 사이 샤브샤브를 먹을 수 있기 때문이다. 따라서 먹는 시간이 오래 걸리는 것부터 데우면 탐욕 알고리즘을 통한 풀이가 가능하다.

```cpp
int heat(){
    vector<pair<int,int> > order;

    for(int i=0;i<n;i++){
        // 가장 시간이 많이 걸리는 음식을 앞으로 가져오기 위해 -
        order.push_back(make_pair(-e[i],i));
    }
    // 정렬
    sort(order.begin(),order.end());

    int ret = 0, beginEat = 0;
    // 해당 순서대로 데워먹는 과정 시뮬레이션
    for(int i=0;i<n;i++){
        int box = order[i].second;
        beginEat += m[box];
        ret = max(ret,beginEat + e[box]);
    }
    
    return ret;
}
```

위와 같이 구현한 경우 $O(n)$ 시간이 걸리는 간단한 시뮬레이션으로 답을 구할 수 있다. 따라서 전체 시간 복잡도는 정렬에 걸리는 $O(n \log n)$이다.

##### Resources
- [LUNCHBOX](https://www.algospot.com/judge/problem/read/LUNCHBOX)