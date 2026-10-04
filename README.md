# human-in-the-design

## 概要

`human-in-the-design` は、LLMを使ったソフトウェア開発で、仕様や設計を段階的に具体化し、重要な判断を人間が承認してから次の工程をLLMへ委任するための開発ワークフローです。

LLMには、仕様整理、設計案の作成、スタブ生成、ドキュメントコメント作成、実装、テストなど、多くの作業を委任できます。

一方で、要求の解釈、責務分割、公開API、データモデル、依存方向などの判断まで一度に任せると、最初の前提が間違っていた場合、その誤りを引き継いだ詳細仕様や実装が大量に生成される可能性があります。

`human-in-the-design` では、この問題を避けるために、開発工程をHuman Decision Boundary（人間による判断境界）ごとのPhase（フェーズ）に分割します。

各Phaseは、次の共通した流れを持ちます。

```text
Talk（相談）
    ↓
Artifact（成果物）
    ↓
Decision Check（判断確認）
    ↓
Human Decision（人間による判断）
    ↓
Human Approval（人間による承認）
    ↓
Authority Delegation（権限委譲）
```

一つのSkillは、原則として一つのPhaseを担当します。

```text
1 Skill
=
1 Phase
=
1 Human Decision Boundary
```

人間がすべての成果物を書くことは求めません。

探索、生成、比較、分析はLLMへ委任し、**後から変更するコストが高い判断と、次の工程へ進む許可だけを人間が担当する**ことを基本とします。

## 背景

LLMに「この機能を実装してください」と直接依頼すると、LLMは実装以外にも多くの判断を行います。

たとえば「ユーザー取得機能を追加する」という依頼だけでも、次のような判断が必要です。

- 何を取得成功とみなすか
- 削除済みユーザーをどう扱うか
- どのクラスが処理を担当するか
- Repository（リポジトリ）を設けるか
- どの型を公開するか
- DTO（データ転送オブジェクト）を分けるか
- `null` とエラーをどう区別するか
- 状態を誰が所有するか
- どの依存関係を許可するか

これらを一度に決めると、最初の判断ミスが詳細仕様、設計、実装へ連鎖します。

人間側も、問題設定、振る舞い、構造、実装を同時にレビューしなければならず、確認の負担が大きくなります。

そこで `human-in-the-design` では、判断を次のように分離します。

```text
Problem（何を解決するか）
    ↓
Behavior（どう振る舞うか）
    ↓
Structure（どう分けるか）
    ↓
Implementation（どう実現するか）
```

各段階を独立したPhaseとして扱い、そのPhaseで必要な判断だけを人間へ返します。

# 設計原則

## 1 Skill = 1 Phase = 1 Human Decision Boundary

一つのSkillは、一つのHuman Decision Boundary（人間による判断境界）だけを担当します。

Skill内部では、次の流れを完結させます。

```text
Input Artifact（入力成果物）
    ↓
Talk（相談）
    ↓
Artifact（成果物）
    ↓
Decision Check（判断確認）
    ↓
Human Decision（人間による判断）
    ↓
Human Approval（人間による承認）
    ↓
Approved Artifact（承認済み成果物）
    +
Authority Delegation（権限委譲）
```

Skillは、次のPhaseの仕事まで先回りしません。

たとえばSpecification Phase（仕様フェーズ）は設計を行わず、Design Phase（設計フェーズ）は実装を行いません。

これにより、各Skillの責務と権限範囲を明確にします。

## Talk（相談）とArtifact（成果物）を分離する

Talk（相談）は、まだ結論を固定しない探索の場です。

ここでは、次のような内容を扱います。

- 前提条件の確認
- 問題の整理
- 代替案の探索
- 懸念点の発見
- Trade-off（トレードオフ）の分析
- 不明点の整理
- 今回決めない事項の切り分け

Talkで出た内容は、まだ確定事項ではありません。

```text
Talk
→ Divergence（発散）

Artifact
→ Convergence（収束）
```

Artifact（成果物）は、Talkで得られた情報から、そのPhaseで判断するために必要な内容だけを整理したものです。

後続Phaseには、対話履歴そのものではなく、承認されたArtifactを渡します。

## 人間は生成ではなく判断を担当する

人間がSpecification（仕様）やDesign Stub（設計スタブ）を手書きすることは求めません。

成果物の生成、代替案の整理、Trade-off（トレードオフ）の分析は、可能な限りLLMへ委任します。

人間が主に担当するのは、次の判断です。

- 何を作るか
- 何を作らないか
- どの振る舞いを保証するか
- 責務をどこで分けるか
- どのAPIを公開するか
- どのデータ契約を固定するか
- どの依存方向を許可するか
- 状態を誰が所有するか
- どのTrade-offを受け入れるか

privateメソッドの構成や局所的なアルゴリズムなど、後から変更しやすい判断は原則としてLLMへ委任します。

## Human Decision（人間による判断）とHuman Approval（人間による承認）を分ける

Human Decision（人間による判断）は、どの案を採用するかを決める行為です。

たとえば、次のような判断です。

```text
DTOを分離する
Repositoryは導入しない
状態はElementが所有する
```

Human Approval（人間による承認）は、その判断と成果物を確定し、次のPhaseをLLMへ委任する行為です。

```text
Human Decision
→ 何を選ぶか

Human Approval
→ その判断を確定してよいか

Authority Delegation
→ 次の工程でLLMに何を任せるか
```

この二つを分けることで、「案を選んだこと」と「実行を許可したこと」を区別します。

## 承認はAuthority Delegation（権限委譲）として扱う

Human Approval（人間による承認）は、単なる確認操作ではありません。

承認とは、**採用する判断、判断理由、受け入れるTrade-offを確認した上で、次のPhaseを実行する権限をLLMへ渡すこと**です。

```text
Artifact
    ↓
Decision Check
    ↓
Human Decision
    ↓
Human Approval
    ↓
Authority Delegation
```

次のPhaseは、このAuthority Delegation（権限委譲）が行われてから開始します。

## Decision Check（判断確認）はクイズにしない

Decision Check（判断確認）は、知識や記憶を試すためのものではありません。

明らかな誤答を混ぜた四択問題は使用しません。

複数の現実的な選択肢と、それぞれのTrade-offを提示します。

たとえば、APIのデータ境界を決める場合は次のようにします。

```text
案A: Domain Modelを直接公開する

Benefits（利点）
- DTOやMappingが不要
- 初期実装が単純

Costs / Risks（コスト・リスク）
- Domain Modelの変更が公開APIへ伝わる
- 内部モデルと外部契約が結合する


案B: Response DTOを分離する

Benefits（利点）
- Domain Modelと公開APIを独立して変更できる
- 公開する情報を明示できる

Costs / Risks（コスト・リスク）
- DTOとMappingの実装・保守コストが増える
```

LLMはRecommendation（推奨案）を示せます。

ただし、Recommendation（推奨）とHuman Decision（人間による判断）は分離します。

人間はLLMの推奨とは異なる案を選択できます。

## Decision Check（判断確認）をADRの入力として使う

Design（設計）に関するDecision Checkでは、可能な範囲で次の情報を整理します。

- Context（背景）
- Alternatives（代替案）
- Trade-offs（トレードオフ）
- Recommendation（LLMによる推奨）
- Human Decision（人間による判断）
- Rationale（判断理由）
- Consequences（結果・影響）

重要な設計判断がHuman Approvalによって確定した場合、この情報からADR（Architecture Decision Record / 設計判断記録）を生成できます。

```text
Decision Check
    ↓
Human Decision
    ↓
Human Approval
    ├─ Design Contract（現在の設計）
    └─ ADR（なぜそう決めたか）
```

すべての判断をADRとして残す必要はありません。

主に、後から変更するコストが高く、判断理由を将来参照する価値があるものを対象とします。

## Approved Artifact（承認済み成果物）をPhase間の契約とする

Human Approvalを通過したArtifactは、Approved Artifact（承認済み成果物）として固定します。

後続Phaseは、このApproved Artifactを入力として動作します。

```text
Phase A

Talk
↓
Artifact
↓
Decision
↓
Approval
↓
Approved Artifact A

        ↓

Phase B

Input = Approved Artifact A
```

途中のDraft（草案）、Rejected Alternative（不採用案）、修正前の成果物は、後続Phaseの正しい入力として扱いません。

この境界を、Context Cleansing（コンテキスト整理）としても利用します。

## 必要以上に上位Phaseへ戻らない

Revise（修正要求）が発生した場合、原則として現在のPhase内で修正します。

```text
Talk
 ↓
Artifact
 ↓
Human Decision
 ├─ Revise
 │    ↓
 │   Talk
 │    ↓
 │   Revised Artifact
 │
 └─ Approve
      ↓
 Approved Artifact
```

Design（設計）の問題だけでSpecification（仕様）まで戻すなど、不必要な巻き戻しは行いません。

上位のApproved Artifactを変更する必要がある場合だけ、そのPhaseへ戻ります。

## Design Stub（設計スタブ）を設計成果物の中心とする

Design Phase（設計フェーズ）では、設計案を可能な限りコンパイル可能なDesign Stub（設計スタブ）として表現します。

たとえばC#では次のようになります。

```csharp
/// <summary>
/// 指定されたユーザーIDに対応する有効なユーザーを取得します。
/// </summary>
/// <returns>
/// ユーザーが存在しない場合は <c>null</c> を返します。
/// </returns>
Task<User?> FindAsync(
    UserId id,
    CancellationToken cancellationToken = default);
```

この段階では内部実装を含めません。

Design Stubによって、次の設計要素をコードとして確認できるようにします。

- 型
- 公開API
- DTO
- Value Object（値オブジェクト）
- interface
- 依存方向
- 状態所有
- ライフサイクル

## ドキュメントコメントをDesign Contract（設計契約）の一部とする

型だけでは表現できないContract（契約）は、Design Stubと同時にドキュメントコメントへ記述します。

主な対象は次のとおりです。

- APIの責務
- 引数の意味
- 戻り値の意味
- `null` の意味
- 発生する例外
- 副作用
- 状態遷移
- 所有権
- ライフサイクル上の制約
- 必要な場合のスレッド安全性

これらを明確に説明できない場合、Specification（仕様）またはDesign（設計）が曖昧である可能性があります。

その場合は実装側で推測せず、該当するPhaseへ戻します。

# Phase Contract（フェーズ契約）

すべてのPhaseは、原則として次の構造を持ちます。

```text
Phase

Input
→ 前PhaseのApproved Artifact

Talk
→ 探索、相談、代替案の分析

Artifact
→ 今回のPhaseで確定候補となる成果物

Decision Check
→ 選択肢とTrade-offの整理

Human Decision
→ 採用案の決定

Human Approval
→ ArtifactとDecisionの確定

Output
→ Approved Artifact

Authority Delegation
→ 次Phaseへ許可する作業
```

すべてのPhase Skillは、このPhase Contract（フェーズ契約）に従います。

# Phase構成

## Specification Outline Phase（仕様概要フェーズ）

### Input（入力）

- User Request（ユーザー要求）
- Project Rules（プロジェクト規約）
- 必要な既存仕様

### Talk（相談）

次の内容を整理します。

- 何を解決するか
- Scope（対象範囲）
- Non-goals（非目標）
- 主要ユースケース
- 制約
- 未決定事項

### Artifact（成果物）

Specification Outline（仕様概要）を生成します。

主な内容は次のとおりです。

- Goal（目的）
- Background（背景）
- Scope（対象範囲）
- Non-goals（非目標）
- Primary Use Cases（主要ユースケース）
- Major Constraints（主要な制約）
- Expected Outcome（期待する結果）
- Unresolved Questions（未決定事項）

### Decision Check（判断確認）

ScopeやNon-goalsに複数の妥当な選択肢がある場合、それぞれのTrade-offを提示します。

### Authority Delegation（権限委譲）

承認後、Detailed Specification Phase（詳細仕様フェーズ）へ進む権限を委譲します。

## Detailed Specification Phase（詳細仕様フェーズ）

### Input（入力）

Approved Specification Outline（承認済み仕様概要）

### Talk（相談）

具体的な振る舞い、境界ケース、エラー時の処理などを検討します。

### Artifact（成果物）

Detailed Specification（詳細仕様）を生成します。

主な内容は次のとおりです。

- Functional Requirements（機能要件）
- Behavioral Rules（振る舞いの規則）
- Acceptance Criteria（受け入れ条件）
- Edge Cases（境界ケース）
- Error Behavior（エラー時の振る舞い）
- State Transitions（状態遷移）
- Compatibility Requirements（互換性要件）
- Constraints（制約）

### Decision Check（判断確認）

複数の妥当な振る舞いがある部分について、それぞれのTrade-offを提示します。

### Authority Delegation（権限委譲）

承認後、Design Phase（設計フェーズ）へ進む権限を委譲します。

## Design Phase（設計フェーズ）

### Input（入力）

- Approved Detailed Specification（承認済み詳細仕様）
- Project Rules（プロジェクト規約）

### Talk（相談）

次の内容を検討します。

- 責務分割
- 公開API
- DTO
- Value Object
- interface
- 依存方向
- 状態所有
- ライフサイクル
- Alternative（代替案）

### Artifact（成果物）

次の成果物を生成します。

```text
Design Stub（設計スタブ）
+
Contract Documentation（契約ドキュメント）
```

### Decision Check（判断確認）

変更コストの高い設計判断について、現実的なAlternative（代替案）とTrade-offを提示します。

### Human Decision（人間による判断）

採用する設計を決定します。

### Human Approval（人間による承認）

承認された成果物をDesign Contract（設計契約）として固定します。

必要な判断についてはADRを生成します。

### Authority Delegation（権限委譲）

承認されたDesign Contractの範囲内で、Implementation Phase（実装フェーズ）へ進む権限を委譲します。

## Implementation Phase（実装フェーズ）

### Input（入力）

- Approved Specification（承認済み仕様）
- Design Contract（設計契約）
- 必要なADR
- Project Rules（プロジェクト規約）

### Talk（相談）

実装中に必要な局所的な判断を扱います。

Design Contractを変更しない範囲の判断は、原則としてLLMへ委任します。

### Artifact（成果物）

実装コードとテストを生成します。

### Decision Check（判断確認）

通常は行いません。

現在委譲されているAuthority（権限）を超える変更が必要になった場合は、Implementation Phaseを停止します。

### Human Decision / Approval

Contract Surface（契約面）の変更が必要な場合は、このPhase内で承認せず、Design Change Request（設計変更要求）としてDesign Phaseへ戻します。

### Authority Delegation（権限委譲）

実装完了後、Verification Phase（検証フェーズ）へ進む権限を委譲します。

## Verification Phase（検証フェーズ）

### Input（入力）

- Approved Specification（承認済み仕様）
- Design Contract（設計契約）
- 実装コード
- テスト
- Contract Snapshot（契約スナップショット）

### Talk（相談）

検証結果や逸脱を分析します。

### Artifact（成果物）

Verification Report（検証結果）を生成します。

### Decision Check（判断確認）

失敗やContract Drift（契約逸脱）があり、人間の判断が必要な場合だけ実施します。

### Human Decision（人間による判断）

必要に応じて、次のいずれかを判断します。

- 修正する
- Design Phaseへ戻す
- Specification Phaseへ戻す
- 現状を受け入れる

### Authority Delegation（権限委譲）

すべての検証条件を満たした場合、作業完了を許可します。

# Contract Drift Prevention（契約逸脱の抑止）

Design Approval（設計承認）後、変更コストの高いContract Surface（契約面）をContract Snapshot（契約スナップショット）として固定します。

対象は、たとえば次のとおりです。

- public / protected型
- public / protectedメソッド
- 引数
- 戻り値
- interface
- DTO
- 継承関係
- nullability
- 必要なAttribute
- Generic Constraint

Implementation Phaseでは、Contract Snapshotと現在のコードを比較します。

利用可能な環境では、次のような機械的検査を利用します。

- コンパイル
- API Surface比較
- AST比較
- Roslyn等による解析
- 静的解析
- Git Diffによる変更箇所の特定

Git DiffだけでContract Driftを判定しません。

Contract Driftを検出した場合は、実装失敗ではなく、

**現在委譲されている権限では実行できない変更が必要になった**

と扱います。

```text
Contract Drift
    ↓
Implementation Stop
    ↓
Design Change Request
    ↓
Design Phase
```

# Context Cleansing（コンテキスト整理）

Phase境界では、次Phaseへ渡す情報をApproved Artifact（承認済み成果物）へ収束させます。

```text
Talk
├─ Draft A
├─ Draft B
├─ Rejected Alternative
└─ Revised Draft
        ↓
Human Approval
        ↓
Approved Artifact
        ↓
Next Phase
```

次Phaseでは、未承認のDraftやRejected Alternativeを正しい情報として扱いません。

主要な入力は原則として次のとおりです。

```text
Approved Artifacts
+
Current User Request
+
Project Rules
```

# Change Request（変更要求）

実行中に上位のApproved Artifactを変更する必要が生じた場合、LLMは勝手に変更しません。

```text
Behaviorを変更する必要がある
→ Specification Change Request（仕様変更要求）

Structure / Contractを変更する必要がある
→ Design Change Request（設計変更要求）
```

Change Requestには、最低限次の内容を含めます。

- 変更対象
- 必要な変更
- 変更理由
- 影響範囲
- 現在の契約を維持する場合の代替案

変更が必要な最も近い上位Phaseへ戻ります。

不要にさらに上位へ巻き戻しません。

# State Transition（状態遷移）

全体は次の状態遷移として表現できます。

```text
OUTLINE_PHASE
    ↓ Approval
SPECIFICATION_PHASE
    ↓ Approval
DESIGN_PHASE
    ↓ Approval
IMPLEMENTATION_PHASE
    ↓
VERIFICATION_PHASE
    ↓ Approval
DONE
```

各Phase内部では、共通して次の状態を持ちます。

```text
TALK
 ↓
ARTIFACT_DRAFT
 ↓
DECISION_CHECK
 ↓
HUMAN_DECISION
 ├─ Revise → TALK
 ├─ Reject → Previous Phase / Cancel
 └─ Approve
      ↓
 APPROVED_ARTIFACT
      ↓
 AUTHORITY_DELEGATED
```

この状態遷移を各Skillで共通利用します。

# Skill構成

`human-in-the-design` は、全体の状態遷移を管理するOrchestrator（オーケストレーター）として扱います。

個別Skillは、それぞれ一つのPhaseを担当します。

```text
human-in-the-design
│
├─ specification-outline
│   → Specification Outline Phase
│
├─ detailed-specification
│   → Detailed Specification Phase
│
├─ design
│   → Design Phase
│
├─ implementation
│   → Implementation Phase
│
└─ verification
    → Verification Phase
```

必要に応じて、ADR生成やContract Drift Detection（契約逸脱検知）などの補助Skillを利用できます。

Phase Skillと補助Skillは区別します。

Phase SkillはHuman Decision Boundaryを持ちます。

補助Skillは、Phase内部から呼ばれる生成や分析だけを担当し、人間への権限委譲境界は持ちません。

# Decision Check Prompting Guideline（判断確認の生成原則）

Decision Checkは、次の原則に従います。

- 明らかな誤答を含むクイズにしない
- 一般知識を試験しない
- 実際に採用可能な案だけを提示する
- メリットだけでなくコストとリスクを示す
- 各案の説明粒度を揃える
- RecommendationとHuman Decisionを分離する
- 人間が提示された案以外を提案できるようにする
- 判断する必要がない項目にはDecision Checkを作らない
- 必要に応じてADRへ変換できる情報を残す

Decision Checkの目的は、正解を当てることではありません。

**複数の成立する選択肢の中から、どのTrade-offを受け入れるかを人間が決めること**です。

# 小規模変更への適用

すべての変更で、すべてのPhaseを実行する必要はありません。

既存のApproved Artifactを変更しないTrivial Change（軽微な変更）では、必要なPhaseだけを実行します。

たとえば、既存仕様とDesign Contractの範囲内に収まる単純なバグ修正では、

```text
Implementation Phase
    ↓
Verification Phase
```

だけで構いません。

既存仕様は維持したままDesign Contractだけを変更する場合は、

```text
Design Phase
    ↓
Implementation Phase
    ↓
Verification Phase
```

とします。

つまり、常に最初のPhaseから開始するのではなく、**変更対象となる最上位のHuman Decision Boundaryから開始する**ことを原則とします。

# 人間とLLMの責務分担

```text
Human（人間）
├─ Scope Decision（対象範囲の判断）
├─ Behavior Decision（振る舞いの判断）
├─ Trade-off Decision（トレードオフ判断）
├─ Responsibility Boundary Decision（責務境界の判断）
├─ Public API Decision（公開APIの判断）
├─ Data Contract Decision（データ契約の判断）
├─ Dependency Direction Decision（依存方向の判断）
├─ Human Approval（承認）
└─ Authority Delegation（権限委譲）

LLM
├─ Talk Support（相談支援）
├─ Requirement Analysis（要求分析）
├─ Artifact Generation（成果物生成）
├─ Alternative Generation（代替案生成）
├─ Trade-off Analysis（トレードオフ分析）
├─ Recommendation Generation（推奨案生成）
├─ Design Stub Generation（設計スタブ生成）
├─ Contract Documentation（契約コメント生成）
├─ ADR Generation（設計判断記録生成）
├─ Implementation（実装）
├─ Test Generation（テスト生成）
├─ Contract Drift Detection（契約逸脱検知）
└─ Verification（検証）
```

# Non-goals（非目標）

このSkillは、すべての判断を人間へ戻すことを目的としません。

また、次のことも目的としません。

- 人間がすべての仕様を書くこと
- 人間がすべての設計を書くこと
- 人間がスタブを手書きすること
- Decision Checkを知識クイズにすること
- 明らかな誤答を用意して擬似的な選択を作ること
- LLMのRecommendationを人間へ強制すること
- すべての判断をADRとして保存すること
- Contract Surfaceの変更そのものを禁止すること
- privateな実装詳細まで事前に固定すること
- 将来の可能性だけを理由に抽象化を増やすこと
- すべての変更で全Phaseを実行すること
- Phase Skillが次のPhaseの仕事まで先回りすること

# 期待する効果

`human-in-the-design` では、開発をHuman Decision Boundary（人間による判断境界）ごとのPhaseへ分割します。

```text
Talk
→ 探索する

Artifact
→ 現在の案を収束させる

Decision Check
→ 選択肢とTrade-offを明確にする

Human Decision
→ 採用案を選ぶ

Human Approval
→ 判断を確定する

Authority Delegation
→ 次の仕事をLLMへ任せる
```

これにより、LLMは各Phaseで必要な問題だけに集中できます。

人間も、完成した大量のコードを見てから、仕様・設計・実装をまとめて確認する必要がなくなります。

さらに、Phase間をApproved Artifact（承認済み成果物）で接続することで、途中の相談や不採用案を次工程へ持ち込まず、コンテキストを整理できます。

`human-in-the-design` の中心にある考え方は、LLMの自律性をなくすことではありません。

**一つのSkillを一つのHuman Decision Boundaryとして扱い、LLMに探索と生成を任せ、人間が重要なTrade-offを確定し、その判断に基づいて次のPhaseに必要な権限だけを段階的に委譲すること**が、このSkill群の設計原則です。
