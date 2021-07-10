---
title: Video Record
author: Beomsu Lee
category: [Android]
tags: [record]
---

## Description

오디오 녹음에 사용한 `MediaRecorder` 객체를 동영상 녹화에도 이용할 수 있다. 오디오 녹음과 다른 점은 카메라 미리보기를 사용할 수 있도록 만들어주어야 한다는 점이다. 

카메라는 `SurfaceView`를 이용해 미리보기를 구현한다. 

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

`activity_main.xml`에서 4개의 버튼(녹화 시작, 녹화 정지, 시작, 정지)과 프레임 레이아웃 하나(동영상 재생시키기 위함)를 배치한다.

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
        android:text="play"/>
    <Button
        android:id="@+id/button4"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="stop"/>

    <FrameLayout
        android:id="@+id/container"
        android:layout_width="match_parent"
        android:layout_height="match_parent"/>
</LinearLayout>
```

`MainActivity`에서 4개 버튼에 대한 수행 코드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    MediaPlayer player;
    MediaRecorder recorder;

    String filename;

    SurfaceHolder holder;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // SurfaceView 객체 생성
        SurfaceView surfaceView = new SurfaceView(this);
        holder = surfaceView.getHolder();
        // 미리보기 화면이 보이도록 설정
        holder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);

        FrameLayout frameLayout = findViewById(R.id.container);
        frameLayout.addView(surfaceView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startRecording();
            }
        });
        Button button2= findViewById(R.id.button2);
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

        String sdcard = Environment.getExternalStorageDirectory().getAbsolutePath();
        filename = sdcard + File.separator + "recorded.mp4";

        ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE,Manifest.permission.READ_EXTERNAL_STORAGE,Manifest.permission.CAMERA,Manifest.permission.RECORD_AUDIO},101);
    }

    public void startRecording(){
        if(recorder == null){
            recorder = new MediaRecorder();
        }
        // 오디오 입력은 마이크
        recorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        // 비디오 입력은 카메라
        recorder.setVideoSource(MediaRecorder.VideoSource.CAMERA);
        recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        // 오디오, 비디오 기본 인코더 설정
        recorder.setAudioEncoder(MediaRecorder.AudioEncoder.DEFAULT);
        recorder.setVideoEncoder(MediaRecorder.VideoEncoder.DEFAULT);
        recorder.setOutputFile(filename);

        // MediaRecorder에 미리보기 화면을 보여줄 객체 설정
        recorder.setPreviewDisplay(holder.getSurface());

        try{
            recorder.prepare();
            recorder.start();
        }catch (Exception e){
            e.printStackTrace();
            recorder.release();
            recorder = null;
        }
    }

    public void stopRecording(){
        if(recorder == null){
            return;
        }

        recorder.stop();
        recorder.reset();
        recorder.release();
        recorder = null;

        // ContentProvider를 이용해 저장
        ContentValues values = new ContentValues(10);
        values.put(MediaStore.MediaColumns.TITLE, "RecordedVideo");
        values.put(MediaStore.Audio.Media.ALBUM, "Video Album");
        values.put(MediaStore.Audio.Media.ARTIST, "Mike");
        values.put(MediaStore.Audio.Media.DISPLAY_NAME, "Recorded Video");
        values.put(MediaStore.MediaColumns.DATE_ADDED, System.currentTimeMillis() / 1000);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4");
        values.put(MediaStore.Audio.Media.DATA, filename);

        Uri videoUri = getContentResolver().insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI,values);
        if(videoUri == null){
            Log.d("MainActivity", "video insert failed");
            return;
        }

        // 미디어 앨범에 저장되었다는 정보를 broadcast
        sendBroadcast(new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE,videoUri));
    }

    public void startPlay(){
        if(player == null){
            player = new MediaPlayer();
        }

        try{
            player.setDataSource(filename);
            // SurfaceHolder 객체 지정
            player.setDisplay(holder);
            player.prepare();
            player.start();
        }catch (Exception e){
            e.printStackTrace();
        }
    }
    public void stopPlay() {
        if (player == null) {
            return;
        }

        player.stop();
        player.release();
        player = null;
    }
}
```

## Conclusion

RECORD START 버튼을 누르면 녹화가 시작되며 STOP을 눌러 저장 후 해당 비디오를 재생할 수 있는 것을 확인하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
