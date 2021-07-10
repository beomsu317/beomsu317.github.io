---
title: Kotlin Function
author: Beomsu Lee
category: [Development,Kotlin]
tags: [kotlin]
---

## Kotlin Functions

코틀린은 2가지 타입의 함수가 존재한다. 

- Standard library function
- User defined function

### Kotlin standard library function

코틀린에서는 사용가능하도록 미리 정의된 빌트인 다양한 함수들이 존재한다. 

다음의 경우 빌트인 함수는 `arrayOf()`, `sum()`, `println()`를 사용한다.

```kotlin
fun main(args: Array<String>) {
    var sum = arrayOf(1,2,3,4,5,6,7,8,9,10).sum()
    println("The sum of all the elements of an array is: $sum")
}
```

다음은 `rem()` 함수를 사용해 나머지를 구하는 프로그램이다.

```kotlin
fun main(args: Array<String>) {
    var num1 = 26
    var num2 = 3
  
    var result = num1.rem(num2)
    println("The remainder when $num1 is divided by $num2 is: $result")
}
```

이외에도 다양한 빌트인 함수들이 존재한다.

- sqrt() : 제곱근
- print() : 메시지 표준 출력
- rem() : 나눠진 후 나머지
- toInt() : integer 값으로 변환
- readline() : 표준 입력
- compareTo() : 두 숫자 비교 후 boolean으로 반환

### Kotlin user-defined function



### References
- [geeksforgeeks - kotlin](https://www.geeksforgeeks.org/kotlin-programming-language/)