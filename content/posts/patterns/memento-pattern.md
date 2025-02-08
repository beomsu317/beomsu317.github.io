---
title: "Memento Pattern"
date: "2025-02-01"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

메멘토 패턴은 객체의 상태를 저장하고, 그 상태를 복원할 수 있도록 하는 패턴이다. 객체의 이전 상태를 추적하고 복원할 때 유용하다.

## Motivation

어떤 애플리케이션에서 실행 취소(undo) 기능을 구현하려 한다. 사용자가 특정 상태에서 변경을 가했을 때, 이전 상태로 되돌릴 수 있어야 한다. 

예를 들어, 사용자가 텍스트 편집기에서 문서를 수정한 후, 실행 취소 버튼을 누르면 이전 상태로 되돌려야 한다. 하지만 직접 객체의 내부 상태를 저장하면 캡슐화를 위반하게 된다. 

이때 메멘토 패턴을 활용하면 상태 정보를 캡슐화하여 저장해 이전 상태로 쉽게 복원할 수 있다.

## Applicability

- 어떤 객체의 상태에 대한 스냅샷을 저장한 후 나중에 그 상태로 복구해야 할 때
- 상태를 얻는 데 필요한 직접적인 인터페이스를 두면 그 객체의 구현 세부사항이 노출되어 객체의 캡슐화가 깨질 때

## Structure

![memento pattern structure](images/patterns/memento_pattern_structure.png)

- `Memento`: `Originator` 객체의 상태를 캡슐화하고, 이를 저장한다. 이 저장된 상태는 다른 객체로부터 보호되어야 하므로 `Memento` 클래스에는 두 가지 인터페이스가 존재한다. 
    - 좁은 인터페이스(Narrow Interface): `Caretaker`가 메멘토를 관리할 때 사용할 수 있는 제한된 인터페이스로 `Memento`의 상태에 접근하거나 변경할 수 없다.
    - 넓은 인터페이스(Wide Interface): `Originator`가 자신의 상태를 저장하거나 복원할 때 필요한 인터페이스로, 자신의 내부 상태를 볼 수 있는 권한을 가진다.
- `Originator`: 원본 객체이다. 메멘토를 생성해 현재 객체의 내부 상태를 저장하고 메멘토를 사용해 내부 상태를 복원한다.
- `Caretaker`: `Memento` 객체를 관리하는 책임을 진다. `Caretaker`는 메멘토 상태에 직접 접근하지 않으며, 단순히 메멘토를 보관하고 관리하는 역할만 한다.

## Collaborations

- `Caretake` 객체는 `Originator` 객체에 `Memento` 객체를 요청한다. 또 요청한 시간을 저장하며, 받은 `Memento` 객체를 다시 `Originator` 객체에 돌려준다. 

    ![memento pattern diagrm](images/patterns/memento_pattern_diagrm.png)

    `Caretaker` 객체는 `Memento` 객체를 `Originator` 객체에 전달하지 않을 수도 있다. `Originator` 객체가 이전 상태로 돌아갈 필요가 없을 때는 전달할 필요가 없기 때문이다.
- `Memento` 객체는 수동적이다. `Memento` 객체를 생성한 `Originator` 객체만이 상태를 설정하고 읽어올 수 있다.

## Consequences

1. **캡슐화된 경계를 유지할 수 있다.** 

    `Originator`만이 `Memento`를 다룰 수 있기 때문에 `Memento`가 외부에 노출되지 않는다. 이는 복잡한 `Originator` 클래스의 내부 상태를 다른 객체로 분리하여 상태에 대한 정보의 캡슐화를 보장한다.
2. **`Originator` 클래스를 단순화할 수 있다.**

    상태를 별도로 관리하면 `Originator` 클래스는 간단해지고, 상태를 변경할 때마다 이를 `Originator`에게 알려줄 필요도 없다.

3. **메멘토의 사용으로 더 많은 비용이 들어갈 수 있다.**

    `Originator` 클래스가 많은 양의 정보를 저장하거나 `Memento`를 반환해야 할 때 `Memento`가 상당한 오버헤드를 가져올 수 있다. `Originator` 클래스의 상태를 저장하는 비용과 복구하는 비용이 싸지 않다면 해당 패턴이 적합하지 않을 수 있다. 

4. **좁은 인터페이스(Narrow Interface)와 넓은 인터페이스(Wide Interface)를 정의해야 한다.**
5. **메멘토를 관리하는 데 필요한 비용이 숨어있다.**

    `Caretaker`는 메멘토를 저장하는 책임은 잇지만 메멘토에 저장된 상태가 얼마나 많은지를 알 수 없기 때문에 여러 가지 문제가 발생할 수 있다. 이 문제들은 적지 않은 비용을 발생시킬 수도 있다.

## Implementation

1. **언어의 지원 여부.**

    메멘토에는 좁은 인터페이스(Narrow Interface), 넓은 인터페이스(Wide Interface) 두 종류 인터페이스가 있다. 좁은 인터페이스는 다른 객체들에게 제공할 서비스를 정의하고, 넓은 인터페이스는 `Originator` 클래스에 제공하는 서비스를 정의한다.

    C++에서는 `Originator` 클래스를 `Memento` 클래스의 `friend` 클래스로 정의하고, `Memento` 클래스의 넓은 인터페이스를 모두 `private`으로 만든다. 좁은 인터페이스에 해당하는 연산만 `public`으로 정의해야 한다.

    ```cpp
    class State;
    class Originator {
    public:
        Memento* CreateMemento();
        void SetMemento(const Memento*);
    private:
        State* _state;
    };

    class Memento {
    public:
        // internal data structures
        // narrow public interface
        virtual ~Memento();
    private:
        // private members accessible only to Originator
        friend class Originator;
        Memento();
        void SetState(State*); State* GetState();
    private:
        State* _state;
    };
    ```

    `Originator` 클래스는 `Memento` 클래스의 `friend` 클래스로 모든 연산을 사용할 수 있어 넓은 범위의 인터페이스를 제공하는 셈이다. 그러나 이외의 클래스들은 `public`으로 정의된 연산만 사용할 수 있으므로 좁은 범위의 인터페이스를 제공하는 것이 된다.
2. **점증적 상태 변경을 저장한다.**

    `Memento`가 생성되어 다시 `Originator`에 반환되면 `Memento`는 `Originator`의 내부 상태 변경 과정을 지속적으로 저장해야 한다. 이때, 모든 상태를 저장하는 것이 아니라 변경된 정보들만 추가(점증적)한다. 이로써 메모리와 성능 측면에서 비용을 절감할 수 있다.

## Sample Code

그래픽 객체를 이동 또는 취소시킬 때 메멘토 패턴을 적용해보자.

그래픽 객체를 한 위치에서 다른 위치로 이동(또는 취소)시키는 `MoveCommand` 객체를 사용한다. 그래픽 편집기는 명령어에 정의된 `Execute()` 연산을 호출해 그래픽 객체를 이동시키고, `Unexecute()` 연산을 호출해 이동을 취소한다. 

`ConstraintSolverMemento`는 메멘토 객체로 그래픽 객체가 이동하기 전의 상태를 저장한다.

명령어는 자신이 어느 주체를 이동시키고 취소했는지 저장해야 하고, 이동한 거리 및 `ConstraintSolver`의 상태를 저장할 메멘토인 `ConstraintSolverMemento` 클래스 인스턴스도 저장해야 한다.

```cpp
class Graphic;
// base class for graphical objects in the graphical editor
class MoveCommand {
public:
    MoveCommand(Graphic* target, const Point& delta);
    void Execute();
    void Unexecute();
private:
    ConstraintSolverMemento* _state;
    Point _delta;
    Graphic* _target;
};
```

`ConstraintSolver` 클래스는 객체 간 연결되어 있을 때 제약 조건(constraint)들을 처리하도록 한다. `Solve()`는 `AddConstraint()` 연산으로 등록한 제약 사항들을 처리한다.

```cpp
// singleton
class ConstraintSolver { 
public:
    static ConstraintSolver* Instance();
    void Solve();
    void AddConstraint(Graphic* startConnection, Graphic* endConnection);
    void RemoveConstraint(Graphic* startConnection, Graphic* endConnection);
    ConstraintSolverMemento* CreateMemento();
    void SetMemento(ConstraintSolverMemento*);
private:
    // nontrivial state and operations for enforcing
    // connectivity semantics
};
```

`CreateMemento()` 연산을 통해 `ConstraintSolverMemento` 클래스의 인스턴스를 만들어 `ConstraintSolver` 클래스의 상태를 저장해 둔다.

```cpp
class ConstraintSolverMemento {
public:
    virtual ~ConstraintSolverMemento();
private:
    friend class ConstraintSolver;
    ConstraintSolverMemento();

    // private constraint solver state
};
```

이렇게 정의된 인터페이스를 통해 `MoveCommand` 클래스의 멤버 함수인 `Execute()`와 `Unexecute()`를 구현할 수 있다.

```cpp
void MoveCommand::Execute() {
    ConstraintSolver* solver = ConstraintSolver::Instance();
    _state = solver->CreateMemento(); // create a memento 
    _target->Move(_delta);
    solver->Solve();
}
void MoveCommand::Unexecute() {
    ConstraintSolver* solver = ConstraintSolver::Instance();
    _target->Move(-_delta);
    solver->SetMemento(_state); // restore solver state
    solver->Solve();
}
```

`Execute()` 연산은 그래픽 객체를 이동시키기 전 `ConstraintSolverMemento`를 얻어온다. `Unexecute()` 연산은 객체를 다시 원래 위치로 되돌린다. 