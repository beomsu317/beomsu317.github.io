---
title: Context Injection
author: Beomsu Lee
category: [Android, Dagger]
tags: [dagger]
math: true
mermaid: true
---

## Context Injection

`context` 객체는 직접 생성할 수 있는 것이 아닌, 안드로이드 시스템에서 만들어주는 객체이기 때문에 클래스에서 `context`를 사용하기 위해선 파라미터를 통해 전달받아야 한다.

이 `context`를 Dagger2 그래프에 주입하는 방법으로 3가지로 나눠서 보자.

1. 생성자 인자가 있는 Module
1. @Component.Builder
1. @Component.Factory

### 생성자 인자가 있는 Module

이 방법은 단순히 생성자 인자를 Module에 전달하는 방법이다. `AppModule` 생성자를 보면 `context` 파라미터가 존재한다.

```kotlin
@Module
class AppModule(val context: Context) {
    // 의존성 주입 메서드인 `provideContext()`는 `AppModule`의 속성인 `context`를 반환
    @Provides
    fun provideContext() : Context = context
}
```

`AppComponent.Builder`를 통해 `appModule`을 파라미터로 받아 초기화할 수 있다. `appModule`을 초기화하고 `build()` 메서드로 Component 인스턴스를 반환받는다.
```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    ...

    @Component.Builder
    interface Builder {
        fun appModule(appModule: AppModule) : Builder
        
        fun build() : AppComponent
    }
}
```

```kotlin
DaggerAppComponent.builder()
    .appModule(AppModule(this))
    .build()
```

이러한 방식은 Module 생성자를 통해 간단하지만, Module을 추상화할 수 없다는 단점이 있다. 

### @Component.Builder

Dagger2.12에 생성자에 인자를 전달하여 1번 방법과 동일한 작업을 수행하기 위해 `@Component.Builder`와 `@BindsInstance` 2가지의 주석이 추가되었고, Module에 초기화하지 않는다. `@BindsInstance`는 인스턴스를 구성요소에 바인딩한다. 이 작업을 통해 Dagger 그래프에 `context`가 추가되고, 어디에서나 Dagger를 통해 `context`를 얻을 수 있다. `@BindsInstance` 어노테이션으로 AppComponent가 `context` 요소로 갖게 되고, 이 Component에 설정된 Module에서 `context`를 자유롭게 사용할 수 있다.

```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    ...

    @Component.Builder
    interface Builder {

        @BindsInstance
        fun application(context: Context): Builder
        
        fun build(): AppComponent
    }
}
```

`TestClass`에 `context` 파라미터가 필요한 경우 `AppComponent`에 설정된 `AppModule`에서 `context`를 다음과 같이 사용할 수 있다.

```kotlin
@Module
class AppModule {

    @Provides
    fun provideTestClass(context: Context): TestClass = TestClass(context)
}
```

#### Builder.interface

1. Builder에는 Component 또는 Component의 super 타입을 리턴하는 메서드가 하나 이상 있어야 한다. (여기선 `build()` 메서드)
1. 인스턴스를 바인딩하는데 사용되는 `build()` 메서드 이외의 메서드는 `Builder`를 리턴해야 한다. (여기선 `application()` 메서드로 리턴 타입이 Builder)
1. 종속성 바인딩에 사용되는 메서드에는 2개 이상의 매개변수가 없어야 한다. 더 많은 종속성을 바인딩하려면 각 종속성마다 다른 메서드를 추가로 생성해줘야 한다. ()

다음은 DaggerComponent를 생성하는 방법이다. Builder 메서드인 `application()`의 파라미터로 `@BindInstance` 어노테이션이 붙은 `context`에 전달해주면, 어디서나 `context`를 참조할 수 있게 된다.

```kotlin
DaggerAppComponent
    .builder()
    .application(this)
    .build()
```

생성자의 인자를 전달할 필요가 없으므로 Module은 상태를 저장하지 않도록 구현할 수 있고, 모든 정적 메서드를 포함할 수 있다. 하지만 Instance를 Component 요소에 바인딩하려면 긴 메서드 체인을 만들어야 한다.

`context`, `age`, `name`의 종속성을 바인딩하려 한다.

```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    ...

    @Component.Builder
    interface Builder {
        
        // context 종속성 바인딩 함수
        @BindsInstance
        fun application(context: Context): Builder
        
        // age 종속성 바인딩 함수
        @BindsInstance
        fun age(age: Int): Builder
        
        // name 종속성 바인딩 함수
        @BindsInstance
        fun name(name: String): Builder

        fun build(): AppComponent
    }
}
```

이렇게 종속성 바인딩 할 개수만큼 메서드가 늘어나고, 반환 타입을 `Builder`로 설정해서 메서드 체이닝을 구현해야 한다. `application()` 메서드로 `context`만 Component 요소에 바인딩 할 때보다 2개의 메서드가 추가되었다. 이렇게 Builder를 반환함으로써 메서드 체이닝 구현으로 Component 인스턴스 생성 시 코드가 길어지게 된다.

```kotlin
DaggerAppComponent
    .builder()
    .application(this)
    .age(20)
    .name("홍길동")
    .build()
```

### @Component.Factory

Dagger 2.22에서 `@Component.Builder`의 문제점을 해결하기 위해 `@Component.Factory`를 추가하였다. Builder와 다른점은 각 매개변수에 `@BindInstance` 어노테이션을 붙이면서 Component 요소에 바인딩을 `create()` 메서드 하나로 구현할 수 있다.

```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    ...

    @Component.Factory
    interface Factory {
        // @BindInstance를 매개변수에 사용
        fun create(@BindsInstance context: Context) : AppComponent
    }
}
```

`create()` 메서드 하나로 `context`를 Component 요소에 바인딩하고 Component 인스턴스를 반환하는 것이 가능하다. Builder와 다르게 메서드 체이닝을 구현하지 않아도 Component에 `@BindInstance`가 달린 요소를 등록할 수 있다.

```kotlin
DaggerAppComponent
    .factory()
    .create(this)
```

1. Factory는 둘 이상의 `create()` 메서드를 선언할 수 없다. 
1. `create()` 메서드는 Component 또는 super 인스턴스를 반환해야 한다.

Component에 3개의 요소(`context`, `age`, `name`)를 바인딩 해보자.

```kotlin
Component(modules = [AppModule::class])
interface AppComponent {
    ...

    @Component.Factory
    interface Factory {
    
        fun create(
            @BindsInstance context: Context,
            @BindsInstance age: Int,
            @BindsInstance name: String
        ): AppComponent
    }
}
```

Factory는 `create()` 메서드 하나에 바인딩 할 요소를 매개변수로 추가해주면 된다. Builder는 각 요소들을 바인딩하기 위해 메서드 체이닝으로 긴 체인이 발생했는데, Factroy는 `create()` 메서드 하나로 모두 바인딩이 가능하다.

```kotlin
DaggerAppComponent
    .factory()
    .create(this, 22, "홍길동")
```

### References
- [context 주입방법 @BindsInstance @Component.Builder @Component.Factory](https://jaejong.tistory.com/144)

