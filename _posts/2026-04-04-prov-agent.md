---
layout: post
title: "PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows"
authors: "Renan Souza, Amal Gueroudji, Stephen DeWitt, Daniel Rosendo, Tirthankar Ghosal, Robert Ross, Prasanna Balaprakash, Rafael Ferreira da Silva"
venue: "IEEE e-Science 2025"
arxiv: "https://arxiv.org/abs/2508.02866"
tags: [distributed-systems, provenance, agentic-workflow, llm, mcp, hpc, hallucination, responsible-ai]
date: "2026-04-04"
---

## Introduction

AI 에이전트가 과학적 워크플로우의 핵심 구성 요소로 자리 잡으면서, 새로운 종류의 신뢰성 문제가 부상하고 있습니다. 하나의 에이전트가 hallucination(환각)을 일으키면, 그 잘못된 출력이 다음 에이전트의 입력이 되어 오류가 전파될 수 있습니다. 수천 레이어를 처리하는 금속 3D 프린팅 공정을 생각해 보십시오. 레이어 1에서의 잘못된 AI 결정이 레이어 1000의 제조 결함으로 이어질 수 있습니다.

기존 provenance(출처 추적) 시스템은 이 문제에 대한 답을 갖고 있지 않습니다. W3C PROV 표준은 데이터와 프로세스의 흐름을 기록하는 강력한 기반을 제공하지만, AI 에이전트에 특화된 핵심 아티팩트, 즉 프롬프트·응답·모델 호출·에이전트 결정을 명시적으로 모델링하지 않습니다. 결과적으로 "어떤 프롬프트가 이 잘못된 결정을 유발했는가?"라는 질문에 답하는 것이 불가능합니다.

Oak Ridge National Laboratory(ORNL)와 Argonne National Laboratory의 연구팀은 이 간극을 메우기 위해 **PROV-AGENT**를 제안합니다. PROV-AGENT는 W3C PROV를 확장하고 Model Context Protocol(MCP)의 개념을 통합하여, AI 에이전트 상호작용을 전통적인 워크플로우 provenance와 통합된 단일 그래프로 표현합니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig1-agentic-workflow.png" alt="Figure 1: Edge-Cloud-HPC 연속체에 걸친 Agentic 워크플로우">
  <br>
  <em>Figure 1. Edge(실험 시설) – Cloud – HPC에 걸친 cross-facility agentic 워크플로우. 데이터는 엣지에서 HPC로 실시간 스트리밍되고, AI 에이전트 결정이 피드백 루프를 통해 upstream 태스크에 영향을 미친다 (Souza et al., 2025)</em>
</p>

## Background and Related Work

### W3C PROV and Its Limitations for Agentic Workflows

W3C PROV는 provenance 표현의 사실상 표준으로, 세 가지 핵심 클래스를 중심으로 구성됩니다.

- **Entity**: 데이터, 파일, 결과물 등 "물(物)"
- **Activity**: 프로세스, 실행, 태스크 등 "일(事)"
- **Agent**: 활동을 책임지는 소프트웨어 또는 인간 행위자

<p align="center">
  <img src="/assets/img/prov-agent/fig2-w3c-prov.png" alt="Figure 2: W3C PROV 핵심 모델">
  <br>
  <em>Figure 2. W3C PROV의 세 핵심 클래스(Agent, Entity, Activity)와 그 관계 (W3C, 2013)</em>
</p>

이 모델을 기반으로 다양한 도메인 확장이 제안되었습니다. **ProvONE**은 워크플로우 관리 시스템을 위한 메타데이터를 추가하고, **PROV-ML**은 ML 모델 훈련과 평가를 위한 아티팩트를 모델링합니다. **PROV-DfA**는 인간이 개입하는 human-steered 워크플로우의 동적 적응을 추적합니다.

그러나 이들은 모두 공통된 한계를 공유합니다. AI 에이전트가 독립적으로 계획하고, 결정하고, 다른 에이전트와 협력하는 **agentic workflow(에이전틱 워크플로우)**의 핵심 의미론을 표현하지 못합니다. 특히 다음이 누락됩니다.

- 에이전트에 전달된 **프롬프트**와 에이전트가 생성한 **응답**
- LLM 등 foundation model 호출의 메타데이터(모델명, provider, temperature)
- 에이전트 결정이 후속 워크플로우 태스크에 미친 **인과적 영향**

또한 MCP 기반 프레임워크들(LangChain, AutoGen, CrewAI 등)은 내부적으로 프롬프트와 응답을 기록하지만, 이 데이터는 워크플로우의 나머지 부분과 **단절**되어 있어 end-to-end 추적이 불가능합니다.

### The Cross-Facility Challenge

현대 과학 워크플로우는 단일 시스템에서 실행되지 않습니다. 실험 데이터는 엣지 장치(센서, 로봇, 계측기)에서 생성되어 클라우드 AI 서비스를 통해 처리되고, HPC 시스템에서 물리 시뮬레이션이 수행됩니다. 이 이기종 환경에서 provenance를 통합 추적하려면, 서로 다른 시스템의 데이터 스키마와 형식을 조화시키는 연합(federated) 접근이 필요합니다.

## PROV-AGENT: A Provenance Model for Agentic Workflows

### Core Design Philosophy

PROV-AGENT는 두 가지 핵심 원칙 위에 설계되었습니다.

1. **W3C PROV 확장**: 기존 표준을 대체하지 않고 서브클래스를 통해 호환성을 유지합니다.
2. **MCP 개념 통합**: 업계 표준으로 자리 잡고 있는 Model Context Protocol의 tool, prompt, resource 개념을 provenance 모델에 반영합니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig3-prov-agent-model.png" alt="Figure 3: PROV-AGENT 모델 다이어그램">
  <br>
  <em>Figure 3. PROV-AGENT: W3C PROV의 agentic 워크플로우 확장. 점선 화살표는 subClassOf 관계를 나타낸다 (Souza et al., 2025)</em>
</p>

### Model Components

PROV-AGENT의 구성 요소는 두 계층으로 나뉩니다.

**Activity 계층** (PROV Activity의 서브클래스):

| 클래스 | 설명 |
|--------|------|
| `Campaign` | 일련의 워크플로우 실행을 묶는 상위 컨테이너 |
| `Workflow` | 개별 워크플로우 실행 인스턴스 |
| `Task` | 전통적인 워크플로우 태스크(비-에이전틱) |
| `AgentTool` | MCP tool로 정의된 에이전트 도구 실행 |
| `AIModelInvocation` | LLM 등 foundation model 호출 |

**Entity 계층** (PROV Entity의 서브클래스 `DataObject`의 하위):

| 클래스 | 설명 |
|--------|------|
| `DomainData` | 도메인 특화 데이터(파라미터, KPI, 결과물) |
| `SchedulingData` | 실행 위치 메타데이터(노드, CPU, GPU ID) |
| `TelemetryData` | 런타임 메트릭(CPU/GPU 사용률, 디스크) |
| `Prompt` | LLM에 전달된 프롬프트 |
| `ResponseData` | LLM이 생성한 응답 |
| `AIModel` | 모델 메타데이터(이름, provider, temperature) |

**Agent 계층**:

| 클래스 | 설명 |
|--------|------|
| `AIAgent` | PROV Agent의 서브클래스; AI 에이전트 인스턴스 |

### Key Relationships

PROV-AGENT는 표준 PROV 관계를 활용하여 에이전트 아티팩트를 워크플로우와 연결합니다.

$$\text{AgentTool} \xrightarrow{\text{wasInformedBy}} \text{AIModelInvocation}$$

$$\text{AIModelInvocation} \xrightarrow{\text{used}} \text{Prompt},\ \text{AIModel}$$

$$\text{ResponseData} \xrightarrow{\text{wasGeneratedBy}} \text{AIModelInvocation}$$

$$\text{ResponseData} \xrightarrow{\text{wasAttributedTo}} \text{AIAgent}$$

여기서 `wasInformedBy`는 하나의 `AgentTool` 실행이 하나 이상의 LLM 호출 결과에 의해 정보를 제공받았음을 나타냅니다. 이 관계가 바로 "어떤 LLM 호출이 이 에이전트 결정에 영향을 미쳤는가"를 추적 가능하게 만드는 핵심입니다.

모든 관계가 표준 PROV 구문(`used`, `wasGeneratedBy`, `wasAssociatedWith`, `wasInformedBy`)으로 표현되므로, 결과 그래프는 **완전히 연결되고 질의 가능**합니다. 사용자는 최종 결과물에서 시작하여 에이전트 추론, 프롬프트, 입력 데이터, 시스템 컨텍스트까지 역방향으로 탐색할 수 있습니다.

**모달리티 독립성**: PROV-AGENT는 LLM에만 국한되지 않습니다. 프롬프트-호출-응답 상호작용 모델을 따르는 모든 foundation model, 즉 비전, 오디오, 멀티모달 모델에 적용 가능하도록 설계되었습니다.

## System Implementation

### Flowcept Integration

논문은 PROV-AGENT를 처음부터 구현하는 대신 **Flowcept**라는 기존 오픈소스 분산 provenance 프레임워크를 확장합니다. Flowcept는 다양한 형식과 스키마를 가진 원시 provenance 데이터를 스트리밍 방식으로 수집하고, 중앙 통합 서비스가 이를 W3C PROV 확장 모델로 정제하여 영구 저장합니다. 지원하는 데이터 소스는 Redis, Kafka, SQLite, 파일 시스템, 객체 저장소 등을 포함합니다.

### Instrumentation via Decorators

에이전트 도구의 provenance 캡처는 Python 데코레이터 두 개로 이루어집니다.

<p align="center">
  <img src="/assets/img/prov-agent/fig4-mcp-agent-tool.png" alt="Figure 4: MCP 에이전트 도구 코드 예시">
  <br>
  <em>Figure 4. @flowcept_agent_tool 데코레이터와 FlowceptLLM 래퍼를 적용한 MCP 에이전트 도구. 단 두 줄의 추가로 도구 실행과 LLM 호출 provenance가 자동으로 캡처된다 (Souza et al., 2025)</em>
</p>

```python
from langchain_openai import ChatOpenAI
from flowcept import FlowceptLLM, flowcept_agent_tool

@mcp.tool()
@flowcept_agent_tool
def evaluate_scores(layer, result, scores):
    ...
    prompt = get_prompt(layer, result, scores)
    llm = FlowceptLLM(ChatOpenAI(model="gpt-4o"))
    response = llm.invoke(prompt)
    ...
    return ...
```

`@flowcept_agent_tool` 데코레이터는 함수 실행 시 자동으로 `AgentTool` 인스턴스를 생성하고, 입력·출력·텔레메트리 데이터를 캡처합니다. `FlowceptLLM`은 기존 LLM 객체를 래핑하여 `invoke()` 호출마다 `AIModelInvocation`을 기록하고, 프롬프트·응답·모델 메타데이터를 저장합니다. 이 두 컴포넌트는 CrewAI, LangChain, OpenAI 등 주요 LLM 인터페이스와 호환됩니다.

**MCP 서버 초기화 시**, Flowcept는 `AIAgent` 인스턴스를 생성하고 식별자와 이름을 할당합니다. 이후 모든 도구 실행은 이 에이전트 인스턴스와 `wasAssociatedWith` 관계로 연결됩니다.

Flowcept는 Streamlit 기반 GUI도 제공하는데, 사용자는 이를 통해 **자연어 질의**로 provenance 데이터베이스를 탐색할 수 있습니다. 이 인터페이스 자체도 MCP 에이전트로 구현되어 있습니다.

## Evaluation: Additive Manufacturing Use Case

### Workflow Description

논문은 ORNL의 Manufacturing Demonstration Facility(MDF)에서 개발 중인 자율 금속 3D 프린팅 워크플로우를 사용 사례로 채택합니다.

- **엣지(Edge)**: MDF의 금속 3D 프린터가 레이어별로 센서 데이터를 수집
- **HPC(OLCF)**: 물리 기반 시뮬레이션으로 각 레이어의 상태를 추정하고 미래 레이어에 대한 control result를 예측
- **클라우드**: GPT-4o 기반 AI 에이전트가 physics model 점수를 분석하고 다음 레이어의 제어 결정을 내림

Model predictive control(모델 예측 제어) 방식으로, 각 레이어의 에이전트 결정이 다음 레이어의 결정 컨텍스트에 포함됩니다. 이 피드백 루프에서 **단 하나의 hallucination이 수천 레이어에 걸쳐 연쇄 오류를 일으킬 수 있습니다**.

### End-to-End Provenance Graph

<p align="center">
  <img src="/assets/img/prov-agent/fig5-provenance-graph.png" alt="Figure 5: PROV-AGENT 통합 provenance 그래프와 자연어 질의 인터페이스">
  <br>
  <em>Figure 5. (A) 적층 제조 워크플로우에 대한 PROV-AGENT 인스턴스화. 레이어 i의 에이전트 결정이 레이어 i+1에 영향을 미치는 피드백 루프가 명시적으로 모델링된다. (B) Flowcept 에이전트의 자연어 질의 인터페이스 (Souza et al., 2025)</em>
</p>

Figure 5-A에서 통합 provenance 그래프의 구조를 확인할 수 있습니다. 레이어 $i$에 대한 실행 흐름은 다음과 같습니다.

1. `Sensor_Driver_i` (Task, Edge)가 `Sensor_Data_i`를 생성
2. `Physics_Model_i` (Task, HPC)가 센서 데이터를 소비하여 `Control_Result_i` 생성
3. `Model_Evaluation_i` (Task, HPC)가 결과를 평가하여 `Scores_i` 생성
4. `Agent_Tool_i` (AgentTool, HPC)가 점수, 제어 결과, 이전 결정(`Agent_Decision_{i-1}`)을 입력받음
5. `LLM_Invocation_i` (AIModelInvocation, Cloud)가 `Prompt_i`를 소비하여 `Response_i` 생성
6. `Agent_Decision_i` (DomainData)가 에이전트에 귀속(`wasAttributedTo`)되어 다음 반복의 컨텍스트로 전달

### Exemplary Provenance Queries

PROV-AGENT가 활성화하는 대표적인 질의 5가지입니다.

**Q1. 에이전트 결정의 완전한 계보(lineage)는?**

`Agent_Decision_i`에서 시작하여 `Agent_Tool_i` → `Scores_i` → `Model_Evaluation_i` → `Physics_Model_i` → `Sensor_Data_i` → `Experiment_Setup`까지 역방향으로 탐색합니다.

**Q2. 레이어 2에서의 결정, 옵션, 추론은?**

`Agent_Decision_2` → `Agent_Tool_2`를 통해 `Scores_2`, `Control_Result_2`, `Response_2`(`LLM_Invocation_2`로부터)를 동시에 조회합니다. 에이전트가 어떤 옵션을 고려했고 왜 특정 결정을 내렸는지 파악할 수 있습니다.

**Q3. 예상치 못한 결정에 대한 LLM 프롬프트와 응답은?** (Figure 5-B에 도시)

hallucination이 감지된 `Agent_Decision_2`를 시작점으로, `Agent_Tool_2` → `LLM_Invocation_2` → `Prompt_2`, `Response_2`를 추적합니다. 자연어 인터페이스로 "레이어 2의 Choose Option 태스크에 영향을 준 LLM 호출은 무엇인가?"라는 질문을 통해 조회할 수 있습니다.

**Q4. 에이전트 결정이 후속 활동에 어떻게 영향을 미쳤는가?**

`Agent_Decision_i`가 `Agent_Decision_{i+1}`에 사용됨을 추적하여, `used`/`wasGeneratedBy` 관계를 재귀적으로 탐색합니다.

**Q5. 오류 데이터의 원점과 전파 경로는?**

`Agent_Decision_i`에서 backward로 도구, LLM 응답, 물리 모델 출력, `Sensor_Data_i`까지 원인을 역추적하고, forward로 영향받은 모든 downstream 결과를 식별합니다.

이 질의들은 PROV-AGENT가 단순한 로그 기록이 아니라 **인과 관계를 명시적으로 모델링**함으로써 가능해집니다.

## Limitations and Future Directions

논문은 초기 구현으로서의 한계를 명시합니다.

- **에이전트 메타데이터**: 현재 구현은 에이전트의 ID와 이름만 기록하며, 모델 및 도구의 버전 상태, 상세 설정 파라미터 등은 아직 지원하지 않습니다.
- **RAG 지원**: 에이전트가 Retrieval-Augmented Generation(검색 증강 생성)을 활용할 때 외부 지식 소스의 추적은 현재 범위 밖입니다.
- **라이브 연결**: 평가 사용 사례에서 엣지 센서와 HPC 시뮬레이션 간의 직접 실시간 데이터 연결은 아직 개발 중입니다.
- **hallucination 탐지**: PROV-AGENT는 hallucination 발생 후 사후 추적을 지원하지만, 자동 탐지나 실시간 remediation은 미래 연구 과제로 남겨져 있습니다.

## Conclusion

PROV-AGENT는 agentic 워크플로우에서 AI 에이전트 상호작용을 추적하는 첫 번째 전용 provenance 프레임워크입니다. W3C PROV를 확장하고 MCP 개념을 통합함으로써, 프롬프트·응답·모델 호출·에이전트 결정을 전통적인 데이터 흐름과 동일한 그래프에서 표현합니다.

이 작업의 핵심 기여는 세 가지입니다. 첫째, 에이전트 아티팩트를 first-class 시민으로 취급하는 표준 호환 데이터 모델을 제시합니다. 둘째, 기존 MCP 기반 코드에 데코레이터 두 줄을 추가하는 것만으로 provenance 캡처가 가능한 실용적 구현을 제공합니다. 셋째, Edge–Cloud–HPC 연속체를 아우르는 실제 과학 워크플로우에서 end-to-end 추적과 hallucination 분석을 시연합니다.

AI 에이전트가 자율적으로 과학적 결정을 내리는 환경에서, 책임 있고 재현 가능한 AI를 위한 provenance 인프라는 선택이 아닌 필수입니다. PROV-AGENT는 그 기반을 체계적으로 확립하는 중요한 첫걸음입니다.
