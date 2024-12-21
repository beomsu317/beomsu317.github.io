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

하지만 `getTimeKeeper()` 함수가 반환하는 포인터는 파생 클래스의 포인터이며, 이 포인터가 가리키는 객체가 삭제될 때는 기본 클래스 포인터(`TimeKeeper`)를 통해 삭제된다는 것, 그리고 기본 클래스에 들어있는 소멸자가 non-virtual 이라는 것이다.

C++ 규정에 의하면 기본 클래스 포인터를 통해 파생 클래스 객체가 삭제될 때 기본 클래스에 non-virtual 소멸자가 있으면 해당 프로그램의 동작은 미정의 사항이라 되어 있다. 일반적으로 파생 클래스 부분이 소멸되지 않게 된다. 

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

이런 문제를 해결하려면 `logTransaction()`을 `Transaction`의 non-virtual 멤버 함수로 바꾸는 것이다. 그리고 파생 클래스의 생성자에서 필요한 로그 정보를 `Transaction`의 생성자로 넘겨야 한다는 규칙을 만들어 `logTransaction()`을 안전하게 호출할 수 있다.

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

- 새로 정의한 타입의 객체 생성 및 소멸은 어떻게 이루어져야 하는가?
- 객체 초기화는 객체 대입과 어떻게 달라야 하는가?
- 새로운 타입으로 만든 객체가 값에 의해 전달되는 경우 어떤 의미를 줄 것인가?
- 새로운 타입이 가질 수 있는 적법한 값에 대한 제약은 무엇으로 잡는가?
- 기존 클래스 상속 계통망(inheritance graph)에 맞출 것인가?
- 어떤 종류의 타입 변환을 허용할 것인가?
- 어떤 연산자 함수를 두어야 의미가 있을끼?
- 표준 함수들 중 어떤 것을 허용하지 말 것인가?
- 새로운 타입의 멤버에 대한 접근권한을 어느 쪽에 줄 것인가?
- “선언되지 않은 인터페이스”로 무엇을 둘 것인가?
- 새로 만드는 타입이 얼마나 일반적인가?
- 정말로 필요한 타입인가?

### Item 20: Prefer pass-by-reference-to-const to pass-by-value

C++은 함수로부터 객체를 전달받거나 함수에 객체를 전달할 때 "값에 의한 전달(pass-by-value)" 방식을 사용한다.

`Student` 클래스를 전달받는 `validateStudent()` 함수가 있다고 하자.

```cpp
bool validateStudent(Student s); // function taking a Student by value

Student plato; // Plato studied under Socrates
bool platoIsOK = validateStudent(plato); // call the function
```

`plato`로부터 매개변수 `s`를 초기화시키기 위해 `Student`의 복사 생성자가 호출되며, `validateStudent()`에서 복귀할 때 소멸될 것이다. 즉, 이 함수의 매개변수 전달 비용은 `Student`의 복사 생성자 호출 한 번, `Student`의 소멸자 호출 한 번이다.

이러한 생성자, 소멸자 호출 비용을 지불하지 않기 위해 상수 객체에 대한 참조자(reference-by-const)로 전달할 수 있다. 새로 만들어지는 객체가 없기 때문에 생성자와 소멸자가 전혀 호출되지 않는다. 

```cpp
bool validateStudent(const Student& s);
```

> C++ 컴파일러에서 참조자는 보통 포인터를 써서 구현되기 때문에, 기본제공 타입(`int` 등) 및 반복자, 함수 객체 타입의 경우 참조자로 전달하는 것보다 값으로 전달하는 편이 효율적일 때가 많다. 

### Item 21: Don’t try to return a reference when you must return an object

`Rational`이라는 유리수 클래스에 `*` 연산에서 효율을 위해 참조자 객체를 반환하도록 구현했다고 하자.

```cpp
const Rational& operator*(const Rational& lhs, const Rational& rhs) // warning! bad code!
{
	Rational result(lhs.n * rhs.n, lhs.d * rhs.d); 
	return result;
}
```

이 연산자 함수는 `result`를 반환하는데, `result`는 로컬 객체다. 즉, 함수가 끝날 때 같이 소멸되는 객체라는 것이다.

새로운 객체를 반환해야 하는 함수는 **새로운 객체를 반환하게 만들어야 한다**. 여기에 들어가는 비용은 올바른 동작에 지불되는 작은 비용이다. 

```cpp
inline const Rational operator*(const Rational& lhs, const Rational& rhs) {
	return Rational(lhs.n * rhs.n, lhs.d * rhs.d); 
}
```

> C++ 컴파일러는 기존 코드 수행 성능을 높이는 최적화가 적용되어 있다. 즉, 일부 조건하에서는 최적화에 의해 `operator*`의 반환 값에 대한 생성과 소멸 동작이 안전하게 제거될 수 있다(RVO: Return Value Optimization). 

### Item 22: Declare data members private

데이터 멤버를 `private`으로 두면 접근 불가, 읽기 전용, 쓰기 접근을 직접 구현할 수 있다.

```cpp
class AccessLevels { 
pub
lic:
	...
	int getReadOnly() const { return readOnly; }
	void setReadWrite(int value) { readWrite = value; }
	int getReadWrite() const { return readWrite; }
	void setWriteOnly(int value) { writeOnly = value; }
private:
	int noAccess; // no access to this int
	int readOnly; // read-only access to this int
	int readWrite; // read-write access to this int
	int writeOnly; // write-only access to this int
};
```

어떤 식으로든 외부에 노출시키면 안 되는 데이터 멤버들이 꽤 있기 때문에 이러한 접근 제어는 중요하다.

또한 데이터 멤버를 캡슐화하면 내부 구현을 융통성 있게 바꿀 수 있으며, 클래스의 불변속성을 강화할 수 있다.

### Item 23: Prefer non-member non-friend functions to member functions

똑같은 기능을 제공하는데 "멤버 함수를 쓸 것이냐, 비멤버 함수를 쓸 것이냐"를 생각해보면, 캡슐화 정도가 높은 후자이다. 비멤버 함수는 어떤 클래스의 `private` 멤버 부분을 접근할 수 있는 함수의 개수를 늘리지 않기 때문이다.

C++로 더 자연스러운 방법은 `clearBrowser()`를 비멤버 함수로 두고, `WebBrowserStuff`와 같은 네임스페이스 안에 두는 것이다.

```cpp
namespace WebBrowserStuff {

class WebBrowser { ... };
void clearBrowser(WebBrowser& wb); 
...

}
```

### Item 24: Declare non-member functions when type conversions should apply to all parameters

일반적으로 암시적 변환은 안좋은 생각이지만, 이 규칙에도 예외가 있다. 예를 들어 `Rational` 유리수 타입을 만든다고 하자. `operator*`는 클래스 안에 구현하는게 자연스러울 것이다.

```cpp
class Rational { 
public:
	Rational(int numerator = 0, int denominator = 1);// ctor is deliberately not explicit; allows implicit int-to-Rational conversions
	int numerator() const; // accessors for numerator and denominator — see Item 22
	int denominator() const;

	const Rational operator*(const Rational& rhs) const; 
private: 
	...
};
```

하지만 연산을 해보면 반쪽짜리 연산인 것을 알게 될 것이다. 두 번째 줄에서 정수 `2`는 클래스가 연관되지 않기 때문에 `operator*` 멤버 함수도 없다(컴파일 에러). 

```cpp
Rational oneHalf(1, 2);
Rational result;

result = oneHalf * 2; // oneHalf.operator*(2);
result = 2 * oneHalf; // 2.operator*(oneHalf);
```

`Rational::operator*` 선언문을 보면 인자로 `Rational` 객체를 받도록 한다. 이는 암시적 타입 변환(implicit type conversion)으로 가능하다. 즉, 이 함수에 `int`를 넘기면 `Rational`로 타입 변환이 발생한다.


```cpp
const Rational temp(2);  // create a temporary Rational object from 2
result = oneHalf * temp; // same as oneHalf.operator*(temp);
```

`operator*`를 비멤버 함수로 만들어 컴파일러 쪽에서 모든 인자에 대해 암시적 타입 변환을 수행하도록 할 수 있다.

```cpp
const Rational operator*(const Rational& lhs, const Rational& rhs) // contains no operator* now a non-member function
{
	return Rational(lhs.numerator() * rhs.numerator(),
}
```

### Item 25: Consider support for a non-throwing swap

표준 라이브러리에서 제공하는 `swap()` 알고리즘은 복사가 세 번 일어나게 된다. 타입에 따라서는 사본이 필요없는 경우도 있다.

복사하면 손해보는 타입의 예로 pimpl(pointer to implementation)이다. 예로 `Widget` 클래스를 보자.

```cpp
class WidgetImpl { // class for Widget data; details are unimportant
public:
	...
private:
	int a, b, c; // possibly lots of data — expensive to copy!
	std::vector<double> v; 
	...
};

class Widget { // class using the pimpl idiom
public:
	Widget(const Widget& rhs);
	Widget& operator=(const Widget& rhs) { // to copy a Widget, copy its WidgetImpl object. For details on implementing operator= in general, see Items 10, 11, and 12.
		...
		*pImpl = *(rhs.pImpl); 
		...
	} 
	...
private:
	WidgetImpl *pImpl; // ptr to object with this Widget’s data
}; 
```

`Widget` 객체를 바꾼다면, `pImpl` 포인터만 바꾸기만 하면 된다. `Widget` 객체를 바꿀 때는 `pImpl` 포인터만 바꾸도록 특수화를 해보자.

`pImpl` 포인터는 `private` 멤버이기 때문에 `Widget` 내 `swap()` 멤버 함수를 선언하고 이 함수가 실제로 맞바꾸기를 수행하도록 한다. 이 함수는 예외를 던져서는 안 된다.

```cpp
class Widget { // same as above, except for the addition of the swap mem func
public:
	...
	void swap(Widget& other) {
		using std::swap; // the need for this declaration is explained later in this Item
		swap(pImpl, other.pImpl); // to swap Widgets, swap their pImpl pointers
	}
	... 
};
```

```cpp
namespace std {

template<> // revised specialization of std::swap
void swap<Widget>(Widget& a, Widget& b) {
	a.swap(b); // to swap Widgets, call their swap member function
}

}
```

만약 `Widget`이 클래스 템플릿으로 만들어져 있다고 하면`std::swap()`을 특수화하는 데 어려울 수 있다.

```cpp
template<typename T>
class WidgetImpl { ... };

template<typename T>
class Widget { ... };
```

C++은 클래스 템플릿에 대해서는 부분 특수화가 가능하지만 함수 템플릿에 대해서는 허용하지 않는다. 따라서 함수 템플릿을 "부분적으로 특수화"하고 싶을 때는 오버로드 버전을 추가한다.

```cpp
namespace std {

template<typename T> void swap(Widget<T>& a, Widget<T>& b) // an overloading of std::swap (note the lack of “<...>” after // “swap”), but see below for why this isn’t valid code
{ a.swap(b); }

}
```

`std` 내 템플릿 완전 특수화는 허용하지만, `std`에 새로운 템플릿을 추가하는 것은 불가하다. 

멤버 `swap()`을 호출하는 비멤버 `swap()`을 선언하되, 비멤버 함수를 `std::swap()`의 특수화 버전이나 오버로딩 버전으로 선언하지만 않으면 된다. 예를 들어 `Widget` 관련 기능이 `WidgetStuff`에 들어 있다면 다음과 같이 작성하면 된다.  

```cpp
namespace WidgetStuff { 
... // templatized WidgetImpl, etc.

template<typename T> class Widget { ... }; // as before, including the swap member function
...
template<typename T> void swap(Widget<T>& a, Widget<T>& b) // non-member swap function; not part of the std namespace
{
a.swap(b);
}

}
```

타입 `T` 전용 버전이 있으면 이를 호출하고, `T` 타입 전용 버전이 없으면 `std`의 일반 버전이 호출되도록 하고 싶다면 다음과 같이 구현한다.

```cpp
template<typename T>
void doSomething(T& obj1, T& obj2) {
	using std::swap; // make std::swap available in this function
	...
	swap(obj1, obj2); // call the best swap for objects of type T
	...
}
```

## Implementations

### Item 26: Postpone variable definitions as long as possible

이 함수는 비밀번호가 충분히 길 경우에 해당 비밀번호를 암호화하여 반환하는 함수다.

```cpp
// this function defines the variable "encrypted" too soon 
std::string encryptPassword(const std::string& password) {
	using namespace std;
	string encrypted;
	if (password.length() < MinimumPasswordLength) { 
		throw logic_error("Password is too short");
	}
	... // do whatever is necessary to place an encrypted version of password in encrypted
	return encrypted; 
}
```

`encrypted` 객체는 예외가 발생된 경우 사용되지 않는다. 즉, `encryptPassword()` 함수가 예외를 던지더라도 `encrypted` 객체의 생성과 소멸에 대한 비용을 내야 한다는 것이다.

```cpp
// this function postpones encrypted’s definition until it’s truly necessary 
std::string encryptPassword(const std::string& password)
{
	using namespace std;
	if (password.length() < MinimumPasswordLength) { 
		throw logic_error("Password is too short");
	}
	string encrypted;
	... // do whatever is necessary to place an encrypted version of password in encrypted
	return encrypted; 
}
```

### Item 27: Minimize casting

C++은 네 가지 캐스팅 연산자를 제공한다.

- `const_cast<T>(표현식)`: 객체의 상수성을 없애는 용도
- `dynamic_cast<T>(표현식)`: "안전한 다운캐스팅"을 할 때 사용
- `reinterpret_cast<T>(표현식)`: 포인터를 `int`로 바꾸는 등의 low-level 캐스팅을 위해 사용
- `static_cast<T>(표현식)`: 암시적 변환을 강제로 진행할 때 사용(`int`를 `double`로 바꾸는 등)

C++ 스타일의 캐스트를 쓰는 것이 바람직하다.  

`dynamic_cast` 연산자는 상당수 구현환경에서 클래스 이름에 대한 문자열 비교 연산에 기반으로 매우 느리게 구현되어 있다. 따라서 다른 방법이 가능하다면 `dynamic_cast`는 피해야 한다.

### Item 28: Avoid returning “handles” to object internals

`Rectangle` 클래스 객체를 썼을 때 메모리 부담을 최대한 줄이고 싶어, 사각형의 꼭지점을 별도의 구조체에 넣은 후 `Rectangle`이 이 구조체를 가리키도록 구현했다고 하자. `upperLeft()`와 `lowerRight()`를 통해 `Point` 객체에 대한 참조자를 반환하도록 했다.

```cpp
class Point { // class for representing points
public:
	Point(int x, int y); 
	...
	void setX(int newVal); 
	void setY(int newVal); 
	...
};

struct RectData { // Point data for a Rectangle
	Point ulhc; // ulhc = “upper left-hand corner”
	Point lrhc; // lrhc = “lower right-hand corner”
};

class Rectangle { 
public:
	Point& upperLeft() const { return pData->ulhc; } 
	Point& lowerRight() const { return pData->lrhc; }
	... 
private:
	std::tr1::shared_ptr<RectData> pData; // see Item 13 for info on tr1::shared_ptr
};
```

`upperLeft()`, `lowerRight()`는 상수 멤버 함수이다. 즉, `Rectangle` 객체는 수정할 수 없게 설계된 것이다. 그러나 이 함수들이 반환하는 것은 `private` 멤버인 내부 데이터에 대한 참조자다. 이를 사용해 마음대로 수정할 수 있다.

참조자, 포인터, 반복자는 모두 핸들(handle: 다른 객체에 손을 댈 수 있게 하는 매개자)이고, 어떤 객체의 내부요소에 대한 핸들을 반환하게 하면 언제든 그 객체의 캡슐화를 무너뜨리는 위험이 있다.

이는 멤버 함수 앞에 `const` 키워드를 붙여 해결할 수 있다.

```cpp
class Rectangle { 
public:
	...
	const Point& upperLeft() const { return pData->ulhc; } 
	const Point& lowerRight() const { return pData->lrhc; } 
	...
};
```

### Item 29: Strive for exception-safe code

```cpp
void PrettyMenu::changeBackground(std::istream& imgSrc)
{
	lock(&mutex); // acquire mutex (as in Item 14)
	delete bgImage; // get rid of old background 
	++imageChanges; // update image change count
	bgImage = new Image(imgSrc); // install new background
	unlock(&mutex);
}
```

**예외 안정성**을 가진 함수라면 예외가 발생할 때 다음과 같이 동작해야 한다.

- **자원이 새도록 만들지 않는다.** 자원 관리 전담 클래스를 사용해 해결할 수 있다.
	- `new Image(imgSrc)`에서 예외를 던지면 `unlock()` 함수가 실행되지 않아 뮤텍스가 계속 잡힌 상태
- **자료구조가 더럽혀지는 것을 허용하지 않는다.**
	- `new Image(imgSrc)`에서 예외를 던지면 `bgImage`가 가리키는 객체는 이미 삭제된 상태이며, 새로운 그림이 정상적으로 변경되지 않았음에도 `imageChanges` 변수는 증가된 상태

예외 안정성을 갖춘 함수는 다음 세 가지 보장(guarantee) 중 하나를 제공한다.

1. **기본적인 보장(basic guarantee)**
	- 함수 동작 중 예외가 발생하면, 실행 중인 프로그램에 관련된 모든 것들을 유효한 상태로 유지한다는 보장
2. **강력한 보장(strong guarantee)**
	- 함수 동작 중 예외가 발생하면, 프로그램 상태를 절대 변경하지 않는다는 보장
	- 호출이 성공하면 마무리까지 완벽하게 성공하고, 호출이 실패하면 함수 호출이 없었던 것처럼 상태가 되돌아감
	- **복사 후 맞바꾸기(copy-and-swap)**: 어떤 객체를 수정하고 싶으면 그 객체의 사본을 만들고 그 사본을 수정하는 것 
3. **예외불가 보장(nothrow guarantee)**
	- 예외를 던지지 않겠다는 보장
	- 약속한 동작은 끝까지 완수한다는 의미

```cpp
void someFunc() {
	... // make copy of local state
	f1(); 
	f2();
	... // swap modified state into place
}
```

`f1()` 혹은 `f2()`에서 보장하는 예외 안정성이 강력하지 못하면, `someFunc()` 역시 강력한 예외 안정성을 보장하기 힘들다.

### Item 30: Understand the ins and outs of inlining

`inline`은 컴파일레에 요청하는 것이지, 명력하는 것이 아니다. 클래스 정의 안에 함수를 바로 정의하면 컴파일러는 그 함수를 인라인 후보로 생각한다.

```cpp
class Person { 
public:
	...
	int age() const { return theAge; } // an implicit inline request: age is defined in a class definition
	...
private:
	int theAge;
};
```

함수 인라인은 작고, 자주 호출되는 함수에 대해서만 수행하자.  

> 대부분의 빌드 환경에서 인라인을 컴파일 도중에 실행하기 떄문에 대체로 헤더 파일에 있어야 한다.

### Item 31: Minimize compilation dependencies between files

pimpl(pointer to implementation) 패턴으로 설계하면 구현 세부사항과의 연관이 없게 된다. 

```cpp
#include <string> // standard library components shouldn’t be forward-declared
#include <memory> // for tr1::shared_ptr; see below

class PersonImpl; // forward decl of Person impl. class forward decls of classes used in Person interface
class Date; 
class Address;

class Person { 
public:
	Person(const std::string& name, const Date& birthday, 
				 const Address& addr);
	std::string name() const; 
	std::string birthDate() const; 
	std::string address() const; 
	...
private:
	std::tr1::shared_ptr<PersonImpl> pImpl; // ptr to implementation; see Item 13 for info on std::tr1::shared_ptr
};
```

`Person` 사용자 쪽에서는 컴파일을 다시 할 필요가 없다. 

> pimpl 패턴을 사용하는 `Person` 같은 클래스를 핸들 클래스라 한다.

인터페이스와 구현을 둘로 나누는 열쇠는 *정의부에 대한 의존성(dependencies on definitions)*을*선언부에 대한 의존성(dependencies on declarations*)으로 바꾸어 놓는 데 있다. 이것이 컴파일 의존성을 최소화하는 핵심 원리이다.

- **객체 참조자 및 포인터로 충분한 경우에는 객체를 직접 쓰지 않는다.**
- **가능하면 클래스 정의 대신 클래스 선언에 최대한 의존하도록 만든다.**
- **선언부와 정의부에 대해 별도의 헤더 파일을 제공한다.**

> 핸들 클래스 방법 대신 다른 방법으로는 `Person`을 추상 클래스, 즉 인터페이스 클래스로 만드는 방법도 있다. 이런 클래스는 데이터 멤버도 없고, 생성자도 없으며, 하나의 가상 소멸자와 순수 가상 함수들만 있다.

## Inheritance and Object-Oriented Design

### Item 32: Make sure public inheritance models “is-a.”

`public` 상속은 "is-a"를 의미한다. 

```cpp
class Person { ... };
class Student: public Person { ... }; // Student is a Person
```

> 

### Item 33: Avoid hiding inherited names

C++은 겹치는 이름들의 타입이 같냐 다르냐에 대한 부분은 신경쓰지 않고 덮어버린다.

```cpp
class Base { 
private:
	int x;
public:
	virtual void mf1() = 0; 
	virtual void mf1(int);
	virtual void mf2();
	void mf3();
	void mf3(double);
	... 
};

class Derived: public Base { 
public:
	virtual void mf1();
	void mf3();
	void mf4();
	... 
};
```

`Base` 클래스에 있는 함수들 중 `mf1()` 및 `mf3()`은 모두 `Derived` 클래스에 있는 `mf1()` 및 `mf3()`에 의해 가려진다. 이러한 현상은 바람직하지 않은 구현이다.

이렇게 가려진 심볼들은 `using` 선언으로 꺼내올 수 있다.

```cpp
class Derived: public Base { 
public:
	using Base::mf1; // make all things in Base named mf1 and mf3 visible (and public) in Derived’s scope
	using Base::mf3;

	virtual void mf1(); 
	void mf3();
	void mf4();
	...
};
```

### Item 34: Differentiate between inheritance of interface and inheritance of implementation

기하학적 도형을 나타내는 클래스 계통구조를 보자.(

```cpp
class Shape { 
public:
	virtual void draw() const = 0;
	virtual void error(const std::string& msg);
	int objectID() const;
	... 
};

class Rectangle: public Shape { ... }; 
class Ellipse: public Shape { ... };
```

`draw()`는 순수 가상 함수이며, 순수 가상 함수는 다음 두 특징을 가진다.

1. 순수 가상 함수를 물려받은 구체 클래스가 해당 순수 가상 함수를 다시 선언해야 한다.
2. 순수 가상 함수는 전형적으로 추상 클래스 안에서 정의를 갖지 않는다.

> 순수 가상 함수에도 정의를 제공할 수 있으며, 이 함수를 호출하려면 반드시 클래스 이름을 한정자로 붙여 주어야 한다.


