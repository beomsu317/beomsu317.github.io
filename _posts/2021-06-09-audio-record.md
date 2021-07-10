---
title: Audio Record
author: Beomsu Lee
category: [Android, Audio]
tags: [android, audio]
math: true
mermaid: true
---

## Description

오디오 녹음이나 동영상 녹화를 위해서는 `MediaRecorder`가 사용된다. 다음 과정을 거쳐 음성을 녹음할 수 있다.

1. 매니페스트에 권한 설정
1. `MediaRecorder` 객체 생성
1. 오디오 입력 및 출력 형식 설정
1. 오디오 인코더와 파일 지정
1. 녹음 시작

## Implementation

SD 카드에 저장하기 위해 `AndroidManifest.xml`에 권한을 추가한다. `application` 태그에 `requestLegacyExternalStorage` 속성을 참으로 주어야 SD 카드에 저장이 가능하다.

```xml
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<application
    ...
    android:requestLegacyExternalStorage="true">
```

`activity_main.xml`에 4개의 버튼(녹음 시작, 녹음 정지, 녹음 재생, 녹음 중지)을 배치한다.

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
        android:id="@+id/buttton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="record start"/>

    <Button
        android:id="@+id/button2"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="record stop"/>

    <Button
        android:id="@+id/button3"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Play"/>

    <Button
        android:id="@+id/button4"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="stop"/>

</LinearLayout>
```

`MainActivity`에 4개 버튼에 해당하는 코드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    MediaRecorder recorder;
    MediaPlayer player;

    String filename;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.buttton);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startRecording();
            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopRecording();
            }
        });

        Button button3 = findViewById(R.id.button3);
        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startPlay();
            }
        });

        Button button4 = findViewById(R.id.button4);
        button4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopPlay();
            }
        });

        ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.READ_EXTERNAL_STORAGE,Manifest.permission.WRITE_EXTERNAL_STORAGE,Manifest.permission.RECORD_AUDIO},101);

        // API 30 이상인 경우 SD 카드 접근 권한 문제 발생
        String sdcard = Environment.getExternalStorageDirectory().getAbsolutePath();
        filename = sdcard + File.separator + "recorded.mp4";
    }

    public void startRecording(){
        if(recorder == null){
            recorder = new MediaRecorder();
        }
        // MediaRecorder 설정
        recorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        // 포맷 지정
        recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        // 기본 인코더 사용
        recorder.setAudioEncoder(MediaRecorder.AudioEncoder.DEFAULT);
        recorder.setOutputFile(filename);

        try {
            // MediaRecorder 시작
            recorder.prepare();
            recorder.start();
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public void stopRecording(){
        if(recorder == null){
            return;
        }
        // MediaRecorder 리소스 해제
        recorder.stop();
        recorder.release();
        recorder = null;

        ContentValues values = new ContentValues(10);
        values.put(MediaStore.MediaColumns.TITLE,"Recorded");
        values.put(MediaStore.Audio.Media.ALBUM,"Audio Album");
        values.put(MediaStore.Audio.Media.ARTIST,"Mike");
        values.put(MediaStore.Audio.Media.DISPLAY_NAME,"Recorded Audio");
        values.put(MediaStore.Audio.Media.IS_RINGTONE,1);
        values.put(MediaStore.Audio.Media.IS_MUSIC,1);
        values.put(MediaStore.MediaColumns.DATE_ADDED,System.currentTimeMillis()/1000);
        // 미디어 파일 포맷
        values.put(MediaStore.MediaColumns.MIME_TYPE,"audio/mp4");
        // MediaStore.Audio.Media.DATA은 저장된 녹음 파일을 의미
        values.put(MediaStore.Audio.Media.DATA,filename);

        // ContentResolver의 insert 메서드 사용해 저장
        Uri audioUri = getContentResolver().insert(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,values);
        if(audioUri == null){
            Log.d("MainActivity", "Audio insert failed");
            return;
        }
    }


    public void startPlay() {
        killMediaPlayer();

        try {
            player = new MediaPlayer();
            player.setDataSource("file://" + filename);
            player.prepare();
            player.start();
        } catch(Exception e) {
            e.printStackTrace();
        }
    }

    public void stopPlay() {
        if (player != null) {
            player.stop();
        }
    }

    private void killMediaPlayer() {
        if (player != null) {
            try {
                player.release();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
```

## Conclusion

RECORD START 버튼을 누를 경우 녹음이 시작되며 RECORD STOP 버튼을 누르면 녹음이 종료되고 리소스가 해제된 후 SD 카드 위치에 저장된다. PLAY 버튼을 누르면 녹음된 파일이 재생되며 STOP을 누를 경우 정지되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
