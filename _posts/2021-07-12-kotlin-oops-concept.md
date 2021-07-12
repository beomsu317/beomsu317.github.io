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

