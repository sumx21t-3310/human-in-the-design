# skills

`human-in-the-design` の Skill 群です。設計の考え方は、リポジトリのルートの [README.md](../README.md) にあります。

| Skill | 役割 |
|---|---|
| `human-in-the-design` | Orchestrator。開始する Phase を決め、Phase Skill を順に起動する |
| `hitd-specification-outline` | Specification Outline Phase |
| `hitd-detailed-specification` | Detailed Specification Phase |
| `hitd-design` | Design Phase |
| `hitd-implementation` | Implementation Phase |
| `hitd-verification` | Verification Phase |

## 導入

各 Skill のフォルダを、エージェントの Skill のフォルダ(Claude Code では `$HOME/.claude/skills/`)へコピーまたはリンクします。検証のスクリプトは `uv` で実行します。

## 成果物の置き場所

Skill は、対象プロジェクトの `docs/hitd/<feature>/` に次のファイルを作ります。

| ファイル | 内容 |
|---|---|
| `state.md` | 現在の Phase と、各 Phase の状態 |
| `outline.md` | Specification Outline |
| `specification.md` | Detailed Specification |
| `design.md` | Design Contract の説明と判断の記録 |
| `contract-snapshot.md` | 承認時点の public と protected の宣言 |
| `adr/` | 設計判断の記録 |
| `verification.md` | Verification Report |
| `change-requests/` | 上位の Phase へ戻すときの変更要求 |

## 保守

`assets/hitd-check.py` は、各 Skill のフォルダだけで手順を再現できるように、6つのフォルダへ同じ内容で置いています。書き換えるときは `human-in-the-design/assets/hitd-check.py` を直し、ほかの5つへコピーします。次のコマンドが何も出力しなければ、内容は一致しています。

```bash
for s in hitd-*; do cmp human-in-the-design/assets/hitd-check.py $s/assets/hitd-check.py; done
```

## 既存の Skill との関係

作成の前に、同じ用途の公開 Skill を探しました。段階ごとに人間の確認を挟む [spec-driven-development](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md) がありますが、Human Decision と Human Approval の分離、Design Stub、Contract Snapshot を持たないため、自作としました。
