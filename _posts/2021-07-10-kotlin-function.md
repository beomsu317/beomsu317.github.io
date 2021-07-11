---
title: Kotlin Function
author: Beomsu Lee
category: [Android,Kotlin]
tags: [kotlin]
math: true
mermaid: true
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

코틀린은 함수는 맨 위에 선언될 수 있고, 함수를 가지고 있는 클래스를 만들 필요가 없다. 

일반적으로 함수는 다음과 같이 정의된다. 

```kotlin
fun fun_name(a: data_type, b: data_type, ......): return_type  {
    // other codes
    return
}
```

- fun : 함수를 정의하기 위한 키워드
- fun_name : 함수의 이름
- a: data_type : a는 인자이며, data_type은 인자의 데이터 타입
- return_type : 함수의 반환 값의 데이터 타입
- {....} : 함수의 블록

```kotlin
fun mul(num1: Int, num2: Int): Int {
    var number = num1.times(num2)
    return number
}
```

## Default and Named argument

대부분 언어에선 모든 인자를 명시할 필요가 있지만, 코틀린에서는 모든 인자를 

코틀린의 함수에선 다음과 같이 `,`를 이용해 파라미터를 구분한다.

```kotlin
fun fun_name(name1: data_type, name2: data_type )
```

코틀린에는 두 가지 유형의 인자가 있다.
- Default arguments
- Named arguments

### Default arguments

아무런 인자가 전달되지 않을 경우 Default 인자가 함수의 파라미터로 전달된다. 이 값들은 함수를 선언할 때 초기화되어야 한다. 이렇게 정의된 경우 부분적으로 인자를 전달할 수 있고, 모든 인자를 전달할 수도 있다.

```kotlin
// default arguments in function definition name, standard and roll_no
fun student(name: String="Praveen", standard: String="IX" , roll_no: Int=11) {        
    println("Name of the student is: $name")
    println("Standard of the student is: $standard")
    println("Roll no of the student is: $roll_no")
}
fun main(args: Array<String>) {
    val name_of_student = "Gaurav"
    val standard_of_student = "VIII"
    val roll_no_of_student = 25
    student()         // passing no arguments while calling student
}
```

### Named arguments

만약 인자를 전달할 때 순서 없이 전달하거나, 필요한 인자만 전달할 경우 컴파일 에러가 발생할 수 있다. 따라서 인자의 이름을 지정해줌으로써 이러한 에러들을 피할 수 있다.

```kotlin
// default arguments in function definition
// name,standard and roll_no
fun student( name: String="Praveen", standard: String="IX" , roll_no: Int=11 ) {
    println("Name of the student is: $name")
    println("Standard of the student is: $standard")
    println("Roll no of the student is: $roll_no")
}
  
fun main(args: Array<String>) {
    val name_of_student = "Gaurav"
    val standard_of_student = "VIII"
    val roll_no_of_student = 25
  
    // passing the arguments with name as defined in function
    student(name=name_of_student,roll_no=roll_no_of_student)
}
```

## Lambdas Expressions and Anonymous Functions

람다식 표현과 익명 함수는 따로 함수를 구현하지 않고 즉시 실행될 수 있도록 하는 기능이다. 이름 없는 함수를 익명 함수라 하며, 람다식 표현은 익명 함수라 할 수 있다.

### Lambda Expression

코틀린 람다식은 자바의 람다식과 거의 비슷하다. 

```kotlin
fun main(args: Array<String>) {
    val company = { println("GeeksforGeeks")}
 
    // invoking function method1
    company() 
 
    // invoking function method2
    company.invoke()
}
```

### Syntax of Lambda expression

람다식 표현은 항상 중괄호(`{}`)로 둘러싸여 있으며, 인자는 중괄호 안에 선언된다. `code_body`는 `->` 뒤에 온다. 반환 값이 `Unit`이 아니면, 람다식의 마지막 줄의 값이 반환 값으로 처리된다.

```kotlin
val lambda_name : Data_type = { argument_List -> code_body }
```

다음은 람다식의 예제이다.

```kotlin
val sum = {a: Int , b: Int -> a + b}
```

다음은 선택적인 부분을 제거한 후의 람다식이다.

```kotlin
val sum:(Int,Int) -> Int = { a, b -> a + b}
```

### Type inference in lambdas

코틀린의 타입 추론은 컴파일러가 람다식의 타입을 알아내는데 도움을 준다. 다음은 2개의 숫자를 더하는 람다식이다.

```kotlin
val sum = {a: Int , b: Int -> a + b}
```

코틀린 컴파일러는 이것을 `Int` 유형의 2개의 파라미터를 취하고, `Int` 값을 반환하는 함수라고 인지한다.

```kotlin
(Int,Int) -> Int
```

스트링을 반환하고 싶다면 `toString()` 메서드를 사용해 반환할 수 있다. 이 경우 컴파일러는 반환 값의 유형이 스트링이라고 인지하게 된다.

```kotlin
val sum1 = { a: Int, b: Int ->
    val num = a + b
    num.toString()     //convert Integer to String
}
fun main(args: Array<String>) {
    val result1 = sum1(2,3)
    println("The sum of two numbers is: $result1")
}
```

### Type declaration in lambdas

우리는 명시적으로 람다식의 유형을 선언해야 한다. 람다가 값을 반환하지 않는다면 `Unit`을 사용해야 한다.

```kotlin
val lambda1: (Int) -> Int = ({a -> a * a})
val lambda2: (String,String) -> String = { a , b -> a + b }
val lambda3: (Int)-> Unit = {print(Int)}
```

#### Lambdas can be used as class extension

다음은 클래스의 확장으로써 람다식 표현을 사용하였다. `this` 키워드는 `String`에 사용되었고, `it` 키워드는 람다식에 인자로 전달되는 `Int` 파라미터로 사용되었다. `code_body`는 두 개의 값을 합친 후 반환한다.

```kotlin
val lambda4: String.(Int) -> String = {this + it}
val result = "Geeks".lambda4(50)
println(result)
```

**Output**

```
System.out: Geeks50
```

람다식은 인자가 1개인 경우 인자 이름을 생략할 수 있으며, 인자에 접근하려면 `it` 키워드로 접근할 수 있다. 

### Kotlin program using shorthand form of lambda function

```kotlin
val numbers = arrayOf(1,-2,3,-4,5)
 
fun main(args: Array<String>) {
      println(numbers.filter {  it > 0 })
}
```

### Kotlin program using longhand form of lambda function

```kotlin
val numbers = arrayOf(1,-2,3,-4,5)
 
fun main(args: Array<String>) {
     println(numbers.filter {item -> item > 0 })
}
```

### Returning a value from lambda expression

람다식이 실행된 이후 람다식 마지막의 값이 반환된다. Integer, String, Boolean 등의 유형이 반환될 수 있다.

```kotlin
val find =fun(num: Int): String{
if(num % 2==0 && num < 0) {
    return "Number is even and negative"
   }
    else if (num %2 ==0 && num >0){
    return "Number is even and positive"
    }
    else if(num %2 !=0 && num < 0){
    return "Number is odd and negative"
    }
    else {
    return "Number is odd and positive"
    }
}
fun main(args: Array<String>) {
    val result = find(112)
    println(result)
}
```

**Output**

```
Number is even and positive
```

### Anonymous Function

익명 함수는 선언에서 생략된 함수 이름을 제외하고 정규 함수와 거의 비슷하다. 익명 함수의 구현부는 표현(expression)이나 블록(block)이 될 수 있다.

```kotlin
// expression
fun(a: Int, b: Int) : Int = a * b
```

```kotlin
// block
fun(a: Int, b: Int): Int {
    val mul = a * b
    return mul
}
```

### Return type and parameters

1. 반환 타입과 파라미터는 정규 함수와 동일하지만, 문맥상 추론할 수 있는 경우 파라미터를 생략할 수 있다.
1. 함수의 반환 타입은 표현(expression)인 경우 자동적으로 추론할 수 있으며, 블록(block)인 경우 익명 함수에 대해 명시적으로 지정해주어야 한다.

### Kotlin program to call the anonymous function

```kotlin
// anonymous function with body as an expression
val anonymous1 = fun(x: Int, y: Int): Int = x + y
 
// anonymous function with body as a block
val anonymous2 = fun(a: Int, b: Int): Int {
            val mul = a * b
            return mul
            }
fun main(args: Array<String>) {
    //invoking functions
    val sum = anonymous1(3,5)
    val mul = anonymous2(3,5)
    println("The sum of two numbers is: $sum")
    println("The multiply of two numbers is: $mul")
}
```

## Kotlin Inline Functions

코틀린에서는 고차 함수 또는 람다식이 함수와, 클래스모두 객체로 저장되어 가상 호출 시 런타임 오버헤드가 발생할 수 있다. 이를 해결하기 위해 람다식을 인라인으로 처리하여 메모리 오버헤드를 줄일 수 있다. 고차 함수나 람다식의 메모리 오버헤드를 줄이기 위해 인라인 키워드를 사용해 컴파일러에게 메모리를 할당하지 말고 간단하게 호출 지점의 인라인 코드를 복사하도록 요청한다.

```kotlin
fun higherfunc( str : String, mycall :(String)-> Unit) {
    // inovkes the print() by passing the string str
    mycall(str)
}

fun main(){
    println("GeeskforGeeks: ")
    higherfunc("A Computer Science portal for Geeks",::println)
}
```

디컴파일을 하기 위해 **Tools -> Kotlin -> Show Kotlin Bytecode**의 Decompile을 클릭한다.

```java
public final void higherfunc(@NotNull String str, @NotNull Function1 mycall) {
   Intrinsics.checkNotNullParameter(str, "str");
   Intrinsics.checkNotNullParameter(mycall, "mycall");
   mycall.invoke(str);
}

public final void main() {
   String var1 = "GeeskforGeeks: ";
   boolean var2 = false;
   System.out.println(var1);
   this.higherfunc("A Computer Science portal for Geeks", (Function1)null.INSTANCE);
}
```

`mycall`은 `String`을 파라미터로 전달해 `println()` 함수를 호출한다. `println()` 함수가 호출되는 동안 추가적인 Call이 메모리 오버헤드를 증가시킨다. 

```kotlin
mycall(new Function() {
        @Override
        public void invoke() {
         //println statement is called here.
        }
    });
```

만약 파라미터로 많은 함수를 호출하면 각 함수가 메서드 카운트에 추가된다. 그러면 메모리 성능에 큰 영향을 미치게 된다. 인라인 키워드를 사용하면 어떻게 될까?

```kotlin
inline fun higherfunc( str : String, mycall :(String)-> Unit) {
    // inovkes the print() by passing the string str
    mycall(str)
}

fun main(){
    println("GeeskforGeeks: ")
    higherfunc("A Computer Science portal for Geeks",::println)
}
```

`inline` 키워드를 사용하면, `println()` 람다 표현식이 `main()` 함수에 `System.out.println` 형식으로 복사되며 더 이상 호출이 이루어지지 않는다.

```java
public final void higherfunc(@NotNull String str, @NotNull Function1 mycall) {
   int $i$f$higherfunc = 0;
   Intrinsics.checkNotNullParameter(str, "str");
   Intrinsics.checkNotNullParameter(mycall, "mycall");
   mycall.invoke(str);

}
public final void main() {
   String var1 = "GeeskforGeeks: ";
   boolean var2 = false;
   System.out.println(var1);
   String str$iv = "A Computer Science portal for Geeks";
   int $i$f$higherfunc = false;
   int var5 = false;
   boolean var6 = false;
   System.out.println(str$iv);
}
```

### Kotlin Program of Using Return in Lambda While Passing as an Argument to Inlined Function

코틀린은 람다식에서 `return` 키워드를 통해 값을 반환할 수 없다. 하지만 인라인 키워드를 이용하면, 람다식에서 `return`을 사용할 수 있다. 

2개의 람다식을 인자로 `inlinedFunc()` 함수에 전달했다. 인라인 함수인 `lmbd1()`에서 1번째 표현을 실행하고 강제로 반환하여 `main()` 함수를 강제로 종료시킨다.

```kotlin
fun main(args: Array<String>){
    println("Main function starts")
    inlinedFunc({ println("Lambda expression 1")
    return },      // inlined function allow return
                   // statement in lambda expression
                   // so, does not give compile time error
 
    { println("Lambda expression 2")} )
 
    println("Main function ends")
}
// inlined function
inline fun inlinedFunc( lmbd1: () -> Unit, lmbd2: () -> Unit  ) { 
    lmbd1()
    lmbd2()
}
```

**Output**

```
Main function starts
Lambda expression 1
```

#### crossline keyword

위의 프로그램의 1번째 람다식에서 반환을 중지하려면 `crossline` 키워드를 사용해 표시할 수 있다. 해당 키워드를 추가하면 람다식에 `return` 구문이 있을 경우 컴파일러 에러를 발생시킨다.

```kotlin
fun main(args: Array<String>){
    println("Main function starts")
     inlinedfunc({ println("Lambda expression 1")
        return },     // It gives compiler error
         { println("Lambda expression 2")} )
 
    println("Main function ends")
}
 
inline fun inlinedfunc( crossinline lmbd1: () -> Unit, lmbd2: () -> Unit  ) {
    lmbd1()
    lmbd2()
}
```

#### noinline keyword

인라인 함수로 전달되는 람다식 중 일부만 전달하려면 `noinline` 키워드를 사용하면 된다.

```kotlin

fun main(args: Array<String>){
    println("Main function starts")
    inlinedFunc({ println("Lambda expression 1")
        return },    
        { println("Lambda expression 2")
            return } )    // It gives compiler error
 
    println("Main function ends")
}
 
inline fun inlinedFunc( lmbd1: () -> Unit, noinline lmbd2: () -> Unit  ) {
    lmbd1()
    lmbd2()
}
```

### Reified Type Parameters

제네릭 함수 `genericFunc()`의 타입 `T`는 컴파일 타임에는 존재하지만 런타임에 `Type erasure` 때문에 접근할 수 없다. 따라서 일반적인 클래스에 작성된 함수 body에 제네릭 타입에 접근하고 싶다면 명시적으로 타입을 파라미터로 전달해야 한다.

```kotlin
fun <T> genericFunc(c: Class<T>)
```

하지만 `reified type parameter`와 `inline` 함수를 만들면 추가적으로 `Class<T>` 파라미터를 넘겨줄 필요 없이 런타임에 타입 `T`에 접근할 수 있다. 

```kotlin
fun main(args: Array<String>) {
    genericFunc<String>()
}
 
inline fun <reified T> genericFunc() {
    print(T::class)
}
```

## Kotlin infix function notation

코틀린은 infix 키워드로 표시된 함수는 점이나 괄호를 사용하지 않고 호출할 수 있다. 2가지 유형의 infix 함수 표기법이 있다.

1. Standard library infix 함수 표기
1. User defined infix 함수 표기

### Standard library infix function notation

`like`, `or`, `shr`, `shl` 등을 호출할 때 컴파일러는 함수를 찾고 원하는 함수를 호출한다. 

#### Koltin program using bitwise and operator

`a.and(b)` 함수를 infix `(a and b)`로 사용해 호출하였다. 둘 다 동일하게 출려된 것을 확인할 수 있다.

```kotlin
fun main(args: Array<String>) {
	var a = 15
	var b = 12
	var c = 11
	// call using dot and parenthesis
	var result1 =(a > b).and(a > c)		
	println("Boolean result1 = $result1")
	// call using infix notation
	var result2 =(a > b) and (a > c)		
	println("Boolean result1 = $result2")
}
```

**Output**

```kotlin
Boolean result1 = true
Boolean result1 = true
```

#### Kotlin program of using signed shift right(shr) operator 

```kotlin
fun main(args: Array<String>) {
	var a = 8

	// call using infix notation
	var result1 = a shr 2
	println("Signed shift right by 2 bit: $result1")
	// call using dot and parenthesis
	var result2 = a.shr(1)
	println("Signed shift right by 1 bit: $result2")
}
```

#### Kotlin program of using increment and decrement operators

```kotlin
fun main(args: Array<String>) {
	var a = 8
	var b = 4
	
	println(++a)	 // call using infix notation
	println(a.inc()) // call using dot and parenthesis
	println(--b)	 // call using infix notation
	println(b.dec()) // call using dot and parenthesis
}
```

### User defined infix function notation

함수가 다음을 충족할 경우 infix 표기법을 사용할 수 있다.
- member function 이거나 extension function이여야 한다.
- 하나의 파라미터만 받아야 한다.
- 파라미터는 변수 개수의 인자를 허용하지 않아야 하며 기본 값은 없어야 한다.
- infix 키워드로 표시되어야 한다.

```kotlin
// 멤버 함수이여야 하므로 math 클래스의 함수로 등록
class math {
	// user defined infix member function
	// infix 키워드 사용, 하나의 파라미터만 받고, 기본 값은 없으며 반환 값은 Integer이다.
	infix fun square(n : Int): Int{
		val num = n * n
		return num
	}
}
fun main(args: Array<String>) {
val m = math()
	// call using infix notation
	val result = m square 3
	print("The square of a number is: "+result)
}
```

## Kotlin Higher-Order Functions

코틀린 함수들은 변수와 데이터 구조에 저장될 수 있으며, 인자로 전달되어 다른 고차 함수에서 반환된다.

### Higher-Order Function

코틀린에선 함수를 파라미터로 받아들이거나 함수를 반환할 수 있는 함수를 고차 함수라 한다. Integer, String, Array 대신 익명 함수 또는 람다식을 전달한다. 

### Passing lambda expression as a parameter to Higher-Order Function

고차 함수에 람다식을 파라미터로 전달할 수 있으며, 전달할 수 있는 2가지 유형의 람다식이 있다.
- 반환 값이 `Unit`인 람다식
- 반환 값이 Integer, String 등인 람다식

#### Kotlin program of lambda expression which returns Unit

```kotlin
// 람다식을 정의
var lambda = {println("GeeksforGeeks: A Computer Science portal for Geeks") }
// 하나의 파라미터를 포함하는 고차 함수를 정의
// lmbd는 local 변수 이름, ()는 아무 인자도 받지 않는 함수임을 의미, Unit은 반환 값이 없음을 의미
fun higherfunc( lmbd: () -> Unit ) {	 // accepting lambda as parameter
	lmbd()							 //invokes lambda expression
}
fun main(args: Array<String>) {
	// invoke higher-order function
	higherfunc(lambda)				 // passing lambda as parameter
}
```

**Output**
```
GeeksforGeeks: A Computer Science portal for Geeks
```

#### Kotlin program of lambda expression which returns Integer value

```kotlin
// 람다식을 정의
var lambda = {a: Int , b: Int -> a + b }
// higher order function
// lmbd는 lcoal 변수 이름, (Int, Int)는 두 개의 Integer 타입의 파라미터, -> Int 는 반환 값이 Integer
fun higherfunc( lmbd: (Int, Int) -> Int) {	 // accepting lambda as parameter
		
	var result = lmbd(2,4) // invokes the lambda expression by passing parameters				
	println("The sum of two numbers is: $result")
}

fun main(args: Array<String>) {
	higherfunc(lambda)		 //passing lambda as parameter
}
```

### Passing function as a parameter to Higher-Order function

함수를 고차 함수에 인자로 전달할 수 있다. 전달할 수 있는 2가지 타입의 함수가 있다.
- 반환 값이 `Unit`인 함수
- 반환 값이 Integer, String 등인 함수

#### Kotlin program of passing function which returns Unit

```kotlin
// String을 인자로 받아 출력하는 함수
fun printMe(s:String): Unit{
	println(s)
}
// higher-order function definition
// (str : String) 은 String 파라미터, myfunc: (String) -> Unit 은 반환 값이 Unit인 함수를 의미
fun higherfunc( str : String, myfunc: (String) -> Unit){
// invoke regular function using local name
	myfunc(str)
}
fun main(args: Array<String>) {
	// invoke higher-order function
	higherfunc("GeeksforGeeks: A Computer Science portal for Geeks",::printMe)
}
```

#### Kotlin program of passing function which returns integer value

```kotlin
// 두 개의 숫자를 받아 더해주는 함수
fun add(a: Int, b: Int): Int{
	var sum = a + b
	return sum
}
// higher-order function definition
// 2개의 Integer 유형의 파라미터를 입력 받아 Integer 타입으로 반환
fun higherfunc(addfunc:(Int,Int)-> Int){
	// invoke regular function using local name
	var result = addfunc(3,6)
	print("The sum of two numbers is: $result")
}
fun main(args: Array<String>) {
	// invoke higher-order function
	higherfunc(::add)
}
```

## References
- [geeksforgeeks - kotlin](https://www.geeksforgeeks.org/kotlin-programming-language/)
- [코틀린에서 reified는 왜 쓸까?](https://sungjk.github.io/2019/09/07/kotlin-reified.html)