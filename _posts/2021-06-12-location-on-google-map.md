---
title: Location on Google Map
author: Beomsu Lee
category: [Android]
tags: [google map]
---

## Description

안드로이드에서는 앱 화면 안에 지도를 넣을 수 있도록 `MapFragment`를 제공하고 있다. 다음 과정을 통해 지도를 보여줄 수 있다.

1. Google Play Service 라이브러리 사용 설정
1. XML 레이아웃에 `MapFragment` 추가
1. 소스 코드에서 내 위치로 지도 이동
1. 메니페스트 설정 추가
1. 지도 API 키를 발급받아 매니페스트에 설정

## Google Maps Implementation

우선 Goole Play Service 라이브러리 설정을 위해 SDK Manager를 연다. SDK Tools 탭을 선택한 후 `Goole Play Service` 모듈을 설치한다. 

그리고 Project Structure 메뉴로 들어가 Declared Dependencies 아래의 '+' 버튼을 누르고 Library Dependency를 선택한다. `play-services-maps`를 입력 후 적용한다.

우선 `AndroidManifest.xml`에 구글앱 라이브러리를 사용한다닌 정보와 함께 GPS, 인터넷 사용에 대한 권한과 기타 설정 정보를 등록해야 한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.sample.location.map">

    <permission android:name="com.example.sample.location.map.permission.MAPS_RECEIVE"
        android:protectionLevel="signature"/>
    <uses-permission android:name="com.example.sample.location.map.permission.MAP_RECEIVE"/>
    <!-- 위험 권한 -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="com.google.android.providers.gsf.permission.READ_GSERVICES"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    <!-- OpenGL 기능 사용하도록 하기 위함 --> 
    <uses-feature android:glEsVersion="0x00020000"
        android:required="true"/>

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.SampleLocationMap">
        <uses-library android:name="com.google.android.maps"/>
        <uses-library android:name="org.apache.http.legacy" android:required="false"/>
        <!-- 구글맵 서비스를 위한 키 값을 설정해주어야 한다. -->
        <meta-data android:name="com.google.android.maps.v2.API_KEY"
            android:value="API_KEY"/>

        <meta-data android:name="com.google.android.gms.version"
            android:value="@integer/google_play_services_version"/>

        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### Google Maps API Key

1. 먼저 <https://console.developers.google.com>에 접속한다. 
1. 새로운 프로젝트를 하나 생성한 후 `API 및 서비스` 메뉴로 들어간다. 
1. `라이브러리`를 선택하고 `Maps SDK for Android`를 검색 후 `사용 설정` 버튼을 누른다. 
1. 왼쪽의 `사용자 인증 정보` 메뉴를 누르고, `사용자 인증 정보 만들기` -> `API 키`를 선택하면 API Key를 발급받을 수 있다.

`activity_main.xml`에 버튼과 `fragment`를 추가하고, `fragment`의 `class` 속성에 `com.google.android.gms.maps.SupportMapFragment` 설정을 해준다. 

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
        android:text="Request My Location"/>

    <fragment
        android:id="@+id/map"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        class="com.google.android.gms.maps.SupportMapFragment"/>
</LinearLayout>
```

`MainActivity`에 버튼을 누르면 현재 위치를 구글맵에 보여주도록 구현한다.

```java
public class MainActivity extends AppCompatActivity {

    final String TAG = "MainActivity";

    SupportMapFragment mapFragment;
    GoogleMap map;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // mapFragment 참조 후
        mapFragment = (SupportMapFragment)getSupportFragmentManager().findFragmentById(R.id.map);
        // getMapAsync() 호출, 비동기 방식으로 처리
        mapFragment.getMapAsync(new OnMapReadyCallback() {
            @Override
            public void onMapReady(GoogleMap googleMap) {
                // 초기화 완료될 때 자동 호출됨
                Log.d(TAG, "onMapReady");
                map = googleMap;
            }
        });

        try {
            MapsInitializer.initialize(this);
        } catch (Exception e) {
            e.printStackTrace();
        }

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startLocationService();
            }
        });

        ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, 101);
    }

    public void startLocationService() {
        LocationManager manager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);

        try {
            Location location = manager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (location != null) {
                Double latitude = location.getLatitude();
                Double longitude = location.getLongitude();
            }

            GPSListener gpsListener = new GPSListener();
            long minTime = 10000;
            float minDistance = 0;

            manager.requestLocationUpdates(LocationManager.GPS_PROVIDER, minTime, minDistance, gpsListener);

        } catch (SecurityException e) {
            e.printStackTrace();
        }
    }

    class GPSListener implements LocationListener {
        @Override
        public void onLocationChanged(@NonNull Location location) {
            Double latitude = location.getLatitude();
            Double longitude = location.getLongitude();
            // 해당 메서드를 통해 현재 위치를 지도에 보여준다. 
            showCurrentLocation(latitude, longitude);
        }
    }

    private void showCurrentLocation(Double latitude, Double longitude) {
        // 현재 위치의 좌표로 LatLng 객체 생성
        LatLng curPoint = new LatLng(latitude, longitude);
        // 지정한 위치의 지도 영역 보여준다.
        // 2번째 인자는 지도의 축척이며 1로 설정되면 가장 멀리서 보는 모습이 되고, 값이 점점 커질수록 확대된다. 
        map.animateCamera(CameraUpdateFactory.newLatLngZoom(curPoint, 15));
    }
}
```

## Icons Implementation

기본 지도 이외에 다른 아이콘을 표시하여 주변의 시설들을 표시해 줄 수 있어야 사용자가 알고 싶어하는 정보를 보여줄 수 있다. 

`map.setMyLocationEnabled()` 메서드를 이용해 현재 내 위치를 지도에 표시해 줄 수 있다. 또한 `Marker`를 사용해 내 위치나 원하는 위치를 표시할 수 있다.

```java
public class MainActivity extends AppCompatActivity {
    MarkerOptions markerOptions;
    ...
    private void showCurrentLocation(Double latitude, Double longitude) {
        LatLng curPoint = new LatLng(latitude, longitude);
        map.animateCamera(CameraUpdateFactory.newLatLngZoom(curPoint, 15));
        showMyLocationMarker(curPoint);
    }

    private void showMyLocationMarker(LatLng curPoint){
        if(markerOptions == null){
            // 마커 객체 생성
            markerOptions = new MarkerOptions();
            markerOptions.position(curPoint);
            markerOptions.title("My Location");
            markerOptions.snippet("GPS Verified Locations");
            markerOptions.icon(BitmapDescriptorFactory.fromResource(R.drawable.mylocation));
            // 지도에 마커 추가
            map.addMarker(markerOptions);
        }else{
            markerOptions.position(curPoint);
        }
    }
}
```

## Conclusion

버튼을 누르면 현재 위치 정보가 구글맵에 보여지는 것을 구현했고, 마커를 추가해 현재 위치를 아이콘으로 표현되는 것을 확인할 수 있다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
