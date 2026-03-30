---
layout: post
title: "PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows"
authors: "Renan Souza, Amal Gueroudji, Stephen DeWitt, Daniel Rosendo, Tirthankar Ghosal, Robert Ross, Prasanna Balaprakash, Rafael Ferreira da Silva"
venue: "IEEE e-Science 2025"
arxiv: "https://arxiv.org/abs/2508.02866"
tags: [distributed-systems, provenance, agentic-workflow, llm, mcp, scientific-computing]
date: "2026-03-30"
---

여러분, 오늘은 AI 에이전트가 주도하는 과학 워크플로우에서 **투명성(transparency)**과 **추적 가능성(traceability)**을 확보하기 위한 provenance 모델 **PROV-AGENT**를 살펴보겠습니다. 이 논문은 Oak Ridge 국립 연구소와 Argonne 국립 연구소의 공동 연구로, IEEE e-Science 2025에 발표되었습니다. LLM 기반 에이전트가 잘못 추론하거나 hallucinate(환각)했을 때, 그 오류가 다운스트림 워크플로우 전체에 전파될 수 있다는 문제의식에서 출발합니다.

## Background

### Agentic Workflow와 Cross-Facility 환경

Agentic workflow(에이전트 기반 워크플로우)는 자율 AI 에이전트가 작업을 계획하고, 인간 및 다른 에이전트와 상호작용하며, 과학적 의사결정을 내리는 워크플로우입니다. 기존의 정적·결정론적 워크플로우와 달리, agentic workflow는 에이전트의 추론 결과에 따라 실행 경로가 동적으로 변합니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig1-cross-facility-workflow.png" alt="Figure 1: Cross-facility agentic workflow">
  <br>
  <em>Figure 1. Edge–Cloud–HPC 컨티뉴엄에 걸친 cross-facility agentic workflow. 실험 시설의 센서 데이터가 실시간 스트리밍으로 HPC에 전달되고, AI 에이전트가 클라우드 LLM 서비스를 호출해 의사결정을 내린다. (Souza et al., 2025)</em>
</p>

이러한 워크플로우는 Edge 장치, 클라우드 서비스, HPC(고성능 컴퓨팅) 시스템을 아우르는 이질적이고 분산된 환경에서 실행됩니다. LangChain, AutoGen, LangGraph, CrewAI 같은 멀티 에이전트 프레임워크는 이미 Model Context Protocol (MCP)을 채택하고 있는데, MCP는 도구(tools), 프롬프트(prompts), 리소스(resources), 컨텍스트 관리 등 에이전트 AI 개발의 핵심 개념을 표준화합니다.

### Provenance와 W3C PROV

Provenance(출처)는 데이터나 계산 결과가 어떻게 생성되었는지를 추적하는 메타데이터입니다. W3C PROV 표준은 provenance 표현을 위한 범용 모델로, 세 가지 핵심 추상화를 정의합니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig2-w3c-prov.png" alt="Figure 2: W3C PROV 모델">
  <br>
  <em>Figure 2. W3C PROV Provenance 모델: Entity, Activity, Agent 세 가지 추상화와 이들 사이의 관계. (Groth & Moreau, 2013)</em>
</p>

- **Entity**: 데이터, 파일, 결과물 등 존재하는 것
- **Activity**: 데이터를 소비하거나 생성하는 작업
- **Agent**: 활동에 책임이 있는 행위자 (사람, 소프트웨어 등)

W3C PROV는 다양한 도메인 확장을 지원하며, PROV-Wf(워크플로우), ProvONE(과학 워크플로우), PROV-ML(AI/ML) 등 수많은 확장이 제안되었습니다. 그러나 이들은 에이전트 기반 워크플로우의 핵심 개념인 프롬프트, 응답, 에이전트 의사결정을 워크플로우 컨텍스트와 연결해 표현하는 기능이 부족합니다.

### 문제: 에이전트 메타데이터의 고립

기존 MCP 기반 에이전트 프레임워크들도 프롬프트, 응답, AI 서비스 호출을 기록하지만, 이 데이터는 나머지 워크플로우 실행 정보와 **분리(isolated)**되어 있습니다. 에이전트의 행동이 다운스트림 작업에 어떤 영향을 미쳤는지, 어떤 입력 데이터로부터 어떤 의사결정이 도출되었는지 추적할 수 없습니다. 에이전트가 hallucinate하거나 잘못된 추론을 했을 때, 그 오류의 근원을 역추적하고 워크플로우 전체에 미친 영향을 파악하기가 매우 어렵습니다.

## PROV-AGENT: Provenance Model for Agentic Workflows

### Overview

PROV-AGENT는 W3C PROV를 확장하고 MCP 개념을 통합하여, AI 에이전트의 상호작용과 모델 호출을 워크플로우 전체의 provenance 그래프에 통합하는 모델입니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig3-prov-agent-model.png" alt="Figure 3: PROV-AGENT 모델">
  <br>
  <em>Figure 3. PROV-AGENT: W3C PROV 확장 모델. 점선 화살표는 subClassOf 관계를 나타낸다. (Souza et al., 2025)</em>
</p>

### Workflow Structure

모델의 기반은 표준 워크플로우 구조입니다. `Campaign`, `Workflow`, `Task`는 모두 PROV Activity의 서브클래스로 모델링됩니다.

- **Campaign**: 여러 Workflow 실행을 묶는 최상위 단위. `Person` 또는 `Organization` 에이전트와 `wasAssociatedWith` 관계를 가짐
- **Workflow**: Campaign 내의 개별 실행 인스턴스
- **Task**: Workflow 내의 개별 작업 단위. 도메인별 데이터를 소비(`used`)하고 생성(`wasGeneratedBy`)함

Task는 세 종류의 메타데이터를 생성합니다.

- **DomainData**: 파라미터, 인자, KPI(핵심 성과 지표), QoI(관심 지표), 도메인 파일 포인터 등 도메인 고유 데이터
- **SchedulingData**: 태스크가 실행된 위치 (컴퓨팅 노드, CPU 코어, GPU ID 등)
- **TelemetryData**: 런타임 메트릭 (CPU/GPU 사용률, 디스크 사용량 등)

`SchedulingData`와 `TelemetryData`는 `DataObject`(→ PROV Entity의 서브클래스)로 모델링되어, provenance 그래프에 인프라 수준 컨텍스트를 제공합니다.

### AIAgent and Tool Execution

W3C PROV Agent를 확장하여 `AIAgent`를 정의합니다. 단일 에이전트뿐 아니라 멀티 에이전트 시나리오에서도 각 에이전트가 자신의 도구와 추론 경로를 가진 독립 인스턴스로 동일한 provenance 그래프 내에 표현될 수 있습니다.

MCP 용어를 따라, AI 에이전트는 하나 이상의 **도구 실행(tool execution)**과 연관됩니다. PROV-AGENT는 `AgentTool`이라는 Activity를 정의하여 각 도구 실행을 캡처합니다. `AgentTool`은 해당 도구를 소유한 `AIAgent`와 `wasAssociatedWith` 관계로 연결됩니다.

### AIModel Invocation

도구 실행은 종종 하나 이상의 LLM 호출에 의해 결정됩니다. PROV-AGENT는 이를 위해 다음 요소들을 정의합니다.

- **AIModel**: 사용된 LLM의 메타데이터 (제공자, 모델명, temperature 등 파라미터)
- **AIModelInvocation**: 각 LLM 호출을 나타내는 Activity
- **Prompt**: LLM에 전송된 프롬프트 (Entity)
- **ResponseData**: LLM이 생성한 응답 (Entity, `wasAttributedTo` AIAgent)

`AgentTool`이 LLM 결과에 기반해 동작할 때, `wasInformedBy` 관계가 `AgentTool`에서 해당 `AIModelInvocation`으로 명시적으로 연결됩니다. 이 관계가 에이전트의 추론 과정을 워크플로우 실행 컨텍스트와 연결하는 핵심 고리입니다.

## System Implementation: Flowcept

PROV-AGENT는 새로운 시스템을 처음부터 구축하는 대신, 기존 오픈소스 분산 데이터 관측(data observability) 시스템인 **Flowcept**를 확장합니다. Flowcept는 계측(instrumentation)된 스크립트, Dask·MLflow 같은 워크플로우 도구의 훅(hook), Redis·Kafka·SQLite 등 데이터 스트리밍 서비스로부터 데이터를 수집하고, 이를 W3C PROV 기반 provenance 데이터베이스에 통합합니다.

### Instrumentation via Decorators

MCP 서버가 초기화되면, `AIAgent` 인스턴스가 생성되어 식별자와 이름이 할당됩니다. MCP 도구 함수에는 `@flowcept_agent_tool` 데코레이터를 적용합니다. 이 데코레이터는 함수 실행 시 입력·출력, 텔레메트리 데이터, 스케줄링 데이터를 자동으로 캡처하고 `AgentTool` 실행 Activity를 생성합니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig4-code-example.png" alt="Figure 4: MCP tool with Flowcept decorators">
  <br>
  <em>Figure 4. @flowcept_agent_tool 데코레이터와 FlowceptLLM 래퍼를 적용한 MCP 에이전트 도구 예시. 도구 실행과 LLM 호출이 자동으로 provenance 데이터베이스에 기록된다. (Souza et al., 2025)</em>
</p>

### FlowceptLLM Wrapper

LLM 호출 캡처를 위해 `FlowceptLLM`이라는 범용 래퍼를 제공합니다. 이 래퍼는 CrewAI, LangChain, OpenAI 등 주요 LLM 인터페이스와 호환되며, 클라우드 LLM 서비스(OpenAI, SambaNova, Azure 등)에 프롬프트가 전송될 때마다 다음 정보를 캡처합니다.

- 프롬프트 내용
- 모델 응답
- 모델 메타데이터 (제공자, 모델명, temperature)
- 선택적 텔레메트리 (응답 시간 등)

각 호출은 `AIModelInvocation` Activity 인스턴스로 기록되며, 해당 `Prompt` Entity 및 `ResponseData` Entity와 연결됩니다.

### Natural Language Query Agent

Flowcept는 Streamlit GUI를 갖춘 MCP 에이전트도 제공합니다. 사용자는 자연어 쿼리로 런타임 중에 provenance 데이터베이스를 탐색할 수 있습니다. Fig. 5(B)에서 확인할 수 있듯, "layer 7의 Choose Option 태스크에 어떤 LLM 호출이 사용되었나?"와 같은 질문을 직접 입력해 즉각적인 답변을 얻습니다.

## Evaluation: Additive Manufacturing Workflow

### 시나리오 설정

PROV-AGENT를 평가하기 위해 논문은 **금속 적층 제조(additive manufacturing)** 워크플로우를 사례로 사용합니다. 이 워크플로우는 Edge–Cloud–HPC 컨티뉴엄에 걸쳐 실행됩니다.

- **Edge**: 센서 드라이버(`Sensor_Driver_i`)가 레이어별로 센서를 구동
- **HPC**: 물리 시뮬레이션 모델(`Physics_Model_i`)이 센서 데이터를 처리하고 품질 평가
- **Cloud**: AI 에이전트가 클라우드 LLM을 호출해 레이어별 의사결정

<p align="center">
  <img src="/assets/img/prov-agent/fig5-provenance-graph.png" alt="Figure 5: PROV-AGENT 인스턴스화 및 Flowcept Agent Chat">
  <br>
  <em>Figure 5. (A) 적층 제조 워크플로우에 대한 PROV-AGENT 통합 provenance 그래프 인스턴스. 에이전트 의사결정이 이전 반복(iteration i)의 결과를 입력으로 받아 다음 반복(i+1)에 영향을 준다. (B) Flowcept Agent Chat에서 자연어 쿼리로 LLM 호출 정보를 질의하는 화면. (Souza et al., 2025)</em>
</p>

반복 $i$마다 에이전트 의사결정 도구(`Agent_Tool_i`)가 물리 모델 출력(`Control_Result_i`, `Scores_i`)을 입력으로 받고 LLM을 호출(`LLM_Invocation_i`)합니다. LLM 호출은 명시적으로 `Prompt_i`와 `Response_i` Entity에 연결되며, 최종 `Agent_Decision_i`는 `Analysis_Agent_i`에 `wasAttributedTo` 관계로 귀속됩니다. 이 결정은 다음 반복의 입력으로 사용되어 반복 간 인과관계를 완전히 추적 가능하게 합니다.

### Provenance Query 예시

PROV-AGENT가 가능하게 하는 쿼리를 구체적으로 살펴보겠습니다.

**Q1. 에이전트 결정으로부터 최초 입력 데이터까지의 완전한 lineage는?**

`Agent_Decision_i` → `Agent_Tool_i` → `Scores_i`, `Control_Result_i`, `Agent_Decision_{i-1}` → `Model_Evaluation_i`, `Physics_Model_i` → `Sensor_Data_i` → `Experiment_Setup`까지 역방향으로 추적합니다.

**Q2. 레이어 2 출력 시 에이전트 결정, 점수 선택지, 추론 근거는?**

`Agent_Decision_2`에서 `Agent_Tool_2`로 이동하고, 그 입력인 `Scores_2`, `Control_Result_2`, 그리고 `LLM_Invocation_2`의 `Response_2`를 조회해 의사결정 맥락을 재구성합니다.

**Q3. 특정 에이전트 결정에서 hallucination이 의심될 때 해당 LLM 프롬프트와 응답은?**

레이어 2 점수 선택 시 비정상적 결정이 식별된 경우, `Agent_Decision_2` → `Agent_Tool_2` → `LLM_Invocation_2` → `Prompt_2`, `Response_2`를 역추적해 전체 추론 컨텍스트를 복원합니다.

**Q4. 에이전트 결정이 이후 워크플로우 활동에 어떤 영향을 미쳤는가?**

`Agent_Decision_i`가 `Agent_Tool_{i+1}`의 입력으로 사용되었음을 순방향으로 추적합니다. 하나의 의사결정이 수천 개의 반복에 걸쳐 전파될 수 있는 아디티브 제조 시나리오에서 특히 중요합니다.

**Q5. 오류 데이터의 원점과 전파 경로는?**

특정 `Agent_Tool_i`에서 비정상 결정이 발견된 경우, 그것이 사용한 `Scores_i`까지 역추적하고 해당 점수를 생성한 `Physics_Model_i`, 나아가 그 입력인 `Sensor_Data_i`로 거슬러 올라가 오류의 근원지를 특정합니다.

## Limitations and Future Work

논문이 명시하는 현재 구현의 제약은 다음과 같습니다.

- **LLM 전용 구현**: 첫 번째 구현은 LLM 기반 에이전트에 집중. 비전(vision), 시계열, 로보틱스 등 다른 foundation model 유형에 대한 확장이 필요함
- **제한된 에이전트 메타데이터**: 현재 구현은 에이전트의 ID와 이름만 기록. 모델/도구의 버전 관리 상태, 추가 설정 파라미터 등 확장 가능한 메타데이터가 모델에는 정의되어 있으나 아직 완전히 캡처되지 않음
- **예비 평가**: 평가가 단일 과학 도메인(적층 제조)에 국한. 더 광범위한 agentic workflow 시나리오에 대한 검증이 추후 과제

## Conclusion

PROV-AGENT는 세 가지 핵심 기여를 통해 agentic workflow의 책임성 문제를 해결합니다.

1. **Provenance 모델**: W3C PROV를 확장하고 MCP 개념을 통합해, AI 에이전트의 상호작용을 워크플로우 provenance의 first-class element로 표현
2. **오픈소스 시스템**: Flowcept 기반의 근실시간 agentic provenance 캡처 시스템 — 데코레이터와 래퍼만으로 기존 코드에 최소한의 수정
3. **Cross-facility 검증**: Edge–Cloud–HPC 환경에서 hallucination 역추적과 에이전트 reliability 분석을 지원하는 쿼리 능력 검증

AI 에이전트가 과학 워크플로우의 핵심 구성 요소로 자리잡고 있는 현 시점에서, 에이전트의 행동을 워크플로우 전체 맥락 속에서 추적·설명·재현할 수 있는 기반은 점점 더 중요해질 것입니다. PROV-AGENT는 그 첫 걸음을 MCP 표준과의 정렬, 그리고 기존 오픈소스 인프라 위에서 실용적으로 구현하는 방향으로 제시합니다.
