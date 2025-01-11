---
title: "Effective Modern C++"
date: "2024-12-24"
author: "Beomsu Lee"
tags: ["c++", "language", "effective"]
---

## Deducing Types


### Item 1: Understand template type deduction

예를 들어 함수 템플릿 선언이 다음과 같다고 하자.

```cpp
template<typename T> 
void f(const T& param); // ParamType is const T&
```

그리고 이를 다음과 같이 호출한다.

```cpp
int x = 0;

f(x); // call f with an int
```

이 경우 `T`는 `int`로 추론되나 `ParamType`은 `const int&`로 추론된다.

`T`에 대해 추론된 타입은 `expr` 타입 뿐만 아니라 `ParamType`의 타입에도 의존한다. 타입에 따라 총 3가지 경우로 나뉜다.

1. `ParamType`이 포인터 또는 참조 형식이지만 보편 참조(universal reference)는 아닌 겨웅
2. `ParamType`이 보편 참조인 경우
3. `ParamType`이 포인터도 아니고 참조도 아닌 경우

#### 경우 1: ParamType이 포인터 또는 참조 타입이지만 보편 참조는 아님

이 경우 타입 추론은 다음과 같이 진행된다. 

1. `expr`이 참조 형식이면 참조 부분을 무시
2. 그 다음 `epxr`의 타입을 `ParamType`에 대해 패턴 매칭 방식으로 대응시켜 `T` 타입을 결정

함수 템플릿이 다음과 같고

```cpp
template<typename T>
void f(T& param); // param is a reference
```

다음과 같은 변수 선언들이 있고, 추론되었다고 하자.

```cpp
int x = 27; // x is an int
const int cx = x; // cx is a const int
const int& rx = x; // rx is a reference to x as a const int

f(x); // T is int, param's type is int&
f(cx); // T is const int, param's type is const int&
f(rx); // T is const int, param's type is const int&
```

둘째, 셋째 호출에서 `cx`와 `rx`가 `const` 값이기 때문에 `T`가 `const int`로 추론되었다. 셋째 호출에서 `rx`의 타입이 참조이지만 `T`는 비참조로 추론되었다. 이는 타입 추론 과정에서 `rx`의 참조성(reference-ness)이 무시되기 때문이다.

#### 경우 2: ParamType이 보편 참조임

보편 참조 매개변수의 선언은 오른값 참조와 같은(`T&&`) 모습이지만, 왼값 인수가 전달되면 오른값 참조와는 다른 방식으로 행동한다.

```cpp
template<typename T> 
void f(T&& param); // param is now a universal reference
```

- `expr`이 왼값이면, `T`와 `ParamType` 둘 다 왼값 참조로 추론된다.
- `expr`이 오른값이면 정상적인 규칙(경우 1)이 적용된다. 

```cpp
f(x); // x is lvalue, so T is int&, param's type is also int&
f(cx); // cx is lvalue, so T is const int&, param's type is also const int&
f(rx); // rx is lvalue, so T is const int&, param's type is also const int&
f(27); // 27 is rvalue, so T is int, param's type is therefore int&&
```

#### 경우 3: ParamType이 포인터도 아니고 참조도 아님

이 경우 인수가 함수에 값으로 전달(pass-by-value)되는 상황이다.

```cpp
template<typename T>
void f(T param); // param is now passed by value
```

따라서 `param`은 주어진 인수의 복사본, 즉 새로운 객체이다. 그러므로 `expr`에서 `T`가 추론되는 과정에서 다음과 같은 규칙이 적용된다.

1. `expr`의 타입이 참조이면 참조 부분은 무시된다.2
2. `expr`의 참조성을 무시한 후, 만약 `expr`이 `const`라면 그 `const` 역시 무시한다. 만일 `volatile`이면 이것도 무시한다.

```cpp
f(x); // T's and param's types are both int
f(cx); // T's and param's types are again both int
f(rx); // T's and param's types are still both int
```

#### 배열 인수

배열을 값 전달 매개변수를 받는 템플릿에 전달하면

```cpp
const char * ptrToName = name;

template<typename T>
void f(T param);      // template with by-value parameter

f(name);              // what types are deduced for T and param?
```

타입 매개변수 `T`는 `const char*`로 추론된다(`name`은 배열이지만). 

비록 함수의 매개변수를 진짜 배열로 선언할 수 없지만, 배열에 대한 참조로는 선언할 수 있다. 즉, 다음처럼 템플릿 `f`가 인수를 참조로 받도록 수정하고

```cpp
template<typename T>
void f(T& param); // template with by-reference parameter
```

`f` 함수에 배열(`name`)을 전달하면 `T`에 대해 추론된 타입은 배열의 실제 타입이 된다. 이 타입은 배열의 크기를 포함하므로, `T`는 `const char [13]`으로 추론되고, `f`의 매개변수 타입은 `const char (&)[13]`으로 추론된다.

#### 함수 인수

함수 타입도 함수 포인터로 추론될 수 있으며, 배열에 대한 타입 추론과 동일하게 적용된다.

### Item 2: Understand auto type deduction

템플릿 타입 추론과 `auto` 타입 추론은 알고리즘적으로 상호 변환이 가능하다.

```cpp
template<typename T>
void f(ParamType param);

f(expr); // call f with some expression
```

`f`를 호출할 때 컴파일러는 `expr`을 이용해 `T`의 타입과 `ParamType`을 추론한다. 

`auto`를 이용해 변수를 선언할 때 `auto`는 템플릿의 `T`와 동일한 역할을 하며, 변수의 타입 지정자(type specifier)는 `ParamType`과 동일한 역학을 한다.

```cpp
auto x = 27;
const auto cx = x;  // type specifier is const auto
const auto& rx = x; //type specifier is const auto &
```

`x`, `cx`, `rx`의 타입들을 추론할 때, 컴파일러는 마치 선언마다 템플릿 함수 하나와 해당 초기화 표현식으로 그 템플릿 함수를 호출하는 구문이 존재하는 것처럼 행동한다.

```cpp
template<typename T>               // conceptual template for deducing x's type
void func_for_x(T param);          
func_for_x(27);                    // conceptual call: param's deduced type is x's type
 
template<typename T>               // conceptual template for deducing cx's type
void func_for_cx(const T param); 
func_for_cx(x);                    // conceptual call: param's deduced type is cx's type

template<typename T>               // conceptual template for deducing rx's type
void func_for_rx(const T& param);
func_for_rx(x);                    // conceptual call: param's deduced type is rx's type
```

`auto`의 타입 추론은 템플릿 타입 추론과 동일하게 작동한다.

그러나 다른 점이 있다. `int` 변수를 선언하는 예를 보면, 아래의 두 선언은 값이 27인 원소 하나를 담은 `std::initializer_list<int>` 타입의 변수를 선언한다.

```cpp
auto x1 = 27;     // type is int, value is 27
auto x2(27);      // ditto
auto x3 = { 27 }; // type is std::initializer_list<int>, value is { 27 }
auto x4{ 27 };    // ditto
```

이는 `auto`에 대한 특별한 타입 추론 규칙 때문이다. `auto`로 선언된 변수의 초기치(initializer)가 중괄호 쌍으로 감싼 형태이면, 추론된 타입은 `std::initiazlier_list`이다. 만약 이런 타입을 추론할 수 없으면 컴파일이 거부된다.

C++14에서는 함수의 반환 타입을 `auto`로 지정해 컴파일러가 추론하게 만들 수 있으며, 람다의 매개변수 선언에 `auto`를 사용하는 것도 가능하다. 하지만 이 용법들에는 `auto` 타입 추론이 아니라 템플릿 타입 추론 규칙이 적용된다.

### Item 3: Understand decltype

`decltype`은 주어진 이름이나 표현식의 타입을 알려준다.

`decltype`은 반환 타입이 그 매개변수 타입들에 의존하는 함수 템플릿을 선언할 때 주로 사용된다.

```cpp
template<typename Container, typename Index> // works, but requires refinement 
auto authAndAccess(Container& c, Index i)    
  -> decltype(c[i])
{
  authenticateUser();
  return c[i];
}
```

함수 이름 앞에 있는 `auto`는 타입 추론과는 관련이 없다. 이 `auto`는 여기에 후행 반환 타입(trailing return type) 구문이 쓰인다는 것을 나타낸다. 즉, 반환 타입을 이 위치가 아니라 매개변수 목록 다음(`->`) 선언하겠다는 점을 나타낸다. 이러한 후행 반환 타입을 매개변수들을 이용해 지정할 수 있다는 장점이 있다. 위 예에서는 `c`와 `i`를 이용해 반환 타입을 지정했다.

C++14에서는 후행 반환 타입(`-> decltype(c[i])`)을 생략하고 그냥 함수 이름 앞에 `auto`만 남겨도 된다. 이러한 형태의 선언에서는 실제로 `auto`가 타입 추론이 일어나는 것을 의미한다.

Item 2에서 설명했듯, 함수의 반환 타입에 `auto`가 지정되어 있으면 컴파일러는 템플릿 타입 추론을 적용한다. `T` 객체들을 담은 컨테이너에 대한 `operator[]` 연산은 대부분의 경우 `T&`를 반환한다. 그러나 문제는 Item 1에서 설명했듯 템플릿 타입 추론 과정에서 초기화 표현식의 참조성이 무시된다는 것이다.

```cpp
std::deque<int> d;
...
authAndAccess(d, 5) = 10;  // authenticate user, return d[5],
                           // then assign 10 to it; 
                           // this won't compile!
```

`d[5]`는 `int&`를 돌려주지만, `authAndAccess()`에 대한 `auto` 반환 타입이 타입 추론 과정에서 참조가 제거되기 때문에 결국 반환 타입은 `int`가 된다. 이 값은 rvalue이며 결과적으로 rvalue에 10을 할당하려 하기 때문에 컴파일이 되지 않는다.

따라서 `authAndAccess()`가 `c[i]`의 반환 타입과 동일한 타입을 반환하게 만들어야 한다. 이는 `decltype(auto)` 지정자를 통해 가능하게 만들 수 있다. `auto`는 해당 타입이 추론되어야 함을 뜻하고, `decltype`은 추론 과정에서 `decltype` 타입 추론 규칙이 적용되어야 함을 뜻한다.

```cpp
template<typename Container, typename Index> // C++14; works, but still requires refinement
decltype(auto)
authAndAccess(Container& c, Index i)
{
  authenticateUser();
  return c[i];
}
```

다음은 C++14 버전의 `authAndAccess()` 선언이다.

```cpp
template<typename Container, typename Index>
decltype(auto) authAndAccess(Container& c, Index i);
```

### Item 4: Know how to view deduced types

컴파일러가 추론하는 타입을 IDE 편집기나 컴파일러 오류 메시지, Boost.TypeIndex 라이브러리를 이용해 파악할 수 있는 경우가 많다.

## auto

### Item 5: Prefer auto to explicit type declarations

`auto` 타입은 해당 초기치로부터 추론되므로, 반드시 초기치를 제공해야 한다. 따라서 초기화를 빼먹는 실수를 저지를 여지가 사라진다. 

지역 변수 선언에서 변수의 값을 반복자 역참조로 초기화하는 것도 가능하다.

```cpp
template<typename It> // as before
void dwim(It b, It e)
  {
    while (b != e) {
      auto currValue = *b; // typename std::iterator_traits<It>::value_type => auto
      ...
    } 
  }
```

그리고 `auto`는 타입 추론을 사용하므로(Item 2), 예전에는 컴파일러만 알던 타입을 지정할 수 있다.

```cpp
auto derefUPLess =                       // comparison func.
  [](const std::unique_ptr<Widget>& p1,  // for Widgets
     const std::unique_ptr<Widget>& p2)  // pointed to by
  { return *p1 < *p2; };                 // std::unique_ptrs
```

`std::function`은 호출 가능한 객체이면 어떤 것도 가리킬 수 있다. 

```cpp
bool(const std::unique_ptr<Widget>&,  // C++11 signature for
     const std::unique_ptr<Widget>&)  // std::unique_ptr<Widget>
                                      // comparison function
```

위 함수 시그니처에 해당하는 `std::function`을 생성한다고 하면 다음과 같을 것이다.

```cpp
std::function<bool(const std::unique_ptr<Widget>&,
                   const std::unique_ptr<Widget>&)> func;
```

람다 표현식이 산출하는 클로저는 호출 가능 객체이므로, `std::function` 객체에 저장할 수 있다.

```cpp
std::function<bool(const std::unique_ptr<Widget>&,
                   const std::unique_ptr<Widget>&)>
  derefUPLess = [](const std::unique_ptr<Widget>& p1,
                   const std::unique_ptr<Widget>& p2)
                  { return *p1 < *p2; };
```

이 때 `std::function`을 사용하는 것과 `auto`로 선언하는 것 사이 중요한 차이가 있다. 

`auto`로 선언된 그리고 클로저를 담는 변수는 그 클로저와 같은 형식이며, 따라서 그 클로저에 요구되는 만큼의 메모리만 사용한다.

그러나 클로저를 담는 `std::function`으로 선언된 변수 타입은 `std::function` 템플릿의 한 인스턴스이며, 이 크기는 임의의 주어진 시그니처에 대해 고정되어 있다. 그런데 이 크기는 요구된 클로저를 저장하기에 부족할 수 있으며, 이런 경우 `std::function`은 힙 메모리를 할당해 클로저를 저장한다. 

즉, `std::function` 객체는 `auto`로 선언된 객체보다 메모리를 더 많이 소비한다. 그리고 인라인화(inlining)를 제한하고 간접 함수 호출을 산출하는 구현 세부사항 때문에 `std::function` 객체를 통해 클로저를 호출하는 것은 거의 항상 `auto`로 선언된 객체를 통해 호출하는 것보다 느리다.

### Item 6: Use the explicitly typed initializer idiom when auto deduces undesired types

`Widget`을 받아서 `std::vector<bool>`을 돌려주는 함수가 있다고 하자.

```cpp
Widget w; ...
bool highPriority = features(w)[5];  // is w high priority?
processWidget(w, highPriority);      // process w in accord
                                     // with its priority
```

`highPriority`의 명시적 타입을 `auto`로 대체하면 상황이 달라진다. 컴파일은 되나 그 행동을 예측할 수 없다.

```cpp
auto highPriority = features(w)[5]; // is w high priority?
processWidget(w, highPriority);      // undefined behavior!
```

`auto`를 사용하는 버전에서 `highPriority` 타입은 더 이상 `bool`이 아니다. 

`std::vector<bool>`은 `bool`을 담는 컨테이너다. 그러나 `std::vector<bool>`의 `operator[]`가 돌려주는 것은 그 컨테이너의 한 요소에 대한 참조가 아닌, `std::vector<bool>::reference` 타입(`std::vector<bool>` 안에 내포된 클래스)의 객체이다.

`std::vector<bool>::reference`가 존재하는 것은 `std::vector<bool>`이 자신의 `bool`들을 `bool` 당 1비트의 압축된 타입으로 표현하도록 명시되어 있기 때문이다. 따라서 `operator[]`를 직접 구현할 수 없다. `std::vector<T>`의 `operator[]`는 `T&`를 돌려주지만, C++에서 비트에 대한 참조는 금지되어 있다. 따라서 `std::vector<bool>`의 `operator[]`는 마치 `bool&`처럼 작동하는 객체를 돌려주도록 우회책을 사용한 것이다. 

명시적 타입을 사용한 경우(`bool highPriority`) `features()`는 `std::vector<bool>` 객체를 돌려주며, 이 객체에 대해 `operator[]`가 호출된다. `operator[]`는 `std::vector<bool>::reference`를 돌려주며, 이 객체가 암묵적으로 `bool`로 변환되어 5번 비트가 `highPriority` 초기화에 쓰인다.

`au
to`를 사용할 경우(`auto highPriority`) `std::vector<bool>::reference` 객체를 돌려주는 것 까지는 동일하다. 그러나 `auto`에 의해 `highPriority` 타입이 추론되기 때문에 `std::vector<bool>` 타입의 5번 비트로 초기화되지 않게 된다.

이때 `highPriority`가 가지는 값은 `std::vector<bool>::reference` 구현 방식에 따라 다르다. 이 구현 방식 중 하나는 그 객체의 참조된 비트를 담은 기계어 워드(word)를 가리키는 포인터 하나와 이 워드의 비트들 중 참조된 비트의 위치를 뜻하는 오프셋으로 구성된다. 이 경우 `features()`는 임시 `std::vector<bool>` 객체(`temp`라 하자)를 돌려주며, 이 객체에는 `temp`가 관리하는 비트들을 담은 자료구조의 한 워드를 가리키는 포인터와 그 워드에서 참조된 비트(5번)에 해당하는 비트의 오프셋이 담겨 있다. 따라서 `highPriority`는 `std::vector<bool>::reference` 객체의 한 복사본이며, `highPriority` 역시 `temp` 안의 해당 워드를 가리키는 포인터와 5번 비트 오프셋을 담게 된다. 즉, `highPriority`의 포인터는 댕글링 포인터가 되며 미정의 행동을 유발한다.

`std::vector<bool>::reference`는 프록시 클래스(프록시 패턴), 즉 어떤 형식을 흉내내고 보강하는 것이 존재 이유인 클래스다. 프록시 패턴 중 클라이언트에게 명백히 드러나도록 설계된 것의 대표적인 예로 `std::shared_ptr`, `std::unique_ptr`가 있다. 반면 다른 프록시 패턴들은 다소 은밀하게 동작되도록 설계되었다.

이러한 *보이지 않는* 프록시 클래스는 `auto`와 잘 맞지 않는다. 

보통 프록시 클래스는 그 존재가 드러나지 않도록 설계되었지만, 그래도 라이브러리 문서에서 프록시 클래스의 존재가 명시되어 있는 경우가 많다. 이러한 방식을 통해 `auto`가 프록시 클래스 타입을 추론한다는 것을 알았다고 하자. 이때 `auto`가 다른 타입을 추론하도록 강제할 수 있다.

> explicitly typed initializer idiom.

변수를 `auto`로 선언하되 초기화 표현식의 타입을 `auto`가 추론하길 원하는 타입으로 캐스팅한다. 

```cpp
auto highPriority = static_cast<bool>(features(w)[5]);
```

이전과 같이 `std::vector<bool>::reference`를 돌려주나, 캐스팅 때문에 표현식 타입은 `bool`이 되어, `std::vector<bool>::operator[]`가 돌려준 `std::vector<bool>::reference` 객체는 자신이 지원하는 `bool`로의 변환을 수행하며, 그 변환 도중 `features()`가 돌려주는 `std::vector<bool>`을 가리키는 포인터가 역참조된다. 이 시점에서 포인터는 여전히 유효하므로, 미정의 행동 이슈는 더 이상 발생하지 않는다.

## Moving to Modern C++

### Item 7: Distinguish between () and {} when creating objects

C++11에서는 중괄호 초기화(uniform initialization)을 도입했다. 어디서나 사용할 수 있고 모든 것을 표현할 수 있는 초기화 구문이다.

```cpp
int x(0);      // initializer is in parentheses
int y = 0;     // initializer follows "="
int z{ 0 };    // initializer is in braces
int z = { 0 }; // initializer uses "=" and braces
```

복사할 수 없는 객체(`std::atomic`)는 중괄호나 괄호로는 초기화할 수 있지만, `=`로는 초기화할 수 없다.

```cpp
std::atomic<int> ai1{ 0 }; // fine
std::atomic<int> ai2(0);   // fine 
std::atomic<int> ai3 = 0;  // error!
```

중괄호 초기화 기능 중 하나는 내장 기능들 사이 암묵적 좁히기 변환(narrowing conversion)을 방지해준다는 것이다. 중괄호 초기치에 있는 어떤 표현식의 값을 초기화하려는 객체의 타입으로 온전히 표현할 수 있음이 보장되지 않는 경우, 컴파일러는 그 사실을 보고해야 한다.

```cpp
double x, y, z;
...
int sum1{ x + y + z }; // error! sum of doubles may not be expressible as int
```

중괄호 초기화의 또 다른 주목할 점은 *most vexing parse*에서 자유롭다는 것이다. most vexing parse는 "선언으로 해석할 수 있는 것은 항상 선언으로 해석해야 한다."는 C++ 규칙에서 비롯된 하나의 부작용인데, 기본 생성자를 이용해 객체를 생성하려 했지만 의도와 달리 함수를 선언하게 되었을 때 이를 경험한 것이다.

```cpp
Widget w2(); // most vexing parse! declares a function 
             // named w2 that returns a Widget!
```

중괄호를 이용해 객체를 생성할 때는 이런 문제를 겪지 않는다.

`auto`를 사용한 중괄호 초기화에서 `std::initializer_list` 타입으로 추론되는 경우가 많다. 생성자 호출에서 `std::initializer_list`  매개변수가 관여하지 않는 한 괄호와 중괄호의 의미는 같다. 

그러나 생성자 중 하나 이상이 `std::initializer_list` 타입의 매개변수를 선언한다면, 중괄호 초기화 구문은 `std::initializer_list`를 받는 오버로딩 버전을 강하게 선호한다. 중괄호 초기치가 쓰인 호출을 `std::initializer_list`를 받는 버전의 생성자 호출로 해석할 여지가 조금이라도 있다면 컴파일러느 반드시 그 해석을 선택한다.

```cpp
class Widget {
public:
  Widget(int i, bool b);   // as before
  Widget(int i, double d); // as before
  Widget(std::initializer_list<long double> il); // added ...
};

Widget w1(10, true);  // uses parens and, as before, calls first ctor
Widget w2{10, true};  // uses braces, but now calls std::initializer_list ctor
                      // (10 and true convert to long double)
Widget w3(10, 5.0);   // uses parens and, as before, calls second ctor
                      // uses braces, but now calls
Widget w4{10, 5.0};   // std::initializer_list ctor
                      // (10 and 5.0 convert to long double)
```

컴파일러는 중괄호 초기치의 인수 타입들을 `std::initializer_list` 안의 타입으로 아예 변환할 수 없을때에만 다른 생성자를 선택한다.

또 하나 흥미로운 경우를 보면, 기본 생성을 지원하며 `std::initializer_list` 생성도 지원하는 객체를 빈 중괄호 쌍으로 생성한다고 하자. 표준에 따르면 컴파일러는 기본 생성자가 호출된다. 즉, 빈 중괄호 쌍은 빈 `std::initializer_list`가 아니라 인수 없음을 뜻한다.

```cpp
Widget w1;   // calls default ctor 
Widget w2{}; // also calls default ctor
Widget w3(); // most vexing parse! declares a function!
```

`std::initializer_list` 생성자를 호출하고 싶다면 빈 중괄호 쌍을 괄호로 감싸거나(`Widget w4({});`), 빈 중괄호 쌍을 또 다른 중괄호 쌍으로 감싸면(`Widget w5{{}};`) 된다.

결과적으로 클래스 사용자로서 객체를 생성할 때는 괄호와 중괄호를 세심하게 선택해야 한다. 두 방식 모두 장단점이 있으므로 둘 중 하나를 선택해 일관되게 적용하도록 하자.

### Item 8: Prefer nullptr to 0 and NULL

`nullptr`은 정수 타입 또는 포인터 타입이 아니다. `nullptr`의 실제 타입은 `std::nullptr_t`인데 `std::nullptr_t` 자체는 다시 `nullptr`의 타입으로 정의된다. `std::nullptr_t`는 모든 raw pointer 타입으로 암묵적으로 변환되며, 따라서 `nullptr`은 마치 모든 타입의 포인터처럼 행동한다.

```cpp
auto result = findRecord( /* arguments */ );
if (result == nullptr) { 
  ...
}
```

`findRecord()`의 타입을 모른다면 `result`가 포인터 타입인지 정수 타입인지 명확히 알 수 없다. 따라서 `result == 0`인 경우 `0`은 포인터 타입으로도, 정수 타입으로도 작용할 수 있다. 하지만 `result == nullptr` 같은 코드는 중의성이 없으며 `result`는 포인터 타입임이 명확하다. 

다음 템플릿을 보자.

```cpp
template<typename FuncType,
         typename MuxType,
         typename PtrType>
decltype(auto) lockAndCall(FuncType func, // C++14
                           MuxType& mutex, 
                           PtrType ptr)
{
  MuxGuard g(mutex);
  return func(ptr);
}

auto result1 = lockAndCall(f1, f1m, 0); // error!
auto result2 = lockAndCall(f2, f2m, NULL); // error! 
auto result3 = lockAndCall(f3, f3m, nullptr); // fine
```


`lockAndCall()`에 `0`을 전달하면 `0`의 타입을 파악하기 위해 템플릿 타입 추론을 수행하는데, `0`의 타입은 항상 `int`이므로 매개변수와 호환되지 않아 컴파일 오류가 발생한다. `NULL` 또한 동일한 이유로 오류를 발생시킨다.

반면, `nullptr`은 `std::nullptr_t`로 추론되고, `ptr`을 `func`에 전달하면 `std::nullptr_t`에서 `Widget*`으로 암묵적 변환이 일어난다. `std::nullptr_t`는 암묵적으로 모든 포인터 타입으로 변환되기 때문이다.

### Item 9: Prefer alias declarations to typedefs

`typedef`를 사용해 간단하게 표현할 수 있지만, 이는 C++98의 유물이다. 

```cpp
typedef
  std::unique_ptr<std::unordered_map<std::string, std::string>>
  UPtrMapSS;
```

C++11에서도 `typedef`가 동작하나 별칭 선언(alias declaration)도 제공하고 있다. `typedef`와 별칭 선언이 하는 일을 정확히 동일하다.

```cpp
using UPtrMapSS =
  std::unique_ptr<std::unordered_map<std::string, std::string>>;
```

별칭 선언이 강력한 이유는 템플릿에 있다. `typedef`는 템플릿화할 수 없지만, 별칭 선언은 템플릿화할 수 있다. 

`MyAlloc`이라는 커스텀 할당자를 사용하는 링크드 리스트의 동의어를 정의한다고 하자. `using`을 사용할 경우 간단하지만

```cpp
template<typename T> // MyAllocList<T> 
using MyAllocList = std::list<T, MyAlloc<T>>; // is synonym for
                                              // std::list<T, MyAlloc<T>>
MyAllocList<Widget> lw; // client code
```

`typedef` 버전은 템플릿화가 불가능해 복잡한 구조가 된다.

```cpp
template<typename T> // MyAllocList<T>::type 
struct MyAllocList { // is synonym for
  typedef std::list<T, MyAlloc<T>> type; // std::list<T, MyAlloc<T>>
};
MyAllocList<Widget>::type lw;            // client code
```

또한 템플릿 매개변수로 지정된 타입의 객체들을 담는 링크드 리스트를 생성하려는 목적으로 템플릿 안에서 `typedef`를 사용하려면 `typename`를 붙여야 한다.

```cpp
template<typename T>
class Widget {                        // Widget<T> contains
  private:                            // a MyAllocList<T>
  typename MyAllocList<T>::type list; // as a data member
  ... 
};
```

여기서 `MyAllocList<T>::type`는 템플릿 타입 매개변수(`T`)에 의존적인 타입을 지칭한다.  

`MyAllocList`를 별칭 선언으로 지정하면 `typename`을 붙일 필요가 없다.

```cpp
template<typename T>
  using MyAllocList = std::list<T, MyAlloc<T>>;  // as before

template<typename T>
class Widget {
private:
  MyAllocList<T> list;  // no "typename", no "::type"
  ... 
};
```

`MyAllocList<T>`는 템플릿 매개변수 `T`에 의존하는 것 같지만, 컴파일러는 그렇게 여기지 않는다. 컴파일러가 `Widget`을 처리하는 과정에서 `MyAllocList<T>`에 도달했을 때, 컴파일러는 이 `MyAllocList<T>`가 타입의 이름임을 이미 알고 있다. 즉, `MyAllocList<T>`는 비의존적 타입이므로 `typename` 지정자를 붙일 필요가 없다. 

반면, `Widget` 템플릿 안에서 `MyAllocList<T>::type`을 만난 컴파일러는 이 타입이 이름임을 확신하지 못한다(Effective C++ Item 42 참고). 

### Item 10: Prefer scoped enums to unscoped enums

일반적으로 중괄호 쌍 안에서 어떤 이름을 선언하면 그 이름의 가시성은 해당 중괄호 쌍이 정의하는 범위로 한정된다. 그러나 C++98 스타일의 `enum`으로 선언된 열거자(enumerator)는 이런 규칙이 적용되지 않는다. 이런 종류의 `enum`을 범위 없는(unscoped) `enum`이라 한다. 

이에 대응되는 C++11의 범위 있는(scoped) `enum`에서는 이름 누수가 발생하지 않는다.

```cpp
enum class Color { black, white, red }; // black, white, red are scoped to Color

auto white = false;       // fine, no other "white" in scope
Color c = white;          // error! no enumerator named "white" is in this scope
Color c = Color::white;   // fine
auto c = Color::white;    // also find (and in accord with Item 5's advice)
```

`enum class`의 또 다른 장점으로 타입에 더 강력하게 적용된다는 것이다. `enum`은 암묵적으로 정수 타입으로 변환되어 다음과 같은 코드를 만났을 때 의미론적 재앙이 유효하다.

```cpp
Color c = red;
if (c < 14.5) {         // compare Color to double (!)
  auto factors =        // compute prime factors of a Color (!)
    primeFactors(c);
  ... 
}
```

그러나 `enum class`는 암묵적으로 다른 타입으로 변환되지 않아 위와 같은 문제는 발생되지 않는다.

추가로 `enum class`는 전방 선언(forward declaration)이 가능하다. 즉, 열거자들을 지정하지 않고 열거형 이름만 미리 선언할 수 있다. 따라서 전방 선언된 `enum class`를 포함하는 헤더는 다시 컴파일하지 않아도 된다.

```cpp
enum Color;               // error!
enum class Color;         // fine
```

### Item 11: Prefer deleted functions to private undefined ones

C++98에서는 사용을 금지하려는 멤버 함수(복사 생성자, 복사 할당자 등)들을 `private`으로 선언하고 정의하지 않는 방식을 사용했다.

`iostream` 계통 구조의 뿌리 부근에는 `basic_ios`라는 클래스 템플릿이 있다. 여기서 입력 스트림이나 출력 스트림 객체는 복사하지 않는 것이 좋은데, 이는 그 객체에 대한 복사 연산이 구체적으로 어떤 일을 해야 할 것인지가 명확하지 않기 때문이다. 

입출력 스트림 클래스들의 복사를 방지하기 위해 C++98에서는 `private` 섹션에 선언만 수행한다.

C++11에서는 같은 목적을 달성하기 위해 `= delete`를 사용한다. 

```cpp
template <class charT, class traits = char_traits<charT> > 
class basic_ios : public ios_base {
public:
  ...
  basic_ios(const basic_ios& ) = delete; 
  basic_ios& operator=(const basic_ios&) = delete; 
  ...
};
```

삭제된 함수는 어떤 방법으로든 사용할 수 없다. 

> 삭제할 함수는 `private`이 아니라 `public`으로 선언하는 것이 관례이다.

배제할 타입들에 대해 함수 오버로딩을 명시적으로 삭제하여 컴파일되지 않도록 할 수 있다.

```cpp
bool isLucky(int number);      // original function
bool isLucky(char) = delete;   // reject chars
bool isLucky(bool) = delete;   // reject bools
bool isLucky(double) = delete; // reject doubles and floats
```

`char*`(C 스타일 문자열), `void*`(역참조나 증가, 감소가 불가)와 같이 특별한 포인터들을 처리가 필요한 경우가 많은데, `processPointer()` 템플릿은 이 타입들을 이용한 호출을 아예 거부하는 것이라 하자. 단순히 템플릿 인스턴스들을 삭제하면 된다.

```cpp
template<>
void processPointer<void>(void*) = delete;
template<>
void processPointer<char>(char*) = delete;
```

### Item 12: Declare overriding functions override

가상 함수 재정의는 파생 클래스 함수를 기반 클래스의 인터페이스를 통해 호출할 수 있게 만드는 메커니즘이다. 

재정의가 일어나려면 다음과 같은 조건을 만족해야 한다.

- 기반 클래스 함수가 반드시 가상 함수여야 한다.
- 기반 함수와 파생 함수의 이름이 반드시 동일해야 한다.
- 기반 함수와 파생 함수의 매개변수 타입들이 동일해야 한다.
- 기반 함수와 파생 함수의 상수(const)성이 반드시 동일해야 한다.
- 기반 함수와 파생 함수의 반환 타입과 예외 명세가 반드시 호환되어야 한다.
- 멤버 함수들의 참조 한정사(reference qualifier)들이 반드시 동일해야 한다. 멤버 함수 참조 한정사 기능을 이용하면 멤버 함수를 왼값에만 또는 오른값에만 사용할 수 있게 제한할 수 있다(C++11).
  - 기반 클래스의 가상 함수에 참조 한정사가 있으면, 그 함수를 재정의하는 파생 클래스의 함수에도 정확히 같은 참조 한정사가 있어야 한다는 것을 기억하자.

```cpp
class Base {
public:
  virtual void mf1() const; 
  virtual void mf2(int x); 
  virtual void mf3() &; 
  virtual void mf4() const;
};

class Derived: public Base {
public:
  virtual void mf1() const override;
  virtual void mf2(int x) override;
  virtual void mf3() & override; 
  void mf4() const override;       // adding "virtual" is OK, but not necessary
};
```

### Item 13: Prefer const_iterators to iterators

`const_iterator`는 `const`를 가리키는 포인터의 STL 버전이다. C++11에서는 `const_iterator`를 C++98에 비해 얻기도 쉽고 사용하기도 쉽다. `cbegin()`, `cend()`는 `const_iterator`를 반환한다. 삽입, 삭제 위치를 지정하는 목적으로 반복자를 사용하는 STL 멤버 함수들은 `const_iterator`를 사용한다.

다음은 `const_iterator`를 C++98 코드에서 사용하는 실용적인 코드이다.

```cpp
std::vector<int> values; // as before ...
auto it =                // use cbegin
  std::find(values.cbegin(),values.cend(), 1983); // and cend
values.insert(it, 1998);
```

### Item 14: Declare functions noexcept if they won’t emit exceptions

C++11에서는 함수가 예외를 하나라도 던질 수 있는지 아니면 절대 던지지 않는지 이분법적 논리를 적용했다. C++11에서 함수 선언 시 그 함수가 예외를 방출하지 않을 것임을 명시할 때 `noexcept`라는 키워드를 사용하면 된다.

함수를 `noexcept`로 선언할 것인지 여부는 인터페이스 설계상의 문제다. 함수의 예외 방출은 클라이언트에게는 아주 중요한 사항이다. 함수의 호출자는 함수의 `noexcept` 여부를 조회할 수 있으며, 그 조회 결과는 호출 코드의 예외 안정성이나 효율성에 영향을 미친다. 

예외를 방출하지 않는 함수에 `noexcept`를 적용하면 컴파일러가 더 나은 목적 코드(object code)를 산출할 수 있다. 예를 들어 함수 `f()`를 호출했을 때 호출자가 예외를 받는 일이 결코 없음을 약속하는 것을 표현하는 방법은 두 가지다.

```cpp
int f(int x) throw();  // no exceptions from f: C++98 style 
int f(int x) noexcept; // no exceptions from f: C++11 style
```

C++98에서는 예외 명세가 위반되면 호출 스택이 `f()`를 호출한 지점에 도달할 때까지 풀리며(unwind), 그 지점에서 몇 가지 동작이 취해진 후 프로그램이 종료된다.

C++11에서는 프로그램 실행이 종료되기 전 호출 스택이 풀릴 수도 있고, 되지 않을 수도 있다. 이는 컴파일러 코드 작성이 큰 영향을 미친다. `noexcept` 함수에서 컴파일러의 최적화는 예외 함수가 바깥으로 전파될 수 있다고 해도 런타임 스택을 풀기 가능한 상태로 유지할 필요가 없다. 또한 예외가 `noexcept` 함수를 벗어난다고 해도 `noexcept` 함수 안 객체들을 반드시 생성 반대 순서로 파괴해야 하는 것도 아니다. 예외 명세가 `throw`이거나 명세가 아예 없는 함수는 이런 최적화 유연성이 없다. 

```cpp
RetType function(params) noexcept; // most optimizable
RetType function(params) throw();  // less optimizable
RetType function(params);          // less optimizable
```

대부분의 함수는 **예외에 중립적(exception-neutral)** 이다. 예외 중립적 함수는 스스로 예외를 던지지 않지만, 예외를 던지는 다른 함수를 호출할 수 있다. 어떤 함수가 예외를 던지면 예외 중립적 함수는 그 예외를 그대로 통과시킨다. 따라서 예외 중립적 함수는 결코 `noexcept`가 될 수 없다. 

> `noexcept`로 선언하는 것이 중요한 일부 함수들은 기본적으로 `noexcept`로 선언된다. 기본적으로 메모리 해제 함수와 모든 소멸자는 암묵적으로 `noexcept`다. 따라서 이런 함수들은 직접 `noexcept`로 선언할 필요가 없다.

라이브러리 인터페이스 설계자들 중 넓은 계약(wide contract)들을 가진 함수와 좁은 계약(narrow contract)들을 가진 함수를 구분하는 사람들이 있다.

- 넓은 계약을 가진 함수는 전제조건이 없는 함수를 말한다. 이런 함수는 프로그램 상태와는 무관하게 호출할 수 있으며, 호출자가 전달하는 인수에 어떠한 제약도 가하지 않는다. 넓은 계약 함수는 미정의 행동을 보이지 않는다.
- 넓은 계약을 가진 함수가 아닌 함수들은 모두 좁은 계약을 가진 함수이다. 이런 함수의 경우 함수의 전제 조건이 위반되면 이 결과는 미정의 행동으로 나타난다.

넓은 계약을 가진 함수를 작성할 때, 이 함수가 예외를 던지지 않는다면 `noexcept`로 선언하는 것은 쉽다. 그러나 좁은 계약의 경우 조금 더 까다롭다. `std::string` 매개변수를 받는 `f()` 함수를 작성하는데, `f()` 구현이 결코 예외를 방출하지 않는다고 하자. 그렇다면 `f()`는 `noexcept`로 선언해야 한다.

그런데 `f()`에 `std::string` 매개변수 길이가 32자를 넘지 않아야 한다는 전제조건이 있다고 하자. 길이가 32를 넘는 `std::string`으로 호출한 결과는 미정의 행동에 해당한다. 때문에 `f()`는 이러한 전제조건을 점검해야 할 의무가 없다. 그렇다면 `f()`를 `noexcept`로 선언하는 것은 합당하다.

`f()`의 구현자가 전제조건 위반을 `f()`에서 직접 점검한다고 하자. "전제조건 위반" 예외를 던질 수 있지만, `noexcept`로 선언되어 있어 이 방법은 불가능할 수 있다. 따라서 설계자들은 넓은 계약을 가진 함수들에 대해서만 `noexcept`를 사용하려는 경향이 있다.

### Item 15: Use constexpr whenever possible

`constexpr`이 적용된 객체는 실제로 `const`이며, 그 값은 컴파일 시점에 알려진다. 

상수이자 컴파일 시점에서 알려진 정수 값을 C++에서 **정수 상수 표현식(integral constant expression)** 이 요구되는 문맥(배열 크기, 정수 템플릿 인수, 열거자 값, alignment 지정자 등)에서 사용할 수 있다. 이러한 변수를 `constexpr`로 선언하면 컴파일러는 이것이 컴파일 시점 상수임을 보장해준다.

```cpp
int sz;   // non-constexpr variable
...
constexpr auto arraySize1 = sz; // error! sz's value not known at compilation
std::array<int, sz> data1;      // error! same problem

constexpr auto arraySize2 = 10; // fine, 10 is a compile-time constant
std::array<int, arraySize2> data2;  // fine, arraySize2 is constexpr
```

> 모든 `constexpr` 객체는 `const`지만, 모든 `const` 객체가 `constexpr`인 것은 아니다.

`constexpr` 함수는 다음과 같은 특징을 가진다.

- 컴파일 시점 상수를 요구하는 문맥에 `constexpr` 함수를 사용할 수 있다. 이런 문맥에서 `constexpr` 함수에 넘겨주는 인수의 값이 컴파일 시점에 알려진다면, 함수 결과는 컴파일 도중 계산된다. 인수 값이 컴파일 시점에 알려지지 않는다면, 코드의 컴파일이 거부된다.
- 컴파일 시점에 알려지지 않는 하나 이상의 값들로 `constexpr` 함수를 호출하면 함수는 보통의 함수처럼 동작한다. 즉, 런타임에 계산된다.
- `constexpr` 함수는 반드시 리터럴(literal) 타입들을 받고 돌려주어야 한다. C++14에서 모든 빌트인 타입이 리터럴 타입이며, 생성자와 적절한 멤버 함수들이 `constexpr`인 사용자 타입도 리터럴 타입이 될 수 있다.
  
  ```cpp
  class Point {
  public:
    constexpr Point(double xVal = 0, double yVal = 0) noexcept 
    : x(xVal), y(yVal) {}

    constexpr double xValue() const noexcept { return x; } 
    constexpr double yValue() const noexcept { return y; }
  };
  ```

  `Point`의 생성자를 `constexpr`로 선언할 수 있는 이유는, 주어진 인수들이 컴파일 시점에 알려진다면 생성된 `Point` 객체의 자료 멤버들의 값 역시 컴파일 시점에 알려질 수 있기 때문이다.

`constexpr`은 객체나 함수의 인터페이스의 일부라는 점을 명심하자. `constexpr`를 지정한다는 것은 "이 함수(또는 객체)를 C++이 상수 표현식을 요구하는 문맥에서 사용할 수 있다"는 사실을 말하는 것이다.

### Item 16: Make const member functions thread safe

다항식(Polynomial)을 표현하는 클래스가 있다고 하자. 이 클래스는 다항식의 근(root)들, 즉 다항식이 0으로 평가되는 값들을 계산하는 멤버 함수를 갖추어야 할 것이다. 중복된 계산을 피하기 위해 캐시에 저장해 돌려주도록 구현하는 것이 바람직하다.

```cpp
class Polynomial {
  public:
    using RootsType = std::vector<double>;
    RootsType roots() const
    {
      if (!rootsAreValid) {   // if cache not valid
        ...                   // compute roots, store them in rootVals
        rootsAreValid = true;
      }
      return rootVals;
    }
private:
  mutable bool rootsAreValid{ false };  // see Item 7 for info on initializers
  mutable RootsType rootVals{}; 
};
```

`roots()`는 `const`로 선언되어 있어 자신이 속한 `Polynomial` 객체를 변경하지 않는다. 그러나 캐시를 위해선 `rootVals`와 `rootsAreValid`의 변경이 필요할 수 있다. 

만약 두 스레드가 하나의 `Polynomial` 객체에 대해 `roots`를 동시에 호출한다고 한다.

```cpp
Polynomial p;
// ...
/*-----  Thread 1  ----- */     /*-------  Thread 2  ------- */
auto rootsOfP = p.roots();      auto valsGivingZero = p.roots()
```

지금 예에서는 `roots()` 안에서 두 스레드 중 하나나 둘 다가 자료 멤버 `rootVals`와 `rootsAreValid`를 수정하려 할 수 있다. 이는 레이스 컨디션(race condition)이 발생할 수 있다는 것을 의미하며 의도하지 않은 동작을 유발할 수 있다.

이는 뮤텍스를 사용해 해결할 수 있다. 

```cpp
RootsType roots() const
{
  std::lock_guard<std::mutex> g(m); // lock mutex
  if (!rootsAreValid) {             // if cache not valid compute/store roots
    ...
    rootsAreValid = true;
  }
  return rootVals;
}   
```

### Item 17: Understand special member function generation

C++의 special member function들은 C++이 스스로 작성하는 멤버 함수(생성자, 소멸자, 복사 생성자, 복사 할당 연산자)들을 가리킨다. 이 함수들은 꼭 필요한 경우, 즉 이 함수들을 사용하는 클라이언트 코드가 존재할 때에만 작성된다.

C++11은 special member function에 두 가지를 추가했다.

1. 이동 생성자(move constructor)
2. 이동 할당 연산자(move assignment operator)

```cpp
class Widget {
public:
  ...
  Widget(Widget&& rhs);            // move constructor
  Widget& operator=(Widget&& rhs); // move assignment operator
  ... 
};
```

이동 생성자는 주어진 파라미터 `rhs`의 자료 멤버들 각각 **이동 생성**하고, 이동 할당 연산자는 주어진 파라미터 `rhs`의 자료 멤버 각각을 **이동 할당**한다. 기반 클래스 부분도 동일하다.

복사 연산들과 동일하게 명시적으로 선언한 이동 연산들을 자동으로 작성되지 않는다. 그러나 이동 연산들이 작성되는 구체적인 조건은 복사 연산들과는 조금 다르다.

두 복사 연산들을 서로 독립적이다. 둘 중 하나를 선언했다고 해서 다른 하나의 작성이 방지되지 않는다. 예를 들어, 복사 생성자를 선언했지만 복사 할당 연산자를 선언하지 않았고, 복사 할당 연산이 필요한 클라이언트 코드를 작성했다면, 컴파일러가 자동으로 복사 할당 연산자를 작성한다.

그러나 두 이동 연산은 독립적이지 않다. 둘 중 하나를 선언하면 컴파일러는 다른 하나를 작성하지 않는다. 이런 규칙에 깔린 근거는 다음과 같다. 어떤 클래스에 대해 이동 생성자를 선언했다면, 이는 컴파일러가 작성해주는 기본적인 멤버 이동 생성이 해당 클래스에 적합하지 않아 다른 방식으로 구현해야 하기 때문일 것이다. 그리고 멤버별 이동 생성이 적합하지 않다면, 멤버별 이동 할당 역시 적합하지 않을 가능성이 크다. 따라서 이동 생성자와 이동 할당 연산자는 독립적이지 않도록 구현되어 있다.

또한 복사 연산을 하나라도 선언한 클래스에 대해서는 이동 연산들이 작성되지 않는다. 복사 연산을 선언했다는 것은 일반적인 객체 복사 방식이 해당 클래스에 적합하지 않다는 뜻이고, 만일 복사 연산들에 대해 멤버별 복사가 적합하지 않다면 이동 연산들에 대한 멤버별 이동 역시 적합하지 않을 가능성이 크다는 것이다.

반대도 마찬가지다. 이동 연산을 하나라도 명시적으로 선언하면 컴파일러는 복사 연산들을 비활성화 한다. 멤버별 이동이 적절한 객체 이동 방식이 아니라면, 멤버별 복사가 적절한 객체 복사 방식이라고 기대할 수 없다.

**3의 법칙(Rule of Three)** 라 부르는 지침이 있다. 만일 복사 생성자와 복사 할당 연산자, 소멸자 중 하나라도 선언했다면 나머지 둘도 선언해야 한다는 것이다. 어떤 클래스의 복사 할당 연산을 프로그래머가 직접 작성해야 할 때는 거의 그 클래스가 어떤 형태로든 자원 관리를 수행해야 하기 때문에 발생한다. 이러한 클래스에서는 거의 항상

1. 한 복사 연산이 수행하는 자원 관리를 다른 복사 연산에서도 수행해야 하며
2. 클래스의 소멸자 역시 그 자원 관리에 참여한다.

결과적으로 클래스에 대한 이동 연산은 다음 세 조건이 모두 만족될 때만, 그리고 필요할 때만 자동으로 작성된다.

- 클래스에 어떤 복사 연산도 선언되어 있지 않다.
- 클래스에 어떤 이동 연산도 선언되어 있지 않다.
- 클래스에 소멸자가 선언되어 있지 않다.

컴파일러가 작성한 함수들의 행동이 정확하다면 C++11에서 기본 행동을 사용하겠다는 의사를 `= default`를 이용해 명시적으로 표현할 수 있다.

### Item 18: Use std::unique_ptr for exclusive-ownership resource management

`std::unique_ptr`은 raw pointer와 거의 동일한 크기이며, 대부분의 연산들은 raw pointer와 정확히 동일한 명령들을 실행한다. 

`std::unique_ptr`은 독점적 소유권(exclusive ownership) 의미론을 구현하고 있다. `std::unique_ptr`을 이동하면 소유권이 원본 포인터에서 대상 포인터로 옮겨진다(원본은 null로 설정). `std::unique_ptr`의 복사는 허용되지 않는다. 따라서 `std::unique_ptr`은 이동 전용(move-only) 타입이다. null이 아닌 `std::unique_ptr`은 소멸 시 자신이 가리키는 자원을 파괴한다. 

기본적으로 자원 파괴는 `delete`를 통해 일어나나, 커스텀 삭제자(custom deleter)를 지정할 수도 있다.

```cpp
auto delInvmt = [](Investment* pInvestment)   // custom deleter
                {                             // (a lambda expression)
                  makeLogEntry(pInvestment);
                  delete pInvestment;
                };

template<typename... Ts>                      // revised return type
std::unique_ptr<Investment, decltype(delInvmt)>
makeInvestment(Ts&&... params)
{
  // ...
}
```

`std::unique_ptr`이 독점 소유권을 표현하는 주된 방법이라는 것 외에, `std::shared_ptr`로의 변환이 쉽고 효율적인 특징도 있다.

```cpp
std::shared_ptr<Investment> sp = // converts std::unique_ptr 
  makeInvestment( arguments );   // to std::shared_ptr
```

팩토리 함수가 `std::unique_ptr`을 반환한다면, 호출자에서 좀 더 유연하게 변환할 수 있는 여지가 생긴다.

### Item 19: Use std::shared_ptr for shared-ownership resource management

`std::shared_ptr`을 통해 접근되는 객체의 수명은 그 공유 포인터가 공유된 소유권(shared ownership) 의미론을 통해 관리된다. 객체를 가리키던 마지막 `std::shared_ptr`이 더 이상 객체를 가리키지 않게 되면, `std::shared_ptr`은 자신이 가리키는 객체를 파괴한다.

`std::shared_ptr`은 참조 횟수(reference count)를 통해 최후의 공유 포인터임을 알 수 있다. 참조 횟수는 관리되는 자원에 연관된 값으로, 그 자원을 가리키는 `std::shared_ptr`들의 개수에 해당한다.

이러한 참조 횟수 관리는 성능에 다음과 같은 영향을 미친다.

- **`std::shared_ptr`의 크기는 raw pointer의 두 배이다.**
  - 자원 참조 횟수를 가리키는 raw pointer도 저장해야 하기 때문이다.
- **참조 횟수를 담을 메모리를 반드시 동적으로 할당해야 한다.**
  - `std::make_shared`를 이용해 `std::shared_ptr`을 생성하면 동적 할당 비용을 피할 수 있다.
- **참조 횟수의 증가와 감소가 반드시 원자적 연산이어야 한다.**

참조 횟수가 증가하지 않는 경우는 이동 생성을 사용할 경우이다. 기존의 `std::shared_ptr`을 이동해 새로우ㄴ `std::shared_ptr`을 생성하면, 원본 `std::shared_ptr`은 null이 된다. 즉, 새로운 `std::shared_ptr`의 수명이 시작되는 시점에 기존 `std::shared_ptr`은 더 이상 자원을 가리키지 않는 상태가 된다. 따라서 `std::shared_ptr`을 이동하는 것이 복사하는 것보다 빠르다. 

`std::shared_ptr`은 `delete`를 기본적인 자원 파괴 메커니즘으로 사용하며, 커스텀 삭제자(custom deleter)를 지원한다. 그러나 지원하는 방식은 `std::unique_ptr`과는 다르다. `std::unique_ptr`은 삭제자 타입이 스마트 포인터 타입의 일부였지만, `std::shared_ptr`은 그렇지 않다. `std::shared_ptr`의 설계가 더 유연하다.

```cpp
auto loggingDel = [](Widget *pw)        // custom deleter (as in Item 18)
                  {
                    makeLogEntry(pw);
                    delete pw; 
                  };

std::shared_ptr<Widget>          // deleter type is not part of ptr type
spw(new Widget, loggingDel);
```

`std::shared_ptr`는 객체에 대한 참조 횟수를 가리킨다고 했지만, 사실은 **제어 블록(control block)** 이라는 자료구조를 가리키고 있다. 커스텀 삭제자를 지정했다면, 참조 횟수와 함께 커스텀 삭제자 복사본이 제어 블록에 담긴다. 커스텀 할당자(custom allocator)를 지정했다면 이 복사본도 제어 블록에 담긴다. 이외에도 약한 참조(weak count)라 부르는 이차적인 참조 횟수가 포함되며 이 밖의 다른 추가 자료도 포함될 수 있다.

![control block](images/control_block.png)

제어 블록은 다음과 같은 규칙들로 생성된다.

- `std::make_shared`는 항상 제어 블록을 생성한다(Item 21).
- 고유 소유권 포인터(`std::unique_ptr`, `std::auto_ptr`)로부터 `std::shared_ptr` 객체를 생성하면 제어 블록이 생성된다.
- raw pointer로 `std::shared_ptr` 생성자를 호출하면 제어 블록이 생성된다.

raw pointer 타입의 변수로부터 `std::shared_ptr`을 생성하는 일은 피해야 한다. 다음은 `*pw`에 대해 두 개의 참조 횟수가 있다. 두 참조 횟수는 결국 0이 될 것이며, `*pw`의 파괴가 두 번 시도되어 의도되지 않은 동작이 발생할 것이다.

```cpp
auto pw = new Widget; // pw is raw ptr

std::shared_ptr<Widget> spw1(pw, loggingDel); // create control block for *pw
std::shared_ptr<Widget> spw2(pw, loggingDel); // create 2nd control block for *pw!
```

### Item 20: Use std::weak_ptr for std::shared_ptr- like pointers that can dangle

`std::shared_ptr`처럼 행동하되 가리키는 자원의 소유권 공유에 참여하지 않는 것이 편리한 상황도 있다. 이런 종류의 스마트 포인터는 가리키는 대상이 이미 파괴되었을 수도 있는 문제를 극복해야 한다. 즉, 자신이 가리키는 객체가 더 이상 존재하지 않는 상황을 검출할 수 있어야 한다. `std::weak_ptr`이 바로 그런 포인터이다.

대체로 `std::weak_ptr`은 `std::shared_ptr`을 이용해 생성한다. `std::weak_ptr`은 자신을 생성하는데 쓰인 `std::shared_ptr`이 가리키는 것과 동일한 객체를 가리키나, 그 객체의 참조 횟수에는 영향을 주지 않는다.

```cpp
auto spw =                       // after spw is constructed,
  std::make_shared<Widget>();    // the pointed-to Widget's
                                 // ref count (RC) is 1. (See
                                 // Item 21 for info on
                                 // std::make_shared.)
...
std::weak_ptr<Widget> wpw(spw); // wpw points to same Widget
                                // as spw. RC remains 1
...
spw = nullptr;                  // RC goes to 0, and the
                                // Widget is destroyed.
                                // wpw now dangles
```

대상을 잃은 `std::weak_ptr`을 가리켜 "만료되었다(expired)"라고 한다. 만료 여부는 다음과 같이 확인한다.

```cpp
if (wpw.expired()) ... // if wpw doesn't point
                       // to an object...
```

`std::weak_ptr`의 만료를 검사해 만료되지 않았다면 객체에 접근하는 방식의 코드를 생각할 수 있다. 하지만 `std::weak_ptr`은 역참조 연산이 없어 이런 용법은 허용되지 않는다.

제대로 된 용법은 `std::weak_ptr`의 만료 여부를 점검하고, 아직 만료되지 않았다면 객체에 대한 접근을 돌려주는 연산을 하나의 원자적 연산으로 수행하는 것이다. 즉, `std::weak_ptr`로부터 `std::shared_ptr`을 생성하면 되는데, 이 생성 방법은 이미 만료된 `std::weak_ptr`로 `std::shared_ptr`을 생성했을 때의 행동 방식에 따라 두 가지로 나뉜다.

1. `std::weak_ptr::lock()` 사용
    
    `lock()`은 `std::shared_ptr` 객체를 돌려준다. 만약 `std::weak_ptr`이 만료되었다면 null을 반환한다. 
    
    ```cpp
    std::shared_ptr<Widget> spw1 = wpw.lock();  // if wpw's expired, spw1 is null
    auto spw2 = wpw.lock();                     // same as above, but uses auto
    ```
2. `std::weak_ptr`을 인수로 받는 `std::shared_ptr` 생성자 사용
    
    이 경우 `std::weak_ptr`이 만료되었다면 예외가 발생한다.
   
    ```cpp
    std::shared_ptr<Widget> spw3(wpw);  // if wpw's expired,
                                        // throw std::bad_weak_ptr
    ```

### Item 21: Prefer std::make_unique and std::make_shared to direct use of new

`std::make_shared`와 `std::make_unique`는 임의의 개수와 타입의 인수들을 받아 이것들을 생성자로 완벽 전달해 객체를 동적으로 생성하고, 그 객체를 가리키는 스마트 포인터를 돌려주는 세 가지 `make` 함수 중 둘이다. 나머지 하나는 `std::allocate_shared`이다. 이 함수는 `std::make_shared`처럼 작동하나, 첫 인수가 동적 메모리 할당에 쓰일 할당자 객체이다.

다음과 같은 코드가 있다고 하자.

```cpp
processWidget(std::shared_ptr<Widget>(new Widget),  // potential 
              computePriority());                   // resource
                                                    // leak!
```

`processWidget()`을 호출할 경우 다음과 같은 일들이 발생한다.

- 표현식 `new Widget`이 평가된다. 즉, `Widget`이 힙에 생성된다.
- `new`가 산출한 포인터를 관리하는 `std::shared_ptr<Widget>`의 생성자가 실행된다.
- `computePriority()`가 실행된다.

그러나 컴파일러가 이 세 가지 작업들을 순서대로 실행하는 코드를 만드는 것은 아니다. `std::shared_ptr` 생성자가 호출되려면 그 인수가 먼저 평가되어야 하므로, `new Widget`이 `std::shared_ptr`보다 먼저 평가된다. 그러나 `computePriority()`는 이 호출들보다 먼저 실행되거나, 늦게 실행되거나, 혹은 중간에 실행될 수 있다. 따라서 다음과 같은 순서로 실행하는 오브젝트 코드를 산출할 수도 있다.

1. `new Widget` 실행
2. `computePriority()` 실행
3. `std::shared_ptr` 생성자 실행

만약 `computePriority()`가 예외를 던지면 1에서 생성된 `Widget` 객체의 누수(leak)가 발생할 수 있다. 

`std::make_shared`를 사용하면 이와 같은 문제가 생기지 않는다. 위와 동일하게 `std::make_shared`가 먼저 실행되거나 늦게 실행될 수 있다. 만약 `std::make_shared`가 먼저라면, 동적으로 할당된 `Widget`을 가리키는 raw pointer는 `computePriority()`가 호출되기 전 반환된 `std::shared_ptr`에 안전하게 저장된다. 그 다음 예외가 발생한다면, `std::shared_ptr`의 소멸자가 `Widget` 객체를 파괴한다. `computePriority()`가 먼저 호출되고 예외를 발생시킨다면, `std::make_shared`는 아예 호출되지 않아 메모리 누수가 발생될 가능성은 전혀 없다.

또한 `std::make_shared`를 사용하면 더 간결한 자료구조를 사용하는 작고 빠른 코드를 산출할 수 있게 된다. `new`를 직접 사용한다면 `std::shared_ptr` 생성자는 제어 블록을 위한 메모리와 객체를 위한 메모리 할당, 즉 두 번의 할당이 일어난다. `std::make_shared`를 사용하면 객체와 제어 블록 모두를 담을 수 있는 크기의 메모리 조각을 한 번에 할당한다. 따라서 할당 호출 코드가 한 번만 있으면 되므로 프로그램의 정적 크기가 줄어든다.  

`make` 함수 사용이 불가능 또는 부적합한 다음의 경우들이 있다.

1. `make` 함수들은 커스텀 삭제자를 지정할 수 없다.
2. `std::initializer_list`를 받는 생성자와 받지 않는 생성자를 모두 가진 형식의 객체를 생성할 때, 생성자 인수들을 중괄호로 감싸면 오버로딩 해소 과정에서 `std::initializer_list`를 받는 버전이 선택되고, 괄호로 감싸면 `std::initializer_list`를 받지 않는 버전이 선택된다(Item 7). 
    
    ```cpp
    auto upv = std::make_unique<std::vector<int>>(10, 20);
    auto spv = std::make_shared<std::vector<int>>(10, 20);
    ```
    
    위 두 호출 모두 요소의 값이 20인 요소 10개의 `std::vector`를 생성한다. 중괄호 초기화를 사용하기 위해선 반드시 `new`를 직접 사용해야 한다. `make` 함수로 이와 같은 일을 하려면 중괄호 초기화를 완벽하게 전달해야 하는데, Item 30에서 설명하듯 중괄호 초기화의 완벽 전달은 불가능하다.

`std::shared_ptr`에 대해서 `make` 함수가 부적합한 경우가 더 있다.

1. 커스텀 메모리 관리 기능을 가진 클래스를 다루는 경우
    
    예를 들어 `Widget` 클래스를 위한 `operator new`와 `operator delete`라면 크기가 정확히 `sizeof(Widget)`인 메모리 조각들의 할당과 해제를 처리하는 데 특화된 경우가 많다. 이런 루틴들은 `std::shared_ptr`의 커스텀 할당(`std::allocate_shared`를 통한)과 커스텀 해제(커스텀 삭제자를 통한)에 잘 맞지 않는다. `std::allocate_shared`가 요구하는 메모리 조각의 크기는 객체의 크기가 아니라 그 크기에 제어 블록의 크기를 더한 것이기 때문이다.
2. 메모리가 넉넉하지 않은 시스템에서 큰 객체를 다루어야 하고 `std::weak_ptr`들이 해당 `std::shared_ptr`보다 더 오래 살아남는 경우
    
    제어 블록에는 여러 관리용 정보가 있는데, 참조 횟수는 제어 블록을 참조하는 `std::shared_ptr`들의 개수를 뜻한다. 이외에도 제어 블록을 참조하는 `std::weak_ptr`들의 개수에 해당하는 또 다른 참조 횟수도 있다. 이 둘째 참조 횟수를 **약한 횟수(weak count)** 라 한다. 제어 블록을 참조하는 `std::weak_ptr`들이 존재하는 한 제어 블록을 담고 있는 메모리는 여전히 할당된 상태여야 한다. 따라서 `std::shared_ptr` 용 `make` 함수가 할당한 메모리 조각은 이것을 참조하는 마지막 `std::shared_ptr`과 마지막 `std::weak_ptre` 둘 다 파괴된 후에 해제될 수 있다.

### Item 22: When using the Pimpl Idiom, define special member functions in the implementation file

Pimpl 관용구는 클래스의 자료 멤버들을 구현 클래스를 가리키는 포인터로 대체하고, 주 클래스에 쓰이는 멤버들을 그 구현 클래스로 옮기고, 포인터를 통해 간접적으로 접근하는 기법이다. 이 기법은 클래스 구현과 클라이언트 사이 컴파일 의존성을 줄여 빌드 시간을 감소시킨다.

```cpp
class Widget {  // still in header "widget.h"
public:
  Widget();
  ~Widget();    // dtor is needed—see below
  ...
private:
  struct Impl;  // declare implementation struct
  Impl *pImpl;  // and pointer to it
};
```

```cpp
#include "widget.h"          // in impl. file "widget.cpp"
#include "gadget.h"
#include <string>
#include <vector>

struct Widget::Impl {        // definition of Widget::Impl
  std::string name;          // with data members formerly
  std::vector<double> data;  // in Widget
  Gadget g1, g2, g3;
};

Widget::Widget()            // allocate data members for
: pImpl(new Impl)           // this Widget object
{}

Widget::~Widget()           // destroy data members for
{ delete pImpl; }           // this object
```

> 선언만 하고 정의는 하지 않는 타입을 불완전 타입(incomplete type)이라 부른다. 여기서는 `Widget::Impl`이 이런 타입이다.

`std::unique_ptr`(Item 18)을 통해 raw pointer를 대체해보자.

```cpp
class Widget {  // in "widget.h"
public:
  Widget(); 
  ...
  struct Impl;
  std::unique_ptr<Impl> pImpl;  // use smart pointer instead of raw pointer
};
```

```cpp
#include "widget.h"   // in "widget.cpp" 
#include "gadget.h"
#include <string>
#include <vector>

struct Widget::Impl { // as before
  // ...
};

Widget::Widget()                  // per Item 21, create
: pImpl(std::make_unique<Impl>()) // std::unique_ptr
{}                                // via std::make_unique
```

위 코드 자체는 컴파일되나, 이를 사용하는 클라이언트 쪽에서는 컴파일 되지 않는다.

```cpp
#include "widget.h"
Widget w;            // error!
```

`w`가 파괴되는 지점에서 `w`의 소멸자가 호출되는데, `std::unique_ptr`을 이용하는 `Widget` 클래스에는 따로 소멸자가 선언되어 있지 않다(소멸자에서 해야 할 일이 없음). 이 경우 컴파일러가 생성하는 특수 멤버 함수에 대한 통상적인 규칙들에 의해 컴파일러가 대신 소멸자를 작성해준다. 이 소멸자 안에 `Widget`의 자료 멤버 `pImpl`의 소멸자를 호출하는 코드를 삽입한다. 즉, 기본 삭제자를 사용하는 `std::unique_ptr`이고, 그 기본 삭제자는 `std::unique_ptr` 안에 있는 raw pointer에 대해 `delete`를 적용하는 함수이다. 그런데 대부분의 삭제자 함수는 `delete`를 적용하기 전, raw pointer가 *불완전한 형식*을 가리키지는 않는지 `static_assert`를 이용해 점검한다. 컴파일러는 `Widget` 객체 `w`의 파괴를 위한 코드를 산출하는 과정에서 `static_assert`는 참이 아닌 것으로 판정되며, 오류가 발생하게 된다.

`std::unique_ptr<Widget::Impl>`을 파괴하는 코드가 만들어지는 지점에서 `Widget::Impl`이 완전한 형식이 되게 하면 문제는 해결된다. 컴파일러는 형식의 정의를 보게 되면 그 형식을 완전한 형식으로 간주한다. 그리고 `Widget::Impl`의 정의는 widget.cpp에 있다. 따라서 `Wdiget::Impl` 정의 이후에 컴파일러가 그 소스 파일에 있는 `Widget`의 소멸자의 본문(즉, 컴파일러가 `std::unique_ptr` 자료 멤버를 파괴하는 코드를 작성하는 곳)을 보게 한다면 클라이언트 코드는 문제없이 컴파일된다.

```cpp
class Widget {   // as before, in "widget.h" 
public:
  Widget();
  ~Widget();     // declaration only
  ...
private:         // as before
  struct Impl;
  std::unique_ptr<Impl> pImpl;
};
```

```cpp
Widget::~Widget() = default; // same effect as above
```

객체 내부 `pImpl` 포인터가 구현 객체를 독점적으로 소유한다는 점에서, Pimpl 관용구에 적합한 스마트 포인터는 `std::unique_ptr`이다. 

## Rvalue References, Move Semantics, and Perfect Forwarding

- 이동 의미론(move semantics)
    
    컴파일러는 비싼 복사 연산 대신 덜 비싼 이동 연산으로 대체할 수 있다.
- 완벽 전달(perfect forwarding)
    
    임의의 인수를 받아 이것들을 다른 함수로 전달하는 함수를 작성할 때, 그 대상 함수가 애초에 전달 함수가 받은 것과 정확히 같은 인수들을 받게 만들 수 있다.

### Item 23: Understand std::move and std::forward

`std::move`와 `std::forward`는 그냥 캐스팅을 수행하는 함수다. `std::move`는 주어진 인수를 무조건 오른값으로 캐스팅하고, `std::forward`는 특정 조건이 만족될 때마다 이런 캐스팅을 수행한다.

```cpp
template<typename T>              // C++14; still in
decltype(auto) move(T&& param) {  // namespace std
  using ReturnType = remove_reference_t<T>&&;
  return static_cast<ReturnType>(param);
}
```

`std::move`는 객체에 대한 참조(universal reference: Item 24)를 받아 같은 객체에 대한 어떤 참조를 돌려준다.

함수의 반환 타입에 있는 `&&`은 하나의 오른값 참조를 돌려준다. 그러나 타입 `T`가 왼값 참조면 `T&&`는 왼값 참조가 된다. 이를 방지하기 위해 `T`에 `std::remove_reference_t`를 적용한다. 그러면 반환 타입의 `&&`은 항상 참조가 아닌 타입에 적용된다. 즉, `std::move`는 반드시 오른값 참조를 돌려준다. 

`text`를 자료 멤버에 복사할 때 복사 연산 비용을 치르지 않고, `std::move`를 `text`에 적용해 오른값을 얻는다고 하자(Item 41).

```cpp
class Annotation {
public:
  explicit Annotation(const std::string text)
  : value(std::move(text)) // "move" text into value; this code 
  { ... }                  // doesn't do what it seems to!
  ...
private:
  std::string value;
};
```

`text`는 `value`로 이동하는 것이 아닌 **복사**가 된다. `std::move` 때문에 `text`가 오른값으로 캐스팅되지만, `text`는 `const std::string`으로 선언되어 캐스팅 이전에 왼값 `const std::string`이고, 캐스팅 결과는 오른값 `const std::string`이다. 즉, `const`가 그대로 유지된다.

컴파일러가 `std::string` 생성자 중 하나를 선택할 때 `const`의 존재가 어떤 영향을 미치는지 보자.

```cpp
class string {            // std::string is actually a
public:                   // typedef for std::basic_string<char>
  ...
  string(const string& rhs);  // copy ctor
  string(string&& rhs);       // move ctor
  ...
};
```

`std::move(text)`의 결과는 `const std::string` 타입의 오른값이다. 이 오른값은 `std::string`의 이동 생성자에 전달할 수 없다. 왜냐하면, 이 이동 생성자는 `const`가 아닌 `std::string`에 대한 오른값 참조를 받기 때문이다. 그러나 `const std::string`을 복사 생성자에 전달할 수는 있다. 따라서 `std::string`의 복사 생성자를 호출한다. 

여기서 배울 점은 두 가지이다.

1. 이동을 지원할 객체는 `const`로 선언하지 말아야 한다.
2. `std::move`는 실제 아무것도 이동하지 않으며, 캐스팅되는 객체가 이동 자격을 갖추게 된다는 보장도 제공하지 않는다. 확실한 것은 `std::move`를 적용한 결과가 하나의 오른값이라는 것 뿐이다.

`std::forward`에 대해서도 `std::move`와 비슷하게 적용된다. 단, `std::move`는 주어진 인수를 무조건 오른값으로 캐스팅하지만, `std::forward`는 특정 조건이 만족될 때만 캐스팅한다. 즉, 조건부 캐스팅이다.

Universal reference 매개변수를 받아 이것을 다른 어떤 함수에 전달하는 함수를 보자.

```cpp
void process(const Widget& lvalArg);  // process lvalues
void process(Widget&& rvalArg);       // process rvalues

template<typename T>                  // template that passes
void logAndProcess(T&& param) {       // param to process
  auto now =
    std::chrono::system_clock::now(); // get current time

  makeLogEntry("Calling 'process'", now);
  process(std::forward<T>(param)); 
}
```

```cpp
Widget w;
logAndProcess(w);             // call with lvalue
logAndProcess(std::move(w));  // call with rvalue
```

`logAndProcess()`는 `param`을 함수 `process()`에 전달한다. 따라서 `logAndProcess()` 내부에서 일어나는 모든 `process()` 호출은 결국 `process()`의 왼값 오버로딩 버전을 실행하게 된다(`logAndProcess()`에 전달된 인수 자체는 왼값이므로). 이를 방지하기 위해 `param`을 초기화하는 데 쓰인 인수가 오른값이면, 이럴 때만 `param`을 오른값으로 캐스팅하는 메커니즘이 필요하다. `std::forward`가 하는 일이 바로 이것이다. 주어진 인수가 오른값으로 초기화된 것일 때만 이것을 오른값으로 캐스팅한다는 점에서 조건부 캐스팅이라 한다.

`std::move`는 주어진 인수를 무조건 오른값으로 캐스팅하겠다는 뜻이지만, `std::forward`는 오른값에 묶인 참조만 오른값으로 캐스팅하겠다는 뜻이다. 후자는 객체의 왼값 또는 오른값 성질을 유지한 채로 다른 함수에 넘겨주는, 즉 전달하는(forward) 것이다.

### Item 24: Distinguish universal references from rvalue references

어떤 타입 `T`에 대해 오른값 참조를 선언할 때는 `T&&` 표기를 사용한다. 따라서 `T&&`를 발견한다면 이것이 오른값 참조라 가정할 수 있지만, 그렇게 단순하지 않다.

`T&&`에는 두 가지 의미가 있다.

1. 오른값 참조
    - 오직 오른값에만 묶이며, 일차적인 존재 이유는 이동의 원본이 될 수 있는 객체를 지정하는 것
2. 오른값 참조 또는 왼값 참조 중 하나
    - 소스 코드에서는 오른값 참조(`T&&`)로 보이나, 때에 따라서는 왼값 참조(`T&`)인 것처럼 행동한다. 따라서 이런 참조는 오른값 또는 왼값으로 묶일 수 있다.
    - 더욱이 이런 참조는 `const` 객체에 묶을 수도 있고, `non-const` 객체도 묶을 수 있으며, `volatile` 객체에 묶을 수도 있고 `non-volatile` 객체에도 묶을 수 있다.
    - 즉, 거의 모든 것에 묶을 수 있다 하여 **보편 참조(universal reference)** 라 한다.

보편 참조는 두 가지 문맥에서 나타난다.

1. 템플릿 매개변수

    ```cpp
    template<typename T>
    void f(T&& param); // param is a universal reference
    ```

2. `auto` 선언

    ```cpp
    auto&& var2 = var1; // var2 is a universal reference
    ```

이 두 문맥의 경우 타입 추론이 일어난다. 템플릿 `f()`에서는 `param`의 타입 추론이 되고, `var2`의 선언에서는 `var2`의 타입이 추론된다. 타입 추론이 일어나지 않는 경우 `T&&`가 있다면 이는 오른값 참조이다.

```cpp
void f(Widget&& param);   // no type deduction;
                          // param is an rvalue reference
Widget&& var1 = Widget(); // no type deduction;
                          // var1 is an rvalue reference
```

보편 참조는 참조이므로 반드시 초기화해야 한다. 보편 참조가 오른값 참조를 나타내는지 왼값 참조를 나타내는지는 보편 참조의 초기치(initializer)가 결정한다. 초기치가 왼값이면 보편 참조는 왼값 참조에 해당한다. 보편 참조가 함수의 매개변수인 경우, 초기치는 이 함수를 호출하는 지점에서 제공한다.
  
```cpp
Widget w;             // lvalue passed to f; param's type is
f(w);                 // Widget& (i.e., an lvalue reference)

f(std::move(w));      // rvalue passed to f; param's type is
                      // Widget&& (i.e., an rvalue reference)
```

### Item 25: Use std::move on rvalue references, std::forward on universal references

오른값 참조는 이동할 수 있는 객체에만 바인딩된다. 어떤 매개변수가 오른값 참조라면, 그 참조에 바인딩된 객체를 이동할 수 있다. 

반면 보편 참조는 이동에 적합한 객체 바인딩될 수도 있고 아닐 수도 있다. 보편 참조는 오른값으로 초기화되는 경우에만 오른값으로 캐스팅되어야 한다(`std::forward`). 

즉, 오른값 참조를 다른 함수로 전달할 때는 오른값으로의 무조건적인 캐스팅(`std::move`)을 적용하고, 보편 참조를 다른 함수로 전달할 때는 오른값으로의 조건부 캐스팅을 적용해야 한다(`std::forward`).

오른값 참조에 `std::forward`를 사용해도 원하는 동작이 수행되나, 코드가 길어지고 실수의 여지가 있으며 관용구에 벗어난 모습이 된다. 따라서 오른값 참조에 `std::forward`를 사용하는 것은 피해야 한다.

보편 참조에 `std::move`를 적용하는 것은 더 좋지 않다. 이렇게 되면 왼값(지역변수 등)이 의도치 않게 수정되는 결과가 일어날 수 있다.

```cpp
class Widget {
public:
  template<typename T>
  void setName(T&& newName)        // universal reference compiles, but is
  { name = std::move(newName); }   // bad, bad, bad!
  ...
private:
  std::string name;
  std::shared_ptr<SomeDataStructure> p;
};

std::string getWidgetName();       // factory function
Widget w;
auto n = getWidgetName();          // n is local variable
w.setName(n);                      // moves n into w!
...                                // n's value now unknown
```

다음과 같이 '복사'를 '이동'으로 바꾸어 함수를 최적화할 수 있다고 생각할 수 있다.

```cpp
Widget makeWidget()        // Moving version of makeWidget
{
  Widget w;
  ...
  return std::move(w);     // move w into return value (don't do this!)
}
```

그러나 여기서 간과한 것은 이런 종류의 최적화를 위한 대비책이 이미 마련되어 있다는 것이다. 지역변수 `w`를 함수의 반환값을 위해 마련한 메모리 안에 생성한다면 `w`의 복사를 피할 수 있다. 이를 **반환값 최적화(RVO: Return Value Optimization)** 이라 한다.

컴파일러가 결과를 값 전달 방식으로 반환하는 함수의 어떤 지역 객체의 복사를 제거할 수 있으려면

1. 그 지역 객체의 타입이 함수의 반환 타입과 같아야 하고
2. 그 지역 객체가 함수의 반환값이어야 한다.

```cpp
Widget makeWidget()  // "Copying" version of makeWidget
{
  Widget w;
  ...
  return w;           // "copy" w into return value
}
```

따라서 위 예에서는 조건이 모두 만족되므로 반환값 최적화를 적용해 `w`의 복사를 피할 것이다. 

하지만 `std::move(w)`를 적용한 버전은 반환값은 지역 객체 `w`가 아닌 `w`에 대한 참조이다. 따라서 RVO의 조건을 만족하지 못하며, 컴파일러는 반드시 `w`를 함수의 반환값 장소로 옮겨야 한다. 결과적으로 `std::move`를 통해 최적화하려 했으나, 실제로는 컴파일러가 할 수 있는 최적화를 제한하게 된다.

### Item 26: Avoid overloading on universal references

오버로딩된 `logAndAdd()`가 있고, 

```cpp
std::string nameFromIdx(int idx);      // return name corresponding to idx

void logAndAdd(int idx)                // new overload 
{
  auto now = std::chrono::system_clock::now(); 
  log(now, "logAndAdd"); 
  names.emplace(nameFromIdx(idx));
}

template<typename T> void logAndAdd(T&& name) {
  auto now = std::chrono::system_clock::now(); 
  log(now, "logAndAdd"); 
  names.emplace(std::forward<T>(name));
}
```

클라이언트가 인덱스 값을 담은 `short`를 전달한다고 하자.

```cpp
short nameIdx;
...                     // give nameIdx a value
logAndAdd(nameIdx);     // error!
```

보편 참조를 받는 버전은 `T`를 `short&`로 추론할 수 있으며, 이러면 주어진 인수와 정확히 부합되는 형태가 되어 보편 참조 오버로딩이 호출된다. 보편 참조를 받는 오버로딩에서 `name`은 주어진 `short`에 바인딩된다. 그 다음 `name`이 `std::forward`를 통해 `names`의 멤버 함수 `emplace()`에 전달된다. `emplace()`는 이를 `std::string` 생성자에 전달한다. 그런데 `std::string` 생성자 중 `short`를 받는 버전은 없으므로 컴파일이 실패한다. 

보편 참조를 받는 템플릿 함수는 C++에서 가장 욕심 많은 함수다. 이런 템플릿 인스턴스는 거의 모든 타입의 인수와 정확히 부합한다. 보편 참조 오버로딩이 예상한 것보다 훨씬 많은 인수 타입들을 받아들인다는 점에서 오버로딩과 결합하는 것은 거의 항상 나쁜 선택이다.

완벽 전달(perfect forward) 생성자를 사용해 해결할 수 있겠지만 문제는 더 심각해진다. `std::string`을 받는 `Person` 클래스를 만들어보자.

```cpp
class Person {
public:
  template<typename T>
  explicit Person(T&& n)          // perfect forwarding ctor; initializes data member
  : name(std::forward<T>(n)) {}

  explicit Person(int idx)        // int ctor
  : name(nameFromIdx(idx)) {}
  ...

private:
  std::string name;
};
```

`int` 이외의 정수 타입을 넘겨주면 `int`를 받는 생성자 대신 보편 참조를 받는 생성자가 호출되어 컴파일에 실패한다. C++은 특정 조건에서 복사 생성자와 이동 생성자를 자동으로 작성하며, 심지어 템플릿화된 생성자가 복사 생성자나 이동 생성자에 해당하는 서명으로 인스턴스화되는 경우에도 자동으로 만들어진다. 따라서 `Person`에 대해 복사 생성자와 이동 생성자가 작성된다면 다음과 같을 것이다.

```cpp
class Person {
public:
  template<typename T>            // perfect forwarding ctor
  explicit Person(T&& n)
  : name(std::forward<T>(n)) {}

explicit Person(int idx);         // int ctor
  Person(const Person& rhs);      // copy ctor (compiler-generated)
  Person(Person&& rhs);           // move ctor (compiler-generated)
  ... 
};
```

따라서 다음과 같은 코드는 이상하게 동작할 것이다.

```cpp
Person p("Nancy");
auto cloneOfP(p);   // create new Person from p;
                    // this won't compile!
```

이 코드는 완벽 전달 생성자가 호출한다. 이 함수는 `Person`의 `std::string` 자료 멤버를 `Person` 객체(`p`)로 생성하려 하는데, `std::string`은 `Person`을 받는 생성자가 없으므로 컴파일이 실패한다.

복사할 객체를 `const`로 바꾸면 상황이 달라진다.

```cpp
const Person cp("Nancy"); // object is now const 
auto cloneOfP(cp);        // calls copy constructor!
```

이제 복사 생성자와 정확히 부합된다.

> C++의 오버로딩 해소 규칙에 어떤 함수 호출이 템플릿 인스턴스와 비템플릿 인스턴스(보통 함수)에 똑같이 부합한다면, 보통 함수를 우선시하는 규칙이 있기 때문이다. 그래서 복사 생성자가 자신과 같은 서명을 가진 템플릿 인스턴스보다 우선시된다.

상속에 관여하는 클래스에서는 완벽 전달 생성자와 컴파일러가 작성한 복사 및 이동 연산들 사이 상호작용히 미치는 여파가 더욱 커진다. 파생 클래스의 복사, 이동 생성자는 해당 기반 클래스의 복사, 이동 생성자를 호출하는 것이 아니라, 기반 클래스의 완벽 전달 생성자를 호출한다.

```cpp
class SpecialPerson: public Person {
public:
  SpecialPerson(const SpecialPerson& rhs)  // copy ctor; calls 
  : Person(rhs)                            // base class
  { ... }                                  // forwarding ctor!

  SpecialPerson(SpecialPerson&& rhs)       // move ctor; calls
  : Person(std::move(rhs))                 // base class
  { ... }                                  // forwarding ctor!
};
```

완벽 전달 생성자는 대체로 `non-const` 왼값에 대한 복사 생성자보다 더 나은 부합이며, 기반 클래스 복사 및 이동 생성자들에 대한 파생 클래스의 호출들을 가로챌 수 있기 때문이다.

### Item 27: Familiarize yourself with alternatives to overloading on universal references

보편 참조에 대한 오버로딩이 아닌 기법을 이용해, 또는 보편 참조에 대한 오버로딩이 부합할 수 있는 인수들의 타입을 제한하여 이런 바람직한 행동을 달성하는 방법들을 보자.

1. Abandon overloading

    오버로딩 버전에 각자 다른 이름을 붙이면 보편 참조에 대한 오버로딩에 대한 단점을 피할 수 있다(Item 26). 그러나 생성자 오버로딩에서 문제가 발생될 수 있다.
2. Pass by const T&

    보편 참조 대신 `const`에 대한 왼값 참조 매개변수를 사용하는 것이다(Item 26). 그러나 보편 참조와 오버로딩의 상호 작용에 의한 문제점이 있으니 효율성을 포기하더라도 예상치 않은 문제를 피하는 것이 좋다.
3. Pass by value

    복잡도를 높이지 않고 성능을 높일 수 있는 한 가지 방식으로, 참조 전달 매개변수 대신 값 전달 매개변수를 사용하는 것이다.

    ```cpp
    class Person {
    public:
      explicit Person(std::string n) // replaces T&& ctor; see
      : name(std::move(n)) {}        // Item 41 for use of std::move
      
      explicit Person(int idx)       // as before
      : name(nameFromIdx(idx)) {}
      ...
    private:
      std::string name;
    };
    ```
4. Use Tag dispatch
    보편 참조를 사용하려는 이유가 완벽 전달이라면, 보편 참조 말고는 다른 대안이 없다. 이 경우에도 보편 참조와 오버로딩 둘 다 사용하되 보편 참조에 대한 오버로딩을 피하려면 **태그 디스패치(tag dispatch)** 를 사용하면 된다. 

    매개변수 목록에 보편 참조 매개변수 뿐 아니라 보편 참조가 **아닌** 매개변수들도 포한되어 있으면, 보편 참조 매개변수가 있는 오버로딩을 제치고 선택될 가능성이 있다. 이것이 태그 디스패치 접근 방식이다.

    실제 작업을 수행하는 두 함수의 이름을 `logAndAddImpl()`로 한다. 즉, 이들에 대해서 오버로딩을 수행한다. 둘 중 하나는 보편 참조를 받는다. 두 함수는 전달된 인수가 정수 타입인지 아닌지를 뜻하는 매개변수를 받는다.

    ```cpp
    template<typename T>
    void logAndAdd(T&& name)
    {
      logAndAddImpl(std::forward<T>(name), 
                    std::is_integral<T>()); // not quite correct
    }
    ```

    이 함수는 자신의 매개변수를 `logAndAddImpl()`에 전달하며, 이와 함께 매개변수 타입 `T`가 정수인지를 뜻하는 인수도 전달한다. 만약 `name`으로 전달된 인수가 왼값이면 `T`는 왼값 참조 타입으로 추론(Item 28)된다. 따라서 `int` 타입의 왼값이 `logAndAdd()`에 전달되면, `T`는 `int&`로 추론된다. 참조는 정수 타입이 아니므로 `std::is_integral<T>`는 거짓이 된다.
    
    이를 해결하기 위해 `std::remove_reference`를 사용한다.

    ```cpp
    template<typename T>
    void logAndAdd(T&& name)
    {
      logAndAddImpl(
        std::forward<T>(name),
        std::is_integral<typename std::remove_reference<T>::type>()
      ); 
    }
    ```

    `std::true_type` 타입과 `std::false_type` 타입은 오버로딩 해소에 우리가 원하는 방식으로 일어나게 하는 데에 쓰이는 일종의 "태그(tag)"이다.
5. Constraining templates that take universal references

    완벽 전달 생성자에 대한 문제는 태그 디스패처로는 해결할 수 없다. 컴파일러가 자동으로 복사 생성자와 이동 생성자를 작성하기 때문에, 생성자 하나만 작성해 그 안에서 태그 디스패치를 사용한다면 일부 생성자 호출은 컴파일러가 작성한 함수들로 처리되어 태그 디스패치가 적용되지 않을 위험이 있다.

    `std::enable_if`를 이용하면 컴파일러가 마치 특정 템플릿이 존재하지 않는 것처럼 행동할 수 있다. 이런 템플릿을 비활성화된(disabled) 템플릿이라 한다. `Person` 예에서는 `Person`이 아닌 타입의 인수가 전달된 경우에만 `Person`의 완벽 전달 생성자가 활성화되게 해야 한다. 

    ```cpp
    class Person {
    public:
      template<typename T,
               typename = typename std::enable_if<condition>::type>
      explicit Person(T&& n);
      ...
    };
    ```

    두 타입이 같은지를 확인하는 `std::is_same`이 있다. 이를 이용해 `!std::is_same<Person, T>::value` 표현식을 조건으로 지정하면 되겠다. 그러나 왼값으로 초기화되는 보편 참조는 항상 왼값 참조로 추론된다. 즉, `Person&`로 추론되어 `std::is_same`은 다르다고 판정할 것이다.

    그렇다면 `T`에 대해 다음 두 사항을 무시해야 할 것이다.

    1. 참조 여부
    2. `const`성과 `volatile`성

    표준 라이브러리에는 `std::decay`라는 특질(trait)이 있다. `std::decay<T>::type`은 `T`에서 모든 참조와 cv-한정사(cv-qualifier: `const`, `volatile` qualifier)를 제거한 타입에 해당한다. 결과적으로 다음과 같은 코드가 될 것이다.

    ```cpp
    class Person {
    public:
      template<
        typename T,
        typename = typename std::enable_if<
                     !std::is_same<Person,
                                   typename std::decay<T>::type
                                   >::value
                   >::type
        >
      explicit Person(T&& n);
      ... 
    };
    ```
    
    그러나 아직 `Person`에서 파생된 클래스에서 문제가 발생될 수 있다. `SpecialPerson` 객체가 복사 연산들과 이동 연산들을 통상적인 방식으로 구현했다고 하자(Item 26).

    복사, 이동 생성자들은 `SpecialPerson` 객체를 기반 클래스의 생성자들에 넘겨주는데, `SpecialPerson`은 `Person`과 같지 않으므로(`std::decay` 적용 후에도) 기반 클래스의 보편 참조 생성자 템플릿이 활성화된다. 

    특정 타입에서 파생된 것인지를 알려주는 `std::is_base_of` 특질이 있다. `std::is_base_of<T1, T2>::value`는 만일 T2가 T1에서 파생된 타입이면 참이게 된다. 따라서 ` std::is_same`만 `std::is_base_of`로 바꾸면 된다. C++14 버전으로 더 간결한 코드를 만들 수 있다.

    ```cpp
    class Person {                    // C++14
    public:
      template<
        typename T,
        typename = std::enable_if_t<  // less code here
                     !std::is_base_of<Person,
                                      std::decay_t<T> // and here
                                     >::value
                     >                                // and here
      >
      explicit Person(T&& n);
      ... 
    };
    ```

    이제 마지막으로 다음 두 가지만 하면 된다.

    1. 정수 인수들을 처리하는 `Person` 생성자 오버로딩 추가
    2. 이런 인수들에 대해서는 템플릿화된 생성자가 비활성화되도록 하는 조건 추가

    ```cpp
    class Person {
    public:
      template<
        typename T,
        typename = std::enable_if_t<
        !std::is_base_of<Person, std::decay_t<T>>::value
        &&
        std::is_integral<std::remove_reference_t<T>>::value
        > 
      >
      explicit Person(T&& n)      // ctor for std::strings and
      : name(std::forward<T>(n))  // args convertible to
      { ... }                     // std::strings
      
      explicit Person(int idx)    // ctor for integral args
      : name(nameFromIdx(idx)) 
      { ... }
      ...                         // copy and move ctors, etc.
    private:
      std::string name;
    };
    ```
6. Trade-offs

    처음의 세 가지 기법은 호출되는 함수들의 각 매개변수 타입을 지정한다. 

    1. 오버로딩을 피하는 것
    2. `const T&`를 전달하는 것
    3. 값을 전달하는 것

    나머지 두 기법은 완벽 전달을 사용하므로, 매개변수 타입을 지정하지 않는다.

    1. 태그 디스패치
    2. 템플릿 활성화 제한

    완벽 전달이 더 효율적이나 단점들이 있다. 완벽 전달이 불가능한 인수들이 있다는 점과 클라이언트가 유효하지 않은 인수를 전달했을 때 오류 메시지가 난해하다는 것이다. 

    `Person`의 경우 보편 참조 매개변수가 `std::string`에 대한 초기화로 쓰일 것을 알고 있으므로, 이 초기화로 사용하는 것이 가능하지 미리 `static_assert`를 통해 점검하는 방법도 있다. `std::is_constructible` 특질은 한 타입의 객체를 다른 한 타입의 객체로부터 생성할 수 있는지를 컴파일 타임에 판정할 수 있다. 

    ```cpp
    static_assert(
        std::is_constructible<std::string, T>::value,
        "Parameter n can't be used to construct a std::string"
      );
    ```

### Item 28: Understand reference collapsing

템플릿 매개변수 `T`에 대해 추론된 타입을 `param`으로 전달된 인수가 왼값이었는지 오른값이었는지에 대한 정보가 인코딩될 것이다.

```cpp
template<typename T>
void func(T&& param);
```

C++에서 참조에 대한 참조는 위법이다.

```cpp
int x;
auto& & rx = x; // error! can't declare reference to reference
```

그런데 보편 참조를 받는 함수 템플릿에 왼값을 넘겨주면 `T`에 대해 추론된 타입(`Widget &`)으로 템플릿이 인스턴스화한 결과는 다음과 같다.

```cpp
void func(Widget& && param);
```

이는 참조에 대한 참조지만 컴파일된다. 보편 참조 `param`은 왼값으로 초기화되므로, `param` 타입은 왼값 참조가 된다. 따라서 컴파일러가 `T`에 대해 추론된 타입을 템플릿에 대입하면 위와 같은 시그니처가 나온다. 그러나 실제로 만들어지는 시그니처는 다음과 같다.

```cpp
void func(Widget& param);
```

이는 **참조 축약(reference collapsing)** 이다. 참조에 대한 참조는 위법이나, 특정 문맥에서 컴파일러가 참조에 대한 참조를 산출하는 것이 허용된다. 템플릿 인스턴스화가 이런 문맥 중 하나이다.

참조는 두 종류(왼값, 오른값)로 참조에 대한 참조가 가능한 조합은 총 네 가지이다. 

> 만일 두 참조 중 하나라도 왼값이면 결과는 왼값 참조이다. 그렇지 않으면(둘 다 오른값 참조) 결과는 오른값 참조이다.

`std::forward`가 작동하는 것은 이 참조 축약 덕분이다. Item 25에서 설명하듯 `std::forward`는 보편 참조 매개변수에 적용된다. 

```cpp
template<typename T>
void f(T&& fParam)
{
  ...   // do some work
  someFunc(std::forward<T>(fParam)); // forward fParam to someFunc
}
```

`fPararm`이 보편 참조이므로 `f()`에 전달된 인수가 왼값인지 오른값인지에 대한 정보가 타입 매개변수 `T`에 인코딩된다. 

다음은 `std::forward`의 가능한 구현 중 하나이다.

```cpp
template<typename T>        // in namespace std
T&& forward(typename
            remove_reference<T>::type& param)
{
  return static_cast<T&&>(param);
}
```

`f()`에 전달된 인수가 `Widget` 타입의 왼값이라고 하자. 그러면 `T`는 `Widget&`로 추론되며 `std::forward<Widget&>` 타입으로 인스턴스화된다. `Widget&`를 `std::forward`의 구현에 대입하면 다음과 같아질 것이다.

```cpp
Widget& && forward(typename
                   remove_reference<Widget&>::type& param)
{ return static_cast<Widget& &&>(param); }
```

`remove_reference<Widget&>::type`는 `Widget`을 산출하므로 `std::forward`는 다음과 같이 변한다.

```cpp
Widget& && forward(Widget& param)
{ return static_cast<Widget& &&>(param); }
```

참조 축약이 적용된 최종 버전은 다음과 같다.

```cpp
Widget& forward(Widget& param)          // still in
{ return static_cast<Widget&>(param); } // namespace std
```

만약 `f()`에 전달된 인수가 `Widget` 타입의 오른값이면 `f()` 타입 매개변수 `T`에 대해 추론되는 타입은 그냥 `Widget`이다.

```cpp
Widget&& forward(typename
                 remove_reference<Widget>::type& param)
{ return static_cast<Widget&&>(param); }
```

`remove_reference`를 비참조 타입 `Widget`에 적용하면 `Widget`이 산출되므로 `std::forward`는 다음과 같아진다.

```cpp
Widget&& forward(Widget& param)
{ return static_cast<Widget&&>(param); }
```

여기서 참조 축약이 일어난 문맥은 네 가지이다.

1. 템플릿 인스턴스화
2. `auto` 변수에 대한 타입 추론
3. `typedef`와 별칭 선언의 지정 및 사용(Item 9)
4. `decltype` 사용

### Item 29: Assume that move operations are not present, not cheap, and not used

다음은 C++에서 이동 의미론이 도움이 되지 않는 몇 가지 시나리오다.

1. **이동 연산이 없다.** 이동할 객체가 이동 연산들을 제공하지 않는다. 이 경우 이동 요청은 복사 요청이 된다.
2. **이동이 더 빠르지 않다.** 이동할 객체의 이동 연산이 해당 복사 연산보다 빠르지 않다.
3. **이동을 사용할 수 없다.** 이동이 일어나려면 이동 연산이 예외를 방출하지 않아야 하는 문맥에서, 해당 연산이 noexcept로 선언되어 있지 않다.

다음은 이동 의미론이 효율성 면에서 이득이 되지 않는 시나리오다.

1. **원본 객체가 왼값이다.** 드문 경우(Item 25)지만, 오직 오른값만 이동 연산의 원본이 될 수 있는 경우도 있다.

### Item 30: Familiarize yourself with perfect forwarding failure cases

전달(forwarding)은 한 함수가 자신들의 인수들을 다른 함수에 넘겨주는 것을 뜻한다. 이때 목표는 둘째 함수(전달받는 함수)가 첫 함수(전달하는 함수)가 받았던 것과 동일한 객체들을 받게 하는 것이다. 값 전달 방식의 매개변수로는 이런 목표를 달성할 수 없다. 원래의 호출자가 넘겨준 인수의 복사본이기 때문이다. 우리가 원하는 것은 전달받는 함수가 원래 전달된 객체를 다룰 수 있게 하는 것이다.

완벽 전달은 단순히 객체들을 전달하는 것만이 아니라, 그 객체들의 타입, 왼값, 오른값 여부, `const`나 `volatile` 여부까지 전달하는 것이다. 이를 위해선 보편 참조 매개변수(Item 24)가 필요하다. 

```cpp
template<typename... Ts>
void fwd(Ts&&... params)            // accept any arguments 
{
  f(std::forward<Ts>(params)...);   // forward them to f 
}
```

대상 함수 `f()`와 전달 함수 `fwd()`가 있다고 할 때, 만약 어떤 인수로 `f()`을 호출했을 때 일어나는 일과 같은 인수로 `fwd()`를 호출했을 때 일어나는 일이 다르다면 완벽 전달은 실패한 것이다.

이러한 실패 사례들을 살펴보자.

1. Braced initializers

    `f()`의 선언이 다음과 같다고 할 때,

    ```cpp
    void f(const std::vector<int>& v);
    ```

    중괄호 초기화(`fwd()`)에 넘겨주는 코드는 컴파일되지 않는다.

    ```cpp
    fwd({ 1, 2, 3 }); // error! doesn't compile
    ```

    템플릿 `fwd()`를 통해 `f()`를 간접적으로 호출할 때, 컴파일러는 `fwd()`의 호출 지점에서 전달된 인수들과 `f()`에 선언된 매개변수를 직접 비교할 수 없다. 대신 컴파일러는 `fwd()`에 전달되는 인수들의 타입을 추론하고, 추론된 타입들을 `f()`의 매개변수 선언들과 비교한다. 이때 다음 두 조건 중 하나라도 만족하면 완벽 전달은 실패한다.

    1. `fwd()`의 매개변수들 중 하나 이상에 대해 컴파일러가 타입을 추론하지 못한다.
    2. `fwd()`의 매개변수들 중 하나 이상에 대해 컴파일러가 타입을 잘못 추론한다.

    `fwd({ 1, 2, 3 })` 호출에서는 `std::initializer_list`가 될 수 없는 타입으로 선언된 함수 템플릿 매개변수에 중괄호 초기화로 넘겨준다는 것이다. 이를 **비추론 문맥(non-deduced context)** 이라 한다. 즉, `fwd()`의 매개변수가 `std::initializer_list`가 될 수 없는 타입으로 선언되어 있어 `fwd()`에 쓰인 표현식 `{ 1, 2, 3 }`의 타입을 컴파일러가 추론하는 것이 금지되어 있다는 뜻이다.
2. 0 or NULL as null pointers

    0이나 `NULL`을 템플릿에 넘겨주려 하면 컴파일러는 이를 포인터 타입이 아닌 정수 타입으로 추론한다(Item 8). 해결책으로 `nullptr`을 사용하면 된다.

3. Declaration-only integral static const and constexpr data members

    `static const` 멤버와 `static constexpr` 멤버는 클래스 안에서 정의할 필요가 없다. 선언만 하면 된다. 이런 멤버의 값에 대해 컴파일러는 **const 전파(const propagation)** 를 적용해, 이런 멤버의 값을 위한 메모리를 따로 마련할 필요가 없어지기 때문이다.

    ```cpp
    class Widget {
    public:
      static const std::size_t MinVals = 28;    // MinVals' declaration
      ... 
    };
    ...                                         // no defn. for MinVals
    ```

    `fwd(Widget::MinVals)`를 호출하면 링크에 실패한다. 코드에 `MinVals`의 주소를 취하는 부분이 없다 해도, `fwd()` 매개변수는 보편 참조이며 컴파일러가 산출한 코드에서 참조는 포인터처럼 취급되는 것이 보통이다. 따라서 `MinVals`를 참조로 전달하는 것은 사실상 포인터로 넘겨주는 것이며, 이런 포인터가 가리킬 뭔가가 필요하다. 따라서 `static const` 멤버와 `static constexpr` 멤버를 참조로 전달하려면 이 멤버를 **정의**할 필요가 있다.

    ```cpp
    const std::size_t Widget::MinVals;     // in Widget's .cpp file
    ```
4. Overloaded function names and template names

    `f()`가 다음과 같이 함수 포인터를 받고, 

    ```cpp
    void f(int pf(int));
    ```

    오버로딩된 `processVal()` 함수가 있다고 하자.

    ```cpp
    int processVal(int value);
    int processVal(int value, int priority);
    ```

    함수 템플릿 `fwd(processVal)`은 이러한 호출에 필요한 타입에 대한 정보가 전혀 없다. 따라서 컴파일러는 어떤 오버로딩을 선택해야 할지 결정하지 못한다.

    함수 템플릿을 사용하려 할 때도 같은 문제가 발생한다. 함수 템플릿은 하나의 함수를 나타내는 것이 아니라 다수의 함수를 대표한다.

    ```cpp
    template<typename T>
    T workOnVal(T param)    // template for processing values 
    { ... }
    fwd(workOnVal);         // error! which workOnVal instantiation?
    ```

    `fwd()` 같은 완벽 전달 함수가 오버로딩된 함수 이름이나 템플릿 이름을 받아들이게 하려면, 전달하고자 하는 오버로딩이나 템플릿 인스턴스를 명시적으로 지정하면 된다.

    ```cpp
    using ProcessFuncType = int (*)(int)            // make typedef; see Item 9
    ProcessFuncType processValPtr = processVal;     // specify needed signature for processVal
    fwd(processValPtr);                             // fine
    fwd(static_cast<ProcessFuncType>(workOnVal));   // also fine
    ```
5. Bitfields

    비트필드가 함수 인수로 쓰일 때 완벽 전달이 실패한다. 임의의 비트들을 가리키는 포인터를 생성하는 방법은 없으며, 따라서 참조를 임의의 비트들에 묶는 방법도 없다.

    그러나 우회책을 사용해 비트필드의 완벽 전달을 가능하게 할 수 있다. 전달 대상 함수가 항상 비트필드 값의 복사본을 받게 되는 사실을 활용하는 것이다.

    1. 값으로 전달
        
        호출될 함수가 비트필드 값의 복사본임이 명확하다.
    2. `const`에 대한 참조로 전달
    
        `const` 참조는 비트필드 자체에 바인딩되는 것이 아니라 복사된 '보통' 객체에 바인딩된다.

## Lambda Expressions

- **클로저(closure)** 는 람다에 의해 만들어진 런타임 객체이다. 캡처 모드에 따라 클로저가 캡처된 자료의 복사본을 가질 수도 있고, 그 자료에 대한 참조를 가질 수도 있다. 
- **클로저 클래스**는 클로저를 만드는 데 쓰인 클래스를 말한다.

컴파일 타임에 존재하는 것(람다와 클로저 클래스)와 런타임에 존재하는 것(클로저)을 구분하는 것이 중요하다.

### Item 31: Avoid default capture modes

C++11의 기본 캡처 모드는 두 가지이다.

1. 참조에 의한(by-reference) 캡처 모드
2. 값에 의한(by-value) 캡처 모드

참조에 의한 캡처 모드를 사용하는 클로저는 지역 변수 또는 람다가 정의된 범위에서 볼 수 있는 매개변수에 대한 참조를 가지게 된다. 람다에 의해 생성된 클로저의 수명이 그 지역 변수나 매개변수의 수명보다 오래 지속되면 클로저 안의 참조 대상을 잃는다.

```cpp
void addDivisorFilter()
{
  auto calc1 = computeSomeValue1();
  auto calc2 = computeSomeValue2();
  
  auto divisor = computeDivisor(calc1, calc2);

  filters.emplace_back(                             // danger!
    [&](int value) { return value % divisor == 0; } // ref to
  );                                                // divisor
}                                                   // will dangle!
```

`divisor`와 관련된 문제를 해결하는 방법은 값 캡처 모드를 사용하는 것이다. 

```cpp
filters.emplace_back(               // now divisor
  [=](int value)                    // can't dangle
{ return value % divisor == 0; }
);
```

그러나 값 캡처 모드도 다른 문제가 있다. 포인터를 값으로 캡처하면 이 포인터는 람다에 의해 생성된 클로저 안으로 복사되는데, 람다 바깥의 어떤 코드가 이 포인터를 `delete`로 삭제하지 않는다고 보장할 수 없기 때문이다.

```cpp
class Widget {
public:
  ...                       // ctors, etc.
  void addFilter() const;   // add an entry to filters
private:
  int divisor;              // used in Widget's filter
};
```

캡처는 오직 람다가 생성된 범위 안에서 보이는 `static`이 아닌 지역 변수(또는 매개변수)에만 적용된다. 따라서 다음 코드는 컴파일되지 않는다.

```cpp
void Widget::addFilter() const
{
  filters.emplace_back( 
    [divisor](int value)              // error! no local
    { return value % divisor == 0; }  // divisor to capture
  ); 
}
```

람다가 클로저 안에 캡처하는 것은 `divisor`가 아니라 `Widget`의 `this` 포인터다. 즉, 컴파일러는 값 캡처 `[=]`를 다음과 같이 취급한다.

```cpp
void Widget::addFilter() const
{
  auto currentObjectPtr = this;
  filters.emplace_back(
    [currentObjectPtr](int value)
    { return value % currentObjectPtr->divisor == 0; }
  ); 
}
```

결과적으로 이 람다에서 만들어진 클로저의 유효성이 `Wdiget` 객체의 수명에 의해 제한된다. 

이 문제는 캡처하려는 멤버의 지역 복사본을 만들어 이 복사본을 캡처하면 된다. 이는 값 캡처 모드(`[=]`)에서도 잘 동작한다.

```cpp
void Widget::addFilter() const
{
  auto divisorCopy = divisor;               // copy data member
  
  filters.emplace_back(                     
    [divisorCopy](int value)                // capture the copy
    { return value % divisorCopy == 0; }    // use the copy
  ); 
}
```

C++14에서 멤버를 캡처하기 위해 일반화된 람다(Item 32)를 사용하는 방법도 있다.

```cpp
void Widget::addFilter() const
{
  filters.emplace_back(                 // C++14:
    [divisor = divisor](int value)      // copy divisor to closure 
    { return value % divisor == 0; }    // use the copy
  ); 
}
```

람다는 지역 변수나 매개변수 뿐 아니라 정적 저장소 수명 기간(static storage duration)를 가진 객체에도 의존할 수 있다. 전역 범위나 네임스페이스 범위에 정의된 객체와 클래스, 함수, 파일 안에서 `static`으로 선언된 객체들이 이에 해당한다. 그러나 값 캡처 모드는 이런 객체도 모두 캡처되어 격리되었다고 오해할 수 있다. 

### Item 32: Use init capture to move objects into closures

이동 전용 객체를 클로저 안으로 들여오려는 경우 값 캡처 모드나 참조 캡처 모드는 마땅치 않다. 그러나 C++14에서는 객체를 클로저 안으로 이동하는 수단을 직접 제공한다.

C++14는 새로운 캡처 메커니즘으로 **초기화 캡처(init capture)** 를 도입했다. 초기화 캡처로 표현할 수 없는 것 하나는 기본 캡처 모드인데, Item 31에 설명하듯 어짜피 기본 캡처 모드는 피해야 한다.

초기화 캡처로 다음과 같은 것들을 지정할 수 있다.

1. 람다로부터 생성되는 클로저 클래스에 속한 자료 멤버의 이름
2. 이 자료 멤버를 초기화하는 표현식

다음은 초기화 캡처를 통해 `std::unique_ptr`을 클로저 안으로 이동하는 예다.

```cpp
class Widget {      // some useful type
public:
  ...
  bool isValidated() const;
  bool isProcessed() const;
  bool isArchived() const;
private: 
  ...
};

auto pw = std::make_unique<Widget>();   // create Widget; see Item 21 
                                        // for info on std::make_unique

...                                     // configure *pw

auto func = [pw = std::move(pw)]                // init data mbr
            { return pw->isValidated()          // in closure w/
                     && pw->isArchived(); };    // std::move(pw)
```

`=`의 좌변은 클로저 클래스 안 자료 멤버(클로저에서 사용할)의 이름이고, 우변은 이것을 초기화하는 표현식이다. 좌변의 범위는 해당 클로저 클래스의 범위이고, 우변의 범위는 람다가 정의되는 지점의 범위와 동일하다. 즉, `pw = std::move(pw)`는 "클로저 안에서 자료 멤버 `pw`를 생성하되, 지역 변수 `pw`에 `std::move`를 적용한 결과로 이 자료 멤버를 초기화하라"는 의미이다.

만약 수정이 필요하지 않다면 지역 변수 `pw`는 필요하지 않다. 그냥 `[pw = std::make_unique<Widget>()]`와 같이 클로저 클래스의 멤버를 직접 초기화하면 된다.

> C++11에서 람다를 고집한다면 `std::bind`를 사용해 비슷하게 흉내낼 수 있다. 그러나 Item 34에서 `std::bind`보다는 람다를 선호하라고 조언한다.

### Item 33: Use decltype on auto&& parameters to std::forward them

C++14에서 특별한 기능은 매개변수 명세에 `auto`를 사용한 람다이다. 람다의 클로저 클래스의 `operator()`를 템플릿 함수로 만들면 된다. 

다음과 같은 람다 클래스가 있다고 하자.

```cpp
auto f = [](auto x){ return func(normalize(x)); };
```

클로저 클래스의 함수 호출 연산자는 다음과 같은 모습으로 산출된다.

```cpp
class SomeCompilerGeneratedClassName { 
public:
  template<typename T>              // see Item 3 for
  auto operator()(T x) const        // auto return type
  { return func(normalize(x)); }
  ...                               // other closure class functionality
};
```
