---
title: Content Provider
author: Beomsu Lee
category: [Android, Component]
tags: [android, component, content provider]
math: true
mermaid: true
---

## Description

Content Provider는 한 앱에서 관리하는 데이터를 다른 앱에서도 접근할 수 있도록 해주는 기능이다. 안드로이드는 보안을 위해 앱들은 각각 독립된 프로세스를 가지고 있으며 서로 접근할 수 없고 해당 프로세스의 데이터만을 사용하여 관리된다. 하지만 가끔 다른 앱에 접근해야하는 경우가 있는데, 이 때 Content Provider를 사용하여 접근할 수 있다. Content Provider도 앱 구성요소 중 하나이기 때문에 시스템에서 관리하며, `AndroidManifest.xml`에 등록해주어야 사용할 수 있다.

Content Provider는 다음 3가지의 데이터를 공유할 수 있다. 
- Database
- File
- Shared Preferences

이 중 Database에 접근하는 것이 가장 일반적인데 Content Provider는 CRUD 동작을 기준으로 하기 때문이다. CRUD에 대응되는 메서드들은 다음과 같다.
|Create|Read|Update|Delete|
|:---:|:---:|:---:|:---:|
|`insert()`|`query()`|`update()`|`delete()`|

Content Provider에서 허용한 통로로 접근하려면 `ContentResolver` 객체가 필요하다. 

## CRUD Implementation

`activity_main.xml`에 `insert`, `query`, `update`, `delete` 버튼 4개와 스크롤뷰 안에 텍스트뷰를 하나 생성한다.

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
            android:id="@+id/insertBtn"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginRight="3dp"
            android:layout_marginLeft="3dp"
            android:layout_marginTop="3dp"
            android:layout_marginBottom="3dp"
            android:layout_weight="1"
            android:text="insert"/>
        <Button
            android:id="@+id/queryBtn"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginRight="3dp"
            android:layout_marginLeft="3dp"
            android:layout_marginTop="3dp"
            android:layout_marginBottom="3dp"
            android:layout_weight="1"
            android:text="query"/>
        <Button
            android:id="@+id/updateBtn"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginRight="3dp"
            android:layout_marginLeft="3dp"
            android:layout_marginTop="3dp"
            android:layout_marginBottom="3dp"
            android:layout_weight="1"
            android:text="update"/>
        <Button
            android:id="@+id/deleteBtn"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginRight="3dp"
            android:layout_marginLeft="3dp"
            android:layout_marginTop="3dp"
            android:layout_marginBottom="3dp"
            android:layout_weight="1"
            android:text="delete"/>

    </LinearLayout>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical">
            <TextView
                android:id="@+id/textView"
                android:layout_width="match_parent"
                android:layout_height="match_parent"/>
        </LinearLayout>
    </ScrollView>
</LinearLayout>
```

`SQLiteOpenHelper`를 상속하는 `DatabaseHelper` 클래스를 추가하고, `person.db`라는 데이터베이스를 만든다.

```java
public class DatabaseHelper extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "person.db";
    private static final int DATABASE_VERSION = 1;

    public static final String TABLE_NAME = "person";
    public static final String PERSON_ID = "_id";
    public static final String PERSON_NAME = "name";
    public static final String PERSON_AGE = "age";
    public static final String PERSON_MOBILE = "mobile";
    public static final String[] ALL_COLUMNS = {PERSON_ID,PERSON_NAME,PERSON_AGE,PERSON_MOBILE};

    private static final String CREATE_TABLE = "CREATE TABLE " + TABLE_NAME +" (" +
                                                    PERSON_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, "+
                                                    PERSON_NAME + " TEXT, " +
                                                    PERSON_AGE + " INTEGER, " +
                                                    PERSON_MOBILE + " TEXT" +
                                                    ")";

    public DatabaseHelper(@Nullable Context context) {
        super(context,DATABASE_NAME,null,DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        // person TABLE 생성
        db.execSQL(CREATE_TABLE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS "+TABLE_NAME);
        onCreate(db);
    }
}
```

`ContentProvider`를 상속하는 `PersonProvider`를 생성하고 CURD에 해당하는 메서드를 만든다. Content Provider를 만들기 위해 고융의 값을 가진 content URI를 만들어야 한다. 예제에선 앱의 이름과 person 테이블 이름을 합쳐 content URI를 정의했다.

|Name|Description|
|:---:|:---|
|content://|Content Provider에 의해 제어되는 데이터라는 의미로 항상 content://로 시작|
|Authority|`com.example.sampleprovider` 부분을 가리키며 내용 제공자를 구분하는 고유한 값|
|Base Path |`person` 값을 가리키며 요청할 데이터의 자료형을 결정|
|ID |맨 뒤의 숫자이며 요청할 데이터 레코드를 지정|

```java
public class PersonProvider extends ContentProvider {

    private static final String AUTHORITY = "com.example.sampleprovider";
    private static final String BASE_PATH = "person";
    public static final Uri CONTENT_URI = Uri.parse("content://"+AUTHORITY+"/"+BASE_PATH);

    private static final int PERSONS = 1;
    private static final int PERSON_ID = 2;
    // uriMatcher는 URI를 매칭하는데 사용
    private static final UriMatcher uriMatcher = new UriMatcher(UriMatcher.NO_MATCH);

    // uriMatcher에 2개의 uri를 추가하여 실행 가능한 uri 여부 확인
    static {
        uriMatcher.addURI(AUTHORITY,BASE_PATH,PERSONS);
        uriMatcher.addURI(AUTHORITY,BASE_PATH+"/#",PERSON_ID);
    }

    private SQLiteDatabase database;

    @Override
    public boolean onCreate() {
        DatabaseHelper helper = new DatabaseHelper(getContext());
        database = helper.getWritableDatabase();
        return true;
    }

    @Nullable
    @Override
    public Cursor query(@NonNull Uri uri, 
                        @Nullable String[] projection,  // 어떤 컬럼을 조회할 것인지 지정(null인 경우 모든 컬럼)
                        @Nullable String selection,     // where 절에 들어갈 조건 지정
                        @Nullable String[] selectionArgs,   // selection이 있을 경우 그 안에 들어갈 조건 값을 대체하기 위해 사용
                        @Nullable String sortOrder) {   // 정렬 컬럼 지정(null인 경우 정렬 미적용)
        Cursor cursor;
        switch(uriMatcher.match(uri)){
            case PERSONS:
                cursor = database.query(DatabaseHelper.TABLE_NAME, DatabaseHelper.ALL_COLUMNS,selection,null,null,null,DatabaseHelper.PERSON_NAME+" ASC");
                break;
            default:
                throw new IllegalArgumentException("Unknown URI : " + uri);
        }
        cursor.setNotificationUri(getContext().getContentResolver(),uri);
        return cursor;
    }

    // MIME 타입 반환
    @Nullable
    @Override
    public String getType(@NonNull Uri uri) {
        switch (uriMatcher.match(uri)){
            case PERSONS:
                return "vnd.android.cursor.dir/persons";
            default:
                throw new IllegalArgumentException("Unknown URI : "+uri);
        }

    }

    @Nullable
    @Override
    public Uri insert(@NonNull Uri uri, 
                      @Nullable ContentValues values) { // 저장할 컬럼명과 값들이 들어간 ContentValues 객체
        long id = database.insert(DatabaseHelper.TABLE_NAME,null,values);

        if(id > 0){
            Uri _uri = ContentUris.withAppendedId(CONTENT_URI,id);
            getContext().getContentResolver().notifyChange(_uri,null);
            return _uri;
        }
        throw new SQLException("Add fail -> URI : " + uri);
    }

    @Override
    public int delete(@NonNull Uri uri, 
                      @Nullable String selection,   // where 절에 들어갈 조건 지정
                      @Nullable String[] selectionArgs) { // selection에 값이 있을 경우 그 안에 들어갈 조건 값을 대체하기 위해 사용
        int count = 0;
        switch (uriMatcher.match(uri)){
            case PERSONS:
                count = database.delete(DatabaseHelper.TABLE_NAME,selection,selectionArgs);
                break;
            default:
                throw new IllegalArgumentException("Unknown URI : "+uri);
        }
        getContext().getContentResolver().notifyChange(uri,null);
        return count;
    }

    @Override
    public int update(@NonNull Uri uri, 
                      @Nullable ContentValues values,   // 저장할 컬럼명과 값들이 들어간 ContentValues 객체 
                      @Nullable String selection,       // where 절에 들어갈 조건
                      @Nullable String[] selectionArgs) {   // selection에 값이 있을 경우 그 안에 들어갈 조건 값을 대체하기 위해 사용
        int count = 0;
        switch (uriMatcher.match(uri)){
            case PERSONS:
                count = database.update(DatabaseHelper.TABLE_NAME,values,selection,selectionArgs);
                break;
            default:
                throw new IllegalArgumentException("Unknown URI : "+ uri);
        }
        getContext().getContentResolver().notifyChange(uri,null);
        return count;
    }
}
```

`MainActivity`에 CRUD 각각 수행할 메서드를 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    TextView textView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView = findViewById(R.id.textView);

        Button insertBtn = findViewById(R.id.insertBtn);
        insertBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                insertPerson();
            }
        });

        Button queryBtn = findViewById(R.id.queryBtn);
        queryBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                queryPerson();
            }
        });

        Button updateBtn = findViewById(R.id.updateBtn);
        updateBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                updatePerson();

            }
        });

        Button deleteBtn = findViewById(R.id.deleteBtn);
        deleteBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                deletePerson();

            }
        });
    }

    public void println(String data){
        textView.append(data + "\n");
    }

    public void insertPerson(){
        println("insertPerson called");

        String uriString = "content://com.example.sampleprovider/person";
        Uri uri = new Uri.Builder().build().parse(uriString);

        Cursor cursor = getContentResolver().query(uri,null,null,null,null);
        // 컬럼 개수 가져온다.
        String[] columns = cursor.getColumnNames();
        println("columns count -> "+columns.length);

        // 컬럼 출력
        for(int i=0;i<columns.length;i++){
            println("#"+i+" : "+columns[i]);
        }

        // ContentValues에 컬럼과 값을 저장
        ContentValues values = new ContentValues();
        values.put("name","john");
        values.put("age",20);
        values.put("mobile","010-1000-1234");

        // 저장한 값을 insert 
        uri = getContentResolver().insert(uri,values);
        println("insert result -> " + uri.toString());
    }

    public void queryPerson(){
        try{
            String uriString = "content://com.example.sampleprovider/person";
            Uri uri = new Uri.Builder().build().parse(uriString);

            // 컬럼 지정
            String[] columns = new String[] {"name","age","mobile"};
            Cursor cursor = getContentResolver().query(uri,columns,null,null,"name ASC");
            println("query result : "+cursor.getCount());

            int index = 0;
            while(cursor.moveToNext()){
                String name = cursor.getString(cursor.getColumnIndex(columns[0]));
                int age = cursor.getInt(cursor.getColumnIndex(columns[1]));
                String mobile = cursor.getString(cursor.getColumnIndex(columns[2]));
                println("#" + index + " -> " + name + ", " + age +", "+mobile);
                index += 1 ;
            }
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public void updatePerson(){
        String uriString = "content://com.example.sampleprovider/person";
        Uri uri = new Uri.Builder().build().parse(uriString);

        // 모바일 컬럼의 값이 010-1000-1234 인 경우 010-2000-3000 으로 변경
        String selection = "mobile = ?";
        String[] selectionArgs = new String[]{"010-1000-1234"};
        ContentValues updateValue = new ContentValues();
        updateValue.put("mobile","010-2000-3000");
        int count = getContentResolver().update(uri,updateValue,selection,selectionArgs);
        println("update result : "+count);
    }

    public void deletePerson(){
        String uriString = "content://com.example.sampleprovider/person";
        Uri uri = new Uri.Builder().build().parse(uriString);

        // name이 john이면 삭제
        String selection = "name = ?";
        String[] selectionArgs = new String[]{"john"};

        int count = getContentResolver().delete(uri,selection,selectionArgs);
        println("delete result : " + count);
    }
}
```

마지막으로 해당 데이터베이스에 `READ`, `WRITE` 권한을 부여하고 `application` 태그 안에 `provider` 태그를 추가한다.

```xml
<permission android:name="com.example.sampleprovider.READ_DATABASE" android:protectionLevel="normal"/>
<permission android:name="com.example.sampleprovider.WRITE_DATABASE" android:protectionLevel="normal"/>
<application>
    ...
    <provider
        android:authorities="com.example.sampleprovider"
        android:name=".PersonProvider"
        android:exported="true"
        android:readPermission="com.example.sampleprovider.READ_DATABASE"
        android:writePermission="com.example.sampleprovider.WRITE_DATABASE"/>
    ...
</application>
```

## Album Implementation

이번에는 Content Provider를 통해 앨범에 있는 사진을 가져오도록 구현할 것이다. `activity_main.xml`에 버튼과 이미지뷰를 생성한다.

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
        android:text="Select Image"/>

    <ImageView
        android:id="@+id/imageView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@mipmap/ic_launcher"/>

</LinearLayout>
```

`MainActivity`에 버튼을 누르면 갤러리를 열고 선택된 사진을 이미지뷰에 출력해주도록 구현한다.

```java
public class MainActivity extends AppCompatActivity {
    ImageView imageView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        imageView = findViewById(R.id.imageView);

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openGallery();
            }
        });
        // READ_EXTERNAL_STORAGE 권한 추가, AndroidManifest.xml에도 권한 추가
        String perm = Manifest.permission.READ_EXTERNAL_STORAGE;
        int permChk = ContextCompat.checkSelfPermission(this,perm);
        if (permChk == PackageManager.PERMISSION_GRANTED) {
            Toast.makeText(this, "Permission Granted", Toast.LENGTH_SHORT).show();
        }else{
            ArrayList<String> targetList = new ArrayList<String>();
            String[] targets = new String[1];
            targets[0] = perm;
            ActivityCompat.requestPermissions(this,targets,101);
        }
    }

    public void openGallery(){
        Intent intent = new Intent();
        // MIME 타입이 이미지인 것을 가져오라는 의미
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);

        // 사진 선택 후 onActivityResult()에서 결과를 전달받을 수 있다.
        startActivityForResult(intent,101);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable @org.jetbrains.annotations.Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if(requestCode == 101){
            if (resultCode == RESULT_OK) {
                // uri의 자료형의 값이 반환됨 -> ContentResolver를 이용해 참조할 수 있는 이미지 파일
                Uri fileUri = data.getData();

                ContentResolver resolver = getContentResolver();

                try{
                    // openInputStream()을 통해 InputStream 객체 반환 후 BitmapFactory.decodeStream()를 통해 bitmap 객체로 만들고 imageView에 출력
                    InputStream insStream = resolver.openInputStream(fileUri);
                    Bitmap imgBitmap = BitmapFactory.decodeStream(insStream);
                    imageView.setImageBitmap(imgBitmap);
                    insStream.close();

                }catch (Exception e){
                    e.printStackTrace();
                }
            }
        }
    }
}
```

## Contacts Implementation

이번엔 Content Provider를 이용해 연락처에 있는 정보를 가져와 출력해주도록 구현할 것이다. `activity_main.xml`에 버튼 하나, 스크롤뷰 안에 텍스트뷰 하나를 추가한다.

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
        android:text="Get Contacts"/>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        <TextView
            android:id="@+id/textView"
            android:layout_width="match_parent"
            android:layout_height="match_parent" />
    </ScrollView>
</LinearLayout>
```

`MainActivity`에서 `getContentResolver`를 통해 연락처를 가져와 출력해주도록 구현한다.

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
                chooseContats();
            }
        });

        String[] perms = {Manifest.permission.READ_CONTACTS, Manifest.permission.WRITE_CONTACTS};
        ActivityCompat.requestPermissions(this,perms,101);
    }

    public void chooseContats(){
        // 연락처 화면을 띄우기 위한 인텐트 생성
        Intent contentPickerIntent = new Intent(Intent.ACTION_PICK, ContactsContract.Contacts.CONTENT_URI);
        startActivityForResult(contentPickerIntent,101);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable @org.jetbrains.annotations.Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if(resultCode == RESULT_OK){
            if(requestCode == 101){
                try{
                    // 선택된 연락처 정보를 가리키는 Uri 객체 반환
                    Uri contactsUri = data.getData();
                    // 선택한 연락처의 id 확인 -> 선택한 연락처의 상세 정보가 다른 곳에 있기 때문
                    String id = contactsUri.getLastPathSegment();
                    getContacts(id);
                }catch (Exception e){
                    e.printStackTrace();
                }
            }
        }
    }
    public void getContacts(String id){
        Cursor cursor = null;
        String name = "";

        try{
            // 연락처의 상세 정보를 조회하는데 사용하는 Uri
            // id 컬럼의 이름은 ContactsContract.Data.CONTACT_ID 
            cursor = getContentResolver().query(ContactsContract.Data.CONTENT_URI,
                                            null,
                                            ContactsContract.Data.CONTACT_ID + "=?",
                                            new String[] {id},
                                            null);
            if (cursor.moveToFirst()) {
                name = cursor.getString(cursor.getColumnIndex(ContactsContract.Data.DISPLAY_NAME));
                println("Name : "+name);

                String columns[] =cursor.getColumnNames();
                for(String column : columns){
                    int index = cursor.getColumnIndex(column);
                    String columnOutput = ("#" + index + "- > [" + column + "]" + cursor.getString(index));
                    println(columnOutput);
                }
                cursor.close();
            }

        }catch (Exception e){
            e.printStackTrace();
        }
    }

    public void println(String data){
        textView.append(data + "\n");
    }
}
```

`AndroidManifest.xml`에 다음 2가지 권한을 추가한다.

```xml
<uses-permission android:name="android.permission.READ_CONTACTS"/>
<uses-permission android:name="android.permission.WRITE_CONTACTS"/>
```


## Conclusion

데이터베이스에 테이블을 만들고 해당 테이블에 삽입, 조회, 삭제, 변경과 앨범, 연락처에서 Content Provider를 이용해 데이터를 가져올 수 있다.

## References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)