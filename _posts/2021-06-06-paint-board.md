---
title: Paint Board
author: Beomsu Lee
category: [Android]
tags: [paint board]
math: true
mermaid: true
---

## Description

사용자가 화면을 터치하며 직접 그릴 수 있도록 하려면 터치 이벤트를 이용하여야 한다. `onTouchEvent()` 메서드를 이용해 터치한 곳의 좌표 값을 이용해 그리기 기능을 구현할 수 있다.

## Implementation

`PaintBoard` 클래스를 만들고 터치 후 좌표가 변경될 때 그려주도록 구현하였다.

```java
public class PaintBoard extends View {
    Canvas mCanvas;
    Bitmap mBitmap;
    Paint mPaint;

    int lastX;
    int lastY;

    public PaintBoard(Context context) {
        super(context);
        init(context);
    }

    public PaintBoard(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    private void init(Context context){
        this.mPaint = new Paint();
        this.mPaint.setColor(Color.BLACK);

        this.lastX = -1;
        this.lastY = -1;

    }

    protected void onSizeChanged(int w,int h,int oldw, int oldh){
        Bitmap img = Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas();
        canvas.setBitmap(img);
        canvas.drawColor(Color.WHITE);

        mBitmap = img;
        mCanvas = canvas;
    }

    @Override
    protected void onDraw(Canvas canvas) {
        if(mBitmap != null){
            canvas.drawBitmap(mBitmap,0,0,null);
        }
    }

    public boolean onTouchEvent(MotionEvent event) {
        int action = event.getAction();

        // 좌표 값 얻어온다.
        int X = (int)event.getX();
        int Y = (int)event.getY();

        switch (action){
            // 손가락을 떼었을 때
            case MotionEvent.ACTION_UP:
                lastX = -1;
                lastY = -1;
                break;
            // 손가락으로 터치했을 때
            case MotionEvent.ACTION_DOWN:
                if(lastX != -1){
                    if(X != lastX || Y != lastY){
                        mCanvas.drawLine(lastX,lastY,X,Y,mPaint);
                    }
                }
                lastX = X;
                lastY = Y;
                break;
            // 터치하고 있고 이동했을 때
            case MotionEvent.ACTION_MOVE:
                if(lastX != -1){
                    mCanvas.drawLine(lastX,lastY,X,Y,mPaint);
                }
                lastX = X;
                lastY = Y;

                break;
        }
        // 다시 그려준다.
        invalidate();
        return true;
    }
}
```

## Path Implementation

위와 같이 구현한 경우 선이 직선으로 그려지는 경우가 존재한다. 이것은 이벤트를 처리할 때 직선으로 각각의 좌표 값을 연결했기 때문이다. `Path`를 이용하면 이런 직선으로 그려지는 경우를 부드러운 곡선으로 만들 수 있다.

```java
public class BestPaintBoard extends View {
    public boolean changed = false;

    Canvas mCanvas;
    Bitmap mBitmap;
    Paint mPaint;

    float lastX;
    float lastY;

    Path mPath = new Path();
    float mCurveEndX;
    float mCurveEndY;

    int mInvalidateExtraBorder = 10;

    static final float TOUCH_TOLERANCE = 8;

    public BestPaintBoard(Context context) {
        super(context);
        init(context);
    }

    public BestPaintBoard(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }
    private void init(Context context){
        mPaint = new Paint();
        mPaint.setAntiAlias(true);
        mPaint.setColor(Color.BLACK);
        mPaint.setStyle(Paint.Style.STROKE);
        mPaint.setStrokeJoin(Paint.Join.ROUND);
        mPaint.setStrokeCap(Paint.Cap.ROUND);
        mPaint.setStrokeWidth(3.0F);

        this.lastX = -1;
        this.lastY = -1;
    }

    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        // ARGB_8888 : 한 pixel을 4byte를 이용해 색 표현
        Bitmap img = Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas();
        canvas.setBitmap(img);
        canvas.drawColor(Color.WHITE);

        mBitmap = img;
        mCanvas = canvas;
    }

    protected void onDraw(Canvas canvas){
        if(mBitmap != null){
            canvas.drawBitmap(mBitmap,0,0,null);
        }
    }

    public boolean onTouchEvent(MotionEvent event){
        int action = event.getAction();
        switch (action){
            case MotionEvent.ACTION_UP:
                changed = true;
                Rect rect = touchUp(event,false);
                if(rect != null){
                    // rect 영역만 다시 그려 성능 향상
                    invalidate(rect);
                }
                mPath.rewind();
                return true;
            case MotionEvent.ACTION_DOWN:
                rect = touchDown(event);
                if(rect != null){
                    invalidate(rect);
                }
                return true;
            case MotionEvent.ACTION_MOVE:
                rect = touchMove(event);
                if(rect != null){
                    invalidate(rect);
                }
                return true;
        }
        return false;
    }

    private Rect touchDown(MotionEvent event){
        float x = event.getX();
        float y = event.getY();

        lastX = x;
        lastY = y;

        Rect mInvalidRect = new Rect();
        mPath.moveTo(x,y);

        final int border = mInvalidateExtraBorder;
        
        mInvalidRect.set((int)x-border,(int)y-border,(int)x+border,(int)y+border);
        mCurveEndX = x;
        mCurveEndY = y;

        mCanvas.drawPath(mPath,mPaint);
        return mInvalidRect;
    }

    private Rect touchMove(MotionEvent event){
        Rect rect = processMove(event);
        return rect;
    }
    private Rect touchUp(MotionEvent event,boolean cancel){
        Rect rect = processMove(event);
        return rect;
    }

    private Rect processMove(MotionEvent event){
        final float x = event.getX();
        final float y = event.getY();

        final float dx = Math.abs(x-lastX);
        final float dy = Math.abs(y-lastY);

        Rect mInvalidRect = new Rect();
        if(dx >= TOUCH_TOLERANCE || dy >= TOUCH_TOLERANCE){
            final int border = mInvalidateExtraBorder;
            mInvalidRect.set((int)mCurveEndX-border,(int)mCurveEndY-border,(int)mCurveEndX+border,(int)mCurveEndY+border);
            float cX = mCurveEndX = (x + lastX) / 2;
            float cY = mCurveEndY = (y + lastY) / 2;

            // 곡선 모양으로 그린다.
            mPath.quadTo(lastX,lastY,cX,cY);

            // 사각형 확장
            mInvalidRect.union((int)lastX - border,(int)lastY - border,(int)lastX + border,(int)lastY+border);
            mInvalidRect.union((int)cX - border,(int)cY-border,(int)cX+border,(int)cY+border);

            lastX = x;
            lastY = y;

            mCanvas.drawPath(mPath,mPaint);
        }
        return mInvalidRect;
    }
}
```

`MainAcitivty`에 `BestPaintBoard` 객체 선언 후 그려준다. 

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        BestPaintBoard view = new BestPaintBoard(this);
        setContentView(view);
    }
}
```

## Conclusion

터치 후 좌표 값이 변경될 때 그려주도록 구현하였고, 이를 좀 더 부드럽게 곡선으로 그려주는 방식의 그림판을 구현하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)