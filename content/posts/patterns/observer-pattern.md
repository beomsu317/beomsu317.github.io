---
title: "Observer Pattern"
date: "2025-02-01"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

객체의 상태 변화가 잇을 때, 그 객체에 의존하는 다른 객체들에게 자동으로 알림을 보내고, 상태를 업데이트하는 패턴이다. 이 패턴은 관찰자(observer) 객체들이 주체(subject) 객체의 상태 변화를 관찰하고, 주체 객체의 상태가 변할 때마다 그에 맞는 행동을 취한다.

## Motivation

여러 명의 구독자가 뉴스레터를 구독한다고 하자. 뉴스레터는 주제(subject) 역할을 하고, 구독자는 관찰자(observer) 역할을 한다. 뉴스레터의 내용이 변경될 때마다 구독자에게 알림을 보내야 한다.

이때 옵저버 패턴을 사용하면 새롭게 변경된 내용을 구독자에게 전달할 수 있다.

## Applicability

- 주체 객체와 관찰자 객체를 서로 독립적으로 만들고 이들 간 관계를 느슨하게 유지(캡슐화)해야 할 때 
- 주체 객체에 가해진 변경으로 관찰자 객체를 변경해야 되지만, 그 관찰자들이 얼마나 많은지 몰라도 될 때
- 주체 객체가 관찰자 객체에 자신의 변화를 통보해야 하는데, 그 변화에 관심있어 하는 관찰자 객체들이 누구인지에 대한 가정 없이도 통보가 되어야 할 때

## Structure

![observer pattern structure](images/patterns/observer_pattern_structure.png)

- `Subject`: 관찰자 객체들을 관리한다. 주체는 관찰자 객체를 추가하거나 삭제하는 데 필요한 인터페이스를 제공한다.
- `Observer`: 주체에 생긴 변화에 관심 있는 객체를 갱신하는 데 필요한 인터페이스를 정의한다. 
- `ConcreteSubject`: `ConcreteObserver` 객체에게 알려주어야 하는 상태를 저장한다. 또한 이 상태가 변경될 때 관찰자에게 변경을 통보한다.
- `ConcreteObserver`: `ConcreteSubject` 객체에 대한 참조자를 보유하고 있다. 이를 통해 `ConcreteSubject` 객체의 상태 변화를 관찰하고, 주체에 대한 상태에 따라 자신의 상태도 갱신하는 역할을 한다. 이때 두 객체의 상태가 일관되게 유지(동기화)되어야 한다.

## Collaborations

- `ConcreteSubject`는 `Observer`에게 상태 변경을 통보한다.
- `ConcreteSubject`에서 변경이 통보된 후, `ConcreteObserver`는 필요한 정보를 `Subject`에 질의하여 얻어온다. 이 정보를 이용해 주체의 상태와 자신의 상태를 동기화한다. 

![observer pattern structure](images/patterns/observer_pattern_structure.png)

## Consequences

1. **`Subject`와 `Observer` 클래스 간 추상적인 결합도만이 존재한다.**

    주체가 아는 것은 관찰자의 리스트 뿐이다. 이 관찰자 들은 `Observer` 클래스에 정의된 인터페이스를 따른다. 그러나 주체는 어떤 `ConcreteObserver` 클래스가 있는지에 대해 알 필요가 없다. 따라서 주체와 관찰자 간 결합은 추상적이며, 그 조차도 최소화되어 있다. 
2. **브로드캐스트 방식의 교류를 가능하게 한다.**

    주체가 보내는 통보는 구체적인 수신자를 지정할 필요가 없다. 통보는 주체의 정보를 원하는 모든 객체에 자동으로 전달되어야 한다. 
3. **예측하지 못한 정보를 갱신한다.**

    주체의 상태가 변경되었을 때, 그 변경이 어떤 속성에 해당하는지 명시적으로 알리지 않으면, 관찰자는 불필요한 갱신을 할 수 있다.

## Implementation

1. **주체와 그것의 관찰자를 대응시킨다.**

    자신이 통보해주어야 하는 관찰자들을 주체가 지속적으로 관리하는 가장 쉬운 방법은 관찰자에 대한 참조자를 저장하는 것이다.
2. **하나 이상의 주체를 관찰한다.**

    어떨 때는 하나 이상의 주체에 종속된 관찰자가 있을 수 있다. 관찰자가 어떤 주체에서 통보되는지 알아야 한다면 `Update()` 연산을 확장할 필요가 있다.
3. **갱신 촉발자(trigger).**

    주체와 관찰자는 동기화를 위해 통보 메커니즘에 의존할 수밖에 없다. 여기에는 두 가지 방법이 있다.

    - `Subject` 클래스의 상태 변경 후 상태를 지정하는 연산에서 `Notify()`를 호출한다. 주체가 정의한 `Notify()`를 사용자가 호출할 필요가 없지만, 계속되는 연산의 수행으로 여러 번 수정해야 하므로 비효율적이다.
    - 사용자가 적시에 `Notify()`를 호출하는 책임을 지도록 한다. 따라서 사용자가 일련의 상태 변경이 될 때까지 갱신을 미룰 수 있다. 때문에 중간의 불필요한 수정이 일어나지 않는다. 단점은 사용자에게 수정하게 하는 추가적 행동을 요청해야 한다는 것이다. 

4. **삭제한 주체에 대한 무효(dangling) 참조자를 계속 유지할 때가 있다.**

    주체의 삭제로 관찰자가 무효한 참조자를 갖도록 하면 안 된다. 이를 피하는 한 가지 방법은 주체가 관찰자에게 자신이 삭제되었음을 통보하는 것이다. 

5. **통보 전 주체의 상태가 자체 일관성을 갖추도록 만들어야 한다.**

    관찰자는 자신의 상태를 변경하기 위해 주체에서 현재 상태를 질의한다. 이러한 자체 일관성(self-consistency) 규칙은 서브클래스에 정의한 연산이 상속한 연산을 호출하게 되면 뜻하지 않게 깨지기 쉽다. 

    예를 들어, 슈퍼클래스 연산을 먼저 호출하고 자신의 상태를 바꾸게 되는데, 이 경우 슈퍼클래스 연산으로 통보가 되고, 자신이 변경한 상태는 반영되지 않아 문제가 발생할 수 있다.

    ```cpp
    void MySubject::Operation(int newValue) {
        BaseClassSubject::Operation(newValue);
        // trigger notification
        _myInstVar += newValue;
        // update subclass state (too late!)
    }
    ```

    이 문제를 피하기 위해 `Subject` 클래스에 템플릿 메서드를 정의하고 이 메서드로 통보를 처리할 수 있다. 재정의할 서브클래스에서 오버라이드 할 기본 연산을 정의하고 템플릿 메서드의 맨 마지막 연산에 실제 `Notify()` 연산을 수행한다. 이렇게 하면 `Subject` 연산을 서브클래스에서 오버라이드 할 때 그 객체는 일관성을 유지할 수 있다.

6. **관찰자 별 갱신 프로토콜을 피한다(푸시 & 풀 모델).**

    - 푸시 모델(Push Model): 주체가 변경된 정보를 관찰자에게 직접 전달한다. 관찰자는 받은 정보를 즉시 처리할 수 있지만 주체와 관찰자 간 결합도가 높고, 불필요한 정보가 전달될 수 있다.
    - 풀 모델(Pull Model): 관찰자가 주체의 상태를 필요할 때 요청한다. 주체와 관찰자 간 결합도가 낮고, 불필요한 정보가 전달되지는 않지만, 관찰자는 상태를 요청해야 하므로 효율성이 떨어질 수 있다.

7. **자신이 관심있는 변경이 무엇인지 명확하게 지정한다.**

    `Subject` 클래스에 자신이 관심 있는 이벤트에 대한 관찰자를 등록하는 인터페이스를 정의하여 갱신 과정을 조금 더 효율화할 수 있다. 이를 지원하기 위해 `Subject` 객체는 양상(aspect)이라는 개념을 사용할 수 있다. 주체는 다음 연산을 이용해 관찰자를 등록한다.

    ```cpp
    void Subject::Attach(Observer*, Aspects interest);
    ```

    `interest` 매개변수는 관심을 갖고 있는 이벤트를 의미한다. 실제로 통보가 일어날 때, 주체는 `Update()` 연산의 매개변수로 관심 있는 내용을 전달한다.

    ```cpp
    void Observer::Update(Subject*, Aspect& interest);
    ```

8. **복잡한 갱신의 의미 구조를 캡슐화한다.**

    주체와 관찰자 간 일어나는 관련성이 복잡하다면, 이들 관련성을 관리하는 별도의 객체(중재자)를 만들 수 있다. 이 객체의 목적은 관찰자가 처리해야 하는 주체의 변경 처리를 최소화하는 것이다. 이 객체는 다음의 세 가지를 책임져야 한다.

    1. 주체와 관찰자를 매핑하고 이를 유지하는 인터페이스를 정의한다.
    2. 특별한 갱신 전략을 정의한다. 이 전략은 중복 갱신을 방지하고, 불필요한 갱신을 최소화한다.
    3. 주체의 상태가 변경될 때, 그에 따른 모든 독립적 관찰자들에게 변경 사항을 통보해야 한다.

## Sample Code

추상 클래스로 정의한 `Observer` 인터페이스는 다음과 같다.

```cpp
class Subject;
class Observer {
public:
    virtual ~Observer();
    virtual void Update(Subject* theChangedSubject) = 0;
protected:
    Observer();
};
```

여러 개의 주체가 각각의 관찰자를 가질 수 있도록 만든 구현이다. 관찰자가 여러 개의 주체를 관찰하고 있을 때, 변경된 주체의 인스턴스가 `Update()` 연산에 전달되어 어떤 주체가 변경되어야 하는지 관찰자가 결정할 수 있다.

비슷하게 `Subject` 인터페이스를 정의한다.

```cpp
class Subject {
public:
    virtual ~Subject();
    virtual void Attach(Observer*);
    virtual void Detach(Observer*);
    virtual void Notify();
protected:
    Subject();
private:
    List<Observer*> *_observers;
};

void Subject::Attach(Observer* o) {
    _observers->Append(o);
}

void Subject::Detach(Observer* o) {
    _observers->Remove(o);
}

void Subject::Notify() {
    ListIterator<Observer*> i(_observers);
    for (i.First (); ! i. IsDone (); i.Next()) {
        i.CurrentItem()->Update(this);
    }
}
```

`ClockTimer` 클래스는 일정을 기억하고 관리하는 클래스로 `Subject`를 상속한다. 매초마다 관찰자에게 시간 변경을 알려준다. 

```cpp
class ClockTimer : public Subject {
public:
    ClockTimer();
    virtual int GetHour();
    virtual int GetMinute();
    virtual int GetSecond();

    void Tick();
};
```

`Tick()` 연산은 정의된 간격에 따라 내부 타이머로 호출되는 연산이다. `Tick()` 연산은 `ClockTimer` 클래스의 내부 상태를 변경하고, `Notify()` 연산을 호출해 변경을 관찰하는 `Observer`에게 변경 사실을 알려준다.

```cpp
void ClockTimer::Tick() {
    // update internal time-keeping state
    // ...
    Notify();
}
```

이제 시간을 표시하는 `DigitalClock` 클래스를 정의한다. `Widget` 클래스의 그래픽 기능을 상속받고, `Observer` 클래스를 상속받아 관찰자의 역할을 한다.

```cpp
class DigitalClock: public Widget, public Observer {
public:
    DigitalClock(ClockTimer*);
    virtual ~DigitalClock();
    virtual void Update(Subject*);

    // overrides Observer operation
    virtual void Draw();

    // overrides Widget operation;
    // defines how to draw the digital clock
private:
    ClockTimer* _subject;
};

DigitalClock::DigitalClock(ClockTimer* s) {
    _subject = s;
    _subject->Attach(this);
}

DigitalClock::~DigitalClock() {
    _subject->Detach(this);
}
```

`Update()` 연산은 시계 그림을 그리기 전, 통지하는 주체가 그 시계의 주체인지를 확인해야 한다.

```cpp
void DigitalClock::Update(Subject* theChangedSubject) {
    if (theChangedSubject == _subject) {
        Draw();
    }
}

void DigitalClock::Draw() {
    // get the new values from the subject
    int hour = _subject->GetHour();
    int minute = _subject->GetMinute();
    //etc.

    // draw the digital clock
}
```

`AnalogClock` 클래스도 동일한 방법으로 정의될 수 있다.

```cpp
class AnalogClock : public Widget, public Observer {
public:
    AnalogClock(ClockTimer*);
    virtual void Update(Subject*);
    virtual void Draw();
    // ...
}
```

`AnalogClock`과 `DigitalClock` 코드를 생성하는 방법은 다음과 같다.

```cpp
ClockTimer* timer = new ClockTimer;
AnalogClock* analogClock = new AnalogClock(timer);
DigitalClock* digitalClock = new DigitalClock(timer);
```

`timer`의 시간이 바뀔 때마다 두 개의 시계가 변경되어 다시 출력된다.

