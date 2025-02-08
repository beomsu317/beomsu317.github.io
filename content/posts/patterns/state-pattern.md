---
title: "State Pattern"
date: "2025-02-02"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

객체 내부 상태에 따라 객체의 행동을 변경할 수 있도록 하는 패턴이다. 이 패턴을 사용해 조건문 대신, 각 상태로 별도의 클래스로 분리하여 객체의 상태 변화에 따라 동적으로 행동을 변경할 수 있다.

## Motivation

게임 캐릭터가 여러 상태를 가질 수 있다고 하자. 예륻 들어, 캐릭터는 대기 상태, 공격 상태, 방어 상태 등 여러 상태가 있을 수 있다. 캐릭터의 행동은 현재 상태에 따라 달라지며, 상태가 바뀔 때마다 행동도 달라진다.

이 경우 상태 패턴을 도입하여 게임 캐릭터의 상태 변화에 따라 동적으로 행동을 변경할 수 있다. 

## Applicability

- 객체의 행동이 상태에 따라 달라질 수 있고, 객체의 상태에 따라 런타임 행동이 바뀌어야 할 때
- 어떤 연산에 그 객체 상태에 따라 달라지는 다중 분기 조건 처리가 너무 많이 들어 있을 때

## Structure

![state pattern structure](images/patterns/state_pattern_structure.png)

- `Context`: 상태를 관리하는 클래스이다. 현재 상태를 나타내는 객체를 유지하며, 상태를 변경학고 상태에 맞는 동작을 처리한다.
- `State`: 상태에 대한 인터페이스로, 상태별로 처리해야 할 행동을 정의한다.
- `ConcreteState`: 각 상태에서 수행할 구체적인 행동을 정의하는 클래스이다.

## Collaborations

- 상태에 따라 다른 요청을 받으면 `Context` 클래스는 현재의 `ConcreteState` 객체로 전달한다. 이 클래스의 객체는 `State` 클래스를 상속하는 서브클래스들 중 하나의 인스턴스다.
- `Context` 클래스는 실제 연산을 처리할 `State` 객체에 자신을 매개변수로 전달한다. 이로써 `State` 객체는 `Context` 클래스에 접근할 수 있게 된다.
- `Context` 클래스는 사용자가 상호작용하는 기본적인 인터페이스를 제공한다. 즉, `Context` 클래스에 현 상태를 정의하는 것이다. 사용자는 `State`를 직접 다루지 않고, `Context` 객체를 통해 상태 전환이나 행동을 요청한다.
- `Context` 클래스 또는 `ConcreteState` 서브클래스는 상태 전이 규칙을 정의한다. 이 규칙은 현재 상태에서 어떤 조건에 따라 다른 상태로 전이할지를 결정하는데, 이로 인해 상태가 변경되는 방식과 시점이 명확하게 정의된다.

## Consequences

1. **상태에 따른 행동을 국소화하며, 서로 다른 상태에 대한 행동을 별도의 객체로 관리한다.**

    상태 패턴을 사용하면 각 상태에 따른 행동을 별도의 객체로 관리할 수 있다. 이를 통해 한 상태에 종속적인 코드를 해당 상태 객체 안에서만 유지할 수 있어 코드의 응집도가 높아지고 유지보수가 쉬워진다.

2. **상태 전이를 명확하게 만든다.**

    어떤 객체가 자신의 현재 상태를 오직 내부 데이터 값으로만 정의하면, 상태 전이는 명확한 표현을 갖지 못한다. 각 상태별로 별도의 객체를 만드는 것은 상태 전이를 명확하게 해주는 결과가 된다.

3. **상태 객체는 공유될 수 있다.**

    상태는 일반적으로 행동(behavior)만을 캡슐화하는 객체이므로, 특정 상태에 대한 인스턴스를 여러 `Context` 객체에서 공유할 수 있다. 이렇게 상태 인스턴스를 공유하면 메모리 사용율을 줄이고 객체 생성 비용을 줄일 수 있다. 

## Implementation

1. **상태 전이 정의.**

    상태 패턴에서는 "누가" 상태 전이를 책임질지 명확하게 정의하지 않는다. 즉, 상태 전이를 `Context`가 담당할 수도 있고, 개별 `State` 서브클래스가 담당할 수도 있다.

    `Context`가 상태 전이를 담당하면 `State` 간 종속성이 없지만, `Context` 코드가 복잡해질 수 있다. `State` 객체가 상태 전이를 담당하면 `Context` 수정 없이 확장할 수 있으나 `State` 간 의존성이 생긴다. 

    따라서 `State` 간 전이 규칙이 자주 변경될 가능성이 있다면, `State` 객체가 상태 전이를 담당하는 방식이 더 적절하다.
2. **테이블 기반의 대안.**

    상태 패턴을 사용하지 않고 테이블을 이용해 상태 전이를 정의하는 방법도 있다. 각 상태에 대해 가능한 입력과 해당 입력이 발생했을 때 다음 상태를 테이블에 저장하는 방식이다. 이 방식을 사용하면 코드 대신 테이블 데이터를 수정하는 것만으로 상태 전이를 변경할 수 있다.

    테이블 기반 방식은 상태 전이에 초점을 맞춘 방법으로, 규칙적인 상태 전이가 필요한 경우 유리하다.
3. **상태 객체의 생성과 소멸.**

    상태 객체를 구현할 때 다음 두 가지를 고려한다.
    
    1. 상태 객체를 필요할 때만 생성하고 필요하지 않다면 제거
    2. 필요하기 전 미리 만들어두고 제거하지 않고 유지
    
    상태 변화가 수시로 일어날 때는 두 번째가 좋은 방법이다. 그러나 `Context` 클래스가 언제나 모든 상태에 대한 참조자를 계속 관리해야 하는 부담이 생긴다.

4. **동적 상속을 이용하는 방법.**

    어떤 특정 요청에 따라 행동을 바꾸려면, 객체가 런타임에 자신의 클래스를 변경하면 해결되지 않을까? 
    
    이런 접근 방식은 직관적이지만, 대부분의 객체지향 언어에서는 불가능하다.

## Sample Code

상태 패턴을 TCP 연결에 적용해보자. 

`TCPConnection` 클래스는 사용자가 TCP 연결에 대한 요청할 수 있는 인터페이스를 제공하며, 내부적으로 현재 상태를 나타내는 `TCPState` 객체를 관리한다.

```cpp
class TCPOctetStream;
class TCPState;
class TCPConnection {
public:
    TCPConnection() ;

    void ActiveOpen();
    void PassiveOpen();
    void Close();
    void Send();
    void Acknowledge();
    void Synchronize();

    void ProcessOctet(TCPOctetStream*);
private:
    friend class TCPState;
    void ChangeState(TCPState*);
private:
    TCPState* _state;
};
```

`TCPState` 클래스와 그 서브클래스들은 각 상태에 맞는 동작과 상태 전이 규칙을 캡슐화하여, `TCPConnection`의 상태 변경을 자체적으로 처리할 수 있도록 한다.

```cpp
class TCPState {
public:
    virtual void Transmit(TCPConnection*, TCPOctetStream*);
    virtual void ActiveOpen(TCPConnection*);
    virtual void PassiveOpen(TCPConnection*);
    virtual void Close(TCPConnection*);
    virtual void Synchronize(TCPConnection*);
    virtual void Acknowledge(TCPConnection*);
    virtual void Send(TCPConnection*);
protected:
    void ChangeState(TCPConnection*, TCPState*);
};
```

`TCPConnection`은 모든 상태 관련된 요청을 `TCPState`에 전달한다. `TCPConnection`은 자신의 멤버 데이터인 `_state`를 변경하는 연산을 제공한다. 

```cpp
TCPConnection::TCPConnection() {
    _state = TCPClosed::Instance();
}

void TCPConnection::ChangeState(TCPState* s) {
    _state = s;
}

void TCPConnection::ActiveOpen() {
    _state->ActiveOpen(this);
}

void TCPConnection::PassiveOpen() {
    _state->PassiveOpen(this);
}

void TCPConnection::Close() {
    _state->Close(this);
}

void TCPConnection::Acknowledge() {
    _state->Acknowledge(this);
}

void TCPConnection::Synchronize() {
    _state->Synchronize(this);
}
```

`TCPState` 클래스는 자신에게 전달된 모든 요청에 대한 기본 행동을 구현한 부모 클래스이다. `ChangeState()` 연산을 통해 `TCPConection` 클래스의 상태를 변경한다. `TCPState` 클래스는 `TCPConnection` 클래스의 `friend`로 정의되어 `TCPConnection` 클래스의 연산을 사용할 수 있다.

```cpp
void TCPState::Transmit(TCPConnection*, TCPOctetStream*) { }
void TCPState::ActiveOpen(TCPConnection*) { }
void TCPState::PassiveOpen(TCPConnection*) { }
void TCPState::Close(TCPConnection*) { }
void TCPState::Synchronize(TCPConnection*) { }
void TCPState::ChangeState(TCPConnection* t, TCPState* s) {
    t->ChangeState(s);
}
```

`TCPState` 서브클래스는 멤버 변수를 정의하지 않는다. 내부 상태가 없기 때문에 `TCPState` 서브클래스의 인스턴스들(예: `TCPEstablished`, `TCPListen` 등)은 공유가 가능하므로, 각 서브클래스의 인스턴스는 하나만 있으면 된다.

각 상태의 유일한 인스턴스는 `Instance()` 연산에 의해 얻어진다.

```cpp
TCPClosed::ActiveOpen(TCPConnection* t) {
    // send SYN, receive SYN, ACK, etc.
    ChangeState(t, TCPEstablished::Instance()) ;
}

void TCPClosed::PassiveOpen(TCPConnection* t) {
    ChangeState(t, TCPListen::Instance());
}

void TCPEstablished::Close(TCPConnection* t) {
    // send PIN, receive ACK of FIN
    ChangeState(t, TCPListen::Instance());
}

void TCPEstablished::Transmit(TCPConnection* t, TCPOctetStream* o) {
    t->ProcessOctet(o);
}

void TCPListen::Send(TCPConnection* t) {
    // send SYN, receive SYN, ACK, etc.
    ChangeState(t, TCPEstablished::Instance());
}
```

상태별 처리를 수행한 후, 각 연산은 `ChangeState()` 연산을 호출해 `TCPConnection` 클래스의 상태를 변경한다. `TCPConnection` 자체는 TCP 연결 프로토콜이므로 `TCPState`의 서브클래스들이 각 상태 전이를 정의하고 처리하도록 한다.