---
title: Matrix Multiplication Fibonacci Algorithm
author: Beomsu Lee
math: true
mermaid: true
tags: [math]
---

## Overview

피보나치 수열이란 첫 번째와 2번째 항이 1이고 3번째 항부터는 이전 2개의 숫자를 더한 점화식을 갖는 수열이다. 이를 행렬 제곱 알고리즘을 이용해 $\log$ 시간 내 구하는 방법을 구현해보자.

## Content

피보나치 수열은 구하는 방법으로는 단순 재귀, 반복적 풀이, 동적 계획법을 사용한 풀이 등이 존재하지만 행렬 곱셈을 이용하면 $O(\log 2n)$ 시간 내 풀이가 가능하다.

다음은 피보나치를 행렬로 만든 점화식이다. 

$$
\begin{multline}
\shoveleft{ F_n = F_{n-1} + F_{n-2} } \cr
\shoveleft{ F_{n-1} = F_{n-1} + 0 * F_{n-2} } \cr
\end{multline}
$$

아래의 식을 $\alpha$라 하자.

$$
\begin{multline}
\shoveleft
{ 
\begin{pmatrix}
F_n \cr
F_{n-1} \cr
\end{pmatrix} 
= 
\begin{pmatrix}
1 & 1 \cr
1 & 0 \cr
\end{pmatrix} 
\begin{pmatrix}
F_{n-1} \cr
F_{n-2} \cr
\end{pmatrix} 
}
\end{multline}
$$

$\alpha$에 $n$ 대신 $n-1$을 대입해 $\beta$를 만들 수 있다.

$$
\begin{multline}
\shoveleft
{ 
\begin{pmatrix}
F_{n-1} \cr
F_{n-2} \cr
\end{pmatrix} 
= 
\begin{pmatrix}
1 & 1 \cr
1 & 0 \cr
\end{pmatrix} 
\begin{pmatrix}
F_{n-2} \cr
F_{n-3} \cr
\end{pmatrix} 
}
\end{multline}
$$

이 $\beta$를 $\alpha$에 대입하면 다음과 같은 식을 만들 수 있다.

$$
\begin{multline}
\shoveleft
{ 
\begin{pmatrix}
F_{n} \cr
F_{n-1} \cr 
\end{pmatrix} 
= 
\begin{pmatrix}
1 & 1 \cr
1 & 0 \cr 
\end{pmatrix} 
\begin{pmatrix}
F_{n-1} \cr
F_{n-2} \cr 
\end{pmatrix} 
=
\begin{pmatrix}
1 & 1 \cr
1 & 0 \cr 
\end{pmatrix} 
\begin{pmatrix}
1 & 1 \cr
1 & 0 \cr 
\end{pmatrix} 
\begin{pmatrix}
F_{n-2} \cr
F_{n-3} \cr 
\end{pmatrix} 
=
{ \begin{pmatrix}
1 & 1 \cr
1 & 0 \cr 
\end{pmatrix} }^2
\begin{pmatrix}
F_{n-2} \cr
F_{n-3} \cr 
\end{pmatrix} 
}
\end{multline}
$$

이런 식으로 계속 진행하게 되면 다음과 같은 식을 얻을 수 있다.

$$
\begin{multline}
\shoveleft
{ 
\begin{pmatrix}
F_{n} \cr
F_{n-1} \cr 
\end{pmatrix} 
= 
{ \begin{pmatrix}
1 & 1 \cr
1 & 0 \cr 
\end{pmatrix} }^2
\begin{pmatrix}
F_1 \cr
F_0 \cr 
\end{pmatrix} 
}
\end{multline}
$$

행렬 $\begin{pmatrix} 1 & 1 \cr 1 & 0 \cr \end{pmatrix} $을 $W$라 하면 아래와 같은 식을 만들 수 있다.

$$
\begin{pmatrix}
F_{n} \cr
F_{n-1} \cr 
\end{pmatrix} 
= 
W^{n-1}
\begin{pmatrix}
F_1 \cr
F_0 \cr 
\end{pmatrix} 
$$

위 식을 정리해 아래와 같이 나타낼 수 있다.

$$
\begin{pmatrix}
F_{n+1} & F_n \cr
F_n & F_{n-1} \cr 
\end{pmatrix} 
= 
{ 
\begin{pmatrix}
1 & 1 \cr
1 & 0 \cr
\end{pmatrix} 
}^n
$$

이를 코드로 구현하면 다음과 같으며 $O(\log 2n)$의 시간이 걸린다.

```cpp
#include <iostream>
#include <vector>
using namespace std;
typedef vector<vector<long long>> matrix;
const long long mod = 1000000007LL;
matrix operator * (const matrix &a, const matrix &b) {
    int n = a.size();
    matrix c(n, vector<long long>(n));
    for (int i=0; i<n; i++) {
        for (int j=0; j<n; j++) {
            for (int k=0; k<n; k++) {
                c[i][j] += a[i][k] * b[k][j];
            }
            c[i][j] %= mod;
        }
    }
    return c;
}
int main() {
    long long n;

    cin >> n;

    if (n <= 1) {
        cout << n << '\n';
        return 0;
    }

    matrix ans = { {1, 0}, {0, 1}};
    matrix a = { {1, 1}, {1, 0}};

    while (n > 0) {
        if (n % 2 == 1) {
            ans = ans * a;
        }
        a = a * a;
        n /= 2;
    }

    cout << ans[0][1] << '\n';

    return 0;
}
```

##### Resources
- [피보나치 수를 구하는 여러가지 방법](https://www.acmicpc.net/blog/view/28)