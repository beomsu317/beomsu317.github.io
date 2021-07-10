---
title: Kotlin Basic
author: Beomsu Lee
category: [Android,Kotlin]
tags: [kotlin]
math: true
mermaid: true
---

## Kotlin Data Types

코틀린의 다양한 데이터 타입의 종류이다.

1. Integer Data type
1. Floating-point Data Type
1. Boolean Data Type
1. Character Data Type

### Integer Data Type

|Data Type|Bits|Min Value|Max Value|
|:---:|:---:|:---:|:---:|
|byte|8 bits|-128|127|
|short|16 bits|-32768|32767|
|int|32 bits|-2147483648|2147483647|
|long|64 bits|-9223372036854775808|9223372036854775807|


```kotlin
var myint = 35
//add suffix L for long integer
var mylong = 23L
  
println("My integer ${myint}")
println("My long integer ${mylong}")

var b1: Byte = Byte.MIN_VALUE
var b2: Byte = Byte.MAX_VALUE
println("Smallest byte value: " +b1)
println("Largest byte value: " +b2)

var S1: Short = Short.MIN_VALUE
var S2: Short = Short.MAX_VALUE
println("Smallest short value: " +S1)
println("Largest short value: " +S2)

var I1: Int = Int.MIN_VALUE
var I2: Int = Int.MAX_VALUE
println("Smallest integer value: " +I1)
println("Largest integer value: " +I2)

var L1: Long = Long.MIN_VALUE
var L2: Long = Long.MAX_VALUE
println("Smallest long integer value: " +L1)
println("Largest long integer value: " +L2)
```

**Output**

```
My integer 35
My long integer 23
Smallest byte value: -128
Largest byte value: 127
Smallest short value: -32768
Largest short value: 32767
Smallest integer value: -2147483648
Largest integer value: 2147483647
Smallest long integer value: -9223372036854775808
Largest long integer value: 9223372036854775807
```

### Floating-Point Data Type

|Data Type|Bits|Min Value|Max Value|
|:---:|:---:|:---:|:---:|
|float|32 bits|1.40129846432481707e-45|3.40282346638528860e+38|
|double|64 bits|4.94065645841246544e-324|1.79769313486231570e+308|


```kotlin
var myfloat = 54F                  // add suffix F for float
println("My float value ${myfloat}")

var F1: Float = Float.MIN_VALUE
var F2: Float = Float.MAX_VALUE
println("Smallest Float value: " +F1)
println("Largest Float value: " + F2)

var D1: Double = Double.MIN_VALUE
var D2: Double = Double.MAX_VALUE
println("Smallest Double value: " + D1)
println("Largest Double value: " + D2)
```

**Output**

```
My float value 54.0
Smallest Float value: 1.4E-45
Largest Float value: 3.4028235E38
Smallest Double value: 4.9E-324
Largest Double value: 1.7976931348623157E308
```

### Boolean Data Type

|Data|Bits|Data Range|
|:---:|:---:|:---|
|boolean|1 bit|true or false|


```kotlin
if (true is Boolean){
    print("Yes,true is a boolean value")
}
```

**Output**

```
Yes, true is a boolean value
```

### Character Data Type

|Data Type|Bits|Min Value|Max Value|
|:---:|:---:|:---:|:---:|
|char|8 bits|-128|127|


```kotlin
var alphabet: Char = 'C'
println("C is a character : ${alphabet is Char}")
```

## Kotlin Variables

1. Immutable은 `val` 키워드 사용
1. Mutable은 `var` 키워드 사용

```kotlin
val myName = "Gaurav"
myName = "Praveen"    // Immutable이기 때문에 컴파일 에러
```

## Kotlin Type Conversion

자바는 작은 타입에서 더 큰 타입으로 implicit 타입 변환을 지원한다. (integer가 long 데이터 타입으로 변환할 수 있는 것처럼) 

하지만 코틀린은 implicit 타입 변환을 지원하지 않는다. integer는 long 데이터 타입으로 할당될 수 없다.

```kotlin
var myNumber = 100
var myLongNumber: Long = myNumber       // Compiler error
// Type mismatch: inferred type is Int but Long was expected
```

코틀린에서는 helper 함수를 사용해 explicit 타입 변환이 가능하다.

- toByte()
- toShort()
- toInt()
- toLong()
- toFLoat()
- toDouble()
- toChar()

```kotlin
var myNumber = 100
var myLongNumber: Long = myNumber.toLong()     // compiles successfully
```

boolean 타입은 helper 함수가 존재하지 않는다.

## Kotlin Labeling

코틀린에는 두 가지의 **break**와 **continue**가 존재한다.

- Labeled break, continue
- Unlabeled break, continue

Unlabeled는 흔히 사용하는 break, countinue이며 Labeled는 루프 시작에 label을 달아 해당 라벨을 break 하거나 continue 할 수 있는 기능이다.

다음은 `outer@` 라벨을 달아 `i == 10`인 경우 바깥의 while 문의 break를 수행하는 예제이다.

```kotlin
outer@ while(true) {
    inner@ while(true) {
        if(i == 10) {
            break@outer
        }
        i++
    }
}
```

## References
- [geeksforgeeks - kotlin](https://www.geeksforgeeks.org/kotlin-programming-language/)