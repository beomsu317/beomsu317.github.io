---
title: Morse Dictionary
author: Beomsu Lee
tags: [dynamic programming]
---

## Problem

모스 부호는 짧은 신호(단점, o)와 긴 신호(장점, -)으로 나타내는 표현방식이다. 이 n개의 장점과 m개의 단점으로 구성된 모든 신호를 담고 있는 사전이 있고, 이 신호들은 사전순서대로 정렬되어 있다. n = m = 2 인 경우 다음과 같다.

```
--oo
-o-o
-oo-
o--o
o-o-
oo--
```

여기서 k 번째 신호를 출력하는 프로그램을 만들면 된다. 예를 들어 위에서 4번째 신호는 o\-\-o 이다.

1. 입력의 첫 줄에는 테스트 케이스의 수 C(<= 50)
1. 각 테스트 케이스는 3개의 정수 n, m(1 <= n,m <= 100), k(1 <= k <= 1,000,000,000)

## Solving

우선 간단하게 완전 탐색으로 구현하여 k번째의 신호를 출력할 수 있다. 

```cpp
int k;
void generate2(int n,int m,string s){
    // base case
    if(k < 0) return;
    if(n == 0 && m == 0){
        // k가 0인 경우 출력
        if(k == 0) cout << s << "\n";
        k--;
        return; 
    }
    if(n > 0) generate2(n-1,m,s+"-");
    if(m > 0) generate2(n,m-1,s+"o");
}
```

위의 코드는 신호를 하나하나 만들어야 해서 k가 크다면 시간 안에 답을 구할 수 없다. 이를 좀 더 빠르게 구현하는 방법이 있다. `generate2(n,m,s)`가 호출되어 n개의 장점과 m개의 단점을 s뒤에 이어야 하는데, 이를 조합할 수 있는 방법은 이항 계수로 표현할 수 있다.

$ $
\eqalign{
\frac {(n+m)!}{n!m!}
&= \frac {(n+m)!}{n!((n+m)-n)!} \\ 
&= \binom {n+m}{n}
} 
$$

이 때 k가 이항 계수보다 같거나 크다면 `generate2(n,m,s)`가 종료할 때 k는 $ \binom {n+m}{n} $만큼 줄어 있고, 답은 구하지 못한 상태가 된다. 따라서 굳이 실행할 필요 없이 k만 줄이고 종료해도 똑같은 결과가 된다. 따라서 각각의 경우의 수를 저장하고 k가 이항 계수보다 큰 경우 그만큼 k를 줄여버리면 된다.

n = m = 100 인 경우 전체 신호의 수는 $ \binom {200}{100} \approx 9 * {10}^{58}$으로 정수가 저장할 수 있는 범위를 넘어 오버플로가 발생하게 된다. 하지만 k는 항상 10억 이하이고 k를 이용해 대소 비교만 수행하기 때문에 `min()`을 사용해 오버플로를 방지할 수 있다. 이렇게 구현할 경우 각 이항 계수의 시간 복잡도는 $ O(n+m) $이며, 처음에 각 이항 계수를 미리 계산하는데는 $ O(nm) $의 시간이 걸리기 때문에 전체 시간 복잡도는 $ O(nm) $이 된다.

```cpp
int bino[201][201];
const int M = 1e9 + 100;
// 모든 이항 계수 계산
void calcBino(){
    memset(bino,0,sizeof(bino));
    // 파스칼의 삼각형 점화식을 사용
    for(int i=0;i<=200;i++){
        bino[i][0] = bino[i][i] = 1;
        for(int j=1; j<i;j++){
            // 이항 계수는 오버플로우 발생 가능하므로 min()을 통해 오버플로 방지
            bino[i][j] = min(M,bino[i-1][j-1] + bino[i-1][j]);
        }
    }
}
void generate3(int n,int m,string s){
    // base case
    if(k < 0) return;
    if(n == 0 && m == 0){
        if(k == 0) cout << s << "\n";
        k--;
        return; 
    }
    // bino[n+m][n]보다 k가 크다면 k를 이항 계수만큼 줄인다.
    if(bino[n+m][n] <= k){
        k -= bino[n+m][n];
        return;
    }
    if(n > 0) generate3(n-1,m,s+"-");
    if(m > 0) generate3(n,m-1,s+"o");
}
```

이를 더 깔끔하게 구현하는 방법이 있다. 첫 글자가 장점이면 나머지 부분은 n-1개의 장점과 m개의 단점이 있게 된다. 따라서 $ \binom {n+m-1}{n-1} $개가 있게 된다. 장점으로 시작되는 신호의 수가 k보다 작다면 이 신호들을 건너뛰게 되니 단점으로 시작하게 될 것이다. 이를 통해 다음과 같은 점화식을 세울 수 있다.

$ 
kth(n,m,k) = 
\begin{cases}
{"-" + kth(n-1,m,k)} & \text{ if } n > 0, k < \binom {n+m-1}{n-1} \\
{"o" + kth(n,m-1,k - \binom {n+m-1}{n-1})} & \text{ else }
\end{cases}
$

위의 점화식으로 다음과 같이 구현할 수 있다.

```cpp
string kth(int n,int m,int k){
    // n == 0인 경우 모두 'o'이기 때문에 m 개수만큼의 'o' 반환
    if(n == 0) return string(m,'o');
    // 
    if(bino[n+m-1][n-1] > k)
        return "-" + kth(n-1,m,k);
    return "o" + kth(n,m-1,k - bino[n+m-1][n-1]);
}
```


##### Resources
- [MORSE](https://www.algospot.com/judge/problem/read/MORSE)