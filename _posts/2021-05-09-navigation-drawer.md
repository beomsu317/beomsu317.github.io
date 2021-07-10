---
title: Navigation Drawer
author: Beomsu Lee
category: [Android, Navigation]
tags: [android, navigation drawer]
math: true
mermaid: true
---

## Description

Navigation Drawer는 화면의 좌측에 상단에 있는 아이콘을 눌렀을 때 나타나는 화면이다. 로그인한 사용자의 프로필 정보나 설정 메뉴를 보여줄 때 사용하기도 한다.

## Implementation

우선 Navigation Drawer Activity 프로젝트를 선택하여 생성한다. 그 후 `activity_main.xml` 파일을 다음과 같이 수정한다. `FrameLayout`에 `app:layout_behavior="@string/appbar_scrolling_view_behavior` 속성을 부여해 `CoordinatorLayout` 내에서 해당 레이아웃이 스크롤 등 작업이 진행될 때 차지할 면적을 자동으로 계산해준다. `NavigationView`의 `headerLayout` 속성은 사용자 프로필 등을 보여주고, `menu` 속성은 그 아래 메뉴를 보여준다. `FrameLayout`에서 선택된 메뉴에 따라 프래그먼트를 변경할 것이므로 `id`를 `container`로 지정한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.drawerlayout.widget.DrawerLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/drawer_layout"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fitsSystemWindows="true"
    tools:openDrawer="start">

    <androidx.coordinatorlayout.widget.CoordinatorLayout xmlns:android="http://schemas.android.com/apk/res/android"
        xmlns:app="http://schemas.android.com/apk/res-auto"
        xmlns:tools="http://schemas.android.com/tools"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        tools:context=".MainActivity">

        <com.google.android.material.appbar.AppBarLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:theme="@style/Theme.SampleDrawer.AppBarOverlay">
            <androidx.appcompat.widget.Toolbar
                android:id="@+id/toolbar"
                android:layout_width="match_parent"
                android:layout_height="?attr/actionBarSize"
                android:background="?attr/colorPrimary"
                app:popupTheme="@style/Theme.SampleDrawer.PopupOverlay" />
        </com.google.android.material.appbar.AppBarLayout>

        <FrameLayout
            android:id="@+id/container"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            app:layout_behavior="@string/appbar_scrolling_view_behavior">
        </FrameLayout>
    </androidx.coordinatorlayout.widget.CoordinatorLayout>

    <com.google.android.material.navigation.NavigationView
        android:id="@+id/nav_view"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        android:fitsSystemWindows="true"
        app:headerLayout="@layout/nav_header_main"  
        app:menu="@menu/activity_main_drawer" />
</androidx.drawerlayout.widget.DrawerLayout>
```

다음과 같이 프래그먼트들을 만들어준다. 구분을 위해 버튼의 `text` 속성을 다르게 해주었다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#00BCD4"
    android:orientation="vertical">

    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="First" />
</LinearLayout>
```

각 프래그먼트들에 대응하는 `java` 코드도 만들어준다. 

```java
public class Fragment1 extends Fragment {
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment1,container,false);
    }
}
```

`FragmentCallback` 인터페이스를 만든다. `FragmentCallback` 인터페이스는 어떤 프래그먼트를 보여줄지 선택하는 메서드를 포함하고 있다.

```java
public interface FragmentCallback {
    public void onFragmentSelected(int position, Bundle bundle);
}
```

`MainActivity`에서 `toolbar` 생성, `drawer`의 액션바를 `toolbar`로 설정, 메뉴 선택 시 리스너 설정 등을 구현하였다. `GravityCompat.START`은 왼쪽에서 열리고 닫히는 것을 명시해주는 것이다.

```java
public class MainActivity extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener, FragmentCallback {

    Fragment1 fragment1;
    Fragment2 fragment2;
    Fragment3 fragment3;

    DrawerLayout drawer;
    Toolbar toolbar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 툴바 생성
        toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        drawer = findViewById(R.id.drawer_layout);
        // toolbar를 actionbar로 설정
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        // DrawerLayout과 상태를 동기화, DrawerLayout은 좌측 상단의 메뉴 표시
        toggle.syncState();

        NavigationView navigationView = findViewById(R.id.nav_view);
        // 메뉴를 선택했을 때의 Listener 설정
        navigationView.setNavigationItemSelectedListener(this);

        fragment1 = new Fragment1();
        fragment2 = new Fragment2();
        fragment3 = new Fragment3();

        getSupportFragmentManager().beginTransaction().add(R.id.container, fragment1).commit();

    }

    @Override
    public void onBackPressed() {
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // 메뉴 선택에 따른 프래그먼트 변경
        int id = item.getItemId();
        if (id == R.id.menu1) {
            onFragmentSelected(0, null);
        } else if (id == R.id.menu2) {
            onFragmentSelected(1, null);
        } else if (id == R.id.menu3) {
            onFragmentSelected(2, null);
        }

        drawer.closeDrawer(GravityCompat.START);

        return true;
    }

    @Override
    public void onFragmentSelected(int position, Bundle bundle) {
        Fragment curFragment = null;

        if (position == 0) {
            curFragment = fragment1;
            toolbar.setTitle("First");
        } else if (position == 1) {
            curFragment = fragment2;
            toolbar.setTitle("Second");
        } else if (position == 2) {
            curFragment = fragment3;
            toolbar.setTitle("Third");
        }

        getSupportFragmentManager().beginTransaction().replace(R.id.container, curFragment).commit();
    }
}
```

`activity_main_drawer.xml` 내 `item`의 `id` 속성을 변경한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    tools:showIn="navigation_view">

    <group android:checkableBehavior="single">
        <item
            android:id="@+id/menu1"
            android:icon="@drawable/ic_menu_camera"
            android:title="@string/menu_home" />
        <item
            android:id="@+id/menu2"
            android:icon="@drawable/ic_menu_gallery"
            android:title="@string/menu_gallery" />
        <item
            android:id="@+id/menu3"
            android:icon="@drawable/ic_menu_slideshow"
            android:title="@string/menu_slideshow" />
    </group>
</menu>
```

## Conclusion

Navigation Drawer의 메뉴를 선택하면 선택된 프래그먼트로 변경되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)