---
title: "Effective C++"
date: "2024-12-12"
author: "Beomsu Lee"
tags: ["c++", "language", "effective"]
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

1. **비트수준 상수성** 은 C++에서 적용하는 상수성이며, "그 객체의 어떤 데이터 멤버도 건드리지 않아야 그 멤버가 상수임을 정하는 개념"이다. 즉, 그 객체를 구성하는 비트들 중 어떤 것도 바뀌면 안된다는 것이다.
2. **논리적 상수성** 은 상수 함수여도 몇 비트 정도는 바꿀 수 있되, 사용자 측에서 알아채지 못하게만 하면 상수 멤버 자격이 있다고 판단하는 것이다(`mutable`).

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

이를 해결하기 위해선 기본 클래스에 **가상 소멸자** 를 선언하면 된다.

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

새로운 객체를 반환해야 하는 함수는 **새로운 객체를 반환하게 만들어야 한다.** 여기에 들어가는 비용은 올바른 동작에 지불되는 작은 비용이다. 

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

**예외 안정성** 을 가진 함수라면 예외가 발생할 때 다음과 같이 동작해야 한다.

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
	- **복사 후 맞바꾸기(copy-and-swap)** : 어떤 객체를 수정하고 싶으면 그 객체의 사본을 만들고 그 사본을 수정하는 것 
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

단순 가상 함수는 순수 가상 함수처럼 파생 클래스로 하여금 함수의 인터페이스를 상속하는 점은 같지만, 파생 클래스 쪽에서 오버라이드 할 수 있는 함수 구현부터 제공하는 점에서 다르다.

`error()`가 발생하더라도 파생 클래스에서 특별히 해주는 일이 없다면 `Shape()` 클래스에 기본으로 제공되는 에러 처리를 그냥 사용해도 된다.

비가상 함수인 `objectID()`는 파생 클래스에서 다른 행동이 일어날 것으로 가정하지 않는다는 뜻이다.

### Item 35: Consider alternatives to virtual functions

`healthValue()`는 캐릭터의 체력이 얼마나 남았는지를 나타내는 정수 값을 반환한다고 하자.

```cpp
class GameCharacter { 
public:
	virtual int healthValue() const; 	// return character’s health rating;
	... // derived classes may redefine this
};
```

#### The Template Method Pattern via the Non-Virtual Interface Idiom

`public` 비가상 멤버 함수를 통해 `private` 가상 함수를 간접적으로 호출하게 만드는 방법으로 NVI(Non-Virtual Interface) 패턴이 있다. 

```cpp
class GameCharacter { 
public:
	int healthValue() const { // derived classes do not redefine this — see Item 36
		... // do “before” stuff — see below
		int retVal = doHealthValue(); // do the real work
		... // do “after” stuff — see below
		return retVal; 
	}
	...
private:
	virtual int doHealthValue() const { // derived classes may redefine this
		... // default algorithm for calculating character’s health
	}
};
```

#### The Strategy Pattern via Function Pointers

체력 계산이 캐릭터의 일부가 아니라, 별개의 함수로 놓을수도 있다. 이는 전략(Strategy) 패턴의 예이다.

```cpp
class GameCharacter; // forward declaration
// function for the default health calculation algorithm 
int defaultHealthCalc(const GameCharacter& gc);

class GameCharacter { 
public:
	typedef int (*HealthCalcFunc)(const GameCharacter&);
	explicit GameCharacter(HealthCalcFunc hcf = defaultHealthCalc) 
	: healthFunc(hcf) 
	{}
	int healthValue() const
	{ return healthFunc(*this); }
	...
private:
	HealthCalcFunc healthFunc;
};
```

#### The Strategy Pattern via tr1::function

`tr1::function` 타입을 써서 기존 함수 포인터 `healthFunc`를 대신하게 만들 수 있다. 

```cpp
class GameCharacter; // as before 
int defaultHealthCalc(const GameCharacter& gc); // as before
class GameCharacter { 
public:
// HealthCalcFunc is any callable entity that can be called with
// anything compatible with a GameCharacter and that returns anything 
// compatible with an int; see below for details
	typedef std::tr1::function<int (const GameCharacter&)> HealthCalcFunc;
	explicit GameCharacter(HealthCalcFunc hcf = defaultHealthCalc) 
	: healthFunc(hcf)
	{}
	int healthValue() const
	{ return healthFunc(*this); }
	...
private:
	HealthCalcFunc healthFunc;
};
```

`HealthCalcFunc`은 `tr1::function` 템플릿을 인스턴스화한 것의 `typedef` 타입이다. 즉, 이 타입은 일반화된 함수 포인터 타입처럼 동작한다.

`HealthCalcFunc`는 `GameCharacter`를 참조자로 받고 `int`를 반환하는 함수로 이 시그니처와 호환되는 callable 객체 어떤 것도 가질 수 있다.

#### The “Classic” Strategy Pattern

체력 계산 함수를 나타내는 클래스 계통을 따로 만들고, 실제 계산 함수는 이 클래스 계통의 가상 멤버 함수로 만드는 방법도 있다.

```cpp
class GameCharacter; // forward declaration
class HealthCalcFunc { 
public:
	...
	virtual int calc(const GameCharacter& gc) const {...}
	...
};
HealthCalcFunc defaultHealthCalc;
class GameCharacter { 
public:
	explicit GameCharacter(HealthCalcFunc *phcf = &defaultHealthCalc) 
	: pHealthCalc(phcf)
	{}
	int healthValue() const
	{ return pHealthCalc->calc(*this); }
	...
private:
	HealthCalcFunc *pHealthCalc; 
};
```

### Item 36: Never redefine an inherited non-virtual function

비가상 함수는 **정적 바인딩(static binding)** 으로 묶인다. 따라서 `Base`의 비가상 함수를 `Derived` 클래스가 동일한 이름의 함수로 정의하고 있다면 의도하지 않은 동작이 발생할 수 있다.

### Item 37: Never redefine a function’s inherited default parameter value

가상 함수는 동적으로 바인딩되지만, 디폴트 파라미터 값은 정적으로 바인딩된다. 

```cpp
// a class for geometric shapes 
class Shape {
public:
	enum ShapeColor { Red, Green, Blue };
	// all shapes must offer a function to draw themselves 
	virtual void draw(ShapeColor color = Red) const = 0;
	...
};

class Rectangle: public Shape { 
public:
	// notice the different default parameter value — bad! 
	virtual void draw(ShapeColor color = Green) const;
	...
};
```

```cpp
Shape *ps; // static type = Shape*
Shape *pc = new Circle; // static type = Shape*
Shape *pr = new Rectangle; // static type = Shape*
```

`pr`의 `draw()` 함수는 동적으로 바인딩되지만, 정적 타입은 `Shape`이므로 디폴트 파라미터(`Red`)는 `Shape` 클래스에서 가져온다.

> NVI 패턴을 통해 해결할 수 있다.

### Item 38: Model “has-a” or “is-implemented-in-terms-of” through composition

Composition이란 어떤 타입의 객체들이 그와 다른 타입의 객체들을 포함하고 있을 경우 성립하는 그 타입들 사이 관계를 말한다.

```cpp
class Address { ... }; // where someone lives
class PhoneNumber { ... };
class Person { 
public:
	...
private:
	std::string name; // composed object
	Address address; // ditto
	PhoneNumber voiceNumber; // ditto
	PhoneNumber faxNumber; // ditto
};
```

Composition은 "has-a" 또는 "is-implemented-in-terms-of"를 뜻한다. 이는 소프트웨어 개발에서의 영역(domain)이 두 가지이기 때문이다.

1. 응용 영역(Application domain)
	- 일상생활에서 볼 수 있는 사물을 본 뜬 것
	- "has-a" 관계
2. 구현 영역(Implementation domain)
	- 버퍼, 뮤텍스 등 순수하게 시스템 구현만을 위한 인공물
	- "is-implemented-in-terms-of" 관계

`List` 클래스를 써서 `Set` 클래스를 만든다고 하자. `List`를 상속받을 수 있으나, `Set`은 중복 원소를 가질 수 없는 컨테이너이므로 두 클래스 관계가 `public` 상속("is-a")이 맞지 않다. 그러나 `List` 객체를 사용해 구현되는 형태의 설계로 해결 가능하다.

```cpp
template<typename T>
bool Set<T>::member(const T& item) const {
	return std::find(rep.begin(), rep.end(), item) != rep.end(); 
}

template<typename T>
void Set<T>::insert(const T& item) {
	if (!member(item)) rep.push_back(item); 
}

template<typename T>
void Set<T>::remove(const T& item) {
	typename std::list<T>::iterator it = // see Item 42 for info on “typename” here
		std::find(rep.begin(), rep.end(), item);
	if (it != rep.end()) rep.erase(it); 
}

template<typename T> std::size_t Set<T>::size() const {
	return rep.size(); 
}
```

### Item 39: Use private inheritance judiciously

`private` 상속의 의미는 "is-implemented-in-terms-of"이다. `Base` 클래스로부터 `private` 상속을 통해 `Derived` 클래스를 파생시킨 것은 `Base` 클래스에서 쓸 수 있는 기능들을 활용할 목적이지, 두 클래스 간 어떤 개념적 관계가 있어 한 행동이 아니다. 즉, `private` 상속은 그 자체로 구현 기법 중 하나이다.

Item 38에 소개한 Composition도 "is-implemented-in-terms-of"의 의미를 갖는다. 가능하면 Composition을 사용하고, 꼭 필요한 경우 `private` 상속을 사용하자.

`private` 상속 대신 `public` 상속에 Composition 조합이 더 많이 쓰인다. 다음 두 가지 장점이 있기 때문이다.

1. `Widget` 클래스를 설계하는 데 있어 파생은 가능하되, 파생 클래스에서 `onTick()`을 재정의할 수 없도록 설계 차원에서 막고 싶을 때 유용하다.
2. `Widget`의 컴파일 의존성을 최소화할 수 있다.

```cpp
class Timer {
public:
	explicit Timer(int tickFrequency); 
	virtual void onTick() const; // automatically called for each tick
	... 
};
```

```cpp
class Widget { 
private:
	class WidgetTimer: public Timer {
	public:
		virtual void onTick() const;
		... 
	};
	WidgetTimer timer;
	... 
};
```

> `private` 상속은 EBO(Empty Base Optimization)를 활성화시킬 수 있다. 이는 객체 크기를 고민하는 라이브러리 개발자에게 매력적인 특징이다.

### Item 40: Use multiple inheritance judiciously

다중 상속(MI: Multiple Inheritance)은 둘 이상의 기반 클래스로부터 똑같은 이름을 물려받을 가능성이 있다.

```cpp
class BorrowableItem { // something a library lets you borrow
public:
	void checkOut(); // check the item out from the library
	... 
};
class ElectronicGadget { 
private:
	bool checkOut() const; // perform self-test, return whether test succeeds
	...
};
```

`checkOut()` 함수를 호출하는 부분에서 모호성이 발생한다. 이 모호성을 해소하기 위해 호출할 기반 클래스의 함수를 손수 지정해주어야 한다.

MI는 상위 단계의 기반 클래스를 여러 개 갖는 클래스 계통에서 "죽음의 마름모꼴(deadly MI diamond)"라고 알려진 좋지 않은 모양이 나올 수 있다.

```cpp
class File { ... };
class InputFile: public File { ... };    
class OutputFile: public File { ... };
class IOFile: public InputFile, public OutputFile {...};
```

이렇게 기반 클래스와 파생 클래스 사이 경로가 두 개 이상 되는 상속 계통에서 기반 클래스의 데이터 멤버가 경로 개수만큼 중복 생성된다.

`virtual public` 상속을 통해 데이터 멤버의 중복 생성을 막을 수도 있지만, `virtual` 상속을 사용한 클래스로 만들어진 객체는 `virtual` 상속을 쓰지 않은 것보다 크기가 더 크다. 또한 `virtual` 기반 클래스의 데이터 멤버에 접근하는 속도도 `non-virtual` 기반 클래스의 데이터 멤버에 접근하는 속도보다 느리다. 

그러므로 `virtual` 기반 클래스에 대한 조언은 간단하다.

1. 구태여 쓸 필요가 없다면 `virtual` 기반 클래스를 사용하지 말자.
2. `virtual` 기반 클래스를 꼭 사용해야 하는 상황이라면, `virtual` 기반 클래스에 최대한 데이터 멤버를 넣지 않는 쪽으로 신경써라.

> 다중 상속을 적법하게 쓸 수 있는 경우가 있다. 여러 시나리오 중 하나는 인터페이스 클래스로부터 `public` 상속을 하고, 동시에 구현을 돕는 클래스로부터 `private` 상속을 하는 것이다.

## Templates and Generic Programming

### Item 41: Understand implicit interfaces and compile-time polymorphism

객체 지향 프로그램의 주요 특징은 명시적 인터페이스(explicit interface)와 런타임 다형성(runtime polymorphism)이다.

`Widget` 클래스와 이를 사용하는 `doProcessing()` 함수가 있다고 하자.

```cpp
class Widget { 
public:
	Widget();
	virtual ~Widget();
	virtual std::size_t size() const; 
	virtual void normalize();
	void swap(Widget& other); // see Item 25
	... 
};
```

```cpp
void doProcessing(Widget& w) {
	if (w.size() > 10 && w != someNastyWidget) { 
		Widget temp(w);
		temp.normalize();
		temp.swap(w);
	} 
}
```

`w`는 `Widget` 타입으로 해당 클래스의 인터페이스를 지원해야 한다. 이 인터페이스를 가리켜 **명시적 인터페이스** 라 한다.

`Widget`의 멤버 함수 중 몇 개는 `virtual` 함수이므로, 이 `virtual` 함수에 대한 호출은 **런타임 다형성** 에 이루어진다. 

템플릿 일반화 프로그래밍은 이와는 다른 부분이 있다. 명시적 인터페이스 및 런타임 다형성은 그대로 존재한다. 추가로 **암시적 인터페이스(implicit interface)** 와 **컴파일 타임 다형성(compile-time polymorphism)** 이 있다.

`doProcessing()`을 함수 템플릿으로 바꾸어 보자.

```cpp
template<typename T> 
void doProcessing(T& w) {
	if (w.size() > 10 && w != someNastyWidget) { 
		T temp(w);
		temp.normalize();
		temp.swap(w);
	} 
}
```

`w`가 지원해야 하는 인터페이스는 이 템플릿 안에서 `w`에 대해 실행되는 연산이 결정한다. `T`는 `size()`, `normalize()`, `swap()` 멤버 함수를 지원해야 한다. 이 템플릿이  제대로 컴파일되려면 일부 표현식이 유효해야 하는데, 이 표현식들은 `T`가 지원해야 하는 **암시적 인터페이스** 라는 것이다.

`w`가 수반되는 함수 호출이 일어날 때, 예를 들어 `operator>` 및 `operator!=` 함수가 호출될 때 해당 호출을 성공시키기 위해 템플릿 인스턴스화가 일어난다. 이 인스턴스화가 일어나는 시점은 컴파일 도중이다. 인스턴스화를 진행하는 함수 템플릿에 어떤 템플릿 매개변수가 들어가느냐에 따라 호출되는 함수가 달라지기 때문에, 이것을 가리켜 **컴파일 타임 다형성** 이라 한다.

암시적 인터페이스는 함수 시그니처에 기반하고 있지 않다. 암시적 인터페이스를 이루는 요소는 유효 표현식(expression)이다. `T`는 다음과 같은 제약이 있다.

- `doProcessing()` 템플릿의 `T`는 정수 계열의 값을 반환하고 이름이 `size()`인 함수를 지원해야 한다.
- `T` 타입 객체 둘을 비교하는 `operator!=` 함수를 지원해야 한다.

실제로는 연산자 오버로딩 가능성이 있기 때문에 `T`는 위 두 제약 중 어떤 것도 만족시킬 필요가 없다. `size()` 멤버 함수는 `operator>`가 성립될 수 있도록 어떤 `X` 타입의 객체만 반환하면 된다. 

`operator!=` 함수도 마찬가지로, `T`가 `operator!=` 함수를 지원해야 하는 필수 요구사항이 아니다. `operator!=`가 `X` 타입의 객체 하나와 `Y` 타입의 객체 하나를 받아들인다고 하면 이 부분은 별 걸림돌 없이 넘어갈 수 있다.

결과적으로 `if`문의 조건식 부분은 불(boolean) 표현식이어야 하기 때문에, 표현식에 쓰이는 것들이 어떤 타입인지 상관없이 이 조건식 부분의 결과 값은 `bool`과 호환되어야 한다. 이것이 `doProcessing()` 템플릿 타입 매개변수인 `T`에 대해 요구하는 암시적 인터페이스의 일부이다.

나머지 복사 생성자, `normalize()`, `swap()` 함수에 대한 호출이 `T` 타입의 객체에 대해 '유효'해야 한다.

### Item 42: Understand the two meanings of typename

다음과 같은 함수 템플릿이 있다고 하자.

```cpp
template<typename C> // print 2nd element in container;
void print2nd(const C& container) { // this is not valid C++!
	if (container.size() >= 2) { 
		C::const_iteratoriter(container.begin()); // get iterator to 1st element
		++iter; // move iter to 2nd element
		int value = *iter;  // copy that element to an int 
		std::cout << value; // print the int
	} 
}
```

`iter`의 타입은 `C::const_iteratoriter`인데, 템플릿 매개변수 `C`에 따라 달라지는 타입이다. 이렇게 템플릿 매개변수에 종속된 것을 가리켜 **의존 이름(dependent name)** 이라 한다. 템플릿 매개변수가 특정 타입을 나타낼 때 그 타입 안에 정의된 멤버, 형식(type), 또는 함수 이름을 참조하는 경우 이를 **중첩 의존 이름(nested dependent name)** 이라 한다.

`value`는 `int` 타입이며, 템플릿 매개변수가 어떻든 상관없는 타입이다. 이를 **비의존 이름(non-dependent name)** 이라 한다.

코드 안에 중첩 의존 이름이 있으면 컴파일러가 구문 분석할 때 애로사항이 있을 수 있다.

```cpp
template<typename C>
void print2nd(const C& container) {
	C::const_iterator * x;
	... 
}
```

만약 `C::const_iterator`가 타입이 아니고, `const_iterator`라는 이름을 가진 정적 데이터 멤버이고, `x`가 다른 전역 변수의 이름이라면, 이 경우 `C::const_iterator`와 `x`를 피연산자로 한 곱셈 연산이 된다.

C++은 이런 모호성을 해결하기 위해 구문 분석할 때 중첩 의존 이름을 만난다면 타입이라고 알려주지 않는 한 그 이름이 타입이 아니라고 가정하는 규칙이 있다.

따라서 `iter`의 선언이 선언으로서 의미가 있으려면 `C::const_iterator`가 반드시 타입이어야 하는데, 이 경우 `C::const_iterator` 앞에 `typename` 키워드를 붙인다.

```cpp
typename C::const_iterator iter(container.begin());
```

> `typename`은 중첩 의존 이름만 식별하는데 사용해야 한다. 그 외 이름은 `typename`을 가져선 안 된다.

> 중첩 의존 타입 이름이 기반 클래스 리스트에 있거나, 멤버 초기화 리스트 내 기반 클래스 식별자로서 있을 경우 `typename` 붙여주면 안 된다.

### Item 43: Know how to access names in templatized base classes

회사에 메시지를 전송할 수 있는 앱을 만든다고 하자. `MsgSender` 클래스는 `Company` 템플릿 매개변수를 받는다.

```cpp
template<typename Company> 
class MsgSender {
public:
	... // ctors, dtor, etc.
	void sendClear(const MsgInfo& info) {
		std::string msg; create msg from info;
		Company c;
		c.sendCleartext(msg); 
	}
	void sendSecret(const MsgInfo& info) // similar to sendClear, except calls c.sendEncrypted
	{ ... }
};
```

여기에 메시지를 보낼 때마다 관련 정보를 남기고 싶은 경우 파생 클래스에서 `sendClear()`를 호출하여 이 기능을 쉽게 붙일 수 있다.

```cpp
template<typename Company>
class LoggingMsgSender: public MsgSender<Company> { 
public:
	... // ctors, dtor, etc.
	void sendClearMsg(const MsgInfo& info) {
		// write "before sending" info to the log;
		sendClear(info); // call base class function; this code will not compile!
		// write "after sending" info to the log; 
	}
	... 
};
```

하지만 이 코드는 `sendClear()` 함수가 존재하지 않기 때문에 컴파일되지 않는다. 문제는 컴파일러가 `LoggingMsgSender` 클래스 템플릿 정의와 마주칠 때 이 클래스가 어디서 파생된 것인지 모른다는 것이다. `MsgSender<Company>`인 것은 분명하나, `Company`는 템플릿 매개변수이고, 이 템플릿 매개변수(`LoggingMsgSender`가 인스턴스로 만들어질 때)는 나중까지 아무것도 무엇이 될지 알 수 없다.

이를 해결하기 위한 세 가지 방법이 존재한다.

1. 기반 클래스 함수에 대한 호출문 앞에 `this->`를 붙인다.
	```cpp
	this->sendClear(info); 
	```
2. `using` 선언을 사용한다.
	```cpp
	using MsgSender<Company>::sendClear; 
	```
3. 호출할 함수가 기반 클래스 함수라는 것을 명시적으로 지정한다.
	```cpp
	MsgSender<Company>::sendClear(info);
	```

> 마지막 방법은 호출되는 함수가 가상 함수인 경우, 바인딩이 무시될 수 있기에 추천하지 않는다.

### Item 44: Factor parameter-independent code out of templates

아무 생각 없이 템플릿을 사용하면 코드 비대화(code bloat)가 초래될 수 있다. 따라서 코드가 비대화되는 불상사를 미연에 방지할 방법을 알아두어야 한다.

**공통성 및 가변성 분석(commonality and variability analysis)** 을 통해 코드 비대화를 방지할 수 있다.

템플릿을 작성할 경우 템플릿이 아닌 코드에서는 코드 중복이 명시적이지만, 템플릿 코드에서는 코드 중복이 암시적이다. 소스코드에는 템플릿이 하나밖에 없기 때문에, 어떤 템플릿이 여러 번 인스턴스화될 때 발생할 수 있는 코드 중복을 감각적으로 알아채야 한다는 것이다.

정방행렬을 나타내는 템플릿을 만든다고 하자. 이 행렬은 역행렬 연산을 지원한다.

```cpp
template<typename T, std::size_t n> // template for n x n matrices of objects of type T; see below for info on the size_t parameter
class SquareMatrix { 
public:
	...
	void invert(); // invert the matrix in place
};
```

이 템플릿은 `size_t` 타입의 비타입 매개변수(non-type parameter) `n`을 받는다.

```cpp
SquareMatrix<double, 5> sm1; 
SquareMatrix<double, 10> sm2; 
```

이 때 `invert()`는 사본이 인스턴스화되는데 만들어지는 사본의 개수가 두 개이다. 하지만 행과 열의 크기를 나타내는 상수만 빼면 두 함수는 완전히 동일하다. 이 현상이 코드 비대화를 일으키는 일반적인 형태 중 하나이다.

`SquareMatrixBase`를 추가해 다음과 같이 구현해보자.

```cpp
template<typename T> class SquareMatrixBase { 
protected:
	SquareMatrixBase(std::size_t n, T *pMem) // store matrix size and a ptr to matrix values
	: size(n), pData(pMem) {}
	void invert(std::size_t matrixSize); // invert matrix of the given size
	void setDataPtr(T *ptr) { pData = ptr; } // reassign pData
	...
private: 
	std::size_t size; // size of matrix
	T *pData; // pointer to matrix values
};
```

행렬의 크기를 매개변수로 받도록 바뀐 `invert()` 함수가 기반 클래스에 있다. `SquareMatrixBase`는 행렬의 원소가 갖는 타입에 대해서만 템플릿화되어 있을 뿐이다. 따라서 같은 타입 객체를 원소로 갖는 모든 정방행렬은 오직 한 가지의 `SquareMatrixBase` 클래스를 공유한다.

`SquareMatrixBase::invert()`는 자신이 상대할 데이터가 어떤 데이터인지 알아야 하는데, 이는 행렬 값(들)을 담는 메모리에 대한 포인터를 `SquareMatrixBase`가 저장하게 하여 해결할 수 있다.

이렇게 설계하면 메모리 할당 방법의 결정 권한이 파생 클래스 쪽으로 넘어가게 된다. 어느 메모리에 데이터를 저장하느냐에 따라 설계가 달리지겠지만, 코드 비대화 측면에서 효과를 볼 수 있다.

### Item 45: Use member function templates to accept “all compatible types.”

스마트 포인터로 암시적인 타입 변환을 표현하려면 까다롭다.

```cpp
template<typename T> 
class SmartPtr {
public: // smart pointers are typically initialized by built-in pointers
	explicit SmartPtr(T *realPtr);
	... 
};
SmartPtr<Top> pt1 = SmartPtr<Middle>(new Middle); // convert SmartPtr<Middle> => SmartPtr<Top>
SmartPtr<Top> pt2 = SmartPtr<Bottom>(new Bottom); // convert SmartPtr<Bottom> => SmartPtr<Top>
SmartPtr<const Top> pct2 = pt1; // convert SmartPtr<Top> => SmartPtr<const Top>
```

같은 템플릿으로 만들어진 다른 인스턴스들 사이에는 어떤 관계도 없기 때문에, 컴파일러에게는 `SmartPtr<Middle>`과 `SmartPtr<Top>`은 완전 별개의 클래스다. `SmartPtr` 클래스들 사이 변환을 하고 싶다면, 변환되도록 직접 프로그램을 만들어야 한다.

원칙적으로 원하는 생성자의 개수는 *무제한*이다. 템플릿을 인스턴스화하면 무제한 개수의 함수를 만들어 낼 수 있다. 바로 생성자를 만들어내는 템플릿을 쓰는 것이다. 이 생성자 템플릿은 **멤버 함수 템플릿(member function template)** 의 한 예이다. 멤버 함수 템플릿은 어떤 클래스의 멤버 함수를 찍어내는 템플릿을 말한다.

```cpp
template<typename T> 
class SmartPtr {
public:
	template<typename U> // member template for a ”generalized copy constructor”
	SmartPtr(const SmartPtr<U>& other); 
	...
};
```

모든 `T` 타입 및 모든 `U` 타입에 대해 `SmartPt<T>` 객체가 `SmartPtr<U>`로부터 생성될 수 있다는 의미이다. 이런 꼴의 생성자를 가리켜 **일반화 복사 생성자(generalized copy constructor)** 라 한다.

하지만 이 일반화 복사 생성자는 `SmartPtr<Top>`으로부터 `SmartPtr<Bottom>`을 생성할 수 있다. 

멤버 초기화 리스트를 사용해 `SmartPtr<T>` 데이터 멤버인 `T*` 타입의 포인터를 `SmartPtr<U>`에 들어 있는 `U*` 타입의 포인터로 초기화했다. 이렇게 하면 `U*`에서 `T*`로 진행되는 암시적 변환이 가능할 때만 컴파일 에러가 발생하지 않는다.

```cpp
template<typename T> 
class SmartPtr {
public:
	template<typename U> SmartPtr(const SmartPtr<U>& other) // initialize this held ptr with other’s held ptr
	: heldPtr(other.get()) { ... }
	T* get() const { return heldPtr; }
	...
private: // built-in pointer held by the SmartPtr
	T *heldPtr;
};
```

### Item 46: Define non-member functions inside templates when type conversions are desired

Item 24에서 소개된 `Rational` 클래스에 대한 `operator*` 부분을 템플릿으로 변경해보자.

```cpp
template<typename T>
class Rational { 
public:
	Rational(const T& numerator = 0, const T& denominator = 1); // see Item 20 for why params are now passed by reference
	const T numerator() const; // see Item 28 for why return values are still passed by value
	const T denominator() const; // Item 3 for why they’re const
	...
};

template<typename T>
const Rational<T> operator*(const Rational<T>& lhs, const Rational<T>& rhs)
{...}
```

```cpp
Rational<int> oneHalf(1, 2); // this example is from Item 24, except Rational is now a template
Rational<int> result = oneHalf * 2; // error! won’t compile
```

`operator*`에 넘겨진 두 번째 매개변수 `2`는 `int` 타입이다. 따라서 `2`를 `Rational<int>`로 변환하고, 이를 통해 `T`가 `int`라 유추할 수 있다고 생각할 수 있다. 하지만 컴파일러는 템플릿 인자 추론 과정에서 암시적 타입 변환이 고려되지 않아 이런 방식으로 동작하지 않는다.

클래스 템플릿 안에 프렌드 함수를 넣으면 함수 템플릿으로서의 성격을 주지 않고 특정한 함수 하나를 나타낼 수 있다는 사실을 이용해 해결할 수 있다. 즉, `Rational<T>` 클래스에 대해 `operator*`를 프렌드 함수로 선언하는 것이 가능하다는 말이다. 클래스 템플릿 인자는 인자 추론 과정에 좌우되지 않으므로, `T`에 대한 정확한 정보는 `Rational<T>` 클래스가 인스턴스화되는 시점에 알 수 있다.

```cpp
template<typename T>
class Rational {
public:
	...
friend // declare operator* function (see below for details)
	const Rational operator*(const Rational& lhs, const Rational& rhs);
};
```

`oneHalf` 객체가 `Rational<int>` 타입으로 선언되며 `Rational<int>` 클래스가 인스턴스로 만들어지고, 이때 그 과정의 일부로서 `Rational<int>` 타입의 매개변수를 받는 프렌드 함수인 `operator*`도 자동으로 선언되기 때문이다. 이전과 달리 지금은 함수가 선언된 것이므로, 컴파일러는 이 호출문에 대해 암시적 변환 함수를 적용할 수 있게 된다.

그러나 이 코드는 링크가 되지 않는다. `operator*` 함수는 `Rational` 안에 선언되어 있지, 정의까지 된 것은 아니다. 

`operator*` 함수의 본문을 선언부와 붙이면 컴파일 및 링크까지 수행된다.

```cpp
template<typename T> 
class Rational {
public:
	...
friend const Rational operator*(const Rational& lhs, const Rational& rhs) {
	return Rational(lhs.numerator() * rhs.numerator(), lhs.denominator() * rhs.denominator()); // same impl as in Item 24
}
};
```

### Item 47: Use traits classes for information about types

`advance()` 템플릿은 지정된 반복자를 지정된 거리만큼 이동시키는 것이다.

```cpp
template<typename IterT, typename DistT> // move iter d units forward; 
void advance(IterT& iter, DistT d);      // if d < 0, move iter backward
```

`+=` 연산을 지원하는 반복자는 임의 접근 반복자 뿐이므로, `iter += d`와 같이 구현하는 것은 한계가 있다. 다른 타입의 경우 `++`, `--` 연산을 사용해 구현해야 한다.

STL 반복자는 각 반복자가 지원하는 연산에 따라 다섯 개의 범주로 나뉜다.

1. 입력 반복자(input iterator)
	- 전진만 가능
	- 한 번에 한 칸씩 이동
	- 자신이 가리키는 위치에서 읽기만 가능하며, 읽을 수 있는 횟수는 1번
2. 출력 반복자(output iterator)
	- 입력 반복자와 비슷하나 출력용인 점만 다름
	- 자신이 가리키는 위치에 쓰기만 가능하며, 쓸 수 있는 횟수는 1번
3. 순방향 반복자(forward iterator)
	- 입력 반복자와 출력 반복자가 하는 일은 기본적으로 다 할 수 있음
	- 자신이 가리키는 위치에서 읽기, 쓰기를 동시에 할 수 있으며, 여러 번 가능
4. 양방향 반복자(bidirectional iterator)
	- 순방향 반복자에 뒤로가는 기능 추가
5. 임의 접근 반복자(random access iterator)
	- 양방향 반복자에 "반복자 산술 연산" 수행 기능 추가

C++ 표준 라이브러리는 위 다섯 개의 반복자 범주 각각을 식별하는 데 쓰이는 태그(tag) 구조체가 정의되어 있다.

```cpp
struct input_iterator_tag {};
struct output_iterator_tag {};
struct forward_iterator_tag: public input_iterator_tag {};
struct bidirectional_iterator_tag: public forward_iterator_tag {};
struct random_access_iterator_tag: public bidirectional_iterator_tag {};
```

다음 코드가 제대로 동작하려면 `iter`가 임의 접근 반복자인지를 판단할 수 있어야 한다.

```cpp
template<typename IterT, typename DistT> void advance(IterT& iter, DistT d) {
	if (iter is a random access iterator) { 
		iter += d; // use iterator arithmetic for random access iters
	} else {
		if (d >= 0) { while (d--) ++iter; } // use iterative calls to ++ or -- for other iterator categories
		else { while (d++) --iter; }
	}
}
```

여기서 필요한 것이 **특성정보(traits)** 이다. 컴파일 도중 어떤 타입의 정보를 얻을 수 있게 하는 객체를 지칭하는 개념이다.

> 특성정보 기법은 포인터 등의 기본제공 타입에 적용할 수 있어야 한다.

특성정보를 다루는 표준적인 방법은 해당 특성정보 템플릿 및 그 템플릿의 1개 이상의 특수화 버전에 넣는 것이다. 반복자의 경우 `iterator_traits`라는 이름으로 준비되어 있다.

```cpp
template<typename IterT> // template for information about iterator types
struct iterator_traits; 
```

위처럼 특성정보를 구현하는 데 사용한 구조체를 가리켜 **특성정보 클래스** 라 한다.

`iterator_traits<IterT>` 안에 `IterT` 타입 각각에 대한 `iterator_category`라는 이름의 `typedef` 타입이 선언되어 있다. 이렇게 선언된 `typedef` 타입이 `IterT` 반복자의 범주를 가리키는 것이다.

`iterator_traits` 클래스는 이 반복자 범주를 두 부분으로 나누어 구현한다.

1. 사용자 정의 반복자 타입에 대한 구현

	사용자 정의 반복자 타입으로 하여금 `iterator_category`라는 이름의 `typedef` 타입을 내부에 가질 것을 요구사항으로 둔다. 예를 들어, `list`의 반복자는 양방향 반복자이기 때문에 다음과 같다. 

	```cpp
	template < ... > 
	class list { 
	public:
		class iterator { 
		public:
			typedef bidirectional_iterator_tag iterator_category;
				... 
			};
		... 
	};
	```

	이 `iterator` 클래스가 내부에 지닌 중첩 `typedef` 타입을 똑같이 재생한 것이 `iterator_traits`다.

	```cpp
	// the iterator_category for type IterT is whatever IterT says it is; 
	// see Item 42 for info on the use of “typedef typename” 
	template<typename IterT>
	struct iterator_traits {
		typedef typename IterT::iterator_category iterator_category;
		... 
	};
	```

	위 코드는 사용자 정의 타입에서 잘 돌아가나, 반복자의 실제 타입이 포인터인 경우 전혀 돌아가지 않는다. 포인터 안에 `typedef` 타입이 중첩되는 것부터 말이 안 되기 때문이다.

2. 반복자가 포인터인 경우의 처리

	포인터 타입 반복자를 지원하기 위해 `iterator_traits`는 포인터 타입에 대한 **부분 템플릿 특수화(partial template specialization)** 버전을 제공한다.

	포인터의 동작 원리가 임의 접근 반복자와 똑같으므로, `iterator_traits`가 이런 식으로 지원하는 반복자 범주가 바로 임의 접근 반복자이다.

	```cpp
	template<typename T> // partial template specialization for built-in pointer types
	struct iterator_traits<T*> 
	{
		typedef random_access_iterator_tag iterator_category;
		... 
	};
	```

지금까지가 특성정보 클래스의 설계 및 구현 방법이다.

1. 다른 사람이 사용하도록 열어주고 싶은 타입 관련 정보를 확인(반복자의 경우 반복자 범주)
2. 그 정보를 식별하기 위한 이름을 선택(`iterator_category`)
3. 지원하고자 하는 타입 관련 정보를 담은 템플릿 및 그 템플릿의 특수화 버전(`iterator_traits`) 제공

따라서 `iterator_traits`가 주어졌으므로 `advance()`의 의사 코드를 다음과 같이 다듬을 수 있다.

```cpp
template<typename IterT, typename DistT> void advance(IterT& iter, DistT d)
{
	if (typeid(typename std::iterator_traits<IterT>::iterator_category) == 
			typeid(std::random_access_iterator_tag))
	... 
}
```

`if`문을 통해 태그를 구분할 수 있지만 프로그램 실행 도중 평가되므로, 컴파일 도중에 조건처리를 수행하기 위해서는 템플릿 오버로딩을 사용한다.

```cpp
template<typename IterT, typename DistT> // use this impl for random access iterators
void doAdvance(IterT& iter, DistT d, std::random_access_iterator_tag) 
{
	iter += d;
}
template<typename IterT, typename DistT> // use this impl for bidirectional iterators
void doAdvance(IterT& iter, DistT d, std::bidirectional_iterator_tag) 
{
	if (d >= 0) { while (d--) ++iter; } 
	else { while (d++) --iter; }
}
template<typename IterT, typename DistT> // use this impl for input iterators
void doAdvance(IterT& iter, DistT d, std::input_iterator_tag)
{
	if (d < 0) {
		throw std::out_of_range("Negative distance"); // see below
	}
	while (d--) ++iter;
}
```

이제 `advance()`가 `doAdvance()`를 호출할 때 적절한 반복자 범주 타입 객체를 전달해주어야 한다.

```cpp
template<typename IterT, typename DistT> 
void advance(IterT& iter, DistT d)
{
	doAdvance(iter, d, // call the version of doAdvance
		typename std::iterator_traits<IterT>::iterator_category() // that is appropriate for iter’s iterator category
	); 
}
```

### Item 48: Be aware of template metaprogramming

TMP는 컴파일 도중 실행되는 템플릿 기반 프로그램을 작성하는 것을 말한다. TMP는 강점 두 가지가 있다.

1. TMP를 쓰면 다른 방법으로는 불가능한 일을 쉽게 할 수 있다.
2. TMP는 C++ 컴파일이 진행되는 동안 실행되기 때문에, 기존 작업을 런타임 영역에서 컴파일 타임 영역으로 전환할 수 있다.

이러한 결과로 런타임에 발생되는 에러들을 컴파일 도중 찾을 수 있으며, TMP를 쓰면 모든 면에서 효율적일 여지가 많아진다.

TMP에서는 `if ... else` 구문을 나타내는 데 템플릿 및 템플릿 특수화 버전을 사용한다.

TMP의 동작에서 루프를 빼놓을 수 없는데, 재귀를 통해 루프 효과를 낸다. 그런데 TMP의 루프는 재귀 함수 호출을 만들지 않고 **재귀식 템플릿 인스턴스화(recursive template instantiation)** 를 한다.

다음은 계승을 계산하는 템플릿이다.

```cpp
template<unsigned n> // general case: the value of Factorial<n> is n times the value of Factorial<n-1> 
struct Factorial { 
	enum { value = n * Factorial<n-1>::value };
};
template<> // special case: the value of struct 
Factorial<0> { // Factorial<0> is 1
	enum { value = 1 }; 
};
```

C++ 프로그래밍에서 TMP가 효과를 발휘하는 예는 세 가지가 있다.

1. 치수 단위(dimensional unit)의 정확성 확인
2. 행렬 연산의 최적화
3. 맞춤식 디자인 패턴 구현의 생성

## Customizing new and delete

### Item 49: Understand the behavior of the new-handler

`operator new` 함수가 예외를 던지기 전, 이 함수는 사용자 쪽에서 지정할 수 있는 에러 처리 함수를 우선적으로 호출하게 되어 있다. 이 에러 처리 함수를 가리켜 new handler라고 한다.

```cpp
namespace std {
	typedef void (*new_handler)();
	new_handler set_new_handler(new_handler p) throw(); 
}
```

사용자가 요청한 만큼 메모리를 할당하지 못하면, `operator new`는 충분한 메모리를 찾아낼 때까지 new handler를 되풀이해서 호출한다. New handler는 다음 동작 중 하나를 꼭 해주어야 한다.

1. 사용할 수 있는 메모리를 더 많이 확보한다.
2. 다른 new handler를 설치한다.
3. new handler의 설치를 제거한다.
4. 예외를 던진다.
5. 복귀하지 않는다.

`Widget` 클래스에 대한 메모리 할당 실패를 처리하고 싶다면, 호출될 new handler 함수를 만들어야 하므로, 이를 가리키는 `new_handler` 타입의 정적 멤버 데이터를 선언한다.

```cpp
class Widget { 
public:
	static std::new_handler set_new_handler(std::new_handler p) throw(); 
	static void* operator new(std::size_t size) throw(std::bad_alloc);
private:
	static std::new_handler currentHandler;
};

std::new_handler Widget::currentHandler = 0; // init to null in the class impl. file
```

`Widget`이 제공하는 `set_new_handler()` 함수는 자신에게 넘어온 포인터를 아무 점검 없이 저장하고, 바로 전에 저장했던 포인터를 점검 없이 반환한다. (표준 라이브러리의 `set_new_handler()`와 동일)

```cpp
std::new_handler Widget::set_new_handler(std::new_handler p) throw() {
	std::new_handler oldHandler = currentHandler; 
	currentHandler = p;
	return oldHandler;
}
```

```cpp
void outOfMem(); // decl. of func. to call if mem. alloc. for Widget objects fails

Widget::set_new_handler(outOfMem); // set outOfMem as Widget’s new-handling function
Widget *pw1 = new Widget; // if memory allocation fails, call outOfMem 

std::string *ps = new std::string; // if memory allocation fails, call the global new-handling function (if there is one)

Widget::set_new_handler(0); // set the Widget-specific new-handling function to nothing (i.e., null)
Widget *pw2 = new Widget; // if mem. alloc. fails, throw an exception immediately. (There is no new- handling function for class Widget.)
```

### Item 50: Understand when it makes sense to replace new and delete

`operator new`와 `operator delete`를 변경하려는 이유는 다음과 같을 수 있다.

- 잘못된 힙 사용을 탐지하기 위해
- 할당 및 해제 속력을 높이기 위해
- 기본 메모리 관리자의 공간 오버헤드를 줄이기 위해
- 적당히 타협한 기본 할당자의 바이트 정렬 동작을 보장하기 위해
- 임의의 관계를 맺고 있는 객체들을 한 군데 나란히 모아놓기 위해
- 그때그때 원하는 동작을 수행하도록 하기 위해

### Item 51: Adhere to convention when writing new and delete

관례에 맞는 `operator new`를 구현하려면 다음 요구사항을 지켜야 한다.

- 반환 값이 제대로 되어 있어야 한다.
- 가용 메모리가 부족할 경우 new handler 함수를 호출해야 한다.
- 크기가 없는(0 byte) 메모리 요청에 대한 대비책을 갖춰야 한다.
- 실수로 기본 형태의 `new`가 가려지지 않도록 한다.

```cpp
void* operator new(std::size_t size) throw(std::bad_alloc) { // your operator new might take additional params
using namespace std;
	if (size == 0) { // handle 0-byte requests by treating them as 1-byte requests
		size = 1;
	}
	while (true) {
		// attempt to allocate size bytes;
		if (the allocation was successful) 
			return (a pointer to the memory);

		// allocation was unsuccessful; find out what the
		// current new-handling function is (see below) 
		new_handler globalHandler = set_new_handler(0); 
		set_new_handler(globalHandler);

		if (globalHandler) (*globalHandler)();
		else throw std::bad_alloc(); 
	}
}
```

`operator delete`를 작성할 때의 관례로는 널 포인터에 대한 `delete` 적용이 항상 안전하도록 보장한다는 사실만 기억하자.

```cpp
void operator delete(void *rawMemory) throw() {
	if (rawMemory == 0) return; // do nothing if the null pointer is being deleted
	deallocate the memory pointed to by rawMemory; 
}
```

### Item 52: Write placement delete if you write placement new

C++ 런타임 시스템은 호출된 `operator new` 함수와 짝이 되는 `operator delete` 함수를 호출하는 것인데, 이것이 제대로 되려면 `operator delete` 함수들 가운데 어떤 것을 호출해야 하는지 런타임 시스템이 제대로 알고 있어야 한다.

메모리 할당 정보로 로그를 기록할 `ostream`을 지정받는다고 가정하자. 그리고 클래스 전용 `operator delete`는 기본형이라고 하자.

```cpp
class Widget { 
public:
	...
	static void* operator new(std::size_t size, std::ostream& logStream) 
		throw(std::bad_alloc);
	static void operator delete(void *pMemory) throw();
	static void operator delete(void *pMemory, std::ostream& logStream) 
		throw();
	...
};
```

사용자 정의 `operator new` 함수는 매개변수를 추가로 받는 형태로도 선언할 수 있다. 이런 형태의 함수를 가리켜 **위치지정(placement)** `new`라 한다.

만약 메모리 할당은 성공했지만, `Widget` 생성자에서 예외가 발생한 경우 C++ 런타임 시스템이 책임지고 되돌려야 한다. 그런데 런타임 시스템 쪽에서 호출된 `operator new`가 어떻게 동작하는지 알아낼 수 없으므로, 자신이 할당 자체를 되돌릴 수 없다. 대신 런타임 시스템은 호출된 `operator new`가 받아들이는 매개변수의 개수 및 타입이 똑같은 버전의 `operator delete`를 찾았다면 이를 호출한다.

```cpp
void operator delete(void*, std::ostream&) throw();
```

이런 형태의 `operator delete`를 가리켜 **위치지정 삭제(placement delete)** 라 한다.

> 단, 바깥쪽 유효범위에 있는 어떤 함수의 이름과 클래스 멤버 함수 이름이 같으면 바깥쪽 유효범위 함수가 *이름만 같아도* 가려진다. 따라서 자신이 사용할 수 있다고 생각하는 다른 `new`들을 클래스 전용의 `new`에 가려지지 않도록 신경써야 한다. 