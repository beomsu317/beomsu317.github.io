---
title: Multi Window Mode
author: Beomsu Lee
category: [Android]
tags: [android, multi window]
math: true
mermaid: true
---

## Description

멀티 윈도우는 단말 화면에 여러 개의 액티비티가 보이도록 지원하는 기능이다. 이 기능은 API 24부터 지원되며 이전 단말에서는 없던 기능이다. 

오버뷰 화면에서 상단의 타이틀 가운데 부분을 클릭하면 다중 창으로 만들 수 있는 메뉴가 있다. 이 메뉴를 선택해 화면 분할 후 다른 액티비티를 다른 창에 보이도록 선택하면 된다.

멀티 윈도우 모드로 동작할 때 액티비티가 보이는 영역이 줄어들기 때문에 화면 레이아웃을 변경해주어야 할 수도 있다. 이런 문제를 해결하기 위해 다음과 같은 메서드가 제공된다.


- public boolean isInMultiWindowMode()
    - 다중 창 모드에 들어가 있는지 확인
- public boolean isInPictureInPictureMode()
    - PIP 모드에 들어가 있는지 확인
- public void onMultiWindowModeChanged(boolean isInMultiWindowMode, Configuration newConfig)
    - 다중 창 모드로 변경되었을 때 호출됨

## Implementation

`activiy_main.xml`에 2개의 버튼과 스크롤뷰 안에 텍스트뷰를 배치한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">
        <Button
            android:id="@+id/button"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Check Multi Mode"/>
        <Button
            android:id="@+id/button2"
            android:layout_marginLeft="5dp"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Check PIP Mode"/>
    </LinearLayout>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        <TextView
            android:id="@+id/textView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"/>
    </ScrollView>
</LinearLayout>
```

`MainActivity`에 각 버튼을 눌렀을 경우 멀티 윈도우 모드인지 PIP 모드인지 출력해주는 코드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {

    TextView textView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView = findViewById(R.id.textView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @RequiresApi(api = Build.VERSION_CODES.N)
            @Override
            public void onClick(View view) {
                boolean isIn = isInMultiWindowMode();
                println("Multi Window Mode :"+isIn);
            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @RequiresApi(api = Build.VERSION_CODES.N)
            @Override
            public void onClick(View view) {
                boolean isIn = isInPictureInPictureMode();
                println("PIP Mode :"+isIn);
            }
        });
    }

    @Override
    public void onMultiWindowModeChanged(boolean isInMultiWindowMode) {
        super.onMultiWindowModeChanged(isInMultiWindowMode);
        println("Multi Window Mode Changed : "+isInMultiWindowMode);
    }

    public void println(String data){
        textView.append(data + "\n");
    }
}
```

## Conclusion

멀티 윈도우로 액티비티를 띄우고 버튼을 누르면 멀티 윈도우 모드인지 여부를 확인할 수 있으며 PIP 모드도 동일하게 확인 가능하다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
