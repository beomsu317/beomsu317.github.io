---
title: "Mediator Pattern"
date: "2025-02-01"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

객체 간 직접적인 상호작용을 제한하고, 대신 중재자를 통해 통신하도록 하는 패턴이다. 중재자 객체를 통해 간접적으로 상호작용하여 객체 간 결합도를 낮추는 것이 목표이다.

## Motivation

GUI 애플리케이션에 여러 개의 UI 컴포넌트(예: 버튼, 체크박스, 텍스트 필드 등)가 서로 상호작용할 때, 한 컴포넌트의 상태가 변경되면 다른 컴포넌트도 변경되어야 하는 상황이 많다.

예를 들어,
- 체크박스를 선택하면 버튼이 활성화됨
- 텍스트 필드에 입력하면 버튼의 상태가 변경됨
- 버튼을 클릭하면 다른 UI 요소들이 변경됨

이러한 상호작용을 각각의 UI 요소가 직접 관리하면, 객체 간 결합도가 높아져 유지보수가 어려워진다.

이때 중재자(Mediator) 패턴을 사용하면 UI 요소들이 직접 서로 통신하는 것이 아니라, 중재자를 통해 간접적으로 상호작용 할 수 있다. 즉, 객체 간 직접적인 의존성을 줄이고, 변경이 필요할 때 하나의 중재자만 수정하면 되는 구조이다.

## Applicability

- 여러 객체가 잘 정의된 형태이나 복잡한 상호작용을 가질 때
- 객체 간 의존성이 구조화되지 않으며 이해하기 어려울 때
- 한 객체가 다른 객체를 너무 많이 참조하고, 너무 많은 의사소통을 수행해 그 객체를 재사용하기 힘들 때
- 여러 클래스에 분산된 행동들이 상속 없이 상황에 맞게 수정되어야 할 때

## Structure

![alt text](images/mediator_pattern_structure.png)

- `Mediator`: `Colleague` 객체와 교류하는 데 필요한 인터페이스를 정의한다.
- `ConcreteMediator`: `Colleague` 객체들을 관리하며, 이들 간 협력 행동을 조정하는 역할을 수행한다.
- `Colleague` 클래스들: 중재자를 통해 다른 객체들과 통신하는 개별 컴포넌트이다. 이들은 직접적으로 다른 `Colleague` 객체와 상호작용하지 않고, 반드시 `Mediator`를 통해서만 통신한다.

## Collaborations

- `Colleague`는 `Mediator`에서 요청을 송수신한다. `Mediator`는 필요한 `Coleague` 사이에 요청을 전달할 의무가 있다.

## Consequences

1. **서브클래싱을 제한한다.**

    중재자는 여러 객체 간 복잡한 상호작용을 한 곳(중재자)에서 관리하는 것이다. 이 방식을 통해 `Colleague` 클래스의 독립성을 유지할 수 있고(재사용), 행동 변경 시 `Mediator` 서브클래스만 수정하면 되며(확장성), 객체 간 직접적인 의존성을 제거하여 코드 복잡도가 낮아진다.
2. **`Colleague` 객체 사이 종속성을 줄인다.**
3. **객체 프로토콜을 단순화한다.**

    중재자는 다대다(M:N) 관계를 일대다(1:N) 관계로 축소시킨다. 이로써 이해하기 쉬울 뿐만 아니라 유지하거나 확장하기 쉬워진다.
4. **객체 간 협력 방법을 추상화한다.**

    객체 사이 중재를 독립적인 개념으로 만들고 캡슐화함으로써, 사용자는 각 객체의 행동과 상관없이 객체 간 연결 방법에만 집중할 수 있다.
5. **통제가 집중화된다.**

    복잡한 모든 통신들을 `Mediator` 내부에서만 오가게 한다. 상호작용에 관련된 프로토콜을 모두 캡슐화하기 때문에 어느 복잡해질 가능성이 있어, `Mediator` 클래스 자체의 유지보수가 어려워질 수 있다. 

## Implementation

1. **추상 클래스인 `Mediator` 생략.**

    만약 관련 객체들이 오직 하나의 `Mediator` 클래스와 동작한다면 굳이 추상 클래스로 정의할 필요가 없다. 추상 클래스의 목적은 또 다른 상호작용을 정의할 새로운 `Mediator` 서브클래스를 만들 때를 대비한 것이다. 
2. **`Colleague` - `Mediator` 간 의사소통.**

    필요한 이벤트가 발생할 때 `Colleague` 클래스는 `Mediator` 클래스와 데이터를 주고 받아야 한다.

## Sample Code

`DialogDirector`는 추상 클래스로 지시자(director)에 대한 인터페이스를 정의한다.

```cpp
class DialogDirector {
public:
    virtual ~DialogDirector();
    virtual void ShowDialog();
    virtual void WidgetChanged(Widget*) = 0;
protected:
    DialogDirector();
    virtual void CreateWidgets() = 0;
};
```

`Widget` 클래스는 위젯에 대한 추상 클래스다. 위젯은 지시자가 누군지를 알고 있다.

```cpp
class Widget {
public:
    Widget(DialogDirector*);
    virtual void Changed();
    virtual void HandleMouse(MouseEvent& event);
    // ...
private:
    DialogDirector* _director;
};
```

`Changed()` 연산은 지시자 인스턴스 변수가 참조하는 객체의 `WidgetChanged()` 연산을 호출하여 변경 사실을 알린다.

```cpp
void Widget::Changed() {
    _director->WidgetChanged(this);
}
```

`DialogDirector` 서브클래스는 `WidgetChanged()` 연산을 재정의하여 적절하게 `Widget` 클래스가 변경되도록 한다. `WidgetChanged()` 연산에게 자신에 대한 참조자(`this`)를 인자로 전달한다. 이로써 변경된 위젯이 무엇인지 지시자에게 알려준다. `DialogDirector`의 서브클래스들은 `CreateWidgets()` 연산을 재정의해 대화상자에 필요한 위젯들을 구성한다.

`ListBox`, `EntryField`, `Button`은 `Widget`의 서브클래스로 구체적인 사용자 인터페이스 컴포넌트이다. 

`ListBox` 클래스는 `GetSelection()` 연산을 통해 현재 선택된 항목이 무엇인지 알려준다.

```cpp
class ListBox : public Widget {
public:
    ListBox(DialogDirector*);
    virtual const char* GetSelection();
    virtual void SetList(List<char*>* listItems);
    virtual void HandleMouse(MouseEvent& event);
    // ...
};
```

`EntryField` 클래스의 `SetText()` 연산은 새로운 텍스트를 입력 창에 표시한다.

```cpp
class EntryField : public Widget {
public:
    EntryField(DialogDirector*);
    virtual void SetText(const char* text);
    virtual const char* GetText();
    virtual void HandleMouse(MouseEvent& event);
    // ...
}
```

`Button` 클래스는 `HandleMouse()` 연산을 구현할 때 `Changed()` 연산을 호출하도록 한다.

```cpp
class Button : public Widget {
public:
    Button(DialogDirector*) ;
    virtual void SetText(const char* text);
    virtual void HandleMouse(MouseEvent& event);
    // ...
};

void Button::HandleMouse(MouseEvent& event) {
    // ...
    Changed();
}
```

`FontDialogDirector` 클래스는 `DialogDirector`의 서브클래스로 대화상자에 정의한 위젯 간 중재 역할을 수행한다. 

```cpp
class FontDialogDirector : public DialogDirector {
public:
    FontDialogDirector();
    virtual ~FontDialogDirector();
    virtual void WidgetChanged(Widget*);
protected:
    virtual void CreateWidgets();
private:
    Button* _ok;
    Button* _cancel; 
    ListBox* _fontList;
    EntryField* _fontName;
};
```

`FontDialogDirector` 클래스는 자신이 화면에 표시한 위젯에 대한 정보를 계속 추적한다. `CreateWidgets()` 연산을 재정의해 위젯을 생성하고, 이 위젯에 대한 참조자로 `FontDialogDirector` 클래스의 인스턴스 변수들을 초기화한다.

```cpp
void FontDialogDirector::CreateWidgets() {
    _ok = new Button(this);
    _cancel = new Button(this);
    _fontList = new ListBox(this);
    _fontName = new EntryField(this);
    // fill the listBox with the available font names
    // assemble the widgets in the dialog
}
```

`WidgetChanged()` 연산은 중재자가 변경된 위젯에 따라 적절한 작업을 수행하는 역할을 한다.

```cpp
void FontDialogDirector::WidgetChanged(Widget* theChangedWidget) {
    if (theChangedWidget == _fontList) {
        _fontName->SetText(_fontList->GetSelection());
    } else if (theChangedWidget == _ok) {
        // apply font change and dismiss dialog
        // ...
    } else if (theChangedWidget == _cancel) {
        // dismiss dialog
    }
}
```

`WidgetChanged()` 연산이 복잡해지면 대화상자도 복잡해진다. 