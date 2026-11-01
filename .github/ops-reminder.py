#!/usr/bin/env python3
"""週次の運用チェック用 Issue の本文を組み立てる。

このスクリプトは通知するだけで、index.html は一切書き換えない。
掲載内容の追加・修正は、必ず人が公式発表を確認してから行うこと（OPERATIONS.md 3節）。

期限やフェーズ別タスクを増やすときは、下の DEADLINES / PHASES を編集する。
"""
import datetime
import pathlib

JST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(JST).date()

# 掲載中の窓口の受付期限。期限の14日前から通知が出る。
# 【重要】カードを整理し終えた窓口は、この一覧からも必ず削除すること。
# 残したままだと「〇日経過」の通知が永久に出続け、本当に未対応のものが埋もれる。
# 総務省 熊本行政評価事務所「生活支援窓口案内（熊本県版ガイドブック）」。市町村ごとの期限の出典。
GUIDE = "https://www.soumu.go.jp/main_content/001084949.pdf"

DEADLINES = [
    # --- 11月 ---
    ("公費解体（上天草市・芦北町）申請、氷川町の申請予約", "2026-11-30", GUIDE),
    ("り災証明書（菊陽町）申請", "2026-11-30", GUIDE),
    ("日本弁護士連合会の電話相談", "2026-11-30", GUIDE),
    # --- 12月 ---
    ("公費解体（熊本市）書類受付", "2026-12-10",
     "https://www.city.kumamoto.jp/kiji00372403/index.html"),
    ("持続化補助金 災害支援枠（2次）", "2026-12-15",
     "https://www.kmt-cci.or.jp/news/reiwa8kumamotojisin2jikoubokouboyouryoukoukai/"),
    ("公費解体（大津町）申請", "2026-12-18", GUIDE),
    ("公費解体（美里町）申請", "2026-12-21", GUIDE),
    ("公費解体（氷川町）申請", "2026-12-25", GUIDE),
    ("日本カーシェアリング協会 災害サポート・レンタカー", "2026-12-25",
     "https://www.japan-csa.org/blog/archives/13936"),
    ("公費解体（宇土市・水俣市・合志市・西原村）申請", "2026-12-28", GUIDE),
    # --- 2027年 ---
    ("住宅の応急修理 完了（宇土市・上天草市・合志市・嘉島町・益城町・氷川町）", "2027-01-27", GUIDE),
    ("り災証明書（水俣市、発災から6か月）", "2027-01-28", GUIDE),
    ("公費解体（宇城市）申請", "2027-01-29",
     "https://www.city.uki.kumamoto.jp/toppage/important/2622644"),
    ("公費解体（八代市）申請", "2027-03-31",
     "https://www.city.yatsushiro.lg.jp/kiji00327083/index.html"),
    # 熊本県・日赤の義援金は 2026-10-05 ごろ、10/30 から 2027/3/31 へ延長された。
    ("熊本県 義援金", "2027-03-31",
     "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
    ("日本赤十字社 義援金", "2027-03-31",
     "https://www.jrc.or.jp/contribute/help/20260731/"),
]

# フェーズが進んだら検討する掲載内容。対象日を過ぎると通知に出続ける。
PHASES = [
    # 「ボランティアの案内を募集案内へ切り替える」は 2026-08-11 に対応済み（Issue #15）。
    # 以後の募集状況の変化は WEEKLY の定点確認で追う。
    # 「不要な物資の注意を具体化」は 2026-08-31 に対応済み。
    # 熊本県が専用フォームによる事前申請制をとっている旨を注意ボックスに明記した。
    # 「発災直後の措置（00000JAPAN・災害用伝言板・通行実績マップ）の整理」は 2026-09-28 に対応済み（Issue #48）。
    # 「義援金の配分状況を追記する」は 2026-10-19 に対応済み（Issue #53）。
    # 第1次配分（9/28 決定）の基準額を被災者向けに、配分の規模を寄付した人向けに掲載した。
    ("2026-12-07", "義援金の第2次配分を確認する",
     "熊本県の配分委員会で第2次配分が決まっていれば、義援金セクションの案内文と"
     "「義援金の受け取り」カードを更新する。",
     "https://www.pref.kumamoto.jp/soshiki/27/281576.html"),
    # 「公費解体の締切が未掲載の町」「持続化補助金の2次公募」は 2026-11-01 に対応済み。
    # 総務省のガイドブックをもとに、21市町村の期限一覧（index.html の #kigen）を作った。
    ("2026-11-16", "市町村ごとの期限の一覧を、ガイドブックの最新版と照合する",
     "総務省のガイドブックは随時更新される。版が上がっていれば、り災証明書・応急修理・"
     "公費解体の期限を照合し、一覧の見出しの時点（〇月〇日時点）も更新する。"
     "期限を過ぎたものは「終了」に書き換える。",
     GUIDE),
    ("2026-11-16", "熊本市の応急修理の期限延長が確定したか確認する",
     "10月時点では 2027/1/27 まで延長する方向で国と協議済み、さらに延長を協議予定とされていた。"
     "確定していれば一覧の熊本市の欄を更新する。",
     "https://www.city.kumamoto.jp/kiji00372104/index.html"),
    ("2027-10-13", "アクセシビリティの再試験（年1回）",
     "accessibility.html の達成基準チェックリストに沿って全38項目を確認し直し、試験日を更新する（OPERATIONS.md 9節）。",
     "https://kumamoto-shien.net/accessibility.html"),
    ("2027-04-05", "義援金の受付終了後の導線を整理する",
     "熊本県・日赤の義援金が 2027/3/31 で終了した場合、カードを受付終了に切り替え、"
     "サイトの重心を被災者向けの制度案内へ寄せる。寄付セクションの残りを 点検し、"
     "受付中の窓口だけが残っている状態にする。",
     "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
]

# 毎週必ず確認する主要窓口
WEEKLY = [
    ("熊本県 義援金", "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
    ("熊本県 令和8年熊本地震に関する情報", "https://www.pref.kumamoto.jp/soshiki/1/274517.html"),
    ("熊本県 災害ボランティア情報", "https://www.fukushi-kumamoto.or.jp/kvc/"),
    ("経済産業省 中小企業支援措置", "https://www.meti.go.jp/press/20260729003.html"),
    ("国交省 通れるマップ", "https://www.mlit.go.jp/road/saigai/r8kumamoto/index.html"),
    ("熊本県 住まいの支援制度", "https://www.pref.kumamoto.jp/soshiki/117/277826.html"),
    # 2026-08-26 開設の新しいサイト。毎週火曜の更新が続いているかを確認する
    ("神田研究室 渋滞状況（毎週火曜更新）", "https://www.ykandalab.net/d-trip/2026-kumamoto/"),
    # 自動リンクチェックでは毎回タイムアウトする（GitHub の実行環境からは応答が遅い）ため、
    # link-check.yml の対象から外し、ここで人が確認する。
    ("さとふる 災害緊急支援寄付", "https://www.satofull.jp/oenkifu/oenkifu_detail.php?page_id=542"),
    # 2026-10 から自動チェックで 503 が続く（実行環境からの接続を拒否しているとみられる）ため同様に除外。
    ("ふるさとチョイス 災害支援", "https://www.furusato-tax.jp/saigai/"),
    # 市町村ごとの期限一覧の出典。版（表紙の第〇版）が上がっていないかを見る。
    ("総務省 生活支援窓口案内（熊本県版ガイドブック）", GUIDE),
]

# 期限の何日前から通知を出すか
DEADLINE_NOTICE_DAYS = 14


def main() -> None:
    monday = TODAY - datetime.timedelta(days=TODAY.weekday())
    title = f"運用チェック（{monday:%Y-%m-%d} の週）"

    out = [f"OPERATIONS.md 4節の定期見直しです。確認して、対応が済んだらこの Issue を閉じてください。",
           "",
           "**このIssueは通知だけで、サイトは自動更新されません。**"
           "掲載の追加・修正は公式発表を確認してから手で行ってください。",
           ""]

    # 期限が近い / 過ぎた窓口
    urgent = []
    for name, date_s, url in DEADLINES:
        d = datetime.date.fromisoformat(date_s)
        left = (d - TODAY).days
        if left < 0:
            urgent.append(f"- [ ] **{name}** — {date_s} で受付終了済み（{-left}日経過）。"
                          f"カードを削除するか「受付終了」と明記してリンクを外す。<{url}>")
        elif left <= DEADLINE_NOTICE_DAYS:
            urgent.append(f"- [ ] **{name}** — 残り{left}日（{date_s}）。"
                          f"延長の有無を確認する。<{url}>")
    if urgent:
        out += ["## 受付期限が近い・過ぎた窓口", ""] + urgent + [""]

    # フェーズ別に検討するもの
    phase = [f"- [ ] **{t}**\n  {desc}\n  <{url}>"
             for date_s, t, desc, url in PHASES
             if datetime.date.fromisoformat(date_s) <= TODAY]
    if phase:
        out += ["## 掲載内容の見直し（フェーズ）", ""] + phase + [""]

    # 毎週の定点確認
    out += ["## 主要窓口の定点確認", "",
            "受付期間の延長・終了、支援措置の追加が無いか各公式ページを見る。", ""]
    out += [f"- [ ] [{name}]({url})" for name, url in WEEKLY]
    out += [""]

    # 第1月曜は全体通読
    if monday.day <= 7:
        out += ["## 今月の全体通読（第1月曜）", "",
                "- [ ] サイトを通読し、いまのフェーズに合わない情報",
                "（発災直後の緊急情報など）が残っていないか確認して入れ替える。", ""]

    pathlib.Path("reminder-title.txt").write_text(title + "\n", encoding="utf-8")
    pathlib.Path("reminder-body.md").write_text("\n".join(out), encoding="utf-8")
    print(title)


if __name__ == "__main__":
    main()
