---
title: ViewPager
author: Beomsu Lee
category: [Android]
tags: [android, viewpager]
math: true
mermaid: true
---

## Description

뷰페이저는 손가락으로 좌우 스크롤하여 넘겨볼 수 있는 기능이다. 화면 전체를 뷰페이저로 사용할 수도 있고 부분 화면도 뷰페이저를 사용할 수 있다. 

## Implementation

우선 뷰페이저를 `activity_main`에 정의하였다. `PagerTitleStrip`을 사용해 아이템을 구분하여 보여주도록 했다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <androidx.viewpager.widget.ViewPager
        android:id="@+id/view_pager"
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        <androidx.viewpager.widget.PagerTitleStrip
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_gravity="top">
        </androidx.viewpager.widget.PagerTitleStrip>
    </androidx.viewpager.widget.ViewPager>
</LinearLayout>
```

다음은 뷰페이저를 통해 변경될 프래그먼트를 만든다. 각 레이아웃마다 TextView를 두어 구별하였다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/white"
    android:orientation="vertical" >

    <TextView
        android:id="@+id/textView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:textSize="30sp"
        android:text="First View" />
</LinearLayout>
```

이 `xml`에 대응되는 `java` 코드를 작성하여 `xml`이 뷰에 로드되도록 한다.

```java
public class Fragment1 extends Fragment {
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment1,container,false);
    }
}
```

`MainActivity`에서 `FragmentStatePagerAdapter`를 상속한 `MyPageAdapter` 내부 클래스를 만들었다. 어댑터는 뷰페이저에 보여줄 각 프래그먼트를 담아두는 `ArrayList`를 만들었다. 뷰페이저는 어댑터와 상호작용 하면서 `getCount()` 메서드를 통해 몇 개의 프래그먼트가 들어 있는지 확읺나다. 그 후 화면 상태에 따라 해당하는 프래그먼트를 꺼내 보여준다. `setOffscreenPageLimit()`를 사용하면 미리 로딩할 아이템의 개수를 지정할 수 있는데 이는 스크롤 시 더 빠르게 보여주는 역할을 한다.

```java
public class MainActivity extends AppCompatActivity {

    ViewPager pager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        pager = findViewById(R.id.view_pager);
        // 미리 로딩해 놓을 아이템의 개수
        pager.setOffscreenPageLimit(3);

        MyPageAdapter adapter = new MyPageAdapter(getSupportFragmentManager());

        Fragment1 fragment1 = new Fragment1();
        adapter.addItem(fragment1);
        Fragment2 fragment2 = new Fragment2();
        adapter.addItem(fragment2);
        Fragment3 fragment3 = new Fragment3();
        adapter.addItem(fragment3);

        // 어댑터 설정
        pager.setAdapter(adapter);

    }

    class MyPageAdapter extends FragmentStatePagerAdapter{
        ArrayList<Fragment> items = new ArrayList<Fragment>();

        public MyPageAdapter(FragmentManager fm){
            super(fm);
        }

        public void addItem(Fragment item){
            items.add(item);
        }

        @Override
        public Fragment getItem(int position) {
            return items.get(position);
        }

        @Override
        public int getCount() {
            return items.size();
        }

        @Nullable
        @org.jetbrains.annotations.Nullable
        @Override
        public CharSequence getPageTitle(int position) {
            return "Page" + position;
        }
    }
}
```

## Conclusion

뷰페이저를 통해 스크롤 시 화면이 넘어가 원하는 프래그먼트로 이동할 수 있는 것을 확인할 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)