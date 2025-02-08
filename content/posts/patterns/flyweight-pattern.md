---
title: "Flyweight Pattern"
date: "2025-01-30"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "structural pattern"]
---

공유를 통해 많은 수의 세밀한(fine-grained) 객체들을 효과적으로 지원한다.

## Motivation

게임에서 각 객체가 같은 속성을 가지지만 다수의 인스턴스를 만들 경우, 이로 인해 메모리 낭비와 성능 저하가 발생될 수 있다. 예를 들어, 여러 객체가 같은 색상, 크기, 형태 등 공통된 속성을 가질 때, 이를 매번 새로 생성하는 것은 비효율적이다.

Flyweight 패턴을 적용하면 공유 가능한 부분을 외부에서 관리하고, 변경 가능한 부분만 각 객체에 보관하여 메모리 사용을 최적화할 수 있다.

## Applicability

- 애플리케이션이 대량의 객체를 사용해야 할 때
- 객체의 수가 너무 많아져 저장 비용이 높아질 때
- 대부분의 객체 상태를 부가적인 것으로 만들 수 있을 때
- 부가적인 속성들을 제거하면 객체들이 동일한 특성을 가질 때
- 애플리케이션이 객체의 정체성에 의존하지 않을 때

## Structure

![flyweight pattern structure](images/patterns/flyweight_pattern_structure.png)

`Flyweight` 객체의 공유 방법은 다음과 같다.

![sharing flyweight object](images/patterns/sharing_flyweight_object.png)


- `Flyweight`: `Flyweight` 인터페이스를 정의한다. 이 인터페이스는 부가적인 상태를 다룰 수 있어야 한다. 즉, 객체가 공유될 수 있도록 본질적인 상태와 부가적인 상태를 분리하는 역할을 한다.
- `ConcreteFlyweight`: `Flyweight` 인터페이스를 구현하고 내부적으로 갖고 있어야 하는 본질적 상태에 대한 저장소를 정의한다. 해당 객체는 공유할 수 있는 것이어야 한다. 
- `UnsharedConcreteFlyweight`: `Flyweight` 인터페이스를 구현하고 있지만, 공유되지는 않는 객체이다. 이 객체는 자신의 자식 객체를 가질 수 있으며, 이런 객체들은 공유되지 않고 독립적으로 관리된다.
- `FlyweightFactory`: `Flyweight` 객체를 생성하고 관리하며, `Flyweight` 객체가 잘 공유되도록 보장한다. 
- `Client`: `Flyweight` 객체에 대한 참조자를 관리하며, `Flyweight` 객체의 부가적인 상태를 저장한다.

## Collaborations

- 본질적인 상태는 `ConcreteFlyweight`에 저장하고, 부가적인 상태는 사용자가 저장하거나, 연산되어야 하는 다른 상태로 관리해야 한다. 사용자는 연산을 호출할 때 자신에게만 필요한 부가적 상태를 `Flyweight` 객체에 매개변수로 전달한다.
- 사용자는 `ConcreteFlyweight`의 인스턴스를 직접 만들 수 없으며, `ConcreteFlyweight` 객체를 `FlyweightFactory` 객체에서 얻어야 한다. 이렇게 해야 `Flyweight` 객체가 공유될 수 있다.

## Consequences

1. **공유해야 하는 인스턴스의 전체 수를 줄일 수 있다.**
2. **객체 별 본질적인 상태의 양을 줄일 수 있다.**
3. **부가적인 상태는 연산되거나 저장될 수 있다.**

## Implmentation

1. **부가적 상태를 제외한다.**

    부가적인 상태 정보를 외부에서 관리하고, 객체는 본질적인 상태만을 저장한다. 이렇게 분리하면 저장소 공간을 그만큼 절약할 수 있다. 
2. **공유할 객체를 관리한다.**

    객체는 공유될 수 있으므로 사용자가 직접 인스턴스를 만들면 안 된다. `FlyweightFactory`를 통해 사용자에게 제공되어야 한다.

## Sample Code

`Glyph`는 컴포지트 패턴으로 만든 클래스로, 다른 그래픽 요소를 갖고 그것을 그릴 수 있다. 여기서는 폰트 속성만 고려해보자.

```cpp
class Glyph {
public:
    virtual ~Glyph();

    virtual void Draw(Window*, GlyphContext&);

    virtual void SetFont(Font*, GlyphContext&);
    virtual Font* GetFont(GlyphContext&);

    virtual void First(GlyphContext&);
    virtual void Next(GlyphContext&);
    virtual bool IsDone(GlyphContext&);
    virtual Glyph* Current(GlyphContext&);

    virtual void Insert(Glyph*, GlyphContext&);
    virtual void Remove(GlyphContext&);
protected:
    Glyph();
};
```

`Character` 서브클래스는 문자 코드를 저장하는 클래스다.

```cpp
class Character : public Glyph {
public:
    Character(char);

    virtual void Draw(Window*, GlyphContext&);
private:
    char _charcode;
};
```

모든 `Glyph`에서 폰트 속성을 할당하는 공간을 절약하려면, `GlyphContext` 객체에 저장하도록 한다.

```cpp
class GlyphContext {
public:
    GlyphContext();
    virtual ~GlyphContext();

    virtual void Next(int step = 1);
    virtual void Insert(int quantity = 1);

    virtual Font* GetFont();
    virtual void SetFont(Font*, int span = 1);
private:
    int _index;
    BTree* _fonts;
};
```

`GlyphContext`는 부가적인 상태에 대한 저장소로 동작한다. `Glyph`의 폰트에 대해 알아야 하는 연산은 `GlyphContext` 인스턴스를 매개변수로 갖고 있다. `GlyphContext`는 폰트와 위치 정보를 관리하며, 여러 `Glyph` 객체들이 동일한 폰트나 위치 정보를 공유할 수 있도록 한다. 각 `Glyph`는 폰트를 가질 수 있는데, `GlyphContext`는 이 폰트에 대한 질의를 처리하며 폰트 변경 연산(`SetFont()`, `GetFont()`)을 담당한다.

`GlyphContext`는 `Glyph` 구조 내 순회 작업 도중 현재 위치에 대한 정보를 계속 유지해야 한다. `GlyphContext::Next()`는 `_index`를 증가시킨다. `Glyph`의 서브클래스는 `Row`와 `Column` 같은 요소들이 있는데, `GlyphContext::Next()`를 호출하도록 `Next()` 연산을 구현해야 한다.

`GlyphContext::GetFont()`는 BTree 구조를 참조하는 키로 인덱스를 이용한다. BTree 구조는 글리프와 폰트 사이 대응 정보를 관리한다. 즉, 문서 편집기에서 각 글자(`Glyph`)가 자신만의 폰트 정보를 가지는 것이 아니라, 폰트 정보를 관리하는 중앙 저장소(BTree)를 참조한다.

트리의 각 노드는 폰트 정보를 줄 수 있는 스트링의 길이로 레이블이 정의되어 있다. 트리의 단말 노드들은 폰트를 포인트하고 내부 노드들은 스트링을 서브스트링으로 쪼개는 일을 한다.

다음은 글리프가 어떻게 구성되어 있는지를 보여준다.

![glyph composition](images/patterns/glyph_composition.png)

BTree 구조는 다음과 같을 것이다.

![BTree structure](images/patterns/btree_structure.png)

루트 노드의 500이라는 값은 전체 문자의 길이가 500이라는 것이다. 그 다음 1 레이블 값을 갖는 단말 노드의 의미는 길이가 1인 문자열이 Times 24 폰트를 갖고 있음을 의미한다. 이는 발췌본의 인덱스 1에 정의한 "O" 문자열에 해당한다. 이후 2번 인덱스부터 101번 인덱스까지 길이가 100인 문자열은 Times 12 폰트를 갖고 있는데, 이 정보는 BTree에서 보면 300 노드의 첫 번째 왼쪽 자식인 노드 100 노드에 의해 정의되고 있다. 300 노드의 의미는 전체 발췌본을 "O" 문자열과 "object ... an" 까지의 스트링으로 구분했을 때, "object ... an"의 길이가 300임을 의미한다. 

내부 노드들은 `Glyph` 인덱스의 범위를 알려준다. 새로운 글자가 추가되거나 삭제될 때, 기존 노드가 이를 포함하도록 수정된다. 특정 위치의 폰트가 변경되면, 그 위치를 기준으로 기존 노드를 나누고 새로운 폰트 정보를 추가한다.

102번 인덱스는 "expect" 단어의 각각 문자에 대한 폰트를 세팅한다.

```cpp
GlyphContext gc;
Font* times12 = new Font("Times-Roman-12");
Font* timesItalic12 = new Font("Times-Italic-12");
// ...
gc.SetFont(times12, 6);
```

새로운 BTree 구조는 다음과 같다.

![new BTree structure](images/patterns/new_btree_structure.png)

"expect" 단어 앞에 "don't " 단어(공백 문자 포함)를 Times-Italic-12 폰트로 삽입하려 한다. 다음 코드는 `gc`에게 이 이벤트를 알려주며 인덱스는 계속 102로 가정한다.

```cpp
gc.Insert(6);
gc.SetFont(timesItalic12, 6);
```

BTree 구조는 이렇게 변한다.

![btree structure becomes](images/patterns/btree_structure_becomes.png)

`GlyphContext`가 현재 `Glyph` 폰트에 대해 질의를 받으면, 현재 스트링의 위치 인덱스에 대한 폰트를 찾을때 까지 BTree를 탐색한다. 폰트의 변경 빈도가 상대적으로 낮기 때문에 트리는 글리프 구조의 크기에 비해 작은 규모를 유지하게 된다.

```cpp
const int NCHARCODES = 128;

class GlyphFactory {
public:
    GlyphFactory();
    virtual ~GlyphFactory();
    virtual Character* CreateCharacter(char);
    virtual Row* CreateRow();
    virtual Column* CreateColumn();
    // ...
private:
    Character* _character[NCHARCODES];
};
```

`_character` 배열은 `Character` 글리프에 대한 참조자를 관리한다. 배열의 각 인덱스를 생성자에서 0으로 초기화한다.

```cpp
GlyphFactory::GlyphFactory() {
    for (int i = 0; i < NCHARCODES; ++i) {
        _character[i] = 0;
    }
}
```

`CreateCharacter()` 연산은 문자 글리프 내 있는 문자를 찾아 존재한다면 해당 글리프를 반환하고, 존재하지 않으면 생성하여 반환한다.

```cpp
Character* GlyphFactory::CreateCharacter(char c) {
    if (!_character[c]) {
        _character[c] = new Character(c);
    }
    return _character[c];
}
```

다른 연산들은 호출될 때마다 새로운 객체를 인스턴스화하기만 한다. 비문자 글리프는 공유되지 않을 것이기 때문이다.

```cpp
Row* GlyphFactory::CreateRow() {
    return newRow;
}

Column* GlyphFactory::CreateColumn() {
    return new Column;
}
```