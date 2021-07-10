---
title: Create Animation with Thread
author: Beomsu Lee
category: [Android, Thread]
tags: [android, thread]
math: true
mermaid: true
---

## Description

여러 이미지를 연속해 바꿔가며 애니메이션 효과를 만들고 싶을 때 스레드를 사용하는 경우가 많다. 이번엔 스레드를 이용해 애니메이션 효과를 구현해보자. 

## Implementation

`activity_main.xml`에 이미지뷰와 버튼을 생성한다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <ImageView
        android:id="@+id/imageView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="168dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.498"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:srcCompat="@drawable/face1" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Start"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.498"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/imageView"
        app:layout_constraintVertical_bias="0.267" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

`MainActivity`에선 5개의 그림을 `drawableList`에 넣고 스레드에서 애니메이션이 동작하도록 구현했다.

```java
public class MainActivity extends AppCompatActivity {
    ImageView imageView;

    ArrayList<Drawable> drawableList = new ArrayList<Drawable>();
    Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Resources res = getResources();
        drawableList.add(res.getDrawable(R.drawable.face1));
        drawableList.add(res.getDrawable(R.drawable.face2));
        drawableList.add(res.getDrawable(R.drawable.face3));
        drawableList.add(res.getDrawable(R.drawable.face4));
        drawableList.add(res.getDrawable(R.drawable.face5));

        imageView = findViewById(R.id.imageView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                AnimThread thread = new AnimThread();
                thread.start();
            }
        });
    }

    class AnimThread extends Thread {
        public void run(){
            int index = 0;
            for(int i=0;i<100;i++){
                // drawableList에서 하나 뽑아 drawable에 저장
                final Drawable drawable = drawableList.get(index);
                index += 1;
                if(index > 4){
                    index = 0;
                }
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        // 1초마다 애니메이션 변경
                        imageView.setImageDrawable(drawable);
                    }
                });

                try{
                    Thread.sleep(1000);
                }catch (Exception e){
                    e.printStackTrace();
                }
            }
        }
    }
}
```

## Conclusion

버튼을 누르면 1초마다 변경되는 애니메이션을 확인할 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)