---
title: Action Bar
author: Beomsu Lee
math: true
mermaid: true
tags: [android]
---

## Description

안드로이드는 시스템 메뉴 버튼을 눌렀을 때 숨어있던 메뉴가 보이도록 할 수 있고, 앱의 상단 타이틀 부분에 메뉴 버튼을 배치하고 그것을 눌렀을 때 메뉴가 보이도록 할 수 있다. 이런 메뉴를 옵션 메뉴(Option Memu)라 한다. 그리고 옵션 메뉴와 다르게 입력상자를 길게 눌러 나타나는 메뉴는 컨텍스트 메뉴(Context Menu)라 한다.

|Menu|Description|
|:---:|:---|
|Option Menu|시스템 메뉴 버튼을 눌렀을 때 나타나는 메뉴로 각 화면마다 설정할 수 있는 주요 메뉴|
|Context Menu|화면을 길게 누르면 나타나는 메뉴로 뷰에 설정하여 나타나게 할 수 있음|

옵션 메뉴는 액션바에 포함되어 보이도록 만들어져 있다. 옵션 메뉴와 컨텍스트 메뉴는 각각 액티비티마다 설정 가능하며 다음 두 메서드를 다시 정의하여 메뉴 아이템을 추가할 수 있다.

- public boolean onCreateOptionsMenu(Menu menu)
- public void onCreateContextMenu(ContextMenu menu, View v, ContextMenu.ContextMenuInfo menuInfo)

위 메서드들을 보면 `Menu`나 `Context` 객체가 전달되는데 이 객체의 `add()` 메서드를 사용해 메뉴 아이템을 추가한다.

- MenuItem add(int groupId, int itemId, int order, CharSequence title)
- MenuItem add(int groupId, int itemId, int order, int titleRes)
- SubMenu addSubMenu(int titleRes)

`groupId`는 아이템을 하나의 그룹으로 묶을 때 사용하며, `itemId`는 아이템이 갖고 있는 고유 ID 값으로, 아이템이 선택되었을 때 각각의 아이템을 구분하는 용도이다. 이렇게 코드에서 메뉴를 추가하는 것보다 XML에서 메뉴의 속성을 정의한 후 객체로 로딩하여 참조하는 것이 더 간단하다.

## Option Menu Implementation

안드로이드는 `/app/res/menu` 폴더 안에 메뉴를 위한 XML 파일이 만들어진다는 것을 미리 알고 있다. 따라서 메뉴를 위한 XML은 항상 이 폴더에 있어야 한다.

`/app/res/menu/menu_main.xml` 파일을 생성한다. `item` 태그는 하나의 메뉴 정보를 담고 있다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <item android:id="@+id/menu_refresh"
        android:title="refresh"
        android:icon="@drawable/menu_refresh"
        app:showAsAction="always"/>
    <item android:id="@+id/menu_search"
        android:title="refresh"
        android:icon="@drawable/menu_search"
        app:showAsAction="always"/>
    <item android:id="@+id/menuSetting"
        android:title="refresh"
        android:icon="@drawable/menu_settings"
        app:showAsAction="always"/>
</menu>
```

`onCreateOptionsMenu()` 메서드는 액티비티가 만들어질 때 미리 자동 호출되어 화면에 메뉴 기능을 추가할 수 있도록 한다. `MainActivity`에서 XML로 만든 메뉴 아이템들을 인플레이션 후 아이템이 선택되면 토스트를 띄우게 구현하였다. 

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // 정의한 메뉴 인플레이션
        getMenuInflater().inflate(R.menu.menu_main,menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int curId = item.getItemId();
        switch (curId){
            case R.id.menu_refresh:
                Toast.makeText(this, "refresh selected", Toast.LENGTH_SHORT).show();
                break;
            case R.id.menu_search:
                Toast.makeText(this, "search selected", Toast.LENGTH_SHORT).show();
                break;
            case R.id.menu_setting:
                Toast.makeText(this, "setting selected", Toast.LENGTH_SHORT).show();
                break;
            default:
                break;
        }
        return super.onOptionsItemSelected(item);
    }
}
```

## Conclusion

액션바에 아이템을 설정하고 해당 아이템을 누르면 해당하는 이벤트가 수행되는 것을 확인할 수 있다.

##### Resources
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)