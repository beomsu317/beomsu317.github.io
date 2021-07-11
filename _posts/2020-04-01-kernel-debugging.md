---
title: Kernel Debugging
author: Beomsu Lee
category: [Exploitation, Kernel]
tags: [exploitation, kernel, debugging]
math: true
mermaid: true
---

## Getting -dbgsym.ddeb packages

저장소 정보 `/etc/apt/sources.list.d/ddebs.list` 파일에 저장한다.

```bash
echo "deb http://ddebs.ubuntu.com $(lsb_release -cs) main restricted universe multiverse
deb http://ddebs.ubuntu.com $(lsb_release -cs)-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com $(lsb_release -cs)-proposed main restricted universe multiverse" | \
sudo tee -a /etc/apt/sources.list.d/ddebs.list
```

ubuntu 18.04 이상 LTS 버전인 경우

```bash
sudo apt install ubuntu-dbgsym-keyring
```

해당 커널 버전에 맞는 Debug packages 설치

```bash
sudo apt-get update
sudo apt-get install linux-image-$(uname -r)-dbgsym
```

설치된 Debug Symbol 파일은 다음과 같은 경로에 위치한다. 해당 파일 추출 후 debugger로 attach 하면 된다.

```bash
bs@bs-virtual-machine:~$ ls /usr/lib/debug/boot/
vmlinux-4.4.0-148-generic
```

## Disable KASLR

`/etc/default/grub` 내 `GRUB_CMDLINE_LINUX_DEFAULT` 필드에 `nokaslr` 추가하여 KASLR 비활성화한다.

```c
# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=0
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet nokaslr"
GRUB_CMDLINE_LINUX="find_preseed=/preseed.cfg auto noprompt priority=critical locale=en_US"

# Uncomment to enable BadRAM filtering, modify to suit your needs
# This works with Linux (no patch required) and with any kernel that obtains
# the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
#GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

# Uncomment to disable graphical terminal (grub-pc only)
#GRUB_TERMINAL=console

# The resolution used on graphical terminal
# note that you can use only modes which your graphic card supports via VBE
# you can see them in real GRUB with the command `vbeinfo'
#GRUB_GFXMODE=640x480

# Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
#GRUB_DISABLE_RECOVERY="true"

# Uncomment to get a beep at grub start
#GRUB_INIT_TUNE="480 440 1"
```

다음 명령을 실행하여 변경된 부팅설정을 반영한다.

```bash
sudo update-grub
```

## VMware debugging

디버깅 대상 `*.vmx` 파일을 열어 다음과 같은 설정 추가한다.

### x86

```
debugStub.listen.guest32 = "TRUE"
debugStub.listen.guest32.remote = "TRUE"
debugStub.hideBreakpoints = "FALSE"
monitor.debugOnStartGuest32 = "TRUE"
```

### x64

```
debugStub.listen.guest64 = "TRUE"
debugStub.listen.guest64.remote = "TRUE"
debugStub.hideBreakpoints = "FALSE"
monitor.debugOnStartGuest64 = "TRUE"
```

디버깅 설정이 저장된 VMware를 실행하면 검은 화면에서 대기하게 된다. 위 상태에서 다른 guest vm에서 root 권한으로 gdb를 실행시켜 해당 VM에 연결한다. gdb 연결하기 전 반드시 해당 시스템의 architecture 설정한다. 디버거가 정상적으로 연결되면 디버깅 할 VMware는 정지되며, gdb에서 `continue` 명령을 통해 부팅한다.

gdb 연결 시 사용되는 포트 
* 32bit : 8832 
* 64bit : 8864

## Kernel Address Display Restriction(KADR)

공격자가 커널 취약점을 이용해 Exploit 시 User Space에서의 Exploit과 같이 필요한 가젯, 커널 함수들의 주소 등의 정보가 필요하다. 커널에서는 KADR에 의해 커널 영역의 주소를 민감한 정보로 처리하고 있으며, 일반 로컬 사용자에게 보이지 않는다.

- /boot/vmlinuz*, /boot/System.map*, /sys/kernel/debug/, /proc/slabinfo

Ubuntu 11.04부터 "/proc/sys/kernel/kptr_rr_rrestrict"에서 알려진 커널 주소 출력을 차단하기 위해 "1"로 설정한다. "0"으로 변경 시 비활성화가 된다.

- sudo sysctl -w kernel.kptr_restrict=0

일반 유저로 커널의 모든 심볼 목록을 보관하고 있는 `/proc/kallsyms` 파일을 읽을 경우 해당 심볼의 주소가 `0000000000000000`으로 출력된다. root 권한으로 읽을 경우 심볼들의 주소 값이 출력되고, `kptr_restrict`의 값을 `0`으로 변경하면 일반 유저 권한으로 커널 심볼들의 주소를 확인할 수 있다.

```
bs@bs-virtual-machine:~/Desktop/programming$ cat /proc/kallsyms | grep escal
0000000000000000 t chardev_release  [escalation]
0000000000000000 t chardev_open [escalation]
0000000000000000 t chardev_write    [escalation]
0000000000000000 t chardev_read [escalation]
0000000000000000 t chardev_ioctl    [escalation]
0000000000000000 b info [escalation]
0000000000000000 t chardev_init [escalation]
0000000000000000 b chardev_cdev [escalation]
0000000000000000 b chardev_major    [escalation]
0000000000000000 b __key.26280  [escalation]
0000000000000000 b chardev_class    [escalation]
0000000000000000 t chardev_exit [escalation]
0000000000000000 d __this_module    [escalation]
0000000000000000 t cleanup_module   [escalation]
0000000000000000 t init_module  [escalation]
0000000000000000 d s_chardev_fops   [escalation]
```

## pref_event_paranoid

`kptr_restrict` 값을 `0`으로 변경해도 일반 유저 권한으로 커널 심볼들의 주소를 확인할 수 없는 이유는 `perf_event_paranoid` 때문이다. `perf_event_paranoid`는 Performance counters(커널의 성능 모니터링)의 액세스 제한 권한을 관리하고 있다.

|Value|Description|
|:---:|:---:|
|2|사용자 공간 측정만 허용(Linux 4.6 이후 기본값)|
|1|커널과 사용자 공간 측정을 모두 허용(Linux 4.6 이후 기본값)|
|0|원시 추적점 샘플이 아닌 CPU 별 데이터에 대한 접근 허용|
|-1|제한 없음|

`perf_event_paranoid`의 값을 1 또는 0, -1로 변경하면, 일반 유저 권한으로 커널 심볼들의 주소를 확인할 수 있다.

```
bs@bs-virtual-machine:~$ sudo sysctl -w kernel.perf_event_paranoid=0
kernel.perf_event_paranoid = 0
bs@bs-virtual-machine:~$ cat /proc/kallsyms | head
0000000000000000 A irq_stack_union
0000000000000000 A __per_cpu_start
0000000000000000 A __per_cpu_user_mapped_start
0000000000004000 A vector_irq
0000000000004800 A unsafe_stack_register_backup
0000000000004840 A cpu_debug_store
00000000000048c0 A cpu_tss
0000000000007000 A exception_stacks
000000000000c000 A gdt_page
000000000000d000 A espfix_waddr
```

## Get section address of module

privilege escalation에서 사용된 escalation.ko 모듈 사용

해당 모듈 커널 등록 후 퍼미션 변경

```bash
bs@bs-virtual-machine:~/Desktop/programming$ sudo insmod escalation.ko 
bs@bs-virtual-machine:~/Desktop/programming$ ls -al /dev/chardev0
crw------- 1 root root 246, 0  6월 10 00:46 /dev/chardev0
bs@bs-virtual-machine:~/Desktop/programming$ sudo chmod 666 /dev/chardev0
```

/proc/kallsyms 파일을 이용해 디버깅할 함수들의 주소값 확인한다. 해당 모듈의 `.test`, `.bss`, `.data` 등 정보를 확인할 수 있다.

- /sys/module/모듈명/sections/.text
- /sys/module/모듈명/sections/.bss
- /sys/module/모듈명/sections/.data

```bash
bs@bs-virtual-machine:~/Desktop/programming$ cat /proc/kallsyms  | grep escalation
bs@bs-virtual-machine:~/Desktop/programming$ sudo cat /proc/kallsyms | grep escal
ffffffffc0398000 t chardev_release  [escalation]
ffffffffc0398020 t chardev_open [escalation]
ffffffffc0398040 t chardev_write    [escalation]
ffffffffc0398070 t chardev_read [escalation]
ffffffffc03980a0 t chardev_ioctl    [escalation]
ffffffffc039a480 b info [escalation]
ffffffffc03981a0 t chardev_init [escalation]
ffffffffc039a520 b chardev_cdev [escalation]
ffffffffc039a588 b chardev_major    [escalation]
ffffffffc039a480 b __key.26280  [escalation]
ffffffffc039a508 b chardev_class    [escalation]
ffffffffc03982e0 t chardev_exit [escalation]
ffffffffc039a100 d __this_module    [escalation]
ffffffffc03982e0 t cleanup_module   [escalation]
ffffffffc03981a0 t init_module  [escalation]
ffffffffc039a000 d s_chardev_fops   [escalation]
bs@bs-virtual-machine:~/Desktop/programming$ cat /sys/module/escalation/sections/.text 
0x0000000000000000
bs@bs-virtual-machine:~/Desktop/programming$ sudo cat /sys/module/escalation/sections/.text 
0xffffffffc0398000
bs@bs-virtual-machine:~/Desktop/programming$ sudo cat /sys/module/escalation/sections/.bss
0xffffffffc039a480
bs@bs-virtual-machine:~/Desktop/programming$ sudo cat /sys/module/escalation/sections/.data
0xffffffffc039a000
```

chardev_ioctl 함수의 시작 주소 disassemble

```
(gdb) x/10i 0xffffffffc03980a0
0xffffffffc03980a0: nop    DWORD PTR [rax+rax*1+0x0]
0xffffffffc03980a5: push   rbp
0xffffffffc03980a6: xor    eax,eax
0xffffffffc03980a8: mov    rdi,0xffffffffc03990e8
0xffffffffc03980af: mov    rbp,rsp
0xffffffffc03980b2: push   r12
0xffffffffc03980b4: mov    r12,rdx
0xffffffffc03980b7: push   rbx
0xffffffffc03980b8: mov    ebx,esi
0xffffffffc03980ba: call   0xffffffff8118cc7b <printk>
```

objdump -d 명령으로 메모리에 저장된 `chardev_ioctl` 함수 코드와 덤프된 코드가 일치하는 것을 확인할 수 있다.

```
00000000000000a0 <chardev_ioctl>:
a0: e8 00 00 00 00          callq  a5 <chardev_ioctl+0x5>
a5: 55                      push   %rbp
a6: 31 c0                   xor    %eax,%eax
a8: 48 c7 c7 00 00 00 00    mov    $0x0,%rdi
af: 48 89 e5                mov    %rsp,%rbp
b2: 41 54                   push   %r12
b4: 49 89 d4                mov    %rdx,%r12
b7: 53                      push   %rbx
b8: 89 f3                   mov    %esi,%ebx
ba: e8 00 00 00 00          callq  bf <chardev_ioctl+0x1f>
bf: 81 fb 02 47 88 40       cmp    $0x40884702,%ebx
c5: 0f 84 85 00 00 00       je     150 <chardev_ioctl+0xb0>
cb: 81 fb 03 47 88 80       cmp    $0x80884703,%ebx
d1: 74 48                   je     11b <chardev_ioctl+0x7b>
d3: 81 fb 00 47 00 00       cmp    $0x4700,%ebx
d9: 74 1c                   je     f7 <chardev_ioctl+0x57>
db: 89 de                   mov    %ebx,%esi
dd: 48 c7 c7 00 00 00 00    mov    $0x0,%rdi
e4: 31 c0                   xor    %eax,%eax
```

디버깅을 위해 `chardev_ioctl` 함수의 시작 주소에 breakpoint 설정한다.

```
(gdb) b*0xffffffffc03980a0
Breakpoint 1 at 0xffffffffc03980a0
```

모듈 동작시키기 위해 `test` 프로그램 실행한다. breakpoint가 동작하게 되며 해당 모듈을 동적으로 분석할 수 있다.

```
Thread 1 hit Breakpoint 1, 0xffffffffc03980a0 in ?? ()
(gdb) x/22i $rip
=> 0xffffffffc03980a0:  nop    DWORD PTR [rax+rax*1+0x0]
0xffffffffc03980a5: push   rbp
0xffffffffc03980a6: xor    eax,eax
0xffffffffc03980a8: mov    rdi,0xffffffffc03990e8
0xffffffffc03980af: mov    rbp,rsp
0xffffffffc03980b2: push   r12
0xffffffffc03980b4: mov    r12,rdx
0xffffffffc03980b7: push   rbx
0xffffffffc03980b8: mov    ebx,esi
0xffffffffc03980ba: call   0xffffffff8118cc7b <printk>
0xffffffffc03980bf: cmp    ebx,0x40884702
0xffffffffc03980c5: je     0xffffffffc0398150
0xffffffffc03980cb: cmp    ebx,0x80884703
0xffffffffc03980d1: je     0xffffffffc039811b
0xffffffffc03980d3: cmp    ebx,0x4700
0xffffffffc03980d9: je     0xffffffffc03980f7
0xffffffffc03980db: mov    esi,ebx
0xffffffffc03980dd: mov    rdi,0xffffffffc03991b7
0xffffffffc03980e4: xor    eax,eax
0xffffffffc03980e6: call   0xffffffff8118cc7b <printk>
0xffffffffc03980eb: mov    rax,0xfffffffffffffff2
0xffffffffc03980f2: pop    rbx
```

0xffffffffc0398100(printk)에 breakpoint 설정하고 `rdi` 인자 확인하면 `GIVE_ME_ROOT` 이라는 문자열을 확인할 수 있다.

```
0xffffffffc03980f7: mov    rdi,0xffffffffc03991a9
0xffffffffc03980fe: xor    eax,eax
0xffffffffc0398100: call   0xffffffff8118cc7b <printk>
0xffffffffc0398105: xor    edi,edi
0xffffffffc0398107: call   0xffffffff810a4890 <prepare_kernel_cred>
0xffffffffc039810c: mov    rdi,rax
(gdb) b*0xffffffffc0398100
Breakpoint 3 at 0xffffffffc0398100
(gdb) c
Continuing.
Thread 1 hit Breakpoint 3, 0xffffffffc0398100 in ?? ()
(gdb) info r rdi
rdi            0xffffffffc03991a9  -1069968983
(gdb) x/s 0xffffffffc03991a9
0xffffffffc03991a9: "GIVE_ME_ROOT\n"
```

`prepare_kernel_cred()` 함수 호출 후 리턴 값에 `struct cred` 구조체를 적용하면 `uid`, `gid`, `suid`, `sgid` 등 값이 0으로 설정된다.

```
hread 1 hit Breakpoint 4, 0xffffffffc0398107 in ?? ()
1: x/i $rip
=> 0xffffffffc0398107:  call   0xffffffff810a4890 <prepare_kernel_cred>
(gdb) ni
0xffffffffc039810c in ?? ()
1: x/i $rip
=> 0xffffffffc039810c:  mov    rdi,rax
(gdb) info r rax
rax            0xffff8800ae81ef00  -131938467582208
(gdb) p *(struct cred*)$rax
$1 = {usage = {counter = 1}, uid = {val = 0}, gid = {val = 0}, suid = {
    val = 0}, sgid = {val = 0}, euid = {val = 0}, egid = {val = 0}, fsuid = {
    val = 0}, fsgid = {val = 0}, securebits = 0, cap_inheritable = {cap = {0, 
    0}}, cap_permitted = {cap = {4294967295, 63}}, cap_effective = {cap = {
    4294967295, 63}}, cap_bset = {cap = {4294967295, 63}}, cap_ambient = {
    cap = {0, 0}}, jit_keyring = 1 '\001', 
session_keyring = 0x0 <irq_stack_union>, 
process_keyring = 0x0 <irq_stack_union>, 
thread_keyring = 0x0 <irq_stack_union>, 
request_key_auth = 0x0 <irq_stack_union>, security = 0xffff88009ddd21e0, 
user = 0xffffffff81e492e0 <root_user>, 
user_ns = 0xffffffff81e49360 <init_user_ns>, 
group_info = 0xffffffff81e51000 <init_groups>, rcu = {
    next = 0x0 <irq_stack_union>, func = 0x0 <irq_stack_union>}}
```

## References
- [02.Debugging kernel and modules](https://www.lazenca.net/display/TEC/02.Debugging+kernel+and+modules)