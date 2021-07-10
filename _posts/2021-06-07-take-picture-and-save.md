---
title: Take Picture and Save
author: Beomsu Lee
category: [Android, Camera]
tags: [android, camera]
math: true
mermaid: true
---

## Description

카메라는 멀티미디어 기능에서 자주 사용되는 기능 중 하나이다. 최근에는 단순히 사진 찍는 용도로 사용되는 것이 아닌 미리보기 화면에 정보를 표시하거나, 영상이나 이미지를 앱의 다른 기능에 활용하는 경우가 많아졌다. 예를 들어, 바코드 정보를 추출할 수 있는 바코드 리더기 등이 있다. 

카메라로 사진을 찍기 위한 방법은 2가지로 나눌 수 있다.
- 인텐트로 단말의 카메라 앱을 실행한 후 결과 사진을 받아 처리
- 앱 화면에 카메라 미리보기를 보여주고 직접 사진을 찍어 처리

## Intent Implementation

인텐트를 통해 사진을 찍는 것을 구현할 것이다. `activity_main.xml`에 버튼과 이미지뷰를 배치한다.

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

    <ImageView
        android:id="@+id/imageView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@mipmap/ic_launcher"/>

</LinearLayout>
```

`res/xml/external.xml` 파일을 만들고 `paths` 태그로 수정한다. 이 태그는 `external-path` 태그를 포함하고 있으며, 특정 폴더를 현재 폴더로 인식하게 한다. 

```xml
<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-path name="sdcard" path="."/>
</paths>
```

`AndroidManifest.xml`에 외부 저장소 권한과 카메라 권한을 추가하며, `provider` 태그를 사용하는데 `FileProvider`는 특정 폴더를 공유하는데 사용하는 Content Provider이다. `resource` 속성 값으로 `external.xml` 값을 설정한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.sample.capture.intent">
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-feature android:name="android.hardware.camera" android:required="true"/>

    <application
        ...
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="com.example.sample.capture.intent.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/external" />
        </provider>
    </application>
</manifest>
```

`MainActivity`에서 3가지 권한을 부여받고 버튼을 누를 경우 카메라 앱을 인텐트로 호출하여 찍은 사진을 가져오도록 구현하였다.

```java
public class MainActivity extends AppCompatActivity {
    ImageView imageView;

    File file;
    Uri uri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        imageView = findViewById(R.id.imageView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                takePicture();
            }
        });

        // 권한 부여
        ActivityCompat.requestPermissions(this,new String[]{
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.CAMERA
        },101);
    }

    public void takePicture() {
        try {
            // 파일 생성
            file = createFile();
            if (file.exists()) {
                file.delete();
            }

            file.createNewFile();
        } catch(IOException e) {
            e.printStackTrace();
        }

        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (takePictureIntent.resolveActivity(this.getPackageManager()) != null) {
            if(Build.VERSION.SDK_INT >= 24) {
                // File 객체로부터 Uri 객체를 만든다.
                uri = FileProvider.getUriForFile(this, "com.example.sample.capture.intent.fileprovider", file);
            } else {
                uri = Uri.fromFile(file);
            }
            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT,uri);
            // 카메라 앱을 호출
            startActivityForResult(takePictureIntent, 101);
        }
    }

    private File createFile() {
        String filename = "capture.jpg";
        File outFile = new File(getExternalCacheDir(), filename);

        return outFile;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == 101 && resultCode == RESULT_OK) {
            try {
                BitmapFactory.Options options = new BitmapFactory.Options();
                // 해상도가 높은 경우 Bitmap 객체의 크기도 커지므로 적당한 비율로 축소한다. 1/8로 축소
                options.inSampleSize = 8;
                // 받아온 이미지를 Bitmap 객체로 만든다.
                Bitmap bitmap = BitmapFactory.decodeFile(file.getAbsolutePath(),options);
                // 이미지뷰에 bitmap 설정
                imageView.setImageBitmap(bitmap);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

}
```

## Conclusion

인텐트를 통해 카메라 앱으로 이동하여 사진을 찍고, 찍은 사진을 파일로 저장 및 화면에 표시되는 것을 확인할 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)
- [photobasics](https://developer.android.com/training/camera/photobasics)
