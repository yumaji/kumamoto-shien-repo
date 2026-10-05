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
DEADLINES = [
    ("住宅の応急修理 完了", "2026-10-27",
     "https://www.pref.kumamoto.jp/soshiki/27/275109.html"),
    ("公費解体（熊本市）書類受付", "2026-12-10",
     "https://www.city.kumamoto.jp/kiji00372403/index.html"),
    ("小規模事業者持続化補助金 災害支援枠（1次）", "2026-10-16",
     "https://www.chusho.meti.go.jp/koukai/hojyokin/kobo/2026/260909001.html"),
    ("日本カーシェアリング協会 災害サポート・レンタカー", "2026-12-25",
     "https://www.japan-csa.org/blog/archives/13936"),
    ("済生会熊本病院（READYFOR）", "2026-10-28",
     "https://readyfor.jp/projects/saiseikai-kumamoto"),
    ("熊本県 義援金", "2026-10-30",
     "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
    ("日本赤十字社 義援金", "2026-10-30",
     "https://www.jrc.or.jp/contribute/help/20260731/"),
]

# フェーズが進んだら検討する掲載内容。対象日を過ぎると通知に出続ける。
PHASES = [
    # 「ボランティアの案内を募集案内へ切り替える」は 2026-08-11 に対応済み（Issue #15）。
    # 以後の募集状況の変化は WEEKLY の定点確認で追う。
    # 「不要な物資の注意を具体化」は 2026-08-31 に対応済み。
    # 熊本県が専用フォームによる事前申請制をとっている旨を注意ボックスに明記した。
    # 「発災直後の措置（00000JAPAN・災害用伝言板・通行実績マップ）の整理」は 2026-09-28 に対応済み（Issue #48）。
    # 2026-09-29 に確認したが、配分委員会による配分決定は未公表だったため対象日を延期。
    ("2026-10-19", "義援金の配分状況を追記する",
     "県の配分委員会の開催後、配分内容を確認して掲載する。寄付した人が結果を追えるようにする。",
     "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
    ("2026-11-02", "義援金の受付終了後の導線を整理する",
     "熊本県・日赤の義援金が 10/30 で終了した場合、カードを受付終了に切り替え、"
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
