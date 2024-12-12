---
title: "Effective C++"
date: "2024-12-12"
author: "Beomsu Lee"
tags: ["c++", "language"]
---

## Accustoming Yourself to C++

### Item 1: View C++ as a federation of languages

C++은 다중 프로그래밍 언어(multiparadigm programming language)이다.

1. C++은 절차적 언어인 C를 기본으로 한다.
2. 객체 지향 개념의 C++ (클래스, 캡슐화, 상속, 다형성, 가상함수 등)
3. 템플릿 C++ (TMP)
4. STL

위 4가지 언어들이 C++을 이루고(federation) 있다. 효과적인 프로그래밍 규칙은 경우에 따라 달라지며, 이는 C++의 어떤 부분을 사용하느냐이다.


### Item 2: Prefer consts, enums, and inlines to #defines

매크로를 사용하면 컴파일러에 심볼릭 이름(symbolic name)이 보이지 않아 에러가 발생할 경우 확인이 어렵다. 이는 상수를 써서 해결 가능하다.

다음과 같은 매크로 함수가 있다고 하자.

```cpp
// call f with the maximum of a and b
#define CALL_WITH_MAX(a, b) f((a) > (b) ? (a) : (b))
```

`f()`가 호출되기 전 `a`가 증가하는 횟수가 달라진다. 매크로 함수는 이러한 잠재적인 문제를 가질 수 있다.

```cpp
int a=5,b=0;
CALL_WITH_MAX(++a, b);     // a is incremented twice
CALL_WITH_MAX(++a, b+10);  // a is incremented once
// f((++a) > (b) ? (++a) : (b))
```

`inline` 함수를 사용하면 기존 매크로 효율을 유지할 수 있다.

```cpp
template <typename T>                           // because we don’t
inline void callWithMax(const T& a, const T& b) // know what T is, we
{                                               // pass by reference-to-
   f(a > b ? a : b);                            // const
}
```

### Item 3: Use const whenever possible

`const`를 붙이면 컴파일러가 에러를 잡아내는데 도움을 준다. 또한 `const`는 어떤 유효범위에 있는 개체에도 붙을 수 있다. 예를 들어, 함수 매개변수 및 반환 타입에도 붙을 수 있으며, 멤버 함수에도 붙을 수 있다.

멤버 함수가 상수 멤버라는 것은 다음 두 양대 개념이 있다.

1. **비트수준 상수성**은 C++에서 적용하는 상수성이며, "그 객체의 어떤 데이터 멤버도 건드리지 않아야 그 멤버가 상수임을 정하는 개념"이다. 즉, 그 객체를 구성하는 비트들 중 어떤 것도 바뀌면 안된다는 것이다.
2. **논리적 상수성**은 상수 함수여도 몇 비트 정도는 바꿀 수 있되, 사용자 측에서 알아채지 못하게만 하면 상수 멤버 자격이 있다고 판단하는 것이다(`mutable`).

다음은 `length()` 함수가 비트 수준의 상수성을 지켜지게 한 예제이다.

```cpp
class CTextBlock {
public:
    ...
    std::size_t length() const;
private:
    char *pText;
    mutable std::size_t textLength;     // these data members may always be modified, even in const member functions
    mutable bool lengthIsValid;
};

std::size_t CTextBlock::length() const {
    if (!lengthIsValid) {
        textLength = std::strlen(pText);    // now fine
        lengthIsValid = true;               // also fine
    }
    return textLength;
}
```

상수 멤버 및 비상수 멤버 함수가 기능적으로 똑같이 구현되어 있는 경우, 중복을 피하기 위해 비상수 버전이 상수 버전을 호출하도록 한다.

### Item 4: Make sure that objects are initialized before they’re used

C++의 기본제공 타입의 객체는 초기화가 될 때도 있고 안될 때도 있으므로 **항상** 초기화한다.

C++ 규칙에 의하면 어떤 객체든 그 객체의 데이터 멤버는 생성자의 본문이 실행되기 전에 초기화되어야 한다고 명시되어 있다.

```cpp
class PhoneNumber { ... };

class ABEntry {                 // ABEntry = “Address Book Entry”
public:
    ABEntry(const std::string& name, const std::string& address,
            const std::list<PhoneNumber>& phones);
private:
    std::string theName;
    std::string theAddress;
    std::list<PhoneNumber> thePhones;
    int numTimesConsulted;
};

ABEntry::ABEntry(const std::string& name, const std::string& address,
                 const std::list<PhoneNumber>& phones)
: theName(name),
theAddress(address),            // these are now all initializations
thePhones(phones),
numTimesConsulted(0)
{}                              // the ctor body is now empty
```

initializer list를 통해 초기화하면 생성자가 호출되기 전에 초기화가 가능하다. 생성자에서 대입을 사용한 경우 `theName`, `theAddress`, `thePhones`에 대해 기본 생성자를 먼저 호출해 초기화를 미리 해놓고 생성자에서 새로운 값을 대입하게 된다.

정적(static) 객체는 자신이 생성된 시점부터 프로그램이 끝날 때까지 살아있는 객체다. 

- 비지역 정적 객체
    - 전역 객체
    - 네임스페이스 유효범위에서 정의된 객체

- 지역 정적 객체
    - 클래스 안에서 `static`으로 선언된 객체
    - 함수 안에서 `static`으로 선언된 객체
    - 파일 유효범위에서 `static`으로 정의된 객체

서로 다른 번역 단위에 정의된 비지역 정적 객체들 사이 상대적인 초기화 순서는 정해져 있지 않다. 즉, A에서 정의된 객체가 B에서 사용될 경우 초기화되지 않아 문제가 발생할 수 있다.

이는 지역 정적 객체로 변경하여 해결할 수 있다. 지역 정적 객체는 함수 호출 중 그 객체의 정의에 도달하면 초기화되도록 만들어져 있다.

```cpp
FileSystem& tfs() {                 // this replaces the tfs object; it could be static in the FileSystem class
    static FileSystem fs;           // define and initialize a local static object
    return fs;                      // return a reference to it
}
```