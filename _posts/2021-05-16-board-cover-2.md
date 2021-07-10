---
title: Board Cover 2
author: Beomsu Lee
math: true
mermaid: true
tags: [combinatorial search]
---

## Problem

HxW 크기의 게임판과 한 가지 모양의 블록이 여러개 있다. 게임판에 가능한 많은 블록을 올려놓는 프로그램을 만들면 되며 주어진 블록을 자유롭게 회전하여 놓을 수 있지만 서로 겹치거나, 격자에 어긋나거나, 검은 칸을 덮거나, 게임판 밖으로 나가선 안된다.

1. 입력의 첫 줄에는 테스트 케이스의 수 $T(T<=100)$
1. 각 테스트 케이스의 첫 줄에는 게임판의 크기 $H, W(1<=H,W<=10)$와 블록의 모양을 나타내는 격자의 크기 $ R, C(1<=R, C<=10)$
1. 다음 $H$줄에는 각 $W$글자의 문자열로 게임판이 주어짐
1. 다음 $R$줄에는 각 $C$글자의 문자열로 블록의 모양이 주어지며 `#`은 블록의 일부, `.`는 빈 칸

## Solving

회전이 자유롭다는 것은 주어진 블록에 대해 4가지 방법이 있다는 것이다. 따라서 이 4가지를 전처리 과정을 통해 미리 저장해 두고 진행해야 한다. 

```cpp
// 블록의 모든 회전한 형태를 상대 좌표 목록으로 저장
vector<vector<pair<int,int> > > rotations;
// 블록의 크기
int block_size;

vector<string> rotate(const vector<string> &block){
    vector<string> ret(block[0].size(),string(block.size(),' '));
    for(int i=0;i<block.size();i++){
        for(int j=0;j<block[0].size();j++){
            ret[j][block.size() - i - 1] = block[i][j];
        }
    }
    return ret;
}
// block의 4가지 회전 형태를 만들고 이를 상대 좌표의 목록으로 변환
void generateRotations(vector<string> &block){
    rotations.clear();
    rotations.resize(4);
    for(int rot=0;rot<4;rot++){
        int y = -1, x = -1;
        for(int i=0;i<block.size();i++){
            for(int j=0;j<block[0].size();j++){
                if(block[i][j] == '#'){
                    // 가장 윗줄 맨 왼쪽에 있는 칸이 원점
                    if(y == -1){
                        y = i;
                        x = j;
                    }
                    // 각 칸의 위치를 원점으로부터 상대좌표로 표현
                    rotations[rot].push_back(make_pair(i - y, j - x));
                }
            }
        }
        // 시계 방향으로 90도 회전
        block = rotate(block);
    }
    // 중복 제거
    sort(rotations.begin(),rotations.end());
    rotations.erase(unique(rotations.begin(),rotations.end()),rotations.end());
    // 블록 사이즈 저장
    block_size = rotations[0].size();
}
```

모든 칸을 덮을 수 없는 경우가 있기 때문에 현재 칸을 항상 덮는 것이 아닌 빈 칸으로 남겨 두는 경우도 고려해야 한다. 이렇게 큰 답을 찾아야 하는 경우 낙관적인 휴리스틱 문제들를 과소평가 대신 과대평가한다. 즉, 실제로 놓을 수 있는 블록 수 이상을 항상 반환해야 하는 것이다. 휴리스틱 함수를 만드는 쉬운 방법은 블록을 통째로 내려놓아야 하는 제약을 없애, 블록을 한 칸씩 쪼개 놓을 수 있도록 문제를 변형하는 것이다. 따라서 단순히 남은 빈 칸의 수를 블록의 크기로 나눈 값은 실제 놓을 수 있는 블록의 수 이상이기 때문에, 항상 답의 상한이 된다. 이 답의 상한이 현재 찾은 최적해 이하라면 더 이상 탐색을 수행할 필요가 없게된다. 

```cpp
int H,W,R,C;
// 게임판의 각 칸의 정보
int covered[10][10];
// 최적해
int best;

// 블록을 놓을 때 이미 놓인 블록이나 검은 칸과 겹치면 거짓, 아니면 참을 반환
bool set(int y,int x, const vector<pair<int,int> > &block,int delta){
    bool result = true;
    for(int i=0;i<block.size();i++){
        // 범위 안에 있는 경우
        if(y + block[i].first >= 0 && y + block[i].first < H && x + block[i].second >= 0 && x + block[i].second < W){
            covered[y + block[i].first][x + block[i].second] += delta;
            result = result && (covered[y + block[i].first][x + block[i].second] == 1);
        }else{
            return false;
        }
    }
    return result;
}

// 가지치기 
bool prune(int placed){
    int cnt = 0;
    for(int i=0;i<H;i++){
        for(int j=0;j<W;j++){
            // 빈 칸을 다 더한다.
            cnt += !(covered[i][j]) ? 1 : 0;
        }
    }
    // 더한 값을 block_size로 나누고 placed와 합친 결과가 최적해 이하면 true 반환
    return ((cnt / block_size) + placed <= best);
}

void search(int placed){
    if(prune(placed)){
        return;
    }
    // 아직 채우지 못한 빈 칸 중 가장 윗줄 왼쪽에 있는 칸을 찾는다.
    int y = -1, x = -1;
    for(int i = 0;i < H;i++){
        for(int j=0;j < W;j++){
            if(covered[i][j] == 0){
                y = i;
                x = j;
                break;
            }
        }
        if(y != -1){
            break;
        }
    }
    // 기저 사례
    if(y == -1){
        best = max(best,placed);
        return;
    }
    // 이 칸을 덮는다. 
    for(int i=0;i < rotations.size();i++){
        if(set(y,x,rotations[i],1)){
            search(placed + 1);
        }
        set(y,x,rotations[i],-1);
    }
    // 이 칸을 덮지 않고 막는 경우도 탐색한다.
    covered[y][x] = 1;
    search(placed);
    covered[y][x] = 0;
}

int solve(){
    best = 0;
    // covered 배열 초기화
    for(int i=0; i < H;i++){
        for(int j=0; j < W; j++){
            covered[i][j] = (board[i][j] == '#' ? 1 : 0);
        }
    }
    search(0);
    return best;
}
```

##### Resources
- [BOARDCOVER2](https://www.algospot.com/judge/problem/read/BOARDCOVER2)