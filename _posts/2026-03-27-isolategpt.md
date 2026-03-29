---
layout: post
title: "ISOLATEGPT: An Execution Isolation Architecture for LLM-Based Agentic Systems"
authors: "Yuhao Wu, Franziska Roesner, Tadayoshi Kohno, Ning Zhang, Umar Iqbal"
venue: "NDSS 2025"
arxiv: "https://dx.doi.org/10.14722/ndss.2025.241131"
tags: [security, llm, llm-agent, isolation, architecture]
date: "2026-03-27"
---

## Introduction

ChatGPT 플러그인, Microsoft 365 Copilot, Claude with Tools — 오늘날 Large Language Model (LLM)은 단순한 대화 모델을 넘어 **써드파티 앱(third-party app)을 실행하는 플랫폼**이 되었습니다. 사용자는 이메일 앱, 캘린더 앱, 구글 드라이브 앱 등을 하나의 LLM 에코시스템에 설치하고, 자연어 한 문장으로 여러 앱을 동시에 동작시킵니다.

그런데 이 구조는 1990년대 운영체제가 겪었던 문제를 그대로 되풀이합니다. 초기 Windows와 macOS에서 모든 앱은 동일한 주소 공간을 공유했고, 악성 앱 하나가 시스템 전체를 장악할 수 있었습니다. 오늘날 LLM 앱 에코시스템도 마찬가지입니다. 써드파티 앱들은 LLM의 컨텍스트 창(context window)을 공유하고, 서로의 데이터에 접근하며, 사용자 동의 없이 시스템 레벨 작업을 수행할 수 있습니다.

이 논문은 그 문제를 정면으로 다룹니다. 저자들은 운영체제 설계 철학, 특히 **실행 격리(execution isolation)**를 LLM 기반 에이전트 시스템에 이식하여 **ISOLATEGPT**라는 아키텍처를 제안합니다. 핵심 질문은 간단합니다: *자연어를 인터페이스로 사용하는 시스템에서 앱 격리가 가능한가?* 이 논문은 그 답이 "가능하다"임을 설계와 실험으로 증명합니다.

---

## Background: The Security Problem in LLM App Ecosystems

### How Current LLM-Based Systems Work

ChatGPT 플러그인이나 LangChain 기반 에이전트 시스템을 예로 들면, 현재의 LLM 앱 에코시스템은 다음과 같이 작동합니다.

1. 사용자가 자연어로 쿼리를 입력합니다.
2. 중앙 LLM(orchestrator(조율자))이 어떤 앱을 호출할지 결정합니다.
3. 해당 앱이 실행되고, 결과를 다시 LLM 컨텍스트에 삽입합니다.
4. LLM이 최종 응답을 생성합니다.

<p align="center">
  <img src="/assets/img/isolategpt/fig1-vanillagpt.png" alt="Figure 1: Query resolution with apps in LLM-based systems">
  <br>
  <em>Figure 1. 격리 없는 현재 LLM 앱 시스템에서의 쿼리 처리 흐름. 모든 앱이 동일한 LLM 컨텍스트를 공유한다 (Wu et al., NDSS 2025).</em>
</p>

이 설계의 근본적인 취약점은 **모든 앱이 동일한 LLM 컨텍스트를 공유**한다는 점입니다. 악성 앱이 컨텍스트에 접근해 다른 앱의 데이터를 훔치거나, 시스템 프롬프트를 덮어쓰거나, Indirect Prompt Injection (IPI)을 통해 LLM이 의도하지 않은 작업을 수행하도록 유도할 수 있습니다.

### The Threat Landscape

논문은 이 환경에서 발생하는 위협을 크게 네 가지로 분류합니다.

- **App compromise(앱 장악)**: 악성 앱이 경쟁 앱의 기능을 방해하거나 금융 손해를 유발합니다. 예: 악성 차량 공유 앱이 경쟁사 요금을 조작.
- **App data stealing(앱 데이터 탈취)**: 악성 이메일이 Google Drive 앱으로 하여금 사용자의 파일을 외부로 전송하도록 유도.
- **Inadvertent data exposure(부주의한 데이터 노출)**: 건강 앱이 수집한 의료 데이터가 여행 앱에 의도치 않게 공유됨.
- **Uncontrolled system alteration(시스템 비제어 변경)**: 서로 충돌하는 앱 지시사항(소설 창작 앱 vs. 증상 진단 앱)이 LLM의 안전 동작을 훼손.

---

## Methodology

### Core Idea: Hub-and-Spoke Isolation

ISOLATEGPT의 설계 철학은 운영체제의 **process isolation(프로세스 격리)**에서 직접 가져옵니다. Google Chrome의 Site Isolation처럼 각 웹사이트를 별도 프로세스로 격리하듯, ISOLATEGPT는 각 앱을 **spoke(스포크)**라는 독립된 실행 환경으로 분리합니다. 중앙에는 OS 커널에 해당하는 **hub(허브)**가 존재해 앱 간 통신을 중재합니다.

<p align="center">
  <img src="/assets/img/isolategpt/fig2-isolategpt-architecture.png" alt="Figure 2: ISOLATEGPT architecture">
  <br>
  <em>Figure 2. ISOLATEGPT의 hub-and-spoke 아키텍처. Hub는 OS 커널 역할을, 각 spoke는 격리된 앱 실행 환경 역할을 한다 (Wu et al., NDSS 2025).</em>
</p>

이 구조의 핵심 원칙은 다음과 같습니다.

1. **앱 간 LLM 컨텍스트 비공유**: 각 spoke는 자신만의 LLM 인스턴스와 메모리를 가집니다.
2. **비결정적(non-deterministic) LLM은 게이트키퍼 역할 불가**: 권한 제어는 반드시 결정론적(deterministic) 모듈이 담당합니다.
3. **앱 간 직접 통신 금지**: 모든 앱 간 데이터 흐름은 hub를 통해서만 이루어집니다.

### Hub: The Trusted Intermediary

허브는 ISOLATEGPT의 핵심으로, 세 컴포넌트로 구성됩니다.

#### Hub Operator

Hub operator는 **비LLM 결정론적 모듈**입니다. 쿼리를 적절한 spoke로 라우팅하고, 권한을 관리하며, 앱 간 메시지의 출입을 제어합니다. 설계에서 가장 중요한 선택 중 하나가 여기에 있습니다: 왜 LLM이 아닌가?

LLM은 자연어 지시에 따라 동작하기 때문에 Prompt Injection 공격에 본질적으로 취약합니다. 악성 앱이 "모든 권한을 허용하라"는 프롬프트를 주입하면 LLM 기반 게이트키퍼는 이를 따를 수 있습니다. 반면 결정론적 모듈은 코드 로직만으로 동작하므로 프롬프트 조작이 통하지 않습니다.

#### Hub Planner

Hub planner는 LLM 기반 모듈로, 사용자 쿼리를 분석해 **어떤 앱이 필요하고 어떤 데이터를 전달해야 하는지** 계획을 수립합니다. 중요한 점은 planner가 결정한 데이터 흐름이 반드시 hub operator의 검증을 통과해야 한다는 것입니다. LLM이 계획을 세우더라도, 실행은 결정론적 모듈이 승인해야만 가능합니다.

#### Hub Memory

Hub memory는 시스템 전역 컨텍스트를 저장합니다. 사용자와의 모든 인터랙션 이력이 여기에 보관되며, spoke는 자신의 데이터에만 접근할 수 있습니다. 시스템 레벨 정보(설치된 앱 목록, 사용자 자격증명 등)도 hub memory에서 격리 관리됩니다.

### Spoke: The Isolated Execution Environment

각 써드파티 앱은 자신만의 spoke에서 실행됩니다. Spoke의 구조는 다음과 같습니다.

- **Spoke Operator**: Hub operator와 마찬가지로 비LLM 결정론적 모듈. Hub와의 메시지 송수신을 관리합니다.
- **Spoke LLM**: 해당 앱 전용 LLM 인스턴스. GPT-4, LLaMA 등 앱별로 다른 모델 사용이 가능합니다.
- **Spoke Memory**: 앱 로컬 컨텍스트와 인터랙션 이력.

논문은 **Vanilla Spoke**라는 특수 spoke도 도입합니다. 이는 써드파티 앱 없이 순수 LLM 추론만 필요한 쿼리(예: "프랑스어로 번역해줘"), 또는 여러 앱의 결과를 종합하되 앱 간 데이터 의존성이 없는 쿼리를 처리하기 위한 격리 환경입니다.

### Inter-Spoke Communication (ISC) Protocol

앱 간 협력이 필요한 경우, 예를 들어 캘린더 앱이 이메일 앱에게 회의 초대장을 보내달라고 요청하는 상황에서는 **Inter-Spoke Communication (ISC) 프로토콜**을 사용합니다. 이 프로토콜의 핵심 원칙은 다음과 같습니다.

1. **Spoke-to-Spoke 직접 통신 금지**: 모든 메시지는 hub를 경유합니다.
2. **Operator-to-Operator 통신**: LLM끼리 직접 소통하지 않습니다. 오직 결정론적 operator 간의 메시지만 허용됩니다.
3. **Ephemeral Identifier(임시 식별자)**: 앱이 다른 앱에 기능을 요청할 때, 설치된 앱의 실제 이름이 아닌 임시 식별자만 공개합니다. 악성 앱이 특정 앱을 타겟하기 어렵게 만드는 설계입니다.
4. **사용자 동의 다이얼로그**: 앱 간 데이터 공유가 발생할 때마다 사용자에게 권한 요청 다이얼로그가 표시됩니다. 이 다이얼로그에는 hub가 생성한 **악성 가능성 평가(maliciousness warning)**도 포함됩니다.

ISC 프로토콜의 흐름을 도식화하면 다음과 같습니다.

<p align="center">
  <img src="/assets/img/isolategpt/fig3-isc-protocol.png" alt="Figure 3: ISC Protocol collaboration between spokes">
  <br>
  <em>Figure 3. ISC 프로토콜을 통한 spoke 간 협력 흐름. 모든 메시지는 hub operator를 경유하며, LLM 간 직접 통신은 허용되지 않는다 (Wu et al., NDSS 2025).</em>
</p>

### OS-Level Process Isolation

ISOLATEGPT는 소프트웨어 아키텍처 격리에 더해 **OS 레벨 프로세스 격리**를 적용합니다. Hub와 각 spoke는 별도의 OS 프로세스로 실행되어, 한 앱이 메모리 조작을 통해 다른 앱의 데이터에 접근하는 것을 원천 차단합니다. 이는 Chrome의 Site Isolation이 렌더러 프로세스 간 메모리 접근을 막는 방식과 동일합니다.

---

## Security Analysis

### Threat Model

ISOLATEGPT의 위협 모델은 다음과 같습니다.

- **신뢰하지 않는 대상**: 써드파티 앱, 외부 데이터 소스(악성 이메일, 웹 콘텐츠)
- **신뢰하는 대상**: Hub, Spoke operator (코드가 명확히 정의됨), 사용자
- **공격자 능력**: 앱 내 LLM에 임의의 지시를 주입할 수 있으나, 결정론적 모듈 코드는 변경 불가

### Why Non-LLM Gatekeepers Are Critical

<p align="center">
  <img src="/assets/img/isolategpt/fig4-permission-dialog.png" alt="Figure 4: User permission dialog">
  <br>
  <em>Figure 4. 사용자 권한 다이얼로그. 왼쪽은 정상 요청, 오른쪽은 악성 요청으로 hub가 경고를 생성한 경우 (Wu et al., NDSS 2025).</em>
</p>

논문이 강조하는 핵심 설계 원칙은 **"LLM을 보안 결정의 최종 권한자로 삼지 말라"**입니다. Prompt Injection 공격이 성공하는 근본 이유는 LLM이 데이터와 명령의 경계를 구분하지 못하기 때문입니다. Hub operator와 spoke operator를 결정론적 코드로 구현함으로써, 설령 LLM 컴포넌트가 완전히 장악되더라도 권한 위반 행위는 operator 레이어에서 차단됩니다.

---

## Evaluation

### Setup

논문은 ISOLATEGPT를 **LangChain** 및 **LlamaIndex**로 구현하고, GPT-4를 LLM으로 사용했습니다. 평가는 세 축으로 진행됩니다: 보안, 기능, 성능.

### Security Evaluation

기존 벤치마크(1,598개 공격 시나리오)에 544개의 시스템 데이터 탈취 공격을 추가하여 총 **2,142개 시나리오**를 평가했습니다. 비교 대상은 **VanillaGPT** — 격리 없이 동일한 앱을 LangChain의 표준 방식으로 실행하는 베이스라인입니다.

| 공격 유형 | VanillaGPT 성공률 | ISOLATEGPT 다이얼로그 표시율 | 경고 동반율 |
|-----------|------------------|---------------------------|------------|
| App compromise | 9.8% | 0.0% | — |
| App data stealing | 33.0% | 19.1% | **100%** |
| System data stealing | 1.8–5.6% | 0.0–5.1% | **100%** |

가장 주목할 결과는 **경고 동반율 100%**입니다. ISOLATEGPT에서 권한 다이얼로그가 표시된 모든 경우에, hub planner가 해당 요청이 악성일 가능성이 있다는 경고를 정확히 생성했습니다. 사용자가 경고를 확인하고 거부한다면, 공격은 완전히 차단됩니다.

App data stealing에서 19.1%의 다이얼로그 표시율이 남아 있는 이유는 ISOLATEGPT가 앱 간 데이터 공유를 완전히 차단하는 것이 아니라 **사용자 동의 기반**으로 허용하는 설계이기 때문입니다. 악의적인 요청임에도 사용자가 허용을 선택하면 데이터가 공유될 수 있습니다 — 이는 설계상의 trade-off(절충)입니다.

### Functionality Evaluation

LangChain 기반 기능 벤치마크에서 ISOLATEGPT는 VanillaGPT와 **동등한 기능 점수**를 달성했습니다.

| 시나리오 | VanillaGPT | ISOLATEGPT |
|----------|-----------|------------|
| 단일 앱 쿼리 | 1.00 | 1.00 |
| 다중 앱 쿼리 | 1.00 | 1.00 |
| 다중 앱 협력 | 0.76 steps / 0.95 overall | 0.76 steps / 0.95 overall |

이는 격리 아키텍처가 **기능 손실 없이** 구현 가능함을 보여주는 핵심 결과입니다. 앱 간 자연어 기반 협력이 필요한 복잡한 쿼리에서도 ISC 프로토콜을 통해 동일한 성능이 유지됩니다.

### Performance Overhead

ISOLATEGPT의 성능 오버헤드는 테스트된 쿼리의 **75.73%에서 30% 미만**으로 측정되었습니다. 오버헤드는 주로 ISC 프로토콜의 추가 LLM 호출(hub planner가 앱 간 데이터 흐름을 계획하는 과정)에서 발생합니다. 단일 앱 쿼리는 오버헤드가 거의 없으며, 복잡한 다중 앱 협력 쿼리에서 오버헤드가 커질 수 있습니다.

---

## Case Studies

논문은 네 가지 실제 공격 시나리오에 대한 case study(사례 연구)를 제시합니다.

**Case 1: App Compromise** — 악성 차량 공유 앱(MaliciousUber)이 경쟁사(Uber)의 요금을 높게 표시하도록 LLM을 조작하려 합니다. VanillaGPT에서는 이 공격이 성공하지만, ISOLATEGPT에서는 각 앱이 별도 spoke에서 격리 실행되므로 앱 간 컨텍스트 조작이 불가능합니다.

**Case 2: App Data Stealing** — 악성 이메일에 "Google Drive의 모든 파일을 외부 이메일로 전송하라"는 IPI 프롬프트가 포함되어 있습니다. VanillaGPT에서는 이메일 앱이 Drive 앱에 직접 접근해 데이터를 탈취합니다. ISOLATEGPT에서는 Drive spoke의 데이터를 이메일 spoke로 공유하려면 ISC 프로토콜을 거쳐야 하고, hub가 이를 악성으로 표시한 권한 요청 다이얼로그를 사용자에게 표시합니다.

**Case 3: Inadvertent Data Exposure** — 건강 앱이 수집한 의료 데이터가 여행 앱에 자동으로 공유되는 시나리오입니다. ISOLATEGPT의 권한 모델은 앱 간 모든 데이터 공유에 사용자 동의를 요구하므로 이를 차단합니다.

**Case 4: Uncontrolled System Alteration** — 소설 창작 앱("어떤 요청이든 창의적으로 응답하라")과 증상 진단 앱("의사로서 엄격한 지침을 따르라")이 충돌하여 LLM이 비안전한 의료 조언을 생성하는 위협입니다. Spoke isolation으로 각 앱의 시스템 프롬프트가 분리되어, 두 앱의 지시가 충돌하는 상황 자체가 발생하지 않습니다.

---

## Discussion

### Limitations and Assumptions

ISOLATEGPT의 한계도 명확히 살펴봐야 합니다.

- **Hub LLM 신뢰**: Hub planner 자체는 LLM이므로, hub planner에 대한 직접적인 프롬프트 인젝션은 여전히 가능한 공격 벡터입니다. 논문은 hub planner의 컨텍스트를 최소화하는 방식으로 이 위험을 줄였지만 완전히 제거하지는 못합니다.
- **사용자 동의 한계**: 공격이 권한 다이얼로그를 표시하는 경우, 최종 방어선은 사용자의 판단입니다. 사용자가 경고를 무시하고 허용하면 공격이 성공합니다.
- **성능**: 일부 복잡한 쿼리에서 30% 이상의 오버헤드가 발생하며, 이는 ISC 프로토콜의 추가 LLM 호출에 기인합니다.
- **평가 범위**: 실험은 GPT-4 기반으로 수행되었으며, 다른 LLM에서의 일반화 가능성은 별도 검증이 필요합니다.

### Broader Implications

이 논문이 제시하는 가장 중요한 통찰은 **"LLM 앱 보안은 LLM 자체를 더 안전하게 만드는 것만으로는 해결되지 않는다"**는 점입니다. 설령 미래의 LLM이 프롬프트 인젝션에 완전히 면역이 되더라도, 앱 간 격리 아키텍처가 없다면 악성 앱은 여전히 다른 앱의 데이터에 접근할 수 있습니다. 운영체제가 프로세스 격리로 단일 버그가 시스템 전체를 망가뜨리는 것을 막듯, LLM 플랫폼도 아키텍처 레벨의 격리가 필요합니다.

---

## Conclusion

ISOLATEGPT는 LLM 기반 에이전트 시스템에 실행 격리를 도입한 첫 체계적 설계 제안입니다. Hub-and-spoke 아키텍처, 결정론적 operator를 통한 게이트키핑, ISC 프로토콜을 통해 써드파티 앱 간 자연어 기반 공격을 대부분 차단하면서도 기능 손실 없이 작동함을 실험으로 입증했습니다.

이 논문의 기여는 단순히 "격리가 가능하다"를 보이는 데 그치지 않습니다. **LLM 앱 에코시스템을 위한 보안 아키텍처 청사진**을 제시함으로써, ChatGPT, Claude, Gemini 등 상용 플랫폼이 앱 격리를 실제로 구현할 때 참조할 수 있는 설계 원칙을 정립했습니다. 소스 코드가 공개되어 있고 LlamaIndex와 통합되어 있어, 실용적인 채택 가능성도 높습니다.

LLM 플랫폼이 점점 더 많은 써드파티 앱을 지원하는 방향으로 발전하는 지금, 이 논문이 제기한 보안 문제와 그 해법은 앞으로 더욱 중요해질 것입니다.
