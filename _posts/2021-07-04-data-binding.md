---
title: Data Binding
author: Beomsu Lee
category: [Android]
tags: [android, data binding]
math: true
mermaid: true
---

## Data Binding

Data Binding이란 provider와 cosumer로부터 데이터 소스를 묶어 동기화하는 기법이다. 보통 안드로이드에선 XML 파일에 Data를 바인딩해서 사용할 수 있게 해주며, Android JetPack 라이브러리의 기능이다. 즉, 데이터바인딩은 앱 로직과 레이아웃을 바인딩하는데 필요한 코드를 최소화 시켜준다. 

Data Binding을 이용해 LiveData를 바인딩하면 LiveData의 값이 변경될 때 View의 Data가 자동으로 변경되기 때문에 코드를 줄일 수 있는 장점이 있다.

DataBinding을 적용하려면 안드로이드 프로젝트에서 DataBinding을 활성화시켜야 한다. `build.gradle`의 android 모듈에 DataBinding을 사용하겠다는 선언을 해준다.

```xml
android {
    ...
    dataBinding {
        enabled = true
    }
}
```

## Basic Example

`User` 클래스에 대한 정보를 화면에 표시해보자. 원래라면 `setText()` 메서드를 통해 `TextView`에 내용을 표시했었다. 이러한 방식으로 표현하는 대신, DataBinding은 자동적으로 값들을 바인딩해준다. 

다음은 `name`과 `email`을 가진 `User` 클래스이다.

```java
public class User {
    String name;
    String email;
 
    public String getName() {
        return name;
    }
 
    public void setName(String name) {
        this.name = name;
    }
 
    public String getEmail() {
        return email;
    }
 
    public void setEmail(String email) {
        this.email = email;
    }
}
```

DataBinding을 사용하려면, root element는 `<layout>` 태그로 시작해야 한다. 이 태그와 함께 `<data>`와 `<variable>` 태그가 사용되어져야 한다. 다음은 DataBinding의 레이아웃 구조이다.

```xml
<layout ...> 
    <data>
         
        <variable
            name="..."
            type="..." />
    </data>
 
    <LinearLayout ...>
       <!-- YOUR LAYOUT HERE -->
    </LinearLayout>
</layout>
```

모든 바인딩 될 값들과 메서드는 `<data>` 태그에 있어야 한다. 변수들은 `<data>` 태그 안의 `<variable>` 태그로 선언된다. `<variable>` 태그는 `name`과 `type` 2개의 속성이 있다. `name` 속성은 alias이며, `type` 속성은 객체의 모델 클래스여야 한다. 

값들을 바인딩하려면, `@` 어노테이션을 사용해야 한다. 다음은 `name`과 `email`을 `@{user.name}`과 `@{user.email}`을 통해 바인딩하였다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android">
    <data>
        <variable
            name="user"
            type="com.example.sample.databinding.data.User" />
    </data>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@{user.name, default=defaults}"/>

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@{user.email, default=defaults}"/>
    </LinearLayout>
</layout>
```

DataBinding이 레이아웃 파일에 통합되었으면 **Build -> Clean Project** 후 **Build -> Rebuild Project** 해준다. 바인딩 클래스를 생성하기 위함이다. 

바인딩 클래스는 바인딩이 적용된 레이아웃 파일 이름을 고려한 명명 규칙을 따른다. `activity_main.xml`의 경우 생성되는 클래스 이름은 `ActivityMainBinding`이다.

UI에 데이터를 바인딩하기 위해 바인딩 클래스를 이용해 바인딩 레이아웃을 inflate 해줘야 한다. 다음은 `ActivityMainBinding`이 레이아웃을 inflate하며, `binding.setUser()`를 통해 `User` 객체를 레이아웃에 바인딩한다.

`findViewById()`를 사용하지 않고도 DataBinding을 통해 값들을 변경할 수 있다. 

```java
public class MainActivity extends AppCompatActivity {

    User user;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        ActivityMainBinding binding;

        binding = DataBindingUtil.setContentView(this, R.layout.activity_main);

        user = new User();
        user.setName("gildong Hong");
        user.setEmail("hong123@gmail.com");

        binding.setUser(user);

    }
}
```

앱을 실행하면 이름과 이메일이 화면에 표시되는 것을 확인할 수 있다.

## DataBinding in <include> layouts

일반적으로 메인 레이아웃과 콘텐츠 레이아웃 2개로 구분하여 사용한다. `content_main.xml`은 메인 레이아웃에 `<include>` 태그를 통해 포함되게 된다. 이 `<include>`가 포함된 레이아웃에서 어떻게 DataBinding을 사용하는지 알아볼 것이다.

다음은 `CoordinatorLayout`, `AppBarLayout`, `FloatingActionButton`가 포함된 `activity_main.xml`이다.

DataBinding을 사용하기 위해 `activity_main.xml`에서 `<layout>` 태그를 설정한다. `<data>`, `<variable>` 태그도 `User` 객체를 바인딩하기 위해 사용한다.

`user`을 `content_main` 레이아웃으로 전달하기 위해 `bind:user="@{user}"` 구문이 사용된다. 이 구문을 사용함으로써 `content_main` 레이아웃에서 객체에 접근할 수 있게 된다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    xmlns:bind="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <data>
        <variable
            name="user"
            type="com.example.sample.databinding.data.User" />
    </data>

    <androidx.coordinatorlayout.widget.CoordinatorLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        tools:context=".MainActivity">

        <com.google.android.material.appbar.AppBarLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content">

            <androidx.appcompat.widget.Toolbar
                android:id="@+id/toolbar"
                android:layout_width="match_parent"
                android:layout_height="60dp"/>

        </com.google.android.material.appbar.AppBarLayout>

        <include
            android:id="@+id/content"
            layout="@layout/content_main"
            bind:user="@{user}"/>

        <com.google.android.material.floatingactionbutton.FloatingActionButton
            android:id="@+id/fab"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="bottom|end" />

    </androidx.coordinatorlayout.widget.CoordinatorLayout>

</layout>
```

`content_main.xml`도 `<layout>` 태그를 이용해 DataBinding을 사용할 수 있도록 만들어준다. `<layout>`, `<data>`, `<variable>` 태그는 부모와 포함할 레이아웃에 필수적으로 있어야 한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <data>
        <variable
            name="user"
            type="com.example.sample.databinding.data.User" />
    </data>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            app:layout_behavior="@string/appbar_scrolling_view_behavior"
            tools:context=".MainActivity"
            tools:showIn="@layout/activity_main">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="@{user.name, default=defaults}"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="@{user.email, default=defaults}"/>
        </LinearLayout>
    
</layout>
```

앱을 실행하면 포함된 레이아웃의 데이터가 표시되는 것을 확인할 수 있다.

## Binding Click Listeners / Events Handling

데이터 뿐만 아니라 클릭같은 다양한 이벤트들을 바인딩 할 수 있다. 클릭을 바인딩하기 위해 콜백 메서드가 포함된 클래스를 필수로 생성해야 한다. 다음은 FAB를 클릭했을 경우 Toast를 출력하는 코드이다.

```java
public class MyClickHandlers {
        public void onFabClicked(View view) {
            Toast.makeText(getApplicationContext(), "FAB clicked!", Toast.LENGTH_SHORT).show();
        }
}
```

이 이벤트를 바인딩하기 위해, `<variable>` 태그를 사용해 핸들러 클래스를 지정해준다. `android:onClick="@{handlers::onFabClicked}"` 구문은 `onFabClicked()` 메서드를 바인딩해준다. 

바인딩 시 파라미터도 전달할 수 있다. `public void onButtonClickWithParam(View view, User user)`는 UI 레이아웃으로부터 `user` 객체를 받으며 파라미터는 `android:onClick="@{(v) -> handlers.onButtonClickWithParam(v, user)}"`을 통해 전달할 수 있다.

```xml
<layout xmlns:bind="http://schemas.android.com/apk/res/android">
 
    <data>
 
        <variable
            name="handlers"
            type="info.androidhive.databinding.MainActivity.MyClickHandlers" />
    </data>
 
    <android.support.design.widget.CoordinatorLayout ...>
 
        <android.support.design.widget.FloatingActionButton
            ...
            android:onClick="@{handlers::onFabClicked}" />
 
    </android.support.design.widget.CoordinatorLayout>
</layout>
```

이벤트를 바인딩하기 위해, Activity에서 `binding.setHandlers(handlers)`를 호출해야 한다. 다음은 `MainActivity`에서 바인딩을 구현한 코드이다. 

```java
public class MainActivity extends AppCompatActivity {

    User user;
    MyClickHandlers handlers;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        ActivityMainBinding binding = DataBindingUtil.setContentView(this, R.layout.activity_main);

        setSupportActionBar(binding.toolbar);

        user = new User();
        user.setName("gildong Hong");
        user.setEmail("hong123@gmail.com");

        binding.setUser(user);

        handlers = new MyClickHandlers(this);
        binding.setHandlers(handlers);
    }

    public class MyClickHandlers {
        Context context;

        public MyClickHandlers(Context context){
            this.context = context;
        }

        public void onFabClicked(View view){
            Toast.makeText(getApplicationContext(), "FAB Clicked!", Toast.LENGTH_SHORT).show();
        }

        public void onButtonClick(View view){
            Toast.makeText(getApplicationContext(), "Button Clicked!", Toast.LENGTH_SHORT).show();
        }

        public void onButtonClickWithParam(View view, User user){
            Toast.makeText(getApplicationContext(), "Button Clicked Name: " +user.getName()+", email: "+user.getEmail(), Toast.LENGTH_SHORT).show();
        }

        public boolean onButtonLongPressed(View view){
            Toast.makeText(getApplicationContext(), "Button Long Pressed!", Toast.LENGTH_SHORT).show();
            return false;
        }

    }
}
```

다음은 `activity_main.xml`이며 `content_main.xml`에게 `user`와 `handler`를 넘겨주고 FAB 버튼을 클릭 이벤트를 바인딩해준다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    xmlns:bind="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <data>
        <variable
            name="user"
            type="com.example.sample.databinding.data.User" />
        <variable
            name="handlers"
            type="com.example.sample.databinding.MainActivity.MyClickHandlers" />
    </data>

    <androidx.coordinatorlayout.widget.CoordinatorLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        tools:context=".MainActivity">

        <com.google.android.material.appbar.AppBarLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content">

            <androidx.appcompat.widget.Toolbar
                android:id="@+id/toolbar"
                android:layout_width="match_parent"
                android:layout_height="60dp"/>

        </com.google.android.material.appbar.AppBarLayout>

        <include
            android:id="@+id/content"
            layout="@layout/content_main"
            bind:user="@{user}"
            bind:handlers="@{handlers}"/>

        <com.google.android.material.floatingactionbutton.FloatingActionButton
            android:id="@+id/fab"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="bottom|end"
            android:onClick="@{handlers::onFabClicked}"/>

    </androidx.coordinatorlayout.widget.CoordinatorLayout>
</layout>
```

`content_main.xml`에서 `handlers`를 통해 이벤트들을 바인딩 해준다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <data>
        <variable
            name="user"
            type="com.example.sample.databinding.data.User" />
        <variable
            name="handlers"
            type="com.example.sample.databinding.MainActivity.MyClickHandlers" />
    </data>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            app:layout_behavior="@string/appbar_scrolling_view_behavior"
            tools:context=".MainActivity"
            tools:showIn="@layout/activity_main">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="@{user.name, default=defaults}"/>

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="@{user.email, default=defaults}"/>

            <Button
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:onClick="@{handlers::onButtonClick}"
                android:text="CLICK"/>
            <Button
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:onClick="@{(v) -> handlers.onButtonClickWithParam(v, user)}"
                android:text="CLICK WITH PARAM"/>
            <Button
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:onLongClick="@{handlers::onButtonLongPressed}"
                android:text="LONG PRESS"/>
        </LinearLayout>
    
</layout>
```

앱을 실행해보면 각 버튼에 대한 이벤트가 발생하는 것을 확인할 수 있다.


## Updating UI using Observables

Observable은 명시적인 setter 메서드 없이 자동적으로 UI와 동기화할 수 있다. 객체의 속성 값이 변경되면 UI가 업데이트 되는 방식이다. 객체를 Observable로 만들기 위해, `BaseObservable`를 상속해야 한다.

속성을 Observable로 만들려면, `@Bindable` 어노테이션을 사용해야 한다. settter 메서드에서 `notifyPropertyChanged(BR.property)`를 호출해 UI를 업데이트 한다. `BR` 클래스는 DataBinding이 활성화되면 자동으로 생성된다.

다음은 `BaseObservable`을 상속한 `User` 클래스이다. 여기서 값이 변경되면 `notifyPropertyChanged()`를 호출해 UI에게 알릴 수 있다.

```java
public class User extends BaseObservable {
    String name;
    String email;

    @Bindable
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
        notifyPropertyChanged(BR.name);
    }

    @Bindable
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
        notifyPropertyChanged(BR.email);
    }
}
```

내용을 확인하기 위해 FAB 클릭 이벤트를 변경하였다. 

```java
    public class MyClickHandlers {
        Context context;

        public MyClickHandlers(Context context){
            this.context = context;
        }

        public void onFabClicked(View view){
            user.setName("Beomsu Lee");
            user.setEmail("beomsu317@gmail.com");
        }
        ...
    }
```

FAB를 클릭하면 이름과 이메일이 변경되는 것을 확인할 수 있다.

## Updating UI using ObservableFields

`ObservableFields`는 단일 속성을 가진 Observable 객체이다. 변수를 `ObservableField`로 선언하고, 새로운 데이터를 설정하면 UI가 업데이트 된다.

다음은 `ObservableFields`를 적용한 `User` 클래스이다.

```java
public class User extends BaseObservable {
    public static ObservableField<String> name = new ObservableField<>();
    public static ObservableField<String> email = new ObservableField<>();

    public ObservableField<String> getName(){
        return name;
    }
    public ObservableField<String> getEmail(){
        return email;
    }
}
```

이 값들을 업데이트 하기 위해, setter 대신 직접적으로 값들을 할당해야 한다. 이번에도 FAB를 클릭하면 값들이 변경되도록 하였다. 

```java
public class MyClickHandlers {
    Context context;
    public MyClickHandlers(Context context){
        this.context = context;
    }
    public void onFabClicked(View view){
        user.name.set("Beomsu Lee");
        user.email.set("beomsu317@gmail.com");
    }
    ... 
}
```

FAB 버튼을 클릭하면 `user`의 값들이 변경되는 것을 확인할 수 있다.


## Loading Images From URL

이미지를 로드하기 위해 `ImageView`를 URL에 바인딩할 수도 있다. URL을 `ImageView`에 바인딩하려면 객체 속성에 `@BindingAdapter` 어노테이션을 사용한다.

우선 Glide를 사용하기 위해 build.gradle에 라이브러리 의존성을 설정한다.

```
dependencies {
    ...
    implementation 'com.github.bumptech.glide:glide:4.12.0'
    annotationProcessor 'com.github.bumptech.glide:compiler:4.12.0'
}
```

다음은 `profileImage` 변수가 `android:profileImage` 속성에 바인딩 된 것이다. 이미지는 `Glide` 또는 `Picasso` 이미지 라이브러리를 통해 로딩된다. 

```java
public class User {
    String profileImage;

    public String getProfileImage(){
        return profileImage;
    }

    public void setProfileImage(String profileImage){
        this.profileImage = profileImage;
    }

    @BindingAdapter({"android:profileImage"})
    public static void loadImage(ImageView view, String imageUrl){
        Glide.with(view.getContext())
                .load(imageUrl)
                .into(view);
    }
}
```

이미지가 `ImageView`로 로딩하기 위해, `android:profileImage="@{user.profileImage}"` 속성을 설정한다. 

```xml
<ImageView
     android:layout_width="100dp"
     android:layout_height="100dp"
     android:layout_marginTop="@dimen/fab_margin"
     android:profileImage="@{user.profileImage}" />
```

## Binding Java Functions 

자바 함수들을 UI 요소에 바인딩할 수도 있다. UI에 표시하기 전에 값에 대한 작업을 수행하려면 `<import>` 태그를 사용하여 쉽게 해당 작업을 수행할 수 있다.

다음은 문자열을 대문자로 변경해주는 메서드가 포함된 클래스이다.

```java
public class BindingUtils {
    public static String capitalize(String text) {
        return text.toUpperCase();
    }
}
```

레이아웃에서 해당 메서드를 호출하려면, `<import>` 태그를 이용하여 클래스를 가져오고 속성에 대한 함수를 호출한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android">
 
    <data>
        <import type="info.androidhive.databinding.BindingUtils" />
    </data>
 
    <LinearLayout ...>
 
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@{BindingUtils.capitalize(user.name)}" />
 
    </LinearLayout>
</layout>
```

### References
- [wikipedia - Data_binding](https://en.wikipedia.org/wiki/Data_binding)
- [developer.android.com - data-binding](https://developer.android.com/topic/libraries/data-binding)
- [android-working-with-databinding](https://www.androidhive.info/android-working-with-databinding/)

