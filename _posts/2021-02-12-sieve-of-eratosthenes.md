---
title:  Sieve of Eratosthenes
author: Beomsu Lee
category: [Algorithm, Math]
tags: [algorithm, math, sieve of eratosthenes]
math: true
mermaid: true
---

에라토스테네스가 만들어 낸 소수를 찾는 방법이다. 체로 치듯이 수를 걸러낸다 하여 에라토스테네스의 체라고 불린다.

## Algorithm

1. 2부터 소수를 구하고자 하는 구간의 모든 수를 나열한다.
1. 2는 소수이므로 2를 소수에 추가하고 자신을 제외한 2의 배수를 모두 지운다.
1. 남아있는 수 중 3은 소수이므로 3을 소수에 추가하고 자신을 제외한 3의 배수를 모두 지운다.
1. 남아있는 수 중 5는 소수이므로 5를 소수에 추가하고 자신을 제외한 5의 배수를 모두 지운다.
1. 위 과정을 반복하면 소수를 제외한 나머지는 모두 지워진다.

다음은 그림으로 나타낸 것이며 빠른 이해를 도울 수 있다.

[에라토스테네스의 체](https://commons.wikimedia.org/wiki/File:Sieve_of_Eratosthenes_animation.gif)

## Implementation

```cpp
std::vector<int> eratos(int num){
    bool primeArr[num + 1];
    for(int i=0;i<=sizeof(primeArr)/sizeof(bool);i++){
        primeArr[i]=1;
    }

    // 0과 1은 소수가 아니다.
    primeArr[0] = false;
    primeArr[1] = false;

    for(int i=2;i<=num;i++){
        // 이미 소수가 아니면 생략
        if(!primeArr[i]){
            continue;
        }
        for(int j = i*2 ;j<=num;j+=i){
            // 이미 소수가 아니면 생략
            if(!primeArr[i]){
                continue;
            }
            // 소수가 아님
            primeArr[j] = false;   
        }
    }

    std::vector<int> eratos;
    for(int i=2;i<=num;i++){
        if(primeArr[i]){
            eratos.push_back(i);
        }
    }
    return eratos;
}
```

## References
- [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes)