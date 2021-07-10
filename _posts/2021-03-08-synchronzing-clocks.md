---
title: Synchronizing Clocks
author: Beomsu Lee
math: true
mermaid: true
tags: [brute force]
---

## Problem

4 x 4 개의 시계가 있으며, 이 시계들은 모두 12시, 3시, 6시, 9시를 가리키고 있다. 이 시계들을 모두 12시를 가리키도록 변경해야 한다.

시계의 시간을 조작하는 방법은 10개의 스위치를 조작하면 되며, 각 스위치들은 3개에서 5개의 시계와 연결되어 있다. 스위치를 누를 때마다 +3시간이 된다.

|Switch|Connected Clock|
|:---:|:---:|
|0|0, 1, 2|
|1|3, 7, 9, 11|
|2|4, 10, 14, 15|
|3|0, 4, 5, 6, 7|
|4|6, 7, 8, 10, 12|
|5|0, 2, 14, 15|
|6|3, 14, 15|
|7|4, 5, 7, 14, 15|
|8|1, 2, 3, 4, 5|
|9|3, 4, 5, 9, 13|

모든 시계를 12시로 변경하기 위해 최소로 눌러야 할 스위치의 개수를 구하면 된다.

1. 첫 줄에는 테스트 케이스가 주어진다. C (<= 30)
1. 각 테스트 케이스에는 16개의 시계 정보들이 주어진다.

## Solving

시계는 3시간씩 증가하기 때문에 4번이면 제자리로 돌아오게 된다. 따라서 시계를 3번 이상 누를 필요가 없다. 스위치는 10개 스위치를 누르는 횟수는 4번이므로 4^10이 경우의 수가 된다. 

정렬되었는지 확인을 위한 함수이다.
```cpp
bool aligned(std::vector<int> &clocks){
    for(int i=0;i<clocks.size();i++){
        if(clocks[i] != 12){
            return false;
        } 
    }
    return true;
}
```

스위치가 눌렸을 경우 해당 스위치의 시계에 +3을 해주는 함수이다.

```cpp
void push(std::vector<int> &clocks,int swtch){
    for(int i=0;i<clocks.size();i++){
        if(connected[swtch][i]==1){
            clocks[i] += 3;
            if(clocks[i] == 15){
                clocks[i] = 3;
            }
        }
    }
}
```

재귀의 핵심 함수며 스위치를 눌러 clocks를 모두 12시로 맞출 수 있는 최소 횟수를 반환한다. 불가능한 경우 INF를 반환한다. INF는 매우 큰 정수로 선언한다.

```cpp
int solve(std::vector<int> &clocks,int swtch){
    // base case
    if(swtch == 10){
        // 모든 시계가 12시로 맞춰져 있다면 0을, 아니면 INF를 반환
        return aligned(clocks) ? 0 : INF;
    }
    int ret = INF;
    // 
    for(int i=0;i<4;i++){
        // swtch : 이번에 누를 스위치
        // 리턴 값과 스위치를 몇 번 눌렀는지를 비교하여 최소인 값을 ret에 저장
        ret = std::min(ret, i + solve(clocks,swtch + 1));
        // 초기화
        push(clocks, swtch);
    }
    return ret;
}
```

메인 함수이며 clocks를 저장 후 재귀함수를 호출한다.

```cpp
// 매우 큰 정수
const int INF = 9999;

// 10개의 스위치 별 연결된 시계 정보
int connected[10][16] = {
    {1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0},
    {0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1},
    {1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0},
    {1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1},
    {0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1},
    {0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1},
    {0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0}
};

int main(int argc, char *argv[])
{
    std::ios::sync_with_stdio(false);

    std::string tmp_str;

    std::getline(std::cin, tmp_str);
    int num = stoi(tmp_str);

    std::vector<int> clocks;
    std::vector<std::string> str_vector;

    std::vector<int> tmp,result;

    while (num--)
    {
        std::getline(std::cin, tmp_str);
        str_vector = split(tmp_str, ' ');

        for (int i = 0; i < str_vector.size(); i++)
        {
            clocks.push_back(stoi(str_vector[i]));
        }
        str_vector.clear();

        int mincnt = solve(clocks,0);
        if(mincnt == INF){
            result.push_back(-1);
        }else{
            result.push_back(mincnt);
        }
        clocks.clear();
    }

    for(int i=0;i<result.size();i++){
        std::cout << result[i] << "\n";
    }

    return 0;
}
```

다음은 실행한 결과이다.

```bash
$./main
2
12 6 6 6 6 6 12 12 12 12 12 12 12 12 12 12 
12 9 3 12 6 6 9 3 12 9 12 9 12 12 6 6
2
9
```

##### Resources
- [Synchronizing Clocks](https://www.algospot.com/judge/problem/read/PICNIC)