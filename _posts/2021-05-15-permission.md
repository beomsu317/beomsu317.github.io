---
title: Permission
author: Beomsu Lee
tags: [android]
---

## Description

안드로이드엔 일반 권한(Normal Permission)과 위험 권한(Dangerous Permission)으로 나눠져 있다. 기존의 방식은 앱을 설치하는 시점에 사용자에게 물어보는 방식이였지만 권한을 확인하지 않고 설치하는 사용자가 많아 위험 권한을 분류하여 앱이 시작되는 시점에 권한을 부여하도록 변경하였다.

예를 들어 `INTERNET` 권한은 일반 권한이며, 앱을 설치할 때 사용자에게 권한이 부여되는 것을 알리고 설치한다. 하지만 위험 권한인 `RECEIVE_SMS`의 경우 설치 시에 부여한 권한은 의미가 없으며 실행 시 물어보게 된다.

위험 권한으로 분류된 기능으로는 위치, 카메라, 마이크, 연락처, 전화, 문자, 일정, 센서 등이 있다.

권한 그룹(Permission Group)은 동일한 기능을 접근하는데 몇 가지 세부 권한을 하나로 묶는 역할을 한다. 

## Dangerous Permission Grant Implementation

`AndroidManifest.xml` 파일을 열고 SD 카드 접근할 때 사용되는 2가지 위험 권한을 부여한다.

```xml
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
```

`MainActivity`를 다음과 같이 구현하여 `onCreate()` 시 권한을 부여하도록 작성한다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // SD 카드 접근에 필요한 권한 
        String[] permissions = {
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
        };
        checkPermissions(permissions);
    }

    public void checkPermissions(String[] permissions){
        ArrayList<String> targetList = new ArrayList<String>();

        for(int i=0;i<permissions.length;i++){
            String curPermission = permissions[i];
            int permissionCheck = ContextCompat.checkSelfPermission(this,curPermission);
            // 권한이 부여되어 있는지 여부를 확인
            if(permissionCheck == PackageManager.PERMISSION_GRANTED){
                Toast.makeText(this, curPermission + " Granted", Toast.LENGTH_SHORT).show();
            }else{
                Toast.makeText(this, curPermission + " not Granted", Toast.LENGTH_SHORT).show();
                // 권한이 부여되어 있는지 여부를 확인 
                if(ActivityCompat.shouldShowRequestPermissionRationale(this,curPermission)){
                    // 부여가 안됐을 경우의 경고
                    Toast.makeText(this, curPermission + " Description Needed", Toast.LENGTH_SHORT).show();
                }else{
                    targetList.add(curPermission);
                }
            }
        }

        String[] targets = new String[targetList.size()];
        targetList.toArray(targets);

        // 권한 부여되지 않았으면 권한 부여 요청
        if(targets.length != 0){
            // 수락했는지 거부했는지 여부를 onRequestPermissionsResult() 콜백 함수에서 확인해야 함
            ActivityCompat.requestPermissions(this,targets,101);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull @org.jetbrains.annotations.NotNull String[] permissions, @NonNull @org.jetbrains.annotations.NotNull int[] grantResults) {
        switch (requestCode){
            case 101:
                if(grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED){
                    Toast.makeText(this, "permission granted", Toast.LENGTH_SHORT).show();
                }else{
                    Toast.makeText(this, "permission denied", Toast.LENGTH_SHORT).show();
                }
                return;
        }
    }
}
```

## Conclusion

권한이 부여되어 있지 않다면 권한 부여 요청하는 창을 띄우며 수락, 거부에 대한 메시지 확인이 가능하다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)