---
title: "Command Pattern"
date: "2025-01-31"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

요청 자체를 캡슐화하여, 사용자와 시스템 간 요청을 파라미터화하고, 요청을 큐에 넣거나 로그로 저장하거나, 작업을 실행할 수 있게 하는 패턴이다. 이 패턴은 요청을 실행하는 객체와 그 요청을 큐에서 실행하는 객체를 분리할 수 있도록 해준다.

## Motivation

리모컨에서 여러 기기들(예: TV, 전등, 팬)에 대한 다양한 명령을 보낸다고 하자. 이 시스템에서는 사용자가 버튼을 눌러 특정 기기와 기능을 제어할 수 있어야 한다.

커맨드 패턴을 적용하여 각 버튼이 특정 명령을 실행하도록 구성하여 유연하게 시스템을 관리할 수 있다.

## Applicability

- 수행할 동작을 매개변수화(콜백 함수)하고자 할 때
- 서로 다른 시간에 요청을 명시하고, 저장하며, 실행하고 싶을 때
- 실행 취소 기능을 지원하고 싶을 때
- 시스템이 고장났을 때 재실행이 가능하도록 변경 과정에 대한 저장, 복구를 지원하고 싶을 때
- 기본적인 연산의 조합으로 만든 상위 수준 연산을 써서 시스템을 구조화하고 싶을 때

## Structure

![command pattern structure](images/patterns/command_pattern_structure.png)

- `Command`: 연산 수행에 필요한 인터페이스를 선언한다.
- `ConcreteCommand`: `Command` 인터페이스를 구현한 클래스이다. 실제로 수행할 작업을 구현하고, 해당 작업을 수행할 `Receiver` 객체를 호출한다.
- `Invoker`: `Command` 객체를 호출하는 역할을 한다. 명령을 요청하고, 실행할 객체에 전달한다. 
- `Receiver`: 실제 요청을 수행하는 객체이다. `Receiver` 객체는 요청에 대한 연산을 수행하는 방법을 알고 있다.
- `Client`: `ConcreteCommand` 객체를 생성하고 해당 명령에 대한 구체적인 `Receiver`를 지정한다.

## Collaborations

- 사용자는 `ConcreteCommand` 객체를 생성하고 이를 `Receiver`로 지정한다.
- `Invoker` 클래스는 `ConcreteCommand` 객체를 저장한다.
- `Invoker` 클래스는 `Command`에 정의된 `Execute()`를 호출하여 요청을 발생시킨다. 명령어가 취소 가능하다면 `ConcreteCommand`는 이전에 `Execute()` 호출 전 상태의 취소 처리를 위해 저장한다.
- `ConcreteCommand` 객체는 요청에 대한 연산을 호출한다.

![command pattern collaboration](images/patterns/command_pattern_collaboration.png)

## Consequences

1. **`Command`는 연산을 호출하는 객체와 연산 수행 방법을 구현하는 객체를 분리한다.**
2. **`Command`는 일급 클래스이다.** 다른 객체와 같은 방식으로 조작되고 확장할 수 있다.
3. **명령을 여러 개 복합하여 복합 명령을 만들 수 있다.**
4. **새로운 `Command` 객체를 추가하기 쉽다.** 기존 클래스를 변경할 필요 없이 새로운 명령에 대응하는 클래스만 정의하면 된다.

## Implementation

1. **`Command` 객체의 지능.**

    명령은 단순히 요청을 보내는 역할을 할 뿐만 아니라, 요청을 처리할 수 있는 객체와 연결하는 역할도 한다. 명령 객체는 요청을 받은 후 이를 적절한 `Receiver`에 전달할 수 있도록 설계된다. 즉, 요청을 수신한 명령은 "어떤 객체에서 그 요청을 처리할 것인지"를 결정할 수 있다.
2. **취소(undo) 및 반복(redo) 연산 지원하기.**

    `ConcreteCommand` 클래스는 각 명령어가 수행하는 동작에 필요한 상태 정보를 관리해야 한다. 명령어가 실행될 때마다 그 결과를 이력 목록(history list)에 저장한다. 

    이력 목록은 여러 번의 명령어 실행을 기록하는 리스트로, 실행된 명령어의 순서대로 저장된다. 이 목록을 뒤집어 읽으면 취소(undo)의 효과를 얻을 수 있다.

    취소할 수 있는 객체를 이력 목록에 저장하기 전 복사해 둘 때도 있다. 복사본을 저장하는 이유는 명령어 객체가 서로 다른 실행에 의해 발생하는 결과를 구분하기 위해서이다.

3. **취소를 진행하는 도중 오류가 누적되는 것 피하기.**

    처리 내역의 이력을 관리할 때는 신뢰성을 보장하면서 처리된 의미들을 유지한 채 수행/취소 처리가 되어야 한다.

4. **C++ 템플릿 사용하기.**

    C++ 템플릿을 쓰면 하나의 템플릿 클래스를 기반으로 여러 타입의 명령어를 정의할 수 있다.

## Sample Code

```cpp
class Command {
public:
    virtual ~Command();
    
    virtual void Execute() = 0;
protected:
    Command();
};
```

`OpenCommand` 클래스는 선택한 이름의 문서를 여는 처리를 추상화한 객체이다. `OpenCommand` 객체를 생성하기 위해 `Application` 객체를 매개변수로 전달받는다. `AskUser()` 연산을 이용해 사용자에게 열어야 하는 문서의 이름을 받는다.

```cpp
class OpenCommand : public Command {
public:
    OpenCommand(Application*);
    
    virtual void Execute();
protected:
    virtual const char* AskUser();
private:
    Application* _application;
    char* _response;
};

OpenCommand::OpenCommand(Application* a) {
    _application = a;
}

void OpenCommand::Execute() {
    const char* name = AskUser();
    
    if (name != 0) {
        Document* document = new Document(name);
        _application->Add(document);
        document->Open();
    }
}
```

`PasteCommand` 클래스는 `Document` 객체를 처리 객체로 전달받아야 한다. 이 객체는 생성자의 매개변수로 정의한다.

```cpp
class PasteCommand : public Command {
public:
    PasteCommand(Document *);
    virtual void Execute();
private:
    Document* _document;
};

PasteCommand::PasteCommand(Document* doc) {
    _document = doc;
}

void PasteCommand::Execute() {
    _document->Paste();
}
```

명령어 취소나 특별한 인자를 요청하지 않는 단순한 명령이라면, 이 처리 객체 자체를 매개변수로 하는 템플릿 클래스를 정의할 수 있다. `SimpleCommand` 서브클래스는 `Command`의 서브클래스로, 처리 객체에 해당하는 `Receiver` 타입으로 매개변수화하여 처리 객체와 처리할 작업 간 연결 관계를 관리한다.

```cpp
template <class Receiver>
class SimpleCommand : public Command {
public:
    typedef void (Receiver::* Action)();
    SimpleCommand(Receiver* r, Action a) :_receiver(r), _action(a) { }
    
    virtual void Execute();
private:
    Action _action;
    Receiver* _receiver;
};
```

생성자는 처리 객체와 처리 내용에 대한 참조자를 저장한다. `Execute()` 연산은 단순히 처리 객체에 해당하는 처리 내용을 호출하는 문장으로 구현될 뿐이다.

```cpp
template <class Receiver>
void SimpleCommand<Receiver>::Execute() {
    (_receiver->*_action)();
}
```

`MyClass` 클래스의 인스턴스인 `Action`을 호출하는 명령어를 생성하려면 사용자 코드를 다음과 같이 작성하면 된다.

```cpp
MyClass* receiver = new MyClass;
// ...
Command* aCommand =
	new SimpleCommand<MyClass>(receiver, &MyClass::Action);
// ...
aCommand->Execute();
```

여기서 `Action()` 연산은 `MyClass`에 정의된 인터페이스 중 매개변수를 요청하지 않으며 반환 타입이 `void`인 연산을 의미한다. 이는 간단한 명령어에서만 가능할 뿐 명령어의 수행 이력을 기록해야 하거나, 특별한 매개변수가 필요할 때는 적용되지 않는다.

다음은 `SimpleCommand`를 통해 문서의 복사를 수행한다.

```cpp
Document doc;
SimpleCommand<Document> pasteCommand(&doc, &Document::Paste);  // 명령 생성
pasteCommand.Execute();  // 실행 -> "Pasting content into document!"
```

여러 가지 처리를 일련의 순서대로 수행할 때 `MacroCommand` 클래스를 정의한다. `MacroCommand` 클래스는 일련의 명령어들을 추가하거나 삭제하는 역할까지 담당한다. 그러나 `MacroCommand` 클래스에는 어떠한 명시적 처리 객체도 정의되어 있지 않다. `MacroCommand`를 구성하는 각 명령어들만이 실제 처리 객체에 대한 정보를 가지고 있으면 되기 때문이다.

```cpp
class MacroCommand : public Command {
public:
    MacroCommand();
    virtual ~MacroCommand();
    
    virtual void Add(Command*);
    virtual void Remove(Command*);
    
    virtual void Execute();
private:
    List<Command*>* _cmds;
};
```

`MacroCommand`에서 중요한 부분은 `Execute()` 멤버 함수이다. 이는 자신이 포함한 명령어들 모두 방문하여 각각의 `Execute()` 함수를 호출한다.

```cpp
void MacroCommand::Execute() {
    ListIterator<Command*> i(_cmds);
    for (i.First(); !i.IsDone(); i.Next()) {
        Command* c = i.CurrentItem();
        c->Execute();
    }
}
```

`MacroCommand` 클래스가 `Unexecute()` 연산을 정의하려면 `Execute()` 연산을 구현하는 순서와 반대로 `Unexecute()` 연산을 수행해야 한다.

또한 `MacroCommand` 클래스는 하위 명령을 관리할 수 있는 연산을 제공해야 한다. `MacroCommand`는 하위 명령을 삭제하는 일도 담당한다.

```cpp
void MacroCommand::Add(Command* c) {
    _cmds->Append(c) ;
}
void MacroCommand::Remove(Command* c) {
    _cmds->Remove(c);
}
```