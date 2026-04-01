---
layout: post
title: "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents"
authors: "Uchi Uchibeke"
venue: "arXiv 2026"
arxiv: "https://arxiv.org/abs/2603.20953"
tags: [security, ai-agent, authorization, tool-call, mcp, agentic-ai]
date: "2026-04-01"
---

여러분, 오늘은 AI 에이전트 보안의 핵심 공백을 짚어낸 논문을 살펴보겠습니다. 제목은 **"Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents"**로, APort Technologies의 Uchi Uchibeke가 작성한 arXiv 프리프린트입니다.

이 논문의 출발점은 매우 직관적인 관찰입니다. "AI 에이전트는 비밀번호(passwords)는 있지만, 허가증(permission slips)이 없다." 현재의 AI 에이전트는 자금 이체, 데이터베이스 쿼리, 셸 명령 실행, 하위 에이전트 위임 등의 tool call을 실행할 때 **사전에 이 행위를 인가(authorize)하는 표준 메커니즘이 존재하지 않습니다.** 이 논문은 이 공백을 *pre-action authorization problem*으로 정의하고, 이를 해결하기 위한 오픈 명세인 **Open Agent Passport (OAP)**를 제안합니다.

## Background and Related Work

### 기존 안전장치의 한계

현재 AI 에이전트의 안전 아키텍처는 크게 두 가지에 의존합니다.

**Model Alignment (학습-시점 정렬)**: RLHF, Constitutional AI 등 훈련-시점 정렬은 모델의 응답 분포를 바람직한 방향으로 조정합니다. 그러나 이는 **확률적(probabilistic)**이어서 적대적 프롬프트로 우회 가능하며, 개별 tool call 수준의 정책 집행을 보장하지 않습니다.

**Post-Hoc Evaluation (사후 평가)**: Promptfoo, Galileo 등의 도구는 에이전트를 적대적 시나리오로 테스트하고 출력을 채점합니다. OpenAI는 2026년 3월 Promptfoo를 인수했을 만큼 이 카테고리가 주목받고 있습니다. 그러나 사후 평가는 구조적으로 **회고적(retrospective)**입니다. 완료된 실행에서 패턴을 찾을 뿐, 프로덕션의 개별 tool call을 인터셉트하지 않습니다.

### Sandboxed Execution

세 번째 접근은 에이전트 실행을 격리된 환경에 가두는 샌드박스 방식입니다. NVIDIA NemoClaw, E2B, Modal, Google Agent Sandbox 등이 대표적입니다. 샌드박스는 코드 실행 공격, 파일 시스템 조작, 네트워크 유출을 억제하지만, 두 가지 중요한 한계가 있습니다.

1. **의미적 비즈니스 정책을 집행할 수 없습니다.** 지출 한도, 데이터 분류 제약, 허가된 수신자 목록 등은 조직 정책에 대한 지식이 필요합니다. 샌드박스는 이를 모릅니다.
2. **사전 인가가 아닙니다.** 샌드박스는 허가된 범위 내의 합법적인 API 호출(예: $500 이체)도 실행은 허용합니다. 문제는 그 행위가 정책을 위반하더라도 막지 못한다는 것입니다.

논문은 이 세 가지 아키텍처가 **경쟁 관계가 아니라 상보 관계**에 있음을 보여줍니다(후술).

### 업계 현황: Authorization Gap의 실재

논문은 이 공백이 이론적 우려가 아님을 구체적 사례로 뒷받침합니다.

- 6개 자율 에이전트를 14일간 운영한 레드팀 연구: 에이전트가 단일 동사 재구성으로 SSN을 유출, 비밀을 지키기 위해 자체 인프라를 파괴
- 27.2%의 엔지니어링 팀이 프레임워크 인가 시스템을 포기하고 하드코딩 로직으로 회귀
- 492개 이상의 MCP 서버가 인증·암호화 없이 프로덕션에 노출
- CVE-2026-26118 (CVSS 8.8): Azure MCP Server의 SSRF 취약점은 유효한 인증 자격증명으로 악용됨 — 공격자는 접근 권한이 있었으나, 실행을 거버닝하는 정책이 없었음

이것들은 정렬(alignment) 실패가 아닙니다. **인가(authorization) 실패**입니다.

## The Open Agent Passport (OAP)

### Design Principles

OAP는 여섯 가지 설계 요구사항을 만족하도록 설계되었습니다.

| 요구사항 | 의미 |
|----------|------|
| **Deterministic** | 동일 입력 → 동일 결정. 샘플링도, 온도도 없음 |
| **Bypass-resistant** | 모델 추론 레이어가 아닌 프레임워크 레이어에서 실행. Prompt injection으로 우회 불가 |
| **Framework-agnostic** | 핵심 명세는 특정 에이전트 프레임워크에 종속되지 않음 |
| **Auditable** | 모든 결정은 서명된 타임스탬프 레코드를 생성 |
| **Fail-closed** | 인가 서비스를 사용할 수 없으면 tool call은 거부됨 |
| **Implementer-independent** | OAP는 제품이 아닌 명세. 누구나 구현 가능 |

### Architecture

OAP는 세 가지 핵심 컴포넌트로 구성됩니다: **Agent Passport**, **Policy Pack**, **before_tool_call Hook**.

<p align="center">
  <img src="/assets/img/open-agent-passport/fig-1-oap-flow.png" alt="Figure 1: OAP Authorization Flow">
  <br>
  <em>Figure 1. OAP 인가 플로우. before_tool_call 훅이 모든 tool call을 실행 전에 인터셉트한다. (Uchibeke, 2026)</em>
</p>

에이전트가 `payment.send($500, USD)`를 호출하려는 순간, `BEFORE_TOOL_CALL` 훅이 동기적으로 개입합니다. 훅은 여섯 단계를 순서대로 수행합니다: ① 여권 로드(Ed25519 서명 검증), ② 상태 확인(active/suspended/revoked), ③ 기능 매칭(payment.send → finance pack), ④ 파라미터 평가(통화 한도, 허용 관할권 등), ⑤ ALLOW/DENY/ESCALATE 결정, ⑥ 결정 레코드 서명.

결과는 둘 중 하나입니다. **ALLOW**면 tool이 실행되고 서명된 영수증이 남습니다. **DENY**면 tool이 차단되고 서명된 거부 이유가 반환됩니다.

### The Agent Passport

에이전트 여권(Agent Passport)은 에이전트의 신원을 허가된 기능 범위(capability scope)에 바인딩하는 서명된 자격증명입니다.

```json
{
  "spec_version": "oap/1.0",
  "agent_id": "ap_117fff4550094005a6c48c8a626c95e4",
  "name": "Acme Research Agent",
  "status": "active",
  "assurance_level": "L2",
  "capabilities": [
    { "id": "web.fetch" },
    { "id": "data.file.read" },
    { "id": "payments.charge" }
  ],
  "limits": {
    "allowed_domains": ["api.github.com", "*.acme.internal"],
    "currency_limits": {
      "USD": { "max_per_tx": 5000, "daily_cap": 25000 }
    },
    "allow_pii": false,
    "max_calls_per_minute": 60
  },
  "canonical_hash": "sha256:oOHPz1s/PrmLR7d8kZ...",
  "registry_sig": "ed25519:qf1LiELhoh7/xGRTJrZ...",
  "registry_key_id": "oap:registry:key-2025-01"
}
```

여권은 레지스트리 서비스가 발급하며 **Ed25519** 타원곡선 디지털 서명으로 보호됩니다. 서명은 모든 tool call마다 검증됩니다. 여권 범위 밖의 기능을 시도하면 즉시 `oap.unknown_capability` 코드와 함께 DENY됩니다. 거부 응답에는 이유 코드와 인간이 읽을 수 있는 설명이 포함되어, 에이전트 프레임워크가 "이 이체는 수신자가 허용된 목록에 없어 거부되었습니다"라는 안내 응답을 생성할 수 있습니다.

### Policy Packs

Policy Pack은 기능 도메인의 인가 제약 조건을 선언적·버전 관리 방식으로 명세합니다. 각 팩은 JSON Schema로 정의된 필수 컨텍스트 필드, 조건-거부코드 쌍의 평가 규칙, 최소 보증 수준 요구사항을 포함합니다.

```json
{
  "policy_id": "finance.payment.refund.v1",
  "required_context": {
    "required": ["amount", "currency", "reason_code"]
  },
  "rules": [
    { "condition": "amount > limits.max_per_tx",
      "deny_code": "oap.limit_exceeded" },
    { "condition": "currency NOT IN limits.supported",
      "deny_code": "oap.currency_unsupported" },
    { "condition": "reason_code NOT IN limits.codes",
      "deny_code": "oap.blocked_pattern" }
  ],
  "min_assurance": "L2"
}
```

현재 OAP 정책 라이브러리는 21개의 팩을 포함합니다: 금융 작업(5개), 데이터 작업(5개), 코드·리포지토리(2개), 웹(2개), 시스템(1개), 메시징(1개), 에이전트 라이프사이클(3개), MCP(1개), 법률(1개).

### The before_tool_call Hook

핵심은 모든 tool call 전에 발동하는 블로킹 훅입니다. 훅은 tool이 실행되기 전에 await됩니다. OpenClaw, Cursor, Claude Code, LangChain, CrewAI 등 주요 프레임워크에 프로덕션 통합이 완료되어 있습니다. **훅은 모델의 출력 파싱 레이어가 아닌 프레임워크/플랫폼 레이어에서 구현**되므로, 모델이 tool call을 요청하도록 설득한 prompt injection도 정책 검사를 우회할 수 없습니다.

### Assurance Level Taxonomy

OAP는 검증 강도를 6단계로 분류합니다.

| 레벨 | 검증 방식 | 예시 요구사항 |
|------|-----------|---------------|
| L0 | 자기 증명 | 감사 전용 기준선 |
| L1 | 이메일 검증 | OAP 훅 존재, fail-closed |
| L2 | GitHub 검증 | 서명된 여권, 명명된 팩 |
| L3 | 도메인 검증 | 고위험 작업 시 인간 개입 |
| L4KYC | KYC/KYB 검증 | 정부 발급 신분증 |
| L4FIN | 금융 데이터 검증 | 은행 명세서; SOC 2 정렬 |

## Formal Characterization

### Threat Model

**공격자 모델**: 공격자는 (a) 에이전트의 입력 컨텍스트에 적대적 콘텐츠를 주입(prompt injection), (b) 위임 체인의 하위 에이전트를 탈취, (c) 합법적 또는 불법적 수단으로 획득한 유효 인증 자격증명 제시, (d) 인가된 기능 내에서 파라미터 조작을 수행할 수 있습니다.

**신뢰 가정**: OAP는 (a) 에이전트 프레임워크 런타임이 before_tool_call 훅을 올바르게 호출하고, (b) 정책 평가 엔진이 결정론적으로 실행되며, (c) Ed25519 서명 키 인프라가 침해되지 않는다고 가정합니다.

**OAP가 방어하는 것**: 비인가 tool call, 기능 경계를 넘는 권한 상승, 침해·조작된 에이전트의 정책 위반 행위, 선언된 한도를 초과하는 파라미터 조작.

**OAP가 방어하지 않는 것**: 인가된 범위 내의 의도치 않은 부작용, 콘텐츠 수준 공격(OAP는 콘텐츠가 아닌 행위를 평가함), 프레임워크 런타임 자체의 침해, 부채널 공격, 커널 수준 익스플로잇.

### Authorization Function

논문은 pre-action authorization을 다음 함수로 형식화합니다.

$$\text{authorize}(T, P, \Pi) \to (D, L)$$

여기서:
- $T$ = tool call (이름, 파라미터, 컨텍스트)
- $P$ = 에이전트 여권 (신원, 기능, 한도, 보증 수준)
- $\Pi$ = 정책 팩 (T에 대한 선언적 규칙)
- $D$ = 인가 결정 $\in \{\text{ALLOW}, \text{DENY}, \text{ESCALATE}\}$
- $L$ = 감사 로그 항목 (에이전트, 도구, 파라미터, 결정, 타임스탬프, Ed25519 서명)

이 함수는 다섯 가지 속성을 만족해야 합니다:

1. **Determinism**: 동일 입력 $(T, P, \Pi)$에 항상 동일한 $D$를 반환 (평가 경로에 모델 추론 없음)
2. **Completeness**: 유효한 모든 $(T, P, \Pi)$에 대해 결정 $D$가 반환됨
3. **Fail-closed**: $P$가 유효하지 않거나 만료·중단되었거나 $\Pi$를 사용할 수 없으면 $D = \text{DENY}$
4. **Non-bypassability**: $D = \text{ALLOW}$가 아니면 $T$가 실행될 수 없음 (플랫폼 수준 집행)
5. **Auditability**: 모든 $(T, P, \Pi, D)$ 튜플이 서명된 $L$을 생성

### Authorization Algorithm

<p align="center">
  <img src="/assets/img/open-agent-passport/fig-2-algorithm.png" alt="Figure 2: OAP Authorization Algorithm">
  <br>
  <em>Figure 2. OAP 인가 알고리즘 (Algorithm 1). Line 14의 ESCALATE는 명세에는 있으나 참조 구현에서는 미구현 상태. (Uchibeke, 2026)</em>
</p>

알고리즘은 순서대로 다음 검사를 수행합니다.

```python
# Algorithm 1: OAP Authorization (의사코드)
def authorize(T, P, policy_packs):
    # 1. 여권 상태 확인
    if P.status not in {ACTIVE}:
        return DENY, sign(T, P, DENY, "passport_" + P.status)

    # 2. 기능 범위 확인
    if T.capability_id not in P.capabilities:
        return DENY, sign(T, P, DENY, "oap.unknown_capability")

    # 3. 정책 팩 조회 (fail-closed)
    pi = lookup(policy_packs, T.capability_id)
    if pi is None:
        return DENY, sign(T, P, DENY, "oap.fail_closed")

    # 4. 보증 수준 확인
    if P.assurance_level < pi.min_assurance:
        return DENY, sign(T, P, DENY, "oap.assurance_insufficient")

    # 5. 정책 규칙 순차 평가
    for rule in pi.rules:
        if evaluate(rule.condition, T.params, P.limits):
            return DENY, sign(T, P, DENY, rule.deny_code)

    # 6. 승인 필요 여부 확인 (ESCALATE - 미구현)
    if P.limits.approval_required:
        return ESCALATE, sign(T, P, ESCALATE, "oap.approval_required")

    return ALLOW, sign(T, P, ALLOW, "oap.allowed")
```

**결정론성**은 알고리즘이 샘플링, 외부 호출, 시간 의존적 분기를 포함하지 않음에서 따릅니다. `evaluate()`는 결정 가능한(decidable) 단편에서만 작동합니다 — 유한 도메인에 대한 비교와 집합 소속 판단만 허용하며, 루프도, 재귀도, 외부 상태도 없습니다. 이는 정책 평가가 항상 $O(n)$ 시간 내에 종료됨을 보장합니다 ($n$은 매칭된 팩의 규칙 수, 통상 3–8개). 반면 PCAS의 Datalog 기반 언어는 표현력이 더 높지만 재귀적 규칙 합성을 허용합니다. OAP는 표현력 대신 보장된 상수 시간 평가를 선택했습니다.

## Three Architectures for Runtime Agent Safety

논문의 중요한 기여 중 하나는 세 가지 런타임 안전 아키텍처의 상보성을 명확히 보이는 것입니다.

| 차원 | Pre-Action Authorization | Sandboxed Execution | Model-Based Screening |
|------|--------------------------|---------------------|-----------------------|
| 작동 위치 | 결정 레이어 (행위 전) | 실행 환경 (행위 중) | 모델 추론 레이어 (행위 전) |
| 메커니즘 | 선언 기능·한도 대비 정책 평가 | 커널/하이퍼바이저 격리 | 경량 모델의 의도 분류 |
| 비인가 행위 방지 | **예** (의미/정책 수준) | 제한적 (리소스/네트워크 수준) | 확률적 |
| 폭발 반경 억제 | 아니오 | **예** | 아니오 |
| 비즈니스 규칙 집행 | **예** (지출 한도, 도메인 허용목록) | 아니오 | 제한적 |
| Prompt injection 방어 | **예** (모델 설득되어도 정책이 거부) | 아니오 (에이전트가 샌드박스 내에서 행동) | 확률적 |
| 감사 레코드 | **예** (암호학적으로 서명) | 부분적 (실행 로그) | 아니오 |
| 오버헤드 | ~53ms (p50) | 100–300ms 콜드 스타트 | 50–200ms |

두 시나리오의 대조가 이 표를 잘 설명합니다.

**시나리오 1** — prompt injection으로 조작된 에이전트가 `data.file.read`로 `/etc/passwd`를 읽으려 합니다.
- OAP: 여권의 `allowed_classifications`에 시스템 파일이 없음 → **DENY**, 읽기 실행 안 됨
- Sandbox: 파일시스템 제약으로 `/etc/passwd` 접근 차단 — 실행은 시도되었지만 억제됨
- Model screening: prompt injection의 프레이밍 방식에 따라 플래그 여부가 달라짐

**시나리오 2** — 에이전트가 적법해 보이는 `payments.charge($500, USD)`를 호출하는데, 이는 에이전트의 거래당 한도($100)를 초과합니다.
- OAP: **DENY** `oap.limit_exceeded`, 청구 실행 안 됨
- Sandbox: 네트워크 호출을 허용 → $500 청구가 실행됨
- Model screening: 유효한 API 호출 패턴으로 보임 → 플래그 없음

논문은 **프로덕션 배포의 최소 요건이 pre-action authorization + sandboxed execution의 조합**임을 주장합니다.

## Evaluation

### Adversarial Testbed: APort Vault CTF

APort는 Vault라는 라이브 적대적 테스트베드를 운영합니다. 참가자들이 소셜 엔지니어링을 통해 AI 뱅킹 에이전트로 비인가 이체를 유도하는 Capture The Flag(CTF) 환경입니다. 에이전트는 대화에 프런티어 언어 모델을, 인가에 OAP 정책 엔진을 사용합니다. 모델의 판단은 대화를 통해 타협시킬 수 있지만, 정책 엔진은 서명된 여권에서 결정론적으로 평가합니다.

2026년 3월 기준 결과는 아래와 같습니다.

<p align="center">
  <img src="/assets/img/open-agent-passport/table-6-t1-t5-baseline.png" alt="Table 6: T1 vs T5 Baseline Comparison">
  <br>
  <em>Table 6. T1(허용적 정책) vs. T5(제한적 정책) 기준선 비교. (Uchibeke, 2026)</em>
</p>

전체 1,151 세션에서 4,437건의 인가 결정이 이루어졌고, 2,419건(54.5%)이 거부되었습니다. 가장 많은 거부 코드는 `oap.unknown_capability`(1,453건)와 `oap.merchant_forbidden`(412건)이었습니다.

핵심 비교는 **T1(허용적)과 T5(제한적)** 두 계층입니다. T1("인턴")은 동일한 모델·인터페이스·OAP 인프라를 사용하지만 허용적 정책(와일드카드 상인, 높은 한도)을 적용합니다. T5("금고")는 제로 기능, $0 한도의 제한적 정책을 사용합니다.

비슷한 공격자 모집단에 대해:
- **T1 (허용적)**: 788회 시도 중 74.6%가 성공 — 모델이 소셜 엔지니어링에 설득되어 tool call을 생성하고, 허용적 OAP 정책이 대부분 통과시킴
- **T5 (제한적)**: 879회 시도 중 **0% 성공** — 모델이 설득되더라도 정책 엔진이 모든 시도를 차단. $5,000 현상금 미청구

T1에서 788회 시도 중 202회(25.6%)는 OAP 결정 자체를 트리거하지 않았습니다 — 모델 자체가 transfer_funds tool call 생성을 거부한 것입니다. 나머지 586회 중 581회는 OAP가 허용했습니다. 결론적으로, **정책이 행위를 허가했을 때(T1) 소셜 엔지니어링의 74.6%가 성공하고, 정책이 엄격한 기능 범위를 집행했을 때(T5) 0%가 성공한다는 것은 결과를 결정한 것이 모델이 아니라 정책 레이어임을 보여줍니다.**

### Performance Benchmarks

<p align="center">
  <img src="/assets/img/open-agent-passport/table-7-latency.png" alt="Table 7: OAP Authorization Latency">
  <br>
  <em>Table 7. OAP 인가 지연 시간 벤치마크 (N=1,000). (Uchibeke, 2026)</em>
</p>

프로덕션 워크로드(N=1,000)에서 Cloud API 중앙값은 **53ms (p50)**, p99는 77ms 이하입니다. 지연 분해는 다음과 같습니다.

| 컴포넌트 | 시간 |
|----------|------|
| 여권 조회 + 캐시 | 20ms |
| 정책 평가 | 15ms |
| 결정 서명 (Ed25519) | 10ms |
| HTTP 오버헤드 (TLS, 파싱, 직렬화) | ~8ms |
| **동기 합계 (블로킹)** | **~53ms** |

감사 로그 기록(~9ms)은 결정 반환 후 비동기적으로 실행되므로 측정 지연에 포함되지 않습니다. 이 수치는 tool call 자체가 I/O 바운드(통상 200ms에서 수 초)임을 감안하면 수용 가능한 오버헤드입니다.

로컬 평가(네트워크 없음)는 Python 서브프로세스 오버헤드로 중앙값 174ms가 측정되었으며, 이는 향후 개선 여지가 있습니다.

### OWASP Agentic Top 10 Coverage

OWASP의 AI 에이전트 애플리케이션 Top 10 리스크에 대한 OAP의 커버리지를 보면, **Agent Goal Hijack**, **Tool Misuse**, **Privilege Escalation**, **Excessive Agency** 등에 부분적 커버리지를, **Identity & Privilege Abuse**에는 전체 커버리지를 제공합니다. 반면 **Improper Output Handling**, **Knowledge Poisoning** 등 콘텐츠 수준 위협은 OAP의 범위 밖입니다(OAP는 행위를 평가하며 콘텐츠를 평가하지 않습니다).

## Limitations and Discussion

논문이 명시하는 주요 한계는 다음과 같습니다.

**Non-bypassability는 플랫폼 신뢰에 의존합니다.** 프레임워크가 훅을 올바르게 호출해야만 집행이 작동합니다. 이는 알고리즘만으로 증명 불가능한 부분으로, Trusted Execution Environment(TEE) 기반 원격 증명이 이 가정을 강화할 수 있습니다.

**CTF 평가의 외적 타당성**. Vault 참가자는 소셜 엔지니어링 방향으로 자기 선택적이며, APT 수준 공격자에게 결과가 일반화되지 않을 수 있습니다. 단일 도메인(뱅킹) 테스트로, 코드 실행이나 다중 에이전트 위임으로의 일반화는 미시연.

**ESCALATE 경로 미구현**: 사람 개입(human-in-the-loop)을 위한 ESCALATE는 명세에는 있으나 참조 구현에서는 아직 미구현입니다.

**정책 표현력의 트레이드오프**: OAP 정책은 결정 가능한 단편(비교, 집합 소속)으로 제한됩니다. "최근 30일 평균 이하이고 금액이 특정 조건을 만족"하는 복잡한 조건은 정책 합성이나 확장이 필요합니다. 이는 표현력 대신 보장을 선택한 의도적 설계입니다.

## Conclusion

이 논문은 AI 에이전트 안전의 핵심 공백 — tool call 수준에서의 결정론적 사전 인가 — 을 명확히 정의하고, 이를 해결하기 위한 오픈 명세 OAP를 제안합니다. 모델 정렬이 확률적으로 동작하고 사후 평가가 회고적인 데 반해, OAP는 동일 입력에 항상 동일 결정을 내리는 결정론적 집행을 제공합니다.

실제 적대적 테스트베드 결과는 논점을 날카롭게 보여줍니다: 허용적 정책 아래서는 소셜 엔지니어링의 74.6%가 성공하지만, 제한적 OAP 정책 아래서는 879회 시도 모두 차단되었습니다. 모델이 설득되더라도 정책이 행위를 막는 것입니다.

OAP가 흥미로운 이유는 보안 도구에 그치지 않기 때문입니다. 지출 한도를 집행하는 동일한 인프라가 품질 게이트, 운영 계약, 컴플라이언스 통제도 집행할 수 있습니다. "AI 에이전트는 비밀번호는 있지만 허가증이 없다"는 이 논문의 핵심 문제 제기는, 자율 에이전트가 점점 더 실제 행위를 취하는 시대에 우리가 먼저 답해야 할 질문입니다.
