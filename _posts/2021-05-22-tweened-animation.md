---
title: Tweened Animation
author: Beomsu Lee
math: true
mermaid: true
tags: [android]
---

## Description

안드로이드는 애니메이션을 간단하게 적용할 수 있는 여러 가지 방법을 제공한다. 그 중 Tweened Animation이 가장 간다하면서 일반적인 방법으로 사용된다. 

애니메이션이 어떻게 동작할지에 대한 정보는 XML로 만든다. 이 XML 정보는 자바 소스에서 Animation 객체로 로딩한 후 View 객체의 `startAntimation()` 메서드를 사용해 애니메이션을 동작하게 한다. 

## Implementation

애니메이션 액션 정보는 `/app/res/` 위치에 존재해야 인식이 된다. 따라서 먼저 `/app/res/anim` 디렉토리를 생성한다.

`anim` 디렉토리에 scale을 변경하는 `scale.xml` 파일을 만든 후 다음과 같이 작성한다. `<set>` 태그 안에 `<scale>` 태그를 추가하였다. `<set>`은 2가지 이상의 이상의 효과를 동시에 사용할 때 정의한다. 2.5초동안 확대한 후 2.5초동안 축소되게 하였다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <scale
        android:duration="2500"
        android:pivotX="50%"
        android:pivotY="50%"
        android:fromXScale="1.0"
        android:fromYScale="1.0"
        android:toXScale="2.0"
        android:toYScale="2.0"/>

    <scale
        android:startOffset="2500"
        android:duration="2500"
        android:pivotX="50%"
        android:pivotY="50%"
        android:fromXScale="1.0"
        android:fromYScale="1.0"
        android:toXScale="0.5"
        android:toYScale="0.5"/>
</set>
```

다음은 `<translate>` 태그를 이용해 뷰를 움직이는 `translate.xml`을 작성한다. 

```xml
 <translate
     xmlns:android="http://schemas.android.com/apk/res/android"
     android:fromXDelta="0"
     android:toXDelta="-50%p"
     android:duration="3000"
     android:fillAfter="true"/>
```

다음은 `<rotate>` 태그를 이용해 뷰를 회전시키는 `rotate.xml`을 작성한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<rotate xmlns:android="http://schemas.android.com/apk/res/android"
    android:fromDegrees="0"
    android:toDegrees="360"
    android:pivotY="50%"
    android:pivotX="50%"
    android:duration="5000"/>
```

다음은 `<alpha>` 태그를 이용해 뷰의 투명도를 0 -> 1로 변경하는 `alpha.xml`을 작성한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<alpha xmlns:android="http://schemas.android.com/apk/res/android"
    android:fromAlpha="0.0"
    android:toAlpha="1.0"
    android:duration="3000"/>
```

`MainActivity`에 버튼 4개를 만들고 해당 버튼을 클릭할 경우 애니메이션을 시작하는 코드를 작성한다.

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Animation anim = AnimationUtils.loadAnimation(getApplicationContext(),R.anim.scale);
                v.startAnimation(anim);
            }
        });

        Button button2 = findViewById(R.id.button2);
        button2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Animation anim = AnimationUtils.loadAnimation(getApplicationContext(),R.anim.translate);
                v.startAnimation(anim);
            }
        });

        Button button3 = findViewById(R.id.button3);
        button3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Animation anim = AnimationUtils.loadAnimation(getApplicationContext(),R.anim.rotate);
                v.startAnimation(anim);
            }
        });

        Button button4 = findViewById(R.id.button4);
        button4.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Animation anim = AnimationUtils.loadAnimation(getApplicationContext(),R.anim.alpha);
                v.startAnimation(anim);
            }
        });
    }
}
```

만약 화면이 사용자에게 보인느 시점에 애니메이션을 시작하고 싶다면 에니메이션의 시작점은 `onWindowFocusChanged()` 메서드가 호출되는 시점이 된다. 즉, 윈도우가 포거스를 받는 시점이 되어야 한다. 해당 메서드 내 `hasFocus` 변수의 값이 `true` 일 경우 각각 애니메이션 객체에 대해 `start()` 메서드를 호출하여 애니메이션이 시작되도록 하면 된다.

애니메이션이 언제 시작했고 끝났는지에 대한 정보는 `AnimationListener` 객체를 설정하면 알 수 있다. 

## Conclusion

각 애니메이션에 따라 버튼이 동작하는 것을 확인할 수 있다.

##### Resources
- [Animation.AnimationListener](https://developer.android.com/reference/android/view/animation/Animation.AnimationListener)

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)