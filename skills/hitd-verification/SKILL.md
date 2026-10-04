---
name: hitd-verification
description: |
  human-in-the-design の Verification Phase を担当する。実装が承認済みの仕様と Design Contract を満たすことを検証し、
  verification.md にまとめる。失敗または Contract Drift がある場合だけ人間に判断を求め、承認を得て作業の完了を確定する。
  発火: human-in-the-design スキルからの起動、「HITD の検証フェーズ」「hitd-verification で」という名指し。
  対象外: 失敗の修正(hitd-implementation へ渡す)。
  対象外: 契約または振る舞いの変更(hitd-design または hitd-detailed-specification へ渡す)。
  対象外: docs/hitd/ に承認済みの成果物がない通常のコードレビュー(このスキルを使わずに進める)。
---

# hitd-verification

このスキルは、実装を検証して Verification Report(検証結果)を作り、人間の承認を得るところまでを担当します。コードの修正は、この Phase では行いません。

- 入力: `status: approved` の `specification.md` と `design.md`、`contract-snapshot.md`、実装コード、テスト。前の Phase が `skipped` で成果物がない場合は、人間が指定した既存の仕様
- 成果物: `docs/hitd/<feature>/verification.md`
- 承認で委譲する権限: 作業を完了として扱うこと

## 前提

- `uv` が使えること
- コマンドは、対象プロジェクトのルートで実行すること
- コマンドの `<skill>` は、このスキルのフォルダのパスに読み替えること
- `<feature>` は、`human-in-the-design` スキルが決めた feature 名に読み替えること

## 手順

1. 開始できることを確かめる。
    - `uv run <skill>/assets/hitd-check.py gate docs/hitd/<feature> verification` を実行すること
    - 出力が `OK` なら手順2へ進む
    - `state.md` が見つからないという `NG:` の場合は、`human-in-the-design` スキルから始めるよう人間に伝えて停止する
    - そのほかの `NG:` の場合は、出力を人間に示して停止する
2. 入力を読む。
    - `specification.md`、`design.md`、`contract-snapshot.md` を読むこと。`skipped` の Phase の成果物がない場合は、既存の仕様の場所を人間にたずねて読む
    - 会話に残っている草案と不採用案は、入力として扱わないこと
    - 読み終えたら手順3へ進む
3. 検証を実行する。
    - プロジェクトのビルドとテストのコマンドを実行し、コマンドと結果を記録すること
    - ビルドのコマンドがないプロジェクトでは、ビルドの行に「コマンドなし」と記録すること
    - `contract-snapshot.md` がある場合は、`uv run <skill>/assets/hitd-check.py snapshot docs/hitd/<feature>/contract-snapshot.md --root .` を実行し、出力を記録すること
    - Acceptance Criteria ごとに、対応するテストの名前と結果を対にすること。対応するテストがない条件は、逸脱として記録する
    - すべて実行し終えたら手順4へ進む
4. Artifact(成果物)を書く。
    - 「成果物の形」のとおりに `verification.md` を `status: draft` で書くこと
    - `verification.md` がすでにある場合は、内容を書き換え、`status` を `draft` に戻すこと
    - 実行したコマンドと、その出力に基づく結果だけを書くこと。実行していない検証は「未実行」と書く
    - `uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/verification.md` の出力が `OK` なら、進み先を決める
        - 失敗、Contract Drift、逸脱が1件もない場合は、`Decisions` に「判断を要する項目なし」と書いて手順6へ進む
        - 1件以上ある場合は、手順5へ進む
5. Decision Check(判断確認)と Human Decision(人間による判断)を行う。
    - 失敗、Contract Drift、逸脱の1件ごとに、次の4つの案の Benefits と Costs / Risks を書き、Recommendation を別に添えて人間に示すこと。成り立たない案は除く
        - 修正する(Implementation Phase へ戻す)
        - Design Phase へ戻す
        - Specification Phase へ戻す
        - 現状を受け入れる
    - `Decisions` に、1件ごとに `### <件の題名>` の見出しを置き、人間が選んだ案、判断理由、受け入れた Trade-off、LLM の Recommendation を箇条書きで書くこと
    - すべての件で「現状を受け入れる」が選ばれた場合は、手順6へ進む
    - 戻す案が1件でも選ばれた場合は、手順8へ進む
6. Human Approval(人間による承認)を受ける。
    - `verification.md` のパス、検証結果の要約、`Authority Delegation` の文を人間に示し、Approve、Revise、Reject のどれかをたずねること
    - Approve の場合は、手順7へ進む
    - Revise の場合は、追加する検証を聞き、手順3へ戻る
    - Reject の場合は、成果物を `status: draft` のまま残し、停止する
7. 成果物を確定する。
    - `verification.md` の `status` を `approved` に、`approved_at` を承認の日付(`YYYY-MM-DD`)にすること
    - `state.md` の `phases.verification` を `completed` にすること
    - `artifact` と `state` の検査が両方 `OK` なら、終了する
8. Change Request を出す。
    - 戻す案が選ばれた1件ごとに、`docs/hitd/<feature>/change-requests/<4桁の連番>-<題名>.md` を「Change Request の形」のとおりに書くこと
    - 戻り先が1つの場合は、その Phase を人間に報告し、終了する
    - 戻り先が2つ以上ある場合は、specification、design、implementation の順で先にある Phase を人間に報告し、終了する

## 成果物の形

```markdown
---
phase: verification
status: draft
approved_at:
---

# <feature> Verification Report

## Verification Results

| 検証 | コマンド | 結果 |
|---|---|---|

| Acceptance Criteria | テスト | 結果 |
|---|---|---|

## Contract Drift
## Deviations
## Decisions
## Authority Delegation

この検証結果をもって、<feature> の作業を完了として扱うことを許可する。
```

## 検証結果の書き方の例

Good:

```text
| 検証 | コマンド | 結果 |
| テスト | dotnet test | 成功(42件中42件) |
| Contract Snapshot | hitd-check.py snapshot | NG: 12行目 FindAsync の宣言が見つからない |
```

Bad:

```text
実装を読んだ限り、仕様を満たしており、問題はなさそうです。
```

- 理由: 実行したコマンドと出力がなく、読み手が結果を確かめられない

## Change Request の形

```markdown
# <題名>

- 種別: 修正の要求、Design Change Request、Specification Change Request のいずれか
- 戻り先の Phase: implementation、design、specification のいずれか
- 変更対象: <成果物と見出し、または宣言>
- 必要な変更:
- 変更理由:
- 影響範囲:
- 現在の契約を維持する場合の代替案:
```

## hitd-check.py による検査

出力が `OK`、終了コードが 0 なら合格です。`NG:` の行が出た場合は、その行が示す箇所を直して再実行します。

```bash
uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/verification.md
```

```bash
uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>
```

## 停止条件

正常に終えて呼び出し元へ戻る場合を「終了」、人間の指示を待つ場合を「停止」と書いています。

- 手順7の検査が両方 `OK` になった
- 手順8で Change Request を出した
- 手順1の `gate` が `NG:` を出した
- 人間が Reject を選んだ
- 同じ `NG:` が3回続けて出た。この場合は、出力を人間に示して指示を待つ
