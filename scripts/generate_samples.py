"""
generate_samples.py - 生成 10 个项目所需的示例 CSV 数据
在本地执行:  python3 scripts/generate_samples.py
将在 data/samples/ 下生成 sample-*.csv 若干文件
所有数据均为虚构，用于教学目的
"""
import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "data", "samples"))
os.makedirs(OUT, exist_ok=True)

N_USERS = 800
CHANNELS = ["自然流量", "搜索引擎", "社交网络", "付费广告", "合作推广"]


def _rand_dates(start: datetime, end: datetime, n: int) -> list:
    span = int((end - start).total_seconds())
    offsets = sorted(random.randrange(span) for _ in range(n))
    return [start + timedelta(seconds=o) for o in offsets]


def project_1_users():
    start = datetime(2025, 11, 1)
    end = datetime(2026, 6, 10)
    dates = _rand_dates(start, end, N_USERS)

    df = pd.DataFrame({
        "user_id": [f"U{i:05d}" for i in range(1, N_USERS + 1)],
        "channel": np.random.choice(CHANNELS, N_USERS, p=[0.25, 0.22, 0.2, 0.2, 0.13]),
        "registered_at": dates,
        "active_days": np.random.randint(1, 30, N_USERS),
        "retain_day1": np.random.choice([0, 1], N_USERS, p=[0.35, 0.65]),
        "retain_day7": np.random.choice([0, 1], N_USERS, p=[0.55, 0.45]),
        "retain_day14": np.random.choice([0, 1], N_USERS, p=[0.7, 0.3]),
    })
    # 让不同渠道的质量略有差异
    ch_map = {"自然流量": 0.4, "搜索引擎": 0.55, "社交网络": 0.35, "付费广告": 0.5, "合作推广": 0.7}
    df["retain_day7"] = df.apply(
        lambda r: 1 if random.random() < ch_map[r["channel"]] else 0, axis=1
    )
    df.to_csv(os.path.join(OUT, "sample-users.csv"), index=False)
    print("✔ 项目 1:", "sample-users.csv", len(df), "行")


def project_2_learning():
    chapters = [f"第{i}章" for i in range(1, 11)]
    rows = []
    for u in range(1, N_USERS + 1):
        start_ch = np.random.randint(1, 5)
        dropout = np.random.choice(chapters)
        for c in chapters:
            rows.append({
                "user_id": f"U{u:05d}",
                "chapter": c,
                "started": 1 if chapters.index(c) + 1 >= start_ch else 0,
                "finished": 1 if c < dropout else 0,
                "progress_pct": min(100, random.randint(0, 100) if c == dropout else (100 if c < dropout else 0)),
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "sample-learning-progress.csv"), index=False)
    print("✔ 项目 2:", "sample-learning-progress.csv", len(df), "行")


def project_3_rfm():
    now = datetime(2026, 6, 10)
    data = []
    for i in range(1, N_USERS + 1):
        days_ago = random.randint(0, 180)
        freq = random.randint(1, 40)
        duration = round(random.uniform(5, 180), 1)  # 学习分钟
        pay = round(random.uniform(0, 500), 2) if random.random() < 0.4 else 0
        data.append({
            "user_id": f"U{i:05d}",
            "last_learn_date": (now - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "recency_days": days_ago,
            "frequency": freq,
            "monetary_minutes": duration,
            "monetary_pay": pay,
        })
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(OUT, "sample-rfm.csv"), index=False)
    print("✔ 项目 3:", "sample-rfm.csv", len(df), "行")


def project_4_reviews():
    good = ["课程内容很清晰", "老师讲得很细", "练习题丰富", "Python 入门好课", "代码可直接跑", "有收获", "案例贴近实战", "推荐给朋友"]
    bad = ["节奏太快", "练习题太难", "讲解不细致", "代码有 bug", "视频质量一般", "进度条不准", "字幕有错"]
    neutral = ["还可以", "一般般", "内容中等", "学完有基础"]
    rows = []
    for i in range(1, 1501):
        label = np.random.choice(["好评", "差评", "中性"], p=[0.55, 0.2, 0.25])
        pool = good if label == "好评" else (bad if label == "差评" else neutral)
        text = random.choice(pool) + "，" + random.choice(pool) + "。"
        rows.append({
            "review_id": f"R{i:05d}",
            "course_id": random.randint(1, 10),
            "rating": {"好评": 5, "中性": 3, "差评": 1}[label],
            "text": text,
            "label": label,
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "sample-reviews.csv"), index=False)
    print("✔ 项目 4:", "sample-reviews.csv", len(df), "行")


def project_5_duration_vs_score():
    n = 600
    duration = np.random.normal(60, 20, n).clip(10, 150)  # 分钟
    pauses = np.random.randint(0, 30, n)
    forwards = np.random.randint(0, 20, n)
    noise = np.random.normal(0, 8, n)
    score = (duration * 0.35 - pauses * 0.4 - forwards * 0.3 + 45 + noise).clip(0, 100)
    df = pd.DataFrame({
        "student_id": [f"S{i:05d}" for i in range(1, n + 1)],
        "duration_min": np.round(duration, 1),
        "pause_count": pauses,
        "forward_count": forwards,
        "quiz_score": np.round(score, 1),
    })
    df.to_csv(os.path.join(OUT, "sample-duration-score.csv"), index=False)
    print("✔ 项目 5:", "sample-duration-score.csv", len(df), "行")


def project_6_funnel():
    stages = ["浏览", "试学", "加购", "付费", "完课"]
    rates = [1.0, 0.45, 0.2, 0.12, 0.06]
    base_users = 20000
    rows = []
    for ch in CHANNELS + ["总计"]:
        factor = 1.0 if ch == "总计" else random.uniform(0.7, 1.3)
        for stage, rate in zip(stages, rates):
            rows.append({
                "channel": ch,
                "stage": stage,
                "users": int(base_users * factor * rate),
                "rate_to_next": round(rate / (rates[stages.index(stage) - 1]) if stages.index(stage) > 0 else 1.0, 3),
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "sample-funnel.csv"), index=False)
    print("✔ 项目 6:", "sample-funnel.csv", len(df), "行")


def project_7_apriori():
    courses = [f"课程{i}" for i in range(1, 9)]
    rows = []
    for u in range(1, 1200):
        n = random.randint(1, 4)
        picks = random.sample(courses, n)
        rows.append({"user_id": f"U{u:05d}", "courses": ",".join(picks)})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "sample-course-bundles.csv"), index=False)
    print("✔ 项目 7:", "sample-course-bundles.csv", len(df), "行")


def project_8_timeseries():
    dates = pd.date_range("2026-01-01", "2026-06-10", freq="D")
    n = len(dates)
    base = 800 + np.sin(np.arange(n) / 7) * 120 + np.random.randint(-80, 80, n)
    sales = base * np.random.uniform(0.05, 0.18, n)
    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "visits": base.astype(int),
        "sales": np.round(sales, 2),
    })
    df.to_csv(os.path.join(OUT, "sample-traffic-sales.csv"), index=False)
    print("✔ 项目 8:", "sample-traffic-sales.csv", len(df), "行")


def project_9_teacher_rating():
    teachers = [f"老师-{c}" for c in "ABCDEFGH"]
    rows = []
    for t in teachers:
        rating = round(random.uniform(3.8, 4.9), 2)
        completion = round(random.uniform(0.5, 0.95), 3)
        interaction = round(random.uniform(0.5, 0.95), 3)
        repeat = round(random.uniform(0.1, 0.7), 3)
        rows.append({
            "teacher": t,
            "rating_5": rating,
            "completion_rate": completion,
            "interaction_rate": interaction,
            "repurchase_rate": repeat,
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "sample-teachers.csv"), index=False)
    print("✔ 项目 9:", "sample-teachers.csv", len(df), "行")


def project_10_user_profile():
    regions = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
    jobs = ["学生", "在职-数据", "在职-产品", "在职-运营", "自由职业", "其他"]
    devs = ["iPhone", "Android", "Windows 桌面", "Mac 桌面"]
    rows = []
    for i in range(1, N_USERS + 1):
        rows.append({
            "user_id": f"U{i:05d}",
            "age": np.random.randint(18, 55),
            "region": random.choice(regions),
            "job": random.choice(jobs),
            "device": random.choice(devs),
            "prefer_hour": np.random.choice(list(range(6, 24))),
            "pay_amount": round(random.uniform(0, 800), 2),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "sample-user-profile.csv"), index=False)
    print("✔ 项目 10:", "sample-user-profile.csv", len(df), "行")


if __name__ == "__main__":
    project_1_users()
    project_2_learning()
    project_3_rfm()
    project_4_reviews()
    project_5_duration_vs_score()
    project_6_funnel()
    project_7_apriori()
    project_8_timeseries()
    project_9_teacher_rating()
    project_10_user_profile()
    print("\n全部示例数据集已生成在:", OUT)
