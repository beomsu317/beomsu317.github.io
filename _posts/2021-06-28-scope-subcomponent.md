---
title: Scope / Subcomponent
author: Beomsu Lee
category: [Android, Dagger]
tags: [dagger]
math: true
mermaid: true
---

## Scope

Dagger2는 Scope를 지원한다. Component 별 `@Scope` 어노테이션으로 주입되는 객체들을 관리할 수 있다. 생성된 객체의 Lifecycle 범위입니다. 안드로이드는 주로 PerActivity, PerFragment 등으로 하면의 생명주기와 맞춰서 사용한다.

`@Singleton`과 비슷하게 객체의 단일 인스턴스를 유지하지만, `@Singleton`과 다른 점은 구성요소의 Lifecycle과 관련이 있다는 것이 차이점이다. 다음은 Scope의 특징이다.

1. type에 `@Scope` 어노테이션을 붙일 때 같은 Scope가 붙은 Components에 의해서만 사용이 가능
1. Components에 `@Scope` 어노테이션을 붙이면 Scope 어노테이션이 없는 type이나 동일한 Scope 어노테이션을 붙인 타입만 제공함
1. Subcomponent는 부모 Component들에서 사용중인 어노테이션을 사용할 수 없음

## Example

`CafeApp`을 통해 Scope가 어떻게 사용되는지 알아보자. `CafeApp`은 `CafeInfo`, `CoffeeMaker`로 구성되어 있다.

- `CafeInfo` : 카페이름을 가지고 있는 클래스
- `CoffeeMaker` : `Heater` 객체로 구성되어 있고, `CoffeeBean`을 받아 커피를 내릴 수 있는 클래스


```kotlin
class CafeInfo(private val name: String = "") {
    fun welcome() { Log.d("Dagger", "Welcome ${name}")}
}
```

```kotlin
class CoffeeMaker @Inject constructor(private var heater: Heater) {

    fun brew(coffeeBean: CoffeeBean) {
        Log.d("Dagger", "CoffeeBean(${coffeeBean}) [_}P coffee ! [_}P ")
    }
}
```

```kotlin
class CoffeeBean {
    var name = Log.d("Dagger", "CoffeeBean")
}
```

Component

```kotlin
@Component(modules = [CafeModule::class])
interface CafeComponent {

    fun cafeInfo() : CafeInfo

    fun coffeeMaker() : CoffeeMaker
}
```

Module

```kotlin
@Module
class CafeModule {
    @Provides
    fun provideCafeInfo(): CafeInfo {
        return CafeInfo()
    }

    @Provides
    fun provideCoffeeMaker(heater: Heater): CoffeeMaker {
        return CoffeeMaker(heater)
    }

    fun provideHeater() : Heater {
        return A_Heater()
    }
}
```

기본 구조를 생성하였다. 다음 조건에 맞춰 `CafeApp`의 구성을 변경한다.

1. `CafeInfo`는 하나뿐이며, 같은 결과를 반환해야 한다. 카페가 망하지 전까지 `CafeInfo`는 동일하다.
1. 카페가 망하여 `CafeMaker`도 없어진다. 카페가 망하지 않아도 `CafeMaker`는 새로 만들거나 교체할 수 있다.
1. `CafeMaker` 생성 시 필요한 `Heater`는 같은 `CoffeeMaker`에 항상 같은 `Heater`가 들어간다.

Subcomponent와 Scope를 이용해 객체들을 관리할 수 있다.

조건 1번에 의해 `CafeInfo`는 Singleton으로 구현해야 한다. Component에 Scope 어노테이션을 사용하면 해당 Component에 Binding 되는 객체들은 해당 Component와 같은 Lifecycle을 갖게 된다.

```kotlin
@Singleton // Scope 설정
@Component(modules = [CafeModule::class]) // CafeModule에 Component와 동일 Scope 사용 시 같은 Lifecycle을 가진다.
interface CafeComponent {
    // Module의 동일한 반환 type의 메서드와 바인딩
    fun cafeInfo() : CafeInfo	
    fun coffeeMaker() : CoffeeMaker 
}
```

```kotlin
@Module
class CafeModule {
    // Singleton을 설정한다. 연결된 Component와 동일한 Lifecycle을 갖게 된다.
    @Singleton
    @Provides
    fun provideCafeInfo(): CafeInfo {
        return CafeInfo()
    }

    @Provides
    fun provideCoffeeMaker(heater: Heater): CoffeeMaker {
        return CoffeeMaker(heater)
    }

    @Provides
    fun provideHeater() : Heater {
        return A_Heater()
    }
}
```

Component에 `@Singleton` 어노테이션을 선언하고, Module의 `CafeInfo`를 제공하는 메서드에 `@Singleton` 어노테이션을 선언하면, Singleton으로 구현된 `CafeInfo` 객체가 주입된다. 하지만 `@Singleton`이 없는 `CafeMaker`를 호출하면 매번 다른 객체를 주입한다.

```kotlin
var cafeComponent = DaggerCafeComponent.create()

// 동일한 객체 주입됨
var cafeInfo1 :CafeInfo = cafeComponent.cafeInfo()
var cafeInfo2 :CafeInfo = cafeComponent.cafeInfo()

// 다른 객체 주입됨
var coffeeMaker1 : CoffeeMaker = cafeComponent.coffeeMaker()
var coffeeMaker2 : CoffeeMaker = cafeComponent.coffeeMaker()
```

### Custom Scope

Dagger는 Custom Scope를 생성할 수 있다. Siblings Component들도 재사용할 수 있도록 `@ActivityScope`, `@FragmentScope` 등 Lifecycle에 의존적으로 이름을 짓는 것을 권장한다. 

kotlin

```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class CoffeeScope {}
```

java

```java
@Scope
@Retention(AnnotationRetention.RUNTIME)
public @interface [커스텀 Scope이름] {}
```


## Subcomponent

Component는 계층관계를 만들 수 있다. Subcomponent는 Dagger의 컨셉인 그래프를 형성한다. Inject로 주입을 요청받으면 Subcomponent에서 먼저 의존성을 검색하고, 없으면 부모로 올라가면서 검색한다.

Subcomponent는 부모 Component를 갖고 있는 Component이며, `@Subcomponent`에서 Builder Interface를 정의해야 부모 Component에서 코드가 생성된다. 

Dagger는 Component 생성 시 builder를 사용한다. `@Subcomponent`는 `@Component` 클래스 안에서 코드가 생성될 때 `@Subcomponent.Builder` 어노테이션이 선언된 인터페이스가 없으면 생성되지 않는다. 따라서 부모 Component에 `@Subcomponent.Builder`를 정의해 주어야 Subcomponent 구현이 가능하다.

```kotlin
@CoffeeScope    // CoffeeMaker와 Heater의 범위를 맞추기위해 Scope 설정
@Subcomponent(modules = [CoffeeModule::class])
interface Coffeecomponent {

    fun coffeeMaker() : CoffeeMaker
    fun coffeeBean() : CoffeeBean

    @Subcomponent.Builder
    interface Builder {
        fun build() : Coffeecomponent
    }
}
```

부모 Component의 Module을 통해 Component와 Subcomponent를 연결한다. 부모 Component에 설정된 모듈인 `CafeModule`으 `@Module`의 속성으로 부모 Component를 선언해 연결할 수 있다.

```kotlin
// 부모-자식 Component 관계 설정
@Module(Subcomponents = [Coffeecomponent::class])	
class CafeModule {
    // Singleton 설정 
    @Singleton      
    @Provides
    fun provideCafeInfo(): CafeInfo {
        return CafeInfo()
    }
}
```

부모 Component에 설정된 모듈인 `CafeModule`에 Subcomponent 관계를 설정하였다. 기존 `CafeModule`에 있던 `CoffeeMaker`, `Heater` 객체를 주입하는 Provider 메서드는 삭제한다. (Subcomponent에서 제공하기 때문)

이제 이 `CafeModule`을 가지는 Component가 부모가 되고, `CoffeeComponent`는 자식 Component가 된다. `CoffeeComponent`와 `Heater`, `CoffeeMaker`는 같은 범위를 갖게 된다.

```kotlin
@Module
class CoffeeModule {
    @CoffeeScope    // CoffeeMaker와 Heater의 범위를 같게 하기위해 Scope 설정
    @Provides
    fun provideCoffeeMaker(heater: Heater) : CoffeeMaker {
        return CoffeeMaker(heater)
    }

    @CoffeeScope    // CoffeeMaker와 Heater의 범위를 같게 하기위해 Scope 설정
    @Provides
    fun provideHeater() : Heater {
        return A_Heater()
    }

    @Provides       // CoffeeBean은 커피를 만들 때마다 소모되기 때문에 Scope 설정 X
    fun provideCoffeeBean() : CoffeeBean {
        return CoffeeBean()
    }
}
```

부모인 `CafeComponent`에서 자식 `CoffeeComponent`를 호출할 수 있도록 메서드를 정의한다.

```kotlin
@Singleton
@Component(modules = [CafeModule::class])
interface CafeComponent {

    fun cafeInfo() : CafeInfo

    // 자식 Component의 Builder를 반환하는 메서드
    fun coffeecomponent() : Coffeecomponent.Builder
}
```

커스텀 Scope가 잘 적용되었는지 확인해보자.

```kotlin
// CafeInfo의 SignleTon 테스트
var cafeComponent: CafeComponent = DaggerCafeComponent.create()
var cafeInfo1: CafeInfo = cafeComponent.cafeInfo()
var cafeInfo2: CafeInfo = cafeComponent.cafeInfo()
Log.d(TAG, "SingleTon scope CafeInfo is euqal : ${cafeInfo1.equals(cafeInfo2)}")

// CoffeeMaker의 CoffeeScope 테스트
var coffeeComponent1: Coffeecomponent = cafeComponent.coffeecomponent().build()
var coffeeComponent2: Coffeecomponent = cafeComponent.coffeecomponent().build()
// 동일한 CoffeComponent로 CoffeeMaker 의존성 주입
var coffeeMaker1: CoffeeMaker = coffeeComponent1.coffeeMaker()
var coffeeMaker2: CoffeeMaker = coffeeComponent1.coffeeMaker()
Log.d(TAG, "CoffeeScope / same component coffeeMaker is equal : ${coffeeMaker1.equals(coffeeMaker2)}")

// 서로 다른 CoffeComponent로 CoffeeMaker 의존성 주입
var coffeeMaker3: CoffeeMaker = coffeeComponent2.coffeeMaker()
Log.d(TAG,"CoffeeScope / different component coffeeMaker is equal : ${coffeeMaker1.equals(coffeeMaker3)}")

// Non-Scope, CoffeeScope 설정하지 않은 CoffeeBean 테스트
var coffeeBean1: CoffeeBean = coffeeComponent1.coffeeBean()
var coffeeBean2: CoffeeBean = coffeeComponent1.coffeeBean()
Log.d(TAG,"Non-Scoped coffeeBean is equal : ${coffeeBean1.equals(coffeeBean2)}")
```

다음은 출력 결과이다.

```kotlin
// CafeInfo는 @Singleton Scope 설정을 하였기 때문에 모두 같은 객체
SingleTon scope CafeInfo is euqal : true

// @CoffeeScope로 인해 동일한 CoffeeComponent로 생성 시 같은 객체를 리턴하므로 True
CoffeeScope / same component coffeeMaker is equal : true

// @CoffeeScope로 인해 CoffeeComponent와 1:1매칭, 서로다른 CoffeeComponent이기 때문에 False
CoffeeScope / different component coffeeMaker is equal : false

// Scope를 설정하지 않았기 때문에 매번 새로 생성하므로 False
Non-Scoped coffeeBean is equal : false
```

`CoffeeComponent`와 Provider 메서드에 같은 `@CoffeeScope`를 설정하므로, `CoffeeComponent` 당 한 개의 `CoffeeMaker`만 존재한다.

## @Component.Builder / @Subcomponent.Builder

Dagger는 생성 시 Builder Pattern을 사용한다. `@Component`의 경우 코드가 생성되기 때문에 builder 역시 생성된다. 

그런데 `@Subcomponent`는 부모 Component의 클래스 안에서 코드가 생성될 때 `@SubComopnent.Builder`가 붙은 interface가 없으면 Subcomponent의 builder를 자동 생성하지 않는다. 따라서 `@Subcomponent.Builder`가 선언된 인터페이스를 Subcomponent에 정의해주어야 한다.

Builder는 빌드하기 전 Module을 파라미터로 넣을 수 있다. 이 방법은 필드를 갖고 있는 Module이 있는 경우 유용하게 사용할 수 있다.

```kotlin
@Module(subcomponents = [Coffeecomponent::class])
class CafeModule(private var name: String? = null) {	// 멤버변수 name 추가

    @Singleton
    @Provides
    fun provideCafeInfo(): CafeInfo {
        if (name == null || name!!.isEmpty()) {
            return CafeInfo()
        }
        return CafeInfo(name!!)
    }
}
```

`CafeModule`은 생성자에서 `name` 필드를 파라미터로 받고 `CafeInfo` 객체 생성에 사용하게 된다. `CafeComponent`에서 `Component.Builder`를 정의한다.

```kotlin
@Singleton
@Component(modules = [CafeModule::class])
interface CafeComponent {
    fun cafeInfo() : CafeInfo
    fun coffeecomponent() : Coffeecomponent.Builder

    @Component.Builder
    interface Builder {
        fun cafeModoule(cafeModule: CafeModule) : Builder
        fun build() : CafeComponent
    }
}
```

이제 Component를 build 하기 전 CafeModule을 먼저 적용할 수 있다. `CafeComponent`를 빌드하기 전 먼저 `name`을 적용한 `CafeModule`을 미리 바인드 할 수 있고, 이를 통해 카페이름이 설정된 `CafeInfo` 객체를 제공받을 수 있다.

```kotlin
var cafeComponent: CafeComponent = DaggerCafeComponent.builder()
    .cafeModoule(CafeModule("CAFFEE"))
    .build()
Log.d(TAG, cafeComponent.cafeInfo().welcome())
```

### References
- [Scope](https://jaejong.tistory.com/131?category=873925#%EC%BB%A4%EC%8A%A4%ED%85%80Scope%EC%84%A0%EC%96%B8%EB%B0%A9%EB%B2%95)