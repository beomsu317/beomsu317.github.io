---
title: "Decorator Pattern"
date: "2025-01-28"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "structural pattern"]
---

객체에 동적으로 새로운 책임을 추가할 수 있게 한다. 상속을 사용하지 않고도 객체의 기능을 확장할 수 있다.

## Motivation

어떤 기능을 추가하려면 기존 클래스를 계속 수정해야 하므로 OCP 원칙을 위반하게 된다. 즉, 새로운 기능을 추가할 때마다 새로운 클래스를 만들어야 한다. 

데코레이터 패턴을 적용하면 기능을 동적으로 추가할 수 있으며, 코드의 재사용과 확장성이 증가한다.

## Applicability

- 동적이며 투명하게, 즉 다른 객체에 영향을 주지 않고 개별의 객체에 새로운 책임을 추가해야 할 때
- 제거될 수 있는 책임일 때
- 실제 상속으로 서브클래스를 계속 만드는 방법이 실질적이지 못할 때

## Structure

![decorator pattern structure](images/decorator_pattern_structure.png)

- `Component`: 동적으로 추가할 기능을 가질 가능성들이 있는 객체에 대한 인터페이스
- `ConcreteComponent`: 추가적인 기능이 실제 정의되어야 할 필요가 있는 객체
- `Decorator`: `Component` 객체에 대한 참조자를 관리하면서 `Component`에 정의된 인터페이스를 만족하도록 인터페이스를 정의
- `ConcreteDecorator`: `Component`에 새롭게 추가할 기능을 실제로 구현하는 클래스

## Collaborations

- `Decorator`는 자신이 `Component` 객체 쪽으로 요청을 전달한다. 요청 전달 후 자신만의 추가 연산을 선택적으로 수행할 수도 있다.

## Consequences

1. **단순 상속보다 설계의 융통성을 더 많이 증대시킬 수 있다.**

    데코레이터 패턴을 사용하면 데코레이터 객체와 연결하거나 분리하는 작업을 통해 새로운 책임을 추가하거나 삭제하는 일이 런타임에 가능하다.
2. **클래스 계통의 상부측 클래스에 많은 기능이 누적되는 상황을 피할 수 있다.**

    데코레이터 패턴은 책임을 추가하는 작업에서 "필요한 비용만 그때 지불하는" 방법을 제공한다. 누락된 기능들 `Decorator` 객체를 통해 지속적으로 추가할 수 있다.
3. **데코레이터와 해당 데코레이터 컴포넌트가 동일한 것은 아니다.**

    기본 객체(`Component`)와 이를 감싸는 `Decorator`는 별개의 객체이다. 즉, 데코레이터는 원본 객체를 감싸서 새로운 기능을 추가할 뿐, 원본 객체 자체가 되는 것은 아니다. 데코레이터는 원본 객체의 껍데기 역할을 하면서 원본 객체와 동일한 인터페이스를 제공한다.
4. **데코레이터를 사용해 작은 규모의 객체들이 많이 생긴다.**

## Implementation

1. **인터페이스 일치시키기.**

    `Decorator`는 자신을 둘러싼 컴포넌트의 인터페이스를 만족해야 한다. 따라서 `ConcreteDecorator` 클래스는 동일한 부모 클래스를 상속해야 한다.
2. **추상 클래스로 정의되는 `Decorator` 클래스 생략하기.**

    `Decorator` 클래스에 정의할 책임이 한 가지인 경우 `Decorator` 클래스의 책임을 `ConcreteDecorator` 클래스와 합칠 수 있다.
3. **`Component` 클래스는 가볍게 유지하기.**

    `Component`와 `Decorator`는 같은 인터페이스를 가져야 하므로 `Decorator`는 `Component`를 상속해야 한다. 이때  `Component` 클래스를 가볍게 정의해야 하는데, 이 의미는 연산에 해당하는 인터페이스만 정의하고 무언가 저장할 수 있는 변수는 저장하지 말아야 한다는 뜻이다. `Component` 클래스가 복잡해지면 `Component`를 상속받는 여러 `Decorator`들도 복잡하고 무거운 클래스가 된다.
4. **객체의 겉을 변경(데코레이터 패턴)할 것인가, 속을 변경(전략 패턴)할 것인가.**

    `Component` 클래스가 본질적으로 복잡하고 무거운 특성을 갖는다면, 전략 패턴이 더 나은 해결방안이다. 전략 패턴에서는 `Strategy` 객체의 대체를 통해 컴포넌트의 기능을 변경하거나 확장하는 방법을 제공한다.

## Sample Code

`VisualComponent` 컴포넌트 클래스가 있다고 하자.

```cpp
class VisualComponent {
public:
    VisualComponent();
    virtual void Draw();
    virtual void Resize();
    // ...
};
```

`VisualComponent`의 서브클래스로 `Decorator`를 정의한다. 다른 데코레이터를 만들려면 `VisualComponent`를 상속받는 다른 서브클래스를 정의하면 된다.

```cpp
class Decorator : public VisualComponent {
public:
    Decorator(VisualComponent*);
    virtual void Draw();
    virtual void Resize();
    // ...
private:
    VisualComponent* _component;
};
```

`Decorator` 클래스는 `VisualComponent`를 상속받아 원본 객체와 동일한 인터페이스를 제공한다.

`_component`는 생성자에서 초기화된다. `Decorator`는 자신이 관리하는 `VisualComponent`에 정의된 연산이 필요하면 `_component->연산()`과 같은 호출을 통해 `VisualComponent`에 요청을 전달하도록 구현한다. 코드에서는 `VisualComponent` 클래스에 메시지를 보내는 것처럼 보이나, 실제로는 `_component`가 `VisualComponent` 클래스의 서브클래스 중 하나의 인스턴스를 참조하게 되는데, 이에 따라 어떤 클래스 연산이 호출될지 결정한다.

```cpp
void Decorator::Draw() {
    _component->Draw();
}

void Decorator::Resize() {
    _component->Resize();
}
```

`Decorator`의 서브클래스는 새로운 기능에 대한 구현 방법을 정의한다. `BorderDecorator`는 자신이 포함하는 요소에 테두리를 추가하기 위해 `Decorator` 클래스를 상속받아 부모 클래스의 `Draw()` 연산을 재정의한다.

`BorderDecorator` 클래스에 정의된 `DrawBorder()` 연산은 `private`로 정의하여 실제 그리기 기능을 담당한다. `private`로 정의하는 이유는 실제 `BorderDecorator`를 사용하는 클래스가 `VisualComponent`에 정의된 연산만을 사용할 뿐, 추가된 `Decorator` 서브클래스에 정의된 연산을 직접 호출할 수 없도록 하려는 것이다.

```cpp
class BorderDecorator : public Decorator {
public:
    BorderDecorator(VisualComponent*, int borderWidth);
    virtual void Draw();
private:
    void DrawBorder(int);
private:
    int _width;
};
void BorderDecorator::Draw() {
    Decorator::Draw();
    DrawBorder(_width);
}
```

이와 비슷한 방법으로 `ScrollDecorator` 클래스와 `DropShadowDecorator` 클래스 등을 개발할 수 있다.

이들 클래스를 조합해보자. 

윈도우에 `TextView`를 추가할 때 간단한 `TextView`만을 생각했다면 다음과 같이 처리된다.

```cpp
void Window::SetContents(VisualComponent* contents) {
   // ...
}
```

윈도우에 텍스트 뷰를 추가한다.

```cpp
Window* window = new Window;
TextView* textView = new TextView;

window->SetContents(textView);
```

이 `TextView`에 스크롤과 테두리를 추가하고 싶다면, 윈도우에 이를 추가하기 전 다음 `Decorator`와 관련된 정의 과정을 거치면 된다.

```cpp
window->SetContents(
   new BorderDecorator(
      new ScrollDecorator(textView), 1
   )
);
```

`Window`는 `VisualComponent` 인터페이스를 통해 자신의 정보를 접근하기 때문에 데코레이터 존재 자체를 알 수 없다. `Window`는 `SetContents()` 메서드에 정의된 `VisualComponent`라는 클래스로만 매개변수를 알고 있을 뿐이지 구체적인 데코레이터를 정의한 것이 아니므로 데코레이터가 추가됐다고 해서 `Window` 코드 변경이 필요한 것은 아니다. 

결과적으로 `Window` 클래스에 추가 변경 없이 새로운 기능을 제공하는 `Decorator` 클래스만 정의하여 확장성을 제공한다.