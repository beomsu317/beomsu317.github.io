---
title: Android Dagger
author: Beomsu Lee
category: [Android, Dagger]
tags: [android, dagger]
math: true
mermaid: true
---

## Component Module을 이용한 구현

Activity, Fragment에서 의존성 주입을 위한 코드를 필수로 작성해야 한다. 다음과 같은 방법으로 구현할 수 있지만, 보일러 플레이트 코드가 증가하기 때문에 거의 사용하지 않는다. 

```kotlin
public class MainActivity : AppCompatActivity {

  @Inject
  lateinit var coffee : Coffee

  override fun onCreate(savedInstanceState : Bundle?) {
    super.onCreate(savedInstanceState)

    // 반드시 선행되어야 할 작업, 그렇지 않으면 coffee 필드는 null
    var mainComponent: MainComponent = (application as MyApplication).appComponent
         .mainComponent()
         .create()

    // Member-Injection 
    mainComponent.inject(this@MainActivity)

    // Provision 
    var coffee2: Coffee = mainComponent.coffee()
  }
}
```

## HasAndroidInjector를 이용한 구현

안드로이드 Dagger는 위와 같은 방법을 단순화해주는 방법을 제공한다. Dagger를 사용하기 위해 추가적인 설정이 필요하다.

```kotlin
@Singleton
@Component(modules = [
    AndroidInjectionModule::class,	// AndroidInjectionModule 추가
    ActivityBindingModule::class,   // ActivityBindingModule 추가
    CoffeeModule::class     // Coffee 의존성 인스턴스 생성을 위한 Module
])
interface AppComponent {
    // Application을 구현한 BaseApplication 클래스
    fun inject(myApp : MyApp)	
}
```

`MainActivity`에서 사용할 SubComponent인 `MainComponent`를 `AndroidInjector<MainActivity>`로 상속해 구현했다. 

```kotlin
// AndroidInjector<Activity 또는 Fragment> 상속
@Subcomponent(modules=[...])
interface MainComponent : AndroidInjector<MainActivity> {
    // AndroidInjector.Factory<Activity 또는 Fragment> 상속 
    @Subcomponent.Factory
    interface Factory : AndroidInjector.Factory<MainActivity> {}
}
```

이제 AppComponent와 부모-자식 관계를 설정하기 위해 `ActivityBindingModule`에 MultiBinding을 설정한다. `ActivityBindingModule`에 `subcomponent` 속성으로 `MainComponent`, `DetailComponent`를 설정하여 AppComponent의 SubComponent로 관계를 설정하였다. 

`MainComponent.Factory`와 `DetailComponent.Factory` 인스턴스를 요청하게 되면 `@Binds`로 설정하였기 때문에 `AndroidInjector.Facotry<*>`로 캐스팅되어 인스턴스를 주입한다.

```kotlin
@Module(subcomponents=[
    MainComponent::class,       // MainActivity Component
    DetailComponent::Class      // DetailActivity Component
])
abstract class ActivityBindingModule {	// @Binds 메서드 사용하기 때문에 abstract

    @Binds
    @IntoMap                        // MultiBinding을 위한 annotation
    @ClassKey(MainActivity::class)  // MultiBinding Map의 Key Type
    abstract fun bindMainInjectorFactory(factory: MainComponent.Factory) : AndroidInjector.Factory<*>

    @Binds
    @IntoMap
    @ClassKey(DetailActivity::class)
    abstract fun bindDetailInjectorFactory(factory: DetailComponent.Factory) : AndroidInjector.Factory<*>
}
```
 
`@Binds`와 `@IntoMap`으로 MultiBinding을 구현하였고 Factory를 반환하는 두 메서드의 반환 타입은 다음과 같다.

```kotlin
Map<Class<*>, AndroidInjector.Factory<*>>
```

만약 SubComponent와 SubComponent.Factory 메서드가 없고, 상속이 없을 경우 `@ContributeAndroidInjector`를 사용한다.  

`MainComponent`를 보면 Component와 Factory 내부 메서드가 따로 없다. 이럴 경우 interface를 선언하지 않고, Module 내부에 `@ContributesAndroidInjector` 어노테이션을 사용한 추상 메서드로 대체할 수 있다.

ActivityBinding을 하는 모듈에 SubComponent들의 선언을 `@ContributesAndroidInjector`로 대체한다. `MainComponent`, `DetailComponent`의 interface 선언은 필요 없으므로 지운다. 자식 Component가 없으므로 `@Module` 어노테이션에 subcomponent 설정을 지운다. 

```kotlin
@Module
abstract class ActivityBindingModule {

    @ActivityScope				// Scope 설정
    @ContributesAndroidInjector(modules=[...]) // modules 연결
    abstract fun mainActivity() : MainActivity

    @ActivityScope				// Scope 설정
    @ContributesAndroidInjector(modules=[...]) // modules 연결
    abstract fun detailActivity() : DetailActivity
}
```
`Application` 단위 클래스에서 `HasAndroidInjector`를 상속하고 `DispatchingAndroidInjector`를 반환하는 `androidInjector()` 메서드를 구현한다.

```kotlin
// HasAndroidInjector 인터페이스 상속
class MyApp : Application(), HasAndroidInjector {

	// AppComponent에게 DispatchingAndroidInjector 의존성 요청
    @Inject
    lateinit var dispatchingAndroidInjector: DispatchingAndroidInjector<Any>

    override fun onCreate() {
        super.onCreate()
        // AppComponent의 Member-Injection 메서드 inject()
        DaggerAppComponent.create().inject(this@MyApp)
    }

    /** Returns an [AndroidInjector].  */
    // HasAndroidInjector 인터페이스 메서드 구현 (재정의)
    override fun androidInjector(): AndroidInjector<Any>? {
        return dispatchingAndroidInjector
    }
}
```

각 Activity, Fragment에서 `AndroidInjection.inject()`로 의존성을 주입한다.

```kotlin
class MainActivity : AppCompatActivity() {

    // 의존성 요청할 MultiBinding 타입 정의
    @Inject
    lateinit var coffee: Map<Class<*>, @JvmSuppressWildcards Coffee>

    override fun onCreate(savedInstanceState: Bundle?) {
        // AndroidInjection.inject() 메서드 한번으로 Dagger 의존성 주입 (super.onCreate() 전에 사용 권장)
        AndroidInjection.inject(this@MainActivity)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        println(coffee[Espresso::class.java]?.name())
    }
}
```

일반적인 Dagger 사용방법처럼 긴 메서드 체이닝 방식을 사용하지 않고 `AndroidInjection.inject(this@MainActivity)` 메서드로 의존성 주입을 자동으로 완료할 수 있다.

## DaggerApplication 등의 기반 클래스를 이용한 구현

안드로이드 기반 클래스(`DaggerApplication`, `DaggerActivity`, `DaggerFragment` 등)를 사용해서 Dagger 의존성 주입을 하는 방법이다.

`AppComponent`에 모듈인 `AndroidSupportInjectionModule` 설정과, `AndroidInjector` 인터페이스를 상속한다.

```kotlin
@Component(modules = [
        AndroidSupportInjectionModule::class,   // AndroidSupportInjectionModule 설정
        ActivityBindingModule::class,
        CoffeeModule::class
])
// AndroidInjector 상속
interface AppComponent : AndroidInjector<MyApp> {	
    // inject() 제거
}	
```

기존 `Application` 상속을 `DaggerApplication`를 상속으로 변경하고, `applicationInjector()`를 재정의한다. `applicationInjector()`의 반환 타입은 `AndroidInjector<out DaggerApplication>`이다. 하지만 반환 값을 보면 `AppComponent`의 인스턴스를 반환하고 있다. 이는 `AppComponent` 인터페이스에서 `AndroidInjector<MyApp>`을 상속하기 때문에 `out DaggerApplication(MyApp extends DaggerApplication)`이 성립하게 된다. 따라서 `AppComponent` 인스턴스는 `AndroidInjector<out DaggerApplication>`으로 추상화가 성립된다. 

이 방법은 `DaggerApplication`으로 복잡한 부분들을 위임했기 때문에 따로 구현하지 않아도 되므로 더 간편하다.

```kotlin
class MyApp : DaggerApplication() {

    override fun onCreate() {
        super.onCreate()
    }

    // DaggerApplication의 메서드 구현(재정의) - AppComponent는 AndroidInjector를 상속했기에 반환Type에 캐스팅
    override fun applicationInjector(): AndroidInjector<out DaggerApplication> {
        return DaggerAppComponent.create()	// AppComponent 인스턴스 반환
    }
}
```

다음은 `DaggerApplication`의 구조이다. 

```kotlin
// DaggerApplication 클래스를 상속하고, HasAndroidInjector를 구현한다.
@Beta
public abstract class DaggerApplication extends Application implements HasAndroidInjector {	
  // DispatchingAndroidInjector 의존성 요청 
  @Inject volatile DispatchingAndroidInjector<Object> androidInjector;	

  @Override
  public void onCreate() {
    // onCreate() 호출
    super.onCreate();		
    injectIfNecessary();
  }

  // 사용자가 재정의할 applicationInjector의 추상 메서드 
  @ForOverride
  protected abstract AndroidInjector<? extends DaggerApplication> applicationInjector(); 

  private void injectIfNecessary() {
   ... // 생략
  }

  // HasAndroidInjector 인터페이스의 androidInjector() 추상메서드 구현
  @Override
  public AndroidInjector<Object> androidInjector() {	
    injectIfNecessary();

    return androidInjector;
  }
}
```

`AppCompatActivity` 상속을 `DaggerActivity` 클래스 상속으로 변경한다. `DaggerActivity` 상속함으로써 기존에 구현하던 의존성 주입 과정을 위임한다.

```kotlin
class MainActivity : DaggerActivity() {	// DaggerActivity() 상속

    // coffee 변수 의존성 요청
    @Inject
    lateinit var coffee: Map<Class<*>, @JvmSuppressWildcards Coffee>

    override fun onCreate(savedInstanceState: Bundle?) {

        // AndroidInjection.inject(this@MainActivity)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

`DaggerActivity`의 구조는 다음과 같다.

```kotlin
/**
 * An {@link Activity} that injects its members in {@link #onCreate(Bundle)} and can be used to
 * inject {@link Fragment}s attached to it.
 */
// Activity 클래스 상속, HasAndroidInjector 구현
@Beta
public abstract class DaggerActivity extends Activity implements HasAndroidInjector {	

  @Inject DispatchingAndroidInjector<Object> androidInjector;

  @Override
  protected void onCreate(@Nullable Bundle savedInstanceState) {
    // MainActivity에서 의존성 주입을 위한 AndroidInjection.inject() 메서드를 대신 수행
    AndroidInjection.inject(this);		
    super.onCreate(savedInstanceState);
  }

  @Override
  public AndroidInjector<Object> androidInjector() {
    return androidInjector;
  }
}
```

## References
- [Android Dagger 사용방법 3가지](https://jaejong.tistory.com/152?category=888864)
- [Dagger_Sample_DI](https://github.com/posth2071/Dagger_Sample_DI)

