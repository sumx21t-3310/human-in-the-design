---
name: human-in-the-design
description: |
  LLM を使った開発を、Phase ごとに人間の承認を得ながら進める human-in-the-design の入口。
  開始する Phase を決め、状態を docs/hitd/<feature>/state.md に記録し、Phase Skill を順に起動する。
  発火: 「human-in-the-design で進めて」「HITD で作って」「HITD を再開して」。
  対象外: Phase を名指しした依頼(hitd-specification-outline、hitd-detailed-specification、hitd-design、hitd-implementation、hitd-verification のうち該当する Phase Skill へ渡す)。
  対象外: 人間の承認を挟まない通常の実装依頼(このスキル群を使わずに進める)。
---

# human-in-the-design

このスキルは、開発全体の状態遷移を管理します。成果物の作成と人間への判断確認は、Phase Skill が担当します。

| Phase | Phase Skill | 成果物 |
|---|---|---|
| outline | `hitd-specification-outline` | `outline.md` |
| specification | `hitd-detailed-specification` | `specification.md` |
| design | `hitd-design` | `design.md`、Design Stub、`contract-snapshot.md`、`adr/` |
| implementation | `hitd-implementation` | 実装コードとテスト |
| verification | `hitd-verification` | `verification.md` |

成果物は、対象プロジェクトの `docs/hitd/<feature>/` に保存します。

## 前提

- `uv` が使えること
- コマンドは、対象プロジェクトのルートで実行すること
- コマンドの `<skill>` は、このスキルのフォルダのパスに読み替えること
- `<feature>` は、手順1で決めた feature 名に読み替えること

## 手順

1. feature 名を決める。
    - 依頼の内容から、英小文字とハイフンの名前を1つ決めること(例: `user-lookup`)
    - `docs/hitd/<feature>/state.md` がすでにあり、`current_phase` が `done` 以外の場合は、手順4へ進む
    - `state.md` がすでにあり、`current_phase` が `done` の場合は、新しい依頼として手順2へ進む。手順3では、frontmatter と「ユーザー要求」の行を書き直し、本文に書かれたプロジェクト規約は残す
    - ない場合は、手順2へ進む
2. 開始する Phase を決める。
    - 依頼が変更する対象のうち、次の表で最も上にある行の Phase を開始 Phase とすること
    - 開始 Phase と理由を人間に示し、同意を得たら手順3へ進む
    - 人間が別の Phase を指定した場合は、その Phase を開始 Phase として手順3へ進む

    | 依頼が変更する対象 | 開始 Phase |
    |---|---|
    | 何を解決するか、Scope、Non-goals | outline |
    | 振る舞い、受け入れ条件、エラー時の処理 | specification |
    | 公開 API、型、DTO、依存方向、状態の所有 | design |
    | 承認済みの仕様と Design Contract の範囲に収まるコード | implementation |
3. `docs/hitd/<feature>/state.md` を作る。
    - 次の形で書くこと。開始 Phase を `in_progress`、開始 Phase より前を `skipped`、後を `pending` とする

    ```markdown
    ---
    feature: user-lookup
    current_phase: outline
    phases:
      outline: in_progress
      specification: pending
      design: pending
      implementation: pending
      verification: pending
    ---

    # user-lookup

    ユーザー要求: <依頼の文面>
    ```

    - `uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>` を実行し、出力が `OK` なら手順4へ進む
4. `state.md` の `current_phase` を読み、進み先を決める。
    - `done` の場合は、手順7へ進む
    - その Phase が `in_progress` の場合は、手順5へ進む
    - その Phase が `completed` の場合は、手順6へ進む
5. `current_phase` の Phase Skill を起動する。
    - Phase Skill へ渡す入力は、feature 名、ユーザー要求、プロジェクト規約の3つとすること
    - プロジェクト規約は、対象プロジェクトの `AGENTS.md`、`CLAUDE.md`、`CONTRIBUTING.md` のうち、あるものを指す
    - 3つともない場合は、使う言語、ビルドのコマンド、テストのコマンドを人間にたずね、`state.md` の本文に書いて規約として渡すこと
    - Phase Skill が終了したら、終了の理由で進み先を決める
        - 承認または完了で終了した場合は、手順6へ進む
        - Change Request を出して終了した場合は、次の順に `state.md` を書き換える
            1. `current_phase` を、Change Request の戻り先の Phase にする
            2. その Phase を `in_progress` にする
            3. それより後の Phase を `pending` にする
            4. `state` の検査が `OK` なら、手順5へ進む
        - 人間が Reject または中止を選んで終了した場合は、停止する
        - `NG:` を出して終了した場合は、出力を人間に示して停止する
6. 次の Phase へ進める。
    - `current_phase` が verification の場合は、`current_phase` を `done` にすること
    - それ以外の場合は、`current_phase` を次の Phase に書き換え、その Phase を `in_progress` にすること
    - `uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>` を実行し、出力が `OK` なら手順4へ進む
7. 完了を報告する。
    - 承認済みの成果物のパスと、`verification.md` の結果を人間に示して終了する

## 開始 Phase の例

依頼: 「削除済みユーザーを取得したときは、null ではなくエラーを返すように変えたい」

Good:
- 開始 Phase を specification とする。取得の振る舞いが変わるため

Bad:
- 開始 Phase を implementation とする
    - 理由: 承認済みの振る舞いを、人間の判断を経ずに実装で書き換えることになる

## Phase をまたぐ入力

Phase Skill は、`docs/hitd/<feature>/` にある `status: approved` の成果物、ユーザー要求、プロジェクト規約を入力とします。会話に残っている草案と不採用案は、入力として扱いません。

## hitd-check.py による検査

`state.md` を書き換えるたびに、次を実行します。出力が `OK`、終了コードが 0 なら合格です。

```bash
uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>
```

`NG:` の行が出た場合は、その行が示す箇所を直して再実行します。

## 停止条件

正常に終えて呼び出し元へ戻る場合を「終了」、人間の指示を待つ場合を「停止」と書いています。

- `current_phase` が `done` になり、完了を報告した
- 人間が Reject または中止を選んだ
- `hitd-check.py` の同じ `NG:` が3回続けて出た。この場合は、出力を人間に示して指示を待つ
