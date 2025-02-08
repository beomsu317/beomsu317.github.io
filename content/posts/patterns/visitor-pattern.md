---
title: "Visitor Pattern"
date: "2025-02-08"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

객체의 구조와 관계는 변경하지 않고, 객체에 대한 연산을 외부에서 추가하는 디자인 패턴이다. 이 패턴은 객체를 방문하여 각 객체에 대해 서로 다른 작업을 수행할 수 있게 해준다.

## Motivation

여러 종류의 도형 객체들을 가진 시스템을 관리한다고 하자. 각 도형 객체(`Circle`, `Rectangle`, `Triangle`)는 자체적인 속성과 고유한 그리기 로직을 가진다. 

시스템에서 도형들에 대해 공통적으로 할 수 있는 연산들(예: 면적 계산, 그리기)을 추가해야 한다고 하자.

방문자 패턴을 사용하면 도형 객체의 확장(수정) 없이 연산을 추가할 수 있다. 

## Applicability

- 서로 다른 인터페이스를 가진 클래스들이 포함된 객체 구조에 연산을 적용하고 싶을 때
- 각각의 특징이 있고 관련되지 않은 많은 연산이 한 객체 구조에 속해있는 객체들에 대해 수행될 필요가 있으며, 연산으로 클래스를 더럽히고 싶지 않을 때
- 객체 구조를 정의한 클래스를 거의 변하지 않지만, 전체 구조에 걸쳐 새로운 연산을 추가하고 싶을 때

## Structure

![visitor pattern structure](images/patterns/visitor_pattern_structure.png)

- `Visitor`: 객체 구조 내에 있는 각 `ConcreteElement` 클래스에 대해 특정한 작업을 수행하는 역할을 한다. 이때 중요한 점은, 각각의 `ConcreteElement` 객체에 대해 서로 다른 작업을 수행할 수 있도록 인터페이스를 정의하는 것이다. `Visitor` 클래스는 방문자로서 객체 구조에 있는 각 구체적인 요소(`ConcreteElement`)들을 방문하여, 이 요소들의 구체 클래스에 맞는 메서드를 호출하는 방식으로 동작한다.
- `ConcreteVisitor`: `Visitor` 클래스에 선언된 연산을 구현한다. `ConcreteVisitor` 클래스는 객체 구조를 순회하며 각 요소에 대해 특정 작업을 수행하는 데 사용된다.
- `Element`: `Visitor`를 인자로 받아들이는 `Accept()` 연산을 정의한다.
- `ConcreteElement`: 인자로 방문자 객체를 받아들이는 `Accept()` 연산을 구현한다.
- `ObjectStructure`: 객체 구조 내 원소들을 나열하고, `Visitor`가 이 원소들을 접근할 수 있게 하는 상위 수준의 인터페이스를 제공한다.

## Collaborations

- `Visitor` 패턴을 방문하는 사용자는 `ConcreteVisitor` 클래스의 객체를 생성하고, 이 객체를 통해 객체 구조를 순회한다.
- `Visitor`가 구성 원소들을 방문할 때, 구성 원소는 해당 클래스의 `Visitor` 연산을 호출하고, 그 연산에 자신을 인자로 제공하여, `Visitor`에게 자신의 상태를 전달할 수 있도록 한다. 

![visitor collaborations](images/patterns/visitor_collaborations.png)

## Consequences

1. **`Visitor` 클래스는 새로운 연산을 쉽게 추가한다.**

    기존 객체 구조는 변경하지 않고 새로운 방문자(`Visitor`) 클래스를 추가하는 것만으로 새로운 연산을 객체 구조에 적용할 수 있다.
2. **방문자를 통해 관련된 연산을 한 군데로 모으고 관련되지 않은 연산을 떼어낼 수 있다.**

    관련된 연산들이 각 객체 구조의 원소에 분산되지 않도록 하며, 모든 연산을 `Visitor` 클래스에 모아서 관리할 수 있게 만든다.
3. **새로운 `ConcreteElement` 클래스를 추가하기 어렵다.**

    `ConcreteElement` 클래스가 새로 생길 때마다, `Visitor` 클래스와 그 서브클래스들 모두를 수정해야 할 필요가 있다. 즉, `ConcreteVisitor` 클래스에 새로운 `ConcreteElement`에 대한 처리를 위한 새로운 메서드를 추가해야 하며, 이는 각 `ConcreteVisitor` 서브클래스에도 동일한 작업을 요구한다.

4. **클래스 계층 구조에 걸쳐 방문한다**

    `Iterator`는 같은 타입의 객체들을 순회할 때 사용하고, `Visitor`는 다양한 타입의 객체들을 순회하며 각 객체 타입에 맞는 연산을 적용할 수 있다. 즉, 방문자 패턴은 객체 구조에 다양한 타입의 원소가 존재할 때 훨씬 유연한 해결책이 된다.

5. **상태를 누적할 수 있다.**
    
    방문자는 객체 구조 내 각 원소들을 방문하며 상태를 누적할 수 있다.

6. **데이터 은닉을 깰 수 있다.**

    방문자 패턴에서 `ConcreteElement` 인터페이스는 원소 내부 상태에 접근하는 데 필요한 연산들을 모두 공개 인터페이스로 만들어야 하는데, 이는 캡슐화 전략을 위배한다.

## Implementation

각 객체 구조는 자신과 연관된 `Visitor` 클래스를 가진다. 이 추상 `Visitor` 클래스는 객체 구조를 정의하는 각각의 `ConcreteElement` 클래스를 위한 `VisitConcreteElement()` 연산을 선언한다. 

`Visitor`의 각 `Visit()` 연산의 인자로 `ConcreteElement`를 정의하여 `Visitor`는 `ConcreteElement`의 인터페이스에 직접 접근하게 한다. `ConcreteVisitor` 클래스는 각 `Visit()` 연산을 재정의해 이에 대응되는 `ConcreteElement` 클래스를 위한 방문자 별 행동을 구현한다.

`Visitor` 클래스는 다음과 같이 선언된다.

```cpp
class Visitor {
public:
    virtual void VisitElementA(ElementA*);
    virtual void VisitElementB(ElementB*);
    // and so on for other concrete elements
protected:
    Visitor();
};
```

`ConcreteElement`는 `Accept()` 메서드를 통해 방문자를 받아들이고, 해당 방문자의 `Visit` 메서드를 호출한다. 

```cpp
class Element {
public:
    virtual ~Element();
    virtual void Accept(Visitor&) = 0;
protected:
    Element();
};

class ElementA : public Element {
public:
    ElementA();
    virtual void Accept(Visitor& v) { v.VisitElementA(this); }
};

class ElementB : public Element {
public:
    ElementB();
    virtual void Accept(Visitor& v) { v.VisitElementB(this); }
};
```

`CompositeElement` 클래스에서는 다음과 같이 `Accept()`를 구현한다.

```cpp
class CompositeElement : public Element {
public:
    virtual void Accept(Visitor&);
private:
    List<Element*>* _children;
};

void CompositeElement::Accept(Visitor& v) {
    ListIterator<Element*> i(_children);
    for (i.First(); !i.IsDone(); i.Next()) {
        i.CurrentItem()->Accept(v);
    }
    v.VisitCompositeElement(this);
}
```

방문자 패턴을 적용할 때 발생되는 두 가지 이슈가 있다.

1. **이중 디스패치.**

    방문자 패턴에서 이중 디스패치는 `Accept()` 메서드를 호출하는 방식으로 구현된다. `Accept()` 메서드는 방문자가 자신을 방문할 때 그 방문자가 호출해야 할 연산을 결정하는 역할을 한다.

    `Accept()` 메서드에서 `Visitor`와 `Element`의 타입에 따라 호출되는 `Visit()` 메서드가 다르게 동작한다. 즉, 연산이 두 개의 타입에 따라 다르게 분기하게 된다.

    따라서 새로운 `Element`가 추가될 때마다 모든 `Visitor` 클래스에서 해당 `Element`를 처리하기 위한 `Visit()` 메서드를 추가해야 하므로(OCP 위배), 새로운 `ConcreteElement` 클래스가 자주 추가되는 경우 코드 유지 관리가 어려워질 수 있다.
2. **객체 구조 순회 책임.**

    객체 구조의 순회 책임은 세 가지 장소 중 하나에서 맡을 수 있다. **객체 구조 자체**, **방문자**, 또는 **별도의 반복자 객체**이다.

    1. 객체 구조 자체

        복합체(Composite) 구조에서 자주 사용된다. 이 방식은 복합체가 자신의 자식 객체에 대해 `Accept()`를 호출하고, 각 자식 객체는 다시 자신의 자식들에게 `Accept()`를 호출하는 형태로 재귀적인 순회가 이루어진다.

    2. 반복자

        반복자는 원소를 순회하는 데 매우 유용한 방식이다. C++에서는 내부 반복자와 외부 반복자를 선택할 수 있으며 각각의 장단점이 있다.
    3. 방문자

        각 `ConcreteVisitor`마다 순회 알고리즘을 구현하는 방식이다. 이를 통해 객체 구조의 순회 방식을 외부에서 제어할 수 있다. 이 방식은 복잡한 순회 알고리즘을 구현하는 데 유용하다.

## Sample Code

방문자 패턴을 통해 재료(material)의 재고량 및 장비(equipment)의 총 비용을 계산한다고 하자.

`Equipment` 클래스에 `Accept()` 연산을 추가하여 `Visitor`와 상호작용 할 수 있도록 한다.

```cpp
class Equipment {
public:
    virtual ~Equipment();

    const char* Name() { return _name; }

    virtual Watt Power();
    virtual Currency NetPrice();
    irtual Currency DiscountPrice();

    virtual void Accept(EquipmentVisitor&);
protected:
    Equipment(const char*);
private:
    const char* _name;
};
```

`Equipment`의 연산들은 장비의 가격을 알려준다. 이 서브클래스들은 가격 정보 반환 연산을 재정의하여 각각의 장비의 가격을 반환한다.

이 장비에 대한 모든 방문자를 나타내는 추상 클래스인 `EquipmentVisitor`에는 각 서브클래스를 위한 가상 함수가 있다. 모든 가상 함수는 아무 동작도 하지 않는다. 

```cpp
class EquipmentVisitor {
public:
    virtual ~EquipmentVisitor();
    virtual void VisitFloppyDisk(FloppyDisk*);
    virtual void VisitCard(Card*);
    virtual void VisitChassis(Chassis*);
    virtual void VisitBus(Bus*);
    // and so on for other concrete subclasses of Equipment
protected:
    EquipmentVisitor();
};
```

`Equipment`의 서브클래스는 `Accept()`를 정의하는 데, 해당 서브클래스를 처리할 수 있는 `EquipmentVisitor()` 연산을 호출한다.

```cpp
void FloppyDisk::Accept(EquipmentVisitor& visitor) {
    visitor.VisitFloppyDisk(this);
}
```

다른 장비들을 (자식으로) 포함한 `Equipment` 서브클래스는 자신의 자식을 순회하고, 또 그들에 대해 `Accept()`를 호출하는 식으로 구현한다. 이후에 `Visit()` 연산을 호출한다.

```cpp
void Chassis::Accept(EquipmentVisitor& visitor) {
    for (ListIterator<Equipment*> i(_parts); !i.IsDone();i.Next()){
        i.CurrentItem()->Accept(visitor);
    }
    visitor.VisitChassis(this);
}
```

`EquipmentVisitor`의 서브클래스들은 더 구체적인 알고리즘을 정의한다. `PricingVisitor`는 속한 요소들의 비용을 계산하는데, 모든 단순 장비(플로피)의 실제 가격과 모든 복합 장비(섀시)의 할인 가격을 계산한다.

```cpp
class PricingVisitor : public EquipmentVisitor {
public:
    PricingVisitor();
    Currency& GetTotalPrice();
    virtual void VisitFloppyDisk(FloppyDisk*);
    virtual void VisitCard(Card*);
    virtual void VisitChassis(Chassis*);
    virtual void VisitBus(Bus*);
    // ...
private:
    Currency _total;
};

void PricingVisitor::VisitFloppyDisk(FloppyDisk* e) {
    _total += e->NetPrice();
}

void PricingVisitor::VisitChassis(Chassis* e) {
    _total += e->DiscountPrice();
}
```

`PricingVisitor`는 장비 구조에 속한 모든 노드의 가격을 계산한다. `PricingVisitor`를 이용해 가격 산정 원칙을 정할 수 있다. 

재고량을 계산하는 용도의 방문자는 다음과 같이 정의할 수 있다.

```cpp
class InventoryVisitor : public EquipmentVisitor {
public:
    InventoryVisitor();

    Inventory& Getlnventory();

    virtual void VisitFloppyDisk(FloppyDisk*);
    virtual void VisitCard(Card*);
    virtual void VisitChassis(Chassis*);
    virtual void VisitBus(Bus*);
    // ...
private:
    Inventory _inventory;
};
```

`InventoryVisitor` 객체는 객체 구조 내 속해있는 각 장비 타입에 대한 총 재고량을 누적한다. 이를 위해, 장비를 추가하는 인터페이스를 정의한, `Inventory` 클래스를 사용한다.

```cpp
void InventoryVisitor::VisitFloppyDisk(FloppyDisk* e) {
    _inventory.Accumulate(e);
}

void InventoryVisitor::VisitChassis(Chassis* e) {
    _inventory.Accumulate(e);
}
```

다음은 장비 객체 구조에 대해 `InventoryVisitor` 객체를 사용하는 예다.

```cpp
Equipment* component;
InventoryVisitor visitor;

component->Accept(visitor);
cout << "Inventory "
     << component->Name()
     << visitor.GetInventory();
```