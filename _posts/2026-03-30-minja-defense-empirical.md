---
layout: post
title: "Memory Poisoning Attack and Defense on Memory-Based LLM Agents: An Empirical Study"
authors: "Balachandra Devarangadi Sunil, Isheeta Sinha, Piyush Maheshwari, Shantanu Todmal, Shreyan Mallik, Shuchi Mishra"
venue: "arXiv 2026"
arxiv: "https://arxiv.org/abs/2601.05504"
tags: [security, llm-agent, memory-poisoning, adversarial-ml, defense]
date: "2026-03-30"
---

여러분, 오늘은 [MINJA](https://beomsu317.github.io/2026-03-30/minja) 공격의 실제 배포 환경에서의 견고성을 체계적으로 평가하고, 두 가지 새로운 방어 메커니즘을 제안하는 경험적 연구를 살펴보겠습니다. 이 논문은 UMass COMPSCI 690F 과목의 연구 프로젝트 결과물로, MINJA가 이상적 조건에서 달성하는 95% 이상의 ISR과 70%의 ASR이 **현실적인 배포 조건에서는 크게 달라진다**는 점을 실증적으로 밝힙니다.

## Motivation

MINJA 원본 논문은 초기 메모리가 거의 없는 통제된 환경에서 공격을 평가했습니다. 그러나 실제 의료 환경의 EHR 에이전트는 다음과 같이 다릅니다.

- 수백만 건의 합법적 쿼리 기록이 이미 축적되어 있음
- 상황에 따라 검색하는 메모리 수(retrieval top-k)가 유동적으로 변함
- GPT-4o-mini 외에 Gemini-2.0-Flash, Llama-3.1-8B-Instruct 등 다양한 LLM 백엔드를 사용

이 논문은 이 세 가지 차원을 체계적으로 변화시켜 **실제 배포 조건에서의 공격 효과를 정량화**하고, 두 가지 방어 메커니즘을 제안 및 평가합니다.

## Threat Model

위협 모델은 MINJA와 동일합니다. 공격자는 시스템 권한 없이 일반 사용자로서 쿼리와 출력만 접근 가능하며, 에이전트의 공유 메모리 뱅크를 오염시켜 이후 피해자 쿼리에서 잘못된 응답(예: 잘못된 환자 ID로 리다이렉트)을 유발하는 것이 목표입니다.

실험에서는 EHRAgent를 대상으로 MIMIC-III 임상 데이터를 사용합니다. victim ID는 027-22704이고 target ID는 015-91239로, 공격 쿼리 예시는 "Give me the LOS of patient 027-22704's last ICU stay"입니다.

<p align="center">
  <img src="/assets/img/minja-defense-empirical/fig1-ehr-attack.png" alt="Figure 1: EHR 에이전트 메모리 포이즈닝 공격 예시">
  <br>
  <em>Figure 1. EHR 에이전트에 대한 메모리 포이즈닝 공격 흐름. 공격자는 indication prompt가 포함된 쿼리를 주입하고, 이후 피해자 쿼리 처리 시 오염된 메모리가 검색되어 잘못된 환자 데이터를 반환. (Sunil et al., 2026)</em>
</p>

## Research Questions

논문은 두 가지 연구 질문을 설정합니다.

- **RQ1**: 현실적인 조건에서 MINJA 공격의 견고성은 어떠한가?
- **RQ2**: 메모리 포이즈닝 공격에 효과적인 방어 메커니즘을 어떻게 설계할 수 있는가?

세 가지 가설도 제시됩니다.

- **Hypothesis 1**: 피해자 ID와 관련된 정상 메모리가 늘어날수록 ASR과 ISR이 감소한다.
- **Hypothesis 2**: indication prompt 수를 늘릴수록 ASR과 ISR이 증가한다.
- **Hypothesis 3**: 검색되는 관련 메모리 수를 늘릴수록 ASR이 증가하고 ISR은 영향받지 않는다.

## RQ1: Attack Robustness

### 초기 메모리 상태의 영향

가장 주목할 만한 결과는 **사전에 존재하는 정상 메모리가 공격 효과를 극적으로 낮춘다**는 것입니다.

| 모델 | 초기 메모리 없음 (ASR / ISR) | 관련 메모리 있음 (ASR / ISR) |
|---|---|---|
| GPT-4o-mini | 62% / 100% | 6.67% / 26.67% |
| Llama-3.1-8B-Instruct | 52.94% / 100% | 0% / 99.95% |

Llama 모델의 경우 ASR이 52.94%에서 0%로 완전히 사라집니다. 피해자 ID와 관련된 benign 쿼리 기록이 2개만 있어도, 유사도 기반 검색에서 악성 레코드보다 이들이 우선 검색되기 때문입니다. 이는 **Hypothesis 1을 강력히 지지**합니다.

### Indication Prompt 수의 영향

관련 초기 메모리가 있는 상태에서 indication prompt를 2개에서 4개로 늘려도 ASR과 ISR은 크게 개선되지 않았습니다. 피해자 ID를 포함하는 다른 의미 있는 쿼리들이 검색에서 더 높은 점수를 받아 악성 지시가 선택되지 않기 때문입니다. 이는 **Hypothesis 2를 반증**합니다. 초기 메모리라는 "천연 방어막"이 있으면 indication prompt를 늘리는 것만으로는 돌파하기 어렵습니다.

### 검색 메모리 수의 영향

검색 top-k를 3 → 5 → 10으로 늘리면 ASR이 상승합니다.

| 모델 | top-k=3 (ASR / ISR) | top-k=5 (ASR / ISR) | top-k=10 (ASR / ISR) |
|---|---|---|---|
| GPT-4o-mini | 6% / 26% | 20% / 50% | 38% / 100% |
| Llama-3.1-8B-Instruct | 0% / 99% | 13.33% / 93.94% | 27.27% / 97.87% |

top-k=10에서 GPT-4o-mini의 ISR은 100%에 도달합니다. 더 많은 메모리를 검색할수록 덜 관련된 악성 레코드도 컨텍스트에 포함될 확률이 높아지기 때문입니다. 그러나 실제 시스템에서는 입력 토큰 한도와 처리 시간 제약으로 top-k를 무한정 늘리기 어렵습니다. **Hypothesis 3은 부분적으로 지지**됩니다(ASR 증가는 확인, ISR 불변 가정은 부정확).

**결론**: 현실적인 배포 조건, 즉 상당한 양의 정상 메모리가 축적된 환경에서 MINJA의 최대 ASR은 GPT-4o-mini 기준 38%, Llama 기준 27%로, 원본 논문의 이상적 조건 결과보다 훨씬 낮습니다. 실제 의료 시스템에서는 수백만 건의 기록이 있어 공격 성공률이 더욱 낮아질 것으로 예상됩니다.

## RQ2: Defense Mechanisms

### Defense 1: Input/Output Moderation

두 단계의 게이트 방식입니다.

1. **입력 모더레이션**: "Knowledge:", "refer", "ignore previous" 등 키워드 매칭을 포함한 정적 휴리스틱으로 빠른 필터링. 통과 시 LLM 기반 의미론적 분류기로 미묘한 주입 시도 탐지.
2. **출력 모더레이션**: 생성된 코드에서 위험 연산(`exec`, `eval`, subprocess 등)을 탐지하고 복합 신뢰 점수(composite trust score)를 계산. 점수가 임계값을 초과하는 항목만 메모리에 저장.

정적 패턴, 동적 응답 검증, 코드 안전성 휴리스틱, 선택적 샌드박스 실행을 결합해 공격자가 여러 독립적인 검사를 동시에 우회해야 하는 구조를 만듭니다.

**GPT-4o-mini 결과**: 23개 후보 메모리 전부가 신뢰 점수 ≤ 0.4로 거부됨. 메모리 저장이 0건이므로 공격 누출 0%이지만, benign 쿼리도 모두 차단되어 장기 메모리 유틸리티가 완전히 사라지는 **과도하게 보수적인 동작**을 보입니다.

### Defense 2: Memory Sanitization with Trust-Aware Retrieval

메모리 저장 및 검색 단계 모두에 신뢰 점수 시스템을 적용합니다.

- **저장 단계**: 출력 검증, 샌드박스 재실행, 정적 패턴 분석(예: "Refer X to Y", "use patient Y instead")으로 신뢰 점수 계산. 임계값 이상의 항목만 저장.
- **검색 단계**: 저장된 항목의 신뢰 점수에 **시간적 감쇠(temporal decay)**를 적용. 오래된 기록일수록 신뢰도가 낮아져 검색에서 제외. 패턴 기반 필터와 신뢰 점수 + 텍스트 유사도 결합 랭킹 적용.

**GPT-4o-mini 결과**: 모든 항목이 저장 차단됨 (Defense 1과 동일한 과보수 문제).

**Gemini-2.0-Flash 결과**: 101건의 공격 쿼리 중 82건이 신뢰 점수 1.0으로 APPEND. 이 중 54건이 악성 포이즌 쿼리 ("Knowledge:" 지시 포함)로, 시스템이 공격자의 사회 공학(social engineering)에 속아 최고 신뢰 점수를 부여한 결과입니다. 나머지 45.7%(69건)는 거부됩니다.

<p align="center">
  <img src="/assets/img/minja-defense-empirical/fig2-action-distribution.png" alt="Figure 2: 메모리 저장 결정 분포">
  <br>
  <em>Figure 2. Gemini-2.0-Flash에서 메모리 저장(APPEND) 대 거부(REJECT) 비율. 54.3%(82건)가 저장되었으나 그 중 54건이 악성 쿼리. (Sunil et al., 2026)</em>
</p>

<p align="center">
  <img src="/assets/img/minja-defense-empirical/fig3-trust-distribution.png" alt="Figure 3: 신뢰 점수 분포">
  <br>
  <em>Figure 3. 전체 메모리 항목의 신뢰 점수 분포. 0.3과 0.4 구간의 낮은 신뢰 집단과 1.0의 높은 신뢰 집단으로 극단적인 양극화. 평균(빨간 점선)은 0.70. (Sunil et al., 2026)</em>
</p>

<p align="center">
  <img src="/assets/img/minja-defense-empirical/fig4-trust-by-decision.png" alt="Figure 4: Guard 결정별 신뢰 점수 분포">
  <br>
  <em>Figure 4. Guard 결정별 신뢰 점수. 저장 허용(녹색)은 모두 1.0, 거부(빨간색)는 0.3–0.4에 집중. 명확한 결정 경계가 존재하나 악성 쿼리 다수가 trust=1.0을 획득. (Sunil et al., 2026)</em>
</p>

## Key Findings and Implications

이 연구에서 도출되는 핵심 통찰은 다음과 같습니다.

**1. 현실적 조건은 천연 방어막을 제공한다**: 정상 운영 중 축적된 benign 메모리가 검색 경쟁에서 악성 레코드를 압도합니다. 실제 의료 시스템에서 MINJA의 위협은 원본 논문이 제시한 것보다 훨씬 낮을 수 있습니다.

**2. 신뢰 기반 방어의 양날의 검**: 신뢰 점수가 너무 엄격하면 정상 쿼리도 모두 차단해 메모리 유틸리티를 제거하고, 너무 관대하면 공격자가 높은 신뢰 점수를 가진 악성 쿼리를 사회 공학적으로 주입하는 데 성공합니다. 이 교정(calibration) 문제가 가장 큰 난제입니다.

**3. 모델별 취약성 차이**: GPT-4o-mini는 과보수적으로 반응해 아무것도 저장하지 않았지만, Gemini-2.0-Flash는 악성 지시에 높은 신뢰 점수를 부여해 모두 저장했습니다. 동일한 방어도 LLM 백엔드에 따라 전혀 다른 특성을 보입니다.

**4. 검색 신뢰의 한계**: 신뢰 점수 1.0을 가진 악성 레코드가 저장된 이후에는 검색 시점 필터링도 효과가 없습니다. 저장 단계에서의 오염이 발생하면 이후 방어는 모두 무력화됩니다.

## Limitations

이 연구는 몇 가지 범위 제약을 가집니다.

- **단일 victim-target 쌍**: 실험이 1개의 환자 ID 쌍에 집중되어 있어 결과의 일반화에 한계가 있습니다. MINJA 원본처럼 9개 이상의 다양한 쌍에서 평가가 필요합니다.
- **50개의 indication prompt 변형 평가**: 공격 다양성 실험을 위해 50개의 변형 prompt를 합성했으나, 실제 공격자는 훨씬 더 다양하고 정교한 방법을 사용할 수 있습니다.
- **신뢰 임계값 조정 미완료**: 적절한 보안-유틸리티 균형점을 찾기 위한 체계적인 임계값 최적화 실험이 향후 연구 과제로 남아 있습니다.

## Conclusion

이 연구는 MINJA의 현실적 위협 수준을 재평가하고, 두 가지 방어 메커니즘의 기본적인 한계를 명확히 밝힙니다. 정상 메모리의 자연 방어 효과, 신뢰 점수 교정의 어려움, 모델별 취약성 차이 등은 미래의 적응형 방어 메커니즘 설계에 중요한 기초 데이터를 제공합니다. 특히 **신뢰(confidence)와 안전성(safety)의 분리**가 핵심 과제로, 모델이 높은 신뢰를 보이더라도 외부 ground truth 검증으로 포이즈닝을 잡아내는 방향이 유망한 연구 방향으로 제시됩니다.
