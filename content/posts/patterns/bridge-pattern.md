---
title: "Bridge Pattern"
date: "2025-01-28"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "structural pattern"]
---

구현에서 추상을 분리하여 이들이 독립적으로 다양성을 가질 수 있도록 한다.

## Motivation

기존 방식에서는 `Window` 클래스가 특정 플랫폼(Linux, Mac, Windows)에 대한 구현을 직접 포함했다면, 새로운 플랫폼이 추가될 때마다 `Window` 클래스를 수정해야 한다.

브릿지 패턴을 이용해 `Window`와 `WindowImp`를 분리하면 독립적으로 확장할 수 있게 된다.

## Applicability

- 추상적 개념과 이에 대한 구현 사이 지속적인 종속 관계를 피하고 싶을 때
- 추상적 개념과 구현 모두가 독립적으로 서브클래싱을 통해 확장되어야 할 때
- 추상적 개념에 대한 구현 내용을 변경하는 것이 다른 관련 프로그램에 아무런 영향을 주지 않아야 할 때
- 사용자에게 구현을 완벽하게 은닉하길 원할 때
- 클래스 계통에서 클래스 수가 급증하는 것을 방지하고자 할 때
- 여러 객체들에 걸쳐 구현을 공유하고자 하며(참조 카운트 등), 또 이런 사실을 사용하는 쪽에 공개하고 싶지 않을 때

## Structure

![bridge pattern structure](images/patterns/bridge_pattern_structure.png)

- `Abstraction`: 추상적 개념에 대한 인터페이스를 제공하고 객체 구현자에 대한 참조자를 관리한다.
- `Refined Abstraction`: 추상적 개념에 정의된 인터페이스를 확장한다.
- `Implementor`: 구현 클래스에 대한 인터페이스를 제공한다. 즉, 실질적인 구현을 제공한 서브클래스들에 공통적인 시그니처만을 정의한다. 
- `ConcreteImplementor`: `Implementor` 인터페이스를 구현한 것으로 실질적인 구현 내용을 담고 있다.

## Collaborations

- `Abstraction` 클래스가 사용자 요청을 `Implementor` 객체에 전달한다.

## Consequences

1. **인터페이스와 구현 분리.** 

    구현이 인터페이스에 얽매이지 않는다. 추상적 개념에 대한 어떤 방식의 구현을 택할지는 런타임에 결정될 수 있다. 즉, 런타임에 어떤 객체가 자신의 구현을 수시로 변경할 수 있음을 의미한다. 
2. **확장성 제고.**

    `Abstraction`과 `Implementor`를 독립적으로 확장할 수 있다.
3. **구현 세부사항 사용자에게서 숨기기.**

## Implementation

1. **`Implementor` 하나만 둔다.**

    구현 방법이 하나인 경우 `Implementor`를 추상 클래스로 정의하는 것은 불필요하다. C++에서는 `Implementor` 클래스의 인터페이스를 사용자에게 보이지 않도록 `private` 영역에 정의하면 된다.
2. **정확한 `Implementor` 객체를 생성한다.**

    `Abstraction` 클래스가 사용할 `ConcreteImplementor`를 직접 생성한다. 생성자에서 매개변수를 받아 적절한 구현체를 선택할 수 있다.

    팩토리 패턴을 활용해 객체 생성을 위임할 수 있다. `Abstraction` 클래스가 직접 `Implementor` 객체를 생성하지 않고, 대신 팩토리를 통해 필요한 구현체를 생성 및 제공받는다. 이러한 방식은 `Abstraction`이 `Implementor`와 직접적인 종속성을 갖지 않도록 한다.
3. **`Implementor`를 공유한다.**
4. **다중 상속을 이용한다.**

    `Abstraction` 클래스는 `public`으로 상속받고, `ConcreteImplementor`는 `private`로 상속받아 인터페이스와 구현을 합칠 수 있다.

## Sample Code

```cpp
class Window {
public:
    Window(View* contents);
    // requests handled by window
    virtual void DrawContents();
    virtual void Open();
    virtual void Close();
    virtual void Iconify();
    virtual void Deiconify();
    
    // requests forwarded to implementation
    virtual void SetOrigin(const Points at);
    virtual void SetExtent(const Point& extent);
    virtual void Raise();
    virtual void Lower();
    
    virtual void DrawLine(const Point&, const Point&);
    virtual void DrawRect(const Point&, const Point&);
    virtual void DrawPolygon(const Point[], int n);
    virtual void DrawText(const char*, const Point&);
    
protected:
    WindowImp* GetWindowImp(); View* GetView();
    
private:
    WindowImp* _imp;
    View* _contents; // the window's contents
};
```

`Window` 클래스는 `WindowImp` 클래스의 인스턴스에 대한 참조자를 관리한다. `WindowImp`의 클래스 구조는 다음과 같으며, `Window`에 정의된 연산과 다른 이름의 연산들이 정의되어 있다. 이는 실제로 윈도우를 생성하고 관리하는 데 필요한 구체적 연산들이다.

```cpp
class WindowImp {
public:
    virtual void ImpTop() = 0;
    virtual void ImpBottom() = 0;
    virtual void ImpSetExtent(const Point&) = 0;
    virtual void ImpSetOrigin(const Point&) = 0;
    
    virtual void DeviceRect(Coord, Coord, Coord, Coord) = 0 ;
    virtual void DeviceText(const char*, Coord, Coord) = 0;
    virtual void DeviceBitmap(const char*, Coord, Coord) = 0;
    // lots more functions for drawing on windows...
protected:
    WindowImp();
};
```

`Window`를 상속하여 새로운 서브클래스를 정의하여 다른 종류의 윈도우를 정의할 수 있다. 이렇게 정의된 새로운 서브클래스에는 추가적인 서비스를 제공하는 연산이 추가될 수 있다.

```cpp
class ApplicationWindow : public Window {
public:
    // ...
    virtual void DrawContents();
};

void ApplicationWindow::DrawContents() {
    GetView()->DrawOn(this);
}
```

`IconWindow`는 나타낼 아이콘에 대한 비트맵을 저장하기 위해 `Window`를 상속해 새롭게 정의한 클래스다.

```cpp
class IconWindow : public Window {
public:
    // ...
    virtual void DrawContents();
private:
    const char* _bitmapName;
};
```

여기서도 `WindowImp`에 대한 참조자를 이용해 구체적인 구현을 얻어 자신의 서비스를 만든다.

```cpp
void IconWindow::DrawContents() {
    WindowImp* imp - GetWindowImp();
    if (imp != 0) {
        imp->DeviceBitmap(_bitmapName, 0.0, 0.0);
    }
}
```

`Window` 연산들은 `WindowImp` 인터페이스에 따라 구현되는데, `Window`에 정의된 서비스 개념의 `DrawRect()`는 두 개의 `Point` 매개변수에서 네 개의 좌표를 구할 수 있다. `WindowImp`에 정의된 `DeviceRect()` 연산을 호출해 윈도우에 사각형을 그린다.

```cpp
void Window::DrawRect(const Point& pi, const Point& p2) {
    WindowImp* imp = GetWindowImp();
    imp->DeviceRect(pl.X(), pl.Y(), p2.X(), p2.Y());
}
```

`WindowImp`를 상속받는 서브클래스들을 이용해 서로 다른 윈도우 시스템을 지원할 수 있게 하는데, `XWindowImp`는 X Window 시스템을 지원한다.

```cpp
class XWindowImp : public WindowImp {
public:
    XWindowImp();
    virtual void DeviceRect(Coord, Coord, Coord, Coord);
    // remainder of public interface...
    
private:
    // lots of X window system-specific state, including:
    Display* _dpy;
    Drawable_winid; //windowid
    GC _gc; // window graphic context
};
```

PM(Presentation Manager)에 대해 `PMWindowImp`를 정의한다.

```cpp
class PMWindowImp : public WindowImp {
public:
    PMWindowImp();
    virtual void DeviceRect(Coord, Coord, Coord, Coord);
    // remainder of public interface...
    
private:
    // lots of PM window system-specific state, including:
    HPS _hps;
};
```

이 서브클래스들은 윈도우 시스템의 기본 기능들을 이용해 `WindowImp` 연산을 구현한다. 예를 들어, `DeviceRect()`는 X Window 시스템에서 다음과 같이 구현할 수 있다.

```cpp
void XWindowImp::DeviceRect(Coord xO, Coord yO, Coord xl, Coord yl) {
    int x = round(min(xO, xl));
    int y = round(min(yO, yl));
    int w = round(abs(xO - xl));
    int h = round(abs(yO - yl));
    XDrawRectangle(_dpy, _winid, _gc, x, y, w, h);
}
```

PM 구현은 다음과 같다.

```cpp
void PMWindowImp::DeviceRect(Coord xO, Coord yO, Coord xl, Coord yl) {
    Coord left = min(xO, xl);
    Coord right = max(xO, xl);
    Coord bottom = min(yO, yl);
    Coord top = max(yO, yl) ;
    
    PPOINTL point[4];
    
    point[0].x = left;      point[0].y = top;
    point[l].x = right;     point[1].y = top;
    point[2].x = right;     point[2].y = bottom;
    point[3].x = left;      point[3].y = bottom;
    
    if (
        (GpiBeginPath(_hps, 1L) == false) ||
        (GpiSetCurrentPosition(_hps, &point[3]) == false) ||
        (GpiPolyLine(_hps, 4L, point) == GPI_ERROR) ||
        (GpiEndPath(_hps) == false)
        ){
            // report error
        } else {
            GpiStrokePath(_hps, 1L, OL);
        }
}
```

즉 `WindowImp` 인터페이스의 구체적인 구현을 각 플랫폼별 시스템에 맞춰 구현할 수 있게 된다.