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
DEADLINES = [
    ("楽天クラッチ募金", "2026-08-28",
     "https://corp.rakuten.co.jp/donation/kumamoto_2026_ja/kumamoto_2026_ja.html"),
    ("CAMPFIRE 緊急災害支援金", "2026-09-25",
     "https://camp-fire.jp/projects/971234/view"),
    ("済生会熊本病院（READYFOR）", "2026-10-28",
     "https://readyfor.jp/projects/saiseikai-kumamoto"),
    ("熊本県 義援金", "2026-10-30",
     "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
]

# フェーズが進んだら検討する掲載内容。対象日を過ぎると通知に出続ける。
PHASES = [
    ("2026-08-04", "ボランティアの案内を「抑制」から「募集案内」へ切り替える",
     "災害VCが本格募集を開始したら、「支援を始める前に」の文面を書き換える。"
     "人手が必要な時期に人を止めてしまわないため、これは遅れるほど害になる。"
     "あわせてボランティア保険の事前加入案内の追加を検討する。",
     "https://www.fukushi-kumamoto.or.jp/kvc/"),
    ("2026-08-18", "不要な物資（千羽鶴・古着など）の注意を具体化する",
     "注意ボックスの物資の項目を、実際に問題化している品目まで踏み込んで書けるか検討する。"
     "自治体が受け入れ不可を公表している場合のみ具体名を出すこと。",
     "https://www.pref.kumamoto.jp/soshiki/1/274517.html"),
    ("2026-09-29", "義援金の配分状況を追記する",
     "県の配分委員会の開催後、配分内容を確認して掲載する。寄付した人が結果を追えるようにする。",
     "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
]

# 毎週必ず確認する主要窓口
WEEKLY = [
    ("熊本県 義援金", "https://www.pref.kumamoto.jp/soshiki/27/274572.html"),
    ("熊本県 令和8年熊本地震に関する情報", "https://www.pref.kumamoto.jp/soshiki/1/274517.html"),
    ("熊本県 災害ボランティア情報", "https://www.fukushi-kumamoto.or.jp/kvc/"),
    ("経済産業省 中小企業支援措置", "https://www.meti.go.jp/press/20260729003.html"),
    ("国交省 通れるマップ", "https://www.mlit.go.jp/road/saigai/r8kumamoto/index.html"),
]

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
