---
title: Recycler View
author: Beomsu Lee
tags: [android]
---

## Description

안드로이드에서 여러 개의 아이템 중 하나를 선택할 수 있는 리스트 모양의 위젯을 "선택 위젯(Selecteion Widget)"이라 한다. 선택 위젯을 일반 위젯과 구분하는 이유는 선택 위젯이 어댑터(Adapter) 패턴을 사용하기 때문이다. 선택 위젯에 데이터를 넣을 때 위젯이 아닌 어댑터에 설정해야하며 뷰도 어댑터에서 만든다. 즉, 리스트 모양의 뷰에 보이는 각각 아이템들을 어댑터에서 관리하는 것이다.

리스트 모양으로 보여줄 수 있는 위젯으로 리싸이클러뷰(RecyclerView)가 있다. 리싸이클러뷰는 상하, 좌우 스크롤을 만들 수 있다. 또한 각각 아이템이 화면에 보일 때 메모리를 효율적으로 사용하도록 캐시(Cache) 메커니즘이 구현되어 있다.

## Implementation

`activity_main.xml`에 RecyclerView를 추가한다. RecyclerView는 선택 위젯이기 때문에 어댑터가 데이터 관리와 뷰 객체 관리를 한다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
```

데이터를 저장할 `Person`이라는 클래스를 생성하고 getter/setter를 설정해준다. 

```java
public class Person {
    String name;
    String mobile;

    public Person(String name, String mobile) {
        this.name = name;
        this.mobile = mobile;
    }

    public String getName() {
        return name;
    }

    public String getMobile() {
        return mobile;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setMobile(String mobile) {
        this.mobile = mobile;
    }
}
```

`/app/res/layout/person_item.xml` 파일을 만들고 다음과 같은 카드뷰를 만든다.

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:orientation="vertical">

    <androidx.cardview.widget.CardView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        app:cardCornerRadius="10dp"
        app:cardElevation="5dp"
        app:cardUseCompatPadding="true">
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">
            <ImageView
                android:id="@+id/imageView"
                android:layout_width="80dp"
                android:layout_height="80dp"
                android:padding="5dp"
                app:srcCompat="@mipmap/ic_launcher"/>
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="match_parent"
                android:layout_margin="5dp"
                android:layout_weight="1"
                android:orientation="vertical">
                <TextView
                    android:id="@+id/textView"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="Name"
                    android:textSize="30sp"/>
                <TextView
                    android:id="@+id/textView2"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="Phone Number"
                    android:textColor="#ff0000ff"
                    android:textSize="25sp"/>
            </LinearLayout>
        </LinearLayout>
    </androidx.cardview.widget.CardView>
</LinearLayout>
```

사용자가 각 아이템을 클릭했을 때 토스트 메시지가 표시되도록 할 것이다. 어댑터 객체 밖에서 리스너 설정하고 설정된 리스너 쪽으로 이벤트를 전달하는 방식의 구현이다. `OnPersonItemClickLinstener()` 인터페이스를 먼저 정의한다.

```java
public interface OnPersonItemClickLinstener {
    public void onItemClick(PersonAdapter.ViewHolder holder, View view,int position);
}
```

`PersonAdapter` 클래스를 만들어 어댑터 생성한다.

```java
public class PersonAdapter extends RecyclerView.Adapter<PersonAdapter.ViewHolder> implements OnPersonItemClickLinstener {
    ArrayList<Person> items = new ArrayList<Person>();
    OnPersonItemClickLinstener listener;

    // 객체가 만들어질 때 호출
    @NonNull
    @org.jetbrains.annotations.NotNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull @org.jetbrains.annotations.NotNull ViewGroup parent, int viewType) {
        // person_item 레아이아웃 인플레이션
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        // 뷰 객체 생성
        View itemView = inflater.inflate(R.layout.person_item,parent,false);
        // 뷰 객체를 전달하고 해당 뷰홀더 객체 반환
        return new ViewHolder(itemView,this);
    }

    // 객체가 재사용될 때 호출
    // 재활용할 수 있는 뷰홀더 객체를 전달받음
    @Override
    public void onBindViewHolder(@NonNull @org.jetbrains.annotations.NotNull PersonAdapter.ViewHolder holder, int position) {
        // 뷰홀더에 현재 아이템에 맞는 데이터만 설정
        Person item = items.get(position);
        holder.setItem(item);
    }

    public void setOnItemClickListener(OnPersonItemClickLinstener listener){
        this.listener = listener;
    }

    // OnPersonItemClickLinstener 인터페이스 구현
    @Override
    public void onItemClick(ViewHolder holder, View view, int position) {
        if(listener != null){
            // 뷰홀더 안에서 뷰가 클릭되었을 때 호출하는 메서드
            listener.onItemClick(holder,view,position);
        }
    }

    // 어댑터에서 관리하는 아이템의 개수 반환
    @Override
    public int getItemCount() {
        return items.size();
    }

    public void addItem(Person item){
        items.add(item);
    }

    public void setItems(ArrayList<Person> items){
        this.items = items;
    }

    public Person getItem(int position){
        return items.get(position);
    }

    public void setItem(int position, Person item){
        items.set(position,item);
    }

    // 각각의 아이템을 위한 뷰는 뷰홀더에 담는다. 이 역할을 하는 클래스를 어댑터에 넣어놓는다.
    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView textView;
        TextView textView2;

        public ViewHolder(View itemView,final OnPersonItemClickLinstener listener){
            // 뷰 객체를 부모 클래스의 변수에 담아두는 역할
            super(itemView);

            // setItem()에서 참조하기 위함
            textView = itemView.findViewById(R.id.textView);
            textView2 = itemView.findViewById(R.id.textView2);

            // 아이템 뷰에 onClickListenter 설정
            itemView.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // getAdapterPosition()은 뷰홀더에 표시할 아이템의 인덱스
                    int position = getAdapterPosition();
                    // 아이템 뷰 클릭 시 미리 정의한 다른 리스너 메서드 호출
                    if(listener != null){
                        listener.onItemClick(ViewHolder.this,v,position);
                    }
                }
            });
        }

        // 뷰홀더에 들어있는 뷰 객체의 데이터를 다른 것으로 보이도록 하는 역할
        public void setItem(Person item){
            textView.setText(item.getName());
            textView2.setText(item.getMobile());
        }
    }
}
```

`MainActivity` 클래스에서 어댑터 설정 및 `Person` 객체를 여러개 추가하여 동작을 확인한다. 만약 어댑터에서 실시간으로 추가된 데이터를 반영하고 싶다면 데이터을 추가하고 `.notifyDataSetChanged()`를 호출하면 된다.

```java
public class MainActivity extends AppCompatActivity {
    PersonAdapter adapter;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        RecyclerView recyclerView = findViewById(R.id.recyclerView);
        // 세로방향의 layoutManager 생성
        LinearLayoutManager layoutManager = new LinearLayoutManager(this,LinearLayoutManager.VERTICAL,false);
        
        // 그리드 모양의 layoutManger
        // GridLayoutManager layoutManager = new GridLayoutManager(this,2);

        // 레이아웃 매니저 객체 설정
        recyclerView.setLayoutManager(layoutManager);

        // 어댑터 생성 후 객체 추가
        adapter = new PersonAdapter();
        adapter.addItem(new Person("Kim min","010-1234-5678"));
        adapter.addItem(new Person("Kim tan","010-3122-3232"));
        adapter.addItem(new Person("Hong gildong","010-1111-1222"));
        for(int i=0;i<30;i++){
            adapter.addItem(new Person("name"+i,"010-1111-1222"));
        }
        recyclerView.setAdapter(adapter);

        // 각 아이템이 클릭되었을 경우 이 리스너의 onItemClick() 메서드가 호출됨
        adapter.setOnItemClickListener(new OnPersonItemClickLinstener() {
            @Override
            public void onItemClick(PersonAdapter.ViewHolder holder, View view, int position) {
                Person item = adapter.getItem(position);
                Toast.makeText(getApplicationContext(), "item selected : "+item.getName(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
```

## Conclusion

RecyclerView를 사용하여 여러개의 아이템들을 리스트 모양으로 보여주도록 구현하였다.

### References
- [Do It! Android Programming](https://github.com/mike-jung/DoItAndroid)