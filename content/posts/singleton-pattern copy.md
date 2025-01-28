---
title: "Singleton Pattern"
date: "2025-01-28"
author: "Beomsu Lee"
tags: ["c++", "design pattern", "creational pattern"]
---

오직 한 개의 클래스 인스턴스만 갖도록 보장하고, 이에 대한 전역적인 액세스 포인트를 제공한다.

## Applicability

- 클래스의 인스턴스가 오직 하나여야 함을 보장하고, 잘 정의된 액세스 포인트로 모든 사용자가 접근할 수 있도록 해야 할 때
- 유일한 인스턴스가 서브클래싱으로 확장되어야 하며, 사용자는 코드 수정 없이 확장된 서브클래스의 인스턴스를 사용할 수 있어야 할 때

## Structure

![singleton pattern structure](images/singleton_pattern_structure.png)

- `Singleton`: `Instance()` 연산을 정의하여 유일한 인스턴스로 접근할 수 있도록 함

## Collaborations

- 사용자는 `Singleton` 클래스에 정의된 `Instance()` 연산을 통해 유일하게 생성되는 싱글톤 인스턴스에 접근할 수 있다.

## Consequences

1. **유일하게 존재하는 인스턴스로의 접근을 통제한다.**

    `Singleton` 클래스 자체가 인스턴스를 캡슐화하기 때문에, 이 클래스에서 사용자가 언제, 어떻게 이 인스턴스에 접근할 수 있는지 제어할 수 있다.
2. **이름 공간(name space)를 좁힌다.** 

    싱글톤 패턴은 전역 변수를 사용해 이름 공간을 망치는 일을 없애준다.
3. **연산 및 표현의 정제를 허용한다.**

    싱글톤 클래스는 상속될 수 있기에, 이 상속된 서브클래스를 통해 새로운 인스턴스를 만들 수 있다. 
4. **인스턴스의 개수를 변경하기 자유롭다.**

    싱글톤 클래스의 인스턴스가 하나 이상 존재할 수 있도록 변경해야 할 때도 있는데, 싱글톤 클래스의 인스턴스에 접근할 수 있는 허용 범위를 결정하는 연산만 변경하면 된다. 즉, 기존에는 하나의 인스턴스로만 접근을 허용했다면, 여러 개의 인스턴스를 생성해 각각 그 인스턴스로 접근할 수 있도록 연산의 구현을 바꿀 수 있다.
5. **클래스 연산을 사용하는 것보다 훨씬 유연한 방법이다.** 

    싱글톤 패턴과 동일한 기능을 발휘하는 방법이 클래스 연산(C++의 정적 멤버 함수 등)을 사용하는 것이다. 그러나 클래스 인스턴스가 하나 이상 존재할 수 있도록 설계를 변경하는 것은 어렵다. 또한 C++의 정적 멤버 함수는 가상 함수가 아니므로 서브클래스들이 이 연산을 오버라이드 할 수 없다.

## Implementation

1. **인스턴스가 유일해야 함을 보장한다.**

    일반적인 방법은 인스턴스를 생성하는 연산을 클래스 연산으로 만드는 것이다. 이 연산은 유일한 인스턴스를 관리할 변수에 접근해 이 변수에 유일한 인스턴스로 초기화하고, 이 변수를 되돌려주어 사용자가 유일한 인스턴스를 사용할 수 있도록 한다.

    ```cpp
    class Singleton {
    public:
        static Singleton* Instance();
    protected:
        Singleton();
    private:
        static Singleton* _instance;
    };
    ```

    구현은 다음과 같다.

    ```cpp
    Singleton* Singleton::_instance = 0;

    Singleton* Singleton::Instance () {
        if (_instance == 0) {
            _instance = new Singleton;
        }
        return _instance;
    }
    ```

    사용자는 반드시 `Instance()` 함수를 통해서만 인스턴스에 접근해야 한다. 또한 생성자가 `protected`로 선언되어 사용자가 임의로 `Singleton` 인스턴스를 생성하려하면 컴파일 오류가 발생한다.

2. **`Singleton` 클래스를 서브클래싱한다.**

    때로는 싱글톤 클래스의 기능을 확장하거나 다른 형태의 인스턴스가 필요할 수 있다. 이를 위해 싱글톤 클래스를 상속받아 서브클래스를 정의할 수 있다. 핵심은 `Singleton`의 인스턴스를 참조하는 변수가 서브클래스의 인스턴스로 초기화되어야 한다는 것이다. 쉬운 방법으로 슈퍼클래스의 인스턴스를 반환할지, 서브클래스의 인스턴스를 반환할지를 `Instance()`에서 판단하는 것이다.

    `Singleton`의 서브클래스를 선택하는 또 다른 방법은 `Instance()` 연산의 구현을 슈퍼클래스가 아닌 서브클래스에서 하는 것이다. 이는 싱글톤 구현 클래스를 연결 시점에 결정할 수 있게 해준다.

    싱글톤에 대한 레지스트리를 사용할 수 있다. `Singleton` 클래스는 이 싱글톤 인스턴스를 레지스트리에 이름을 갖는 인스턴스로 등록한다. 레지스트리는 문자열로 정의된 이름을 해당 싱글톤 인스턴스로 대응시켜 둔다. `Instance()` 연산에서 싱글톤이 필요할 때 레지스트리를 확인해 해당하는 싱글톤을 돌려준다. 이런 방식을 취하면 `Instance()` 연산이 모든 싱글톤 클래스와 인스턴스를 알 필요가 없다.

    ```cpp
    class Singleton {
    public:
        static void Register(const char* name, Singleton*);
        static Singleton* Instance();
    protected:
        static Singleton* Lookup(const char* name);
    private:
        static Singleton* _instance;
        static List<NameSingletonPair>* _registry;
    };
    ```

## Sample Code

`MazeFactory` 클래스는 미로의 각 요소를 생성하는 데 필요한 인터페이스를 정의한다. 서브클래스에서는 인터페이스를 재정의하여 특정 제품 클래스를 생성하여 반환한다.

`MazeFactory`를 싱글톤으로 만들면 `MazeFactory` 인스턴스에 대한 매개변수를 전역 변수로 정의할 필요 없이 어디서나 `MazeFactory` 객체로 접근할 수 있다.

```cpp
class MazeFactory {
public:
    static MazeFactory* Instance();
    
    // existing interface goes here
protected:
    MazeFactory();
private:
    static MazeFactory* _instance;
};
```

구현은 다음과 같다.

```cpp
MazeFactory* MazeFactory::_instance = 0;

MazeFactory* MazeFactory::Instance () {
    if (_instance == 0) {
        _instance = new MazeFactory;
    }
    return _instance;
}
```

환경 변수를 통해 미로의 종류를 선택하고 `MazeFactory` 서브클래스 환경 변수에 정의된 값으로 인스턴스화하는 코드를 추가한다. 

```cpp
MazeFactory* MazeFactory::Instance() {
    if (_instance == 0) {
        const char* mazeStyle - getenv("MAZESTYLE");
        
        if (strcmp(mazeStyle, "bombed") == 0) {
            _instance = new BombedMazeFactory;
        } else if (strcmp(mazeStyle, "enchanted") == 0) {
            _instance = new EnchantedMazeFactory;
            
            // ... other possible subclasses
            
        } else { // default
            _instance = new MazeFactory;
        }
    }
    return _instance;
}
```

`MazeFactory`는 새로운 서브클래스를 만들 때마다 `Instance()`가 변경되어야 한다. 만약 프레임워크에 정의된 추상 팩토리라면 프레임워크를 수정해야 한다. 이럴 때 레지스트리를 사용해 해결할 수 있다.