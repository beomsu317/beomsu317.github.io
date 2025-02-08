---
title: "Factory Method Pattern"
date: "2025-01-28"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "creational pattern"]
---

객체를 생성하기 위해 인터페이스를 정의하지만, 어떤 클래스의 인스턴스를 생성할지에 대한 결정은 서브클래스가 결정하도록 한다.

## Motivation

애플리케이션이 여러 도형(원, 사각형 등)을 그려야 하며, 각 도형은 그리는 방식(화면에 그리기, 파일에 그리기 등)이 다르다. 클라이언트 코드에서 도형을 생성할 때 어떤 도형을 생성할지 조건문으로 판단하고, 이를 여러 곳에서 반복해야 한다.

팩토리 메서드 패턴을 사용하면 객체 생성을 서브클래스에 위임하여 클라이언트 코드에서 도형을 구체적인 클래스에 의존하지 않도록 할 수 있다. 즉, 도형 종류가 추가될 때 기존 코드를 수정하지 않고 새로운 도형 클래스를 추가하는 것만으로 해결할 수 있다.

## Applicability

- 어떤 클래스가 자신이 생성해야 하는 객체의 클래스를 예측할 수 없을 때
- 생성할 객체를 기술하는 책임을 자신의 서브클래스가 지정했으면 할 때
- 객체 생성의 책임을 몇 개의 보조 서브클래스 가운데 하나에게 위임하고, 어떤 서브클래스가 위임인지에 대한 정보를 국소화시키고 싶을 때

## Structure

![factory method pattern structure](images/patterns/factory_method_pattern_structure.png)

- `Product`: 팩토리 메서드가 생성하는 객체의 인터페이스를 정의
- `ConcreteProduct`: `Product` 클래스에 정의된 인터페이스를 실제로 구현
- `Creator`: `Product` 타입 객체를 반환하는 팩토리 메서드를 선언
- `ConcreteCreator`: 팩토리 메서드를 재정의해 `ConcreteProduct`의 인스턴스를 반환

## Collaborations

- `Creator`는 자신의 서브클래스를 통해 실제 필요한 팩토리 메서드를 정의하여 적절한 `ConcreteProduct`의 인스턴스를 반환할 수 있게 한다.

## Consequences

1. **서브클래스에 대한 훅(hook) 메서드를 제공한다.** 

    팩토리 메서드 패턴에서는 객체별로 서로 다른 버전을 제공하는 훅 기능을 서브클래스에 정의한다.

    훅(hook)은 기반 클래스에서 기본 동작(혹은 빈 구현)을 제공하는 메서드이다. 서브클래스나 사용자가 필요할 때 해당 메서드를 오버라이드하거나 새로운 동작을 추가해 원하는 기능을 확장할 수 있게 설계된 메커니즘이다.
2. **병렬적인 클래스 계통을 연결하는 역할을 담당한다.** 

    병렬적인 클래스 계통은 두 개 이상의 클래스 계층구조가 서로 연결되면서 같이 확장되는 상황을 의미한다. 즉, 하나의 클래스 계층구조가 커지면, 이에 따라 다른 관련 클래스 계층 구조도 함께 커지는 구조를 의미한다.

    다양한 그래픽을 표현하는 `Figure` 계층과 그래픽 객체를 조작하는 `Manipulator` 계층이 있다고 하자. `Figure` 계층에 새로운 클래스(예: `LineFigure`, `TextFigure`)를 추가하면 이에 맞는 새로운 `Manipulator` 클래스(예: `LineManipulator`, `TextManipulator`)도 추가해야 한다. 이렇게 두 계층이 병렬적으로 확장되는 구조가 된다.

### Implementation

1. **팩토리 메서드 패턴을 구현하는 방법은 크게 두 가지다.**

    (1) `Creator` 클래스를 추상 클래스로 정의하고, 정의한 팩토리 메서드에 대한 구현은 제공되지 않는 경우와 (2) `Creator`가 구체 클래스이고, 팩토리 메서드에 대한 기본 구현을 제공하는 경우이다. 추상 클래스로 정의할 때는 구현을 제공한 서브클래스를 반드시 정의해야 한다. 이때, 아직 예측할 수 없는 클래스들을 생성해야 하는 문제가 생긴다. 구체 클래스로 정의할 때는 `Creator`가 팩토리 메서드를 사용하여 유연성을 보장할 수 있다.

2. **팩토리 메서드를 매개변수화한다.**

    팩토리 메서드가 매개변수를 받아 어떤 종류의 제품을 생성할지 식별하게 만들 수 있다. 

3. **템플릿을 사용해 서브클래싱을 피한다.**

    팩토리 메서드를 사용하면 생길 수 있는 문제 중 하나는 `Product` 클래스를 하나 추가하려 할 때마다 서브클래싱을 해야 한다는 것이다. 때문에 클래스 계통의 부피가 확장되는 문제가 발생할 수 있다. 이런 문제를 해결할 수 있는 방법으로 `Creator` 클래스의 서브클래스가 되는 템플릿 클래스를 정의하고 이것이 `Product` 클래스로 매개변수화되도록 만드는 것이다.

    ```cpp
    class Creator {
    public:
        virtual Product* CreateProduct() = 0;
    };

    template <class TheProduct>
    class StandardCreator: public Creator { // Creator를 상속받는 팩토리 메서드를 구현할 서브클래스를 템플릿 클래스로 정의
    public:
        virtual Product* CreateProduct();
    };

    template <class TheProduct>
    Product* StandardCreator<TheProduct>::CreateProduct() {
        return new TheProduct;
    }
    ```

    이 템플릿 클래스를 이용하면 사용자는 `Creator`를 상속받는 서브클래스를 정의할 필요 없이, `Product` 클래스만 준비하면 된다.

    ```cpp
    class MyProduct : public Product {
    public:
        MyProduct();
        // ...
    };

    StandardCreator<MyProduct> myCreator;
    ```

4. **명명 규칙을 따르는 것은 중요하다.** 

    팩토리 메서드를 쓴다는 사실을 명확하게 만들어 주는 명명 규칙을 따르는 것이 좋다.

## Sample Code

`CreateMaze()` 함수는 미로를 만들어 반환한다. 이 함수의 문제는 미로, 방, 문, 벽 클래스를 직접 코딩한다는 것이다. 이 문제를 해결하기 위해 팩토리 메서드를 이용해 서브클래스들이 이 컴포넌트들을 선택할 수 있도록 한다.

미로, 방, 벽, 문 객체를 생성하기 위해 `MazeGame` 안에 팩토리 메서드를 정의한다.

```cpp
class MazeGame {
public:
    Maze* CreateMaze();
    
    // factory methods:
    virtual Maze* MakeMaze() const
    { return new Maze; }
    virtual Room* MakeRoom(int n) const
    { return new Room(n); }
    virtual Wall* MakeWall() const
    { return new Wall; }
    virtual Door* MakeDoor(Room* r1, Room* r2) const
    { return new Door(r1, r2); }
};
```

`Make~`로 시작하는 메서드들이 팩토리 메서드이다. 각각의 팩토리 메서드는 미로를 복합하는 컴포넌트를 반환한다. `MazeGame()`은 기본 구현을 제공한다.


```cpp
Maze* MazeGame::CreateMaze() {
    Maze* aMaze = MakeMaze();
    
    Room* r1 = MakeRoom(1);             // 팩토리 메서드 사용
    Room* r2 = MakeRoom(2);             // 팩토리 메서드 사용
    Door* theDoor = MakeDoor(r1, r2);   // 팩토리 메서드 사용
    
    aMaze->AddRoom(r1);
    aMaze->AddRoom(r2);
    
    r1->SetSide(North, MakeWall());
    r1->SetSide(East, theDoor);
    r1->SetSide(South, MakeWall());
    r1->SetSide(West, MakeWall());
    
    r2->SetSide(North, MakeWall());
    r2->SetSide(East, MakeWall());
    r2->SetSide(South, MakeWall());
    r2->SetSide(West, theDoor);
    return aMaze;
}
```

다른 게임을 만든다면 `MazeGame` 클래스를 상속해 재정의하면 된다. 서로 다른 제품에서의 다양성을 정의하기 위해 팩토리 메서드의 일부나 전부를 재정의한다. 예를 들어, `BombedMazeGame` 클래스는 `Room`과 `Wall` 객체를 다시 정의해 폭탄을 맞은 것들을 반환하도록 만든다.

```cpp
class BombedMazeGame : public MazeGame {
public:
    BombedMazeGame();
    
    virtual Wall* MakeWall() const
    { return new BombedWall; }
    
    virtual Room* MakeRoom(int n) const
    { return new RoomWithABomb(n); }
};
```

또 다른 예인 `EnchantedMazeGame`은 다음과 같다.

```cpp
class EnchantedMazeGame : public MazeGame {
public:
    EnchantedMazeGame();
    
    virtual Room* MakeRoom(int n) const
    { return new EnchantedRoom(n, CastSpell()); }
    
    virtual Door* MakeDoor(Room* r1, Room* r2) const
    { return new DoorNeedingSpell(r1, r2); }
    
protected:
    Spell* CastSpell() const;
};
```