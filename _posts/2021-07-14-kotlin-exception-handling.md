---
title: Exception Handling 
author: Beomsu Lee
category: [Android,Kotlin]
tags: [kotlin]
math: true
mermaid: true
---

## Kotlin Exception Handling

예외(Exception)는 예상하지 못하거나 원하지 않는 이벤트가 발생하는 것으로, 프로그램이 실행 중에 발생하며, 프로그램의 정상적인 흐름을 방해한다. 예외처리(Exception handling)은 런타임에 프로그램의 크래시를 방지하는 기술이다. 

2가지 유형의 예외가 있다.

1. Checked Exception - IOException, FileNotFoundException 등과 같은 예외는 전형적으로 메서드에 설정되고 컴파일 타임에 확인된다. 
1. UnChecked Exception - 일반적으로 로직 오류로 인해 NullPointerException, ArrayIndexOutOfBoundException 등 런타임에 확인되는 예외이다.

### Kotlin Exceptions 

코틀린에서 unchecked exception은 런타임에서만 발견된다. 모든 예외 클래스들은 `Throwable`의 자손이다. 

일반적으로 `throw` 표현을 사용해 exception 객체를 넘긴다. 

```kotlin
throw Exception("Throw me")
```

다음은 흔히 발생되는 예외이다.

- NullPointerException: 속성이나 메서드가 null 객체일 때 발생
- Arithmetic Exception: 0으로 나누는 등의 잘못된 산술연산 시 발생
- SecurityException: 보안을 위반할 때 발생
- ArrayIndexOutOfBoundException: 배열의 크기를 넘어갔을 때 발생

이러한 예외들을 처리하기 위해 `try-catch` 블록을 사용한다.

### Kotlin try-catch block 

`try-catch` 블록을 사용해 프로그램의 예외를 처리할 수 있다. `try` 블록은 예외를 throw 하는 것에 대응하고, `catch` 블록은 발생된 예외를 처리한다. `try` 블록 뒤에는 `catch`나 `finally` 블록 중 하나 또는 둘 다 선언되어야 한다.

#### Syntax for try-catch block

```kotlin
try {
   // code that can throw exception
} catch(e: ExceptionName) {
   // catch the exception and handle it
}
```

#### Kotlin program of arithmetic exception handling using try-catch block 

```kotlin
import kotlin.ArithmeticException

fun main(args : Array<String>){
	try{
		var num = 10 / 0
	}
	catch(e: ArithmeticException){
		// caught and handles it
		println("Divide by zero not allowed")
	}
}
```
**Output**
```
Divide by zero not allowed
```

#### Kotlin try-catch block as an expression

이미 알고 있듯이 expression은 항상 값을 반환한다. 코틀린에선 `try-catch` 블록을 expression으로 사용한다. expression에 의해 반환되는 값은 `try` 블록의 마지막 expression 또는 `catch` 블록의 마지막 expression이 된다. 예외가 발생하면 `catch` 블록이 값을 반환한다.

#### Kotlin program of using try-catch as an expression 

```kotlin
fun test(a: Int, b: Int) : Any {
	return try {
		a/b
		//println("The Result is: "+ a / b)
	}
	catch(e:Exception){
		println(e)
		"Divide by zero not allowed"
	}
}
// main function
fun main(args: Array<String>) {
	// invoke test function
	var result1 = test(10,2 ) // execute try block
	println(result1)
	var result = test(10,0 ) // execute catch block
	println(result)
}
```

**Output**
```
5
java.lang.ArithmeticException: / by zero
Divide by zero not allowed
```

### Kotlin finally block 

`finally` 블록은 예외처리 여부와 상관없이 항상 실행된다. 따라서 중요한 코드 문을 실행하는데 사용된다. 예를 들어, 파일을 open하면 예외의 발생 여부에 상관없으 close해주어야 하기 때문에 `finally` 블록에서 처리하는 경우가 있다.

또한 `try` 블록과 `finally` 블록 사이에 `catch` 블록을 스킵할 수 있다.

```kotlin
try {
   // code that can throw exception
} finally {
   // finally block code
}
```

#### Syntax of finally block with try-catch block 

```kotlin
fun main (args: Array<String>){
	try {
		var int = 10 / 0
		println(int)
	} catch (e: ArithmeticException) {
		println(e)
	} finally {
		println("This block always executes")
	}
}
```

**Output**

```
java.lang.ArithmeticException: / by zero
This block always executes
```

### Kotlin throw keyword

`throw` 키워드를 사용해 예외를 명시적으로 발생시킬 수 있다. 또한 이 키워드를 통해 커스텀 예외를 throw 할 수 있다.

```kotlin
fun main(args: Array<String>) {
	test("abcd")
	println("executes after the validation")
}
fun test(password: String) {
	// calculate length of the entered password and compare
	if (password.length < 6)
		throw ArithmeticException("Password is too short")
	else
		println("Strong password")
}
```

**Output**
```
Exception in thread "main" java.lang.ArithmeticException: Password is too short
```

## Kotlin Nested try block and multiple catch block

### Nested try block

중첩된 `try` 블록이란 하나의 `try-catch` 블록 안에 다른 `try-catch` 블록이 있는 것이다. 내부에 예외가 발생했을 때 내부의 `catch`에 의해 처리되지 않는다면 외부의 `try-catch` 블록이 해당 예외를 처리한다.

#### Kotlin program of nested try block 

```kotlin
fun main(args: Array<String>) {
	val numbers = arrayOf(1,2,3,4)

	try {
		for (i in numbers.indices) {
			try {
				var n = (0..4).random()
				println(numbers[i+1]/n)

			} catch (e: ArithmeticException) {
				println(e)
			}
		}
	} catch (e: ArrayIndexOutOfBoundsException) {
		println(e)
	}
}
```

**Output**
```
2
3
java.lang.ArithmeticException: / by zero
java.lang.ArrayIndexOutOfBoundsException: Index 4 out of bounds for length 4
```

### Multiple catch block

`try` 블록은 하나 이상의 `catch` 블록을 가질 수 있다. `try` 블록 안에서 어떤 예외가 발생할지 모르는 경우 여러개의 `catch` 블록을 배치할 수 있으며, 마지막 `catch` 블록에서는 `Exception` 클래스를 사용해 나머지 모든 예외를 처리할 수 있다.

### Use of when in catch block 

코틀린에선 `when`을 사용해 다수의 `catch` 블록을 대체할 수 있다. 

```kotlin
fun main(args: Array<String>) {
	val sc = "GeeksforGeeks"
	try {
		val n = Integer.parseInt(sc.nextLine())
		if (512 % n == 0)
			println("$n is a factor of 512")
	} catch (e: Exception ) {
	when(e){
		is ArithmeticException -> { println("Arithmetic Exception: Divide by zero") }
		is NumberFormatException -> { println("Number Format Exception ") }
	}
	}
}
```

**Input**
```
GeeksforGeeks
```

**Output**
```
Number Format Exception 
```

## References
- [Exception Handling](https://www.geeksforgeeks.org/kotlin-programming-language/?ref=ghm)