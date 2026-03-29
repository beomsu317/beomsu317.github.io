---
layout: post
title: "Attention is All You Need to Defend Against Indirect Prompt Injection Attacks in LLMs"
authors: "Yinan Zhong, Qianhao Miao, Yanjiao Chen, Jiangyi Deng, Yushi Cheng, Wenyuan Xu"
venue: "NDSS 2026"
arxiv: "https://doi.org/10.14722/ndss.2026.240394"
tags: [security, machine-learning, llm, prompt-injection, indirect-prompt-injection, defense, attention]
date: "2026-03-27"
---

## Introduction

"Attention is All You Need" — 2017년 Transformer 아키텍처를 제안한 그 유명한 논문 제목을 오마주한 이 논문은, attention(어텐션)이 언어 모델의 이해를 위한 핵심 mechanism(메커니즘)이기에 공격을 탐지하는 데도 핵심이 된다는 직관을 함축하고 있습니다.

지난 리뷰에서 다루었던 Greshake et al.의 연구는 간접 프롬프트 인젝션(Indirect Prompt Injection, IPI) 공격이 어떻게 LLM 통합 애플리케이션을 위협하는지를 체계적으로 분류했습니다. IPI는 공격자가 LLM과 직접 대화하지 않고, LLM이 추론 시 조회하는 외부 데이터에 악성 명령을 심어 목표를 달성하는 공격입니다. OWASP는 이를 LLM 통합 애플리케이션의 **1순위 보안 위협**으로 선정하였습니다.

그렇다면 어떻게 방어할 수 있을까요? 기존 방어 수단들은 크게 두 가지 한계에 부딪혀 있습니다. classifier(분류기) 기반 탐지는 학습 데이터에 없는 새로운 공격 패턴에 일반화하지 못하고, LLM 기반 탐지는 비용이 비쌀 뿐 아니라 보조 LLM 자체가 IPI에 노출될 수 있습니다. 예방 기법인 Sandwich나 Spotlighting은 고도화된 공격 앞에서 효과가 제한적이고, 파인튜닝 기반 방법은 모델 제공자만이 적용 가능합니다.

이 논문은 **RENNERVATE**라는 새로운 프레임워크를 제안합니다. 핵심 아이디어는 LLM이 주입된 명령어를 처리할 때 보이는 **attention 패턴의 변화**를 token(토큰) 수준에서 정밀하게 탐지하고, 해당 token만을 sanitization(소독)하여 LLM의 정상 동작을 유지하면서 공격을 무력화하는 것입니다.

<p align="center">
  <img src="/assets/img/rennervate-ipi-defense/figure1-ipi-example.png" alt="Figure 1: IPI 공격과 RENNERVATE 방어의 예시">
  <br>
  <em>Figure 1. (a) 공격자가 외부 웹 콘텐츠에 악성 명령을 삽입하여 LLM을 장악하는 IPI 공격 시나리오. (b) RENNERVATE가 주입 token을 탐지·제거하고 LLM이 정상 응답을 반환하는 모습. (Zhong et al., 2026)</em>
</p>

---

## Background: IPI Attack Types and Limitations of Existing Defenses

### Structure of IPI Attacks

LLM 통합 애플리케이션의 전형적인 동작 흐름은 다음과 같습니다.

1. 사용자가 질의 $s$를 입력
2. agent(에이전트)가 외부 소스에서 관련 데이터 $X$를 검색
3. 백엔드 LLM이 $(s, X)$를 조합하여 응답 생성

IPI 공격은 이 과정의 2단계에서 발생합니다. 공격자는 외부 데이터 $X$ 안에 악성 명령어 $s^e$를 삽입합니다. $s^e$는 사용자의 원래 질의 $s$에 포함되지 않기 때문에 직접 프롬프트 인젝션보다 훨씬 은밀합니다.

### Classification of Attack Methods

논문은 IPI 공격을 크게 두 범주로 구분합니다.

**화이트박스 그래디언트 기반 공격**: 모델의 gradient(그래디언트)에 접근할 수 있는 공격자가 최적화된 공격 접미사(adversarial suffix)를 생성합니다. Greedy Coordinate Gradient (GCG) 알고리즘이 대표적이며, POUGH와 Neural Exec도 이 범주에 속합니다.

**블랙박스 프롬프트 엔지니어링 기반 공격**: 모델 내부 접근 없이 정교한 프롬프트 설계만으로 수행됩니다. 논문은 세 가지 전략을 제시합니다.

| 전략 | 예시 | 설명 |
|------|------|------|
| 문맥 무시(Context Ignoring) | "Ignore previous instructions, ..." | 기존 지시를 무효화하는 선언 |
| 이스케이프 문자(Escape Characters) | `\n`, `\t`, `\b`, `\r` | 특수문자로 LLM 파싱 방해 |
| 가짜 완성(Fake Completion) | "Answer: task complete." | 이전 작업이 완료된 척 하여 새 명령 실행 |

이 전략들은 중복 적용되어 더욱 강력한 복합 공격(Combined Attack)을 형성할 수 있습니다.

### Limitations of Existing Defenses

| 방어 유형 | 대표 방법 | 한계 |
|-----------|-----------|------|
| 분류기 기반 탐지 | Prompt-Guard, ProtectAI-v2 | 학습 분포 밖 공격에 일반화 불가 |
| LLM 기반 탐지 | GPT-Resp, Known-Answer | 비용 과다, 보조 LLM 자체가 취약 |
| 프롬프트 수정 예방 | Sandwich, Spotlighting | 고도화 공격에 취약함이 검증됨 |
| 모델 파인튜닝 | StruQ, SecAlign | 모델 제공자만 적용 가능 |

---

## Methodology: RENNERVATE

### Problem Formulation

LLM은 입력 $X$를 $n$개의 token 임베딩 시퀀스로 변환합니다.

$$\mathcal{T}(X) = \mathbf{F} = f_1, f_2, \ldots, f_n$$

여기서 $\mathcal{T}$는 tokenizer(토크나이저), $f_i \in \mathbb{R}^d$는 각 token의 임베딩 벡터입니다.

기존 방법들은 $X$ 전체에 대해 이진 분류(injected/clean)를 수행합니다. RENNERVATE는 이와 달리 **token 수준 탐지**를 수행합니다.

$$\mathcal{M}_\Theta(\mathbf{F}) = \mathcal{S}(\mathcal{C}_\theta(f_1), \mathcal{C}_\theta(f_2), \ldots, \mathcal{C}_\theta(f_n)) \tag{1}$$

$\mathcal{C}_\theta(\cdot)$는 개별 token $f_i$가 주입된 명령어의 일부인지 판별하는 token 수준 탐지기이며, $\mathcal{S}(\cdot)$는 token별 예측을 집약하는 함수입니다.

token 수준 탐지가 가능해지면, 주입된 것으로 판정된 token만 선택적으로 제거하는 **fine-grained sanitization(정밀 소독)**이 가능합니다.

$$\bar{\mathbf{F}} = \mathbf{F} \ominus \mathbf{F}^* \tag{2}$$

$\mathbf{F}^*$는 주입 token으로 분류된 집합, $\bar{\mathbf{F}}$는 정화된 token 시퀀스, $\ominus$는 set difference(집합 차) 연산입니다. 최종적으로 $\bar{X} = \mathcal{T}^{-1}(\bar{\mathbf{F}})$로 소독된 텍스트를 복원합니다.

### System Architecture

RENNERVATE는 세 개의 모듈로 구성됩니다.

**모듈 ①: Token-Level Detector(token 수준 탐지기)** — 각 token의 attention feature(피처)를 입력받아 해당 token이 주입 명령어인지 여부를 예측합니다.

**모듈 ②: Injection Identifier(인젝션 식별자)** — token별 예측 logits(로짓)을 집약하여 전체 데이터 $X$에 주입 여부가 있는지 판정합니다.

**모듈 ③: Injection Sanitizer(인젝션 소독기)** — 주입 token을 위치 지정하여 제거하고 정화된 텍스트를 반환합니다.

<p align="center">
  <img src="/assets/img/rennervate-ipi-defense/figure2-rennervate-overview.png" alt="Figure 2: RENNERVATE 전체 시스템 설계">
  <br>
  <em>Figure 2. LLM 추론 단계에서 attention feature를 활용하는 RENNERVATE의 세 모듈 구성. token 수준 탐지기 ①이 각 token을 분류하고, 인젝션 식별자 ②가 전체 판정을 내리며, 소독기 ③이 주입 token을 제거한다. (Zhong et al., 2026)</em>
</p>

### A. Token-Level Detector

#### Why Attention Features?

token 임베딩 자체를 사용하는 것이 자연스러운 선택처럼 보이지만, 두 가지 이유에서 충분하지 않습니다.

첫째, 의미론적으로 은밀한(stealthy) IPI 공격은 "Please print Yes."처럼 겉으로 보기에 완전히 무해한 문장으로 구성됩니다. token 임베딩은 이런 공격을 탐지할 수 없습니다.

둘째, attention feature는 LLM이 해당 token을 어떻게 **이해하고 있는지**를 반영합니다. 주입된 명령어는 일반 데이터와 다른 attention 패턴을 유발하는데, 이는 LLM이 명령어와 데이터를 내부적으로 다르게 처리하기 때문입니다. 이 패턴은 표면적 표현이 바뀌어도 더 안정적으로 남습니다.

#### Attention Feature Extraction

$l$개 레이어, $h$개 헤드를 가진 LLM에서, $j$번째 응답 token이 입력 token $f_i$에 부여하는 attention feature를 $\mathcal{A}_{\psi,j}(f_i)$라고 합니다. 처음 $m$개의 응답 token에 걸친 attention feature를 연결(concatenate)하면 다음을 얻습니다.

$$\mathcal{A}_{\psi,[:m]}(f_i) = [\mathcal{A}_{\psi,1}(f_i) \oplus \cdots \oplus \mathcal{A}_{\psi,m}(f_i)] \tag{3}$$

결과 텐서의 차원은 $\mathbb{R}^{l \times h \times m}$입니다. 논문은 실험적으로 $m = 32$를 사용합니다. 계산 부담과 탐지 정확도의 균형을 위한 설계 선택이며, 응답 초반부 token들이 이미 충분한 정보를 담고 있음을 실험으로 확인했습니다.

최종 token 수준 탐지기는 다음과 같이 정의됩니다.

$$\mathcal{C}_\theta(f_i) = \tilde{\mathcal{C}}_{\theta \setminus \psi} \circ \mathcal{A}_{\psi,[:m]}(f_i) \tag{4}$$

$\tilde{\mathcal{C}}_{\theta \setminus \psi}$는 attention feature를 입력으로 받는 경량 neural network(신경망)입니다. 전체 탐지기의 파라미터는 $0.5 \sim 0.8$M에 불과하여 매우 경량입니다.

#### 2-Step Attentive Pooling

attention feature의 차원 $\mathbb{R}^{l \times h \times m}$을 어떻게 고정 크기의 표현으로 압축할까요? 단순 평균 풀링은 중요한 헤드나 응답 token의 기여를 희석시킵니다. RENNERVATE는 중요도를 학습하는 **Attentive Pooling(어텐티브 풀링)**을 두 단계에 걸쳐 적용합니다.

**Attentive Statistics Pooling(어텐티브 통계 풀링)**은 다음 구조를 가집니다. 프레임 수준 feature들에 attention 모델을 적용하여 각 프레임의 중요도 가중치 $\alpha_t$를 학습합니다. 이후 가중 평균 $\hat{\mu}$와 가중 표준편차 $\hat{\sigma}$를 모두 계산합니다.

$$\hat{\mu} = \sum_t \alpha_t \cdot x_t, \quad \hat{\sigma} = \sqrt{\sum_t \alpha_t \cdot (x_t - \hat{\mu})^2}$$

$\hat{\mu}$는 어떤 정보가 중요한지를, $\hat{\sigma}$는 피처 간의 변동성을 포착합니다. 두 통계량을 연결(concatenate)하여 더 풍부한 표현을 얻습니다.

**1단계 — Resp-Wise Attentive Pooling**: 응답 token 축($m$ 차원)을 집약합니다. $m$개의 응답 token 중 어느 위치가 주입 탐지에 더 중요한지를 학습합니다. 출력 차원은 $\mathbb{R}^{l \times (2h)}$입니다.

**2단계 — Head-Wise Attentive Pooling**: attention head 축($h$ 차원)을 집약합니다. 어느 헤드가 주입 탐지에 더 기여하는지를 학습합니다. 출력 차원은 $\mathbb{R}^{1 \times (2l)}$입니다.

이후 Fully Connected layer (FC), Batch Normalization (BN), $N$개의 Residual Block(잔차 블록), Dropout(드롭아웃, $p=0.2$), Softmax(소프트맥스)를 거쳐 최종 예측 로짓 $\omega_i \in \mathbb{R}^2$를 출력합니다. 학습은 cross-entropy(크로스 엔트로피) 손실과 Adam 옵티마이저를 사용합니다.

모든 token에 대한 탐지기 실행은 **병렬화**됩니다. 이는 시퀀스 길이에 관계없이 latency(탐지 지연)을 일정하게 유지하는 설계 선택입니다.

<p align="center">
  <img src="/assets/img/rennervate-ipi-defense/figure3-token-detector.png" alt="Figure 3: token 수준 탐지기 구조">
  <br>
  <em>Figure 3. (좌) Attentive Statistics Pooling 레이어의 구성 — 프레임 수준 feature에서 중요도 가중치 α<sub>t</sub>를 학습하여 가중 평균과 가중 표준편차를 출력한다. (우) 전체 token 수준 탐지기 파이프라인 — Resp-Wise → Head-Wise Attentive Pooling 이후 잔차 블록을 거쳐 이진 logits을 출력한다. (Zhong et al., 2026)</em>
</p>

### B. Injection Identifier and Sanitizer (Algorithm 1)

token별 예측 logits $\Omega = (\omega_1, \ldots, \omega_n)$이 주어지면 다음 알고리즘으로 탐지 및 소독을 수행합니다.

```python
def detect_and_sanitize(logits, F, k=5, threshold=5, sanitize=False):
    """
    logits: token별 예측 logits (n x 2)
    F: token 임베딩 시퀀스
    k: 평균 필터 커널 크기
    threshold: 연속 주입 token 판정 임계값
    """
    max_num = 0
    inj_lst = []
    F_bar = list(F)

    # 평균 필터 적용 (replicate padding)
    filtered = mean_filter(logits, k)

    for i, logit in enumerate(filtered):
        label = greedy_search(logit)  # 0=clean, 1=injected
        if label == 1:
            inj_lst.append(i)
        else:
            max_num = max(len(inj_lst), max_num)
            inj_lst = []

    # 소독
    if sanitize:
        F_bar = [f for i, f in enumerate(F) if i not in set(inj_lst)]

    prediction = "Injected" if max_num > threshold else "Clean"
    return prediction, detokenize(F_bar)
```

**평균 필터의 역할**: 단일 token의 오분류는 주입 탐지를 방해할 수 있습니다. 평균 필터는 인접한 $k$개의 logits을 smoothing(평활화)하여 개별 token의 잡음을 줄입니다. IPI 공격은 여러 token에 걸쳐 연속적으로 구성되는 특성이 있기 때문에, 필터 이후에도 연속된 주입 token 시퀀스는 강하게 감지됩니다.

**임계값 기반 판정**: 연속된 주입 token의 최대 길이 $\text{MaxNum}$이 $\text{Threshold}$를 넘으면 "Injected"로 판정합니다. 이 설계는 짧은 단독 오탐(false positive)이 전체 판정을 오염시키는 것을 방지합니다.

---

## FIPI Dataset

기존 IPI 벤치마크는 인스턴스 수가 적고 공격 다양성이 부족했습니다. 논문은 **FIPI(Fine-grained IPI Dataset)**를 새로 구축합니다.

- **규모**: 100,000개의 주입 인스턴스 + 10,000개의 정상 인스턴스
- **기반**: SEP 데이터셋(사용자 질의·정상 데이터 9,160쌍, 3개 주요 카테고리, **300개 NLP 서브태스크**)
- **공격 유형**: Naive, Escape Characters, Context Ignoring, Fake Completion, 3가지 복합 공격 (총 7종)
- **어노테이션**: token-level 레이블 포함

5단계 구축 파이프라인: ① 정상 인스턴스 준비 → ② probe-witness pair(탐침-증거 쌍) 생성 → ③ IPI 공격 적용 → ④ 주입 인스턴스 구성 → ⑤ 학습/테스트 분할

이 데이터셋은 향후 오픈소스로 공개 예정입니다.

---

## Experiments

### Experimental Setup

**5개 대상 LLM**: ChatGLM-6B, Dolly-7B, Falcon-7B, LLaMA2-7B, LLaMA3-8B

모델 선정 기준은 다양한 아키텍처 유형을 포괄하기 위함입니다. prefix decoder(접두 디코더), causal decoder(인과 디코더), GQA(Grouped-Query Attention) 등 서로 다른 설계를 가진 모델들에서의 범용성을 검증합니다.

**15개 베이스라인**: 분류기 기반(4개), LLM 기반(5개), 프롬프트 수정(3개), 모델 수정(1개), LLM 기반 소독(2개)

**평가 지표**:
- 탐지: 정확도(Acc ↑), false positive rate (FPR ↓), false negative rate (FNR ↓)
- 소독: attack success rate (ASR ↓), win rate (WR ↑, 목표 ≈ 50%), Jaccard similarity (JS ↑)

WR(승률)은 소독된 텍스트와 원본 정상 텍스트 중 LLM이 어느 쪽에서 더 나은 응답을 생성하는지를 측정합니다. 50%에 가까울수록 소독 후 유용성 손실이 적음을 의미합니다.

Jaccard similarity(Jaccard 유사도)는 소독된 텍스트와 원본 정상 텍스트 간의 어휘 중복을 측정합니다.

$$J(T_1, T_2) = \frac{|T_1 \cap T_2|}{|T_1 \cup T_2|} \tag{5}$$

$T_1, T_2$가 동일한 텍스트이면 $J = 1$, 완전히 다르면 $J = 0$입니다. 정확히 동일한 두 텍스트를 LLM에 입력할 경우 WR은 50%이므로, 이것이 이상적인 기준점입니다.

### IPI Detection Performance

5개 LLM에서의 탐지 정확도를 비교합니다.

| 방법 | ChatGLM | Dolly | Falcon | LLaMA2 | LLaMA3 |
|------|---------|-------|--------|--------|--------|
| Prompt-Guard | 64.43% | 64.43% | 64.43% | 64.43% | 64.43% |
| ProtectAI-v2 | 75.48% | 75.48% | 75.48% | 75.48% | 75.48% |
| GPT-Resp | 85.15% | 85.12% | 84.58% | 85.08% | 82.55% |
| DS-Resp | 89.04% | 91.52% | 89.50% | 87.93% | 91.71% |
| TaskTracker | — | — | — | — | 95.07% |
| **RENNERVATE** | **99.05%** | **97.88%** | **99.58%** | **99.43%** | **99.37%** |

Prompt-Guard와 ProtectAI-v2가 모든 LLM에서 64~75%의 동일한 정확도를 보이는 것은, 이들이 특정 LLM의 내부 상태를 활용하지 않는 범용 분류기이기 때문입니다. 반면 RENNERVATE는 각 LLM의 attention feature를 활용하여 99% 수준의 정확도를 달성합니다.

LLaMA3에서는 두 번째 모델 대비 FPR을 2.90%p, FNR을 5.70%p 낮췄습니다.

### IPI Sanitization Performance

| 방법 | ChatGLM ASR | Dolly ASR | Falcon ASR | LLaMA2 ASR | LLaMA3 ASR |
|------|-------------|-----------|------------|------------|------------|
| 방어 없음 | 85.90% | 72.10% | 84.90% | 67.10% | 60.80% |
| Sandwich | 44.30% | 46.30% | 67.10% | 33.70% | 29.10% |
| Spotlighting | 38.80% | 32.40% | 35.10% | 49.70% | 51.30% |
| GPT-Loc | 10.30% | 8.20% | 9.80% | 9.70% | 9.30% |
| **RENNERVATE** | **0.10%** | **0.00%** | **0.00%** | **0.20%** | **0.20%** |

RENNERVATE는 방어 없는 경우 대비 ASR을 ChatGLM에서 85.80%p, Dolly에서 72.10%p, Falcon에서 84.90%p까지 낮추었습니다. LLaMA2에서 StruQ(0.30%)와 유사한 수준(0.20%)을 달성했는데, StruQ는 LLaMA2 파인튜닝을 요구하는 방법임을 고려하면 실용성 차원에서 유의미한 결과입니다.

소독 후 Jaccard 유사도는 대부분의 데이터셋에서 0.9 이상을 유지하며, 소독된 텍스트가 원본 정상 데이터와 텍스트적으로 거의 동일함을 확인합니다.

<p align="center">
  <img src="/assets/img/rennervate-ipi-defense/figure4-jaccard.png" alt="Figure 4: 소독 후 Jaccard 유사도">
  <br>
  <em>Figure 4. ChatGLM, Dolly, Falcon, LLaMA2 4개 모델에서 FIPI 및 미학습 데이터셋(M-H, J-R, S-M, M-S, R-J)에 걸친 Jaccard 유사도 분포. 대부분의 박스가 0.8~1.0 범위에 분포하며 소독 후에도 원본 텍스트의 무결성이 유지됨을 보여준다. (Zhong et al., 2026)</em>
</p>

### Transferability: Unseen Datasets

RENNERVATE를 FIPI 데이터셋으로만 학습한 뒤, 5개의 미학습 데이터셋(MRPC, HSOL, Jfleg, RTE, SST2)에서 평가합니다. 이 데이터셋들은 학습 시 전혀 노출되지 않은 NLP 태스크입니다.

미학습 데이터셋에서의 탐지 정확도는 **82.20% ~ 100.0%** 범위를 기록합니다. 일부 조합(RTE-Jfleg on Falcon: 82.20%)에서 다소 낮아지지만, 전반적으로 강력한 전이 성능을 보입니다. 이는 attention feature가 공격의 표면적 표현이 아닌 LLM의 내부 처리 패턴을 포착하기 때문에 태스크 변화에도 안정적임을 시사합니다.

### Robustness: Defense against Adaptive Attackers

**블랙박스 적응 공격**: PAIR와 TAP이라는 두 가지 자동화된 jailbreak(탈옥) 공격으로 RENNERVATE를 공격합니다. 방어 없이는 94~100% ASR이지만, RENNERVATE 적용 후 ChatGLM과 LLaMA2에서는 ASR이 0%로 감소합니다. 가장 높은 경우(LLaMA3, PAIR)에서도 19%에 그칩니다.

**화이트박스 적응 GCG 공격**: 공격자가 RENNERVATE의 탐지를 회피하도록 GCG 공격을 최적화합니다. 방어 없이는 93~99.5%의 ASR이 RENNERVATE 적용 후 **0~5%**로 감소합니다. 이는 GCG가 탐지 우회와 LLM 공격 성공을 동시에 달성하는 접미사를 최적화하기 어려움을 의미합니다.

**미학습 공격 유형 (Neural Exec)**: FIPI 학습에 포함되지 않은 Neural Exec 공격에 대해서도 탐지 정확도 **100.0%**, 소독 후 ASR 0%를 기록합니다. attention feature 기반 탐지가 특정 공격 패턴이 아닌 명령어 처리라는 본질적 속성을 학습한다는 것을 확인합니다.

### Ablation Study

Dolly 기준으로 핵심 구성 요소의 기여를 분석합니다.

| 변형 | FIPI | 미학습 데이터셋 (평균) |
|------|------|----------------------|
| Full RENNERVATE | 97.88% | ~95.1% |
| 2-Step AP → 단순 평균 풀링 | 99.53% | ~87.9% |
| token 수준 → 전체 수준 탐지 | 98.25% | ~93.4% |
| 평균 필터 제거 (k=1) | 97.26% | ~89.1% |

흥미로운 점은 2-Step AP를 단순 평균 풀링으로 교체하면 FIPI에서는 오히려 정확도가 오르는(99.53%) 반면, 미학습 데이터셋에서 최대 12.65%p 하락한다는 것입니다. **2-Step Attentive Pooling의 핵심 기여는 FIPI 내 성능이 아니라 전이 성능**임을 보여줍니다. Attentive Pooling이 task-invariant(과제 불변)한 attention 패턴만을 선택적으로 학습하기 때문입니다.

### Hyperparameter Analysis

주요 하이퍼파라미터의 영향을 요약합니다.

**응답 token 수 $m$**: $m=1$에서는 약 80% 수준이지만 $m=2$부터 급격히 개선됩니다. $m=16$ 이후 성능이 수렴하여 $m=32$ 설정이 충분함을 확인합니다.

**잔차 블록 수 $N$**: $N=2$(사용 설정)가 FIPI와 전이성 간 균형을 최적화합니다. $N=16$은 FIPI에서는 더 높지만 J-R에서 9.95%p, R-J에서 7.00%p 하락하는 overfitting(과적합) 현상을 보입니다.

---

## Limitations and Assumptions

논문이 제시하는 방법론의 제약 사항을 명확히 합니다.

**소독 회복의 완전성**: RENNERVATE는 주입 token을 제거하지만, 그 이후 LLM이 나머지 정상 텍스트만으로 원래 태스크를 얼마나 잘 수행하는지는 태스크 유형에 따라 달라집니다. 문법 교정(Jfleg) 같이 원문의 모든 단어가 중요한 태스크는 소독 후 WR이 낮아집니다. 논문은 이를 한계로 인정하고 더 정교한 복원(recovery) 메커니즘을 미래 연구 과제로 제시합니다.

**화이트박스 지식 가정**: 탐지기 학습에 대상 LLM의 attention feature를 사용하므로, 모델 아키텍처에 대한 화이트박스 접근이 필요합니다. 완전 블랙박스 LLM API 환경에서는 직접 적용이 불가능합니다.

**다중 모달 확장**: 현재 텍스트 기반 입력만을 다룹니다. 이미지, 오디오를 포함하는 다중 모달 LLM agent 환경으로의 확장은 향후 연구 과제입니다.

---

## Conclusion

RENNERVATE는 세 가지 측면에서 기존 방어와 차별화됩니다.

**첫째, 탐지와 소독의 통합**: 기존 방어는 탐지 또는 예방 중 하나에 집중했지만, RENNERVATE는 token 수준 정밀도를 기반으로 두 기능을 하나의 프레임워크에서 수행합니다.

**둘째, 모델 수정 불필요**: 파인튜닝이나 프롬프트 엔지니어링이 필요 없으며, 대상 LLM을 블랙박스 컴포넌트로 두고 외부에서 방어를 추가합니다. 0.5~0.8M의 경량 파라미터로 여러 LLM에 범용 적용이 가능합니다.

**셋째, attention 기반 전이 성능**: 공격 표면이 아닌 LLM 내부의 처리 패턴을 학습함으로써, 미학습 공격 유형과 미학습 데이터셋 모두에서 강인성을 보입니다.

제목의 "Attention is All You Need"가 단순한 유희가 아닌 이유가 여기에 있습니다. Transformer의 attention mechanism은 LLM의 이해를 가능하게 하는 동시에, 그 이해 과정의 이상을 탐지하는 열쇠이기도 합니다.

오늘날 LLM agent 시스템은 더욱 자율화되고 외부 데이터 의존도는 증가하는 방향으로 발전하고 있습니다. RENNERVATE가 제시하는 attention 기반 정밀 탐지 프레임워크는 실용적인 배포 환경에서도 적용 가능한 방향을 제시한다는 점에서, IPI 방어 연구의 중요한 이정표가 될 것입니다.
