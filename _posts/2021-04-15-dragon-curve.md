---
title: Dragon Curve
author: Beomsu Lee
tags: [dynamic programming]
---

## Problem

드래곤 커브는 간단한 수학 규칙으로 그릴 수 있는 그림이다. 선분 하나에서 시작해 규칙을 통해 선분이 변형되며 만들어지고, 변형이 한 번 이루어져 세대가 변할 때마다 더욱 복잡한 모양으로 진화한다. 

드래곤 커브를 그리는 방법은 X, Y, F, +, -로 구성된 문자열로 그리며, 한 점에서 시작해 다음과 같이 커브를 그린다.

- F: 앞으로 한 칸 전진
- +: 왼쪽으로 90도 회전
- -: 오른쪽으로 90도 회전
- X, Y: 무시

0세대 드래곤 커브를 그리는 문자열은 FX이다. 그 후의 세대는 이전 문자열의 X, Y를 치환해서 만든다.

- X => X+YF
- Y => FX-Y

따라서 1, 2세대 드래곤 커브는 다음과 같다.

- 1세대: FX+YF
- 2세대: FX+YF+FX-YF

n세대 드래곤 커브의 p부터 l까지의 글자를 출력하는 프로그램을 만들면 된다.

1. 입력의 첫 줄은 테스트 케이스 c(c <= 50)
1. 각 테스트 케이스의 첫 줄은 세대 n(0 <= n <= 50), p(1<= p <= 1,000,000,000), l(1 <= l <= 50)

## Solving

우선 완전 탐색을 통해 전체 드래곤 커브 문자열을 생성하는 알고리즘을 만든 후 이것을 기반으로한 p번째 문자열을 찾는 알고리즘을 만들 것이다.

```cpp
int n,p,l;
void curve(const string &seed,int generation){
    if(generation == 0){
        cout << seed;
        return;
    }
    for(int i=0;i<seed.size();i++){
        if(seed[i] == 'X'){
            curve("X+YF",generation-1);
        }else if(seed[i] == 'Y'){
            curve("FX-Y",generation-1);
        }else{
            cout << seed[i];
        }
    }
}
```

이 코드에서 p번째 글자만 출력하도록 하는 방법은 재귀 호출 시마다 재귀 호출이 몇 글자를 출력할지 미리 알고 있으면 skip과 비교할 수 있다. 따라서 문자열 "X"를 n세대 진화한 길이와 "Y"를 n세대 진화한 길이를 구해보자. X 또는 Y가 확장했을 때의 결과의 길이이다.

$$
xLength(n)=xLength(n-1)+yLength(n-1)+2\\
yLength(n)=xLength(n-1)+yLength(n-1)+2\\
$$

결과적으론 $ xLength(n)=yLength(n) $이다. 따라서 다음과 같이 단순화할 수 있다.

$ length(n) = 2+2length(n-1) $

먼저 `preCalc()`에서 각 문자열의 길이를 미리 계산한다.

```cpp
int length[51];
// 오버플로우 방지
int MAX=1000000000+1;
void preCalc(){
    length[0]=1;
    for(int i=1;i<=50;i++){
        length[i] = min(MAX,length[i-1]*2+2);
    }
}
```

미리 계산된 문자열의 길이를 `skip`과 비교하며 `skip`이 `length[generation]`보다 작으면 값을 찾는 방식으로 구현하면 된다.

```cpp
char expand(const string &curve,int generation,int skip){
    if(generation == 0){    
        // curve의 skip번째 글자
        return curve[skip];
    }
    for(int i=0;i<curve.size();i++){
        if(curve[i] == 'X' || curve[i] == 'Y'){
            // length[generation]보다 skip이 크다면 length[generation]만큼 건너뜀
            if(skip >= length[generation]){
                skip -= length[generation];
            }else if(curve[i] == 'X'){
                return expand("X+YF",generation - 1,skip);
            }else{
                return expand("FX-Y",generation - 1,skip);
            }
        // +, -와 같은 확장되지 않는 문자 
        }else if(skip > 0){
            skip--;
        // skip == 0 이므로 찾는 문자
        }else{
            return curve[i];
        }
    }
}
```

##### Resources
- [DRAGON](https://www.algospot.com/judge/problem/read/DRAGON)