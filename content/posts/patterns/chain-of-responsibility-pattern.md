---
title: "Chain of Responsibility Pattern"
date: "2025-01-31"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "behavioral pattern"]
---

요청을 한 객체에서 다른 객체로 전달하며, 각 객체가 요청을 처리할지 여부를 결정하는 구조이다.

## Motivation

애플리케이션에서 로그를 처리하는데, 여러 종류의 로그 메시지가 있다고 하자. 정보, 경고, 오류 메시지가 있으며, 각 메시지는 적절한 방식으로 처리되어야 한다. 오류 메시지는 콘솔에 즉시 출력하고, 정보 메시지는 파일에 저장하며, 경고 메시지는 원격 서버에 전송한다. 각 메시지를 처리하는 핸들러가 존재하며, 메시지의 종류에 따라 적합한 핸들러가 메시지를 처리해야 한다.

책임 연쇄 패턴을 사용하면 로그 메시지 처리 체인을 구성하여 해결할 수 있다. 각 로그 레벨을 처리하는 핸들러를 체인으로 연결하여 각 메시지가 처리되도록 할 수 있다. 

## Applicability

- 하나 이상의 객체가 요청을 처리해야 하고, 그 요청 처리자 중 어떤 것이 선행자(priori)인지 모를 때, 처리자가 자동으로 확정되어야 한다.
- 메시지를 받을 객체를 명시하지 않은 채 여러 객체 중 하나에게 처리를 요청하고 싶을 때
- 요청을 처리할 수 있는 객체 집합이 동적으로 정의되어야 할 때

## Structure

![chain of responsibility pattern structure](images/patterns/chain_of_responsibility_pattern_structure.png)

객체 구조는 다음과 같이 보일 수 있다.

![typical object structure](images/patterns/typical_object_structure.png)

- `Handler`: 요청을 처리하는 인터페이스를 정의하고, 후속 처리자(successor)와 연결을 구현한다. 즉, 연결 고리에 연결된 다음 객체에게 다시 메시지를 보낸다.
- `ConcreteHandler`: 실제로 요청을 처리하는 핸들러이다. 즉, 자신이 처리할 행동이 있으면 처리하고, 그렇지 않으면 후속 처리자에 다시 처리를 요청할 수 있다.
- `Client`: `ConcreteHandler` 객체에게 필요한 요청을 보낸다.

## Collaborations

- 사용자는 처리를 요청하고, 이 처리 요청은 실제로 그 요청을 받을 책임이 있는 `ConcreteHandler` 객체를 만날 때까지 정의된 연결 고리를 따라 계속 전달된다.

## Consequences

1. **객체 간 행동적 결합도가 낮아진다.**

    다른 객체가 어떻게 처리하는지 몰라도 된다. 단지 요청을 보내는 객체는 이 메시지가 적절하게 처리될 것만 확신하면 된다. 메시지를 보내는 측이나 받는 측 모두 서로를 모르고, 또 연결된 객체들조차도 그 연결 구조가 어떻게 되는지 모른다. 결과적으로 이 패턴은 객체들 간 상호작용 과정을 단순화시킨다.
2. **객체에게 책임을 할당하는 데 유연성을 높일 수 있다.**

    객체의 책임을 여러 객체에 분산시킬 수 있어 런타임에 객체 연결 고리를 변경하거나 추가하여 책임을 변경하거나 확장할 수 있다.
3. **메시지 수신이 보장되지는 않는다.**

    어떤 객체가 이 처리에 대한 수신을 담당하는 것을 명시하지 않으므로 요청이 처리된다는 보장은 없다. 만약 객체들 간 연결 고리가 잘 정의되지 않으면 요청이 처리되지 못한 채 버려질 수 있다.

## Implmentation

1. **후속 처리자들의 연결 고리 구현하기.** 후속 처리자들의 연결 고리를 구현하는 방법은 두 가지다.

    1. 새로운 연결을 만드는 방법
        
        새로운 연결 정보를 명시적으로 정의하여 처리자 간 연결을 관리하는 방식이다. 주로 `Handler` 클래스에서 `nextHandler` 변수를 사용해 구현되며, 필요할 경우 `ConcreteHandler` 클래스에서 직접 구현할 수 있다. 
    2. 이미 있는 연결 정보를 사용하는 것

        이미 존재하는 연결 정보(예: UI 계층 구조, DOM 트리, 그래프 등)를 활용하여 책임 연쇄를 구현하는 방식이다. 이 방식은 기존 구조를 활용하므로 중복된 연결 정보를 정의하지 않아도 된다.
2. **후속 처리자 연결하기.**

    기본적으로 각 처리자(handler)는 자신의 후속 처리자를 알고 있어야 한다. 후속 처리자는 연결 정보로서, 한 처리자가 자신의 후속 처리자에게 요청을 넘길 수 있도록 도와준다.

    ```cpp
    class HelpHandler {
    public:
        HelpHandler(HelpHandler* s) : _successor(s) { } // 후속 처리자 설정
        virtual void HandleHelp();
    private:
        HelpHandler* _successor;
    };

    void HelpHandler::HandleHelp() {
        if (_successor) {
            _successor->HandleHelp();
        }
    }
    ```
3. **처리 요청의 표현부를 정의한다.**

    1. 처리 요청을 코드화하여 매개변수로 전달

        `HandleRequest()` 메서드를 사용해 요청을 처리하는데, 이 방식은 하드코딩된 방식이라 처리할 수 있는 요청이 제한적이다.

    2. `Request` 클래스를 사용해 처리 요청 정의

        요청을 유연하게 처리하려면 매개변수를 다루는 방식이 필요하다. 이를 위해 `Request` 클래스를 사용해 처리 요청을 정의한다. `Request` 클래스는 서브클래싱을 통해 다양한 요청의 매개변수를 정의할 수 있다. 따라서 각 요청을 구체적인 클래스나 객체로 다룰 수 있으며, 필요에 따라 확장할 수도 있다.

    3. 요청 종류 식별

        `Request` 클래스는 요청의 종류를 식별할 수 있어야 한다. `GetKind()` 메서드를 사용해 요청이 무엇인지 식별하고, 이에 맞는 처리 방식으로 분기한다.

        ```cpp
        void Handler::HandleRequest(Request* theRequest) {
            switch (theRequest->GetKind()) {
                case Help:
                    // cast argument to appropriate type
                    HandleHelp((HelpRequest*) theRequest);
                    break;
                case Print:
                    HandlePrint((PrintRequest*) theRequest);
                    // ...
                    break;
                default:
                    // ...
                    break;
            }
        }
        ```
    
    4. 서브클래스에서 요청 처리 방식 재정의

        `Handler` 클래스의 `HandleRequest()` 메서드를 서브클래스에서 재정의하여 새로운 처리 방법을 구현할 수 있다.

        예를 들어, `ExtendedHandler` 서브클래스에서 `Preview` 요청만 처리하고, 그 외의 요청은 부모 클래스에서 처리하게 할 수 있다.
        
        ```cpp
        class ExtendedHandler : public Handler {
        public:
            virtual void HandleRequest(Request* theRequest);
            // ...
        };

        void ExtendedHandler::HandleRequest(Request* theRequest) {
            switch (theRequest->GetKind()) {
                case Preview:
                    // handle the Preview request
                    break;
                default:
                    // let Handler handle other requests
                    Handler::HandleRequest(theRequest);
            }
        }
        ```

## Sample Code

`HelpHandler` 클래스는 도움말 요청을 처리하는 데 필요한 인터페이스를 정의한다. 도움말 목록을 관리하고 `HelpHandler`의 연결 고리 다음 객체에 대한 참조자를 관리한다. 가장 중요한 연산은 `HandleHelp()`로 서브클래스에서 이 연산을 재정의해야 한다. `HasHelp()`는 관련된 도움말 항목이 있는지 확인하는 연산이다.

```cpp
typedef int Topic;
const Topic NO_HELP_TOPIC = -1;
class HelpHandler {
public:
    HelpHandler(HelpHandler* = 0, Topic = NO_HELP_TOPIC);
    virtual bool HasHelp();
    virtual void SetHandler(HelpHandler*, Topic);
    virtual void HandleHelp();
private:
    HelpHandler* _successor;
    Topic _topic;
};

HelpHandler::HelpHandler(HelpHandler* h, Topic t) : _successor(h), _topic(t) { }

bool HelpHandler::HasHelp() {
    return _topic != NO_HELP_TOPIC;
}

void HelpHandler::HandleHelp() {
    if (_successor != 0) {
        _successor->HandleHelp();
    }
}
```

모든 위젯은 `Widget`이라는 추상 클래스의 서브클래스들이며, `Widget`은 `HelpHandler`의 서브클래스이다. 

```cpp
class Widget : public HelpHandler {
protected:
    Widget(Widget* parent, Topic t = NO_HELP_TOPIC);
private:
    Widget* _parent;
};

Widget::Widget(Widget* w, Topic t) : HelpHandler(w, t) {
    _parent = w;
}
```

버튼은 연결 고리에서 첫 번째 처리자다. `Button` 클래스는 `Widget`의 서브클래스고, `Button`의 생성자는 자신을 포함하는 객체에 대한 참조자와 도움말 항목 정보를 매개변수로 받아들인다.

```cpp
class Button : public Widget {
public:
    Button(Widget* d, Topic t = NO_HELP_TOPIC);

    virtual void HandleHelp();
    // Widget operations that Button overrides...
};
```

`Button` 클래스의 `HandleHelp()` 연산은 우선 버튼에 해당하는 도움말이 있는지 확인한다. 개발자가 정의하지 않았다면 요청을 `HelpHandler()` 연산을 통해 다음 객체에 전달된다. 도움말 항목이 있다면 도움말을 보여주고 객체를 찾는 일은 끝난다.

```cpp
Button::Button(Widget* h, Topic t) : Widgetfh, t) { }

void Button::HandleHelp() {
    if (HasHelp()) {
        // offer help on the button
    } else {
        HelpHandler::HandleHelp();
    }
}
```

`Dialog` 클래스도 비슷한 방법으로 구현한다. 도움말을 제공할 수 있다면 제공하고, 그렇지 않으면 후속 처리자에게 요청을 전달한다.

```cpp
class Dialog : public Widget {
public:
    Dialog(HelpHandler* h, Topic t = NO_HELP_TOPIC);
    virtual void HandleHelp();

    // Widget operations that Dialog overrides...
    // ...
};

Dialog::Dialog(HelpHandler* h, Topic t) : Widget(O) {
    SetHandler(h, t);
}

void Dialog::HandleHelp() {
    if (HasHelp()){
        // offer help on the dialog
    } else {
        HelpHandler::HandleHelp();
    }
}
```

연결의 끝은 `Application`의 인스턴스인데, 애플리케이션은 위젯이 아니다. 따라서 `HelpHandler` 클래스를 직접 상속받는다. 도움말 요청이 이 단계까지 전달되면 애플리케이션에 대한 정보를 제공한다.

```cpp
class Application : public HelpHandler {
public:
    Application(Topic t) : HelpHandler(0, t) { }
    virtual void HandleHelp();
    // application-specific operations...
};

void Application::HandleHelp() {
    // show a list of help topics
}
```

다음 코드는 이들 객체를 생성하고 연결한다.

```cpp
const Topic PRINT_TOPIC - 1 ;
const Topic PAPER_ORIENTATION_TOPIC = 2;
const Topic APPLICATION_TOPIC = 3;

Application* application = new Application(APPLICATION_TOPIC);
Dialog* dialog = new Dialog(application, PRINT_TOPIC);
Button* button = new Button(dialog, PAPER_ORIENTATION_TOPIC);
```

`HandleHelp()`를 호춣하여 도움말을 요청한다. `HelpHandler` 클래스는 `Dialog`의 후속 처리자로 만들어질 수 있다. 또한 후속 처리자는 동적으로 변경될 수도 있다.

```cpp
button->HandleHelp();
```