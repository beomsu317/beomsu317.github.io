---
title: Draw Graphics in View
author: Beomsu Lee
category: [Android]
tags: [graphic]
---

## Description

뷰에 그래픽을 그리는 방법은 뷰(View) 클래스를 상속받고 그 뷰에 직접 그래픽을 그리는 것이다. 그래픽을 그릴 때 주요 클래스는 다음과 같다.

|Class|Description|
|:---:|:---|
|Canvas|뷰의 표면에 직접 그릴 수 있도록 만들어 주는 객체로 그래픽 그리기를 위한 메서드가 정의됨|
|Paint|그래픽 그리기를 위해 필요한 색상 등 속성 보유|
|Bitmap|픽셀로 구성된 이미지로 메모리에 그래픽을 그리는데 사용|
|Drawable|사각형, 이미지 등 그래픽 요소가 객체로 정의됨|

다음은 `Canvas` 객체를 통해 자주 사용되는 그리기 메서드이다.

|Method|Description|
|:---:|:---|
|점|void drawPoint(float x, float y, Paint paint)|
|선|void drawLine(float startX, float startY, float stopX, float stopY, Paint paint)|
|사각형|void drawRect (float left, float top, float right, float bottom, Paint paint)|
|둥근 모서리 사각형|void drawRoundRect (RectF rect, float rx, float ry, Paint paint)|
|원|void drawCircle (float cx, float cy, float radius, Paint paint)|
|타원|void drawOval (float left, float top, float right, float bottom, Paint paint)|
|아크|void drawArc (RectF oval, float startAngle, float sweepAngle, boolean useCenter, Paint paint)|
|패스|void drawPath (Path path, Paint paint)|
|비트맵|void drawBitmap (Bitmap bitmap, float left, float top, Paint paint)|

## Implementation

`View`를 상속받는 `CustomViewStyle`를 생성하고 `onDraw()`에 그래픽을 그려준다.

```java
public class CustomViewStyle extends View {
    Paint paint;

    public CustomViewStyle(Context context){
        super(context);
        init(context);
    }


    public CustomViewStyle(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    private void init(Context context){
        paint = new Paint();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // FILL 스타일의 사각형 
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.RED);
        canvas.drawRect(10,10,100,100,paint);

        // 위의 사각형을 STROKE 스타일로 설정
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(2.0F);
        paint.setColor(Color.GREEN);
        canvas.drawRect(10,10,100,100,paint);

        // 2번째 사각형을 FILL 스타일로 설정
        paint.setStyle(Paint.Style.FILL);
        // 투명도 설정
        paint.setARGB(128,0,0,255);
        canvas.drawRect(120,10,210,100,paint);

        // 2번째 사각형을 STROKE 스타일로 설정하고 DashPathEffect 적용
        // 선이 그려지는 부분과 선이 그려지지 않는 부분을 각각 5의 크기로 지정
        DashPathEffect dashEffect = new DashPathEffect(new float[]{5,5}, 1);
        paint.setStyle(Paint.Style.STROKE);
        // 선의 두께를 설정
        paint.setStrokeWidth(3.0F);
        paint.setPathEffect(dashEffect);
        paint.setColor(Color.GREEN);
        canvas.drawRect(120,10,210,100,paint);

        paint = new Paint();

        // Circle
        paint.setColor(Color.MAGENTA);
        canvas.drawCircle(50,160,40,paint);

        // 선을 부드럽게 그리고 싶은 경우 AntiAlias 설정
        paint.setAntiAlias(true);
        canvas.drawCircle(160,160,40,paint);

        // Text
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(1);
        paint.setColor(Color.MAGENTA);
        paint.setTextSize(30);
        canvas.drawText("Text (Stroke)",20,260,paint);

        paint.setStyle(Paint.Style.FILL);
        paint.setTextSize(30);
        canvas.drawText("Text",20,320,paint);
    }
}
```

만약 새로만든 뷰를 XML에 추가하려면 다음과 같이 작성하면 된다.

```xml
<com.example.graphicscustom.CustomViewStyle
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"/>
```

코드로 구현할 경우 `MainActivity`에 `CustomViewStyle` 객체를 만들고 `setContentView()` 메서드로 그려주면 된다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        CustomViewStyle view = new CustomViewStyle(this);
        setContentView(view);
    }
}
```

클리핑(Cliping)은 원하는 영역에만 그릴 수 있도록 설정하는 것으로 `clipRect()` 또는 `clipRegion()` 메서드를 통해 영역을 설정할 수 있다.

## Conclusion

`View` 객체를 상속해 원하는 위치에 사각형, 원, 텍스트를 그릴 수 있는 것을 확인하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
- [Canvas](https://developer.android.com/reference/android/graphics/Canvas)