---
name: machine-readability
version: 0.1.0
---

# 機械判読性チェック Skill

## 判断基準

- APIが返した事実、AIが行った判断、人が行った判断を分けて扱う。
- 初期MVPではAI判断を確定せず、レビュー対象として扱う。
- checkerのissueは人が確認できる粒度で保持する。

## 作業手順

1. 対象ファイルの形式を確認する。
2. minerとmachine-readable-checkerの結果を確認する。
3. 事実として得られた結果と推定した判断を分離して記録する。
4. 判断理由と根拠をレビューしやすい形で残す。

## 例外

- APIが失敗した場合もAnalysisResultを返し、失敗内容をsource別に保存する。
- Skillが存在しない場合も解析処理は継続する。
