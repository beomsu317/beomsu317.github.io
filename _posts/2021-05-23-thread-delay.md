---
title: Thread Delay
author: Beomsu Lee
category: [Android, Thread]
tags: [android, thread]
math: true
mermaid: true
---

## Description

웹 서버에 요청 후 응답이 늦어질 경우 앱이 대기하는 문제가 생길 수 있다. 이런 경우 별도의 스레드를 만들어 처리하면 된다. 핸들러로 지연 시간을 주었을 때 핸들러로 실행되는 코드는 메시지 큐를 통과하면서 순차적으로 실행되기 때문에 UI 객체들에 영향을 주지 않으면서 지연 시간을 두고 실행된다. 

## Implementation

`activity_main.xml`에 `Button`과 `TextView`를 하나씩 추가한다.

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
        android:text="Request"
        android:textSize="30sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintVertical_bias="0.359" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="76dp"
        android:text="Button"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintHorizontal_bias="0.498"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/textView" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

`MainActivity`에 요청하는 `Dialog`를 띄우고 `Yes`를 눌렀을 경우 스레드를 5초뒤에 수행하도록 한다. 만약 시간을 지정하고 싶다면 `postAtTime()` 메서드를 사용하면 된다.

```java
public class MainActivity extends AppCompatActivity {
    TextView textView;
    Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView = findViewById(R.id.textView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                request();
            }
        });
    }

    private void request(){
        String title = "Remote Request";
        String message = "Data Request?";
        String titleButtonYes = "YES";
        String titleButtonNo = "NO";
        AlertDialog dialog = makeRequestDialog(title,message,titleButtonYes,titleButtonNo);
        dialog.show();

        textView.setText("Dialog showing...");
    }

    private AlertDialog makeRequestDialog(CharSequence title, CharSequence message, CharSequence titleButtonYes,CharSequence titleButtonNo){
        AlertDialog.Builder requestDialog = new AlertDialog.Builder(this);
        requestDialog.setTitle(title);
        requestDialog.setMessage(message);
        requestDialog.setPositiveButton(titleButtonYes, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                textView.setText("Result Represented in 5 Seconds");
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        textView.setText("Requst Done");
                    }
                },5000);
            }
        });

        requestDialog.setNegativeButton(titleButtonNo, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                textView.setText("Request");

            }
        });

        return requestDialog.create();
    }
}
```

## Conclusion

버튼을 눌렀을 경우 요청이 시작되며 5초 후 요청이 완료되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)