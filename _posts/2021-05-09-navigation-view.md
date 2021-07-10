---
title: Navigation View
author: Beomsu Lee
math: true
mermaid: true
tags: [android]
---

## Description

하나의 화면에 많은 구성 요소를 넣으면 성능이나 사용성 면에서 좋지 않다. 기능을 최대한 분리하여 화면에 보이는 뷰의 개수를 줄여주는 것이 좋다. 버튼 메뉴가 있고 이 중 하나의 버튼을 눌러 서브 화면을 전환하는 방식처럼 하나의 뷰에서 여러 개의 정보를 볼 때 탭(Tab)을 사용한다. 탭은 네비게이션(Navigation) 위젯이라고 불리기도 하며 상단 탭과 하단 탭으로 구분할 수 있다. 하단 탭은 별도의 위젯으로 제공된다.

## Implementation

`BottomNavigationView` 위젯을 사용해 하단 탭을 구현해보자. 우선 `/app/res` 디렉토리에 `menu` 디렉토리를 만든 후 그 안에 `menu_bottom.xml` 파일을 만든 후 3개의 아이템을 생성한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <item
        android:id="@+id/tab1"
        app:showAsAction="ifRoom"
        android:enabled="true"
        android:icon="@android:drawable/ic_dialog_email"
        android:title="Email"/>

    <item
        android:id="@+id/tab2"
        app:showAsAction="ifRoom"
        android:icon="@android:drawable/ic_dialog_info"
        android:title="Info"/>

    <item android:id="@+id/tab3"
        app:showAsAction="ifRoom"
        android:enabled="true"
        android:icon="@android:drawable/ic_dialog_map"
        android:title="Loc"/>
</menu>
```

다음은 `activity_main.xml` 파일에서 `BottomNavigationView`을 정의해 화면의 하단에 표시되도록 한다. 그리고 화면 전체는 `FrameLayout`이 차지하도록 만든다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <FrameLayout
        android:id="@+id/container"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="@string/appbar_scrolling_view_behavior"/>

    <com.google.android.material.bottomnavigation.BottomNavigationView
        android:id="@+id/bottom_navigation"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginEnd="0dp"
        android:layout_marginStart="0dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:menu="@menu/menu_bottom"/>

</androidx.constraintlayout.widget.ConstraintLayout>
```

화면 전환 시 필요한 프래그먼트를 생성한다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="First" />
</LinearLayout>
```

`xml`에 대응하는 `java` 코드를 작성한다.

```java
public class Fragment1 extends Fragment {
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment1,container,false);
    }
}
```

그 다음 `MainActivity`에서 각 탭이 눌렸을 때 토스트를 출력하며 `FragmentManager`를 통해 프래그먼트를 변경하는 작업을 수행한다.

```java
public class MainActivity extends AppCompatActivity {

    Fragment1 fragment1;
    Fragment2 fragment2;
    Fragment3 fragment3;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        fragment1 = new Fragment1();
        fragment2 = new Fragment2();
        fragment3 = new Fragment3();

        getSupportFragmentManager().beginTransaction().replace(R.id.container,fragment1).commit();

        BottomNavigationView bottomNavigationView = findViewById(R.id.bottom_navigation);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(@NonNull @org.jetbrains.annotations.NotNull MenuItem item) {
                switch(item.getItemId()){
                    case R.id.tab1:
                        Toast.makeText(MainActivity.this, "First Selected", Toast.LENGTH_SHORT).show();
                        getSupportFragmentManager().beginTransaction().replace(R.id.container,fragment1).commit();
                        return true;
                    case R.id.tab2:
                        Toast.makeText(MainActivity.this, "Second Selected", Toast.LENGTH_SHORT).show();
                        getSupportFragmentManager().beginTransaction().replace(R.id.container,fragment2).commit();
                        return true;
                    case R.id.tab3:
                        Toast.makeText(MainActivity.this, "Third Selected", Toast.LENGTH_SHORT).show();
                        getSupportFragmentManager().beginTransaction().replace(R.id.container,fragment3).commit();
                        return true;
                }
                return false;
            }
        });
    }
}
```

## Conclusion

하단의 각 메뉴를 선택하면 선택된 프래그먼트가 보여지는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)