---
title: Video Player
author: Beomsu Lee
category: [Android]
tags: [widget]
---

## Description

동영상 재생 기능은 오디오 파일 재생과 같이 간단하게 구현할 수 있다. 동영상을 재생하기 위해 `VideoView` 위젯을 사용하면 된다. 

만약 동영상을 좀 더 세밀하게 제어하고 싶다면 `MediaPlayer`를 사용하면 된다.

## Implementation

우선 `AndriodManifest.xml`의 INTERNET 권한을 추가한다.

```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

그리고 `activity_main.xml`에 버튼 하나와 비디오뷰를 배치한다.

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
        android:text="Play"/>

    <VideoView
        android:id="@+id/videoView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</LinearLayout>
```

`MainActivity`에서 `MediaController` 설정 후 버튼이 눌렸을 경우 동영상이 재생되도록 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    public static final String VIDEO_URL = "https://sites.google.com/site/ubiaccessmobile/sample_video.mp4";
    VideoView videoView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        videoView = findViewById(R.id.videoView);

        MediaController mc = new MediaController(this);
        // MediaController 설정
        videoView.setMediaController(mc);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // 재생할 대상 설정 후 재생
                videoView.setVideoURI(Uri.parse(VIDEO_URL));
                videoView.requestFocus();
                videoView.start();
            }
        });
    }
}
```


## Conclusion

버튼을 누르면 동영상이 재생되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
