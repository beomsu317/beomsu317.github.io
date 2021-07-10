---
title: Tic-Tac-Toe
author: Beomsu Lee
category: [Algorithm, Dynamic Programming]
tags: [algorithm, dynamic programming]
math: true
mermaid: true
---

## Problem

틱택토는 3x3 크기의 게임판에서 하는 3목 게임이다. 게임은 항상 x부터 시작하며, 게임을 하는 두 사람 모두 최선을 다한다고 가정할 때, 어느쪽이 이길지 판단하는 프로그램을 만들면 된다.

1. 입력의 첫 줄에는 테스트 케이스 C(<=50)
1. 각 테스트 케이스는 세 줄에 각 세 글자로 게임판 위치에 쓰인 글자가 주어지며 글자가 없는 칸은 (.)로 표현

## Solving

메모제이션을 적용하려면 maps에 vector\<string\>를 넣거나 게임판을 정수로 변환해주는 일대일 함수를 구현해야 한다. 일대일 함수를 구현하는 방법은 `board`를 3진수 숫자로 만드는 것이다. $ 3^9 = 19683 $이므로 시간/공간 내 충분히 계산할 수 있다. 다음은 `board`가 주어졌을 때 3진수의 숫자로 반환하는 함수이다.

```cpp
int cache[19682];
int bijection(const vector<string> &board){
    int ret=0;
    for(int y=0;y<3;y++){
        for(int x=0;x<3;x++){
            ret *=3;
            if(board[y][x] == 'o') 
                ret++;
            else if(board[y][x] == 'x')
                ret += 2;
        }
    }
    return ret;
}
```

틱택토는 승부가 나지 않고 비기는 경우도 존재하므로 `canWin()`의 반환을 3가지로 구분하여야 한다. 

- 이번 순서의 참가자가 이기는 경우(1)
- 비기는 경우(0)
- 최선을 다해도 지는 경우(-1)

다음과 같이 `isFinished()` 함수를 통해 게임이 끝났는지를 기저사례로 한다.

```cpp
bool isFinished(vector<string> &board,char turn){
    // 가로
    for(int y=0;y<3;y++){
        for(int x=0;x<3;x++){
            if(board[y][x] != turn)
                break;
            if(x == 2)
                return true;
            
        }
    }
    // 세로
    for(int y=0;y<3;y++){
        for(int x=0;x<3;x++){
            if(board[x][y] != turn)
                break;
            if(x == 2)
                return true;
            
        }
    }
    // 대각선
    for(int i=0;i<3;i++){
        if(board[i][i] != turn)
            break;
        if(i == 2)
            return true;
    }
    for(int i=0;i<3;i++){
        if(board[i][2-i] != turn)
            break;
        if(i == 2)
            return true;
        
    }
    return false;
}
```

`cache`는 -2로 초기화하여야 하며 -2는 `memset()`을 사용할 수 없으므로 for 문을 돌며 초기화해준다.

```cpp
int canWin(vector<string> &board,char turn){
    // 마지막에 상대방이 뒤서 한 줄이 만들어진 경우
    if(isFinished(board,'o'+'x'-turn)){
        return -1;
    }
    // 메모제이션
    int &ret = cache[bijection(board)];
    if(ret != -2)
        return ret;

    // 최선의 경우를 찾는다.
    int minValue = 2;
    for(int y=0;y<3;y++){
        for(int x=0;x<3;x++){
            if(board[y][x] == '.'){
                board[y][x] = turn;
                minValue = min(minValue,canWin(board,'o'+'x'-turn));
                board[y][x] = '.';
            }
        }
    }
    // 비긴경우가 최선인 경우
    if(minValue == 2 || minValue == 0)
        return ret = 0;
    // 상대가 이기면 나는 무조건 지며, 상대가 지면 나는 무조건 이긴다.
    return ret = -minValue;
}
```

## References
- [TICTACTOE](https://www.algospot.com/judge/problem/read/TICTACTOE)