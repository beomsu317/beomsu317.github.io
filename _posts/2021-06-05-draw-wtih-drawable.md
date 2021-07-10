---
title: Draw with Drawable
author: Beomsu Lee
category: [Android]
tags: [graphic]
---

## Description

그리기가 가능한 요소들은 `Drawable` 객체로 만들어 그릴 수 있다. 이 객체는 그릴 수 있는 모든 것을 의미하는데 대표적으로 `ShapeDrawable`, `BitmapDrawable`, `PictureDrawable`, `LayerDrawable` 등이 있다.

`Drawable` 객체의 형태로는 PNG, JPEG 이미지등을 표현하는 Bitmap, 이미지가 자동으로 늘어는 부분을 설정하여 사용하는 NinePatch, 도형 그리기가 가능한 Shape, 세로축의 순서에 따라 그리는 Layer 등이 있다.

`Drawable`을 사용하면 각각 그래픽 그리기 작업을 독립적인 객체로 나누어 관리할 수 있는 장점이 있다. 또한 이 객체에 애니메이션을 적용할 수도 있다.

## Implementation

뷰 전체를 그라데이션 효과로 채우도록 구현하고, 3개의 선을 구현할 것이다. 우선 `colors.xml`에 3가지 색을 추가한다.

```xml
<resources>
...
    <color name="color01">#FF000000</color>
    <color name="color02">#FF888888</color>
    <color name="color03">#FF333333</color>
</resources>
```

`View`를 상속하여 `CustomViewDrawable`를 구현한다.

```java
public class CustomViewDrawable extends View {
    private ShapeDrawable upperDrawable;
    private ShapeDrawable lowerDrawable;

    public CustomViewDrawable(Context context) {
        super(context);
        init(context);
    }

    public CustomViewDrawable(Context context, @Nullable @org.jetbrains.annotations.Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    private void init(Context context){
        // 윈도우 매니저를 사용해 뷰의 width, height를 알아온다.
        WindowManager manager = (WindowManager)context.getSystemService(Context.WINDOW_SERVICE);
        Display display = manager.getDefaultDisplay();
        int width = display.getWidth();
        int height = display.getHeight();

        // 리소스에 정의된 색상 값을 변수에 설정
        Resources curRes = getResources();
        int blackColor = curRes.getColor(R.color.color01);
        int grayColor = curRes.getColor(R.color.color02);
        int darkGrayColor = curRes.getColor(R.color.color03);

        // Drawable 객체 생성
        upperDrawable = new ShapeDrawable();

        RectShape rectangle = new RectShape();
        rectangle.resize(width,height*2/3);
        upperDrawable.setShape(rectangle);
        upperDrawable.setBounds(0,0,width,height*2/3);

        // LinearGradient : 뷰 영역의 위쪽 2/3과 아래쪽 1/3을 따로 채워줌으로써 위쪽에서부터 아래쪽으로 색상이 조금씩 변하는 배경화면을 만들 수 있다.
        LinearGradient gradient = new LinearGradient(0,0,0,height*2/3,grayColor,blackColor, Shader.TileMode.CLAMP);
        Paint paint = upperDrawable.getPaint();

        // Paint 객체에서 새로 생성한 객체를 Shader로 설정
        paint.setShader(gradient);

        lowerDrawable = new ShapeDrawable();
        RectShape rectangle2 = new RectShape();
        rectangle2.resize(width,height*1/3);
        lowerDrawable.setShape(rectangle2);
        lowerDrawable.setBounds(0,height*2/3,width,height);

        LinearGradient gradient2 =new LinearGradient(0,0,0,height*1/3,blackColor,darkGrayColor,Shader.TileMode.CLAMP);

        Paint paint2 = lowerDrawable.getPaint();
        paint2.setShader(gradient2);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Drawable 객체 그린다.
        upperDrawable.draw(canvas);
        lowerDrawable.draw(canvas);

        // 
        Paint pathPaint = new Paint();
        pathPaint.setAntiAlias(true);
        pathPaint.setColor(Color.YELLOW);
        pathPaint.setStyle(Paint.Style.STROKE);
        // Stroke 폭 설정
        pathPaint.setStrokeWidth(16.0F);
        // Stroke 끝 부분 모양 설정
        pathPaint.setStrokeCap(Paint.Cap.BUTT);
        // Stroke 꼭짓점 부분 연결 모양 설정
        pathPaint.setStrokeJoin(Paint.Join.MITER);

        // Path 생성
        Path path = new Path();
        // 좌표 값 추가
        path.moveTo(20,20);
        // 이전 좌표 값과 선으로 연결
        path.lineTo(120,20);
        path.lineTo(160,90);
        path.lineTo(180,80);
        path.lineTo(200,120);

        // Path 그리기
        canvas.drawPath(path,pathPaint);

        pathPaint.setColor(Color.WHITE);
        pathPaint.setStrokeCap(Paint.Cap.ROUND);
        pathPaint.setStrokeJoin(Paint.Join.ROUND);

        // 주어진 오프셋 이동 후 그리기
        path.offset(30,120);
        canvas.drawPath(path,pathPaint);

        pathPaint.setColor(Color.CYAN);
        pathPaint.setStrokeCap(Paint.Cap.SQUARE);
        pathPaint.setStrokeJoin(Paint.Join.BEVEL);

        path.offset(30,120);
        canvas.drawPath(path,pathPaint);
    }
}
```

`MainActivity`에 `CustomViewDrawable` 객체를 만들고 `setContentView()` 메서드로 그려준다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        CustomViewDrawable view = new CustomViewDrawable(this);
        setContentView(view);
    }
}
```

## Conclusion

위쪽 2/3과 아래쪽 1/3을 따로 채워주어 위쪽에서 아래쪽으로 색상이 변하는 배경화면을 만들었고, 그 위에 각 모양을 가진 선 3개가 그려진 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)