---
title: Bertrand's Postulate
author: Beomsu Lee
tags: [math]
---

두 자연수 n과 2n 사이 적어도 소수는 1개 이상 존재한다는 이론이다.

## Overview

임의의 정수 **n >= 2**에 대해 **n < p < 2n**인 소수가 항상 존재한다.

## Implementation

에라토스테네스의 체를 이용하여 빠른 속도로 풀이가 가능하다. n을 입력하여 n보다 크고 2n보다 같거나 작은 소수의 개수를 출력하는 코드이다.

```cpp
#include <iostream>
#include <vector>
#include <sstream>
#include <cmath>

int isPrimNumber(int num);

int main()
{
    int num;
    int count =0 ;

    while (1)
    {
        scanf("%d", &num);
        if(num == 0){
            break;
        }else if(num == 1){
            printf("1\n");
            continue;
        }
        count = 0;

        bool primeArr[num*2 + 1] = {1,1,};

        for (int i = 2; i <= sqrt(num*2); i++)
        {
            if (!primeArr[i])
            {
                for (int j = i * 2; j <= num*2; j += i)
                {
                    if (!primeArr[j])
                    {
                        primeArr[j] = true;
                    }
                }
            }
        }

        for(int i=num+1;i<num*2;i++){
            if(!primeArr[i]){
                count++;
            }
        }
        printf("%d\n",count);
    }

    return 0;
}
```

##### Resources
- [Bertrand's Postulate](https://en.wikipedia.org/wiki/Bertrand%27s_postulate)