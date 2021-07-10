---
title: Block Game
author: Beomsu Lee
tags: [dynamic programming]
---

## Problem

5x5 크기의 게임판에서 시작해, 참가자 두명이 번갈아 가며 블럭을 하나씩 게임판에 내려놓는다. 블럭은 L자 모양으로 구성된 3칸짜리 블럭과, 2칸짜리 블럭이 있다. 블럭들은 서로 겹칠 수 없고 뒤집거나 회전해서 놓을 수 있다. 두 참가자가 번갈아가며 블록을 올리다가 더 올려놓을 수 없게 되면 마지막에 올려놓은 사람이 승리한다. 진행중인 게임판이 주어질 때 이번 차례인 사람이 승리할 수 있는 방법이 있는지 판단하는 프로그램을 만들면 된다.

1. 입력의 첫 줄에는 테스트 케이스 C(C <= 50)
1. 각 테스트 케이스는 다섯 줄에 다섯 개의 문자로 구성되며, (#)은 블록, (.)은 빈칸

## Solving

이 게임은 게임판이 주어질 때 양쪽이 둘 수 있는 수가 항상 똑같은 대칭 게임(impartial game)이다. 대칭 게임에서는 게임판만 주어지면 지금이 누구의 차례인지 중요하지 않다. 또한 블록의 정확한 배치는 상관이 없고 각 칸에 블록이 놓여 있느냐 아니냐가 중요하다.

따라서 각 칸에 블록이 있느냐 없느냐를 통해 게임의 승패가 정해진다. 

>`play(board)` = 현재 게임판의 상태가 `board` 일 때 이번 차례인 사람이 이길 방법이 있는지를 반환

모든 블록의 위치에 대해 미리 계산하고 이 비트와 현재 `board` 일 때 AND 연산을 통해 블록을 놓을 수 있는지 판단할 수 있다.

```cpp
vector<int> moves;
inline int cell(int y, int x){return 1 << (y*5 + x);}
void precalc(){
    // L자 3칸 블럭
    for(int y=0;y<4;y++){
        for(int x=0;x<4;x++){
            vector<int> cells;
            for(int dy=0;dy<2;dy++){
                for(int dx=0;dx<2;dx++){
                    cells.push_back(cell(y+dy,x+dx));
                }
            }
            int square = cells[0] + cells[1] + cells[2] + cells[3];
            for(int i=0;i<cells.size();i++){
                moves.push_back(square - cells[i]);
            }
        }
    }
    // 2칸 블럭
    for(int y=0;y<5;y++){
        for(int x=0;x<4;x++){
            moves.push_back(cell(y,x) | cell(y,x+1));
            moves.push_back(cell(x,y) | cell(x+1,y));
        }
    }
}
```

비트마스크를 사용해 `board`를 표현하고, `moves`의 원소와 AND 연산을 통해 놓을 수 있는지 없는지를 판단한다. 게임판에 놓을 수 있는 블록의 위치와 방향 조합은 칸의 수 n에 비례한다. 그리고 $ O(2^n) $개의 부분 문제가 있으니 전체 시간 복잡도는 $ O(n2^n) $이다.

```cpp
char cache[1<<25];
bool play(int board){
    char &ret = cache[board];
    if(ret != -1)
        return ret;
    ret = 0;
    for(int i=0;i<moves.size();i++){
        if((board & moves[i]) == 0){
            if(!play(board | moves[i])){
                ret = 1;
                break;
            }
        }
    }
    return ret;
}
```

##### Resources
- [BLOCKGAME](https://www.algospot.com/judge/problem/read/BLOCKGAME)