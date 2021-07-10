---
title: Broadcast Receiver
author: Beomsu Lee
category: [Android, Component]
tags: [android, component, broadcast receiver]
math: true
mermaid: true
---

## Description

브로드캐스트 리시버는 애플리케이션에 메시지를 전달할 때 사용하는 구성 요소이다. 자신이 만든 앱에 메시지를 받고 싶다면 `Broadcast Receiver`를 만들어 앱에 등록하면 된다. 앱의 구성 요소이므로 `AndroidManifest.xml`에 등록해주어야 한다.

`Broadcast Recevier`에는 `onReceive()` 함수가 필요하다. 이 함수는 메시지가 전달되면 자동으로 호출된다. 원하는 메시지를 받으려면 인텐트 필터를 통해 시스템에 등록하면 된다.

## Implementation


SMS 메시지가 들어간 인텐트를 구분하기 위한 액션 정보를 `AndroidManifest.xml`에 등록해준다. SMS를 수신했을 때 이 액션 정보가 들어간 인텐트를 전달하게 된다. 

```xml
<receiver
    android:name=".SmsReceiver"
    android:enabled="true"
    android:exported="true">
    <intent-filter>
        <action android:name="android.provider.Telephony.SMS_RECEIVED"/>
    </intent-filter>
</receiver>
```

앱에서 SMS를 받기 위해선 권한이 필요하며 이 예제에선 라이브러리 [AutoPermissions](https://github.com/pedroSG94/AutoPermissions)을 사용할 것이다. `build.gradle`를 열어 다음과 같이 수정한다.

```gradle
allprojects {
    repositories {
        maven { url 'https://jitpack.io' }
    }
}

dependencies {
    ...
    implementation 'com.github.pedroSG94:AutoPermissions:1.0.3'
}
```

AndroidManifest.xml 파일에 SMS 권한을 추가한다.

```xml
<uses-permission android:name="android.permission.RECEIVE_SMS" />
```

`SmsReceiver` 클래스에선 메시지를 받았을 경우 로그 출력 및 `SmsActivity`로 인텐트를 전달해 실행시켜 주는 코드를 작성한다.

```java
public class SmsReceiver extends BroadcastReceiver {
    private static final String TAG = "SmsReceiver";

    public SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.i(TAG, "onReceive() 메서드 호출됨.");

        Bundle bundle = intent.getExtras();
        SmsMessage[] messages = parseSmsMessage(bundle);
        if (messages != null && messages.length > 0) {
            String sender = messages[0].getOriginatingAddress();
            Log.i(TAG, "SMS sender : " + sender);

            String contents = messages[0].getMessageBody();
            Log.i(TAG, "SMS contents : " + contents);

            Date receivedDate = new Date(messages[0].getTimestampMillis());
            Log.i(TAG, "SMS received date : " + receivedDate.toString());

            sendToActivity(context, sender, contents, receivedDate);
        }
    }

    private SmsMessage[] parseSmsMessage(Bundle bundle) {
        Object[] objs = (Object[]) bundle.get("pdus");

        SmsMessage[] messages = new SmsMessage[objs.length];
        int smsCount = objs.length;
        for (int i = 0; i < smsCount; i++) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                String format = bundle.getString("format");
                messages[i] = SmsMessage.createFromPdu((byte[]) objs[i], format);
            } else {
                messages[i] = SmsMessage.createFromPdu((byte[]) objs[i]);
            }
        }

        return messages;
    }

    private void sendToActivity(Context context, String sender, String contents, Date receivedDate) {
        Intent myIntent = new Intent(context, SmsActivity.class);
        /* 
        FLAG_ACTIVITY_NEW_TASK : 새로운 태스크 생성 (SmsReceiver는 화면이 없음)
        FLAG_ACTIVITY_SINGLE_TOP : 메모리에 있는 경우 재실행되지 않음
        FLAG_ACTIVITY_CLEAR_TOP : 메모리에 있는 경우 포그라운드로 가져옴
        */
        myIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_SINGLE_TOP|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        myIntent.putExtra("sender", sender);
        myIntent.putExtra("contents", contents);
        myIntent.putExtra("receivedDate", format.format(receivedDate));
        context.startActivity(myIntent);
    }
}
```

`SmsActivity` 클래스는 전달받은 데이터들을 `EditText`에 띄워주며 버튼 클릭 시 돌아가는 역할을 수행한다.

```java
public class SmsActivity extends AppCompatActivity {
    EditText editText;
    EditText editText2;
    EditText editText3;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sms);

        editText = findViewById(R.id.editText);
        editText2 = findViewById(R.id.editText2);
        editText3 = findViewById(R.id.editText3);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                finish();
            }
        });

        Intent passedIntent = getIntent();
        processIntent(passedIntent);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        processIntent(intent);

        super.onNewIntent(intent);
    }

    private void processIntent(Intent intent) {
        if (intent != null) {
            String sender = intent.getStringExtra("sender");
            String contents = intent.getStringExtra("contents");
            String receivedDate = intent.getStringExtra("receivedDate");

            editText.setText(sender);
            editText2.setText(contents);
            editText3.setText(receivedDate);
        }
    }

}
```

## Conclusion

브로드캐스트 리시버를 통해 데이터를 SMS를 전달받고 해당 메시지를 출력해주는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)