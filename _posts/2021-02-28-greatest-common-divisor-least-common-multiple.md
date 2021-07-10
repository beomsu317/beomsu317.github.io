---
title:  Greatest Common Divisor, Least Common Multiple
author: Beomsu Lee
category: [Algorithm, Math]
tags: [algorithm, math, gcm, lcm]
math: true
mermaid: true
---

GCM(Greatest Common Divisor)은 최대공약수이며 LSM(Least Common Multiple)은 최소공배수이다. 최대공약수는 두 수를 소인수분해 한 뒤, 두 수의 공통된 소인수를 모두 곱하면 최대공약수, 두 수의 모든 소인수를 곱하면 최소공배수가 된다.

120, 36의 최대공약수는 $12(2^2 * 3)$, 최소공배수는 $360(2^3 * 3^2 * 5)$이다.

## Euclidean Algorithm
최대공약수를 구할 때 작은 수의 경우 직접 계산하여 구할 수 있지만 큰 수의 경우 직접 구하기 어렵다. 따라서 유클리드 호제법(Euclidean-Algorithm)을 사용해 최대공약수를 쉽게 구할 수 있다.

> 두 양의 정수 a, b (a > b)에 대하여 `a = bq + r`이라 하면, a, b의 최대공약수는 b, r의 최대공약수와 같다. 즉, `gcd(a,b)=gcd(b,r), r=0` 이라면, a, b의 최대공약수는 b가 된다.

따라서 두 수 중 큰 수를 작은 수으로 나누고, 나눴던 수와 나머지로 MOD 연산을 반복하는 것이다.

### Example

다음은 123과 321의 최대공약수를 구하는 방법이다.

1. 큰 수(321)을 작은 수(123)으로 나눈다.
```
321 MOD 123 = 75
```

1. 나눈 값(123)을 나머지(75)로 나눈다.
```
123 MOD 75 = 48
```
1. 나눈 값(75)을 나머지(48)로 나눈다.
```
75 MOD 48 = 27
```

1. 나눈 값(48)을 나머지(27)로 나눈다.
```
48 MOD 27 = 21
```
1. 이 과정을 반복한다.
```
27 MOD 21 = 6
21 MOD 6 = 3
6 MOD 3 = 0
```
1. 따라서 123과 321의 최대공약수는 3이 된다.

## Implementation

재귀를 통해 유클리드 호제법을 구현할 수 있다.

```c
int euclid(int n,int mod){
    if(n%mod == 0){
        return mod;
    }else{
        return euclid(mod,n%mod);
    }
}
```

## Least Common Multiple

최대공약수를 구한 상태에서 최소공배수를 구하는 방법은 간단하다. 두 수의 곱은 최대공약수와 최소공배수의 곱과 같기 때문에 A, B인 경우 $A * B = GCM(A, B) * LCM(A, B)$ 공식을 통해 최소공배수를 구할 수 있다.

123, 321의 최대공약수는 3이며 $123 * 321 = 3 * LCM$이 성립한다. 따라서 계산해보면 13161이 최소공배수인 것을 알 수 있다.

## References
- [Euclidean Algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm)