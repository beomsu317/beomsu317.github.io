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
class ClassName {      // class header
   // property
   // member function
}
```

클래스의 생성자는 `constructor` 키워드를 사용해 만들 수 있다.

```kotlin
class ClassName constructor(parameters) {    
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
class Employee {
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
var obj = ClassName()
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
class Employee {// Constructor Declaration of Class

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
	var obj = Employee()
	// object 2 of class employee
	var obj2 = Employee()

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
class OuterClass {
	var str = "Outer class"
	// nested class declaration
	class NestedClass {
		val firstName = "Praveen"
		val lastName = "Ruhil"
	}
}
fun main(args: Array<String>) {
	// accessing member of Nested class
	print(OuterClass.NestedClass().firstName)
	print(" ")
	println(OuterClass.NestedClass().lastName)
}
```

**Output**

```
Praveen Ruhil
```

코틀린에서 중첩 클래스의 멤버 함수에 접근하기 위해 중첩 클래스의 객체를 만들고 그것을 이용해 멤버 함수를 호출한다.

```kotlin
// outer class declaration
class OuterClass {
	var str = "Outer class"
	// nested class declaration
	class NestedClass {
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
	val nested = OuterClass.NestedClass()
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
class OuterClass {
	var str = "Outer class"
	// innerClass declaration without using inner keyword
	class InnerClass {
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
	val inner= OuterClass().InnerClass()
	// inner function call using object
	println(inner.nestfunc())
}
```

`inner` 키워드를 사용해 inner 클래스를 정의하고, 내부 클래스를 사용하기 위해 외부 클래스의 인스턴스를 생성한다. 그럼 컴파일 타임에 에러가 발생하지 않고 정상적으로 실행되는 것을 확인할 수 있다.

```kotlin
// outer class declaration
class OuterClass {
	var str = "Outer class"
	// innerClass declaration with using inner keyword
	inner class InnerClass {
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
	val inner= OuterClass().InnerClass()
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
	val emp = Employee(18018, "Sagnik")
}
class Employee(emp_id : Int , emp_name: String) {
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
	val emp = Employee(18018, "Sagnik")
	// default value for emp_name will be used here
	val emp2 = Employee(11011)
	// default values for both parameters because no arguments passed
	val emp3 = Employee()

}
class Employee(emp_id : Int = 100 , emp_name: String = "abc") {
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
	Employee(18018, "Sagnik")
	Employee(11011,"Praveen",600000.5)
}
class Employee {

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
open class BaseClass (x:Int ) {
      ..........
}
class DerivedClass(x:Int) : BaseClass(x) {
     ...........
}
```

### Kotlin Inheriting property and methods from base class

클래스를 상속할 때 모든 속성과, 함수들이 상속된다. base 클래스의 변수와 함수를 파생 클래스에서 사용할 수 있으며 파생된 클래스 객체를 통해 base 클래스의 함수를 호출할 수 있다.

```kotlin
//base class
open class BaseClass{
	val name = "GeeksforGeeks"
	fun A(){
		println("Base Class")
	}
}
//derived class
class DerivedClass: BaseClass() {
	fun B() {
		println(name)		 //inherit name property
		println("Derived class")
	}
}
fun main(args: Array<String>) {
	val derived = DerivedClass()
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
class WebDeveloper( name: String,age: Int,salary : Int): Employee(name, age,salary) {
	fun website() {
		println("I am website developer")
		println()
	}
}
//derived class
class AndroidDeveloper( name: String,age: Int,salary : Int): Employee(name, age,salary) {
	fun android() {
		println("I am android app developer")
		println()
	}
}
//derived class
class IosDeveloper( name: String,age: Int,salary : Int): Employee(name, age,salary) {
	fun iosapp() {
		println("I am iOS app developer")
		println()
	}
}
//main method
fun main(args: Array<String>) {
	val wd = WebDeveloper("Gennady", 25, 10000)
	wd.website()
	val ad = AndroidDeveloper("Gaurav", 24,12000)
	ad.android()
	val iosd = IosDeveloper("Praveen", 26,15000)
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

## Kotlin Data Classes

보통 데이터를 저장하기 위해 클래스를 만든다. 코틀린에선 `data` 키워드를 통해 데이터 보관 목적으로 만든 클래스를 생성할 수 있다.

```kotlin
data class Student(val name: String, val roll_no: Int)
```

컴파일러는 자동으로 다음 함수를 구현한다.

- `equals()`
- `hashCode()`
- `toString()`
- `copy()`

### Rules to create Data classes

데이터 클래스를 사용하려면 다음의 요구사항을 충족시켜야 한다.

- 적어도 하나의 파라미터를 가진 primary constructor가 필요
- 모든 primary constructor 파라미터는 `val` 또는 `var`로 표시되어야  함
- 데이터 클래스는 `abstract`, `open`, `sealed`, `inner`를 붙일 수 없음
- 데이터 클래스는 상속받을 수 없음

### toString()

`toString()` 함수는 데이터 클래스에 정의된 모든 파라미터를 `String`을 형태로 반환한다. 컴파일러는 primary constructor에서 선언된 속성들만을 사용하기 때문에 클래스 바디에 선언된 속성들은 무시된다. 

```kotlin
fun main(args: Array<String>)
{
	//declaring a data class
	data class man(val roll: Int,val name: String,val height:Int){
		var age: Int = 0
	}

	//declaring a variable of the above data class
	//and initializing values to all parameters

	val man1=man(1,"man",50)
	man1.age = 20
	
	//printing all the details of the data class
	println(man1.toString());
}
```

**Output**
```
man(roll=1, name=man, height=50)
```

### copy()

가끔 객체를 복사해야하는 경우가 있으며, 객체의 속성 중 일부만 변경하고 싶을 때 `copy()` 함수를 사용한다.

#### Properties of copy()

- primary constructor에서 정의한 인자와 멤버들이 복사된다.
- 2개의 객체의 primary 파라미터는 동일하지만 클래스의 바디가 다를 수 있다.

```kotlin
fun main(args: Array<String>)
{
	//declaring a data class
	data class man(val name: String, val age: Int)
	{
		//property declared in class body
		var height: Int = 0;
	}
	
	val man1 = man("manish",18)

	//copying details of man1 with change in name of man
	val man2 = man1.copy(name="rahul")

	//copying all details of man1 to man3
	val man3 = man1.copy();

	//declaring heights of individual men
	man1.height=100
	man2.height=90
	man3.height=110

	//man1 & man3 have different class body values,
	//but same parameter values

	//printing info all 3 men
	println("${man1} has ${man1.height} cm height")
	println("${man2} has ${man2.height} cm height")
	println("${man3} has ${man3.height} cm height")

}
```

**Output**

```
man(name=manish, age=18) has 100 cm height
man(name=rahul, age=18) has 90 cm height
man(name=manish, age=18) has 110 cm height
```

### hashCode() and equals()

`hashCode()` 함수는 객체의 hash code 값을 반환한다.

`equals()` 메서드는 두 개의 객체가 동일한지 여부를 반환하는데, `Float`와 `Double` 값에 대해서 다르게 작동한다.

#### Declaration of hashCode()

```kotlin
open fun hashCode(): Int
```

#### Properties of hashCode()
- 동일한 객체에 대해 두 번 선언된 해시 코드는 동일
- `equals()` 메서드를 통해 두 객체가 동일하다면, 해시 코드도 동일

```kotlin
fun main(args: Array<String>)
{
	//declaring a data class
	data class man(val name: String, val age: Int)
	
	val man1 = man("manish",18)
	val man2 = man1.copy(name="rahul")
	val man3 = man1.copy();

	val hash1=man1.hashCode();
	val hash2=man2.hashCode();
	val hash3=man3.hashCode();

	println(hash1)
	println(hash2)
	println(hash3)

	//checking equality of these hash codes
	println("hash1 == hash 2 ${hash1.equals(hash2)}")
	println("hash2 == hash 3 ${hash2.equals(hash3)}")
	println("hash1 == hash 3 ${hash1.equals(hash3)}")
}
```

`man1`과 `man3`는 동일한 객체이기 때문에 `equals()`의 결과와 `hashCode()`에 대한 결과가 같다.

```
835510190
-938448478
835510190
hash1 == hash 2 false
hash2 == hash 3 false
hash1 == hash 3 true
```

## Kotlin Sealed Classes

코틀린은 sealed 클래스로 알려진 클래스를 제공한다. 자바에서 제공되지 않는 타입이며, sealed 클래스는 super 클래스를 상속받는 child 클래스의 종류를 제한하는 특성을 가지고 있다. sealed 클래스는 런타임이 아니라 컴파일 타임에 일치하는 유형을 제한하여 타입의 안전을 보장한다.

### Declaration of sealed class

sealed 클래스를 정의하기 위해 `sealed` 키워드로 클래스 modifier를 선언해주면 된다. sealed 클래스는 또 하나의 특별한 기능을 가지고 있는데, 이 클래스의 생성자들은 기본적으로 `private`이다.

```kotlin
sealed class Demo
```

sealed 클래스는 암시적으로 `abstract`이기 때문에 인스턴스화 될 수 없다.

### Kotlin program of sealed class

```kotlin
sealed class Demo {
	class A : Demo() {
		fun display()
		{
			println("Subclass A of sealed class Demo")
		}
	}
	class B : Demo() {
		fun display()
		{
			println("Subclass B of sealed class Demo")
		}
	}
}
fun main()
{
	val obj = Demo.B()
	obj.display()

	val obj1 = Demo.A()
	obj1.display()
}
```

**Output**
```
Subclass B of sealed class Demo
Subclass A of sealed class Demo
```

sealed 클래스의 모든 서브클래스는 동일한 코틀린 파일 내에 정의되어야 한다. 단, sealed 클래스 내에 정의할 필요는 없으며, sealed 클래스가 보이는 모든 범위에서 정의할 수 있다.

```kotlin
// A sealed class with a single subclass defined inside
sealed class ABC {
 class X: ABC(){...}
}

// Another subclass of the sealed class defined
class Y: ABC() {
  class Z: ABC()   // This will cause an error. Sealed class is not visible here
}
```

### Sealed class with when

sealed 클래스는 거의 `when`과 함께 사용된다. `when`은 모든 케이스에 대해 처리되어야 하며 `else` 구문이 필요하지만 sealed 클래스를 사용하면 컴파일 시점에 하위 클래스들이 정해져있어 `else` 없이 구현할 수 있다.

#### Example to demonstrate sealed classes with a when clause

```kotlin
// A sealed class with a string property
sealed class Fruit
	(val x: String)
{
	// Two subclasses of sealed class defined within
	class Apple : Fruit("Apple")
	class Mango : Fruit("Mango")
}

// A subclass defined outside the sealed class
class Pomegranate: Fruit("Pomegranate")

// A function to take in an object of type Fruit
// And to display an appropriate message depending on the type of Fruit
fun display(fruit: Fruit){
	when(fruit)
	{
		is Fruit.Apple -> println("${fruit.x} is good for iron")
		is Fruit.Mango -> println("${fruit.x} is delicious")
		is Pomegranate -> println("${fruit.x} is good for vitamin d")
	}
}
fun main()
{
	// Objects of different subclasses created
	val obj = Fruit.Apple()
	val obj1 = Fruit.Mango()
	val obj2 = Pomegranate()

	// Function called with different objects
	display(obj)
	display(obj1)
	display(obj2)
}
```
**Output**

```
Apple is good for iron
Mango is delicious
Pomegranate is good for vitamin d
```

## Kotlin Abstract class

코틀린에서 abstract 클래스는 `abstract` 키워드를 사용해 선언된다. abstract 클래스는 인스턴스화 될 수 없으며 이는 객체를 만들 수 없다는 의미이다. 

### Abstract class declaration

```kotlin
abstract class className {
    .........
}
```

### Points to remember 

1. abstract 클래스로 객체를 생성할 수 없다.
1. abstract 클래스의 모든 변수(속성)와 멤버 함수는 기본적으로 non-abstract이다. 따라서 이것들을 child 클래스에서 override 하려면 `open` 키워드를 사용해야 한다.
1. 멤버 함수를 `abstract`로 선언했다면, `open`이 기본값이기 때문에 `open` 키워드를 사용할 필요가 없다.
1. abstract 멤버 함수가 바디를 가지고 있지 않으며, 파생 클래스에서 구현되어야 한다.

```kotlin
abstract class className(val x: String) {   // Non-Abstract Property
         
    abstract var y: Int      // Abstract Property

    abstract fun method1()   // Abstract Methods

    fun method2() {          // Non-Abstract Method
        println("Non abstract function")
    }
}
```

#### Kotlin program of using both abstract and non-abstract members in an abstract class

```kotlin
//abstract class
abstract class Employee(val name: String,val experience: Int) { // Non-Abstract
																// Property
	// Abstract Property (Must be overridden by Subclasses)
	abstract var salary: Double
	
	// Abstract Methods (Must be implemented by Subclasses)
	abstract fun dateOfBirth(date:String)

	// Non-Abstract Method
	fun employeeDetails() {
		println("Name of the employee: $name")
		println("Experience in years: $experience")
		println("Annual Salary: $salary")
	}
}
// derived class
class Engineer(name: String,experience: Int) : Employee(name,experience) {
	override var salary = 500000.00
	override fun dateOfBirth(date:String){
		println("Date of Birth is: $date")
	}
}
fun main(args: Array<String>) {
	val eng = Engineer("Praveen",2)
	eng.employeeDetails()
	eng.dateOfBirth("02 December 1994")
}
```

**Output**

```
Name of the employee: Praveen
Experience in years: 2
Annual Salary: 500000.0
Date of Birth is: 02 December 1994
```

### Overriding a non-abstract open member with an abstract one

코틀린에선 `open` 클래스의 non-abstract `open` 멤버 함수를 `override` 키워드를 이용해 abstract 클래스에서 override 할 수 있다.

```kotlin
open class Livingthings {
	open fun breathe() {
		println("All living things breathe")
	}
}
abstract class Animal : Livingthings() {
	override abstract fun breathe()
}
class Dog: Animal(){
	override fun breathe() {
		println("Dog can also breathe")
	}
}
fun main(args: Array<String>){
	val lt = Livingthings()
	lt.breathe()
	val d = Dog()
	d.breathe()
}
```

**Output**
```
All living things breathe
Dog can also breathe
```

### Multiple derived classes

abstract 클래스의 abstract 멤버는 파생 클래스에서 override 될 수 있다. 

```kotlin
// abstract class
abstract class Calculator {
	abstract fun cal(x: Int, y: Int) : Int
}
// addition of two numbers
class Add : Calculator() {
	override fun cal(x: Int, y: Int): Int {
		return x + y
	}
}
// subtraction of two numbers
class Sub : Calculator() {
	override fun cal(x: Int, y: Int): Int {
		return x - y
	}
}
// multiplication of two numbers
class Mul : Calculator() {
	override fun cal(x: Int, y: Int): Int {
		return x * y
	}
}
fun main(args: Array<String>) {
	var add: Calculator = Add()
	var x1 = add.cal(4, 6)
	println("Addition of two numbers $x1")
	var sub: Calculator = Sub()
	var x2 = sub.cal(10,6)
	println("Subtraction of two numbers $x2")
	var mul: Calculator = Mul()
	var x3 = mul.cal(20,6)
	println("Multiplication of two numbers $x3")
}
```

**Output**
```
Addition of two numbers 10
Subtraction of two numbers 4
Multiplication of two numbers 120
Division of two numbers 3
```

## Enum Classes in Kotlin

프로그래밍할 때 특정한 값만 가지는 유형이 필요할 때가 있다. 이를 만족시키기 위해 등장한 것이 Enum 클래스이다. 

다른 프로그래밍 언어들처럼, 코틀린에서도 `enum`은  고유의 타입을 가지고 있다.

### Some important points about enum classes in kotlin

- enum 상수는 단순한 상수 집합이 아니다. 상수에는 속성, 메서드 등이 있다.
- 각 enum 상수는 클래스의 개별 인스턴스 역할을 하며 `,`로 구분된다.
- enum은 상수에 미리 정의된 이름을 할당해 가독성을 높인다.
- enum 클래스의 인스턴스는 생성자를 사용해 생성할 수 없다.

enum은 `enum` 키워드를 이용해 선언할 수 있다.

```kotlin
enum class DAYS{
  SUNDAY,
  MONDAY,
  TUESDAY,
  WEDNESDAY,
  THURSDAY,
  FRIDAY,
  SATURDAY
}
```

### Initializing enums 

코틀린에서 enum은 자바의 enum과 같이 생성자를 가질 수 있다. enum 상수는 enum 클래스의 인스턴스이므로 primary constructor에 값을 전달해 상수를 초기화 할 수 있다.

```kotlin
enum class Cards(val color: String) {
    Diamond("black"),
    Heart("red"),
}
```

우리는 쉽게 `card`의 `color`에 접근할 수 있다.

```kotlin
val color = Cards.Diamond.color
```

### Enums properties and methods

자바나 다른 프로그래밍 언어와 같이, 코틀린 enum 클래스는 사용할 수 있는 몇 가지의 내장된 속성과 함수를 가지고 있다.

#### Properties

- ordinal : 이 속성은 상수의 순서 값(일반적으로 0 기반 index)을 저장
- name : 이 속성은 상수의 이름을 저장

#### Methods 

- values : 이 메서드는 enum 클래스에 정의된 모든 상수에 목록을 반환
- valueOf : 이 메서드는 입력 문자열과 일치하는 enum 상수를 반환

```kotlin
enum class DAYS {
	SUNDAY,
	MONDAY,
	TUESDAY,
	WEDNESDAY,
	THURSDAY,
	FRIDAY,
	SATURDAY
}
fun main()
{
	// A simple demonstration of properties and methods
	for (day in DAYS.values()) {
		println("${day.ordinal} = ${day.name}")
	}
	println("${DAYS.valueOf(" WEDNESDAY ")}")
}
```

**Output**
```
0 = SUNDAY
1 = MONDAY
2 = TUESDAY
3 = WEDNESDAY
4 = THURSDAY
5 = FRIDAY
6 = SATURDAY
WEDNESDAY
```

### Enum class properties and functions 

코틀린에선 enum 클래스를 정의할 수 있다. 이 클래스의 타입은 자신만의 속성과 함수들을 가질 수 있다. 속성은 기본 값으로 지정할 수 있지만, 제공되지 않는 경우 각 상수는 속성에 대한 자체적인 값을 정의한다. 함수의 경우 특정 클래스의 인스턴스에 의존하지 않도록 보통 companion object 안에 정의된다. 하지만 companion object 없이도 정의될 수 있다.

```kotlin
// A property with default value provided
enum class DAYS(val isWeekend: Boolean = false){
	SUNDAY(true),
	MONDAY,
	TUESDAY,
	WEDNESDAY,
	THURSDAY,
	FRIDAY,
	// Default value overridden
	SATURDAY(true);

	companion object{
		fun today(obj: DAYS): Boolean {
			return obj.name.compareTo("SATURDAY") == 0 || obj.name.compareTo("SUNDAY") == 0
		}
	}
}

fun main(){
	// A simple demonstration of properties and methods
	for(day in DAYS.values()) {
		println("${day.ordinal} = ${day.name} and is weekend ${day.isWeekend}")
	}
	val today = DAYS.MONDAY;
	println("Is today a weekend ${DAYS.today(today)}")
}
```

**Output**

```
0 = SUNDAY and is weekend true
1 = MONDAY and is weekend false
2 = TUESDAY and is weekend false
3 = WEDNESDAY and is weekend false
4 = THURSDAY and is weekend false
5 = FRIDAY and is weekend false
6 = SATURDAY and is weekend true
Is today a weekend false
```

### Enums as Anonymous Classes

enum 상수는 클래스의 abstract 함수를 재정의하는 것과 함께 자체 함수를 구현함으로써 익명 클래스처럼 동작한다. 중요한 점은 각 enum 상수는 재정의 되어야 한다는 것이다.

```kotlin
// defining enum class
enum class Seasons(var weather: String) {
	Summer("hot"){
		// compile time error if not override the function foo()
		override fun foo() {			
			println("Hot days of a year")
		}
	},
	Winter("cold"){
		override fun foo() {
			println("Cold days of a year")
		}
	},
	Rainy("moderate"){
		override fun foo() {
			println("Rainy days of a year")
		}
	};
	abstract fun foo()
}
// main function
fun main(args: Array<String>) {
	// calling foo() function override be Summer constant
	Seasons.Summer.foo()
}
```

**Output**

```
Hot days of a year
```

### Usage of when expression with enum class

코틀린에서 enum을 사용함으로써 얻는 장점은 `when`과 함께 사용되었을 때이다. enum 클래스는 취할 수 있는 값을 제한하기 때문에 모든 상수에 대한 정의와 함께 사용될 경우 다른 `else`가 필요하지 않다. `else`를 사용하면 컴파일러가 경고를 발생시킬 수 있다.

```kotlin
enum class DAYS{
	SUNDAY,
	MONDAY,
	TUESDAY,
	WEDNESDAY,
	THURSDAY,
	FRIDAY,
	SATURDAY;
}

fun main(){
	when(DAYS.SUNDAY){
		DAYS.SUNDAY -> println("Today is Sunday")
		DAYS.MONDAY -> println("Today is Monday")
		DAYS.TUESDAY -> println("Today is Tuesday")
		DAYS.WEDNESDAY -> println("Today is Wednesday")
		DAYS.THURSDAY -> println("Today is Thursday")
		DAYS.FRIDAY -> println("Today is Friday")
		DAYS.SATURDAY -> println("Today is Saturday")
		// Adding an else clause will generate a warning
	}
}
```

**Output**

```
Today is Sunday
```

## Kotlin extension function

코틀린은 프로그래머에게 기존 클래스를 상속하지 않고도 더 많은 기능을 추가할 수 있는 기능을 제공한다. 이 기능은 extension으로 알려진 기능을 통해 구현된다. 기존 클래스에 함수가 추가될 때 이를 Extension Funcion이라 한다.

클래스에 extension 함수를 추가하려면, 다음과 같이 클래스 이름을 통해 추가할 새로운 함수를 정의한다.

```kotlin
// A sample class to demonstrate extension functions
class Circle (val radius: Double){

	// member function of class
	fun area(): Double{
		return Math.PI * radius * radius;
	}
}
fun main(){
	// Extension function created for a class Circle
	fun Circle.perimeter(): Double{
		return 2*Math.PI*radius;
	}

	// create object for class Circle
	val newCircle = Circle(2.5);

	// invoke member function
	println("Area of the circle is ${newCircle.area()}")

	//invoke extension function
	println("Perimeter of the circle is ${newCircle.perimeter()}")
}
```

**Output**
```
Area of the circle is 19.634954084936208
Perimeter of the circle is 15.707963267948966
```

### Extended library class using extension function 

코틀린은 유저가 정의한 클래스 말고도 라이브러리 클래스들도 확장할 수 있다. 위에서 extension 함수를 정의한 것과 같이 라이브러리도 유사하게 함수를 추가할 수 있다.

```kotlin
fun main(){

	// Extension function defined for Int type
	fun Int.abs() : Int{
		return if(this < 0) -this else this
	}

	println((-4).abs())
	println(4.abs())
}
```

### Extensions are resolved statically

한가지 중요한 점은 extenstion 함수는 정적으로 바인딩 된다는 것이다. 정적 바인딩은 컴파일 시간에 이루어지기 때문에 컴파일 이후로 값이 변경되지 않는다는 것이다.

클래스 `B`가 클래스 `A`를 상속받고 `display()` 함수에 전달되는 인자는 `B` 클래스이다. 동적 메서드였을 경우 25가 출력되어야 하지만 extension 함수는 정적 메서드이기 때문에 `A` 타입의 함수가 호출된다. 그래서 10이 출력되게 된다.

```kotlin
// Open class created to be inherited
open class A(val a:Int, val b:Int){
}

// Class B inherits A
class B():A(5, 5){}

fun main(){
	
	// Extension function operate defined for A
	fun A.operate():Int{
		return a+b
	}

	// Extension function operate defined for B
	fun B.operate():Int{
		return a*b;
	}

	// Function to display static dispatch
	fun display(a: A){
		print(a.operate())
	}

	// Calling display function
	display(B())
}
```

**Output**

```
10
```

### Nullable Reciever 

extension 함수는 클래스 타입이 nullable로도 정의될 수 있다. 이 경우 extension 함수 내부에서 null 검사를 추가하고 적절한 값을 반환한다.

```kotlin
// A sample class to display name 
class AB(val name: String){
	override fun toString(): String {
		return "Name is $name"
	}
}

fun main(){
	// An extension function as a nullable receiver
	fun AB?.output(){
		if(this == null){
			println("Null")
		}else{
			println(this.toString())
		}
	}

	val x = AB("Charchit")
	
	// Extension function called using an instance
	x.output()
	// Extension function called on null
	null.output()
}
```
**Output**

```
Name is Charchit
Null
```

### Companion Object Extensions

클래스가 companion object를 포함한다면, companion object에 대한 extension 함수와 속성을 정의할 수 있다.

```kotlin
class MyClass {
	companion object {
		// member function of companion object
		fun display(str :String) : String{
			return str
		}
	}
}
	// extension function of companion object
fun MyClass.Companion.abc(){
	println("Extension function of companion object")
}
fun main(args: Array<String>) {
	val ob = MyClass.display("Function declared in companion object")
	println(ob)
	// invoking the extension function
	val ob2 = MyClass.abc()
}
```

**Output**

```
Function declared in companion object
Extension function of companion object
```

## Kotlin generics

Generics는 다양한 데이터 타입을 사용해 접근할 수 있는 클래스, 메서드, 속성을 정의하는 동시에 컴파일 타임에 안전성을 유지하는 강력한 기능이다.

### Creating parameterized classes

제네릭 타입은 타입에 따라 파라미터로 구분되는 클래스나 메서드이다. 항상 `()`을 이용해 파라미터를 지정한다.

```kotlin
class MyClass<T>(text: T) {
    var name = text
}
```

`MyClass` 클래스의 인스턴스를 생성하기 위해 인자를 전달해야 한다. 

```kotlin
val my : MyClass<String> = Myclass<String>("GeeksforGeeks")
```

파라미터를 생성자의 인자로부터 추론할 수 있는 경우 인자의 타입을 생략할 수 있다. 인자로 `String` 타입을 전달해 컴파일러가 MyClass\<String\> 타입인 것을 알 수 있다.

```kotlin
val my = MyClass("GeeksforGeeks") 
```

### Advantages of generic

1. 타입 캐스팅을 피할 수 있다.
	- 객체의 타입 캐스트가 필요하지 않다.
1. 타입 안정성을 보장한다.
	- 제네릭은 한 번에 하나의 객체 타입만 허용한다.
1. 컴파일 타임 안정성을 보장한다.
	- 제네릭 코드는 컴파일 타임에 검사되므로 런타임 에러를 방지한다.


### Generic use in our program

제네릭 타입의 파라미터를 전달하면 어떤 타입이 전달되는 처리할 수 있게 된다.

#### Kotlin program using generic class

```kotlin
class Company<T> (text : T){
	var x = text
	init{
		println(x)
	}
}
fun main(args: Array<String>){
	var name: Company<String> = Company<String>("GeeksforGeeks")
	var rank: Company<Int> = Company<Int>(12)
}
```

**Output**

```
GeeksforGeeks
1234
```

### Variance 

Variance이란 파라미터 타입이 클래스 계층에 영향을 주는 것을 말한다. 만약 A 타입의 값이 필요한 모든 클래스에 B 타입을 넣어도 문제가 없을 경우 B는 A의 하위 타입이 된다. 

#### Invariance

`Double`은 `Number`를 상속하고, `Double`의 supertype은 `Number`이다. 하지만 `A\<Double\>`의 supertype은 `A\<Number\>`가 아니다. 두 타입이 서로 상속 관계이지만 제네릭 클래스의 상속 관계가 아니라는 것을 Invariance라 한다.

#### Covariance 

Covariance는 Invariance의 반대이다. `Number`가 `Double`의 supertype일 때 `A\<Number\>`가 `A\<Double\>`의 supertype이면 이를 Covariance라 한다.

코틀린에서 Generic의 모든 타입은 Invariance이다. 이것을 `out`과 `in` 키워드로 Covariance로 변경해 처리할 수 있다. 

1. 선언한 곳의 variance 
1. 사용되는 곳의 variance : Type projection

#### The out Keywords 

코틀린에선 제네릭 타입에 `out` 키워드를 사용할 수 있다. 즉, 이 참조를 모든 supertype에 할당할 수 있다. `out` 값은 지정된 클래스에 의해서만 생성될 수 있으며 소비될 수 없다. 

타입 `T`의 값을 생성할 수 있는 `OutClass` 클래스를 정의했다. 

```kotlin
class OutClass<out T>(val value: T) {
    fun get(): T {
        return value
    }
}
```

그런 다음 `OutClass` 클래스의 supertype인 reference에 인스턴스를 할당할 수 있다.

```kotlin
val out = OutClass("string")
val ref: OutClass<Any> = out   
```

### Contracovariance 

Contracovariance는 반대의 방향으로 공변성 조건을 만족하는 것을 말한다. 즉, `Number`가 `Double`의 supertype 일 때 `A\<Double\>`이 `A\<Number\>`의 supertype이라면 Contracovariance라 한다.

#### The in Keyword

subtype의 참조에 할당하려는 경우 제네릭 타입에 `in` 키워드를 사용할 수 있다. `in` 키워드는 소비되는 파라미터 타입에만 사용할 수 있으며, 생성되지 않는다.

선언된 `toString()` 메서드를 가지고 있으며 `T` 타입의 값만 소비하고 있다. 

```kotlin
class InClass<in T> {
    fun toString(value: T): String {
        return value.toString()
    }
}
```

그럼 해당 Number 타입의 reference를 subtype의 reference에 할당할 수 있다.

```kotlin
val inClassObject: InClass<Number> = InClass()
val ref<Int> = inClassObject
```

### Type projections

어떤 타입 배열의 모든 요소를 Any 타입으로 복사하려면 가능할 수 있지만, 컴파일러가 코드를 컴파일할 수 있도록 하려면 입력 파라미터에 `out` 키워드를 선언해주어야 한다. 이것은 컴파일러가 입력 파라미터가 Any 타입의 subtype이라고 추론할 수 있게 해준다.

#### Kotlin program of copying elements of one array into another

```kotlin
fun copy(from: Array<out Any>, to: Array<Any>) {
	assert(from.size == to.size)
	// copying (from) array to (to) array
	for (i in from.indices)
		to[i] = from[i]
	// printing elements of array in which copied
	for (i in to.indices) {
	println(to[i])
	}
}
fun main(args :Array<String>) {
	val ints: Array<Int> = arrayOf(1, 2, 3)
	val any :Array<Any> = Array<Any>(3) { "" }
	copy(ints, any)

}
```

**Output**

```
1
2
3
```

### Star projections

값의 특정 타입을 알지 못하고 배열의 모든 요소를 print 하는 경우 `*` projection을 사용한다.

```kotlin
// star projection in array
fun printArray(array: Array<*>) {
	array.forEach { print(it) }
}
fun main(args :Array<String>) {
	val name = arrayOf("Geeks","for","Geeks")
	printArray(name)
}
```

**Output**

```
GeeksforGeeks
```

## References
- [OOPs Concept](https://www.geeksforgeeks.org/kotlin-programming-language/?ref=ghm)
- [Kotlin - Sealed class 구현 방법 및 예제](https://codechacha.com/ko/kotlin-sealed-classes/)
- [Kotlin - Generics 클래스, 함수를 정의하는 방법](https://codechacha.com/ko/generics-class-function-in-kotlin/)