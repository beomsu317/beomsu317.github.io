---
title: Create View
author: Beomsu Lee
category: [Android, View]
tags: [android, view, create view]
math: true
mermaid: true
---

## Description

API에서 제공하는 뷰를 사용해 새로운 뷰를 정의할 수 있다. API를 상속해 새로운 뷰를 만들 때 개발자가 추가적인 코드를 넣을 수 있도록 콜백 메서드가 존재한다.

뷰가 스스로의 크기를 정할 때 자동으로 호출되는 함수는 `onMeasure(int widthMeasureSpec, int heightMeasureSpec)`이고 스스로 레이아웃에 맞게 그릴 땐 `onDraw()` 함수가 자동으로 호출된다. `widthMeasureSpec`, `heightMeasureSpec`은 레이아웃에서 이 뷰가 사용 가능한 여유 공간의 폭과 높이에 대한 정보이다. 

뷰가 화면에 보일 때 `onDraw()` 함수가 호출된다. 따라서 `onDraw()` 함수를 재정의한다면 원하는 내용물을 그릴 수 있게 된다.

`invalidate()` 함수를 호출하면 자동으로 `onDraw()` 함수가 호출되어 뷰의 그래픽을 다시 그릴 수 있다.

## Implementation

`/app/res/values/dimens.xml` 파일을 생성한 후 다음과 같이 `text_size`를 16sp로 만들어준다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <dimen name="text_size">16sp</dimen>
</resources>
```

`MyButton` 클래스를 만들고 생성자 및 `onTouchEvent()`, `onDraw()`를 구현한다.

```java
public class MyButton extends AppCompatButton {
    private static final String TAG = "MyButton";

    public MyButton(@NonNull @org.jetbrains.annotations.NotNull Context context) {
        super(context);
        init(context);
    }

    public MyButton(@NonNull @org.jetbrains.annotations.NotNull Context context, @Nullable @org.jetbrains.annotations.Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }
    private void init(Context context){
        setBackgroundColor(Color.CYAN);
        setTextColor(Color.BLACK);

        // /app/res/values 폴더 안에 dimens.xml을 참조
        float textSize = getResources().getDimension(R.dimen.text_size);
        // 픽셀 단위 설정만 가능해 dimens.xml을 통해 얻어온 값을 전달
        setTextSize(textSize);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        Log.d(TAG, "onTouchEvent called");
        int action = event.getAction();
        switch (action){
            // 버튼이 눌렸을 경우 백그라운드는 파랑, 글자 색은 빨강으로 설정
            case MotionEvent.ACTION_DOWN:
                setBackgroundColor(Color.BLUE);
                setTextColor(Color.RED);
                break;
            // 이외의 경우 
            case MotionEvent.ACTION_OUTSIDE:
            case MotionEvent.ACTION_CANCEL:
            case MotionEvent.ACTION_UP:
                setBackgroundColor(Color.CYAN);
                setTextColor(Color.BLACK);
                break;
        }
        // view를 다시 그려준다.
        invalidate();
        return true;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        Log.d(TAG, "onDraw called");
    }
}
```

`activity_main.xml`은 다음과 같이 `MyButton`의 버튼을 추가한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <com.example.sampleview.MyButton
        android:id="@+id/button"
        android:layout_width="200dp"
        android:layout_height="80dp"
        android:layout_centerInParent="true"
        android:text="Start"/>
</RelativeLayout>
```

## Conclusion

가운데 버튼을 눌렀을 때 백그라운드 색과 글자 색이 변경되는 것을 확인할 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)