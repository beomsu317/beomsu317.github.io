---
title: System Service
author: Beomsu Lee
category: [Android]
tags: [android, system service]
math: true
mermaid: true
---

## Description

시스템 서비스는 단말이 켜졌을 때 자동으로 실행되어 백그라운드에서 동작한다. 안드로이드에선 다양한 시스템 서비스가 제공된다.

`ActivityManager`는 액티비티나 서비스를 관리하는 시스템 서비스로 앱의 실행상태를 알 수 있도록 한다. `PackageManager`는 앱의 설치에 대한 정보를 알 수 있도록 하고, `AlarmManager`는 일정 시간에 알림을 받을 수 있도록 시스템에 등록해주는 역할을 수행한다. 이외에도 여러 시스템 서비스가 존재한다.

## Implementation

`activity_main.xml`에 5개의 버튼을 추가하고 스크롤뷰에 텍스트뷰를 배치한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">

        <Button
            android:id="@+id/button"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="process list"/>
        <Button
            android:id="@+id/button2"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_marginLeft="5dp"
            android:layout_weight="1"
            android:text="current activity"/>
    </LinearLayout>
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal">

        <Button
            android:id="@+id/button3"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="app list"/>
        <Button
            android:id="@+id/button4"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_marginLeft="5dp"
            android:layout_weight="1"
            android:text="search activity"/>
    </LinearLayout>

    <Button
        android:id="@+id/button5"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="set alarm"/>

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

`MainActivity`에 버튼을 누르면 각각 수행할 코드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    TextView textView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView = findViewById(R.id.textView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getServiceList();
            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getCurrentActivity();
            }
        });

        Button button3 = findViewById(R.id.button3);
        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getAppList();
            }
        });

        Button button4 = findViewById(R.id.button4);
        button4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                findActivity();
            }
        });

        Button button5 = findViewById(R.id.button5);
        button5.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setAlarm();
            }
        });

    }

    public void getServiceList() {
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        // 실행중인 프로세스 확인
        List<ActivityManager.RunningAppProcessInfo> processInfoList = manager.getRunningAppProcesses();

        for (int i = 0; i < processInfoList.size(); i++) {
            ActivityManager.RunningAppProcessInfo info = processInfoList.get(i);
            println("#" + i + " -> " + info.pid + ", " + info.processName);
        }
    }

    public void getCurrentActivity() {
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        // RunningTaskInfo 객체를 확인하며 액티비티 스택에 들어있는 정보 중 가장 최상위 정보를 확인한다.
        List<ActivityManager.RunningTaskInfo> taskList = manager.getRunningTasks(1);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ActivityManager.RunningTaskInfo info = taskList.get(0);
            println("Running Task -> " + info.topActivity.toString());
        }
    }

    public void getAppList() {
        PackageManager manager = getPackageManager();
        // 설치된 앱 반환
        List<ApplicationInfo> appInfoList = manager.getInstalledApplications(PackageManager.GET_META_DATA);

        for (int i = 0; i < appInfoList.size(); i++) {
            ApplicationInfo info = appInfoList.get(i);
            println("#" + i + " -> " + info.loadLabel(manager).toString() + ", " + info.packageName);
        }
    }

    public void findActivity() {
        PackageManager manager = getPackageManager();

        Intent intent = new Intent(this, MainActivity.class);
        // 인텐트 객체로 실행할 액티비티가 존재하는지 확인
        List<ResolveInfo> activityInfoList = manager.queryIntentActivities(intent, 0);

        for (int i = 0; i < activityInfoList.size(); i++) {
            ResolveInfo info = activityInfoList.get(i);
            println("#" + i + " -> " + info.activityInfo.applicationInfo.packageName);
        }
    }

    public void setAlarm() {
        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);

        // 시간이되면 MainActivity 클래스를 실행한다.
        Intent intent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 101, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        // 알람매니저에 등록
        manager.set(AlarmManager.RTC, System.currentTimeMillis() + 5000, pendingIntent);

    }

    public void println(String data) {
        textView.append(data + "\n");
    }
}
```

## Conclusion

버튼을 누를 경우 실행되는 프로세스, 설치된 패키지, 알람 설정 등의 기능을 시스템 서비스를 통해 구현할 수 있는 것을 확인하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
