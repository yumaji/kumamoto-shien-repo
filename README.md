# 令和8年熊本地震 支援情報まとめ

2026年7月28日発生の令和8年熊本地震について、寄付・ボランティアの窓口と、被災者・被災事業者・復旧工事に入る会社向けの公式情報を整理した非公式まとめサイトです。

- サイト本体: `index.html`（1ファイル構成）
- 運用ルール: [`OPERATIONS.md`](./OPERATIONS.md)
- 自動化: `.github/workflows/`（更新日時の自動書き換え・毎朝のリンクチェック）

## 公開手順（初回のみ・5分）

1. GitHubで新しいリポジトリを作成（例: `kumamoto-shien-matome`、Public）
2. このフォルダの中身をpush:
   ```bash
   cd kumamoto-shien
   git init && git add . && git commit -m "初回公開"
   git branch -M main
   git remote add origin https://github.com/<あなたのユーザー名>/kumamoto-shien-matome.git
   git push -u origin main
   ```
3. リポジトリの **Settings → Pages** で
   Source: `Deploy from a branch` / Branch: `main` / フォルダ: `/ (root)` を選択して保存
4. **Settings → Actions → General → Workflow permissions** で
   `Read repository contents` を選択して保存（必要な書き込み権限は各ワークフロー内で個別に指定）
5. 数分後、`https://<あなたのユーザー名>.github.io/kumamoto-shien-matome/` で公開されます

## ふだんの更新

`index.html` を編集して push するだけ。最終更新日はActionsが自動で書き換えます。
リンク切れは毎朝自動チェックされ、見つかるとIssueが立ちます。対応手順は `OPERATIONS.md` を参照。
