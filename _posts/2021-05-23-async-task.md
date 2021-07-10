---
title: Async Task
author: Beomsu Lee
category: [Android]
tags: [android, asynctask]
math: true
mermaid: true
---

## Description

`AsyncTask` 클래스를 상속해 새로운 클래스를 만들면 그 안에 스레드를 위한 코드와 UI 객체 접근 코드를 같이 사용할 수 있다. 즉, 정의된 백그라운드 작업을 수행하고 필요한 경우 그 결과를 메인 스레드에서 실행하므로 UI 객체에 접근이 가능하다.

`AsyncTask` 클래스의 `doInBackground()` 메서드는 새로 만들어진 스레드에서 실행되어야 할 코드를 넣고, `onPreExecute()`, `onProgressUpdate()`, `onPostExecute()` 메서드는 메인 스레드에서 실행되어질 코드를 넣는다. `onProgressUpdate()` 메서드의 경우 스레드 작업 수행 중간에 UI 객체에 접근해야 하는 경우에 쓰이는데 백그라운드 작업 중간에 `publishProgress()` 메서드를 호출해줘야 한다.

`AsyncTask` 클래스의 `cancel()` 메서드를 호출하면 작업이 취소된다. 

`AsyncTask` 클래스의 `getStatus()` 메서드를 사용하면 `AsyncTask`의 상태를 알 수 있다.(`PENDING`, `RUNNING`, `FINISHED`)

## Implementation

`activity_main.xml`에 프로그레스바와 버튼 2개를 생성한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <ProgressBar
        android:id="@+id/progressBar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Start" />

    <Button
        android:id="@+id/button2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Cancel" />
</LinearLayout>
```

`MainActivity`에 "Start" 버튼을 누르면 스레드를 실행시키며, "Cancel" 버튼을 누르면 취소하는 코드를 작성한다.

```java
public class MainActivity extends AppCompatActivity {
    BackgroundTask task;
    int value;

    ProgressBar progressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        progressBar = findViewById(R.id.progressBar);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 스레드 작업 시작
                task = new BackgroundTask();
                task.execute();
            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 스레드 작업 취소
                task.cancel(true);
            }
        });
    }
    /* 
    AsyncTask<Integer, Integer, Integer>의 
    1번째 Integer는 doInBackground()의 인자의 자료형을, 
    2번째 Integer는 onProgressUpdate()의 인자의 자료형을, 
    3번째 Integer는 onPostExecute()의 인자의 자료형을 명시
    */
    class BackgroundTask extends AsyncTask<Integer, Integer, Integer> {
        protected void onPreExecute(){
            value = 0;
            progressBar.setProgress(value);
        }

        protected Integer doInBackground(Integer... integers) {
            // 취소되지 않았을 경우 value를 1씩 증가시켜 즉시 반영한다.
            while(isCancelled() == false){
                value++;
                if(value >= 100){
                    break;
                }else{
                    publishProgress(value);
                }

                try{
                    Thread.sleep(100);
                }catch (InterruptedException e){}
            }
            return value;
        }

        // publishProgress()가 호출되었을 때 실행
        protected void onProgressUpdate(Integer... values) {
            progressBar.setProgress(values[0].intValue());
        }

        protected void onPostExecute(Integer integer) {
            progressBar.setProgress(0);
        }

        protected void onCancelled() {
            progressBar.setProgress(0);
        }
    }
}
```

## Conclusion

"Start" 버튼을 누르면 스레드에서 100밀리 초마다 프로그레스바를 1씩 증가시키며 "Cancel" 또는 `value`가 100 이상인 경우 스레드를 종료시키는 것을 확인할 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)