---
title: App Widget
author: Beomsu Lee
category: [Android]
tags: [app widget]
math: true
mermaid: true
---

## Description

앱 위젯은 안드로이드 단말의 홈 화면에서 위젯을 바로 보여주고 싶을 때 사용하는 것이다. 홈 화면을 길게 누르면 위젯을 추가할 수 있는 화면이 표시된다. 

앱 위젯은 다른 앱 안에 들어갈 수 있도록 만들어져 있으며 일반적인 앱들과는 달라 결과 화면만을 보여준다. 이러한 특징 때문에 앱 위젯은 다음과 같은 2가지로 구성된다.

- 앱 위젯 호스트
- 앱 위젯 제공자 

즉, 앱 위젯 제공자가 앱 위젯 호스트 안에서 위젯을 보여준다는 의미이다. 이런 앱 위젯을 구성할 때 필요한 요소는 다음 3가지가 있다.

- 위젯을 초기 뷰 레이아웃 : 앱 위젯이 처음에 화면에 나타날 때 필요한 레이아웃 정의
- 앱 위젯 제공자 Info 객체 : 앱 위젯을 위한 메타데이터와 앱 위젯 제공자 클래스에 대한 정보를 가지고 있음
- 앱 위젯 제공자 : 앱 위젯과 정보를 주고받기 위한 기본 클래스

앱 위젯으로 만든 뷰는 주기적으로 업데이트 될 수 있는데, 앱 위젯 제공자의 `onUpdate()` 메서드가 호출된다. 위젯을 바꾸고 싶은 경우 앱 위젯 매니저를 통해 업데이트 할 수 있다.

앱 위젯으로 나타날 뷰 모양은 일반적인 XML 레이아웃과 동일하다. 하지만 모든 뷰가 들어가는 것은 아니며 다음과 같은 뷰를 태그로 추가하여 사용할 수 있다.

|Type|View Name|
|:---:|:---|
|ViewGroup|FrameLayout, LinearLayout, RelativeLayout|
|View|AnalogClock, Button, Chronometer ImageButton, ImageView, ProgressBar, TextView|

앱 위젯에 위의 표로 정리한 뷰들만 들어갈 수 있는 이유는, 앱 위젯으로 표현되는 뷰들이 다른 프로세스에 들어가 있고 이 때문에 다른 프로세스의 뷰에 접근하기 위해 `RemoteViews` 객체가 사용되기 때문이다. 

## Implementation

먼저 `mylocation.xml`이라는 새로운 XML 레이아웃 파일을 생성한다. 이것은 앱 위젯으로 나타날 뷰이다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="@drawable/background"
        android:padding="10dp">
        <TextView
            android:id="@+id/txtInfo"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:gravity="center_horizontal|center_vertical"
            android:text="Reciving My Location..."
            android:textColor="#FFFFFFFF"
            android:lineSpacingExtra="4dp"/>
    </LinearLayout>
</LinearLayout>
```

`/app/res/xml/mylocationinfo.xml` 파일을 추가하여 앱 위젯 제공자 정보를 만든다. 보통 앱 위젯의 크기는 홈 화면의 화면 분할에 따라 74dp 단위로 설정하는 것이 좋다. 74dp 단위 설정 후 위젯의 가장자리가 표시되는 2dp씩을 빼주면 적절한 크기가 된다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="294dp"
    android:minHeight="72dp"
    android:updatePeriodMillis="1800000"
    android:initialKeyguardLayout="@layout/mylocation">
</appwidget-provider>
```

`AndroidManifest.xml`엔 앱 위젯 제공자 클래스를 `receiver` 태그로 추가한다. 액션에 `APPWIDGET_UPDATE`를 설정하고 `meta-data` 태그 안에는 `/app/res/xml/mylocationinfo.xml` 앱 위젯 제공자 정보를 리소스로 설정한다. 그리고 `GPSLocationService` 클래스는 `service` 태그를 사용해 추가한다.

```xml
...
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
...
<application>
    ...
    <receiver android:name=".MyLocationProvider">
        <intent-filter>
            <action android:name="android.appwidget.action.APPWIDGET_UPDATE"/>
        </intent-filter>
        <meta-data android:name="android.appwidget.provider"
            android:resource="@xml/mylocationinfo"/>
    </receiver>
    <service android:name=".MyLocationProvider$GPSLocationService"></service>
</application>
```

`AppWidgetProvider`를 상속하는 `MyLocationProvider` 클래스를 생성한다. 앱이 주기적으로 업데이트 될 때 처리할 코드를 구현한다.

```java
public class MyLocationProvider extends AppWidgetProvider {
    final String TAG = "MyLocationProvider";
    public static double ycoord = 0.0D;
    public static double xcoord = 0.0D;

    @Override
    public void onDeleted(Context context, int[] appWidgetIds) {
        super.onDeleted(context, appWidgetIds);
    }

    @Override
    public void onDisabled(Context context) {
        super.onDisabled(context);
    }

    @Override
    public void onEnabled(Context context) {
        super.onEnabled(context);
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
    }

    // onUpdate 재정의
    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        super.onUpdate(context, appWidgetManager, appWidgetIds);

        Log.d("MyLocationProvider", "onUpdate() called : " + ycoord + ", " + xcoord);

        final int size = appWidgetIds.length;

        for (int i = 0; i < size; i++) {
            int appWidgetId = appWidgetIds[i];

            // 내 위치를 이용해 지도를 보여줄 수 있는 방법은 "geo:"로 시작하는 URI 객체를 만들어 인텐트로 지도를 띄워주는 것이다.
            // geo:<latitude>,<longitude>?z=<zoomLevel>
            // 지도를 띄우기 위한 URI 문자열 생성
            String uriString = "geo:" + ycoord + "," + xcoord + "&z=15";
            Uri uri = Uri.parse(uriString);
            // 지도를 띄우기 위한 인텐트 객체 생성
            Intent intent = new Intent(Intent.ACTION_VIEW, uri);
            // 지도를 띄우기 위한 펜딩 인텐트 객체 생성
            PendingIntent pendingIntent = PendingIntent.getActivity(context, 0, intent, 0);
            
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.mylocation);
            // 뷰를 눌렀을 때 실행할 펜딩 인텐트 객체 지정
            views.setOnClickPendingIntent(R.id.txtInfo, pendingIntent);
            // 앱 위젯 매니저 객체의 updateAppWidget() 호출
            appWidgetManager.updateAppWidget(appWidgetId, views);
        }
        // GPS 위치 확인을 위한 서비스 시작
        context.startService(new Intent(context,GPSLocationService.class));
    }

    public static class GPSLocationService extends Service {
        public static final String TAG = "GPSLocationService";
        private LocationManager manager = null;

        private LocationManager manger = null;
        private LocationListener listener = new LocationListener() {
            @Override
            public void onLocationChanged(@NonNull Location location) {
                Log.d(TAG, "onLocationChanged called");
                // 위치 정보가 확인되면 updateCoordinates() 호출
                updateCoordinates(location.getLatitude(), location.getLongitude());
                stopSelf();
            }
        };

        @Override
        public void onCreate() {
            super.onCreate();
            Log.d(TAG, "onCreate called");
            // 서비스가 생성될 때 위치 관리자 객체 참조
            manager = (LocationManager)getSystemService(LOCATION_SERVICE);
        }

        @Nullable
        @Override
        public IBinder onBind(Intent intent) {
            return null;
        }

        public int onStartCommand(Intent intent, int flags, int startId) {
            // 서비스 시작할 때 startListening() 호출
            startListening();

            return super.onStartCommand(intent, flags, startId);
        }

        public void onDestroy() {
            stopListening();

            Log.d(TAG, "onDestroy() called.");

            super.onDestroy();
        }

        private void startListening() {
            Log.d(TAG, "startListening() called.");

            final Criteria criteria = new Criteria();
            criteria.setAccuracy(Criteria.ACCURACY_COARSE);
            criteria.setAltitudeRequired(false);
            criteria.setBearingRequired(false);
            criteria.setCostAllowed(true);
            criteria.setPowerRequirement(Criteria.POWER_LOW);

            final String bestProvider = manager.getBestProvider(criteria, true);

            try {
                if (bestProvider != null && bestProvider.length() > 0) {
                    // 위치 관리자에 위치 정보 요청
                    manager.requestLocationUpdates(bestProvider, 500, 10, listener);
                } else {
                    final List<String> providers = manager.getProviders(true);

                    for (final String provider : providers) {
                        manager.requestLocationUpdates(provider, 500, 10, listener);
                    }
                }
            } catch(SecurityException e) {
                e.printStackTrace();
            }
        }

        private void stopListening() {
            try {
                if (manager != null && listener != null) {
                    manager.removeUpdates(listener);
                }

                manager = null;
            } catch (final Exception ex) {

            }
        }

        private void updateCoordinates(double latitude, double longitude){
            Geocoder coder = new Geocoder(this);
            List<Address> addresses = null;
            String info = "";

            Log.d(TAG, "updateCoordinates() called.");

            try {
                addresses = coder.getFromLocation(latitude, longitude, 2);

                if (null != addresses && addresses.size() > 0) {
                    int addressCount = addresses.get(0).getMaxAddressLineIndex();

                    if (-1 != addressCount) {
                        for (int index = 0; index <= addressCount; ++index) {
                            info += addresses.get(0).getAddressLine(index);

                            if (index < addressCount)
                                info += ", ";
                        }
                    } else {
                        info += addresses.get(0).getFeatureName() + ", "
                                + addresses.get(0).getSubAdminArea() + ", "
                                + addresses.get(0).getAdminArea();
                    }
                }

                Log.d(TAG, "Address : " + addresses.get(0).toString());
            } catch (Exception e) {
                e.printStackTrace();
            }

            coder = null;
            addresses = null;

            if (info.length() <= 0) {
                info = "[내 위치] " + latitude + ", " + longitude
                        + "\n터치하면 지도로 볼 수 있습니다.";
            } else {
                info += ("\n" + "[내 위치] " + latitude + ", " + longitude + ")");
                info += "\n터치하면 지도로 볼 수 있습니다.";
            }

            // 리모트뷰 생성 후 텍스트뷰의 텍스트 설정
            RemoteViews views = new RemoteViews(getPackageName(), R.layout.mylocation);
            views.setTextViewText(R.id.txtInfo, info);

            ComponentName thisWidget = new ComponentName(this, MyLocationProvider.class);
            AppWidgetManager manager = AppWidgetManager.getInstance(this);
            // 위젯 업데이트
            manager.updateAppWidget(thisWidget, views);

            xcoord = longitude;
            ycoord = latitude;
            Log.d(TAG, "coordinates : " + latitude + ", " + longitude);
        }
    }
}
```

## Conclusion

홈 화면을 길게 눌러 앱 위젯을 추가한 후 텍스트뷰를 누르면 지도에 내 위치가 표시되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
