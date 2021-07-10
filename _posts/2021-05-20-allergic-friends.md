---
title: Allergic Friends
author: Beomsu Lee
tags: [combinatorial search]
---

## Problem

$n$명의 친구들을 초대하려고 한다. 할 줄 아는 $m$ 가지 음식을 대접해야 하며 친구들은 알러지 때문에 못 먹는 음식들이 있다. 만들 줄 아는 음식과 해당 음식을 못먹는 친구들의 목록이 주어졌을 때 최소 몇 가지의 음식을 해야하는지 계산하는 프로그램을 만들면 된다.

1. 입력의 첫 줄에는 테스트 케이스 $T(T<=50)$
1. 테스트 케이스의 각 첫 줄에는 친구의 수 n(1<=n<=50)과 할 줄 아는 음식의 수 $m(1<=m<=50)$
1. 다음 줄은 $n$개의 문자열로 각 친구들의 이름이 주어짐
1. 그 다음 줄은 $m$줄에 각 음식에 대해 먹을 수 있는 친구의 수와 각 친구의 이름이 주어짐

## Solving

음식을 선택하는 모든 경우의 수를 하나하나 만들어 보도록 구현한다. $m$개의 음식이 있으니 $2^m$가지의 수가 있다. 

```cpp
int n, m, best;
// eaters[food] : food를 먹을 수 있는 친구들의 번호
vector<int> eaters[50];
void slowSearch(int food, vector<int>& edible, int chosen){
    // prune
    if(chosen >= best){
        return;
    }
    // base case
    if(food == m){
        if(find(edible.begin(),edible.end(),0) == edible.end()){
            best = chosen;
        }
        return;
    }
    // 해당 음식을 안하는 경우
    slowSearch(food + 1,edible,chosen);

    // 해당 음식을 하는 경우
    for(int i=0;i<eaters[food].size();i++){
        edible[eaters[food][i]]++;
    }
    slowSearch(food+1,edible,chosen+1);
    for(int i=0;i<eaters[food].size();i++){
        edible[eaters[food][i]]--;
    }
}
```

위의 방식으로 구현한 경우 $m$이 최대 값일 경우 시간 제한이 걸려 문제 풀이가 불가능하다. 

문제의 형태를 바꿔 음식을 만들 것인가 여부를 선택하는 것보다, 재귀 호출마다 아직 먹을 음식이 없는 친구를 찾은 뒤 이 친구를 위해 어떤 음식을 만들지 결정하는 방법으로 구현한다.

```cpp
int n, m, best;
vector<int> canEat[50], eaters[50];
void search(vector<int>& edible,int chosen){
    // prune
    if(chosen >= best){
        return;
    }
    // 먹을 음식이 없는 친구를 찾는다.
    int first = 0;
    while(first < n && edible[first] > 0){
        first++;
    }
    // base case
    if(first == n){
        best = chosen;
        return;
    }
    // 먹을 음식이 없는 친구를 찾은 경우 해당 친구의 먹을 수 있는 음식을 순회하며 재귀 호출
    for(int i=0;i<canEat[first].size();i++){
        int food = canEat[first][i];
        for(int j=0;j<eaters[food].size();j++){
            edible[eaters[food][j]]++;
        }
        search(edible,chosen + 1);
        for(int j=0;j<eaters[food].size();j++){
            edible[eaters[food][j]]--;
        }
    }
}
```

- `search()`는 항상 모든 친구가 먹을 음식이 있는 조합만 찾는다. 하지미나 `slowSearch()`는 마지막 조각까지 결정한 뒤에도 배고픈 친구가 남는 경우도 탐색한다.
- `search()`는 호출 시마다 항상 음식을 하지만 `slowSearch()`는 음식을 하지 않고도 재귀 호출을 하게된다. `slowSearch()`의 깊이는 항상 $m$으로 고정되지만 `search()`는 항상 $m$이하의 숫자이다.
- `slowSearch()`는 필요하지 않은 음식도 만들지만 `search()`는 필요한 음식만 한다.

##### Resources
- [ALLERGY](https://www.algospot.com/judge/problem/read/ALLERGY)