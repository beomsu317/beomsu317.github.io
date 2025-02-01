---
title: "Iterator Pattern"
date: "2025-02-01"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

내부 구조를 노출하지 않으면서 어떤 집합 객체에 속한 원소들을 순차적으로 접근할 수 있는 방법을 제공한다.

## Motivation

여러 종류의 자료구조(예: 배열, 리스트)에 대해 그 내부 요소들을 하나씩 순차적으로 처리해야 하는 상황에서, 이 요소들을 순차적으로 접근할 수 있는 공통의 방법을 제공하고 싶다고 하자.

이터레이터 패턴을 사용하면 집합체의 내부 구조를 몰라도, 집합체의 모든 요소에 접근할 수 있게 해준다.

## Applicability

- 객체 내부 표현 방식을 모르고도 집합 객체의 각 원소들에 접근하고 싶을 때
- 집합 객체를 순회하는 다양한 방법을 지원하고 싶을 때
- 서로 다른 집합 객체 구조에 대해서도 동일한 방법으로 순회하고 싶을 때

## Structure

![iterator pattern structure](images/iterator_pattern_structure.png)

- `Iterator`: 원소를 접근하고 순회하는 데 필요한 인터페이스를 제공한다.
- `ConcreteIterator`: `Iterator`에 정의된 인터페이스를 구현하는 클래스로, 순회 과정 중 집합 객체 내에서 현재 위치를 기억한다.
- `Aggregate`: `Iterator` 객체를 생성하는 인터페이스를 정의한다.
- `ConcreteAggregate`: 해당하는 `ConcreteIterator`의 인스턴스를 반환하는 `Iterator` 생성 인터페이스를 구현한다.

## Collaborations

- `ConcreteIterator`는 집합 객체 내 현재 객체를 계속 추적으로 다음번 방문할 객체을 결정한다.

## Consequences

1. **집합 객체의 다양한 순회 방법을 제공한다.** 

    구조가 복잡한 집합 객체는 다양한 방법으로 순회할 수 있다.
2. **`Iterator`는 `Aggregate` 클래스의 인터페이스를 단순화한다.**

    `Iterator`의 순회 인터페이스는 `Aggregate` 클래스에 정의한 자신과 비슷한 인터페이스를 없애 `Aggregate` 인터페이스를 단순화할 수 있다.
3. **집합 객체에 따라 하나 이상의 순회 방법이 제공될 수 있다.**

    각 `Iterator`마다 자신의 순회 상태가 있으므로 하나의 집합 객체를 한 번에 여러 번 순회할 수 있다.

## Implementation

1. **반복 제어.**

    - 외부 반복자(External Iterator): 사용자가 반복을 제어한다. 즉, 외부 반복자는 다음번 원소를 명시적으로 반복자에게 요청해야 하고 반복의 흐름을 직접 제어한다. 
    - 내부 반복자(Internal Iterator): 반복자 자신이 제어를 담당한다. 사용자는 반복자에세 처리할 작업을 넘기고, 반복자는 그 작업 요소들에 자동으로 적용한다.

2. **순회 알고리즘 정의.**

    `Aggregate` 클래스에 순회 알고리즘을 정의하고 `Iterator`는 순회의 상태만 저장할 수도 있다. 이렇게 구현된 반복자를 `Cursor`라 한다. 단순히 집합 구조 내 현재 위치만 가리키는 것이다.

    `Iterator`가 순회 알고리즘을 책임진다면 같은 집합 객체에 대해 다른 순회 알고리즘을 구현하는 것이 쉬워진다. 그러나 반복자가 집합 객체에 정의된 `private` 변수들에 접근해야 할 필요가 있다. 이 경우, 집합체의 내부 데이터 구조에 대한 캡슐화를 위배할 수 있다.
3. **견고한 반복자.**

    만약 순회 중 값이 추가되거나 삭제되면 동일한 원소에 두 번 접근하거나, 하나를 빼먹고 지나갈 수 있다. 이런 불상사를 방지하는 한 가지 방법은 집합 객체를 복사해 놓고 그 복사본을 순회하는 것이다. 그러나 이는 추가 비용이 많이 발생한다. 

    견고한 반복자가 되려면 집합 객체가 수정될 때 해당 수정 사항을 반복자에 반영하여, 수정된 집합 객체를 순회하는 데 문제가 없도록 해야 한다.

4. **추가적으로 필요한 반복자 연산.**

    `Iterator` 클래스에 필요한 최소한의 연산들은 `First()`, `Next()`, `IsDone()`, `CurrentItem()`이다. 이외에도 몇 가지 연산을 추가하는 것이 유용할 수 있다. 순서가 정해진 객체라면 `Previous()` 연산을 통해 현재 반복자 위치를 앞으로 이동시킬 수 있다. 인덱스를 갖는 객체라면 `SkipTo()` 연산으로 어떤 조건에 일치하는 객체로 반복자를 바로 이동시킬 수 있다.
5. **C++에서 다형성을 지닌 반복자를 이용하는 방법.**

    다형적인 반복자는 런타임에 추가적인 비용을 지불해야 한다. 그러므로 다형성은 필요할 때만 사용하는 것이 좋다. 
6. **반복자에는 특수한 접근 권한이 있다.**

    반복자는 그 반복자를 생성한 집합 객체의 확장으로 볼 수 있는데, 이렇게 되면 반복자와 집합 객체 간 결합도가 매우 커진다. 이런 관계를 C++에서 구현한다면, 집합 객체를 정의할 때 반복자를 그 집합 구조의 `friend`로 정의할 수 있다. 그러면 집합 객체에 접근하는 데 필요한 연산들을 정의할 필요가 없어진다. 

    그러나 이런 접근을 부여하면 새로운 순회 방법을 정의하기 어렵다. `friend`를 하나 더 추가하는 데 집합 객체 인터페이스의 변경이 필요하기 때문이다.

    이런 문제를 해결하기 위해 `friend`를 선언한 대신, 집합 객체에 정의된 멤버 변수 중에서 중요하지만 공개할 수 없는 멤버 변수에 접근하는 연산을 `Iterator` 클래스 안에 `protect`로 정의할 수 있다. 이렇게 하면 집합 객체에 직접 접근할 수 있는 권한을 얻고, 동시에 집합 객체와 반복자 간 결합도는 낮출 수 있다.
7. **복합체를 위한 반복자.**

    복합체(Composite) 구조에서 반복자의 구현은 재귀적 합성(Recursive Composition) 구조에 특화된 문제다. 여러 단계에 걸쳐 중첩된 집합체를 처리해야 하기 때문에, 외부 반복자 방식으로는 순회가 어려울 수 있다.

    이 문제를 해결하기 위해 내부 반복자 방식을 사용하거나 복합체 패턴과 이터레이터 패턴을 결합하여 구현할 수 있다. 이때 주로 커서 방식의 반복자를 사용해 노드에 대한 정보를 관리하고, 각 노드 간 이동을 처리한다.
8. **널 반복자.**

    `NullIterator`는 항상 순회 시 끝나는 반복자로 정의된다. `NullIterator`는 `IsDone()` 연산으로 항상 참을 반환한다.

## Sample Code

`List` 클래스의 `Iterator` 구현을 보자.

`List` 클래스는 자료를 저장하고, 리스트 조작 기능을 제공한다. 

```cpp
template <class Item> 
class List {
public:
    List(long size = DEFAULT_LIST_CAPACITY);

    long Count() const;
    Item& Get(long index) const;
    // ...
};
```

`Iterator` 클래스는 기본적인 인터페이스 역할을 한다. `Iterator` 클래스는 `List` 클래스와 독립적으로 순회 기능만 제공할 수 있다.

```cpp
template <class Item> 
class Iterator {
public:
    virtual void First() = 0;
    virtual void Next() = 0;
    virtual bool IsDoneO const = 0;
    virtual Item CurrentItem() const = 0;
protected:
    Iterator();
};
```

`ListIterator`는 `Iterator`의 서브클래스로 정의한다.

```cpp
template <class Item>
class ListIterator : public Iterator<Item> {
public:
    ListIterator(const List<Item>* aList);
    virtual void First();
    virtual void Next();
    virtual bool IsDone() const;
    virtual Item CurrentItem() const;
private:
    const List<Item>* _list;
    long _current;
};
```

`ListIterator`의 구현은 `List`를 저장하고 이를 `_current` 인덱스로 관리한다.

```cpp
template <class Item>
ListIterator<Item>::ListIterator (const List<Item>* aList)
    : _list(aList), _current(0) {
}
```

`First()` 연산은 `Iterator`가 첫 번째 원소를 가리키게 한다. 

```cpp
template <class Item>
void ListIterator<Item>::First() {
    _current = 0;
}
```

`Next()` 연산은 `_current`를 다음 원소로 이동시킨다.

```cpp
template <class Item>
void ListIterator<Item>::Next() {
    _current++;
}
```

리스트 끝에 도달했는지 `IsDone()`을 통해 확인한다.

```cpp
template <class Item>
bool ListIterator<Item>::IsDone() const {
    return _current >= _list->Count();
}
```

`CurrentItem()`은 현재 인덱스의 원소를 반환한다. 반복이 이미 종료된 상태라면 `IteratorOutOfBounds` 예외를 발생시킨다.

```cpp
template <class Item>
Item ListIterator<ltem>::CurrentItem() const {
    if (IsDone()) {
        throw IteratorOutOfBounds;
    }
    return _list->Get(_current);
}
```

`ReverseListIterator`의 `First()` 연산은 `_current`가 리스트의 끝을 가리키고, `Next()` 연산은 `_current`를 감소시키는 것 외에 다른 부분은 동일하다.

`Employee` 리스트를 만들고 포함된 모든 사원을 출력하려면 다음과 같이 사용할 수 있다.

```cpp
void PrintEmployees(Iterator<Employee*>& i) {
    for (i.First(); !i.IsDone(); i.Next()) {
        i.CurrentItem()->Print();
    }
}
```

`Iterator`의 진행 방향을 순방향 및 역방향이 다 가능하도록 정의했기 때문에 다음과 같이 사용할 수 있다.

```cpp
List<Employee*>* employees;
// ...
ListIterator<Employee*> forward(employees);
ReverseListIterator<Employee*> backward(employees);

PrintEmployees(forward);
PrintEmployees(backward);
```

### 리스트 구현이 표준에서 벗어나는 상황 방지

`SkipList` 클래스는 `List`의 서브클래스로 `SkipListIterator` 클래스를 제공해야 한다. `SkipListIterator` 클래스는 효율적으로 반복하기 위해 인덱스를 하나 더 정의했다. 그러나  `SkipListIterator` 클래스는 `Iterator`의 인터페이스를 만족하므로, `PrintEmployee()` 연산은 수정할 필요가 없다.

```cpp
SkipList<Employee*>* employees;
// ...
SkipListIterator<Employee*> iterator(employees);
PrintEmployees(iterator);
```

이런 방식도 유효하지만 이렇게 `List` 클래스에 대한 특정 구현을 끼워 맞추기보다, `List` 인터페이스를 표준화한 `AbstractList` 클래스를 만드는 것이 바람직하다. 

다형적 반복을 지원하기 위해 `AbstractList` 클래스는 팩토리 메서드인 `CreateIterator()`를 정의해야 한다.  

```cpp
template <class Item> 
class AbstractList {
public:
    virtual Iterator<Item>* CreateIterator() const = 0;
    // ...
};
```

이제 어떤 특정 표현과 독립적으로 사원들의 정보를 출력하는 코드를 작성할 수 있다.

```cpp
//we know only that we have an AbstractList
AbstractList<Employee*>* employees;
// ...
Iterator<Employee*>* iterator = employees->CreateIterator();
PrintEmployees(*iterator);
delete iterator;
```

### Iterator 삭제

`CreateIterator()`는 새로 할당된 `Iterator` 객체를 반환한다. 그러므로 이 객체를 삭제해야 하는 쪽은 사용자다. 더 편하게 반복자를 프로그래밍할 수 있도록 `Iterator`에 대한 프록시인 `IteratorPtr`을 제공하려 한다. `IteratorPtr`은 유효범위를 벗어날 때 `Iterator` 객체를 메모리에서 삭제하는 일을 맡는다.

`IteratorPtr`은 항상 스택에 할당된다. 소멸자 호출은 C++에서 자동으로 책임(RAII)지므로 실제 `Iterator`를 없애는 결과를 만들 수 있다.

`IteratorPtr`이 `Iterator`에 대한 포인터처럼 취급될 수 있도록 `operator->`, `operator*` 연산을 재정의한다. `IteratorPtr`의 멤버는 모두 인라인 함수로 구현되어 실행 오버헤드를 일으키지 않는다.

```cpp
template <class Item> 
class IteratorPtr {
public:
    IteratorPtr(Iterator<Item>* i): _i(i) { }
    ~IteratorPtr() { delete _i; }
    Iterator<Item>* operator->() { return _i; }
    Iterator<Item>& operator*() { return *_i; }
private:
    // disallow copy and assignment to avoid
    // multiple deletions of _i:
    IteratorPtr(const IteratorPtr&);
    IteratorPtr& operator=(const IteratorPtr&);
private:
    Iterator<Item>* _i;
};
```

`IteratorPtr` 클래스는 다음과 같이 사원 정보를 출력하는 코드를 단순화시킨다.

```cpp
AbstractList<Employee*>* employees;
// ...
IteratorPtr<Employee*> iterator(employees->CreateIterator());
PrintEmployees(*iterator);
```

### 내부 ListIterator

내부 반복자 역할을 하는 `ListIterator` 클래스를 반복 제어를 직접 수행하며, 리스트의 각 원소에서 특정 연산을 실행하는 역할을 한다. 여기서 각 원소에서 수행할 연산을 어떻게 전달한 것인지에 대한 문제가 발생한다.

연산을 전달하는 두 가지 방법이 있다. **함수 포인터 사용**하거나 **상속을 사용**하는 방법이다. 

그러나 이 두 방법 모두 완전하지 않다. 가끔 반복 도중 상태를 저장하고 싶을 때도 있는데, 이는 함수만으로는 충분하지 않다. 즉, 상태를 저장하기 위해 정적 변수를 사용해야 한다. `Iterator`의 서브클래스는 상태를 저장할 수 있는 변수를 제공할 수 있지만, 모든 경우에 대한 순회 방법마다 서브클래스를 만드는 것 또한 부담스런 작업이다.

상속을 사용하는 방법을 보자.`ListTraverser` 클래스에 내부 반복자를 만든다.

```cpp
template <class Item> 
class ListTraverser {
public:
    ListTraverser(List<Item>* aList);
    bool Traverse();
protected:
    virtual bool ProcessItem(const Item&) = 0;
private:
    ListIterator<Item> _iterator;
};
```

`ListTraverser` 클래스는 `List` 클래스의 인스턴스를 매개변수로 취하며, 내부적으로 `ListIterator` 클래스를 이용해 순회를 처리한다. `Traverse()` 연산으로 순회가 시작되고, 각 항목을 얻고 싶으면 `ProcessItem()`을 이용한다. 원소가 더는 없으면 `ProcessItem()` 연산은 `false`를 반환한다. `Traverse()` 연산은 순회를 잘 끝마쳤는지 여부를 반환한다.

```cpp
template <class Item> 
ListTraverser<Item>::ListTraverser(List<Item>* aList) : _iterator(aList) { }

template <class Item>
bool ListTraverser<Item>::Traverse() {
    bool result = false;
    for (_iterator.First();!_iterator.IsDone(); _iterator.Next()){
        result = ProcessItem(_iterator.CurrentItem());
        if (result == false) {
            break;
        }
    }
    return result;
}
```

사원 리스트에서 10명의 사원을 출력하는 예제에 `ListTraverser` 클래스를 사용해보자. 이를 처리하려면 `ProcessItem()`을 재정의하기 위해서 `ListTraverser` 클래스의 서브클래스를 만들어야 한다. `_count` 인스턴스 변수를 이용해 출력한 사원 수를 누적한다.

```cpp
class PrintNEmployees : public ListTraverser<Employee*> {
public:
    PrintNEmployees(List<Employee*>* aList, int n) : ListTraverser<Employee*>(aList),
    _total(n), _count(0) { }
protected:
    bool ProcessItem(Employee* const&);
private:
    int _total;
    int _count;
};

bool PrintNEmployees::ProcessItem(Employee* const& e) {
    _count++;
    e->Print();
    return _count < _total;
}
```

이제 `PrintNEmployees` 클래스가 리스트에 저장한 10명의 사원을 출력해보자.

```cpp
List<Employee*>* employees;
// ...
PrintNEmployees pa(employees, 10)
pa.Traverse();
```

사용자는 반복을 위해 `for`나 `while`을 사용하지 않아도 된다. 반복을 위해 작성한 코드 그대로 재사용할 수 있는 장점이 있지만, 새로운 클래스를 하나 더 정의해야 하는 단점도 있다.

```cpp
ListIterator<Employee*> i(employees);
int count = 0;
for (i.First(); !i.IsDone(); i.Next()) {
    count++;
    i.CurrentItem()->Print();
    if (count >= 10) {
        break;
    }
}
```

내부 반복자는 서로 다른 반복 방법을 캡슐화한다. 예를 들어, `FilteringListTraverser` 클래스는 조건을 만족하는 것만 반복하도록 할 수 있다.

```cpp
template <class Item>
class FilteringListTraverser {
public:
    FilteringListTraverser(List<Item>* aList);
    bool Traverse();
protected:
    virtual bool ProcessItem(const Item&) = 0;
    virtual bool TestItem(const Item&) = 0;
private:
    ListIterator<Item> _iterator;
};
```

이 인터페이스는 `ListTraverser` 인터페이스와 동일하지만, `TestItem()` 함수를 추가해 테스트를 수행하도록 한다. 서브클래스는 테스트 방법을 재정의할 수 있다. 

```cpp
template <class Item>
void FilteringListTraverser<Item>::Traverse() {
    bool result = false;

    for (_iterator.First();!_iterator.IsDone(); _iterator.Next()){
        if (Testltem(_iterator.CurrentItem())) {
            result = ProcessItem(_iterator.CurrentItem());
            if (result == false) {
                break;
            }
        }
    }
    return result;
}
```