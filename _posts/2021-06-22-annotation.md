---
title: Annotation
author: Beomsu Lee
category: [Development]
tags: [annotation]
---

Annotation이란 자바 소스 코드에 추가할 수 있는 메타 데이터의 한 형태이다. JEEE5(Java Platform, Enterprise Edition 5)부터 새롭게 추가된 요소다. Annotation으로 인해 데이터의 유효성 검사 등을 쉽게 알 수 있고, 관련된 코드가 깔끔해지게 된다. Annotation의 용도는 다양하지만 메타 데이터의 비중이 가장 크다. Annotation은 클래스, 인터페이스, 메서드, 변수, 매개 변수 등에 추가할 수 있다. 

## Annotation Process

Annotation Process는 Annotation에 대한 코드베이스를 검사, 수정 또는 생성하는데 사용된다. Annotation을 잘 사용한다면 코드를 단순화할 수 있다.

## Advantages

1. 빠르다. javac 컴파일러의 일부로 컴파일타임에 발생하기 때문이다.
1. 리플렉션을 사용하지 않는다. 자바의 리플렉션은 런타임에 많은 예외를 발생시키며 비용이 큰데, Annotation Processor는 리플렉션 없이 프로그램의 의미 구조를 알 수 있게 해준다.
1. Boilerplate code를 생성해주어 반복되는 코드로부터 벗어날 수 있다.

## How Annotation Processor works?

1. 자바 컴파일러가 컴파일 수행
1. 실행되지 않는 Annotation Processor들을 수행
1. 프로세서 내부에서 Annotation이 달린 요소(변수, 메서드, 클래스 등)들에 대한 처리
1. 컴파일러가 모든 Annotation Processor가 실행되었는지 확인하고, 그렇지 않다면 위 작업 반복 수행

## Annotation Types

`@Override`는 선언한 메서드가 오버라이드 되었다는 것을 의미한다.

```java
public class MyParentClass {
    public void justaMethod() {
        System.out.println("Parent class method");
    }
}

public class MyChildClass extends MyParentClass {
    @Override
    public void justaMethod() {
        System.out.println("Child class method");
    }
}
```
`@Deprecated`는 해당 메서드가 더 이상 사용되지 않음을 의미힌다.

```java

/**
 * @deprecated
 * reason for why it was deprecated
 */
@Deprecated
public void anyMethodHere(){
    // Do something
}
```
`@SuppressWarnings`는 선언한 곳의 컴파일 경고를 무시한다. 

```java
@SuppressWarnings("deprecation")
    void myMethod() {
        myObject.deprecatedMethod();
}
```

이외에도 다양한 유형의 어노테이션이 존재한다.

## Custom Annotation Implementation

Annotation은 @ 기호로 시작하는 인터페이스이다. 다음 예제를 보자.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@interface MethodInfo {
    String author() default "Igor Brishkoski";
    int revision() default 1;
    String comments() default "";
}
```

`@Target`은 Annotation이 사용되어질 요소(Element)를 지정한다. 지정할 수 있는 Element의 타입은 다음과 같다.

```java
ElementType.METHOD
ElementType.PACKAGE
ElementType.PARAMETER
ElementType.TYPE
ElementType.ANNOTATION_TYPE
ElementType.CONSTRUCTOR
ElementType.LOCAL_VARIABLE
ElementType.FIELD
```

`@Retention`은 컴파일러에게 언제 필요한지를 알려준다. 

- RetentionPolicy.RUNTIME : 컴파일 이후에도 JVM에 의해 참조 가능
- RetentionPolicy.CLASS : 컴파일러가 클래스를 참조할 때까지 유효
- RetentionPolicy.SOURCE : Annotation 정보는 컴파일 이후 없어짐

`awesomeMethod()`를 다음과 같이 작성하고 해당 메서드를 호출하면 런타임에 값들을 설정하게 된다.

```java
@MethodInfo(author = "John Snow", revision = 2, comments = "Hey!")
public void awesomeMethod() {   
    Method method = getClass().getMethod("awesomeMethod");
    MethodInfo methodInfo = method.getAnnotation(MethodInfo.class);

    Log.d("MethodInfo", methodInfo.author());
    Log.d("MethodInfo", methodInfo.revision());
    Log.d("MethodInfo", methodInfo.comments());
}
```

### References
- [Annotation이란 ?](https://www.charlezz.com/?p=1167)
- [Custom Annotations in Android](https://engineering.wework.com/custom-annotations-in-android-af43514f2f1b)
