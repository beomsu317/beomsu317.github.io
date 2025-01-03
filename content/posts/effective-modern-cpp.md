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

`nullptr`은 정수 타입 또는 포인터 타입이 아니다. `nullptr`의 실제 타입은 `std::nullptr_t`인데 `std::nullptr_t` 자체는 다시 `nullptr`의 타입으로 정의된다. `std::nullptr_t`는 모든 raw 포인터 타입으로 암묵적으로 변환되며, 따라서 `nullptr`은 마치 모든 타입의 포인터처럼 행동한다.

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

