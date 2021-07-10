---
title: Thread Handler
author: Beomsu Lee
tags: [android]
---

## Description

스레드는 동시 수행이 가능한 작업 단위이며, 현재 수행 중인 작업 이외의 기능을 동시에 처리할 때 새로운 스레드를 만들어 처리한다. 만약 지연 시간이 길어질 수 있는 기능이면 스레드로 분리한 다음 UI에 응답을 보내는 방식을 사용한다. 

안드로이드에서 UI를 처리할 때 사용하는 기본 스레드를 **메인 스레드**라 한다. 메인 스레드에서 이미 UI에 접근하고 있으므로 다른 스레드에선 핸들러(Handler) 객체를 통해 메시지를 전달해 메인 스레드에서 처리할 수 있도록 만든다. 

## Thread Implementation

`activity_main.xml`에 버튼 하나를 만들고 해당 버튼이 클릭될 경우 스레드가 실행될 수 있도록 `MainActivity`를 작성한다. 만약 생성된 새로운 스레드에서 UI 객체를 직접 접근할 경우 에러가 발생하기 때문에 메시지큐(Message Queue)를 이용해 데이터를 전달한다.

```java
public class MainActivity extends AppCompatActivity {
    int value = 0;
    TextView textView;
    MainHandler handler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView = findViewById(R.id.textView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 스레드 시작
                BackgroundThread thread = new BackgroundThread();
                thread.start();
            }
        });
        handler = new MainHandler();
    }

    class BackgroundThread extends Thread {
        public void run(){
            for(int i=0;i<100;i++){
                try{
                    Thread.sleep(1000);
                }catch (Exception e){}
                value += 1;
                Log.d("Thread", "run: " + value);

                // 메시지 객체 얻고
                Message message = handler.obtainMessage();
                Bundle bundle = new Bundle();
                bundle.putInt("value",value);
                message.setData(bundle);

                // 메시지 큐에 넣는다.
                handler.sendMessage(message);
            }
        }
    }

    class MainHandler extends Handler {
        @Override
        public void handleMessage(@NonNull Message msg) {
            super.handleMessage(msg);
            // 전달된 메시지 처리
            Bundle bundle = msg.getData();
            int value = bundle.getInt("value");
            textView.setText("value : " + value);
        }
    }
}
```

## Runnable Implementation

위의 방식대로 구현한다면 코드가 복잡하게 보이는 단점이 있다. 핸들러 `Runnable` 객체를 실행시킬 수 있는 방법을 제공한다. `Runnable` 객체의 `post()`로 전달하면 이 객체에 정의된 `run()` 메서드 안의 코드는 메인 스레드에서 실행된다.

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
                BackgroundThread thread = new BackgroundThread();
                thread.start();
            }
        });
    }
    class BackgroundThread extends Thread {
        int value=0;
        public void run(){
            for(int i=0;i<100;i++){
                try{
                    Thread.sleep(1000);
                }catch (Exception e){}
                value += 1;
                Log.d("Thread", "run: " + value);

                // 코드가 스레드 안에 있으므로 이해하기 쉽다.
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        textView.setText("value : " + value);
                    }
                });
            }
        }
    }

}
```

## Conclusion

버튼을 누르면 스레드가 생성되며 1초마다 `value` 값을 증가시켜 `TextView`에 나타나는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)