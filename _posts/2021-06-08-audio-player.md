---
title: Music Player
author: Beomsu Lee
tags: [android]
---

## Description

멀티미디어를 제공하기 위한 미디어 API는 `android.media` 패키지에 들어있다. 그 중 `MediaPlayer` 클래스는 음악 파일과 같은 오디오의 재생, 동영상 재생을 담당한다. 단말에 따라 지원되는 음성/영상 코덱이 다르므로 재생할 수 있는 파일의 종류가 다를 수 있지만 기본적으로 제공되는 코덱만으로 오디오와 동영상을 재생할 수 있다. 오디오 파일을 재생하려면 대상을 지정해야 하는데 데이터 소스 지정 방법은 3가지로 나눌 수 있다.

|Location|Description|
|:---:|:---|
|인터넷|미디어가 있는 위치를 URL로 지정|
|프로젝트|리소스 또는 에셋 폴더에 넣은 후 지정|
|단말 SD 카드|SD 카드에 파일을 넣은 후 지정|

음악 파일을 재생하는 과정을 다음과 같다. 첫 번째 단계는 대상 파일을 알려줌으로써 `setDataSource()` 메서드로 URL을 지정한다. 두 번째 단계는 `prepare()` 메서드를 호출해 재생을 준비한다. 이 단계에서 `MediaPlayer`는 대상 파일 몇 프레임을 읽어 정보를 확인한다. 세 번째 단계에서는 음악 파일을 재생한다.

```plantuml!
MediaPlayer --> File : 데이터 소스 지정
MediaPlayer --> MediaPlayer : prepare()
MediaPlayer --> MediaPlayer : start()
```

`MediaPlayer`의 `stop()` 메서드로 재생을 중지했을 때 다른 작업을 수행하고 싶다면 `MediaPlayer.OnCompletionListener`를 구현한 후 `MediaPlayer` 객체에 등록하면 된다.

## Implementation

먼저 `AndroidManifest.xml`에 `INTERNET` 권한과 `usesCleartextTraffic` 속성을 설정한다.

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<application
    ...
    android:usesCleartextTraffic="true">
</application>
```

그리고 `activity_main.xml`에 재생, 정지, 일시정지, 재시작 할 수 있는 버튼 4개를 배치한다.

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
        android:text="play"/>

    <Button
        android:id="@+id/button2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="stop"/>
    <Button
        android:id="@+id/button3"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="pause"/>
    <Button
        android:id="@+id/button4"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="replay"/>

</LinearLayout>
```

`MediaPlayer` 객체 생성 후 각 버튼마다 수행할 코드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    public static final String AUDIO_URL = "http://www.all-birds.com/Sound/western%20bluebird.wav";

    MediaPlayer mediaPlayer;
    int position;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                playAudio(AUDIO_URL);
                Toast.makeText(MainActivity.this, "Music Start", Toast.LENGTH_SHORT).show();

            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mediaPlayer.stop();
            }
        });

        Button button3 = findViewById(R.id.button3);
        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 현재 position 저장
                position = mediaPlayer.getCurrentPosition();
                mediaPlayer.pause();

            }
        });

        Button button4 = findViewById(R.id.button4);
        button4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mediaPlayer.start();
                // 저장된 position 부터 시작
                mediaPlayer.seekTo(position);
                Toast.makeText(MainActivity.this, "Music Restart", Toast.LENGTH_SHORT).show();

            }
        });
    }

    private void playAudio(String url){
        // 앱 내에서 MediaPlayer를 재사용할 경우 기존에 사용하던 리소스를 먼저 해제해야 한다.
        killMediaPlayer();
        try{
            mediaPlayer = new MediaPlayer();
            mediaPlayer.setDataSource(url);
            mediaPlayer.prepare();
            mediaPlayer.start();
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        killMediaPlayer();
    }
    
    // MediaPlayer 객체가 이미 리소스를 사용하고 있을 경우 리소스를 해제
    private void killMediaPlayer(){
        if(mediaPlayer != null){
            try{
                mediaPlayer.release();
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }
}
```

## Conclusion

`MediaPlayer` 객체를 이용해 간단히 오디오 재생을 수행할 수 있는 것을 확인하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
