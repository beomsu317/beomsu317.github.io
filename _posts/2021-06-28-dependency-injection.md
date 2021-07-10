---
title: Dependency Injection
author: Beomsu Lee
category: [Android, Dagger]
tags: [dagger]
math: true
mermaid: true
---

## Dependency Injection

DI(Dependency Injection)이란 프로그래밍 구성요소 간 의존 관계가 아닌 외부를 통해 정의하게 되는 디자인 패턴 중 하나이다. 즉, 외부에서 의존 객체를 생성하여 넘겨주는 것을 의미한다. 예를 들어, A Class가 B Class를 의존할 때 B Object를 A가 생성하지 않고 외부에서 생성해 넘겨주는 것이다. 

DI를 위해 객체를 생성하고 넘겨주는 것이 DI Framework이다. Dagger에서는 Component와 Module이라 한다. DI는 이렇게 의존성이 있는 객체의 제어를 외부로 넘김으로써 IoC(Inversion of Control) 개념을 구현한다. 


## Advantage

1. 의존성 파라미터를 생성자에 작성하지 않아도 되므로 보일러 플레이트 코드를 줄일 수 있다.
1. Interface에 구현체를 쉽게 교체하면서 상황에 따라 적절한 행동을 정의할 수 있다.
1. 리팩토링이 수월하다.
1. 유닛 테스트를 쉽게 수행할 수 있다.

## Example 

Dagger의 CoffeeMaker 예제를 통해 DI의 개념을 알아보자. 

### Heater 

`Heater` 인터페이스를 구현한다. 

```kotlin
interface Heater {

    fun on()
    fun off()

    fun isHot() : Boolean
}
```

해당 인터페이스의 구현체를 구현한다. `on()` 메서드를 호출하면 열을 가하고 `off()` 메서드를 호출하면 열을 가하는 것을 중지한다.

```kotlin
class A_Heater : Heater {
    private var heating : Boolean = false

    override fun on() {
        heating = true
        Log.d("coffeMaker", "A_Heater : ~~~ heating ~~~")
    }

    override fun off() {
        heating = false
        Log.d("coffeMaker", "A_Heater : ~~~ heat Stop ~~~")
    }

    override fun isHot(): Boolean { return heating }
}
```

### Pump
Coffee를 내리는데 필요한 압력을 가하는 인터페이스를 구현한다.

```kotlin
interface Pump {
    fun pump()
}
```

생성자로 `Heater`를 전달하고 히터가 작동중일 때 압력을 가한다.

```kotlin
class A_Pump(private val heater: Heater) : Pump {
    override fun pump() {
        if (heater.isHot()) {
            Log.d("coffeMaker", "A_Pump -> -> pumping -> ->")
        }
    }
}
```


### CoffeeMaker 

`Heater`와 `Pump` 구현체로 구성된 `CoffeeMaker` 클래스이다. `brew()` 메서드를 호출하면 커피를 내린다.

```kotlin
class CoffeeMaker(
    private val heater: Heater,
    private val pump: Pump) 
{
    fun brew() {
        heater.on()
        pump.pump()
        Log.d("coffeMaker", "[_]P coffee! [_]P")
        heater.off()
    }
}
```

위와 같은 구조일 때 일반적인 경우와 DI를 사용했을 때의 예시를 보자. 먼저 DI를 사용하지 않았을 때의 예제이다. `Heater`와 `Pump`를 각각 생성한 후 `CoffeeMaker`에 전달하여 `brew()` 메서드를 호출한다. 이렇게 구현할 경우 `A_Heater`와 `A_Pump`를 생성한 후 `CoffeeMaker`에 넘겨줘야 하기 때문에 보일러 플레이트 코드가 많이 생성되게 된다.

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        var heater: Heater = A_Heater()	
        var pump: Pump = A_Pump(heater)	
        var coffeemaker: CoffeeMaker = CoffeeMaker(heater, pump)
        coffeemaker.brew()
}
```

이번엔 DI를 활용한 예제를 보자. DI는 `CoffeeMaker`가 의존성을 모르는 상태에서도 커피를 내릴 수 있게 해준다. `Injection` 클래스는 DI의 역할을 한다.

```kotlin
class Injection {
    companion object {
        @JvmStatic
        fun provideHeater() : Heater { return A_Heater() }

        @JvmStatic
        fun providePump() : Pump { return A_Pump(provideHeater()) }

        @JvmStatic
        fun provideCoffeeMaker() : CoffeeMaker { return CoffeeMaker(provideHeater(), providePump()) }
    }
}
```

다음은 의존성을 주입하는 코드이다.

```kotlin
var coffeeMaker = CoffeeMaker(Injection.provideHeater(), Injection.providePump())
coffeeMaker.brew()
```
```kotlin
var coffeeMaker = Injection.provideCoffeeMaker()
coffeeMaker.brew()
```

`Injeciton`으로부터 `Heater`와 `Pump`를 제공받아 사용한다. 이로써 사용자는 `Heater`와 `Pump`를 제공받아 사용하기만 하면 된다. 

Heater의 종류를 `A_Heater`에서 `B_Heater`로 변경할 경우 `Injection` 클래스의 `Heater`를 리턴하는 로직만 변경하면 된다.

이런 디자인 패턴을 DI라 한다. 코드 간 커플링을 감소시키며, 재사용 및 유지보수를 용이하게 구현해준다. 

## References
- [DI (Dependency Injection) - 의존성 주입](https://jaejong.tistory.com/123?category=873925)