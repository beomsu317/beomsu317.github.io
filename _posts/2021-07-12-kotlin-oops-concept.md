---
title: Kotlin OOPs Concept
author: Beomsu Lee
category: [Android,Kotlin]
tags: [kotlin]
math: true
mermaid: true
---

## Kotlin Class and Objects

코틀린은 함수 및 OOP를 모두 지원한다. 클래스와 객체는 OOP의 기본 개념이며, 이는 상속, 추상화 등을 지원한다.

### Class

자바와 마찬가지로 Class는 유사한 속성을 가진 객체의 blueprint 이다. 객체를 사용하기 전 클래스를 정의해야 하며 class 키워드를 사용해 클래스를 정의한다. 클래스 선언은 클래스의 이름, 클래스의 헤더, 중괄호로 둘러싸인 클래스 바디로 구성된다.

#### Syntax of class declaration

```kotlin
class className {      // class header
   // property
   // member function
}
```

클래스의 생성자는 `constructor` 키워드를 사용해 만들 수 있다.

```kotlin
class className constructor(parameters) {    
   // property
   // member function
}
```

#### Example of Koltin class 

객체들은 클래스의 속성 및 멤버 함수에 접근하는데 사용되며 다음 3가지의 구성을 갖는다.

- State : 객체의 속성을 나타낸다. 
- Behavior : 객체의 함수를 나타낸다.
- Identity : 객체에 고유한 이름을 부여하고 객체가 다른 객체와 상호작용 할 수 있도록 도와주는 역할이다.

```kotlin
class employee {
    // properties
    var name: String = ""
    var age: Int = 0
    var gender: Char = 'M'
    var salary: Double = 0.toDouble()
   //member functions 
   fun name(){
   }
   fun age() {
   }
   fun salary(){
   }
}
```

#### Create an object

클래스를 참조함으로써 객체를 생성할 수 있다.

```kotlin
var obj = className()
```

#### Accessing the property of the class

클래스 객체의 속성에 다음과 같이 접근할 수 있다. 클래스를 이용해 객체를 생성한 후 속성에 접근한다.

```kotlin
obj.nameOfProperty
```

#### Accessing the member function of class

객체를 사용해 멤버 함수에 접근할 수 있다.

```kotlin
obj.funtionName(parameters)
```

#### Kotlin program of creating multiple objects and accessing the property and member function of class 

```kotlin
class employee {// Constructor Declaration of Class

	var name: String = ""
	var age: Int = 0
	var gender: Char = 'M'
	var salary: Double = 0.toDouble()

	fun insertValues(n: String, a: Int, g: Char, s: Double) {
		name = n
		age = a
		gender = g
		salary = s
		println("Name of the employee: $name")
		println("Age of the employee: $age")
		println("Gender: $gender")
		println("Salary of the employee: $salary")
	}
	fun insertName(n: String) {
		this.name = n
	}

}
fun main(args: Array<String>) {
	// creating multiple objects
	var obj = employee()
	// object 2 of class employee
	var obj2 = employee()

	//accessing the member function
	obj.insertValues("Praveen", 50, 'M', 500000.00)

	// accessing the member function
	obj2.insertName("Aliena")

	// accessing the name property of class
	println("Name of the new employee: ${obj2.name}")

}
```

## Kotlin Nested class and Inner class

### Nested Class

클래스안에 클래스가 정의되는 클래스를 중첩(Nested) 클래스라 한다. 기본적으로 중첩 클래스는 `static`이라서 클래스 객체를 만들지 않고도 `.`을 이용해 접근할 수 있다.

```kotlin
// outer class declaration
class outerClass {
	var str = "Outer class"
	// nested class declaration
	class nestedClass {
		val firstName = "Praveen"
		val lastName = "Ruhil"
	}
}
fun main(args: Array<String>) {
	// accessing member of Nested class
	print(outerClass.nestedClass().firstName)
	print(" ")
	println(outerClass.nestedClass().lastName)
}
```

**Output**

```
Praveen Ruhil
```

코틀린에서 중첩 클래스의 멤버 함수에 접근하기 위해 중첩 클래스의 객체를 만들고 그것을 이용해 멤버 함수를 호출한다.

```kotlin
// outer class declaration
class outerClass {
	var str = "Outer class"
	// nested class declaration
	class nestedClass {
		var s1 = "Nested class"
		// nested class member function
		fun nestfunc(str2: String): String {
			var s2 = s1.plus(str2)
			return s2
		}
	}
}
fun main(args: Array<String>) {
	// creating object of Nested class
	val nested = outerClass.nestedClass()
	// invoking the nested member function by passing string
	var result = nested.nestfunc(" member function call successful")
	println(result)
}
```

**Output**
```
Nested class member function call successful
```

### Comparison with Java

코틀린 클래스는 자바 클래스와 매우 유사하지만 동일하진 않다. 코틀린의 nested class는 자바의 static nested class와 유사하고, inner class는 자바의 non-static nested class와 유사하다.

### Kotlin Inner Class

클래스 안에서 `inner` 키워드를 사용해 클래스를 정의한 것을 inner 클래스라 한다. `inner` 키워드를 추가하면 묵시적으로 외부 클래스를 참조할 수 있다.

다음은 클래스 안의 내부 클래스에서 외부의 `str`에 접근하려고 하면 컴파일 타임 에러가 발생한다.(nested class)

```kotlin
// outer class declaration
class outerClass {
	var str = "Outer class"
	// innerClass declaration without using inner keyword
	class innerClass {
		var s1 = "Inner class"
		fun nestfunc(): String {
			// can not access the outer class property str
			var s2 = str
			return s2
		}
	}
}
// main function
fun main(args: Array<String>) {
	// creating object for inner class
	val inner= outerClass().innerClass()
	// inner function call using object
	println(inner.nestfunc())
}
```

`inner` 키워드를 사용해 inner 클래스를 정의하고, 내부 클래스를 사용하기 위해 외부 클래스의 인스턴스를 생성한다. 그럼 컴파일 타임에 에러가 발생하지 않고 정상적으로 실행되는 것을 확인할 수 있다.

```kotlin
// outer class declaration
class outerClass {
	var str = "Outer class"
	// innerClass declaration with using inner keyword
	inner class innerClass {
		var s1 = "Inner class"
		fun nestfunc(): String {
			// can access the outer class property str
			var s2 = str
			return s2
		}
	}
}
// main function
fun main(args: Array<String>) {
	// creating object for inner class
	val inner= outerClass().innerClass()
	// inner function call using object
	println(inner.nestfunc()+" property accessed successfully from inner class ")
}
```
**Output**

```
Outer class property accessed successfully from inner class
```

## Kotlin Setters and Getters

코틀린에서 속성을 정의할 경우 다른 변수들을 선언하는 것과 동일하게 선언하면 된다. `var` 키워드를 통해 mutable 한 변수를 생성하거나, `val` 키워드를 통해 immutable 한 변수를 선언할 수 있다.

### Syntax of property
```kotlin
var <propertyName>[: <PropertyType>] [= <property_initializer>]
    [<getter>]
    [<setter>]
```

### Setters and Getters

코틀린은 `getter`와 `setter`가 자동적으로 만들어진다. 다음의 예제를 보자.

```kotlin
class Company {
var name: String = "Defaultvalue"
}
```

위 코드는 다음의 코드와 동일하다.

```kotlin
class Company {
    var name: String = "defaultvalue"
        get() = field                     // getter
        set(value) { field = value }      // setter
}
```

위 클래스를 `c` 객체로 만들어 `name` 속성을 초기화할 때 setter의 파라미터로 전달되며 `field`의 값을 설정한다. 또 객체의 `name` 속성에 접근할 때 `get() = field` 코드로 인해 `field`에 접근할 수 있다. `.` 표기를 통해 객체의 속성에 get 또는 set을 수행할 수 있다.

```kotlin
val c = Company()
c.name = "GeeksforGeeks"  // access setter
println(c.name)           // access getter (Output: GeeksforGeeks)
```

### private modifier

만약 `get` 메서드만을 공개적으로 접근할 수 있도록 하려면 다음과 같이 구현한다. set 할 경우 해당 값을 설정하는 메서드를 따로 구현해주어야 한다.

```kotlin
class Company () {
	var name: String = "abc"
		private set

	fun myfunc(n: String) {
		name = n			 // we set the name here
	}
}

fun main(args: Array<String>) {
	var c = Company()
	println("Name of the company is: ${c.name}")
	c.myfunc("GeeksforGeeks")
	println("Name of the new comapny is: ${c.name}")
}
```

**Output**

```
Name of the company is: abc
Name of the new comapny is: GeeksforGeeks
```

## Class Properties and Custom Accessors

클래스의 가장 기본적으고 중요한 요소 중 하나는 **캡슐화(Encapsulation)**이다. 자바에서 데이터가 필드에 저장되며 이는 대부분 `private`이다.

accessor methods : 데이터에 접근할 수 있도록 getter와 setter를 제공한다. 

### Property

속성(Property)는 자바의 경우 접근자(Accessor)와 필드(Field)의 조합이다. 코틀린의 경우 접근자와 필드를 대체할 수 있는 기능이 있다. 클래스의 속성은 `val` 또는 `var` 키워드로 변수를 선언하는 것과 동일하게 선언된다. 

```kotlin
class Abc(
    val name: String, 
    val ispassed : Boolean
)
```

- Readable property : field, trivial getter
- Writable property : getter, setter, field

코틀린에서 생성자는 `new` 키워드 없이 호출할 수 있다. getter를 호출하는 대신, 속성이 직접적으로 참조한다. 자바의 로직은 그대로 남아있지만 코드는 훨씬 간결해졌다. 변경 가능한 속성의 setter도 비슷하게 동작한다.

```kotlin
class Abc(
	val name: String,
	val ispassed : Boolean
)

fun main(args: Array<String>) {

	val abc = Abc("Bob",true)
	println(abc.name)
	println(abc.ispassed)

	/*
	In Java
	Abc abc = new Abc("Bob",true);
	System.out.println(person.getName());
	System.out.println(person.isMarried());

	*/
}
```

### Customer Accessors

커스텀으로 구현한 속성 접근자이다. `isSquare` 속성은 값을 저장하기 위한 필드가 필요없다. 단지 커스텀 getter 만 구현해 제공하면 된다. 매번 해당 속성에 접근할 때마다 값들이 계산된다.

```kotlin
class Rectangle(val height: Int, val width: Int)
{
	val isSquare: Boolean
		get() {
			return height == width
		}
}

fun main(args: Array<String>) {

	val rectangle = Rectangle(41, 43)
	println(rectangle.isSquare)	
}
```

**Output**
```
false
```

## Kotlin constructor

생성자(Constructor)는 객체가 처음 생성될 때 호출되는 특별한 멤버 함수이며 변수나 속성을 초기화할 때 사용된다. 클래스는 생성자를 가지고 있어야 하며 생성자를 선언하지 않으면 디폴트 생성자가 만들어진다. 

코틀린에선 2가지 생성자가 존재한다.

1. Primary Constructor
1. Secondary Constructor

코틀린은 하나의 primary constructor와 하나 이상의 secondary constructor를 가질 수 있다. 전자는 클래스를 초기화하는 반면 후자는 클래스를 초기화하고 몇 가지 추가 로직을 구현하는데 사용된다.

### Primary Constructor

주요 생성자는 클래스 이름 뒤 `constructor` 키워드를 사용해 클래스 헤더에서 초기화된다. 

```kotlin
class Add constructor(val a: Int, val b: Int) {
     // code
}
```

`constructor` 키워드는 어노테이션이나 접근지정자가 지정되지 않은 경우 생략될 수 있다.

```kotlin
class Add(val a: Int, val b: Int) {
     // code
}
```

#### Kotlin program of primary constructor

5, 6 숫자 2개를 입력받아 `Add` 생성자에서 초기화된다. 로컬 변수인 `c`는 결과 값을 가지고 있다. `main()`에서 `add.c`를 통해 생성자의 속성에 접근했다.

```kotlin
//main function
fun main(args: Array<String>)
{
	val add = Add(5, 6)
	println("The Sum of numbers 5 and 6 is: ${add.c}")
}
//primary constructor
class Add constructor(a: Int,b:Int)
{
	var c = a+b;
}
```

#### Primary Constructor with Initializer Block

주요 생성자는 코드를 포함할 수 없으며 초기화 코드는 `init` 키워드가 앞에 붙은 별도의 초기화 블록에 배치해야 한다.



```kotlin
fun main(args: Array<String>) {
	val emp = employee(18018, "Sagnik")
}
class employee(emp_id : Int , emp_name: String) {
	val id: Int
	var name: String

	// initializer block
	init {
		id = emp_id
		name = emp_name

		println("Employee id is: $id")
		println("Employee name: $name")
	}
}
```

**Output**

```
Employee id is: 18018
Employee name: Sagnik
```

#### Default value in primary constructor

함수와 비슷하게 생성자를 통해 디폴트 값을 정의할 수 있다.

```kotlin
fun main(args: Array<String>) {
	val emp = employee(18018, "Sagnik")
	// default value for emp_name will be used here
	val emp2 = employee(11011)
	// default values for both parameters because no arguments passed
	val emp3 = employee()

}
class employee(emp_id : Int = 100 , emp_name: String = "abc") {
	val id: Int
	var name: String

	// initializer block
	init {
		id = emp_id
		name = emp_name

		print("Employee id is: $id, ")
		println("Employee name: $name")
		println()
	}
}
```

**Output**

```
Employee id is: 18018, Employee name: Sagnik

Employee id is: 11011, Employee name: abc

Employee id is: 100, Employee name: abc
```

### Secondary Constructor

코틀린에선 다수의 secondary constructor를 가질 수 있다. secondary constructor는 변수의 초기화 및 클래스의 추가 로직을 구현할 수 있다. 이 생성자들은 `constructor` 키워드로 선언되어 있어야 한다.

#### Kotlin program of implementing secondary constructor

전달받은 파라미터에 따라 어떤 secondary constructor가 호출될지 결정된다. 

```kotlin
fun main(args: Array<String>) {
	employee(18018, "Sagnik")
	employee(11011,"Praveen",600000.5)
}
class employee {

	constructor (emp_id : Int, emp_name: String ) {
		var id: Int = emp_id
		var name: String = emp_name
		print("Employee id is: $id, ")
		println("Employee name: $name")
		println()
	}

	constructor (emp_id : Int, emp_name: String ,emp_salary : Double) {
		var id: Int = emp_id
		var name: String = emp_name
		var salary : Double = emp_salary
		print("Employee id is: $id, ")
		print("Employee name: $name, ")
		println("Employee name: $salary")
	}
}
```

#### Calling one secondary constructor from another

secondary constructor가 `this()` 함수를 통해 다른 secondary constructor를 호출할 수 있다. 

```kotlin
//main function
fun main(args: Array<String>)
{
	Add(5,6)
}
class Add {
	// calling another secondary using this
	constructor(a: Int,b:Int) : this(a,b,7) {
		var sumOfTwo = a + b
		println("The sum of two numbers 5 and 6 is: $sumOfTwo")
	}
	// this executes first
	constructor(a: Int, b: Int,c: Int) {
		var sumOfThree = a + b + c
		println("The sum of three numbers 5,6 and 7 is: $sumOfThree")
	}
}
```

#### Calling parent class secondary constructor from child class secondary constructor

`super` 키워드를 통해 부모의 secondary constructor를 호출할 수 있다. 

```kotlin
fun main(args: Array<String>) {
	Child(18018, "Sagnik")
}
open class Parent {
	constructor (emp_id: Int, emp_name: String, emp_salary: Double) {
		var id: Int = emp_id
		var name: String = emp_name
		var salary : Double = emp_salary
		println("Employee id is: $id")
		println("Employee name: $name")
		println("Employee salary: $salary")
		println()
	}
}
class Child : Parent {
	constructor (emp_id : Int, emp_name: String):super(emp_id,emp_name,500000.55){
		var id: Int = emp_id
		var name: String = emp_name
		println("Employee id is: $id")
		println("Employee name: $name")
	}
}
```

## Kotlin Visibility Modifiers

코틀린에서 visibility modifiers는 클래스, 객체, 인터페이스, 생성자, 함수, 속성과 setter으로의 접근을 특정 수준으로 제한하는데 사용된다. getter는 속성과 visibility가 동일하므로 getter의 visibility를 설정할 필요가 없다. 

코틀린에는 4가지 visibility modifiers가 있다.

|Modifier|Description|
|:---:|:---:|
|public|visible everywhere|
|private|visible inside the same class only|
|internal|visible inside the same module|
|protected|visible inside the same class and its subcalsses|

지정된 modifier가 없다면 기본적으로 public이다.

### public modifier

자바와는 다르게 코틀린에선 public으로 선언할 때 아무런 modifier도 필요하지 않다. 이것만 제외하면 자바와 동일하게 동작한다. 어떠한 패키지에서도 접근 가능하다.

### private modifier

코틀린에서 private modifier는 동일한 scope 내에서 선언된 코드만 접근할 수 있다. 

```kotlin
// class A is accessible from same source file
private class A {
	private val int = 10
	fun display()
	{
		println(int) // we can access int in the same class
		println("Accessing int successful")
	}
}
fun main(args: Array<String>){
	var a = A()
	a.display()
	println(a.int) // can not access 'int': it is private in class A
}
```

### protected modifier

protected modifier는 해당 클래스와 자식 클래스들에게서만 접근 가능하다. 

```kotlin
// base class
open class A {
	protected val int = 10 // protected variable
}
// derived class
class B: A() {
	fun getvalue(): Int {
		return int		 // accessed from the subclass
	}
}
fun main(args: Array<String>) {
	var a = B()
	println("The value of integer is: "+a.getvalue())
}
```

#### Overriding of protected modifier

변수나 함수를 `open` 키워드로 지정하면 파생된 클래스에서 `override` 키워드를 통해 override 할 수 있다. 

```kotlin
// base class
open class A {
	open protected val int = 10 // protected variable

}
// derived class
class B: A() {
override val int = 20
	fun getvalue():Int {
		return int		 // accessed from the subclass
	}
}
fun main(args: Array<String>) {
	var a = B()
	println("The overridden value of integer is: "+a.getvalue())
}
```

### internal modifier

internal modifier는 새로 추가된 modifier로써 자바에서 지원되지 않는다. internal modifier는 같은 모듈 내에만 접근이 가능한 것을 의미한다. 모듈은 컴파일 되는 파일들의 그룹이다.

```kotlin
internal class A {
}
public class B {
	internal val int = 10
	internal fun display() {
	}
}
```

### Constructor Visibility

기본적으로 생성자는 public이지만 modifier를 통해 visibility를 변경할 수 있다.

```kotlin
class A private constructor (name : String) {
      // other code
}
```

## Kotlin Inheritance

상속은 객체지향 프로그래밍의 기능 중 하나의 중요한 기능이다. 상속은 코드의 재사용성을 높여주며, base 클래스의 모든 기능을 파생 클래스로 상속할 수 있다. 또한 파생 클래스는 자신의 기능을 추가할 수 있다.

### Syntax of inheritance

코틀린에서 모든 클래스는 기본적으로 `final`이다. 파생 클래스가 base 클래스에서 상속되도록 하기 위해 base 클래스에서 `open` 키워드를 사용해야 한다.

```kotlin
open class baseClass (x:Int ) {
      ..........
}
class derivedClass(x:Int) : baseClass(x) {
     ...........
}
```

### Kotlin Inheriting property and methods from base class

클래스를 상속할 때 모든 속성과, 함수들이 상속된다. base 클래스의 변수와 함수를 파생 클래스에서 사용할 수 있으며 파생된 클래스 객체를 통해 base 클래스의 함수를 호출할 수 있다.

```kotlin
//base class
open class baseClass{
	val name = "GeeksforGeeks"
	fun A(){
		println("Base Class")
	}
}
//derived class
class derivedClass: baseClass() {
	fun B() {
		println(name)		 //inherit name property
		println("Derived class")
	}
}
fun main(args: Array<String>) {
	val derived = derivedClass()
	derived.A()		 // inherting the base class function
	derived.B()		 // calling derived class function
}
```

**Output**

```
Base Class
GeeksforGeeks
Derived class
```

### Use of Inheritance

base 클래스인 `Employee` 클래스가 있고, base 클래스를 상속받는 `webDeveloper`, `androidDeveloper`, `iOSDeveloper` 클래스를 구현해보자. 

```kotlin
//base class
open class Employee( name: String,age: Int,salary : Int) {
	init {
		println("My name is $name, $age years old and earning $salary per month. ")
	}
}
//derived class
class webDeveloper( name: String,age: Int,salary : Int): Employee(name, age,salary) {
	fun website() {
		println("I am website developer")
		println()
	}
}
//derived class
class androidDeveloper( name: String,age: Int,salary : Int): Employee(name, age,salary) {
	fun android() {
		println("I am android app developer")
		println()
	}
}
//derived class
class iosDeveloper( name: String,age: Int,salary : Int): Employee(name, age,salary) {
	fun iosapp() {
		println("I am iOS app developer")
		println()
	}
}
//main method
fun main(args: Array<String>) {
	val wd = webDeveloper("Gennady", 25, 10000)
	wd.website()
	val ad = androidDeveloper("Gaurav", 24,12000)
	ad.android()
	val iosd = iosDeveloper("Praveen", 26,15000)
	iosd.iosapp()
}
```

### Kotlin inheritance primary constructor

파생 클래스가 primary constructor를 가지고 있다면, 파생된 클래스의 파라미터를 사용해 base 클래스의 생성자를 초기화시켜줄 필요가 있다. 아래의 코드는 base 클래스의 primary constructor는 2개의 파라미터를 가지고 있으며, 파생 클래스는 3개의 파라미터를 가지고 있다. 파생된 클래스인 `CEO`의 생성자에선 `Employee` 클래스에 `name`과 `age`를 전달한다. `Employee` 클래스에서 `init` 블록을 수행한 후 `CEO`의 `init` 블록으로 돌아오게 된다. 

```kotlin
//base class
open class Employee(name: String,age: Int) {
	init{
		println("Name of the Employee is $name")
		println("Age of the Employee is $age")
	}
}
// derived class
class CEO( name: String, age: Int, salary: Double): Employee(name,age) {
	init {
		println("Salary per annum is $salary crore rupees")
	}
}
fun main(args: Array<String>) {
	CEO("Sunder Pichai", 42, 450.00)
}
```

**Output**

```
Name of the Employee is Sunder Pichai
Age of the Employee is 42
Salary per annum is 450.0 crore rupees
```

### Kotlin inheritance secondary constructor

`super` 키워드를 사용해 파생된 클래스에서 secondary constructor를 호출할 수 있다. 

```kotlin
//base class
open class Employee {
	constructor(name: String,age: Int){
			println("Name of the Employee is $name")
			println("Age of the Employee is $age")
	}
}
// derived class
class CEO : Employee{
	constructor( name: String,age: Int, salary: Double): super(name,age) {
		println("Salary per annum is $salary million dollars")
	}
}
fun main(args: Array<String>) {
	CEO("Satya Nadela", 48, 250.00)
}
```

### Overriding Member functions and properties

동일한 이름의 멤버 함수를 base 클래스와 파생 클래스가 가지고 있다면, `open` 키워드로 base 클래스의 멤버 함수를 표시하고, `override` 키워드를 이용해 파생 클래스의 base 멤버 함수를 재정의 할 수 있다. 속성도 동일하게 override 할 수 있다.

#### Kotlin program of overriding the member function

```kotlin
// base class
open class Animal {
   open var name: String = "Dog"
	open fun run() {
		println("Animals can run")
	}
}
// derived class
class Tiger: Animal() {
   override var name = "Tiger"
	override fun run() {	 // overrides the run method of base class
		println("Tiger can run very fast")
	}
}
fun main(args: Array<String>) {
	val t = Tiger()
	t.run()
}
```

### Calling the superclass implementation

`super` 키워드를 이용해 base 클래스의 멤버 함수나 속성을 호출할 수 있다. 

```kotlin
// base class
open class Phone() {
	var color = "Rose Gold"
	fun displayCompany(name:String) {
		println("Company is: $name")
	}
}
// derived class
class iphone: Phone() {
	fun displayColor(){
	
		// calling the base class property color
		println("Color is: "+super.color)
		
		// calling the base class member function
		super.displayCompany("Apple")
	}
}
fun main(args: Array<String>) {
	val p = iphone()
	p.displayColor()
}
```

## Kotlin Interfaces

인터페이스는 코틀린이 제공하는 직접 인스턴스화 할 수 없는 커스텀 타입이다. 대신, 구현 타입이 따라야 하는 동작의 형태를 정의한다.

### Creating Interfaces

코틀린의 인터페이스 정의는 `interface` 키워드 다음에 인터페이스 이름을 붙이고, 이어 인터페이스 멤버가 있는 중괄호가 있다. 차이점은 인터페이스의 멤버들 자신의 정의를 가지고 있지 않는 것이다. 

```kotlin
interface Vehicle()
{
  fun start()
  fun stop()
}
```

### Implementing Interfaces

인터페이스는 클래스나 객체에 의해 구현될 수 있다. 인터페이스를 구현할 때 일치하는 타입의 모든 멤버에 대한 정의를 제공해야 한다. 인터페이스를 구현하기 위해 커스텀 타입의 이름 뒤에 `:`과 구현할 인터페이스 이름을 선언한다.

```kotlin
class Car: Vehicle
```

#### Example to demonstrate an interface in Kotlin

인터페이스에서 `start()`와 `stop()`을 선언했다. `Car` 클래스는 인터페이스를 구현하고 2개의 메서드를 override 했다. `main()` 함수에서 객체를 생성한 후 구현한 2개의 메서드를 호출한다.

```kotlin
interface Vehicle {
	fun start()
	fun stop()
}

class Car : Vehicle {
	override fun start()
	{
		println("Car started")
	}

	override fun stop()
	{
		println("Car stopped")
	}
}

fun main()
{
	val obj = Car()
	obj.start()
	obj.stop()
}
```

**Output**

```
Car started
Car stopped
```

### Default values and Default Methods

인터페이스의 메서드는 디폴트 값을 파라미터로 지정할 수 있다. 함수가 호출되었을 때 파라미터가 제공되지 않으면 디폴트 값이 사용된다. 또한 메서드도 디폴트로 구현을 가질 수도 있다.

```kotlin
interface FirstInterface {
	fun add(a: Int, b: Int = 5)
	fun print()
	{
		println("This is a default method defined in the interface")
	}
}
class InterfaceDemo : FirstInterface {
	override fun add(a: Int, b: Int)
	{
		val x = a + b
		println("Sum is $x")
	}

	override fun print()
	{
      // super 키워드를 사용해 디폴트 구현부 호출
		super.print()
		println("It has been overridden")
	}
}

fun main()
{
	val obj = InterfaceDemo()
	println(obj.add(5))
	obj.print()
}
```

**Output**

```
Sum is 10
This is a default method defined in the interface
It has been overridden
```

### Properties in interface

메서드와 같이, 인터페이스에 속성을 포함할 수 있다. 그러나 인터페이스는 상태를 가지고 있지 않아 인스턴스화 될 수 없으며, 그 값들을 가지고 있을 backing field가 없다. 따라서, 인터페이스의 필드들은 추상적으로 유지되거나 구현해주어야 한다. 

#### Example to demonstrate interface properties

```kotlin
interface InterfaceProperties {
	val a : Int
	val b : String
		get() = "Hello"
}

class PropertiesDemo : InterfaceProperties {
	override val a : Int = 5000
	override val b : String = "Property Overridden"
}

fun main()
{
	val x = PropertiesDemo()
	println(x.a)
	println(x.b)
}
```

**Output**

```
5000
Property Overridden
```

### Inheritance in Interfaces

코틀린의 인터페이스는 다른 인터페이스를 상속할 수 있다. 다른 인터페이스를 상속할 때, 자신의 속성과 메서드를 추가할 수 있으며, 구현하려면 두 인터페이스의 모든 속성 및 메서드에 대해 구현해주어야 한다.

#### Example to demonstrate interface inheritance

```kotlin
interface Dimensions {
	val length : Double
	val breadth : Double
}

interface CalculateParameters : Dimensions {
	fun area()
	fun perimeter()
}

class XYZ : CalculateParameters {
	override val length : Double
		get() = 10.0
	override val breadth : Double
		get()= 15.0

	override fun area()
	{
		println("Area is ${length * breadth}")
	}

	override fun perimeter()
	{
		println("Perimeter is ${2*(length+breadth)}")
	}
}

fun main()
{
	val obj = XYZ()
	obj.area()
	obj.perimeter()
}
```

**Output**

```
Area is 150.0
Perimeter is 50.0
```

### Multiple Interface Implementation

코틀린에서 클래스는 단일 상속의 개념을 따르므로, 클래스는 하나의 클래스만 상속할 수 있지만, 인터페이스의 경우 다중 상속을 지원한다. 클래스는 모든 멤버에 대한 정의를 제공하는 경우, 둘 이상의 인터페이스를 구현할 수 있다.

#### Example to demonstrate multiple interface implementation 

```kotlin
interface InterfaceProperties {
	val a : Int
	val b : String
		get() = "Hello"
}

interface InterfaceMethods {
	fun description()
}
// InterfaceProperties, InterfaceMethods 인터페이스가 정의되었고 MultipleInterface에서 모두 구현되었다.
class MultipleInterface : InterfaceProperties, InterfaceMethods {
	override val a : Int
		get() = 50

	override fun description()
	{
		println("Multiple Interfaces implemented")
	}
}
fun main()
{
	val obj = MultipleInterface()
	obj.description()
}
```

**Output**

```
Multiple Interfaces implemented
```

## References
- [OOPs Concept](https://www.geeksforgeeks.org/kotlin-programming-language/?ref=ghm)
