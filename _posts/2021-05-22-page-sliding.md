---
title: Page Sliding
author: Beomsu Lee
math: true
mermaid: true
tags: [android]
---

## Description

페이지 슬라이딩은 버튼을 눌렀을 때 보이지 않던 뷰가 슬라이딩 방식으로 나타나는 기능이다. 

## Implementation

`activity_main.xml`을 다음과 같이 작성한다. 1번째 레이아웃은 기본 뷰 화면이고 2번째 레이아웃은 슬라이딩 될 뷰이다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical"
        android:background="#ff5555ff">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Base Area"
            android:textColor="#ffffffff"/>
    </LinearLayout>

    <LinearLayout
        android:id="@+id/page"
        android:orientation="vertical"
        android:layout_width="200dp"
        android:layout_height="match_parent"
        android:layout_gravity="right"
        android:background="#ffffff66"
        android:visibility="gone">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Area #1"
            android:textColor="#ff000000"/>
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Area #2"
            android:textColor="#ff000000"/>
    </LinearLayout>

    <LinearLayout
        android:orientation="vertical"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="right|center_vertical"
        android:background="#00000000">
        <Button
            android:id="@+id/button"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Open"/>
    </LinearLayout>


</FrameLayout>
```

슬라이딩에 사용될 애니메이션을 만든다. 다음은 `translate_left.xml`이며 반대의 `translate_right.xml`도 만들어준다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
    android:shareInterpolator="@android:anim/accelerate_decelerate_interpolator">
    <translate
        android:fromXDelta="100%p"
        android:toXDelta="0%p"
        android:duration="500"
        android:repeatCount="0"
        android:fillAfter="true"/>

</set>
```

`MainActivity`에 애니메이션을 로드하고 버튼이 눌릴 때 페이지를 열고 닫을 수 있도록 구현하였다.

```java
public class MainActivity extends AppCompatActivity {

    boolean isPageOpen = false;
    Animation translateLeftAnim;
    Animation translateRightAnim;

    LinearLayout page;
    Button button;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        page = findViewById(R.id.page);

        translateLeftAnim = AnimationUtils.loadAnimation(this,R.anim.translate_left);
        translateRightAnim = AnimationUtils.loadAnimation(this,R.anim.translate_right);

        // 애니메이션의 종료됐을 때의 시점을 알기 위해 AnimationListener 설정
        SlidingPageAnimationListener animListener = new SlidingPageAnimationListener();
        translateLeftAnim.setAnimationListener(animListener);
        translateRightAnim.setAnimationListener(animListener);

        button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(isPageOpen){
                    page.startAnimation(translateRightAnim);
                }else{
                    // 버튼이 눌렸을 때 VISIBLE 적용
                    page.setVisibility(View.VISIBLE);
                    page.startAnimation(translateLeftAnim);
                }
            }
        });
    }

    private class SlidingPageAnimationListener implements Animation.AnimationListener {

        @Override
        public void onAnimationStart(Animation animation) {

        }

        @Override
        public void onAnimationEnd(Animation animation) {
            // 애니메이션이 끝날 때 INVISIBLE 적용
            if(isPageOpen){
                page.setVisibility(View.INVISIBLE);

                button.setText("Open");
                isPageOpen = false;
            }else{
                button.setText("Close");
                isPageOpen = true;
            }
        }

        @Override
        public void onAnimationRepeat(Animation animation) {

        }
    }
}
```

## Conclusion

"OPEN" 버튼을 눌렀을 경우 숨어있던 뷰가 VISIBLE이 되며 나오고 "CLOSE" 버튼을 누르면 애니메이션이 끝난 후 INVISIBLE이 되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)