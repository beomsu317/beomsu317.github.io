---
title: "Proxy Pattern"
date: "2025-01-30"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "structural pattern"]
---

다른 객체들에 대한 접근을 제어하기 위한 대리 객체(Proxy)를 사용한다.

## Motivation

사용자가 원격 서버의 대형 이미지를 로드하고 화면에 표시하는 애플리케이션을 개발한다고 하자. 이때 이미지 로딩이 느려 앱의 성능이 저하되는 문제가 발생할 수 있다. 

프록시 패턴을 사용하면 실제 이미지를 즉시 로드하지 않고 가짜(Proxy) 객체를 먼저 생성한다. 이후 사용자가 이미지를 요청할 때 실제 객체를 로드하여 성능을 최적화한다. 

## Applicability

- **원격지 프록시(remote proxy)** 는 서로 다른 주소 공간에 존재하는 객체를 가리키는 대표 객체로, 로컬 환경에 위치한다.
- **가상 프록시(virtual proxy)** 는 요청이 있을 때만 필요한 고비용 객체를 생성한다.
- **보호용 프록시(protection proxy)** 는 원래 객체에 대한 실제 접근을 제어한다. 이는 객체별로 접근 제어 권한이 다를 때 유용하게 사용할 수 있다.
- **스마트 참조자(smart reference)** 는 원시 포인터의 대체용 객체로, 실제 객체에 대한 접근이 일어날 때 추가적인 행동을 수행한다. 

## Structure

![proxy pattern structure](images/patterns/proxy_pattern_structure.png)

프로그램 실행 중 프록시 구조를 객체 다이어그램으로 나타내면 다음과 같다.

![proxy structure object diagram](images/patterns/proxy_structure_object_diagram.png)

1. `Proxy`: 실제 참조할 대상에 대한 참조자를 관리한다. `RealSubject`와 `Subject` 인터페이스가 동일하다면 프록시는 `Subject`에 대한 참조자를 갖는다.`Subject`와 동일한 인터페이스를 제공하여 실제 대상을 대체할 수 있어야 한다. 실제 대상에 대한 접근을 제어하고 실제 대상의 생성과 삭제를 책임진다.
    
    `Proxy`의 종류에 따라 다음을 수행한다.
    - 원격지 프록시는 요청 메시지와 인자를 인코딩하여 이를 다른 주소 공간에 있는 실제 대상에게 전달한다.
    - 가상 프록시는 실제 대상에 대한 추가적인 정보를 보유하여 실제 접근을 지연할 수 있도록 한다.
    - 보호용 프록시는 요청한 대상이 실제 요청할 수 있는 권한이 있는지 확인한다.
2. `Subject`: `RealSubject`와 `Proxy`에 공통적인 인터페이스를 정의하여, `RealSubject`가 요청되는 곳에 `Proxy`를 사용할 수 있게 한다.
3. `RealSubject`: 프록시가 대표하는 실제 객체이다. 

## Collaborations

- 프록시 클래스는 자신이 받은 요청을 `RealSubject` 객체에 전달한다.

## Consequences

1. **원격지 프록시는 객체가 다른 주소 공간에 존재한다는 사실을 숨길 수 있다.**
2. **가상 프록시는 요구에 따라 객체를 생성하는 등 처리를 최적화할 수 있다.**
3. **보호용 프록시 및 스마트 참조자는 객체가 접근할 때마다 추가 관리를 책임진다. 객체를 생성할 것인지 삭제할 것인지를 관리한다.**

## Implmentation

1. **C++에서는 멤버 접근 연산자를 오버로드한다.**

    `operator->`이 연산자 오버로딩을 사용하면 포인터를 통해 해당 객체에 접근할 때마다 추가적인 행동을 수행할 수 있다. 프록시가 단순 포인터 역할만 할 때는 이 방식이 유용하다.
2. **Proxy가 항상 자신이 상대할 실제 대상을 알 필요는 없다.**

    `Proxy` 클래스는 `RealSubject`와 동일한 인터페이스를 구현하므로, 클라이언트는 `RealSubject`인지 `Proxy`인지 구별할 필요 없이 동일한 방식으로 사용할 수 있다. 그러나 프록시가 실제 객체의 인스턴스를 생성해야 하는 순간이 되면 어떤 클래스를 인스턴스화해야 하는지 알고 있어야 한다.

## Sample Code

### Virtual Proxy

`Graphic` 클래스는 그래픽 객체에 대한 인터페이스를 정의한다.

```cpp
class Graphic {
public:
    virtual ~Graphic();
    
    virtual void Draw(const Point& at) = 0;
    virtual void HandleMouse(Event& event) = 0;
    
    virtual const Point& GetExtent() = 0;
    
    virtual void Load(istream& from) = 0;
    virtual void Save(ostream& to) = 0;
protected:
    Graphic();
};
```

`Image`는 `Graphic` 인터페이스를 구현하여 이미지 파일을 출력한다. `Image`는 `HandleMouse()` 연산을 재정의하여 사용자들이 이미지 크기를 대화식 환경에서 재조정할 수 있다.

```cpp
class Image : public Graphic {
public:
    Image(constchar*file); // loads image from a file
    virtual ~Image();
    
    virtual void Draw(const Point& at);
    virtual void HandleMouse(Event& event);
    
    virtual const Points GetExtent();
    virtual void Load(istream& from);
    virtual void Save(ostream& to);
private:
    // ...
};
```

`ImageProxy`는 `Image`와 같은 인터페이스를 갖는다.

```cpp
class ImageProxy : public Graphic {
public:
    ImageProxy(const char* imageFile);
    virtual ~ImageProxy();
    
    virtual void Draw(const Point& at);
    virtual void HandleMouse(Event& event);
    
    virtual const Point& GetExtent();
    
    virtual void Load(istream& from);
    virtual void Save(ostream& to);
protected:
    Image* GetImage();
private:
    Image* _image;
    Point _extent;
    char* _fileName;
};
```

생성자는 이미지를 저장한 파일의 이름을 저장해 놓고 `_extent` 및 `_image`를 초기화한다.

```cpp
ImageProxy::ImageProxy(const char* fileName) {
    _fileName = strdup(fileName);
    _extent = Point::Zero; // don't know extent yet
    _image = 0;
}

Image* ImageProxy::GetImage() {
    if (_image == 0) {
        _image = new Image(_fileName);
    }
    return _image;
}
```

`GetExtent()`에 대한 구현은 가능하면 자신이 갖고 있는 크기 정보를 제공하고, 그렇지 않으면 파일에서 이미지를 읽어온다. `Draw()` 연산은 이미지를 읽어오고, `HandleMouse()` 연산은 이벤트를 이미지에 전달하는 역할을 한다.

```cpp
const Point& ImageProxy::GetExtent() {
    if (_extent == Point::Zero) {
        _extent = GetImage()->GetExtent();
    }
    return _extent;
}

void ImageProxy::Draw(const Point& at) {
    GetImage()->Draw(at);
}

void ImageProxy::HandleMouse(Event& event) {
    GetImage()->HandleMouse(event);
}
```

`Save()` 연산은 자신이 갖고 있는 정보와 이미지 파일 이름을 스트림에 저장한다. `Load()`는 이 정보를 검색해 해당 멤버 데이터를 초기화한다.

```cpp
void ImageProxy::Save(ostream& to) {
    to << _extent << _fileName;
}

void ImageProxy::Load(istream& from) {
    from >> _extent >> _fileName;
}
```

다음과 같이 크기 정보만을 미리 로드한 후, `Draw()`가 호출되면 실제 `Image` 객체가 그려지게 된다.

```cpp
ImageProxy* proxy = new ImageProxy("image.jpg");

Point size = proxy->GetExtent();  // (파일을 읽지 않고 크기 정보만 반환)

proxy->Draw(Point(10, 10));  // 이 시점에서 Image 객체가 동적으로 생성됨
```