---
title: Play YouTube Video
author: Beomsu Lee
tags: [android]
---

## Description

유투브는 동영상을 재생할 수 있는 API를 제공한다. 이 API를 이용해 동영상 재생 및 녹화를 진행할 수 있다. 

## Implementation


API를 사용하기 위해 [Player API](https://developers.google.com/youtube/android/player/downloads)에 접속해 YouTubeAndroidPlayerApi.zip을 다운 및 압축 해제 후 libs 폴더에 있는 YouTubeAndroidPlayerApi.jar 파일을 `app/libs` 폴더로 옮긴다. 

File -> Project Structure -> Dependencies -> Declared Dependencies -> + -> JAR/AAR Dependency 에서 다운받은 YouTubeAndroidPlayerApi.jar을 선택하고 Apply 한다.

`AndroidManifest.xml` 에 INTERNET 권한을 추가하여 인터넷으로 접근 가능하도록 설정한다.

```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

`activity_main.xml`에 버튼 하나와 `YouTubePlayerView` 하나를 배치한다.

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
        android:text="start"/>

    <com.google.android.youtube.player.YouTubePlayerView
        android:id="@+id/playerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"/>

</LinearLayout>
```

`MainActivity`에서 버튼을 누르면 `videoId` 동영상이 재생되도록 구현한다.

```java
public class MainActivity extends YouTubeBaseActivity {
    YouTubePlayerView playerView;
    YouTubePlayer player;

    private static String API_KEY = "API KEY";
    private static String videoId = "7n9D8ZeOQv0";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initPlayer();

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                playVideo();
            }
        });

    }

    public void initPlayer() {
        playerView = findViewById(R.id.playerView);

        // YouTubePlayerView 초기화
        playerView.initialize(API_KEY, new YouTubePlayer.OnInitializedListener() {
            @Override
            public void onInitializationSuccess(YouTubePlayer.Provider provider, YouTubePlayer youTubePlayer, boolean b) {
                player = youTubePlayer;

                player.setPlayerStateChangeListener(new YouTubePlayer.PlayerStateChangeListener() {
                    @Override
                    public void onLoading() {}

                    @Override
                    public void onLoaded(String id) {
                        Log.d("PlayerView", "onLoaded called : " + id);

                        // 동영상이 로딩되었으면 재생
                        player.play();
                    }

                    @Override
                    public void onAdStarted() {}

                    @Override
                    public void onVideoStarted() {}

                    @Override
                    public void onVideoEnded() {}

                    @Override
                    public void onError(YouTubePlayer.ErrorReason errorReason) {}
                });

            }

            @Override
            public void onInitializationFailure(YouTubePlayer.Provider provider, YouTubeInitializationResult youTubeInitializationResult) {

            }

        });
    }

    public void playVideo() {
        if (player != null) {
            if (player.isPlaying()) {
                player.pause();
            }

            // videoId 전달
            player.cueVideo(videoId);
        }
    }
}
```

## Conclusion

앱이 시작되면 API 키를 전달해 `YouTubePlayerView`를 초기화하고, 버튼을 누르면 `videoId`를 전달해 로딩이 끝나면 동영상이 재생되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
