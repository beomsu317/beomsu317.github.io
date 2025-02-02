---
title: "Strategy Pattern"
date: "2025-02-02"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

전략 패턴은 문제 해결 방법(알고리즘)을 캡슐화하여 클라이언트 코드와 분리함으로써, 알고리즘의 교체를 동적으로 수행할 수 있게 해준다.

## Motivation

정렬 알고리즘을 사용하는 프로그램이 있다고 하자. 이 프로그램은 여러 가지 정렬 알고리즘(예: 버블 정렬, 퀵 정렬)을 지원해야 한다. 사용자는 상황에 따라 정렬 알고리즘을 선택할 수 있어야 한다고 하자.

이때 전략 패턴을 사용하면 클라이언트 코드는 정렬 방식에 의존하지 않으며 전략(정렬 알고리즘)을 동적으로 교체할 수 있다.

## Applicability

- 행동들이 조금씩 다를 뿐 개념적으로 관련된 많은 클래스들이 존재할 때
- 알고리즘의 변형이 필요할 때
- 사용자가 몰라야 하는 데이터를 사용하는 알고리즘이 있을 때
- 하나의 클래스가 많은 행동을 정의하고, 이런 행동들이 그 클래스 연산 안에서 복잡한 다중 조건문의 모습을 취할 때

## Structure

![strategy pattern structure](images/strategy_pattern_structure.png)

- `Strategy`: 제공하는 모든 알고리즘에 대한 공통의 연산들을 인터페이스로 정의한다.
- `ConcreteStrategy`: `Strategy` 인터페이스를 실제 알고리즘으로 구현한다.
- `Context`: `Strategy` 객체에 대한 참조자를 관리하고, 실제 `Strategy` 서브클래스의 인스턴스를 갖고 있음으로써 구체화된다. 또한 `Strategy` 객체가 자료에 접근하는 데 필요한 인터페이스를 제공한다.

## Collaborations

- 사용자는 `ConcreteStrategy` 객체를 생성하여 `Context`에 전달한다.
- 동일 계열의 여러 `ConcreteStrategy` 클래스가 준비되어 있는 경우, 사용자는 상황이나 필요에 따라 원하는 전략을 선택하고, 그 전략을 `Context`에 설정한다.
- `Context`가 `ConcreteStrategy`에 설정되면, `Context`는 클라이언트의 요청을 해당 전략에 전달해 작업을 처리한다.

## Consequences

1. **동일 계열의 관련 알고리즘군이 생긴다.**
2. **서브클래싱을 사용하지 않는 대안이다.**

    `Context` 클래스를 직접 상속해 행동을 구현하는 방법은 간단할 수 있지만, `Context`와 알고리즘이 혼합되어 코드가 복잡해지고, 수정과 확장이 어렵다.

    전략 패턴을 사용해 알고리즘을 별도 클래스로 독립시켜 `Context`와 분리할 수 있으므로, 알고리즘을 쉽게 변경, 이해 및 확장할 수 있으며, 전체 시스템의 유연성과 유지보수성이 크게 향상된다.
3. **조건문을 없앨 수 있다.**

    다음은 전략 패턴을 사용하기 전 코드이다.

    ```cpp
    void Composition::Repair() {
        switch (_breakingStrategy) {
            case SimpleStrategy:
                ComposeWithSimpleCompositor();
                break;
            case TeXStrategy:
                ComposeWithTeXCompositor();
                break;
            // ...
        }
        // merge results with existing composition, if necessary
    }
    ```

    전략 패턴을 사용하면 `case` 문을 없앨 수 있다.

    ```cpp
    void Composition::Repair() {
        _compositor->Compose();
        // merge results with existing composition, if necessary
    }
    ```
4. **구현의 선택이 가능하다.**

    동일한 행동에 대해 서로 다른 구현을 제공할 수 있다.

5. **사용자는 서로 다른 전략을 알아야 한다.**

    사용자는 전략을 선택하기 전 전략들이 어떻게 다른지 이해해야 한다. 즉, 사용자는 구현 내용을 모두 알아야 한다.
6. **`Strategy` 객체와 `Context` 객체 사이 의사소통 오버헤드가 있다.**

    `ConcreteStrategy` 클래스는 `Strategy` 인터페이스를 공유한다. 따라서 어떤 `ConcreteStrategy` 클래스는 이 인터페이스를 통해 들어온 모든 정보를 다 사용하지 않는데도 이 정보를 가져야 할 때도 있다. 
7. **객체 수가 증가한다.**

## Implementation

1. **`Strategy` 및 `Context` 인터페이스를 정의한다.**

    전략 패턴 구현 시 `Strategy` 및 `Context` 사이 데이터 교환 방식은 유연성과 결합도의 균형에 따라 선택된다.

    - 매개변수로 전달하는 방식: 결합도를 낮추면서도, 필요 시 `Strategy`가 충분한 정보를 활용할 수 있다.
    - `Context` 자체 또는 참조를 전달하는 방식: `Strategy`가 필요한 정보를 직접 요청할 수 있으므로 유연하지만, 결합도가 높아질 수 있다.

    어느 쪽을 선택하든 `Context`는 데이터에 접근할 수 있는 정교한 인터페이스를 제공해야 하며, `Strategy` 객체는 그 인터페이스를 통해 필요한 정보를 정확히 요청할 수 있어야 한다.

2. **전략을 템플릿 매개변수로 사용한다.**

    C++의 템플릿을 통해 전략을 가진 클래스를 구성할 수 있다. 이 기법은 두 가지 조건이 만족되어야 적용할 수 있다.

    1. `Strategy` 객체를 컴파일 타임에 결정
    2. `Strategy` 객체가 런타임에 바꿀 필요가 없을 때

    이 조건이 만족한다면 구성할 클래스(`Context`)를 템플릿 클래스로 정의하고, `Strategy` 클래스를 이 템플릿의 매개변수로 정의한다. 이 템플릿을 이용하면 `Strategy` 인터페이스를 정의하는 추상 클래스를 정의할 필요가 없어진다. 

    ```cpp
    template <class AStrategy> 
    class Context {
        void Operation() {
            theStrategy.DoAlgorithm();
        }
        // ...
    private:
        AStrategy theStrategy;
    };
    ``` 

    이렇게 되면 `Context` 클래스는 인스턴스화 시점에 `Strategy` 클래스에서 구성된다.

    ```cpp
    class MyStrategy {
    public:
        void DoAlgorithm();
    };

    Context<MyStrategy> aContext;
    ```
3. **`Strategy` 객체에 선택성을 부여한다.**

    `Context` 객체는 필요한 경우에만 `Strategy` 객체를 사용하고, 그렇지 않다면 `Context` 내부에 미리 정의된 기본 행동(default behavior)을 수행하도록 할 수 있다.

## Sample Code

`Composition` 클래스는 문서 내 포함된 텍스트와 그래픽 컴포넌트를 관리하고, 이를 한 줄로 배열하는 작업을 수행하기 위해 `Compositor` 객체(전략 객체)를 이용한다. 각 컴포넌트는 자신과 연관된 실제 크게, 신축성(stretchability)와 수축성(shrinkability)를 가지고 있다. 

`Composition` 객체는 값을 `Compositor` 객체에 보내며, `Compositor` 객체는 이 값을 사용해 줄 분리에 가장 좋은 위치를 결정한다.

```cpp
class Composition {
public:
    Composition(Compositor*);
    void Repair();
private:
    Compositor* _compositor;
    Component* _components;     // the list of components
    int _componentCount;        // the number of components
    int _lineWidth;             // the Composition's line width
    int* _lineBreaks;           // the position of linebreaks
                                // in components
    int _lineCount;             // the number of lines
};
```

새로운 레이아웃이 필요할 때 `Composition` 클래스는 `Compositor`에게 라인을 어디서 분리해야 하는지 요청한다. 이때, `Compositor` 클래스의 `Compose()` 메서드는 필요한 모든 정보를 매개변수로 받아 처리한 후, 계산된 줄 분리자의 개수를 반환한다.

`Compositor` 클래스의 인터페이스는 필요한 정보를 매개변수로 전달한다.

```cpp
class Compositor {
public:
    virtual int Compose(Coord natural[], 
                        Coord stretch[], 
                        Coord shrink[], 
                        int componentCount,
                        int lineWidth, 
                        int breaks[]) = 0;
protected:
    Compositor();
};
```

`Compositor`의 구체 서브클래스는 특별한 줄 분리 전략을 정의한다.

`Repair()` 연산은 `Composition` 클래스에서 문서의 레이아웃을 다시 계산하는 역할을 한다. 이 과정에서 `Compositor` 객체를 이용해 줄을 어디서 분리할지 결정하고, 그 결과를 이용해 문서의 컴포넌트들을 다시 배치한다.

```cpp
void Composition::Repair() {
    Coord* natural;
    Coord* stretchability;
    Coord* shrinkability;
    int componentCount;
    int* breaks;

    // prepare the arrays with the desired component sizes
    // ...

    // determine where the breaks are:
    int breakCount;
    breakCount = _compositor->Compose(
        natural, 
        stretchability, 
        shrinkability,
        componentCount, 
        _lineWidth, 
        breaks
    );

    // lay out components according to breaks
    // ...
}
```

`SimpleCompositor` 클래스는 `Compositor` 클래스를 상속받는 서브클래스로, 가장 단순한 방식으로 줄을 나누는 알고리즘을 구현한다.  

```cpp
class SimpleCompositor : public Compositor {
public:
    SimpleCompositor();
    virtual int Compose(
        Coord natural[], 
        Coord stretch[], 
        Coord shrink[],
        int componentCount, 
        int lineWidth, 
        int breaks[]
    );
    // ...
};
```

`TeXCompositor`는 TeX의 정교한 조판 시스템을 모방해 문단 단위로 텍스트를 정렬한다.

```cpp
class TeXCompositor : public Compositor {
public:
    TeXCompositor();
    virtual int Compose(
        Coord natural[], 
        Coord stretch[], 
        Coord shrink[],
        int componentCount, 
        int lineWidth, 
        int breaks[]
    );
    // ...
};
```

`ArrayCompositor`는 일정한 간격으로 컴포넌트를 나누어 배치한다.

```cpp
class ArrayCompositor : public Compositor {
public:
    ArrayCompositor(int interval);
    virtual int Compose(
        Coord natural[], 
        Coord stretch[], 
        Coord shrink[],
        int componentCount, 
        int lineWidth, 
        int breaks[]
    );
    // ...
};
```

이 클래스들은 `Compose()` 연산이 넘겨받은 정보를 다 사용하지 않는다. 

마지막으로 `Composition` 클래스의 인스턴스를 만들려면, 필요한 `Compositor` 인스턴스를 넘겨주어야 한다.

```cpp
Composition* quick = new Composition(new SimpleCompositor);
Composition* slick - new Composition(new TeXCompositor);
Composition* iconic = new Composition(new ArrayCompositor(100));
```