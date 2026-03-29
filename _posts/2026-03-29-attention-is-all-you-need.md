---
layout: post
title: "Attention Is All You Need"
authors: "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin"
venue: "NeurIPS 2017"
arxiv: "https://arxiv.org/abs/1706.03762"
tags: [ai, nlp, transformer, attention, sequence-to-sequence]
date: "2026-03-29"
---

오늘 살펴볼 논문은 현대 딥러닝의 기반이 된 **Transformer** 아키텍처를 처음 제안한 "Attention Is All You Need"입니다. 2017년 NeurIPS에서 발표된 이 논문은 recurrence와 convolution을 완전히 제거하고 **attention mechanism만으로** 시퀀스 변환(sequence transduction) 문제를 풀어냈습니다. 오늘날 BERT, GPT, T5 등 대부분의 Large Language Model (LLM)이 이 구조를 기반으로 하고 있습니다.

## Motivation: RNN의 한계

2017년 이전의 sequence-to-sequence 모델들은 Recurrent Neural Network (RNN), 특히 Long Short-Term Memory (LSTM)와 Gated Recurrent Unit (GRU)에 기반하고 있었습니다. 이들은 입력 시퀀스를 **시간 순서대로 순차(sequential)** 처리합니다. 즉, 위치 $t$의 hidden state $h_t$는 반드시 이전 상태 $h_{t-1}$이 계산된 후에야 구할 수 있습니다.

이러한 순차적 특성은 두 가지 근본적인 문제를 낳습니다.

1. **병렬화 불가**: 시퀀스 길이 $n$에 비례하는 순차 연산이 필요하여, 긴 문장일수록 학습 속도가 크게 저하됩니다.
2. **장거리 의존성 학습의 어려움**: 두 위치 사이의 신호가 $O(n)$개의 순차 연산을 통과해야 하므로, 문장이 길수록 먼 위치 간의 dependency를 학습하기 어렵습니다.

Attention mechanism은 이미 RNN과 함께 쓰이며 긴 시퀀스에서의 성능을 향상시켰지만, 항상 recurrent layer와 결합되어 사용되었습니다. 저자들의 핵심 질문은 단순합니다. **"Recurrence 없이 attention만으로 충분하지 않을까?"**

## Model Architecture

Transformer는 encoder-decoder 구조를 따릅니다. Encoder는 입력 시퀀스 $(x_1, \ldots, x_n)$을 연속 표현 $\mathbf{z} = (z_1, \ldots, z_n)$으로 변환하고, Decoder는 $\mathbf{z}$를 바탕으로 출력 시퀀스 $(y_1, \ldots, y_m)$을 autoregressive(자기 회귀)하게 생성합니다.

<p align="center">
  <img src="/assets/img/attention-is-all-you-need/fig1-architecture.png" alt="Figure 1: Transformer 전체 구조">
  <br>
  <em>Figure 1. Transformer 전체 아키텍처. 왼쪽이 Encoder, 오른쪽이 Decoder입니다. (Vaswani et al., 2017)</em>
</p>

### Encoder

Encoder는 $N = 6$개의 동일한 층(layer)을 쌓은 구조입니다. 각 층은 두 개의 sub-layer로 구성됩니다.

1. **Multi-Head Self-Attention**: 입력 시퀀스의 모든 위치가 서로를 참조합니다.
2. **Position-wise Feed-Forward Network (FFN)**: 각 위치에 독립적으로 적용되는 2층 완전연결 신경망입니다.

각 sub-layer의 출력에는 residual connection과 layer normalization이 적용됩니다.

$$\text{output} = \text{LayerNorm}(x + \text{Sublayer}(x))$$

모든 sub-layer와 embedding layer의 출력 차원은 $d_\text{model} = 512$로 통일하여 residual connection이 원활하게 동작하도록 합니다.

### Decoder

Decoder 역시 $N = 6$층으로 구성되며, Encoder의 두 sub-layer에 더해 **세 번째 sub-layer**가 추가됩니다. 이 층은 Encoder의 출력에 대해 Multi-Head Attention을 수행하는 **Encoder-Decoder Attention**입니다.

Decoder의 self-attention에는 **Masked Multi-Head Attention**이 사용됩니다. Autoregressive 생성의 특성상, 위치 $i$에서의 예측은 $i$보다 앞선 위치의 출력에만 의존해야 합니다. 이를 보장하기 위해 softmax 입력에서 미래 위치($i$ 이후)를 $-\infty$로 마스킹하여 attention 가중치가 0이 되도록 강제합니다.

## Methodology

### Scaled Dot-Product Attention

<p align="center">
  <img src="/assets/img/attention-is-all-you-need/fig2-attention.png" alt="Figure 2: Scaled Dot-Product Attention과 Multi-Head Attention">
  <br>
  <em>Figure 2. (왼쪽) Scaled Dot-Product Attention, (오른쪽) Multi-Head Attention 구조 (Vaswani et al., 2017)</em>
</p>

Attention function은 Query, Key, Value 세 종류의 벡터를 받아 output을 계산하는 함수입니다. Output은 Value들의 가중합(weighted sum)이며, 가중치는 Query와 Key의 호환성(compatibility)으로 결정됩니다.

이 논문에서 제안하는 **Scaled Dot-Product Attention**은 다음과 같이 정의됩니다.

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

- $Q \in \mathbb{R}^{n \times d_k}$: Query 행렬, $n$개 위치의 query 벡터를 쌓은 것
- $K \in \mathbb{R}^{m \times d_k}$: Key 행렬, $m$개 위치의 key 벡터를 쌓은 것
- $V \in \mathbb{R}^{m \times d_v}$: Value 행렬, $m$개 위치의 value 벡터를 쌓은 것
- $d_k$: key/query의 차원

$QK^T$는 Query와 모든 Key 사이의 dot product를 한 번에 계산한 $n \times m$ 점수 행렬입니다. 이를 $\sqrt{d_k}$로 나누어 스케일링한 뒤 softmax를 취하여 attention 가중치를 얻고, 이 가중치로 Value를 가중합합니다.

**스케일링의 이유**: $d_k$가 커질수록 dot product의 분산이 $d_k$에 비례하여 커집니다. ($q$와 $k$의 각 성분이 평균 0, 분산 1의 독립 변수라면, $q \cdot k$의 분산은 $d_k$입니다.) 값이 커진 dot product는 softmax를 매우 작은 기울기 영역으로 밀어 넣어 gradient가 소실됩니다. $\sqrt{d_k}$로 나눔으로써 이를 방지합니다.

### Multi-Head Attention

단일 attention function으로 $d_\text{model}$차원을 처리하는 대신, Query, Key, Value를 **$h$번 서로 다른 선형 투영(linear projection)**으로 줄인 뒤 각각 독립적으로 attention을 수행합니다. 이 방식이 Multi-Head Attention입니다.

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O$$

$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

- $W_i^Q \in \mathbb{R}^{d_\text{model} \times d_k}$, $W_i^K \in \mathbb{R}^{d_\text{model} \times d_k}$, $W_i^V \in \mathbb{R}^{d_\text{model} \times d_v}$: 각 head의 투영 행렬
- $W^O \in \mathbb{R}^{h d_v \times d_\text{model}}$: 출력 투영 행렬

이 논문에서는 $h = 8$, $d_k = d_v = d_\text{model}/h = 64$를 사용합니다. 각 head의 차원이 $1/h$로 줄었으므로, 전체 계산 비용은 단일 full-dimensional attention과 유사합니다.

**설계 의도**: 단일 attention은 전체 표현 공간을 평균하여 참조합니다. 반면 여러 head를 두면, 각 head가 **서로 다른 표현 부분공간(representation subspace)**에서 서로 다른 위치 간의 관계를 동시에 학습할 수 있습니다. 예컨대 어떤 head는 통사적(syntactic) 관계를, 다른 head는 의미적(semantic) 관계를 포착할 수 있습니다.

### Applications of Attention

Transformer는 Multi-Head Attention을 세 가지 방식으로 활용합니다.

| 위치 | Query 출처 | Key/Value 출처 | 역할 |
|------|-----------|---------------|------|
| Encoder Self-Attention | Encoder 이전 층 | Encoder 이전 층 | 입력 내 모든 위치 간 상호 참조 |
| Decoder Masked Self-Attention | Decoder 이전 층 | Decoder 이전 층 (현재 위치까지만) | 이미 생성된 토큰만 참조 |
| Encoder-Decoder Attention | Decoder 이전 층 | Encoder 최종 출력 | 입력 시퀀스 전체를 참조하며 디코딩 |

### Position-wise Feed-Forward Networks

각 층의 attention sub-layer 뒤에는 위치별로 동일하게 적용되는 FFN이 따라옵니다.

$$\text{FFN}(x) = \max(0,\, xW_1 + b_1)W_2 + b_2$$

입력/출력 차원은 $d_\text{model} = 512$이고, 내부 차원은 $d_\text{ff} = 2048$입니다. 각 층은 서로 다른 파라미터를 가지지만, 같은 층 내에서는 위치에 무관하게 동일한 파라미터가 사용됩니다. 이는 커널 크기 1인 두 convolution으로 이해할 수도 있습니다.

### Positional Encoding

Transformer에는 recurrence도 convolution도 없으므로, 시퀀스 내 토큰의 순서 정보를 별도로 주입해야 합니다. 저자들은 embedding에 **Positional Encoding**을 더합니다.

$$PE_{(pos, 2i)} = \sin\!\left(\frac{pos}{10000^{2i/d_\text{model}}}\right)$$

$$PE_{(pos, 2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d_\text{model}}}\right)$$

- $pos$: 시퀀스 내 위치 (0, 1, 2, ...)
- $i$: 차원 인덱스 (0 ~ $d_\text{model}/2 - 1$)

각 차원은 서로 다른 주파수의 sinusoid에 대응합니다. 이 함수를 선택한 이유는 임의의 고정 offset $k$에 대해 $PE_{pos+k}$를 $PE_{pos}$의 선형 함수로 표현할 수 있어, 모델이 **상대 위치(relative position)**를 쉽게 학습할 수 있다는 가설 때문입니다. 학습된 positional embedding과 비교했을 때 거의 동일한 성능을 보였으며, sinusoidal 버전은 학습 시 보지 못한 더 긴 시퀀스에 대한 **외삽(extrapolation)** 가능성이 있어 채택되었습니다.

## Why Self-Attention?

저자들은 Self-Attention을 Recurrent, Convolutional 층과 세 가지 기준으로 비교합니다.

| 층 유형 | 층당 복잡도 | 순차 연산 수 | 최대 경로 길이 |
|---------|-----------|------------|------------|
| Self-Attention | $O(n^2 \cdot d)$ | $O(1)$ | $O(1)$ |
| Recurrent | $O(n \cdot d^2)$ | $O(n)$ | $O(n)$ |
| Convolutional (k) | $O(k \cdot n \cdot d^2)$ | $O(1)$ | $O(\log_k n)$ |
| Self-Attention (restricted, r) | $O(r \cdot n \cdot d)$ | $O(1)$ | $O(n/r)$ |

- **순차 연산**: Self-Attention은 모든 위치 쌍을 한 번에 병렬로 계산하므로 $O(1)$입니다. Recurrent는 위치마다 순서대로 처리해야 하므로 $O(n)$입니다.
- **최대 경로 길이**: 두 임의 위치 사이의 신호가 통과해야 하는 최대 연산 수입니다. Self-Attention은 임의의 두 위치를 단 한 번의 연산으로 직접 연결하므로 $O(1)$이며, 이는 장거리 의존성 학습에 크게 유리합니다.
- **층당 복잡도**: 문장 표현에 사용되는 경우, 보통 $n < d$이므로 Self-Attention이 Recurrent보다 복잡도가 낮습니다.

## Training

- **데이터**: WMT 2014 EN-DE (약 450만 문장 쌍, BPE 37K 어휘), WMT 2014 EN-FR (3600만 문장 쌍, word-piece 32K 어휘)
- **하드웨어**: NVIDIA P100 GPU × 8
- **Optimizer**: Adam ($\beta_1 = 0.9$, $\beta_2 = 0.98$, $\epsilon = 10^{-9}$)
- **학습률 스케줄링**:

$$\text{lrate} = d_\text{model}^{-0.5} \cdot \min(\text{step\_num}^{-0.5},\ \text{step\_num} \cdot \text{warmup\_steps}^{-1.5})$$

처음 `warmup_steps = 4000` 스텝 동안 학습률을 선형으로 증가시키고, 이후 step number의 역제곱근에 비례하여 감소시킵니다. 초기에 너무 큰 학습률로 발산하는 것을 방지하고 이후 안정적으로 수렴하도록 유도합니다.

- **Regularization**: Residual Dropout ($P_\text{drop} = 0.1$), Label Smoothing ($\epsilon_{ls} = 0.1$)

Label smoothing은 perplexity를 약간 높이지만, 모델이 과도하게 확신하지 않도록 만들어 accuracy와 BLEU 점수를 향상시킵니다.

## Results

### Machine Translation

| 모델 | EN-DE BLEU | EN-FR BLEU | 학습 비용 (FLOPs) |
|------|-----------|-----------|-----------------|
| GNMT + RL [Wu et al.] | 24.6 | 39.92 | $2.3 \times 10^{19}$ |
| ConvS2S [Gehring et al.] | 25.16 | 40.46 | $9.6 \times 10^{18}$ |
| MoE [Shazeer et al.] | 26.03 | 40.56 | $2.0 \times 10^{19}$ |
| ConvS2S Ensemble | 26.36 | 41.29 | $7.7 \times 10^{19}$ |
| **Transformer (base)** | **27.3** | **38.1** | $3.3 \times 10^{18}$ |
| **Transformer (big)** | **28.4** | **41.8** | $2.3 \times 10^{19}$ |

Transformer (big)은 WMT 2014 EN-DE에서 기존 앙상블 모델들을 포함한 모든 선행 모델보다 2.0 BLEU 이상 높은 **28.4 BLEU**를 달성했습니다. EN-FR에서도 **41.8 BLEU**로 단일 모델 기준 state-of-the-art를 세웠으며, 이를 학습하는 데 8개의 P100 GPU로 단 3.5일이 소요되었습니다. 이전 최고 모델보다 1/4에 불과한 비용입니다.

Base 모델조차 기존의 모든 단일 모델과 앙상블을 능가했으며, 학습 비용은 경쟁 모델의 일부에 불과합니다.

### Attention Visualization

<p align="center">
  <img src="/assets/img/attention-is-all-you-need/fig3-attention-viz.png" alt="Figure 3: Attention 시각화">
  <br>
  <em>Figure 3. 장거리 의존성을 포착하는 attention mechanism의 예시. "making"이 "more difficult"를 강하게 참조합니다. (Vaswani et al., 2017)</em>
</p>

Attention head의 가중치를 시각화하면 각 head가 서로 다른 언어적 관계를 포착한다는 것을 알 수 있습니다. Figure 3에서 볼 수 있듯이, 특정 head는 문장 내 의미적으로 연관된 단어들, 특히 먼 거리에 있는 단어들 사이의 의존성을 명확하게 포착합니다. "making"이라는 단어가 "more difficult"와 강하게 연결되어 있음을 확인할 수 있습니다.

### Model Variations (Ablation Study)

저자들은 다양한 하이퍼파라미터 변형 실험을 통해 설계 선택을 검증했습니다.

- **(A) Head 수**: Single-head attention은 최적 설정보다 0.9 BLEU 낮습니다. 너무 많은 head도 오히려 품질이 떨어집니다.
- **(B) $d_k$ 감소**: attention key 크기를 줄이면 품질이 하락합니다. 호환성 판단이 단순 dot product보다 더 정교한 함수를 필요로 할 수 있음을 시사합니다.
- **(C/D) 모델 크기 및 Dropout**: 모델이 클수록, dropout을 적절히 사용할수록 성능이 향상됩니다.
- **(E) Positional Encoding**: Sinusoidal encoding과 학습된 positional embedding은 거의 동일한 성능을 보입니다.

## Limitations

- **Self-Attention의 이차 복잡도**: 층당 복잡도가 $O(n^2 \cdot d)$이므로, 시퀀스 길이 $n$이 매우 길어지면 메모리와 연산량이 급격히 증가합니다. 이후 연구들(Longformer, Linformer, FlashAttention 등)이 이 문제를 완화하려 시도합니다.
- **Autoregressive 추론**: Decoder는 토큰을 하나씩 순차 생성하므로 추론 속도가 인코딩 대비 느립니다.
- **위치 정보**: Sinusoidal encoding은 학습 시 보지 못한 길이로의 외삽을 가설로만 내세웠으며, 실제 긴 시퀀스에서의 일반화는 제한적일 수 있습니다.

## Conclusion

"Attention Is All You Need"는 sequence-to-sequence 모델링에서 recurrence를 완전히 제거하고 attention만으로 전례 없는 성능과 학습 효율을 동시에 달성했습니다. Scaled Dot-Product Attention과 Multi-Head Attention이라는 간결하고 강력한 구성 요소, 그리고 sinusoidal positional encoding이라는 우아한 설계는 이후 딥러닝 전반의 패러다임을 바꾸었습니다.

오늘날 Transformer는 자연어 처리를 넘어 컴퓨터 비전(ViT), 음성 처리(Whisper), 단백질 구조 예측(AlphaFold2) 등 사실상 모든 딥러닝 분야에서 지배적인 아키텍처로 자리잡았습니다. 이 논문 한 편이 현대 AI의 모습을 얼마나 크게 바꾸었는지를 생각하면, "Attention Is All You Need"라는 제목이 단순한 기술적 주장을 넘어 하나의 선언처럼 느껴집니다.
