---
title: Http Connection
author: Beomsu Lee
category: [Android]
tags: [android, http]
math: true
mermaid: true
---

## Description

HTTP로 웹서버에 접근하기 위해 자바의 방식을 그대로 사용할 수 있다. `URL` 객체를 만들고 이 객체의 `openConnection()` 메서드를 사용해 `HttpURLConnection` 객체를 만들어 요청한다. 

`setRequestMethod()` 메서드를 이용해 요청 방식(GET, POST)을 설정할 수 있고, `setRequestProperty()`를 통해 헤더에 들어갈 필드 값을 지정한다.

## Implementation

인터넷을 사용하기 위해 `AndroidManifest.xml`에서 퍼미션 설정을 해준다. 안드로이드 9(API 28)부터 네트워크 보안이 강화되어 HTTPS가 아닌 경우 접속을 제한하는데 HTTP 접속이 가능하도록 하기 위해 `usesCleartextTraffic`를 `true`로 준다. 

```xml
...
<uses-permission android:name="android.permission.INTERNET"/>
<application
    ... 
    android:usesCleartextTraffic="true">
```

`activity_main.xml`에 입력 상자, 버튼, 스크롤뷰 안에 텍스트뷰를 추가한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <EditText
        android:id="@+id/editText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"/>
    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Request"/>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        <TextView
            android:id="@+id/textView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"/>
    </ScrollView>

</LinearLayout>
```

`MainActivity`에선 버튼을 누르면 입력 상자에 입력된 URL로 접근하도록 작성한다.

```java
public class MainActivity extends AppCompatActivity {
    EditText editText;
    TextView textView;

    Handler handler = new Handler();

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
                final String urlStr = editText.getText().toString();
                // 스레드를 사용해 요청
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        request(urlStr);
                    }
                }).start();
            }
        });
    }

    public void request(String urlStr){
        StringBuilder output = new StringBuilder();
        try{
            URL url = new URL(urlStr);
            // HttpURLConnection 객체 생성
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            if (conn != null) {
                conn.setConnectTimeout(10000);
                conn.setRequestMethod("GET");
                // 서버와의 통신에서 입력 가능한 상태로 설정
                conn.setDoInput(true);

                int resCode = conn.getResponseCode();
                // HttpURLConnection 객체의 스트림을 BufferedReader 객체를 통해 처리
                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                String line = null;
                while(true){
                    line = reader.readLine();
                    if (line == null) {
                        break;
                    }
                    output.append(line + "\n");
                }
                reader.close();
                conn.disconnect();
            }

        }catch (Exception e){
            e.printStackTrace();
        }

        handler.post(new Runnable() {
            @Override
            public void run() {
                textView.append(output);
            }
        });

    }
}
```

## Conclusion

입력 상자에 입력된 URL로 접근하여 받은 응답을 화면에 출력하게 된다. 

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)