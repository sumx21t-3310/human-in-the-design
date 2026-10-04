---
name: hitd-detailed-specification
description: |
  human-in-the-design の Detailed Specification Phase を担当する。承認済みの outline.md をもとに、振る舞い、境界ケース、
  エラー時の処理を人間と相談し、specification.md にまとめ、人間の判断と承認を得て確定する。
  発火: human-in-the-design スキルからの起動、「HITD の詳細仕様フェーズ」「hitd-detailed-specification で」という名指し。
  対象外: Scope と Non-goals の決定(hitd-specification-outline へ渡す)。
  対象外: 型と公開 API の設計(hitd-design へ渡す)。
  対象外: Phase を名指ししない開発依頼(human-in-the-design へ渡す)。
---

# hitd-detailed-specification

このスキルは、Detailed Specification(詳細仕様)を作り、人間の承認を得るところまでを担当します。責務の分け方と型は、Design Phase が扱います。

- 入力: `status: approved` の `docs/hitd/<feature>/outline.md`、ユーザー要求、プロジェクト規約。outline が `skipped` で `outline.md` がない場合は、人間が指定した既存の仕様
- 成果物: `docs/hitd/<feature>/specification.md`
- 承認で委譲する権限: Design Phase を始めること

## 前提

- `uv` が使えること
- コマンドは、対象プロジェクトのルートで実行すること
- コマンドの `<skill>` は、このスキルのフォルダのパスに読み替えること
- `<feature>` は、`human-in-the-design` スキルが決めた feature 名に読み替えること

## 手順

1. 開始できることを確かめる。
    - `uv run <skill>/assets/hitd-check.py gate docs/hitd/<feature> specification` を実行すること
    - 出力が `OK` なら手順2へ進む
    - `state.md` が見つからないという `NG:` の場合は、`human-in-the-design` スキルから始めるよう人間に伝えて停止する
    - そのほかの `NG:` の場合は、出力を人間に示して停止する
2. 入力を読む。
    - `outline.md`、`state.md` のユーザー要求、プロジェクト規約を読むこと。outline が `skipped` で `outline.md` がない場合は、既存の仕様の場所を人間にたずねて読む
    - `docs/hitd/<feature>/change-requests/` に、戻り先が specification で、末尾に `処理済み` の行がない Change Request がある場合は、読むこと
    - 会話に残っている草案と不採用案は、入力として扱わないこと
    - 読み終えたら手順3へ進む
3. Talk(相談)をする。
    - 次の5つを、人間と順に話すこと
        - 主要なユースケースごとの具体的な振る舞い
        - 境界ケース
        - エラー時の振る舞い
        - 状態遷移
        - 互換性の要件
    - Scope または Non-goals を変える必要が出た場合は、手順9へ進む
    - 手順7の Revise、または Change Request で戻ってきた場合は、修正の要求または Change Request に関わる項目だけを話して、手順4へ進む
    - 5つすべてについて人間の考えを聞き終えたら、手順4へ進む
4. Artifact(成果物)を書く。
    - 「成果物の形」のとおりに `specification.md` を `status: draft` で書くこと
    - `specification.md` がすでにある場合は、内容を書き換え、`status` を `draft` に戻すこと
    - Acceptance Criteria は、合否を判定できる文で書くこと
    - `uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/specification.md` の出力が `OK` なら手順5へ進む
5. Decision Check(判断確認)を作る。
    - 採用できる振る舞いが2つ以上ある項目だけを対象にすること
    - 「Decision Check の形」のとおりに、案ごとの Benefits と Costs / Risks を同じ細かさで書くこと
    - Talk で人間がすでに案を選んだ項目は、対象から除き、選んだ内容を手順6の書式で `Decisions` に書くこと
    - 対象の項目がない場合は、手順7へ進む。`Decisions` に1件も書かれていないときは、「判断を要する項目なし」と書く
    - 対象の項目がある場合は、手順6へ進む
6. Human Decision(人間による判断)を受ける。
    - Decision Check を1項目ずつ人間に示し、採用する案をたずねること。選択肢を示す UI がある環境では、その UI を使う
    - 人間は、示した案のほかの案も出せる。その場合は、その案を採用案として扱う
    - `Decisions` に、判断ごとに `### <判断の題名>` の見出しを置き、採用案、判断理由、受け入れた Trade-off、LLM の Recommendation を箇条書きで書くこと
    - 成果物の本文を採用案に合わせること
    - すべての項目に採用案が決まったら、手順7へ進む
7. Human Approval(人間による承認)を受ける。
    - 成果物のパス、`Decisions` の要約、`Authority Delegation` の文を人間に示し、Approve、Revise、Reject のどれかをたずねること
    - Approve の場合は、手順8へ進む
    - Revise の場合は、修正の要求を聞き、手順3へ戻る
    - Reject の場合は、成果物を `status: draft` のまま残し、停止する
8. 成果物を確定する。
    - `specification.md` の `status` を `approved` に、`approved_at` を承認の日付(`YYYY-MM-DD`)にすること
    - 手順2で読んだ Change Request の末尾に、`処理済み YYYY-MM-DD` の形の1行を足すこと
    - `state.md` の `phases.specification` を `completed` にすること
    - `artifact` と `state` の検査が両方 `OK` なら、終了する
9. Specification Change Request を出す。
    - `docs/hitd/<feature>/change-requests/<4桁の連番>-<題名>.md` に、「Change Request の形」のとおりに書くこと
    - 戻り先の Phase を outline として人間に報告し、終了する

## 成果物の形

```markdown
---
phase: specification
status: draft
approved_at:
---

# <feature> Detailed Specification

## Functional Requirements
## Behavioral Rules
## Acceptance Criteria
## Edge Cases
## Error Behavior
## State Transitions
## Compatibility Requirements
## Constraints
## Decisions
## Authority Delegation

Design Phase で、この仕様を満たす責務分割、公開 API、データ契約を設計することを許可する。
```

## Decision Check の形

Good:

```text
判断: 指定した ID のユーザーが存在しないときの振る舞い

案A: 「存在しない」を正常な結果として返す
Benefits: 利用側は、存在の確認と取得を1回の呼び出しで済ませられる
Costs / Risks: 利用側が確認を忘れると、後段で原因の分かりにくいエラーになる

案B: エラーとして返す
Benefits: 確認を忘れても、その場で失敗が分かる
Costs / Risks: 存在しないことが普通に起きる画面では、エラー処理が増える

Recommendation: 案A。Outline のユースケースに、存在の確認を兼ねた取得があるため
```

Bad:

```text
判断: FindAsync の戻り値を Task<User?> にするか Result<User> にするか
```

- 理由: 型の選択は Design Phase の判断であり、この Phase の範囲を越えている

## Change Request の形

```markdown
# <題名>

- 種別: Specification Change Request
- 戻り先の Phase: outline
- 変更対象: <成果物と見出し>
- 必要な変更:
- 変更理由:
- 影響範囲:
- 現在の契約を維持する場合の代替案:
```

## hitd-check.py による検査

出力が `OK`、終了コードが 0 なら合格です。`NG:` の行が出た場合は、その行が示す箇所を直して再実行します。

```bash
uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/specification.md
```

```bash
uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>
```

## 停止条件

正常に終えて呼び出し元へ戻る場合を「終了」、人間の指示を待つ場合を「停止」と書いています。

- 手順8の検査が両方 `OK` になった。次の Phase の作業は始めずに終了する
- 手順9で Change Request を出した
- 手順1の `gate` が `NG:` を出した
- 人間が Reject を選んだ
- 同じ `NG:` が3回続けて出た。この場合は、出力を人間に示して指示を待つ
