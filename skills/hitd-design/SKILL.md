---
name: hitd-design
description: |
  human-in-the-design の Design Phase を担当する。承認済みの specification.md をもとに、責務分割、公開 API、データ契約を
  人間と相談し、Design Stub と design.md にまとめ、人間の判断と承認を得て Design Contract として確定する。
  承認のあとで Contract Snapshot と ADR を作る。
  発火: human-in-the-design スキルからの起動、「HITD の設計フェーズ」「hitd-design で」という名指し、Design Change Request の処理。
  対象外: 振る舞いの決定(hitd-detailed-specification へ渡す)。
  対象外: メソッド本体の実装(hitd-implementation へ渡す)。
  対象外: Phase を名指ししない開発依頼(human-in-the-design へ渡す)。
---

# hitd-design

このスキルは、Design Stub(設計スタブ)と契約のドキュメントコメントを作り、人間の承認を得て Design Contract として確定するところまでを担当します。メソッド本体の実装は、Implementation Phase が扱います。

- 入力: `status: approved` の `docs/hitd/<feature>/specification.md`、プロジェクト規約、戻り先が design の未処理の Change Request。specification が `skipped` で `specification.md` がない場合は、人間が指定した既存の仕様
- 成果物: Design Stub(対象プロジェクトのソースコード)、`design.md`、`contract-snapshot.md`、`adr/`
- 承認で委譲する権限: Design Contract の範囲で実装とテストを書くこと

## 前提

- `uv` が使えること
- コマンドは、対象プロジェクトのルートで実行すること
- コマンドの `<skill>` は、このスキルのフォルダのパスに読み替えること
- `<feature>` は、`human-in-the-design` スキルが決めた feature 名に読み替えること

## 手順

1. 開始できることを確かめる。
    - `uv run <skill>/assets/hitd-check.py gate docs/hitd/<feature> design` を実行すること
    - 出力が `OK` なら手順2へ進む
    - `state.md` が見つからないという `NG:` の場合は、`human-in-the-design` スキルから始めるよう人間に伝えて停止する
    - そのほかの `NG:` の場合は、出力を人間に示して停止する
2. 入力を読む。
    - `specification.md`、プロジェクト規約を読むこと。specification が `skipped` で `specification.md` がない場合は、既存の仕様の場所を人間にたずねて読む
    - `docs/hitd/<feature>/change-requests/` に、戻り先が design で、末尾に `処理済み` の行がない Change Request がある場合は、読むこと
    - 会話に残っている草案と不採用案は、入力として扱わないこと
    - 読み終えたら手順3へ進む
3. Talk(相談)をする。
    - 次の5つを、人間と順に話すこと
        - 責務の分け方
        - 公開する API と型(DTO、Value Object、interface)
        - 依存方向
        - 状態の所有とライフサイクル
        - 代替案
    - 振る舞いを変える必要が出た場合は、手順10へ進む
    - 手順7の Revise、または Change Request で戻ってきた場合は、修正の要求または Change Request に関わる項目だけを話して、手順4へ進む
    - 5つすべてについて人間の考えを聞き終えたら、手順4へ進む
4. Artifact(成果物)を書く。
    - 対象プロジェクトのソースコードに、Design Stub として型、公開 API のシグネチャ、ドキュメントコメントを書くこと
    - メソッド本体は、その言語で未実装を表す記述だけにすること。C# では `throw new NotImplementedException()`、Python では `raise NotImplementedError` と書く
    - 実装済みのメソッド本体がある場合は、本体を残し、宣言とドキュメントコメントだけを変えること
    - ドキュメントコメントには、責務、引数と戻り値の意味、`null` の意味、例外、副作用、状態遷移、所有権を書くこと。該当しない項目は書かない
    - ドキュメントコメントを書けない項目がある場合は、仕様または設計が決まっていないので、手順3へ戻る
    - 「成果物の形」のとおりに `design.md` を `status: draft` で書くこと
    - `design.md` がすでにある場合は、内容を書き換え、`status` を `draft` に戻すこと
    - プロジェクトにビルドのコマンドがある場合は実行し、Design Stub がコンパイルできることを確かめること
    - `uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/design.md` の出力が `OK` なら手順5へ進む
5. Decision Check(判断確認)を作る。
    - 後から変えるコストが高い判断(公開 API、データ契約、依存方向、状態の所有)のうち、採用できる案が2つ以上ある項目だけを対象にすること
    - 案ごとに Context、Benefits、Costs / Risks、Consequences を同じ細かさで書き、Recommendation を別に示すこと
    - private なメソッドの構成と局所的なアルゴリズムは、対象にしないこと
    - Talk で人間がすでに案を選んだ項目は、対象から除き、選んだ内容を手順6の書式で `Decisions` に書くこと
    - 対象の項目がない場合は、手順7へ進む。`Decisions` に1件も書かれていないときは、「判断を要する項目なし」と書く
    - 対象の項目がある場合は、手順6へ進む
6. Human Decision(人間による判断)を受ける。
    - Decision Check を1項目ずつ人間に示し、採用する案をたずねること。選択肢を示す UI がある環境では、その UI を使う
    - 人間は、示した案のほかの案も出せる。その場合は、その案を採用案として扱う
    - `Decisions` に、判断ごとに `### <判断の題名>` の見出しを置き、採用案、判断理由、受け入れた Trade-off、LLM の Recommendation を箇条書きで書くこと
    - Design Stub と `design.md` を採用案に合わせること
    - すべての項目に採用案が決まったら、手順7へ進む
7. Human Approval(人間による承認)を受ける。
    - Design Stub のファイルの一覧、`Decisions` の要約、`Authority Delegation` の文を人間に示し、Approve、Revise、Reject のどれかをたずねること
    - Approve の場合は、手順8へ進む
    - Revise の場合は、修正の要求を聞き、手順3へ戻る
    - Reject の場合は、成果物を `status: draft` のまま残し、停止する
8. Contract Snapshot と ADR を作る。
    - 「Contract Snapshot の形」のとおりに、Design Stub の public と protected の宣言を `contract-snapshot.md` へ書き写すこと
    - `contract-snapshot.md` がすでにある場合は、変わった宣言の行だけを書き換えること
    - 書き写す対象は、型の宣言の行、メソッドと関数のシグネチャの行、公開するフィールドとプロパティの行とすること。可視性の修飾子がない言語では、モジュールの外から使う宣言を対象とする
    - `uv run <skill>/assets/hitd-check.py snapshot docs/hitd/<feature>/contract-snapshot.md --root .` を実行し、出力が `OK` になるまで `contract-snapshot.md` を直すこと
    - 宣言の追加を検出するツール(API の一覧を比較する解析器など)がプロジェクトにある場合は、承認した宣言を基準として設定すること
    - `Decisions` のうち、公開 API、データ契約、依存方向、状態の所有を決めた判断について、`adr/<4桁の連番>-<題名>.md`(例: `adr/0001-return-null-when-missing.md`)を「ADR の形」のとおりに書くこと
    - すでにある ADR の判断を変えた場合は、新しい連番で ADR を足し、古い ADR の `Status` を `superseded` に書き換えること
    - 手順2で読んだ Change Request の末尾に、`処理済み YYYY-MM-DD` の形の1行を足すこと
    - 終えたら手順9へ進む
9. 成果物を確定する。
    - `design.md` の `status` を `approved` に、`approved_at` を承認の日付(`YYYY-MM-DD`)にすること
    - `state.md` の `phases.design` を `completed` にすること
    - `artifact` と `state` の検査が両方 `OK` なら、終了する
10. Specification Change Request を出す。
    - `docs/hitd/<feature>/change-requests/<4桁の連番>-<題名>.md` に、「Change Request の形」のとおりに書くこと
    - 戻り先の Phase を specification として人間に報告し、終了する

## 成果物の形

```markdown
---
phase: design
status: draft
approved_at:
---

# <feature> Design

## Responsibilities
## Design Stub

<Design Stub のファイルのパスを、プロジェクトのルートからの相対パスで並べる>

## Dependency Direction
## State Ownership
## Decisions
## Authority Delegation

Implementation Phase で、Contract Snapshot の宣言を変えない範囲の実装とテストを書くことを許可する。
```

## Design Stub の例

Good:

```csharp
/// <summary>
/// 指定されたユーザーIDに対応する有効なユーザーを取得します。
/// </summary>
/// <returns>
/// ユーザーが存在しない場合は <c>null</c> を返します。
/// </returns>
Task<User?> FindAsync(UserId id, CancellationToken cancellationToken = default);
```

Bad:

```csharp
public async Task<User?> FindAsync(UserId id, CancellationToken cancellationToken = default)
{
    var row = await _db.Users.Where(u => u.Id == id.Value && !u.IsDeleted).FirstOrDefaultAsync(cancellationToken);
    return row is null ? null : new User(new UserId(row.Id), row.Name);
}
```

- 理由: メソッド本体を実装しており、`null` の意味を示すドキュメントコメントがない

## Contract Snapshot の形

見出しは、プロジェクトのルートからのファイルの相対パスです。コードブロックには、宣言を1行に1つずつ書きます。検査は、空白を除いた宣言の文字列がファイルにあることを確かめます。

````markdown
# Contract Snapshot

## src/Accounts/IUserFinder.cs

```text
public interface IUserFinder
Task<User?> FindAsync(UserId id, CancellationToken cancellationToken = default);
```
````

この検査が検出するのは、書き写した宣言の変更と削除です。

## ADR の形

```markdown
# <連番>. <題名>

- Status: accepted
- Date: <承認の日付>

## Context
## Alternatives
## Trade-offs
## Recommendation
## Human Decision
## Rationale
## Consequences
```

## Change Request の形

```markdown
# <題名>

- 種別: Specification Change Request
- 戻り先の Phase: specification
- 変更対象: <成果物と見出し>
- 必要な変更:
- 変更理由:
- 影響範囲:
- 現在の契約を維持する場合の代替案:
```

## hitd-check.py による検査

出力が `OK`、終了コードが 0 なら合格です。`NG:` の行が出た場合は、その行が示す箇所を直して再実行します。

```bash
uv run <skill>/assets/hitd-check.py artifact docs/hitd/<feature>/design.md
```

```bash
uv run <skill>/assets/hitd-check.py snapshot docs/hitd/<feature>/contract-snapshot.md --root .
```

```bash
uv run <skill>/assets/hitd-check.py state docs/hitd/<feature>
```

## 停止条件

正常に終えて呼び出し元へ戻る場合を「終了」、人間の指示を待つ場合を「停止」と書いています。

- 手順9の検査が両方 `OK` になった。実装は始めずに終了する
- 手順10で Change Request を出した
- 手順1の `gate` が `NG:` を出した
- 人間が Reject を選んだ
- 同じ `NG:` が3回続けて出た。この場合は、出力を人間に示して指示を待つ
