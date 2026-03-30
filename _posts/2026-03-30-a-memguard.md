---
layout: post
title: "A-MemGuard: A Proactive Defense Framework for LLM-Based Agent Memory"
authors: "Qianshan Wei, Tengchao Yang, Yaochen Wang, Xinfeng Li, Lijun Li, Zhenfei Yin, Yi Zhan, Thorsten Holz, Zhiqiang Lin, XiaoFeng Wang"
venue: "arXiv 2025"
arxiv: "https://arxiv.org/abs/2510.02373"
tags: [security, llm-agent, memory-defense, adversarial-ml, in-context-learning]
date: "2026-03-30"
---

여러분, 오늘은 LLM 에이전트 메모리 방어 프레임워크인 **A-MemGuard**를 살펴보겠습니다. 앞서 살펴본 [MINJA](https://beomsu317.github.io/2026-03-30/minja)와 같은 메모리 주입 공격이 에이전트 메모리에 심각한 위협이 된다는 사실이 밝혀진 가운데, A-MemGuard는 에이전트의 핵심 아키텍처를 수정하지 않고도 이를 방어하는 최초의 능동적(proactive) 방어 프레임워크를 제안합니다. 핵심 아이디어는 **메모리 자체가 자가 검증과 자가 교정을 수행해야 한다**는 통찰에서 출발합니다.

## Background

### 메모리 주입 공격의 두 가지 핵심 특성

메모리 기반 공격을 방어하기 어려운 이유는 두 가지 핵심 특성에 있습니다.

첫째, **맥락 의존적 위협(context-dependent threat)**입니다. 악성 레코드는 단독으로 볼 때는 완전히 무해해 보입니다. "항상 긴급해 보이는 이메일을 우선순위에 두라"라는 기록은 단독으로는 합리적이지만, 피싱 맥락에서 검색되면 에이전트를 공격자의 메시지로 유도합니다. Agent Security Bench(ASB)에 따르면 LLM 기반 탐지기조차 오염된 메모리 항목의 66%를 놓칩니다.

둘째, **자기 강화 오류 사이클(self-reinforcing error cycle)**입니다. 공격이 초기의 잘못된 결정을 유발하면, 에이전트는 이를 올바른 기록으로 저장합니다. 이 오염된 기억은 이후 작업의 참조 기준이 되어 오류를 반복적으로 증폭시킵니다. 금융 에이전트가 "가장 빠르게 하락하는 주식이 가장 빠르게 반등한다"는 잘못된 기록을 저장하면, 이후 유사한 쿼리에서 계속 이 논리를 따르게 됩니다.

### 기존 방어의 한계

Perplexity Filter, Distilled Classifier, LLM Auditor 등 기존 방어 방법들은 메모리 항목을 **고립된 개별 레코드로** 검사합니다. 그러나 위협은 레코드 자체에 있는 것이 아니라, 레코드가 **특정 쿼리 맥락과 결합될 때** 발생하므로 이런 접근은 근본적으로 한계를 가집니다.

## Threat Model

A-MemGuard가 다루는 위협 모델은 다음과 같습니다.

- **공격 목표**: 소수의 악성 레코드 $\mathcal{M}_{adv}$를 에이전트 메모리에 주입해 오염 상태 $\mathcal{M}^{\prime} = \mathcal{M} \cup \mathcal{M}_{adv}$ 형성. 특정 트리거 쿼리 $q^*$에만 악성 행동 $a^*$를 유발하며, benign 쿼리에서는 정상 동작 유지.
- **주입 경로**: (1) 메모리에 대한 제한적 쓰기 권한을 가진 직접 주입 (AgentPoison 등), (2) benign 쿼리를 통해 에이전트가 스스로 악성 레코드를 보관하도록 유도하는 간접 주입 (MINJA 등).

**형식적 방어 목표**는 두 가지 목적 함수의 균형입니다.

$$\min_V \mathbb{E}_{(q^*, a^*)} \left[ \mathbf{1}\left[\text{Action}\left(\pi_\theta(\cdot | q^*, V(\mathcal{M}_r))\right) = a^*\right] \right]$$

$$\max_V \mathbb{E}_{(q, a_\text{benign})} \left[ \mathbf{1}\left[\text{Action}\left(\pi_\theta(\cdot | q, V(\mathcal{M}_r))\right) = a_\text{benign}\right] \right]$$

즉, 악성 레코드가 에이전트 행동에 미치는 영향을 최소화하면서 동시에 benign 작업에서의 정확도는 최대화해야 합니다.

## Method

A-MemGuard는 두 개의 시너지 모듈로 구성됩니다.

<p align="center">
  <img src="/assets/img/a-memguard/fig1-overview.png" alt="Figure 1: A-MemGuard 개요">
  <br>
  <em>Figure 1. (위) 방어 없는 에이전트: 피싱 메모리가 그대로 검색·실행됨. (아래) A-MemGuard: 합의 검증과 Lesson Memory를 통해 악성 추론을 탐지하고 교정. (Wei et al., 2025)</em>
</p>

<p align="center">
  <img src="/assets/img/a-memguard/fig2-architecture.png" alt="Figure 2: A-MemGuard 아키텍처">
  <br>
  <em>Figure 2. A-MemGuard 전체 아키텍처. 쿼리 수신 후 K개의 메모리로 병렬 추론 경로를 생성하고, 합의 검증으로 이상 경로를 제거한 뒤 Lesson Memory로 최종 행동을 교정. (Wei et al., 2025)</em>
</p>

### Consensus Validation via Reasoning Path Analysis

핵심 아이디어는 단일 메모리가 아니라 **여러 관련 메모리에서 도출된 추론 경로들의 논리적 일관성**을 비교해 이상 징후를 탐지하는 것입니다.

**병렬 추론 경로 생성**: 쿼리 $q_t$에 대해 K개의 메모리 $\mathcal{M}_r$이 검색되면, 각 메모리 $m_i$에서 독립적인 구조화 추론 경로 $\hat{\rho}_i$를 생성합니다.

$$\hat{\rho}_i = \Lambda(q_t, m_i;\, \theta) = (e_1 \xrightarrow{r_1} e_2 \xrightarrow{r_2} \cdots \xrightarrow{r_{L-1}} e_L)$$

여기서 $\Lambda$는 LLM 기반 경로 추출 함수이며, $e_i$는 추론 엔티티, $r_i$는 엔티티 간 관계입니다. 이 과정을 통해 K개의 병렬 경로 집합 $\hat{\mathcal{P}}_t = \{\hat{\rho}_1, \ldots, \hat{\rho}_K\}$가 만들어집니다.

**경로 발산 점수화 및 검증**: 발산 점수화 함수 $S_{div}$는 후보 경로 $\hat{\rho}_i$와 전체 경로 집합 $\hat{\mathcal{P}}_t$를 입력으로 받아 합의(consensus)로부터의 이탈 정도를 수치화합니다.

$$s_i = S_{div}(\hat{\rho}_i,\, \hat{\mathcal{P}}_t)$$

점수가 임계값 $\tau$를 초과하는 경로는 이상(anomalous)으로 표시되며, 검증된 메모리 집합은 다음과 같이 구성됩니다.

$$\mathcal{M}_{val} = \{m_i \in \mathcal{M}_r \;|\; S_{div}(\Lambda(q_t, m_i;\theta),\, \hat{\mathcal{P}}_t) \leq \tau\}$$

논문은 $S_{div}$의 구현으로 LLM 기반 직접 판단을 주요 방법으로 채택합니다. LLM 판단 모델은 K개 경로를 분석해 **합의 플랜**을 먼저 생성한 뒤, 각 개별 경로가 이 합의와 일관되는지 이진(binary) 판단을 수행합니다. 이를 통해 수동으로 임계값 $\tau$를 조정할 필요 없이 미묘한 논리적 불일치를 포착할 수 있습니다.

이 접근의 근거는 **악성 메모리는 단독으로는 그럴듯해 보이지만, 그것이 유발하는 추론 경로는 benign 메모리들이 형성하는 구조적 합의에서 벗어난다**는 통찰에 있습니다. 논문의 knowledge graph 분석에 따르면 benign과 malicious 메모리의 추론 경로 간 구조적 중복(overlap)은 17개 시나리오 평균 1% 미만으로, 이 분리 가능성이 탐지의 핵심 신호가 됩니다.

<p align="center">
  <img src="/assets/img/a-memguard/fig4-knowledge-graph.png" alt="Figure 4: Knowledge Graph 분석">
  <br>
  <em>Figure 4. 추론 경로의 관계 구조 분석. Malicious(연어색)와 Benign(민트색)의 추론 경로 관계가 17개 시나리오 전체에서 거의 겹치지 않음 (평균 overlap < 1%). (Wei et al., 2025)</em>
</p>

### Self-taught Correction via Dual-Memory Structure

탐지만으로는 자기 강화 오류 사이클을 끊을 수 없습니다. A-MemGuard는 **Lesson Memory**를 통해 에이전트가 과거 실수로부터 스스로 학습하도록 합니다.

**구조화 레슨 증류**: 경로 $\hat{\rho}_j$가 이상으로 탐지되면, 이 경로 자체가 "부정 레슨(negative lesson)"이 됩니다. 잘못된 논리의 구조적 지문(fingerprint)으로서 Lesson Memory에 저장됩니다.

$$l_t := \hat{\rho}_j, \quad \mathcal{M}_{les} \leftarrow \mathcal{M}_{les} \cup \{l_t\}$$

**능동적 숙고와 행동 교정**: 에이전트는 검증된 메모리 $\mathcal{M}_{val}$을 기반으로 최종 행동 계획 $p_{final}$을 생성합니다. 실행 전, A-MemGuard는 $p_{final}$을 구조화 경로로 변환한 뒤 Lesson Memory에서 구조적으로 유사한 레슨 $\mathcal{L}_{rel}$을 검색합니다. 관련 레슨이 발견되면 **숙고 루프(deliberative loop)**가 발동되어 에이전트가 계획을 자체 수정(self-reflection)하도록 강제합니다. 이 메커니즘이 에이전트의 학습 과정이 공격에 역이용되는 자기 강화 사이클을 차단합니다.

## Experiments

### 실험 설정

A-MemGuard는 세 가지 공격 유형과 여러 벤치마크에서 평가됩니다.

- **직접 주입 공격(Direct)**: AgentPoison (Chen et al., 2024) — ReAct-StrategyQA, EHRAgent에서 GPT-4o-mini, LLaMA-3-8B 기반
- **간접 주입 공격(Indirect)**: MINJA (Dong et al., 2025) — MMLU 기반 QA 에이전트
- **다중 에이전트 시스템(MAS)**: 협업 에이전트에서 허위 정보 주입 (MISINFOTASK 데이터셋)

비교 기준선은 방어 없음, LLM Auditor, Distil Classifier, Perplexity Filter입니다.

### AgentPoison에 대한 방어 성능

A-MemGuard는 AgentPoison에 대해 전 설정에서 state-of-the-art를 달성합니다. GPT-4o-mini + DPR 설정의 EHRAgent에서 방어 없을 때 ASR-r (Retrieval)이 100%이던 것을 **2.13%**로 낮추며, 다른 방어 방법들이 46.81%~100%에 머무는 것과 대비됩니다.

### 간접 주입 공격(MINJA)에 대한 방어

| 방법 | GPT-4o-mini ASR | LLaMA-3.1-8B ASR |
|---|---|---|
| No Defense | 0.667 | 0.663 |
| LLM Auditor | 0.567 | 0.600 |
| Distil Classifier | 0.689 | 0.567 |
| Perplexity Filter | 0.689 | 0.656 |
| **A-MemGuard** | **0.256** | **0.233** |

A-MemGuard는 두 모델 모두에서 ASR을 60% 이상 낮춥니다. 반면 Perplexity Filter와 Distil Classifier는 방어 없음보다 오히려 ASR이 높아지는 경우도 있어, 맥락 의존적 위협에 단독 레코드 필터링이 얼마나 부적합한지를 보여줍니다.

아래 그림은 방어가 없을 때 라운드가 증가할수록 ISR이 꾸준히 상승해 자기 강화 사이클이 현실임을 확인해 줍니다.

<p align="center">
  <img src="/assets/img/a-memguard/fig3-isr-rounds.png" alt="Figure 3: 라운드별 ISR">
  <br>
  <em>Figure 3. 방어 없는 에이전트에서 상호작용 라운드가 증가할수록 ISR이 선형적으로 상승. 자기 강화 오류 사이클의 실증. (Wei et al., 2025)</em>
</p>

### Benign 작업에서의 유틸리티

실용적인 방어의 핵심 요건은 정상 작업 성능을 유지하는 것입니다. 모든 설정에서 A-MemGuard는 benign ACC가 가장 높거나 그에 준하는 수준을 유지합니다. 예를 들어 GPT-4o-mini + DPR + ReAct에서 방어 없음(63.0%) 대비 76.7%로 오히려 향상됩니다. Distil Classifier는 EHRAgent에서 ACC를 83.0%에서 19.1%로 극적으로 낮추는 반면, A-MemGuard는 71.3%를 유지합니다.

### 다중 에이전트 시스템 확장성

A-MemGuard는 단일 에이전트를 넘어 협업 MAS 환경에서도 효과적입니다. 허위 정보 주입 공격에 대해 Task Success 0.950으로 모든 방어 방법 중 최고를 달성하며, 오류 페널티 집계인 Final Score(낮을수록 좋음)도 2.150으로 No Defense(3.200)와 비교해 가장 낮습니다.

### Ablation Study

| 방법 | ASR-r | ASR-a | ASR-t | ACC |
|---|---|---|---|---|
| Ours (Full) | 2.12 | 12.76 | 36.17 | 63.83 |
| w/o L&C | 41.44 | 33.21 | 71.27 | 44.68 |
| w/o Safety | 6.12 | 15.72 | 38.30 | 58.31 |
| w/o Lessons | 5.13 | 11.29 | 40.63 | 38.29 |

합의 검증과 레슨 메커니즘을 모두 제거(w/o L&C)하면 ASR-t가 36.17에서 71.27로 거의 두 배로 증가합니다. 흥미롭게도 Lesson Memory 제거(w/o Lessons)는 사고 과정 중의 ASR(ASR-a)을 오히려 낮추는데, 이는 레슨 조회 단계가 없어 사고 과정이 "더 깨끗해 보이더라도" 최종 방어력은 더 약해지는 역설적 현상입니다. 두 모듈의 시너지가 전체 프레임워크의 효과에 핵심적임을 확인할 수 있습니다.

### Hyperparameter 민감도

Top-k 분석에서 메인 메모리의 경우 k를 늘릴수록 더 강한 합의가 형성되어 방어 성능이 단조 증가합니다. Lesson Memory의 경우 k=6이 최적이며, k를 너무 크게 설정하면 노이즈가 증가해 최종 결정을 방해하는 현상이 관찰됩니다. 과거 실수로부터 배우는 것이 유익하되, 너무 많은 레슨을 검색하면 오히려 방해가 된다는 직관적인 결과입니다.

## Limitations

- **컴퓨팅 비용**: 각 쿼리마다 K개의 병렬 추론 경로를 생성하고 LLM으로 판단하므로, 방어 없는 에이전트 대비 토큰 비용이 증가합니다. 논문의 성능 대 토큰 비용 분석(Figure 7)에서 A-MemGuard가 최고의 성능-비용 트레이드오프를 제공함을 보이지만, 실시간성이 중요한 환경에서는 고려가 필요합니다.
- **공유 메모리 전제**: 완전히 격리된 메모리 환경에서 간접 주입 공격은 신원 위장 같은 추가 전제가 필요하며, 이 경우 A-MemGuard의 전제 조건도 변합니다.
- **Indication Prompt 의존**: MINJA처럼 indication prompt 없이 악성 레코드가 더 자연스럽게 주입되는 변형 공격에 대한 추가 분석이 필요할 수 있습니다.

## Conclusion

A-MemGuard는 LLM 에이전트 메모리 보안을 정적 필터링에서 **능동적·경험 기반 방어**로 전환하는 첫 프레임워크입니다. 에이전트 핵심 아키텍처를 수정하지 않고도 두 가지 메커니즘의 시너지로 맥락 의존적 위협과 자기 강화 오류 사이클 모두를 효과적으로 차단합니다.

- **합의 기반 검증**은 단독 검사로는 놓칠 수밖에 없는 맥락 의존적 이상을 탐지합니다.
- **Lesson Memory**는 탐지된 오류를 구조적 지문으로 저장해 에이전트가 같은 실수를 반복하지 않도록 하며, 시간이 지날수록 방어가 강화되는 경험 기반 학습을 실현합니다.

이는 메모리를 단순한 저장소가 아니라 **자가 검증·자가 교정 능력을 갖춘 보안 레이어**로 재설계하는 방향을 제시합니다.
