---
title: Karatsuba
author: Beomsu Lee
category: [Algorithm, Divide and Conquer]
tags: [algorithm, divide and conquer]
math: true
mermaid: true
---

카라츠바 알고리즘은 일반 곱셈 알고리즘보다 빠른 곱셈 알고리즘으로 두 개의 정수를 곱하는 알고리즘이다. 수백 자리, 수만 자리 같은 큰 숫자를 다룰 때 주로 사용한다. 

다음은 일반적인 곱셈 수행 과정이다.

```
         1  2  3  4
      x  5  6  7  8
--------------------
         8 16 24 32
      7 14 21 28
   6 12 18 24
5 10 15 20
--------------------
5 16 34 60 61 52 32
```

위의 문제를 코드로 구현하면 다음과 같다.

```cpp
// 자리수 올림의 처리
void normalize(vector<int> &num){
    for(int i=0; i + 1 < num.size();i++){
        if(num[i] < 0){
            int borrow = (abs(num[i]) + 9)/10;
            num[i+1] -= borrow;
            num[i] += borrow*10;
        }else{
            num[i+1] += num[i]/10;
            num[i] %= 10;
        }
    }
    while(num.size() > 1 && num.back() == 0){
        num.pop_back();
    }
}
// 두 정수의 곱을 반환
vector<int> multiply(const vector<int>& a, const vector<int>& b)
{
    vector<int> c(a.size() + b.size() + 1, 0);
    for (int i = 0; i < a.size(); i++) {
        for (int j = 0; j < b.size(); j++) {
            c[i + j] += (a[i] * b[j]);
        }
    }
    normalize(c);
    return c;
}
```

이 알고리즘의 시간 복잡도는 두 정수의 길이가 n이라고 할 때 $O(n^2)$이다. 단순히 for문이 2번 겹쳐있기 때문이다. 

카라츠바의 알고리즘은 두 수를 각각 절반으로 나눈다. a, b가 256자리 수라고 가정하면 a1과 b1은 첫 128자리, $a_0$, $b_0$은 그 다음 128자리를 저장한다. 그럼 다음과 같이 정의할 수 있다.

```
a = a1*10^128 + a0
b = b1*10^128 + b0

a * b = (a1 * 10^128 + a0) * (b1 * 10^128 + b0)
      = a1 * b1 * 10^256 + (ab * b0 + a0 * b1) * 10^128 + a0 * b0
        ----------------   ----------------------------   -------
      =        z2        +              z1              +    z3
```

위의 식을 재귀로 구현하면 다음과 같다.

```cpp
// a += b*(10^k)
void addTo(vector<int>& a, const vector<int> b, int k)
{
    int length = b.size();
    a.resize(max(a.size(), b.size() + k));
    for (int i = 0; i < length; i++)
        a[i + k] += b[i];
}
// a -= b (a > b)
void subFrom(vector<int>& a, const vector<int>& b)
{
    int length = b.size();
    a.resize(max(a.size(), b.size()) + 1);
    for (int i = 0; i < length; i++)
        a[i] -= b[i];
}
vector<int> karatsuba(const vector<int> &a, const vector<int> &b)
{

    int an = a.size(), bn = b.size();
    // a가 작은경우 b, a 변경
    if (an < bn) return karatsuba(b, a);
    // base case 
    if (an == 0 || bn == 0) return vector<int>();
    // 100 이하이면 일반 곱셈을 사용한다.
    if (an <= 100) return multiply(a, b);
    int half = an / 2;
    
    // a와 b를 밑에서 half 자리와 나머지로 분리
    vector<int> a0(a.begin(), a.begin() + half);
    vector<int> a1(a.begin() + half, a.end());
    vector<int> b0(b.begin(), b.begin() + min<int>(b.size(), half));
    vector<int> b1(b.begin() + min<int>(b.size(), half), b.end());
    // z2 = a1 * b1
    vector<int> z2 = karatsuba(a1, b1);
    // z0 = a0 * b0
    vector<int> z0 = karatsuba(a0, b0);
    // a0 = a0 + a1
    addTo(a0, a1, 0);
    // b0 = b0 + b1;
    addTo(b0, b1, 0);
    // z1 = (a0 * b0) - z0 - z2;
    vector<int> z1 = karatsuba(a0, b0);
    subFrom(z1, z0);
    subFrom(z1, z2);
    // ret = z0 + z1*10^half + z2*10^(half*2)
    vector<int> ret;
    addTo(ret, z0, 0);
    addTo(ret, z1, half);
    addTo(ret, z2, half + half);
    return ret;
}
```

## Time Complexity

각 자리수를 2등분하므로 자리 수가 큰 값을 n이라 하면 단계는 $log(n)$이 된다. 그리고 단계마다 곱셈이 3배씩 늘어나기 떄문에 $3^{log(n)}$이 되며 이를 간단하게 표현하면 $O(nlog(3))$이 된다. 일반적인 곱셈의 시간 복잡도 $O(N^2)$보다 빠르다는 것을 알 수 있다.

병합 단계의 시간 복잡도는 단계가 내려갈 때마다 숫자의 길이는 절반으로 줄고, 부분 문제의 개수는 3배 늘기 때문에 i번째 단계에서 필요한 연산 수는 ${ {(\frac{3}{2})}^i}* {n}$ 이 된다. 따라서 모든 단계에서 필요한 전체 연산의 수는 다음 식에 비례한다.

$
n \sum_{i=1}^{log(n)} {(\frac{3}{2})}^i
$

카라츠바 알고리즘의 시간 복잡도는 곱셈이 지배하며 최종 시간 복잡도는 $O({n}^{log(3)})$이 된다.

이러한 방식은 충분히 큰 수는 일반적인 곱셈법보다 빠르지만 작은 수인 경우 추가적인 덧셈과 연산들 때문에 느려지는 경우가 있다.


##### Resources
- [Karatsuba_algorithm](https://en.wikipedia.org/wiki/Karatsuba_algorithm)