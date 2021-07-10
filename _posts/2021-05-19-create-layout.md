---
title: Create Layout
author: Beomsu Lee
category: [Android, Layout]
tags: [android, layout, create layout]
math: true
mermaid: true
---

## Description

레이아웃을 상속해 새로운 레이아웃을 만들어보자. 레이아웃도 뷰를 새로 만드는 것과 동일한 방법으로 만들 수 있다.

## Implementation

먼저 `layout1.xml`을 만든다. `ImageView` 1개와 `TextView` 2개를 넣어준다. 카드뷰를 이용해 영역을 구분해주었다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <androidx.cardview.widget.CardView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        app:cardBackgroundColor="#ffffffff"
        app:cardCornerRadius="10dp"
        app:cardElevation="5dp"
        app:cardUseCompatPadding="true">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">
            <ImageView
                android:id="@+id/imageView"
                android:layout_width="80dp"
                android:layout_height="80dp"
                app:srcCompat="@mipmap/ic_launcher" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_margin="5dp"
                android:orientation="vertical">

                <TextView
                    android:id="@+id/textView1"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textSize="30sp"
                    android:textColor="#ff0000ff"
                    android:text="TextView" />

                <TextView
                    android:id="@+id/textView2"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textSize="25sp"
                    android:textColor="#ff0000ff"
                    android:text="TextView" />
            </LinearLayout>
        </LinearLayout>
    </androidx.cardview.widget.CardView>
</LinearLayout>
```

이에 대응하는 `Layout1.class`를 만들어 `init()` 할 때 인플레이션을 수행하였다. 인플레이션 후 `setImage()`, `setName()`, `setMobile()` 함수를 추가해 외부에서 변경될 수 있도록 작성하였다.

```java
public class Layout1 extends LinearLayout {
    ImageView imageView;
    TextView textView;
    TextView textView2;

    public Layout1(Context context) {
        super(context);
        init(context);
    }

    public Layout1(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    private void init(Context context){
        LayoutInflater inflator = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        inflator.inflate(R.layout.layout1,this,true);

        imageView = findViewById(R.id.imageView);
        textView = findViewById(R.id.textView1);
        textView2 = findViewById(R.id.textView2);
    }

    public void setImage(int resId){
        imageView.setImageResource(resId);
    }

    public void setName(String name){
        textView.setText(name);
    }

    public void setMobile(String mobile){
        textView2.setText(mobile);
    }
}
```

`activity_main.xml`은 버튼 2개를 추가해 프로필 이미지를 변경할 수 있도록 구현하였다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="First Image" />

    <Button
        android:id="@+id/button2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Second Image" />

    <com.example.samplelayout.Layout1
        android:id="@+id/layout1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content">

    </com.example.samplelayout.Layout1>
</LinearLayout>
```

구현된 레이아웃 외부에서 함수를 호출해 수정사항들을 변경할 수 있다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Layout1 layout1 = findViewById(R.id.layout1);

        layout1.setImage(R.drawable.ic_launcher_foreground);
        layout1.setName("Hong gildong");
        layout1.setMobile("010-1234-5678");

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                layout1.setImage(R.drawable.profile1);
            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                layout1.setImage(R.drawable.profile2);
            }
        });
    }
}
```

## Conclusion

레이아웃을 구현하여 외부에서 호출할 수 있는 함수를 만들고 `MainActivity`에서 호출함으로써 변경 가능한 새로운 레이아웃을 구현하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)