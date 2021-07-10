---
title: Multi Touch View
author: Beomsu Lee
category: [Android]
tags: [android, multi touch]
math: true
mermaid: true
---

## Description

Multi-Touch 기능은 두 손가락 이상의 터치에 대해 처리하는 기능이다. 실제 앱을 만들 때는 자주 활용되는 편은 아니지만 생각보다 쉽게 구현할 수 있다.

사용자가 손가락으로 터치했을 때 `getPointerCount()` 메서드를 통해 몇 개의 손가락으로 터치되었는지 알 수 있다. 또한 `getX(int pointerIndex)`, `getY(int pointerIndex)` 메서드를 이용해 모든 터치된 손가락의 좌표 값을 얻어올 수 있다.

## Implementation

한 손가락으로 터치했을 때는 이동, 두 손가락으로 터치했을 때는 확대, 축소되도록 구현한다.

```java
public class ImageDisplayView extends View implements View.OnTouchListener {
    private static final String TAG = "ImageDisplayView";

    Context mContext;
    Canvas mCanvas;
    Bitmap mBitmap;
    Paint mPaint;

    int lastX;
    int lastY;

    Bitmap sourceBitmap;

    Matrix mMatrix;

    float sourceWidth = 0.0F;
    float sourceHeight = 0.0F;

    float bitmapCenterX;
    float bitmapCenterY;

    float scaleRatio;
    float totalScaleRatio;

    float displayWidth = 0.0F;
    float displayHeight = 0.0F;

    int displayCenterX = 0;
    int displayCenterY = 0;

    public float startX;
    public float startY;

    public static float MAX_SCALE_RATIO = 5.0F;
    public static float MIN_SCALE_RATIO = 0.1F;

    float oldDistance = 0.0F;

    int oldPointerCount = 0;
    boolean isScrolling = false;
    float distanceThreshold = 3.0F;

    public ImageDisplayView(Context context) {
        super(context);

        mContext = context;

        init();
    }

    public ImageDisplayView(Context context, AttributeSet attrs) {
        super(context, attrs);

        mContext = context;

        init();
    }

    private void init() {
        mPaint = new Paint();
        mMatrix = new Matrix();

        lastX = -1;
        lastY = -1;

        setOnTouchListener(this);
    }

    // 뷰 초기화 후 화면에 보이기 전 크기가 정해지면 호출되는 메서드
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        // 메모리 상에 새로운 비트맵 객체 생성
        if (w > 0 && h > 0) {
            newImage(w, h);
            redraw();
        }
    }

    public void newImage(int width, int height) {
        Bitmap img = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas();
        canvas.setBitmap(img);

        mBitmap = img;
        mCanvas = canvas;

        displayWidth = (float) width;
        displayHeight = (float) height;

        displayCenterX = width / 2;
        displayCenterY = height / 2;
    }

    public void drawBackground(Canvas canvas) {
        if (canvas != null) {
            canvas.drawColor(Color.BLACK);
        }
    }

    protected void onDraw(Canvas canvas) {
        if (mBitmap != null) {
            // 비트맵 객체 그리기
            canvas.drawBitmap(mBitmap, 0, 0, null);
        }
    }

    public void setImageData(Bitmap image) {
        recycle();

        sourceBitmap = image;

        sourceWidth = sourceBitmap.getWidth();
        sourceHeight = sourceBitmap.getHeight();

        bitmapCenterX = sourceBitmap.getWidth() / 2;
        bitmapCenterY = sourceBitmap.getHeight() / 2;

        scaleRatio = 1.0F;
        totalScaleRatio = 1.0F;
    }

    public void recycle() {
        if (sourceBitmap != null) {
            sourceBitmap.recycle();
        }
    }

    public void redraw() {
        if (sourceBitmap == null) {
            Log.d(TAG, "sourceBitmap is null in redraw().");
            return;
        }

        drawBackground(mCanvas);

        float originX = (displayWidth - (float) sourceBitmap.getWidth()) / 2.0F;
        float originY = (displayHeight - (float) sourceBitmap.getHeight()) / 2.0F;

        mCanvas.translate(originX, originY);
        mCanvas.drawBitmap(sourceBitmap, mMatrix, mPaint);
        mCanvas.translate(-originX, -originY);

        invalidate();
    }


    public boolean onTouch(View v, MotionEvent ev) {
        final int action = ev.getAction();

        int pointerCount = ev.getPointerCount();
        Log.d(TAG, "Pointer Count : " + pointerCount);

        switch (action) {
            case MotionEvent.ACTION_DOWN:
                // 손가락 개수 확인
                if (pointerCount == 1) {
                    float curX = ev.getX();
                    float curY = ev.getY();

                    startX = curX;
                    startY = curY;

                } else if (pointerCount == 2) {
                    // 두 손가락 사이 거리
                    oldDistance = 0.0F;
                    // 손가락 움직이고 있는지 여부
                    isScrolling = true;
                }

                return true;
            case MotionEvent.ACTION_MOVE:

                if (pointerCount == 1) {

                    if (isScrolling) {
                        return true;
                    }

                    float curX = ev.getX();
                    float curY = ev.getY();

                    if (startX == 0.0F) {
                        startX = curX;
                        startY = curY;

                        return true;
                    }

                    float offsetX = startX - curX;
                    float offsetY = startY - curY;

                    if (oldPointerCount == 2) {

                    } else {
                        Log.d(TAG, "ACTION_MOVE : " + offsetX + ", " + offsetY);

                        // 이미지가 커지거나 작아질 때 조절
                        if (totalScaleRatio > 1.0F) {
                            moveImage(-offsetX, -offsetY);
                        }

                        startX = curX;
                        startY = curY;
                    }

                } else if (pointerCount == 2) {

                    float x1 = ev.getX(0);
                    float y1 = ev.getY(0);
                    float x2 = ev.getX(1);
                    float y2 = ev.getY(1);

                    float dx = x1 - x2;
                    float dy = y1 - y2;
                    // 거리 계산
                    float distance = new Double(Math.sqrt(new Float(dx * dx + dy * dy).doubleValue())).floatValue();

                    float outScaleRatio = 0.0F;
                    if (oldDistance == 0.0F) {
                        oldDistance = distance;

                        break;
                    }

                    if (distance > oldDistance) {
                        if ((distance - oldDistance) < distanceThreshold) {
                            return true;
                        }

                        outScaleRatio = scaleRatio + (oldDistance / distance * 0.05F);
                    } else if (distance < oldDistance) {
                        if ((oldDistance - distance) < distanceThreshold) {
                            return true;
                        }

                        outScaleRatio = scaleRatio - (distance / oldDistance * 0.05F);
                    }

                    // 이미지가 커지거나 작아질 때 조절
                    if (outScaleRatio < MIN_SCALE_RATIO || outScaleRatio > MAX_SCALE_RATIO) {
                        Log.d(TAG, "Invalid scaleRatio : " + outScaleRatio);
                    } else {
                        Log.d(TAG, "Distance : " + distance + ", ScaleRatio : " + outScaleRatio);
                        scaleImage(outScaleRatio);
                    }

                    oldDistance = distance;
                }

                oldPointerCount = pointerCount;

                break;

            case MotionEvent.ACTION_UP:

                if (pointerCount == 1) {

                    float curX = ev.getX();
                    float curY = ev.getY();

                    float offsetX = startX - curX;
                    float offsetY = startY - curY;

                    if (oldPointerCount == 2) {

                    } else {
                        moveImage(-offsetX, -offsetY);
                    }

                } else {
                    isScrolling = false;
                }

                return true;
        }

        return true;
    }

    private void scaleImage(float inScaleRatio) {
        Log.d(TAG, "scaleImage() called : " + inScaleRatio);

        // inScaleRatio 기준 확대, 축소
        mMatrix.postScale(inScaleRatio, inScaleRatio, bitmapCenterX, bitmapCenterY);
        // 회전 각도 
        mMatrix.postRotate(0);

        totalScaleRatio = totalScaleRatio * inScaleRatio;

        redraw();
    }

    private void moveImage(float offsetX, float offsetY) {
        Log.d(TAG, "moveImage() called : " + offsetX + ", " + offsetY);

        // 이동
        mMatrix.postTranslate(offsetX, offsetY);

        redraw();
    }
}
```

`activity_main.xml`에 `container` 하나를 생성한다.

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
        android:id="@+id/container"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">

    </LinearLayout>

</LinearLayout>
```

`MainActivity`에 `R.drawable.beach`를 불러와 `ImageDisplayView` 객체에 설정해준다. 

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        LinearLayout container = findViewById(R.id.container);
        Resources res = getResources();
        Bitmap bitmap = BitmapFactory.decodeResource(res,R.drawable.beach);

        ImageDisplayView view = new ImageDisplayView(this);
        view.setImageData(bitmap);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.MATCH_PARENT);
        container.addView(view,params);
    }
}
```

## Conclusion

1개의 손가락으로 터치할 경우 사진이 이동되며, 2개의 손가락으로 터치했을 때의 이미지가 확대, 축소되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
- [Matrix](https://developer.android.com/reference/android/graphics/Matrix)