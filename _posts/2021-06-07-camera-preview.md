---
title: Camera Preview
author: Beomsu Lee
tags: [android]
---

## Description

앱에서 카메라 미리보기 화면에 증강현실을 표현할 아이콘이나 그래픽 등을 보여주고 싶거나 직접 사진을 찍고 싶을 때 `SurfaceView`를 사용해 구현할 수 있다. `SurfaceView`는 다음과 같이 사용된다.

```plantuml!
SurfaceHolder --> Camera : 프리뷰 설정
Camera --> Camera : 프리뷰 시작
SurfaceHolder <-- Camera : 프리뷰 디스플레이
SurfaceView <-- SurfaceHolder : 프리뷰 표시
```

카메라 미리보기 기능을 구현하려면 일반 `View`가 아니라 `SurfaceView`를 사용해야 한다. `SurfaceView`는 `SurfaceHolder` 객체에 의해 생성되고 제어되기 때문에 둘 사이 관계를 이해해야 한다. 만약 카메라 객체를 만든 후 미리보기 화면을 `SurfaceView`에 보여주고 싶다면 `SurfaceHolder` 객체의 `setPreviewDisplay()` 메서드를 호출해 미리보기를 설정하면 된다. 이 때 타입은 `SURFACE_TYPE_PUSH_BUFFERS`가 되어야 한다. 

## Implementation

우선 `AndroidManifest.xml`에 카메라 권한 및 외부 저장소 권한을 추가한다.

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-feature android:name="android.hardware.camera"
    android:required="true" />
```

`activity_main.xml`에 버튼과 미리보기에 사용할 프레임 레이아웃을 배치한다.

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
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Take Picture"/>

    <FrameLayout
        android:id="@+id/previewFrame"
        android:layout_width="match_parent"
        android:layout_height="match_parent"/>
</LinearLayout>
```

`MainActivity`에서 권한 추가 후 `SurfaceView`를 통해 앱 화면에 미리보기를 출력한다.

```java
public class MainActivity extends AppCompatActivity {
    CameraSurfaceView cameraView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        FrameLayout perviewFrame = findViewById(R.id.previewFrame);
        cameraView = new CameraSurfaceView(this);
        perviewFrame.addView(cameraView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                takePicture();
            }
        });

        // 권한 추가
        ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE,Manifest.permission.READ_EXTERNAL_STORAGE,Manifest.permission.CAMERA},101);
    }
    public void takePicture() {
        // capture() 호출
        cameraView.capture(new android.hardware.Camera.PictureCallback() {
            // 해당 메서드로 캡처한 이미지 데이터 전달됨
            public void onPictureTaken(byte[] data, Camera camera) {
                try {
                    // 전달받은 바이트 배열을 Bitmap 객체로 만든다.
                    Bitmap bitmap = BitmapFactory.decodeByteArray(data, 0, data.length);
                    // 미디어 앨범에 추가
                    String outUriStr = MediaStore.Images.Media.insertImage(
                            getContentResolver(),   // ContentResolver
                            bitmap,                 // bitmap
                            "Captured Image",       // title
                            "Captured Image using Camera."); // name

                    if (outUriStr == null) {
                        Log.d("SampleCapture", "Image insert failed.");
                        return;
                    } else {
                        Uri outUri = Uri.parse(outUriStr);
                        sendBroadcast(new Intent(
                                Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, outUri));
                    }

                    camera.startPreview();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }
    // SurfaceView를 상속하고 SurfaceHolder.Callback 인터페이스를 구현하는 새로운 클래스 생성
    private class CameraSurfaceView extends SurfaceView implements SurfaceHolder.Callback {
        private SurfaceHolder mHolder;
        private android.hardware.Camera camera = null;

        public CameraSurfaceView(Context context) {
            super(context);
            // 생성자에서 SurfaceHolder 객체 참조 후 설정
            mHolder = getHolder();
            mHolder.addCallback(this);
        }
        // SurfaceView가 만들어질 때 Camera 객체를 참조
        public void surfaceCreated(SurfaceHolder holder) {
            // 카메라 열고
            camera = android.hardware.Camera.open();
            // 카메라의 기본 모드가 가로이기 때문에 세로로 변경 
            setCameraOrientation();

            try {
                // 미리보기 화면으로 홀더 객체 설정
                camera.setPreviewDisplay(mHolder);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        
        // SurfaceView의 화면 크기가 바뀌는 등의 변경 시점에 미리보기 시작
        public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
            camera.startPreview();
        }

        // SurfaceView 없어질 때 미리보기 중지
        public void surfaceDestroyed(SurfaceHolder holder) {
            camera.stopPreview();
            camera.release();
            camera = null;
        }

        // 카메라 객체의 takePicture() 메서드를 호출해 사진 촬영
        public boolean capture(android.hardware.Camera.PictureCallback handler) {
            if (camera != null) {
                camera.takePicture(null, null, handler);
                return true;
            } else {
                return false;
            }
        }

        public void setCameraOrientation() {
            if (camera == null) {
                return;
            }

            android.hardware.Camera.CameraInfo info = new android.hardware.Camera.CameraInfo();
            android.hardware.Camera.getCameraInfo(0, info);

            WindowManager manager = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
            // 회전에 대한 정보 확인
            int rotation = manager.getDefaultDisplay().getRotation();

            int degrees = 0;
            switch (rotation) {
                case Surface.ROTATION_0: degrees = 0; break;
                case Surface.ROTATION_90: degrees = 90; break;
                case Surface.ROTATION_180: degrees = 180; break;
                case Surface.ROTATION_270: degrees = 270; break;
            }

            int result;
            if (info.facing == android.hardware.Camera.CameraInfo.CAMERA_FACING_FRONT) {
                result = (info.orientation + degrees) % 360;
                result = (360 - result) % 360;
            } else {
                result = (info.orientation - degrees + 360) % 360;
            }

            // 카메라 객체의 setDisplayOrientation() 메서드 호출
            camera.setDisplayOrientation(result);
        }

    }
}
```

## Conclusion

앱 화면 안에 카메라 미리보기가 출력되고 사진도 찍을 수 있는 것을 확인하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)

