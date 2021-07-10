---
title: Notification
author: Beomsu Lee
category: [Android]
tags: [android, notification]
math: true
mermaid: true
---

## Description

`Notification`은 화면 상단에 정보를 표시하여 사용자가 알 수 있도록 해주는 기능이다. 이 알림은 주로 상대방에게서 메시지를 받거나 단말의 상태를 표시할 때 사용한다. 

알림은 `NotificationManager` 시스템 서비스를 이용해 화면 상단에 띄울 수 있다. 알림을 띄우려면 `Notification` 객체를 만들어야 하는데, 이 객체는 `NotificationCompat.Builder` 객체를 이용해 생성한다. 

## Implementation

`activity_main.xml`에 버튼 하나를 추가한다. 이 버튼을 누르면 알림이 오고, 알림을 누르면 `MainActivity` 액티비티가 실행된다.

```java
public class MainActivity extends AppCompatActivity {
    NotificationManager manager;

    private static String CHANNEL_ID = "channel";
    private static String CHANNEL_NAME = "Channel";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showNoti();
            }
        });
    }

    public void showNoti(){
        manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        NotificationCompat.Builder builder = null;
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){
            if(manager.getNotificationChannel(CHANNEL_ID) == null){
                manager.createNotificationChannel(new NotificationChannel(CHANNEL_ID,CHANNEL_NAME,NotificationManager.IMPORTANCE_DEFAULT));
            }
            builder = new NotificationCompat.Builder(this,CHANNEL_ID);
        }else{
            builder = new NotificationCompat.Builder(this);
        }

        Intent intent = new Intent(this, MainActivity.class);
        // PendingIntent는 Intent와 유사하지만 시스템에서 대기하며, 원하는 상황에 해석되고 처리된다.
        PendingIntent pendingIntent = PendingIntent.getActivity(this,101,intent,PendingIntent.FLAG_UPDATE_CURRENT);
        builder.setContentTitle("Simple Noti");
        builder.setContentText("Noti Message");
        builder.setSmallIcon(android.R.drawable.ic_menu_view);
        // 알림을 클릭했을 때 자동으로 알림 삭제
        builder.setAutoCancel(true);
        // PendingIntent 객체 설정
        builder.setContentIntent(pendingIntent);
        Notification noti = builder.build();
        manager.notify(1,noti);
    }
}
```

이외에도 Styled Notification을 이용해 글자를 많이 표시하거나, 큰 사진을 보여주는 알림을 설정할 수 있다.

## Conclusion

버튼을 누르면 상단에 알림이 오고 알림 메시지를 클릭할 경우 해당 액티비티로 이동하는 것을 확인할 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
