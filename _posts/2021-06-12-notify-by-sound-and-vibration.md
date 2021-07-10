---
title: Notify by Sound and Vibration
author: Beomsu Lee
category: [Android]
tags: [android, sound, vibration]
math: true
mermaid: true
---

## Description

안드로이드에선 진동과 소리를 통해 사용자가 알림을 받을 수 있도록 할 수 있다. 진동은 `Vibrator`라는 시스템 서비스 객체를 이용해 진동이 울리는 패턴이나 시간을 지정할 수 있다. 소리는 `Ringtone` 객체의 `play()` 메서드를 호출해 알려줄 수 있다. 음원 파일을 만들어 재생할 때는 `MediaPlayer` 객체를 사용할 수 있다. 

## Implementation

우선 `AndroidManifest.xml`에 진동 권한을 추가한다.

```xml
<uses-permission android:name="android.permission.VIBRATE"/>
```

`activity_main.xml`에 버튼 3개(진동, 사운드, 파일 사운드)를 배치한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Vibrate"/>
    <Button
        android:id="@+id/button2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Sound"/>
    <Button
        android:id="@+id/button3"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="File Sound"/>

</LinearLayout>
```

`MainActivity`에서 버튼 3개에 대한 코드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Vibrator 객체 참조 
                Vibrator vibrator = (Vibrator)getSystemService(Context.VIBRATOR_SERVICE);
                // API 26 이상 파라미터 변경됨
                if(Build.VERSION.SDK_INT >= 26){
                    vibrator.vibrate(VibrationEffect.createOneShot(1000,10));
                }else{
                    vibrator.vibrate(1000);
                }

            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Uri uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                // Ringtone 객체 참조
                Ringtone ringtone = RingtoneManager.getRingtone(getApplicationContext(),uri);
                ringtone.play();
            }
        });

        Button button3 = findViewById(R.id.button3);
        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                MediaPlayer player = MediaPlayer.create(getApplicationContext(),R.raw.beep);
                player.start();

            }
        });

    }
}
```

## Conclusion

각 버튼을 누르면 해당하는 진동, 사운드가 들리는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
