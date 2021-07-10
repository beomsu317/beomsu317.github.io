---
title: Keypad Control
author: Beomsu Lee
category: [Android]
tags: [android, keypad]
math: true
mermaid: true
---

## Description

`EditText`로 만든 입력상자에 포커스를 두게 되면 화면 아래쪽에 소프트 키패드가 생겨 입력할 수 있는 상태가 된다. 소프트 키패드는 자동으로 열고 닫히므로 별도의 코딩이 필요없지만 필요 시 코드를 통해 직접 키패드를 열거나 닫을 수 있다.

키패드와 관련된 기능은 `InputMethodManager` 객체로 사용할 수 있는데 이 객체는 시스템 서비스이므로 `getSystemService()` 메서드로 참조한 후 사용해야 한다. `showSoftInput()`, `hideSoftInputFromWindow()` 메서드를 통해 키패드를 나오도록 하거나 들어가게 할 수 있다.

## Implementation

`activity_main.xml`에 입력 상자와 버튼 하나를 생성한다. 버튼을 누르면 키패드가 들어가도록 구현할 것이다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">


    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginBottom="23dp"
        android:text="Close keypad"
        app:layout_constraintBottom_toTopOf="@+id/editText"
        app:layout_constraintEnd_toEndOf="@+id/editText"
        app:layout_constraintStart_toStartOf="@+id/editText" />

    <EditText
        android:id="@+id/editText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:ems="10"
        android:inputType="number"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

`MainActivity`에서는 버튼이 눌렸을 경우 `InputMethodManager`를 통해 키패드가 들어가도록 설정한다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(getCurrentFocus() != null){
                    InputMethodManager inputMethodManager = (InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);
                    inputMethodManager.hideSoftInputFromWindow(getCurrentFocus().getWindowToken(),0);
                }
            }
        });
    }
}
```

참고로 `AndroidManifest.xml`에서 Activity의 `windowSoftInputMode` 속성을 다음과 같이 설정하면 키패드가 올라온 화면에 맞게 조정된다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.samplekeypad">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.SampleKeypad">
        <activity android:name=".MainActivity"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />

                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

## Conclusion

입력상자에 포커싱되면 키패드가 올라오며 버튼을 누르면 키패드가 다시 내려가는 것을 확인할 수 있다.

##### Resources
- [Keyboard Input Style](https://developer.android.com/training/keyboard-input/style?hl=ko)
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)