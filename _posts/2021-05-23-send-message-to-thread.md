---
title: Send Message to Thread 
author: Beomsu Lee
tags: [android]
---

## Description

메인 스레드에서 별도의 스레드로 메시지를 전달하는 방법은 메시지 큐를 이용하는 방법이 있다. 여러 스레드가 접근할 때는 별도의 스레드 안에 들어있는 메시지 큐를 이용해 순서대로 접근하도록 만들어야 한다.

핸들러가 처리하는 메시지 큐는 루퍼(Looper)로 처리되며, 일반적인 이벤트 처리 과정과 유사하다. 루퍼는 메시지 큐에 들어오는 메시지를 지속적으로 확인하며 하나씩 처리한다. 메인 스레드는 객체들을 처리하기 위해 메시지 큐와 루퍼를 사용하지만 별도의 스레드를 새로 만들었을 땐 루퍼가 없다. 따라서 별도의 스레드에 루퍼를 만든 후 실행해야 한다. 

## Implementation

`activity_main.xml`에 `TextView`, `Button`, `EditText` 위젯을 생성한다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        android:textSize="30sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintVertical_bias="0.601" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginBottom="64dp"
        android:text="Send to Thread"
        app:layout_constraintBottom_toTopOf="@+id/textView"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent" />

    <EditText
        android:id="@+id/editText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginBottom="68dp"
        android:ems="10"
        android:inputType="text"
        app:layout_constraintBottom_toTopOf="@+id/button"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.497"
        app:layout_constraintStart_toStartOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

`MainActivity`에 버튼을 누르면 스레드로 메시지를 전달하며, 전달된 메시지는 `EditText`에 보여지도록 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    EditText editText;
    TextView textView;

    Handler handler = new Handler();

    ProcessThread thread;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        editText = findViewById(R.id.editText);
        textView = findViewById(R.id.textView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String input = editText.getText().toString();
                Message message = Message.obtain();
                // 객체를 message.obj에 할당
                message.obj = input;
                // 객체를 스레드로 전달
                thread.processHandler.sendMessage(message);
            }
        });

        thread = new ProcessThread();
    }

    class ProcessThread extends Thread {
        ProcessHandler processHandler = new ProcessHandler();

        public void run(){
            // 루퍼 생성
            Looper.prepare();
            Looper.loop();
        }

        class ProcessHandler extends Handler {
            // 메시지 처리
            public void handleMessage(Message msg){
                final String output = msg.obj + " from thread";
                // TextView에 전달받은 메시지 설정
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        textView.setText(output);
                    }
                });
            }
        }
    }
}
```

## Conclusion

입력 상자에 문자열 입력 후 버튼을 누르면 서브 스레드로 메시지가 전달되며 전달된 데이터를 `TextView`에 설정되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)