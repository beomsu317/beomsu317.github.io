---
title: "Template Method Pattern"
date: "2025-02-08"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

알고리즘의 구조를 슈퍼클래스에서 정의하고, 세부적인 구현은 서브클래스에서 담당하도록 하는 디자인 패턴이다. 이 패턴은 코드의 중복성을 줄이고 알고리즘의 변하지 않는 부분과 변해야 하는 부분을 분리하는 데 유용하다.

## Motivation

온라인 교육 플랫폼에서 강의 과정의 진행 단계를 표준화하려고 한다. 모든 과정은 다음 단계를 따른다고 하자.

1. 강의 자료 준비
2. 강의 진행
3. 과제 제출
4. 성적 평가

하지만, 강의 유형에 따라 세부적인 구현이 다르다. 

템플릿 메서드를 정의하여 강의 과정의 공통된 흐름을 유지하여, 알고리즘의 흐름을 변경하지 않고 세부 구현만 변경할 수 있으며, 중복 코드를 제거할 수 있다. 

## Applicability

- 어떠한 알고리즘을 이루는 부분 중 변하지 않는 부분을 슈퍼클래스에 정의하고, 다양해질 수 있는 부분은 서브클래스에서 정의할 수 있ㄷ도록 남겨두고자 할 때
- 서브클래스 사이 공통적인 행동을 추출하여 하나의 공통 클래스에 몰아둠으로써 코드의 중복을 피하고 싶을 때
- 서브클래스의 확장을 제어하고 싶을 때

## Structure

![template method structure](images/template_method_structure.png)

- `AbstractClass`: 공통적인 알고리즘의 흐름을 정의한다. 전체 알고리즘을 구성하는 여러 단계 중 일부는 구현을 제공하고, 일부는 서브클래스가 구현하도록 추상메서드로 남겨둔다.
- `ConcreteClass`: `AbstractClass`가 정의한 알고리즘의 추상 메서드를 구현한다. 즉, 템플릿 메서드에서 호출되ㅓ는 추상 메서드의 실제 동작을 정의한다. 

## Collaborations

- `ConcreteClass`는 `AbstractClass`를 통해 알고리즘의 변하지 않는 처리 단계를 구현한다.

## Consequences

1. **템플릿 메서드를 통해 코드 재사용이 가능하며, 특히 라이브러리 구현 시 중요하다.**
2. **훅 연산(hook operation)을 활용하면, 서브클래스가 선택적으로 동작을 확장할 수 있다.**

    훅 연산은 기본적으로 아무 동작도 수행하지 않는다. 슈퍼클래스의 템플릿 메서드에서 `HookOperation()`을 호출하면, 서브클래스는 이를 재정의하여 슈퍼클래스가 서브클래스의 확장을 제어할 수 있다.

    ```cpp
    class ParentClass {
    public:
        void Operation() {  // 템플릿 메서드
            // ParentClass의 기본 동작
            HookOperation();  // 서브클래스가 확장 가능
        }

        virtual void HookOperation() {}  // 기본적으로 아무 동작도 하지 않음
    };
    ```

    ```cpp
    class DerivedClass : public ParentClass {
    public:
        void HookOperation() override {
            // DerivedClass의 확장 동작
        }
    };
    ```
3. **할리우드 원칙을 따르며, 슈퍼클래스가 서브클래스를 제어할 수 있다.**

    할리우드 원칙은 "전화하지 마세요. 우리가 연락할게요(Don’t call us, we’ll call you)."를 의미한다. 즉, 슈퍼클래스는 서브클래스에 정의된 연산을 호출할 수 있지만, 반대 방향의 호출은 불가능하다.

## Implementation

1. **C++의 접근 제한 방법을 이용한다.**

    C++로 구현 시 기본 연산들은 `protected` 멤버로 구현한다. 서브클래스에서 재정의는 가능하지만, 외부에서는 직접 호출할 수 없도록 제한할 수 있다.
2. **기본 연산 수를 최소화한다.**

    템플릿 메서드의 주요 목적 중 하나는 서브클래스가 알고리즘을 실체화하기 위해 오버라이드해야 하는 기본 연산의 개수를 줄이는 것이다.
3. **이름을 짓는 규칙을 만든다.**

    재정의가 필요한 연산은 식별이 잘 되도록 접두사를 붙이는 것이 좋다. 예를 들어, 매킨토시에서 모든 템플릿 메서드는 `DoCreateDocument`, `DoRead` 등 `Do`로 시작하도록 이름을 지었다.

## Sample Code

`View` 클래스는 화면을 그리는 기능을 담당하며, 포커스(focus)를 받은 상태에서만 그리기를 수행할 수 있도록 설계되었다고 하자. 

이러한 상태를 마련하는 데 `Display()` 템플릿 메서드를 사용할 수 있다. `View`는 두 개의 구체 연산인 `SetFocus()`와 `ResetFocus()`를 정의해 `View` 클래스의 그리기 상태를 설정하거나 해제할 수 있도록 한다. `View` 클래스의 `DoDisplay()` 연산은 훅 연산으로, 실제 그리기를 수행한다.

`Display()`는 `DoDisplay()` 전 `SetFocus()`를 호출해 그리기 상태를 설정한다. 이후 그리기 상태를 해제하기 위해 `ResetFocus()`를 호출한다.

```cpp
void View::Display() {
    SetFocus();
    DoDisplay();
    ResetFocus();
}
```

`View` 사용자는 `Display()`만을 호출할 수 있어야 한다. `View` 서브클래스들은 `DoDisplay()`를 재정의할 수 있다.

일반적으로 `View` 클래스에 정의된 `DoDisplay()`는 아무런 일을 하지 않는다.

```cpp
void View::DoDisplay() { }
```

서브클래스에서는 이 연산을 오버라이드하여 특정한 그리기 행동을 추가한다.

```cpp
void MyView::DoDisplay() {
    // render the view's contents
}
```