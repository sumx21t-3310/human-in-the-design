---
name: hitd-implementation
description: |
  human-in-the-design の Implementation Phase を担当する。承認済みの仕様と Design Contract の範囲で実装とテストを書き、
  Contract Snapshot との一致を確かめる。契約の変更が必要になったら実装を止め、Change Request を出す。
  発火: human-in-the-design スキルからの起動、「HITD の実装フェーズ」「hitd-implementation で」という名指し。
  対象外: 公開 API、型、依存方向の変更(hitd-design へ渡す)。
  対象外: 振る舞いの変更(hitd-detailed-specification へ渡す)。
  対象外: docs/hitd/ に承認済みの成果物がない通常の実装依頼(このスキルを使わずに進める)。
---

# hitd-implementation

このスキルは、承認済みの Design Contract の範囲で、実装コードとテストを書きます。この Phase には、人間による判断と承認の手順がありません。委譲された権限を越える変更が必要になった場合は、実装を止めて上位の Phase へ戻します。

- 入力: `status: approved` の `specification.md` と `design.md`、`contract-snapshot.md`、`adr/`、プロジェクト規約、戻り先が implementation の未処理の Change Request。前の Phase が `skipped` で成果物がない場合は、人間が指定した既存の仕様とコード
- 成果物: 実装コードとテスト
- 委譲されている権限: `contract-snapshot.md` の宣言と、`design.md` の責務、依存方向、状態の所有を変えない範囲の実装とテスト
- 完了で委譲される権限: Verification Phase を始めること

## 前提

- `uv` が使えること
- コマンドは、対象プロジェクトのルートで実行すること
- コマンドの `<skill>` は、このスキルのフォルダのパスに読み替えること
- `<feature>` は、`human-in-the-design` スキルが決めた feature 名に読み替えること

## 手順

1. 開始できることを確かめる。
    - `uv run <skill>/assets/hitd-check.py gate docs/hitd/<feature> implementation` を実行すること
    - 出力が `OK` なら手順2へ進む
    - `state.md` が見つからないという `NG:` の場合は、`human-in-the-design` スキルから始めるよう人間に伝えて停止する
    - そのほかの `NG:` の場合は、出力を人間に示して停止する
2. 入力を読む。
    - `specification.md`、`design.md`、`contract-snapshot.md`、`adr/`、プロジェクト規約を読むこと。`skipped` の Phase の成果物がない場合は、既存の仕様とコードの場所を人間にたずねて読む
    - `adr/` がない場合は、ADR なしとして進むこと
    - `contract-snapshot.md` がない場合は、変えない公開の宣言を人間にたずね、答えを委譲の範囲として扱うこと
    - `docs/hitd/<feature>/change-requests/` に、戻り先が implementation で、末尾に `処理済み` の行がない Change Request がある場合は、読むこと
    - 会話に残っている草案と不採用案は、入力として扱わないこと
    - 読み終えたら手順3へ進む
3. 実装とテストを書く。
    - Design Stub のメソッド本体を実装し、`specification.md` の Acceptance Criteria ごとにテストを書くこと
    - private なメソッドの構成と局所的なアルゴリズムは、人間にたずねずに決めること
    - 次のどれかを変える変更が必要な場合は、その変更を加えずに手順5へ進む。判断の例は「委譲の範囲の例」にある
        - `contract-snapshot.md` の宣言
        - `design.md` の Responsibilities、Dependency Direction、State Ownership に書かれた内容
        - `specification.md` の振る舞い
    - すべての Acceptance Criteria に実装とテストがそろったら、手順4へ進む
4. 検証する。
    - プロジェクトのビルドとテストのコマンドを実行し、成功することを確かめること
    - ビルドのコマンドがないプロジェクトでは、テストのコマンドだけを実行すること
    - `contract-snapshot.md` がある場合は、`uv run <skill>/assets/hitd-check.py snapshot docs/hitd/<feature>/contract-snapshot.md --root .` の出力が `OK` であることを確かめること
    - ビルドまたはテストが失敗した場合は、手順3へ戻る
    - `snapshot` が `NG:` を出した場合は、宣言を Contract Snapshot のとおりに戻して手順3へ戻る。戻すと Acceptance Criteria を満たせない場合は、手順5へ進む
    - すべて成功した場合は、手順6へ進む
5. Change Request を出す。
    - 実装を止めること
    - `docs/hitd/<feature>/change-requests/<4桁の連番>-<題名>.md` に、「Change Request の形」のとおりに書くこと
    - `specification.md` の Acceptance Criteria にない振る舞いが増える、または振る舞いが変わる場合は、Specification Change Request とし、戻り先を specification とする。宣言も変わる場合を含む
    - 振る舞いは変わらず、公開 API、型、依存方向、状態の所有だけを変える場合は、Design Change Request とし、戻り先を design とする
    - 戻り先の Phase を人間に報告し、終了する
6. 完了を記録する。
    - 手順2で読んだ Change Request の末尾に、`処理済み YYYY-MM-DD` の形の1行を足すこと
    - `state.md` の `phases.implementation` を `completed` にすること
    - `uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>` の出力が `OK` なら、実行したコマンドと結果を人間に報告して終了する

## 委譲の範囲の例

Design Contract: `Task<User?> FindAsync(UserId id, CancellationToken cancellationToken = default);`

Good:
- 検索の条件を組み立てる private メソッドを足す
- 取得した行を `User` へ変換する処理を、内部のクラスに分ける

Bad:
- `FindAsync` の戻り値の型を `Task<User?>` から `Task<Result<User>>` に変える
    - 理由: 振る舞いは同じで、Contract Snapshot の宣言だけが変わる。Design Change Request を出す変更に当たる
- 削除済みユーザーを `null` ではなく例外で知らせる
    - 理由: 承認済みの振る舞いが変わる。Specification Change Request を出す変更に当たる
- `FindAsync` に `bool includeDeleted` の引数を足す
    - 理由: 宣言も変わるが、削除済みユーザーを返すという Acceptance Criteria にない振る舞いが増える。Specification Change Request を出す変更に当たる

## Change Request の形

```markdown
# <題名>

- 種別: Design Change Request または Specification Change Request
- 戻り先の Phase: design または specification
- 変更対象: <成果物と見出し、または宣言>
- 必要な変更:
- 変更理由:
- 影響範囲:
- 現在の契約を維持する場合の代替案:
```

## hitd-check.py による検査

出力が `OK`、終了コードが 0 なら合格です。`NG:` の行が出た場合は、その行が示す箇所を直して再実行します。

```bash
uv run <skill>/assets/hitd-check.py snapshot docs/hitd/<feature>/contract-snapshot.md --root .
```

```bash
uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>
```

`snapshot` が検出するのは、書き写した宣言の変更と削除です。宣言の追加を検出する道具がプロジェクトにある場合は、その道具も実行します。

## 停止条件

正常に終えて呼び出し元へ戻る場合を「終了」、人間の指示を待つ場合を「停止」と書いています。

- 手順6の検査が `OK` になった。Verification Phase は始めずに終了する
- 手順5で Change Request を出した
- 手順1の `gate` が `NG:` を出した
- 同じビルドの失敗、同じテストの失敗、または同じ `NG:` が3回続けて出た。この場合は、出力を人間に示して指示を待つ
