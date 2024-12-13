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

## Constructors, Destructors, and Assignment Operators

### Item 5: Know what functions C++ silently writes and calls

생성자, 복사 생성자, 복사 대입 연산자, 소멸자는 클래스에 직접 선언하지 않으면 컴파일러가 기본형으로 만들어준다. 예를 들어 `class Empty{};
`로 선언하면 다음과 같은 함수들이 자동으로 생성된다.

```cpp
class Empty { 
public:
	Empty() { ... }                 // default constructor 
	Empty(const Empty& rhs) { ... } // copy constructor
	~Empty() { ... }                // destructor — see below
	                                // for whether it’s virtual
	Empty& operator=(const Empty& rhs) { ... } // copy assignment operator
};
```

### Item 6: Explicitly disallow the use of compiler-generated functions you do not want

자동으로 생성되는 복사 생성자, 복사 대입 생성자의 경우 복사를 원하지 않는 클래스에서도 복사가 지원될 수 있다. 이는 `private` 멤버로 선언하여 해결할 수 있다.

```cpp
class HomeForSale { 
public:
	...
private: 
	...
	HomeForSale(const HomeForSale&); // declarations only
	HomeForSale& operator=(const HomeForSale&);
};
```

### Item 7: Declare destructors virtual in polymorphic base classes

`TimeKeeper`를 상속하는 여러 개의 클래스들이 있다고 가정하자.

```cpp
class TimeKeeper { 
public:
	TimeKeeper( ); 
	~TimeKeeper( ); ...
};

class AtomicClock: public TimeKeeper { ... }; 
class WaterClock: public TimeKeeper { ... }; 
class WristWatch: public TimeKeeper { ... };
```

`getTimeKeeper()` 함수에서 반환되는 객체는 힙에 있으므로 메모리 릭을 막기 위해 해당 객체를 삭제해야 한다.

```cpp
TimeKeeper *ptk = getTimeKeeper();  // get dynamically allocated object from TimeKeeper hierarchy
...           // use it
delete ptk;   // release it to avoid resource leak
```

하지만 `getTimeKeeper()` 함수가 반환하는 포인터는 파생 클래스의 포인터이며, 이 포인터가 가리키는 객체가 삭제될 때는 기본 클래스 포인터(`TimeKeeper`)를 통해 삭제된다는 것, 그리고 기본 클래스에 들어있는 소멸자가 `non-virtual` 이라는 것이다.

C++ 규정에 의하면 기본 클래스 포인터를 통해 파생 클래스 객체가 삭제될 때 기본 클래스에 `non-virtual` 소멸자가 있으면 해당 프로그램의 동작은 미정의 사항이라 되어 있다. 일반적으로 파생 클래스 부분이 소멸되지 않게 된다. 

이를 해결하기 위해선 기본 클래스에 **가상 소멸자**를 선언하면 된다.

```cpp
class TimeKeeper { 
public:
	TimeKeeper( );
	virtual ~TimeKeeper(); 
	...
};
```

Base 클래스로 의도하지 않은 클래스에 대해 가상으로 선언하는 것 또한 좋지 않다. 

가상 소멸자로 만들어지는 순간 프로그램 실행 시 어떤 가상 함수를 호출해야 하는 결정하는데 쓰이는 정보인데, 실제로는 포인터 형태를 취하며 vptr(virtual table pointer)로 불린다. vptr은 가상 함수 주소(포인터 배열)를 가라키고 있으며 vtbl(virtual table)이라 불린다. 즉, 가상 함수를 하나라도 갖는 클래스는 반드시 이와 관련된 vtbl를 갖고 있다. 

따라서 가상 함수가 들어가게 되면 해당 객체 크기가 커지게 되며, C 등의 다른 언어로 선언된 동일한 자료구조와도 호환성이 없어진다.

### Item 8: Prevent exceptions from leaving destructors

소멸자로부터 예외가 발생하는 경우 C++에서 막아주지 않는다. 다음과 같은 DB 연결을 위한 클래스가 있다고 하자.

```cpp
class DBConnection { 
public:
	...
	static DBConnection create(); // function to return DBConnection objects; params omitted for simplicity
	void close(); // close connection; throw an exception if closing fails
};
```

`DBConnection`의 자원 관리 클래스인 `DBConn`를 만들어 소멸자에서 `DBConnection`의 `close()`를 호출하게 할 수 있다.

```cpp
class DBConn { // class to manage DBConnection objects
public:
	...
	~DBConn() { // make sure database connections are always closed
		db.close(); 
	}
private: 
	DBConnection db;
};
```

따라서 다음과 같이 프로그래밍 할 수 있다.

```cpp
{ // open a block
	DBConn dbc(DBConnection::create()); // create DBConnection object and turn it over to a DBConn object to manage
	... // use the DBConnection object via the DBConn interface
} // at end of block, the DBConn object is destroyed, thus automatically calling close on the DBConnection object
```

그러나 `close()`를 호출했는데 여기서 예외가 발생했다고 하자. `DBConn`의 소멸자는 예외를 전파할 것이다. 즉, 소멸자에서 예외가 나가도록 내버려 둔다는 것이다. 

이를 피하기 위한 두 가지 방법이 있다.

1. `close()`에서 예외가 발생하면 `abort()` 호출로 프로그램을 바로 끝낸다.
   ```cpp
   DBConn::~DBConn( ) {
   	try { db.close(); } 
   	catch (...) {
   		make log entry that the call to close failed;
   		std::abort(); 
   	}
   }
   ```
2. `close()`를 호출한 곳에서 일어난 예외를 삼킨다. 이는 좋은 방식이 아니지만, 때에 따라 불완전한 프로그램 종료 혹은 미정의 동작으로 인한 위험을 감수하는 것보다 나을 수 있다.
   ```cpp
   DBConn::~DBConn( ) {
   	try { db.close(); } 
   	catch (...) {
   		make log entry that the call to close failed; 
   	}
   }
   ```

### Item 9: Never call virtual functions during construction or destruction

주식 거래가 발생될 때마다 로그에 거래 내역이 쌓이도록 하고 싶어 `Transaction` 클래스를 생성했다고 하자.

```cpp
class Transaction { // base class for all transactions
public:
	Transaction( );
	virtual void logTransaction() const = 0; // make type-dependent log entry
	... 
};

Transaction::Transaction() { // implementation of base class ctor
	... 
	logTransaction(); // as final action, log this transaction
}

class BuyTransaction: public Transaction { // derived class
public:
	virtual void logTransaction() const; // how to log transactions of this type
	... 
};
```

그리고 다음과 같이 코드를 작성했다고 하자. 

```
BuyTransaction b;
```

`Transaction` 생성자가 먼저 호출되며, 해당 생성자에서 `logTransaction()`을 호출하고 있다. 여기서 호출되는 `logTransaction()` 함수는 `Transaction`의 것이다.

파생 클래스 객체의 기본 클래스 부분이 생성되는 동안 해당 객체의 타입은 기본 클래스이며, 객체가 소멸될 때에도 동일하다.

이런 문제를 해결하려면 `logTransaction()`을 `Transaction`의 `non-virtual` 멤버 함수로 바꾸는 것이다. 그리고 파생 클래스의 생성자에서 필요한 로그 정보를 `Transaction`의 생성자로 넘겨야 한다는 규칙을 만들어 `logTransaction()`을 안전하게 호출할 수 있다.

```cpp
class Transaction { 
public:
	explicit Transaction(const std::string& logInfo);
	void logTransaction(const std::string& logInfo) const; // now a non-virtual func
	... 
};

Transaction::Transaction(const std::string& logInfo) {
	...
	logTransaction(logInfo); // now a non-virtual call
}

class BuyTransaction: public Transaction { 
public:
	BuyTransaction( parameters )
	: Transaction(createLogString( parameters )) {...} // pass log info to base class constructor
	...
private:
	static std::string createLogString( parameters );
};
```

### Item 10: Have assignment operators return a reference to *this

C++의 대입 연산은 우측 연관(right-associative) 연산이다. 따라서 다음과 같이 사용될 수 있다.

```cpp
int x, y, z;
x = y = z = 15; // x = (y = (z = 15));
```

15가 `z`에 먼저 대입되고, 그 결과가 `y`에 대입된 후 `y`의 결과가 `x`에 대입된다. 이것이 가능하려면 대입 연산자가 좌변 인자에 대한 참조자를 반환하도록 구현되어 있을 것이다. 따라서 생성할 클래스에서도 이 컨벤션을 지키는 것이 좋다(모든 형태의 대입 연산자에 대해). 

```cpp
class Widget { 
public:
	...
	Widget& operator=(const Widget& rhs) { // return type is a reference to the current class
		...
		return *this; // return the left-hand object
	}
	... 
};
```

### Item 11: Handle assignment to self in operator=

자기 대입(self assignment)는 어떤 객체가 자기 자신에 대해 대입 연산자를 적용하는 것이다. 같은 타입으로 만들어진 객체 여러 개를 참조자 혹은 포인터로 만들고 동작하는 코드를 작성할 때는 같은 객체가 사용될 가능성을 고려하는 것이 바람직하다.

동적 할당된 비트맵을 가리키는 포인터를 데이터 멤버로 갖는 클래스가 있다고 하자.

```cpp
class Bitmap { ... };
class Widget { 
	...
private:
	Bitmap *pb; // ptr to a heap-allocated object
};
```

다음과 같은 코드에서 `*this`와 `rhs`가 같은 객체일 가능성이 있다. 따라서 함수가 끝나는 시점엔 해당 `Widget` 객체는 자신의 포인터 멤버를 통해 갖고 있던 객체가 삭제되는 상태가 된다.

```cpp
Widget& Widget::operator=(const Widget& rhs) { // unsafe impl. of operator=
	delete pb;                // stop using current bitmap
	pb = new Bitmap(*rhs.pb); // start using a copy of rhs’s bitmap
	return *this;
}
```

따라서 일치성 검사(identity test)를 통해 자기대입을 점검해야 한다.

```cpp
Widget& Widget::operator=(const Widget& rhs) {
	if (this == &rhs) return *this; // identity test: if a self-assignment, do nothing
	delete pb;
	pb = new Bitmap(*rhs.pb);
	return *this; 
}
```

위 코드는 예외 안정성에 대해서 여전히 문제이다. `new Bitmap()`에서 예외가 발생하면 `Widget` 객체는 삭제된 `Bitmap`을 가라키는 포인터를 갖게 된다.

다음과 같이 `pb`를 삭제하지 말고 이 포인터가 가리키는 객체를 복사한 후 삭제하면 해결할 수 있다.

```cpp
Widget& Widget::operator=(const Widget& rhs) {
	Bitmap *pOrig = pb; // remember original pb 
	pb = new Bitmap(*rhs.pb); // point pb to a copy of rhs’s bitmap
	delete pOrig; // delete the original pb
	return *this; 
}
```

> 효율이 신경쓰일 수 있으나, 일치성 검사 역시 공짜가 아니다. 

### Item 12: Copy all parts of an object

`Customer` 클래스가 있고, 이를 상속한 `PriorityCustomer` 클래스가 있다고 하자.

```cpp
class Date { ... }; // for dates in time
class Customer { 
public:
	...   // as before
private:
	std::string name; 
	Date lastTransaction;
};

class PriorityCustomer: public Customer { // a derived class public:
	...
	PriorityCustomer(const PriorityCustomer& rhs); 
	PriorityCustomer& operator=(const PriorityCustomer& rhs); 
	...
private:
	int priority;
};
```

객체의 복사 함수를 작성할 때는 해당 클래스의 데이터 멤버를 모두 복사해야 하며, 이 클래스가 상속한 기본 클래스의 복사 함수도 호출해야 한다.

```cpp
PriorityCustomer::PriorityCustomer(const PriorityCustomer& rhs)
: Customer(rhs), // invoke base class copy ctor
	priority(rhs.priority) {
	logCall("PriorityCustomer copy constructor"); 
}

PriorityCustomer& PriorityCustomer::operator=(const PriorityCustomer& rhs) {
	logCall("PriorityCustomer copy assignment operator");
	Customer::operator=(rhs); // assign base class parts 
	priority = rhs.priority;
	return *this; 
}
```

> 본문이 비슷하게 나오는 경우에 중복을 피라혀 한다면, 겹치는 부분을 별도의 `private` 함수로 분리하고, 이 함수(주로 이름에 `init`이 포함됨)를 호출하도록 한다. 

## Resource Management

### Item 13: Use objects to manage resources

`createInvestment()`에서 얻은 객체를 사용하는 일이 없을 때, 이 객체를 삭제해야 하는 쪽은 호출자(caller)다.

```cpp
void f() {
	Investment *pInv = createInvestment(); // call factory function
	... // use pInv
	delete pInv; // release object
}
```

`...`에 `return`이 있거나 `delete`가 루프 안에 있고, `continue` 혹은 `goto`에 의해 루프에서 빠져나왔을 때 `delete`를 실행하지 않을 수 있다.

`createInvestment()`로 얻어낸 자원이 항상 해제되도록 만드는 방법은, 자원을 객체에 넣고 자원 해제를 소멸자가 맡도록 하며, 이 소멸자는 `f()`가 끝날 때 호출되도록 하는 것이다.

이 객체로 참조 카운팅 방식 스마트 포인터(Reference-Counting Smart Pointer: RCSP)가 있으며, 자원을 가리키는 외부 객체가 0이 되면 해당 자원을 삭제하는 스마트 포인터다. 

> 가비지 컬렉션과 비슷하나, 참조 상태가 고리를 이루는 경우(다른 두 객체가 서로 가리키는 등)를 없앨 수 없다는 점은 가비지 컬렉션과 다르다.

```cpp
void f() {
	...
	std::tr1::shared_ptr<Investment> pInv(createInvestment()); // call factory function 
	... // use pInv as before
} // automatically delete pInv via shared_ptr's dtor
```

### Item 14: Think carefully about copying behavior in resource-managing classes

뮤텍스 잠김을 관리하는 클래스가 있다고 하자.

```cpp
class Lock { 
public:
	explicit Lock(Mutex *pm)
	: mutexPtr(pm)
	{ lock(mutexPtr); } // acquire resource
	~Lock() { unlock(mutexPtr); } // release resource
private:
	Mutex *mutexPtr;
};
```

여기서 `Lock` 객체가 복사된다고 해보자.

```cpp
Lock ml1(&m);  // lock m
Lock ml2(ml1); // copy ml1 to ml2 — what should happen here?
```

RAII 객체가 복사될 때는 다음과 같은 동작이 이루어져야 한다.

- **복사를 금지한다.** `Lock` 클래스와 같이 복사되는 것 자체가 말이 안 되는 경우가 있다. 이러한 경우 클래스는 복사되지 않도록 해야 한다. 복사 함수를 `private`로 만들어 해결할 수 있다.
- **관리하는 자원에 대한 참조 카운팅을 수행한다.** 자원을 참조하는 객체의 개수에 대한 카운트를 증가시키는 방법으로 `tr1::shared_ptr`이 사용하고 있다. `

    `tr1::shared_ptr`은 삭제자(deleter)를 사용할 수 있다. 삭제자란 참조 카운트가 0이 되었을 때 실행할 함수 또는 객체이다. 즉, `Mutex`를 다 썼을 때 이에 대한 삭제가 아닌 잠금 해제만 수행할 수 있다.  

    ```cpp
    class Lock { 
    public:
        explicit Lock(Mutex *pm) 	// init shared_ptr with the Mutex to point to and the unlock func as the deleter
        : mutexPtr(pm, unlock)
        {
            lock(mutexPtr.get()); // see Item 15 for info on “get”
        } 
    private:
        std::tr1::shared_ptr<Mutex> mutexPtr; // use shared_ptr instead of raw pointer
    };
    ```

- **관리하고 있는 자원을 진짜로 복사한다.** 이 경우 자원을 다 썼을 때 각가의 사본을 확실히 해제하는 것이 자원 클래스가 필요한 명분이다. 자원 관리 객체를 복사하면 그 객체의 자원까지 복사되어야(deep copy) 한다.
- **관리하고 있는 자원의 소유권을 옮긴다.** 어떤 특정 자원에 대한 실제 참조하는 객체가 RAII 객체 하나만 존재하도록 하고 싶은 경우, 이 RAII가 복사될 때 그 자원의 소유권을 사본 쪽으로 옮겨야 할 경우도 있다(`auto_ptr`).

### Item 15: Provide access to raw resources in resource-managing classes

포인터를 담기 위해 `tr1::shared_ptr`을 사용했다고 하자.

```cpp
std::tr1::shared_ptr<Investment> pInv(createInvestment()); // from Item 13
```

`Investment` 포인터를 전달받는 다음과 같은 함수가 있다.

```cpp
int daysHeld(const Investment *pi); // return number of days investment has been held
```

RAII 클래스의 객체를 그 객체가 감싸고 있는 실제 자원(`Investment`)으로 변환할 방법이 필요하다. `tr1::shared_ptr`은 `get()`이라는 멤버 함수를 제공한다. 이 함수를 통해 스마트 포인터 객체에 들어있는 실제 포인터를 얻을 수 있다.

RAII 클래스인 `Font`를 `FontHandle`로 변환해야 할 경우가 있다고 하자. `get()`을 통해 명시적으로 얻을 수도 있고, `operator`를 사용해 암시적으로도 얻을 수 있다.

```cpp
class Font { // RAII class
public:
	explicit Font(FontHandle fh) // acquire resource use pass-by-value, because the C API does
	: f(fh) {}
	~Font( ) { releaseFont(f); } // release resource
	FontHandle get() const { return f; } // explicit conversion function
	operator FontHandle() const { return f; } // implicit conversion function
	... // handle copying (see Item 14)
private: 
	FontHandle f; // the raw font resource
};
```

암시적 변환의 경우 `Font`를 쓰려고 한 부분에서 원치 않았는데 `FontHandle`로 바뀌는 실수를 저지를 여지가 많아진다.

```cpp
Font f1(getFont()); 
...
FontHandle f2 = f1; // oops! meant to copy a Font object, but instead implicitly converted f1 into its underlying FontHandle, then copied that
```

### Item 16: Use the same form in corresponding uses of new and delete

`new` 표현식에 `[]`를 사용했으면, `delete` 표현식에도 `[]`를 사용해야 한다. 
`new` 표현식에 `[]`를 사용하지 않았으면, `delete` 표현식에도 `[]`를 사용하지 말아야 한다.

### Item 17: Store newed objects in smart pointers in standalone statements

동적으로 할당된 `Widget`에 대해 어떤 우선순위에 따라 처리를 적용할지 결정하는 함수가 있다고 하자.

```cpp
int priority();
void processWidget(std::tr1::shared_ptr<Widget> pw, int priority);
```

다음과 같이 작성될 수 있으며, 이 코드는 문제가 있다.

```cpp
processWidget(std::tr1::shared_ptr<Widget>(new Widget), priority());
```

`processWidget()` 호출 코드를 만들기 전 이 함수의 매개변수로 넘겨지는 인자를 평가(evaluate)하는 순서가 있다. 컴파일러는 다음 세 연산을 위한 코드를 만들어야 한다.

- `priority()` 호출
- `new Widget` 실행
- `tr1::shared_ptr` 생성자 호출

여기서 각각의 연산이 실행되는 순서는 컴파일러 제작사마다 다르다는 것이다. `new Widget`은 `tr1::shared_ptr` 생성자가 실행되기 전 호출되어야 한다. 만약 어떤 컴파일러에서 `priority()` 호출이 두 번째라고 정했다고 하자.

1. `new Widget` 실행
2. `priority()` 호출
3. `tr1::shared_ptr` 생성자 호출

만약 `priority()`에서 예외가 발생했다면, `new Widget`으로 만들었던 포인터가 유실될 수 있다. `tr1::shared_ptr`에 저장되기 전 예외가 발생했기 때문이다. 

이 문제를 피하기 위해 `Widget`을 생성해 스마트 포인터에 저장하는 코드를 별도의 문장 하나로 만들고, 그 스마트 포인터를 `processWidget()`에 넘기면 된다.

```cpp
std::tr1::shared_ptr<Widget> pw(new Widget); // store newed object in a smart pointer in a standalone statement
processWidget(pw, priority()); // this call won’t leak
```

## Designs and Declarations

### Item 18: Make interfaces easy to use correctly and hard to use incorrectly

날짜를 나타내는 클래스에 생성자를 설계한다고 하자.

```cpp
struct Day {
	explicit Day(int d) 
	: val(d) {}
	int val;
};

struct Month {
	explicit Month(int m) 
	: val(m) {}
	int val;
};

struct Year {
	explicit Year(int y) 
	: val(y){}
	int val;
};

class Date { 
public:
	Date(const Month& m, const Day& d, const Year& y);
	... 
};

Date d(30, 3, 1995); // error! wrong types
Date d(Day(30), Month(3), Year(1995)); // error! wrong types
Date d(Month(3), Day(30), Year(1995)); // okay, types are correct
```

이렇게 타입을 적절히 준비해 두기만 해도 인터페이스 사용 에러를 막을 수 있다.

다른 방법으로 타입에 제약을 부여하여 그 타입을 통해 할 수 있는 일들을 묶어버리는 방법이 있다. 흔히 `const`를 붙이는 것이다. `operator*`의 반환 타입을 `const`로 한정해 사용자가 정의 타입에 대해 실수를 저지르지 않도록 할 수 있다.

```cpp
if (a * b = c) ... // oops, meant to do a comparison!
```

**그렇게 하지 않을 번듯한 이유가 없다면 사용자 정의 타입은 기본제공 타입처럼 동작하게 만들자.** 기본제공 타입과 어긋나는 동작을 피하는 실질적인 이유는 일관성 있는 인터페이스 제공을 위해서다.

사용자 쪽에서 뭔가 외워야 제대로 쓸 수 있는 인터페이스는 잘못 쓰기 쉽다. 처음부터 끝까지 문제가 생길 여지를 주지 않게끔 구현하는 편이 좋다. 즉, 다음과 같이 팩토리 함수가 포인터가 아닌 스마트 포인터를 반환하여 호출자 쪽에서 삭제를 책임지지 않게 만드는 것이다.

```cpp
std::tr1::shared_ptr<Investment> createInvestment();
```

### Item 19: Treat class design as type design

좋은 타입은 문법(syntax)이 자연스럽고, 의미구조가(semantics)가 직관적이며, 효율적인 구현이 한 가지 이상 가능해야 한다.

- **새로 정의한 타입의 객체 생성 및 소멸은 어떻게 이루어져야 하는가?** 이 부분이 어떻게 되느냐에 따라 클래스 생성자 및 소멸자의 설계가 바뀐다. 뿐만 아니라 메모리 할당 함수를 직접 작성할 경우 이들 함수의 설계에도 영향을 미친다.
- **객체 초기화는 객체 대입과 어떻게 달라야 하는가?** 초가화와 대입을 헷갈리지 않는 것이 중요하다.
- **새로운 타입으로 만든 객체가 값에 의해 전달되는 경우 어떤 의미를 줄 것인가?** 어떤 타입에 대해 '값에 의한 전달'을 구현하는 쪽은 복사 생성자이다.
- **새로운 타입이 가질 수 있는 적법한 값에 대한 제약은 무엇으로 잡는가?** 클래스의 데이터 멤버의 몇 가지 조합 값은 반드시 유효해야 한다. 이런 조합을 클래스의 불변속성(invariant)라 하며, 클래스 차원에서 지켜주어야 한다. 특히 생성자, 대입 연산자, setter 함수는 불변속성에 많이 좌우된다.
- **기존 클래스 상속 계통망(inheritance graph)에 맞출 것인가?** 이미 갖고 있는 클래스로부터 상속 한다면, 이들 클래스에 의해 제약을 받는다. 특히 `virtual`인가 `non-virtual`인가의 여부가 가장 큰 요인이다. 다른 클래스들이 상속할 수 있게 만들고자 한 경우, 이에 따라 멤버 `virtual` 함수 여부가 결정된다. 특히 소멸자가 그렇다.
- **어떤 종류의 타입 변환을 허용할 것인가?** `T1` 타입 객체를 `T2` 타입 객체로 암시적으로 변환되도록 하고 싶다면, `T1` 클래스에 타입 변환 함수를 넣던가 아니면 인자 한 개로 호출될 수 있는 `non-explict` 생성자를 `T2` 클래스에 넣어야 할 것이다. `explict` 타입 변환만 허용하고 싶다면, 해당 변환을 맡는 별도 이름의 함수를 만들되 타입 변환 연산자 혹은 `non-explict` 생성자는 만들지 말아야 한다(Item 15). 
- **어떤 연산자 함수를 두어야 의미가 있을끼?** 클래스 안에 선언할 함수가 여기서 결정된다. 어떤 것들은 멤버 함수로 적당하며, 또 몇몇은 그렇지 않을 것이다.
- **표준 함수들 중 어떤 것을 허용하지 말 것인가?** `private`로 선언하는 함수가 여기에 해당된다.
- **새로운 타입의 멤버에 대한 접근권한을 어느 쪽에 줄 것인가?** `public`, `protected`, `private` 영역에 둘 것인가를 결정하는 데 도움을 줄 질문이다.
- **“선언되지 않은 인터페이스”로 무엇을 둘 것인가?** 만들 타입이 제공할 보장이 어떤 종류일까에 대한 질문으로, 보장할 수 있는 부분은 수행 성능 및 예외 안정성 그리고 자원 사용이다. 이들에 대해 보장하겠다고 결정한 결과는 클래스 구현에 있어 제약으로 작용한다.
- **새로 만드는 타입이 얼마나 일반적인가?** 실제로 타입 하나를 정의하는 것이 아닌 타입군(family of types) 전체일수도 있다. 그렇다면 새로운 클래스가 아닌 새로운 클래스 템플릿을 정의해야 할 것이다.
- **정말로 필요한 타입인가?** 기존 클래스에 대해 기능 몇 개가 아쉬어 파생 클래스를 새로 만든다면, 차라리 `non-member` 함수라든지 템플릿을 몇 개 더 정의하는 편이 낫다.