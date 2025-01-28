---
title: "GoF Design Patterns"
date: "2025-01-27"
author: "Beomsu Lee"
tags: ["c++", "design pattern"]
---

## Creational Patterns

미로 게임을 생성 패턴 샘플 코드에 사용할 것이다.

![maze class diagram](images/maze_class_diagram.png)

```cpp
enum Direction {North, South, East, West};
```

`MapSite` 클래스는 미로의 컴포넌트들에 필요한 모든 연산을 정의한 공통 추상 클래스이다. 

```cpp
class MapSite {
public:
    virtual void Enter() = 0;
};
```

`Room` 클래스는 `MapSite`를 상속받은 구체적인 클래스로 미로에 있는 다른 요소와 관련성을 갖도록 정의한다. 

```cpp
class Room : public MapSite {
public:
    Room(int roomNo);
    
    MapSite* GetSide(Direction) const;
    void SetSide(Direction, MapSite*);

    virtual void Enter();
private:
    MapSite* _sides[4];
    int _roomNumber;
};
```

`Wall`, `Door` 클래스는 방의 각 측면에 있을 수 있는 문과 벽을 나타낸다.

```cpp
class Wall : public MapSite {
public:
    Wall();
    virtual void Enter();
};

class Door : public MapSite {
public:
    Door(Room* = 0, Room* = 0);
    virtual void Enter();
    Room* OtherSideFrom(Room*);
private:
    Room* _rooml;
    Room* _room2;
    bool _isOpen;
};
```

방들의 집합을 표현하기 위해 `Maze`를 정의한다.

```cpp
class Maze {
public:
    Maze();
    void AddRoom(Room*) ;
    Room* RoomNo(int) const;
private:
    // ...
};
```

마지막으로 미로를 생성하기 위한 클래스인 `MazeGame`을 생성한다.

```cpp
Maze* MazeGame::CreateMaze () {
    Maze* aMaze = new Maze;
    Room* rl = new Room(l);
    Room* r2 = new Room (2);
    Door* theDoor = new Door(rl, r2);
    
    aMaze->AddRoom(rl);
    aMaze->AddRoom(r2);
    
    rl->SetSide(North, new Wall);
    rl->SetSide(East, theDoor);
    rl->SetSide(South, new Wall);
    rl->SetSide(West, new Wall);
    
    r2->SetSide(North, new Wall);
    r2->SetSide(East, new Wall);
    r2->SetSide(South, new Wall);
    r2->SetSide(West, theDoor);
    
    return aMaze;
}
```

### Abstract Factory

추상 팩토리 패턴은 연관성이 있는 **객체 군**을 생성하기 위한 인터페이스를 제공한다.

#### Applicability

- 객체가 생성되거나 구성, 표현되는 방식과 무관하게 시스템을 독립적으로 만들고자 할 때
- 여러 제품군 중 하나를 선택해 시스템을 설정해야 하고, 한 번 구성한 제품을 다른 제품으로 대체할 수도 있을 때
- 관련된 제품 객체들이 함께 사용되도록 설계되었고, 이 부분에 대한 제약이 외부에서도 지켜지도록 하고 싶을 때
- 제품에 대한 클래스 라이브러리를 제공하고, 이들의 구현이 아닌 인터페이스를 노출시키고 싶을 때

#### Structure

![abstract factory pattern structure](images/abstract_factory_pattern_structure.png)

- `AbstractFactory`: 개념적 제품에 대한 객체를 생성하는 연산으로 인터페이스를 정의
- `ConcreteFactory`: 구체적인 제품에 대한 객체를 생성하는 연산을 구현
- `AbstractProduct`: 개념적 제품에 대한 인터페이스를 정의
- `ConcreteProduct`: 팩토리가 생성할 객체를 정의하고, `AbstractProduct`가 정의하는 인터페이스를 구현
- `Client`: `AbstractFactory`와 `AbstractProduct` 클래스에 선언된 인터페이스를 사용 

#### Consequences

1. **구체적인 클래스를 분리한다.** 제품 객체를 생성하는 과정과 책임을 캡슐화한 것이기 때문에 구체적인 구현 클래스는 사용자에게서 분리된다.
2. **제품군을 쉽게 대체할 수 있다.** 
3. **제품 사이 일관성을 증진시킨다.** 애플리케이션은 한 번에 오직 한 군에서 만든 객체를 사용하도록 하여 프로그램의 일관성을 갖도록 한다.
4. **새로운 종류의 제품을 제공하기 어렵다.** 새로운 컴포넌트를 만들기 위한 확장이 쉽지 않다. 새로운 컴포넌트를 추가하려면 추상 팩토리와 모든 서브클래스의 변경이 필요하다.

#### Sample Code

미로 생성에 추상 팩토리 패턴을 사용해보자. `MazeFactory` 클래스는 미로의 컴포넌트들을 생성한다.

```cpp
class MazeFactory {
public:
    MazeFactory();
    
    virtual Maze* MakeMaze() const
    { return new Maze; }
    virtual Wall* MakeWall() const
    { return new Wall; }
    virtual Room* MakeRoom(int n) const
    { return new Room(n); }
    virtual Door* MakeDoor(Room* r1, Room* r2) const
    { return new Door(r1, r2); }
};
```

`MazeGame`의 `CreateMaze()` 멤버 함수는 다른 멤버 함수를 이용해 방 두 개의 미로를 만든다. 기존 `CreateMaze()` 함수는 클래스 이름을 하드코딩해놨기 때문에 서로 다른 컴포넌트를 가지고 미로를 만들어 내기가 힘들다.

다음은 `MazeFactory`를 매개변수로 받아 이 문제를 해결한 `CreateMaze()` 함수다.

```cpp
Maze* MazeGame::CreateMaze (MazeFactory& factory) {
    Maze* aMaze = factory.MakeMaze();
    Room* r1 = factory.MakeRoom(1);
    Room* r2 = factory.MakeRoom(2);
    Door* aDoor = factory.MakeDoor(r1, r2);
    
    aMaze->AddRoom(r1);
    aMaze->AddRoom(r2);
    
    r1->SetSide(North, factory.MakeWall());
    r1->SetSide(East, aDoor);
    r1->SetSide(South, factory.MakeWall());
    r1->SetSide(West, factory.MakeWall());
    
    r2->SetSide(North, factory.MakeWall());
    r2->SetSide(East, factory.MakeWall());
    r2->SetSide(South, factory.MakeWall());
    r2->SetSide(West, aDoor);
    
    return aMaze;
}
```

또한 폭탄이 장착된 방을 만들고 싶다면, 방에 폭탄이 있는지 추적하고 관리하는 클래스를 `Room`의 서브클래스로 만들면 된다. 또한 방의 폭탄이 터진 후 벽에 손상이 갔을 때 벽의 모습의 바뀌도록 하려면, `Wall`의 새로운 서브클래스를 만들면 된다.

```cpp
Wall* BombedMazeFactory::MakeWall () const {
    return new BombedWall;
}

Room* BombedMazeFactory::MakeRoom(int n) const {
    return new RoomWithABomb(n);
}
```


폭탄이 들어있는 미로를 만들려면 `BombedMazeFactory`를 `CreateMaze`에 넘겨 호출하면 된다.

```cpp
MazeGame game;
BombedMazeFactory factory;    // 생성하고자 하는 요소를 생성하는 MazeFactory의 서브클래스인 BombedMazeFactory의 인스턴스 정의

game.CreateMaze(factory);    // CreateMaze 메서드 호출 시 생성의 책임을 지닐 BombedMazeFactory 인스턴스를 매개변수로 전달
```

또한 마법이 걸린 미로를 만들려면 마찬가지로 `EnchantedMazeFactory`를 `MazeFactory`에서 서브클래싱한 후, 멤버 함수를 재정의하여 `Room`, `Wall`을 상속하는 다른 서브클래스의 인스턴스를 반환하게 한뒤 `CreateMaze`에 넘겨주면 된다.

```cpp
class EnchantedMazeFactory : public MazeFactory {  // MazeFactory를 상속받아 부모 클래스에 정의된 연산을 재정의한 후 구체적인 요소를 생성하여 반환하도록 구현하는 서브클래스
public:
    EnchantedMazeFactory();
    virtual Room* MakeRoom(int n) const
    { return new EnchantedRoom(n, CastSpell()); }   // Room을 상속받은 EnchantedRoom의 인스턴스를 생성하여 반환
    
    virtual Door* MakeDoor(Room* r1, Room* r2) const
    { return new DoorNeedingSpell(r1, r2); }        // Door를 상속받은 DoorNeedingSpell의 인스턴스를 생성하여 반환
    
protected:
    Spell* CastSpell() const;
};
```

#### Builder

복잡한 객체를 생성하는 방법과 표현하는 방법을 정의하는 클래스를 별도로 분리하여, 서로 다른 표현이라도 이를 생성할 수 있는 동일한 절차를 제공한다.

#### Applicability

- 복합 객체의 생성 알고리즘이 이를 합성하는 요소 객체들이 무엇인지 이들의 조립 방법에 독립적일 때
- 합성할 객체들의 표현이 서로 다르더라도 생성 절차에서 이를 지원해야 할 때

#### Structure

