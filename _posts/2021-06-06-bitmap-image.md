---
title: Bitmap Image
author: Beomsu Lee
category: [Android, Graphic]
tags: [android, graphic]
math: true
mermaid: true
---

## Description

`Bitmap` 객체는 메모리에 만들어지는 이미지이며, 이미지 파일을 읽으면 메모리에 비트맵 객체로 만들 수 있다. 또 이를 이용하면 화면에 이미지를 그릴 수 있다. 

`Bitmap`은 그래픽을 그릴 수 있는 메모리 공간을 제공하는데, 이를 Double Buffering이라 한다. 이 기법은 별도의 메모리 공간에 미리 그래픽을 그린 후 뷰가 다시 그려져야 할 필요가 있을 때 미리 그려놓은 비트맵을 화면에 표시하는 방법이다.

`BitmapFactory` 클래스는 비트맵 이미지를 만들기 위한 클래스 메서드들을 제공하며, 이 메서드들은 이미지를 메모리에 비트맵 객체로 만들어줄 수 있는 방법을 제공한다. 대표적인 메서드들은 다음과 같다.

|Read|Method|
|:---:|:---:|
|파일|public static Bitmap decodeFile(String pathName)|
|리소스|public static Bitmap decodeResource(Resources res, int id)|
|바이트 배열|public static Bitmap decodeByteArray(byte[] data, int offset, int length)|
|스트림|public static Bitmap decodeStream(InputStream is)|

## Double Buffering Implementation

Double Buffering을 이용해 비트맵 이미지를 화면에 나타내는 코드를 작성한다.

```java
public class CustomImageView extends View {
    // 메모리에 만들어질 Bitmap 선언
    private Bitmap cacheBitmap;
    // Bitmap 객체에 그리기 위한 Canvas 선언
    private Canvas cacheCanvas;
    private Paint mPaint;

    public CustomImageView(Context context) {
        super(context);
        init(context);
    }

    public CustomImageView(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    private void init(Context context){
        mPaint = new Paint();
    }
    // 뷰가 화면에 보이기 전 
    protected void onSizeChanged(int w,int h,int oldw, int oldh){
        // Bitmap 객체 만들고
        createCacheBitmp(w,h);
        // 그 위에 그린다.
        testDrawing();
    }

    private void createCacheBitmp(int w,int h){
        cacheBitmap = Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
        cacheCanvas = new Canvas();
        cacheCanvas.setBitmap(cacheBitmap);
    }

    // 실제 그래픽이 그려지는 시점
    private void testDrawing(){
        // 빨간 사각형 
        cacheCanvas.drawColor(Color.WHITE);
        mPaint.setColor(Color.RED);
        cacheCanvas.drawRect(100,100,200,200,mPaint);

        // 리소스 이미지 읽고 화면에 그린다.
        Bitmap srcImg = BitmapFactory.decodeResource(getResources(),R.drawable.waterdrop);
        cacheCanvas.drawBitmap(srcImg,30,30,mPaint);

        // 매트릭스 객체를 이용해 좌우 대칭되도록 그린다.
        Matrix horInverseMatrix = new Matrix();
        horInverseMatrix.setScale(-1,1);
        Bitmap horInverseImg = Bitmap.createBitmap(srcImg,0,0,srcImg.getWidth(),srcImg.getHeight(),horInverseMatrix,false);
        cacheCanvas.drawBitmap(horInverseImg,30,130,mPaint);

        // 매트릭스 객체를 이용해 상하 대칭되도록 그린다.
        Matrix verInverseMatrix = new Matrix();
        verInverseMatrix.setScale(1,-1);
        Bitmap verInverseImg = Bitmap.createBitmap(srcImg,0,0,srcImg.getWidth(),srcImg.getHeight(),verInverseMatrix,false);
        cacheCanvas.drawBitmap(verInverseImg,30,230,mPaint);

        // 원본 크기의 3배로 늘렸을 경우의 Blur 효과 적용 
        mPaint.setMaskFilter(new BlurMaskFilter(10,BlurMaskFilter.Blur.NORMAL));
        Bitmap scaledImg = Bitmap.createScaledBitmap(srcImg,srcImg.getWidth()*3,srcImg.getHeight()*3,false);
        cacheCanvas.drawBitmap(scaledImg,30,300,mPaint);
    }

    protected void onDraw(Canvas canvas){
        if(cacheBitmap != null){
            // 메모리의 Bitmap을 이용해 그린다.
            canvas.drawBitmap(cacheBitmap,0,0,null);
        }
    }
}
```

`MainActivity`에 `CustomImageView` 객체 생성 후 그려준다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        CustomImageView view = new CustomImageView(this);
        setContentView(view);
    }
}
```

## Conclusion

Double Buffering을 기법을 이용해 `Bitmap` 이미지를 화면에 나타내었고, 좌우, 상하 대칭, Blur 효과를 적용해보았다. 

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)