---
title: Board Cover
author: Beomsu Lee
math: true
mermaid: true
tags: [brute force]
---

## Problem

H*W 크기의 게임판이 있다. 게임판은 검은 칸과 흰 칸으로 구성되어 있으며 흰 칸 영역에 3칸짜리 L자 모양의 블록으로 덮어야 한다. 블록은 회전할 수 있지만 겹치거나, 검은판을 덮거나, 게임판 밖으로 나가선 안된다. 게임판이 주어질 때 이를 덮는 경우의 수를 구하면 된다.

1. 첫 줄은 테스트 케이스의 수 C (C <= 30) 가 주어진다.
1. 각 테스트 케이스의 첫 줄에는 2개의 정수 H, W (1 <= H,W <= 20) 주어진다. #은 검은 칸, .는 흰 칸을 나타낸다.
1. 흰 칸의 수는 50을 넘지 않는다.

## Solving

두 개의 `cover()`, `set()` 함수가 핵심 역할을 수행한다. 

먼저 `set()` 함수는 L자 type(회전 포함)에 대해 덮을 수 있는지 여부를 알려준다.

```cpp
bool set(std::vector<std::vector<int>> &board,int y,int x,int type,int delta){
    bool ok=true;
    // 3개의 칸에 대해 확인한다.
    for(int i=0;i<3;i++){
        // 덮을 위치의 칸을 구한다.
        const int ny = y + cover_type[type][i][0];
        const int nx = x + cover_type[type][i][1];
        // board의 크기를 넘어가면 false
        if(ny < 0 || ny >= board.size() || nx < 0 || nx >= board[0].size()){
            ok = false;
        }
        // delta를 더한 값이 1보다 크면 false
        else if((board[ny][nx] += delta) > 1){
            ok = false;
        }
    }
    return ok;
}
```

`cover()` 함수는 덮히지 않은 왼쪽 위의 값을 가져와 type 별로 돌려가며 개수를 확인한다.

```cpp
int cover(std::vector<std::vector<int>> &board){
    int x=-1,y=-1;
    // 채워지지 않은 칸 중 가장 왼쪽 위에 있는 칸을 찾는다.
    for(int i=0;i<board.size();i++){
        for(int j=0;j<board[0].size();j++){
            if(board[i][j] == 0){
                y=i;
                x=j;
                break;
            }
        }
        if(y != -1){
            break;
        }
    }

    // base case
    if(y == -1){
        return 1;
    }

    int ret=0;
    // type 별 덮힐 수 있는 개수 확인
    for(int type=0;type<4;type++){
        // 해당 타입으로 덮히는지 여부 확인
        if(set(board,y,x,type,1)){
            // 덮힐 경우 cover 재귀 호출하여 나머지도 덮히는지 확인
            ret += cover(board);
        }
        // 덮힐 수 없다면 delta에 -1을 넣어 칸의 값 0으로 복구
        set(board,y,x,type,-1);
    }
    return ret;
}
```

`main()` 함수에선 흰 칸의 개수가 3배수인지를 점검한다.

```cpp
// L자를 회전한 도형 별 저장
const int cover_type[4][3][2] = {
    { {0,0},{0,1},{1,0} },
    { {0,0},{0,1},{1,1} },
    { {0,0},{1,0},{1,1} },
    { {0,0},{1,-1},{1,0} }
};

int main(int argc, char* argv[]){
    std::ios::sync_with_stdio(false);

    std::string tmp_str;

    std::getline(std::cin,tmp_str);
    int num = stoi(tmp_str);
    
    std::vector<int> result;
    int h,w;
    std::vector<std::vector<int>> board;
    std::vector<int> tmp;
    int cnt=0;

    while(num--){
        std::getline(std::cin,tmp_str);
        auto hw = split(tmp_str,' ');
        h = stoi(hw[0]);
        w = stoi(hw[1]);
        cnt=0;
        for(int i=0;i<h;i++){
            std::getline(std::cin,tmp_str);
            for(int j=0;j<w;j++){
                // #인 경우 1
                if(tmp_str[j] == '#'){
                    tmp.push_back(1);
                }else{
                    tmp.push_back(0);
                    // 3배수 점검을 위한 cnt++
                    cnt++;
                }
            }
            board.push_back(tmp);
            tmp.clear();
        }
        // 3배수이면 cover() 호출
        if(cnt % 3 == 0){
            result.push_back(cover(board));
        // 아니면 결과는 0
        }else{
            result.push_back(0);
        }
        board.clear();
    }

    for(int i=0;i<result.size();i++){
        std::cout << result[i] << "\n";
    }

    return 0;
}
```

##### Resources
- [BOARDCOVER](https://www.algospot.com/judge/problem/read/BOARDCOVER)