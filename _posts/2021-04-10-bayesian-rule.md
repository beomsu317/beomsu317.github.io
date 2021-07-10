---
title: Bayesian Rule
author: Beomsu Lee
category: [Algorithm, Math]
tags: [algorithm, math]
math: true
mermaid: true
---

## Overview

베이즈 정리는 데이터라는 조건이 주어졌을 때의 조건부확률을 구하는 공식이다. 데이터가 주어지기 전에 어느 정도 확률값을 예측하고 있을 때 이를 새로 수집한 데이터와 합쳐 최종 결과에 반영할 수 있다. 데이터의 수가 적은 경우 유리하며, 전체 데이터에 대한 분석 작업을 하지 않아도 되는 장점이 있다.

## Content

다음은 Bayesian Rule의 공식이다.

$ P(A \rvert B) = \dfrac{P(B \rvert A)P(A)}{P(B)} $

$ P(A) $는 **사전확률(prior)**이라하며 사건 B가 발생하기 전 갖고있던 사건 A의 확률이다. 사건 B가 발생하면 이 정보를 반영해 사건 A의 확률은 $ P(A \rvert B) $라는 값으로 변하게 되며 이를 **사후확률(posterior)**라고 한다.

사후확률은 사전확률에 $ \dfrac{P(B \rvert A)}{P(B)} $ 값을 곱해 얻을 수 있다. $P(B \rvert A)$는 **가능도(likelihood)**라 하며 $ P(B) $는 **정규화 상수(normalizing constant) 또는 증거(evidence)**라 한다.

- $ P(A \rvert B) $ : posterior. 사건 B가 발생한 후 갱신된 사건 A의 확률
- $ P(A) $ : prior. 사건 B가 발생되기 전 갖고있던 사건 A의 확률
- $ P(B \rvert A) $ : likelihood. 사건 A가 발생한 경우 사건 B의 확률
- $ P(B) $ : normalizing constant or evidence. 확률의 크기 조정

베이즈 정리는 사건 B가 발생함으로써 사건 A의 확률이 어떻게 변하는지 표현한 정리이다.

## References
- [Bayesian Rule](https://datascienceschool.net/02%20mathematics/06.06%20%EB%B2%A0%EC%9D%B4%EC%A6%88%20%EC%A0%95%EB%A6%AC.html)