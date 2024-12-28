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

`auto`를 사용할 경우(`auto highPriority`) `std::vector<bool>::reference` 객체를 돌려주는 것 까지는 동일하다. 그러나 `auto`에 의해 `highPriority` 타입이 추론되기 때문에 `std::vector<bool>` 타입의 5번 비트로 초기화되지 않게 된다.

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