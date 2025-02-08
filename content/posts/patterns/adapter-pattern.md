---
title: "Adapter Pattern"
date: "2025-01-28"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "structural pattern"]
---

클래스의 인터페이스를 사용자가 기대하는 인터페이스 형태로 변환시킨다. 서로 일치하지 않는 인터페이스를 갖는 클래스들은 함께 동작시킨다.

## Motivation

구식 라이브러리나 외부 라이브러리와 새로운 시스템이 호환되지 않는 문제가 발생할 수 있다. 예를 들어, 어떤 API는 기존 시스템에서 사용하는 인터페이스와 다르게 설계되어, 이를 그대로 사용이 불가능할 수 있다. 

어댑터 패턴을 사용해 호환성을 맞춰줄 수 있다.

## Applicability

- 기존 클래스를 사용하고 싶은데 인터페이스가 맞지 않을 때
- 아직 예측하지 못한 클래스나 실제 관련되지 않는 클래스들이 기존 클래스를 재사용하고자 하지만, 이미 정의된 재사용 가능한 클래스가 지금 요청하는 인터페이스를 정의하고 있지 않을 때, 즉 이미 만든 것을 재사용하고자 하나 이 재사용 가능한 라이브러리를 수정할 수 없을 때
- (Object Adapter만 해당) 이미 존재하는 여러 개의 서브클래스를 사용해야 하는데, 이 서브클래스들의 상속을 통해 이들 인터페이스를 다 개조한다는 것이 현실성이 없을 때, Object Adapter를 사용해 부모 클래스의 인터페이스를 변형하는 것이 더 바람직함

## Structure

### Class Adapter

Class Adapter는 다중 상속을 활용해 한 인터페이스를 다른 인터페이스로 적응시킨다.

![class adapter structure](images/patterns/class_adapter_structure.png)

### Object Adapter

Object Adapter는 객체 합성을 사용해 이루어진다.

![object adapter structure](images/patterns/object_adapter_structure.png)


- `Target`: 사용자가 사용할 인터페이스를 정의하는 클래스
- `Client`: `Target` 인터페이스를 만족하는 객체와 동작할 대상
- `Adaptee`: 인터페이스의 적응이 필요한 기존 인터페이스를 정의
- `Adapter`: `Target` 인터페이스에 `Adaptee`의 인터페이스를 적응시키는 클래스

## Collaborations

- 사용자는 `Adapter`에 해당하는 클래스의 인스턴스 연산을 호출하고, `Adapter`는 해당 요청을 수행하기 위해 `Adaptee`의 연산을 호출한다.

## Consequences

### Class Adapter

- `Adapter` 클래스는 `Adaptee` 클래스를 `Target` 클래스로 변형하는데, 이를 위해 `Adaptee` 클래스를 상속받아야 하기 때문에, 하나의 클래스(`Adaptee`)만 변환할 수 있으며, `Adaptee`의 서브클래스까지 포함하여 변환할 수 없다.
- `Adapter` 클래스는 `Adaptee` 클래스를 상속하기 때문에 `Adaptee`에 정의된 행동을 재정의할 수도 있다.
- 한 개의 객체(`Adapter`)만 사용하며, `Adaptee`로 가기 위한 추가적인 포인터는 필요하지 않다.

### Object Adapter

- `Adapter` 클래스는 하나만 존재해도 많은 `Adaptee` 클래스들과 동작할 수 있다. `Adapter` 객체가 포함하는 `Adaptee`에 대한 참조자는 `Adaptee` 인스턴스를 관리할 수도 있고, `Adaptee` 클래스를 상속받는 다른 서브클래스의 인스턴스도 관리할 수 있기 때문이다. 따라서 하나의 `Adapter` 클래스로 모든 `Adaptee` 클래스와 이를 상속받는 서브클래스 모두를 이용할 수 있다.
- `Adaptee` 클래스의 행동을 재정의하기 어렵다. 이를 위해 `Adaptee` 클래스를 상속받아 새로운 서브클래스를 만들고, `Adapter` 클래스는 `Adaptee` 클래스가 아닌 `Adaptee`의 서브클래스를 참조해야 한다.

## Implementation

1. **Class Adapter를 C++로 구현**

    C++에서 `Adapter` 클래스는 `Target` 클래스에서 `public`으로 상속받고, `Adaptee`는 `private`으로 상속받아야 한다. 즉, `Target`에 정의된 인터페이스는 `Adapter`에서도 `public`으로 공개되지만, `Adaptee`는 내부 구현에 필요한 것이므로, `Adaptee`가 사용자에게 알려질 필요는 없다.
2. **대체 가능 Adapter**

    1. **추상 연산을 사용하는 방법**

        범위가 제한된 `Adaptee` 인터페이스를 추상 연산으로 `Target`에 정의한다. 이 클래스를 상속받는 서브클래스는 이 추상 연산에 대한 구현을 제공해야 하고, 계층 구조를 갖는 객체를 개조할 수 있다. 
    2. **위임 객체를 사용하는 방법**

        `Target` 클래스가 자신에게 요청된 메시지를 다른 위임 객체에게 전달하는 방법이다. 
    3. **매개변수화된 `Adapter`를 사용하는 방법**

        제네릭이나 생성자 주입 등을 사용해 유연하게 다양한 `Target` 객체를 처리할 수 있도록 설계한 `Adapter`이다.

## Sample Code

### Class Adapter

```cpp
class Shape {
public:
    Shape();
    virtual void BoundingBox(Point& bottomLeft, Point& topRight) const;
    virtual Manipulator* CreateManipulator() const;
};

class TextView {
public:
    TextView();
    void GetOrigin(Coord& x, Coord& y) const;
    void GetExtent(Coord& width, Coord& height) const;
    virtual bool IsEmpty() const;
};
```

`Shape`의 `BoundingBox()` 메서드는 `bottomLeft`와 `topRight`를 매개변수로 받아 상자(`BoundingBox`)를 만든다. 그러나 `TextView` 클래스에는 `BoundingBox()` 메서드는 정의되지 않고, 이를 대치할 수 있는 `GetOrigin()`, `GetExtent()` 두 메서드가 정의되어 있다. `GetOrigin()`을 통해 시작점이 되는 `x`, `y` 좌표를 얻고, `GetExtent()`로 넓이, 길이를 구해 경계가 있는 상자를 만들 수 있다.

`Shape` 클래스에는 `Manipulator` 객체를 생성하기 위한 `CreateManipulator()` 연산이 정의되어 있다. 이 연산을 통해 만들어진 객체는 사용자가 도형을 조작할 때 이 도형을 어떻게 이동시키는지 알고 있다. 그러나 `TextView`에는 이런 연산이 없다. 

이렇게 `TextView` 클래스가 `Shape`이 원하는 형태의 연산 이름으로 서비스를 제공하지 않을 때에도 `TextView`를 사용하고자 한다면, `Adapter`를 하나 만들어야 한다.

`Adapter` 클래스인 `TextShape`을 구현할 때 다중 상속을 이용해보자. 

`Adapter` 클래스가 두 개의 부모 클래스에서 상속받지만, 두 개의 상속은 차이가 있다. 하나는 부모 클래스에 정의된 인터페이스를 상속받기 위함이고(`public`), 또 다른 하나는 부모 클래스에 정의된 구현을 상속받기 위함이다(`private`).

```cpp
class TextShape : public Shape, private TextView {
public:
    TextShape();
    
    virtual void BoundingBox(Point& bottomLeft, Point& topRight) const;
    virtual bool IsEmpty() const;
    virtual Manipulator* CreateManipulator() const;
};
```

`BoundingBox()` 연산은 `Shape` 클래스에 정의된 연산과 동일한 이름으로 맞추고 있다. 그러나 그 구현은 `TextView` 클래스에 정의된 `GetOrigin()`, `GetExtent()`를 사용해 기능을 만족시킨다.

```cpp
void TextShape::BoundingBox(Point& bottomLeft, Point& topRight) const {
    Coord bottom, left, width, height;

    GetOrigin(bottom, left);
    GetExtent(width, height);

    bottomLeft = Point(bottom, left);
    topRight = Point(bottom + height, left + width);
};
```

`IsEmpty()` 연산에서는 어댑터 구현에 공통적인 요청을 직접 전달하고 있다.

```cpp
bool TextShape::IsEmpty () const {
    return TextView::IsEmpty();
}
```

`TextView` 클래스에서 제공되지는 않지만, `Shape`의 서브클래스로 제공해야하는 `CreateManipulator()`의 처리를 보자. 이 부분은 새로 개발해야 한다. 즉, `Manipulator` 클래스도 있어야 하고, 이를 상속받아 텍스트를 처리하는 `TextManipulator`도 있어야 한다(이런 클래스들은 이미 개발되어 있다고 가정하자). `CreateManipulator()`의 구현은 이미 개발된 `TextManipulator` 클래스의 인스턴스를 만들어 반환하는 것 뿐이다.

```cpp
Manipulator* TextShape::CreateManipulator() const {
    return new TextManipulator(this);
}
```

### Object Adapter

Object Adapter는 서로 다른 인터페이스를 갖는 두 클래스를 합치기 위해 객체 합성 기법을 사용한다. 이 때 `Adapter` 클래스인 `TextShape`은 `TextView` 클래스 인스턴스에 대한 포인터를 관리한다.

```cpp
class TextShape : public Shape {
public:
    TextShape(TextView*);
    
    virtual void BoundingBox(Point& bottomLeft, Point& topRight) const;
    virtual bool IsEmpty() const;
    virtual Manipulator* CreateManipulator() const;
private:
    TextView* _text;        // TextView에 대한 참조자
};
```

`TextShape` 클래스는 `TextView` 인스턴스에 대한 포인터를 초기화할 수 있는 생성자를 반드시 구현해야 한다. 이 포인터를 통해 `TextView` 클래스에 정의된 서비스가 필요할 때마다, `TextView` 객체에 대한 포인터를 이용해 호출하도록 해야 한다. 

```cpp
TextShape::TextShape(TextView* t) {
    _text = t;
}

void TextShape::BoundingBox(Point& bottomLeft, Point& topRight) const {
    Coord bottom, left, width, height;

    _text->GetOrigin(bottom, left);     // 객체 참조자를 통한 메서드 호출
    _text->GetExtent(width, height);    // 객체 참조자를 통한 메서드 호출

    bottomLeft = Point(bottom, left);
    topRight = Point(bottom + height, left + width);
}

bool TextShape::IsEmpty() const {
    return _text->IsEmpty();
}
```

`CreateManipulator()` 구현은 동일하다. `CreateManipulator()` 구현은 새롭게 구현하는 것이므로 상속을 하더라도 부모 클래스에서 상속받은 내용이 없기 때문에 객체 합성 방식으로 구현하는 것과 차이가 없다.

```cpp
Manipulator* TextShape::CreateManipulator() const {
    return new TextManipulator(this);
}
```

객체 합성 방식의 경우 어댑터 내부에 `Adaptee` 객체를 포함하고, 생성자로 주입받거나 관리해야 하므로 코드가 더 많은 코드가 필요하다. 