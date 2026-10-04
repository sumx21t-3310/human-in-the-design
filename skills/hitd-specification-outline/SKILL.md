---
name: hitd-specification-outline
description: |
  human-in-the-design の Specification Outline Phase を担当する。何を解決するか、Scope、Non-goals を人間と相談し、
  outline.md にまとめ、人間の判断と承認を得て確定する。
  発火: human-in-the-design スキルからの起動、「HITD の仕様概要フェーズ」「hitd-specification-outline で」という名指し。
  対象外: 振る舞いと受け入れ条件の詳細化(hitd-detailed-specification へ渡す)。
  対象外: 型と公開 API の設計(hitd-design へ渡す)。
  対象外: Phase を名指ししない開発依頼(human-in-the-design へ渡す)。
---

# hitd-specification-outline

このスキルは、Specification Outline(仕様概要)を作り、人間の承認を得るところまでを担当します。振る舞いの詳細と設計は、後の Phase が扱います。

- 入力: ユーザー要求、プロジェクト規約、関係する既存仕様
- 成果物: `docs/hitd/<feature>/outline.md`
- 承認で委譲する権限: Detailed Specification Phase を始めること

## 前提

- `uv` が使えること
- コマンドは、対象プロジェクトのルートで実行すること
- コマンドの `<skill>` は、このスキルのフォルダのパスに読み替えること
- `<feature>` は、`human-in-the-design` スキルが決めた feature 名に読み替えること

## 手順

1. 開始できることを確かめる。
    - `uv run <skill>/assets/hitd-check.py gate docs/hitd/<feature> outline` を実行すること
    - 出力が `OK` なら手順2へ進む
    - `state.md` が見つからないという `NG:` の場合は、`human-in-the-design` スキルから始めるよう人間に伝えて停止する
    - そのほかの `NG:` の場合は、出力を人間に示して停止する
2. 入力を読む。
    - `state.md` のユーザー要求、プロジェクト規約、関係する既存仕様を読むこと
    - `docs/hitd/<feature>/change-requests/` に、戻り先が outline で、末尾に `処理済み` の行がない Change Request がある場合は、読むこと
    - 読み終えたら手順3へ進む
3. Talk(相談)をする。
    - 次の6つを、人間と順に話すこと
        - 何を解決するか
        - Scope(対象範囲)
        - Non-goals(非目標)
        - 主要なユースケース
        - 制約
        - 今回決めない事項
    - 手順7の Revise、または Change Request で戻ってきた場合は、修正の要求または Change Request に関わる項目だけを話して、手順4へ進む
    - 6つすべてについて人間の考えを聞き終えたら、手順4へ進む
4. Artifact(成果物)を書く。
    - 「成果物の形」のとおりに `outline.md` を `status: draft` で書くこと
    - `outline.md` がすでにある場合は、内容を書き換え、`status` を `draft` に戻すこと
    - Talk で合意した内容だけを書くこと。合意に至っていない内容は `Unresolved Questions` に書く
    - `uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/outline.md` の出力が `OK` なら手順5へ進む
5. Decision Check(判断確認)を作る。
    - Scope と Non-goals のうち、採用できる案が2つ以上ある項目だけを対象にすること
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
    - `outline.md` の `status` を `approved` に、`approved_at` を承認の日付(`YYYY-MM-DD`)にすること
    - 手順2で読んだ Change Request の末尾に、`処理済み YYYY-MM-DD` の形の1行を足すこと
    - `state.md` の `phases.outline` を `completed` にすること
    - `artifact` と `state` の検査が両方 `OK` なら、終了する

## 成果物の形

```markdown
---
phase: outline
status: draft
approved_at:
---

# <feature> Specification Outline

## Goal
## Background
## Scope
## Non-goals
## Primary Use Cases
## Major Constraints
## Expected Outcome
## Unresolved Questions
## Decisions
## Authority Delegation

Detailed Specification Phase で、この Outline の Scope の範囲の振る舞いを詳細化することを許可する。
```

## Decision Check の形

Good:

```text
判断: 削除済みユーザーの取得を Scope に含めるか

案A: 含める
Benefits: 管理画面の復元機能が、同じ取得機能を使える
Costs / Risks: 取得結果に状態の区別が増え、利用側の分岐が増える

案B: 含めない(Non-goals に入れる)
Benefits: 取得結果は有効なユーザーだけになり、利用側が単純になる
Costs / Risks: 復元機能は、別の取得手段を後から用意することになる

Recommendation: 案B。主要なユースケースに復元がないため
```

Bad:

```text
削除済みユーザーの扱いとして正しいものはどれですか。
1. 含める  2. 含めない  3. データベースを削除する
```

- 理由: 採用できない案が混ざっており、Trade-off が書かれていないので、人間が判断の材料を得られない

## hitd-check.py による検査

出力が `OK`、終了コードが 0 なら合格です。`NG:` の行が出た場合は、その行が示す箇所を直して再実行します。

```bash
uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/outline.md
```

```bash
uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>
```

## 停止条件

正常に終えて呼び出し元へ戻る場合を「終了」、人間の指示を待つ場合を「停止」と書いています。

- 手順8の検査が両方 `OK` になった。次の Phase の作業は始めずに終了する
- 手順1の `gate` が `NG:` を出した
- 人間が Reject を選んだ
- 同じ `NG:` が3回続けて出た。この場合は、出力を人間に示して指示を待つ
