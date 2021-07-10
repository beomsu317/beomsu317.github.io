---
title: Kotlin Array & String
author: Beomsu Lee
category: [Android]
tags: [kotlin]
---

## Kotlin Array

### Create Array

`arrayOf()` 함수를 사용해 배열을 생성할 수 있다.

```kotlin
val num = arrayOf(1, 2, 3, 4)   //implicit type declaration
val num = arrayOf<Int>(1, 2, 3) //explicit type declaration
```

Array constructor를 통해서도 배열을 생성할 수 있다. 1번째 인자는 사이즈이며, 두 번째 인자는 요소를 초기화하는 함수를 전달한다.

```kotlin
val arrayname = Array(5, { i -> i * 1 })
for (i in 0..arrayname.size-1)
{
    println(arrayname[i])
}
```

코틀린은 초기 데이터 타입의 배열을 생성하는 내장된 메서드가 있다.

- byteArrayOf()
- charArrayOf()
- shortArrayOf()
- longArrayOf()

```kotlin
val num = intArrayOf(1, 2, 3, 4)
```

### Accessing and Modifiying

`get()`, `set()` 멤버 함수를 이용해 item에 접근, 변경할 수 있다.

```kotlin
val x = num.get(0)
num.set(1, 3)
```

index operator인 `[]`를 사용해도 접근, 변경 할 수 있다.

```kotlin
val x = num[1]
num[2] = 5;
```

### Traversing Arrays

다음음 코틀린에서 배열을 순회하기 위한 가장 간단하고 흔히 사용되는 코드이다.

```kotlin
for(i in num.indices){
      println(num[i])
}
```

또한 코틀린에서는 `..`을 사용해 시작과 끝의 범위를 지정하여 배열을 순회할 수 있다. 조심해야 할 점은 배열의 경우 size -1을 해주어야 마지막 원소까지 순회한다. 

```kotlin
val arrayname = arrayOf<Int>(1, 2, 3, 4, 5)
for (i in 0..arrayname.size-1)
{
    println(arrayname[i])
}
```

`foreach`를 사용해서도 배열의 원소에 접근할 수 있다.

```kotlin
val arrayname = arrayOf<Int>(1, 2, 3, 4, 5)
arrayname.forEach({ index -> println(index) })
```

## Kotlin String

코틀린 스트링은 자바 스트링과 비슷하지만 몇 개의 함수들이 추가되었다. 코틀린 스트링은 immutable이며 이것은 스트링의 길이를 변경할 수 없다는 의미이다. 

코틀린에서는 다음과 같이 스트링을 선언할 수 있다. 

```kotlin
var variable_name = "Hello, Geeks"   
var variable_name2 : String = "GeeksforGeeks"
```

빈 스트링을 생성하려면 `String()` 클래스의 인스턴스를 생성해야 한다.

```kotlin
var variable_name = String()
```

### Functions

- `length` : 스트링의 길이를 반환

```kotlin
var s =" String"
println(s.length)
```

- `get(index)` : index의 값을 반환

```kotlin
s.get(3) // Output: - i
```

- `subSequence(start, end)` : `start` ~ `end -1` 까지의 스트링을 반환

```kotlin
s.subSequence(1, 4) // Output: - tri
```

- `str.compareTo(string)` : `str` == `string`이면 0을 반환


### References
- [geeksforgeeks - kotlin](https://www.geeksforgeeks.org/kotlin-programming-language/)