"""generate_course_jsons.py - 生成项目 2~10 的 courses JSON"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "data", "courses"))
os.makedirs(OUT, exist_ok=True)


def _ch(i, title, content, code_examples, checks):
    return {"id": f"c{i}", "title": title, "content": content,
            "codeExamples": code_examples, "selfCheckQuestions": checks}


def _q_single(q, opts, ans, explain=""):
    return {"type": "single", "question": q, "options": opts,
            "answer": ans, "explain": explain}


def _q_tf(q, ans, explain=""):
    return {"type": "tf", "question": q, "options": ["正确", "错误"],
            "answer": ans, "explain": explain}


def _q_fill(q, ans, explain=""):
    return {"type": "fill", "question": q, "answer": ans, "explain": explain}


def _q_multi(q, opts, ans, explain=""):
    return {"type": "multi", "question": q, "options": opts,
            "answer": ans, "explain": explain}


def _ex(eid, prompt, starter, hints, sample):
    return {"id": f"e{eid}", "prompt": prompt, "starterCode": starter,
            "expectedChecker": {"type": "output_match", "expectedContains": [""]},
            "hints": hints, "sampleAnswer": sample}


def course2():
    chapters = [
        _ch(1, "数据读取与完成度探索",
            "读取学习进度数据集，统计每章的 start/finish 均值。",
            [{"title": "章节完成度", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-learning-progress.csv')\np = df.groupby('chapter')[['started','finished']].mean()\nprint(p)\nimport matplotlib.pyplot as plt\np.plot(kind='bar', figsize=(9,4))\nplt.title('各章开始/完成率'); plt.tight_layout(); plt.show()"}],
            [_q_single("计算每章完成率的核心聚合方法？", ["mean","count","sum","max"], 0),
             _q_tf("dropna() 可以在聚合前删除缺失行。", 0)]),
        _ch(2, "漏斗：识别流失章节",
            "对每章 finished 汇总，观察漏斗是否递减。",
            [{"title": "漏斗图", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-learning-progress.csv')\nfunnel = df.groupby('chapter')['finished'].sum()\nprint(funnel)\nfunnel.plot(kind='bar', color='#2563eb', figsize=(9,4))\nplt.title('各章完成人数'); plt.tight_layout(); plt.show()"}],
            [_q_single("识别流失节点最直观的可视化是？", ["散点图","饼图","柱状/漏斗","箱线图"], 2)]),
        _ch(3, "用户流失特征与热力图",
            "以 pivot_table 构造用户 × 章节矩阵，并用 heatmap 呈现。",
            [{"title": "热力图", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-learning-progress.csv')\npivot = df.pivot_table(index='user_id', columns='chapter', values='finished')\nprint(pivot.head())\ntry:\n    import seaborn as sns; import matplotlib.pyplot as plt\n    fig, ax = plt.subplots(figsize=(9,5))\n    sns.heatmap(pivot.iloc[:30], cmap='Blues', ax=ax, cbar=False)\n    plt.tight_layout(); plt.show()\nexcept Exception as e:\n    print('seaborn 不可用', e)"}],
            [_q_fill("构造二维矩阵最常用的方法是 pd._____", "pivot_table")]),
    ]
    exercises = [
        _ex(1, "输出每章的完成率，并按升序打印前 3 个“流失最严重”的章节。",
            "import pandas as pd\ndf = pd.read_csv('sample-learning-progress.csv')\n",
            ["groupby('chapter')['finished'].mean()", "sort_values", "head(3)"],
            "res = df.groupby('chapter')['finished'].mean().sort_values()\nprint(res.head(3))"),
        _ex(2, "绘制 started / finished 的分组柱状图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-learning-progress.csv')\n",
            ["groupby(...).agg(...).plot(kind='bar')"],
            "df.groupby('chapter')[['started','finished']].mean().plot(kind='bar', figsize=(9,4))\nplt.legend(['开始','完成']); plt.tight_layout(); plt.show()"),
        _ex(3, "计算每章相对第 1 章的留存率，输出留存率最低的 3 章。",
            "import pandas as pd\ndf = pd.read_csv('sample-learning-progress.csv')\n",
            ["by_ch = df.groupby('chapter')['finished'].sum()", "ret = by_ch / by_ch.iloc[0]"],
            "by_ch = df.groupby('chapter')['finished'].sum()\nret = by_ch / by_ch.iloc[0]\nfor c, v in ret.sort_values().head(3).items():\n    print(c, f'{v:.2%}')"),
    ]
    quizzes = [
        _q_single("漏斗每阶段的分母通常是？", ["总体用户","上一阶段通过用户","付费用户","随机样本"], 1),
        _q_single("找最易流失章节，本质找？", ["完成率最低章节","最早章节","最长标题","最多用户章节"], 0),
        _q_tf("pivot_table 可以把长表转换为宽表。", 0),
        _q_multi("衡量课程完成度的合理指标？", ["章节完成率","退出节点分布","平均进度","姓名长度"], [0,1,2]),
        _q_fill("画柱状图最常用 plt.____", "bar"),
    ]
    final = [
        _q_single("业务目标“找最易流失章节”应关注？", ["开始人数","章节完成率/留存率","标题","价格"], 1),
        _q_tf("某章完成率明显低于其他章节，说明内容或呈现方式可能需要改进。", 0),
        _q_multi("常见的流失可视化？", ["漏斗图","分组柱状图","折线图","热力图"], [0,1,2,3]),
        _q_fill("让当前行和上一行比较用 df.shift(____)", "1"),
        _q_single("df.groupby('chapter')['finished'].mean() 返回？", ["完成人数","完成率","人数","章节数"], 1),
    ]
    return chapters, exercises, quizzes, final


def course3():
    chapters = [
        _ch(1, "RFM 介绍与预处理",
            "R = 距最近学习的天数（越小越好）；F = 学习频次；M = 学习时长/付费金额。",
            [{"title": "读取与描述", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-rfm.csv')\nprint(df.describe())"}],
            [_q_tf("R 越小表示最近越活跃。", 0),
             _q_single("等频分箱用？", ["pd.qcut","pd.sample","df.head","df.tail"], 0)]),
        _ch(2, "分箱与打分",
            "使用 pd.qcut 把 R/F/M 分三档并相加。",
            [{"title": "打分", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-rfm.csv')\ndf['R_score'] = pd.qcut(df['recency_days'], 3, labels=[3,2,1]).astype(int)\ndf['F_score'] = pd.qcut(df['frequency'], 3, labels=[1,2,3]).astype(int)\ndf['M_score'] = pd.qcut(df['monetary_minutes'], 3, labels=[1,2,3]).astype(int)\ndf['RFM_total'] = df['R_score']+df['F_score']+df['M_score']\nprint(df[['user_id','R_score','F_score','M_score','RFM_total']].head())\nprint(df['RFM_total'].value_counts().sort_index())"}],
            [_q_fill("等频分箱用 pd.____", "qcut")]),
        _ch(3, "用户分层与标签",
            "按总分分高价值 / 潜力 / 沉睡用户，并做饼图。",
            [{"title": "分层", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-rfm.csv')\ndf['R_score'] = pd.qcut(df['recency_days'], 3, labels=[3,2,1]).astype(int)\ndf['F_score'] = pd.qcut(df['frequency'], 3, labels=[1,2,3]).astype(int)\ndf['M_score'] = pd.qcut(df['monetary_minutes'], 3, labels=[1,2,3]).astype(int)\ndf['RFM_total'] = df['R_score']+df['F_score']+df['M_score']\ndef seg(t):\n    if t >= 8: return '高价值'\n    if t >= 5: return '潜力'\n    return '沉睡用户'\ndf['segment'] = df['RFM_total'].apply(seg)\ncounts = df['segment'].value_counts(); print(counts)\ncounts.plot(kind='pie', autopct='%.1f%%', figsize=(5,5))\nplt.ylabel(''); plt.title('用户 RFM 价值分层'); plt.tight_layout(); plt.show()"}],
            [_q_single("对数值逐行打标签最常用？", ["apply","cumsum","drop","describe"], 0)]),
    ]
    exercises = [
        _ex(1, "把 recency_days 分 5 档，输出各档人数。",
            "import pandas as pd\ndf = pd.read_csv('sample-rfm.csv')\n",
            ["pd.qcut(df['recency_days'], 5)", "value_counts().sort_index()"],
            "df['r_bin'] = pd.qcut(df['recency_days'], 5)\nprint(df['r_bin'].value_counts().sort_index())"),
        _ex(2, "按 3 档打 RFM 总分并输出高价值用户数。",
            "import pandas as pd\ndf = pd.read_csv('sample-rfm.csv')\n",
            ["R_score/F_score/M_score", "(RFM_total >= 8).sum()"],
            "df['R_score']=pd.qcut(df['recency_days'],3,labels=[3,2,1]).astype(int)\ndf['F_score']=pd.qcut(df['frequency'],3,labels=[1,2,3]).astype(int)\ndf['M_score']=pd.qcut(df['monetary_minutes'],3,labels=[1,2,3]).astype(int)\ndf['RFM_total']=df['R_score']+df['F_score']+df['M_score']\nprint('高价值用户:', (df['RFM_total']>=8).sum())"),
        _ex(3, "绘制各分层的平均付费金额柱状图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-rfm.csv')\n",
            ["先划分 segment", "groupby('segment')['monetary_pay'].mean().plot(kind='bar')"],
            "df['R_score']=pd.qcut(df['recency_days'],3,labels=[3,2,1]).astype(int)\ndf['F_score']=pd.qcut(df['frequency'],3,labels=[1,2,3]).astype(int)\ndf['M_score']=pd.qcut(df['monetary_minutes'],3,labels=[1,2,3]).astype(int)\ndf['RFM_total']=df['R_score']+df['F_score']+df['M_score']\ndf['segment']=df['RFM_total'].apply(lambda t: '高价值' if t>=8 else ('潜力' if t>=5 else '沉睡用户'))\ndf.groupby('segment')['monetary_pay'].mean().plot(kind='bar',color=['#2563eb','#f59e0b','#ef4444'])\nplt.ylabel('平均付费金额'); plt.tight_layout(); plt.show()"),
    ]
    quizzes = [
        _q_single("RFM 的 R 代表？", ["注册日期","最近学习距今天数","推荐人数","地区"], 1),
        _q_tf("qcut 是等距分箱。", 1, "qcut 是等频；cut 是等距。"),
        _q_multi("常见用户分层名称？", ["高价值","潜力","沉睡用户","IP 地址段"], [0,1,2]),
        _q_single("饼图最关注？", ["颜色","各分层占比","字体","图例"], 1),
        _q_fill("对 Series 逐元素做自定义处理用 .____", "apply"),
    ]
    final = [
        _q_single("高价值用户的典型 RFM？", ["R=3/F=1/M=1","均 ≥2 且 F/M 较高","R=1/F=1/M=1","随机"], 1),
        _q_tf("RFM 分层后可以对不同层对比平均付费、平均时长。", 0),
        _q_multi("RFM 分层后可做的运营动作？", ["高价值用户专属权益","沉睡用户召回","潜力用户推荐进阶课程","直接删除低价值账号"], [0,1,2]),
        _q_fill("qcut 的结果类型是 ____", "Categorical"),
        _q_single("F 高但 R 也大的用户应视为？", ["高价值","需召回","沉睡用户","新用户"], 2),
    ]
    return chapters, exercises, quizzes, final


def course4():
    chapters = [
        _ch(1, "读取评论与标签分布",
            "看好评/差评/中性占比并做可视化。",
            [{"title": "分布图", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-reviews.csv')\nprint(df['label'].value_counts())\ndf['label'].value_counts().plot(kind='pie', autopct='%.1f%%')\nplt.ylabel(''); plt.tight_layout(); plt.show()"}],
            [_q_tf("value_counts() 可以看到各标签的样本量。", 0)]),
        _ch(2, "分词与关键词统计",
            "使用 jieba（不可用时按字切分）统计词频。",
            [{"title": "Top 20", "code":
                "import pandas as pd; from collections import Counter\ndf = pd.read_csv('sample-reviews.csv')\ntry:\n    import jieba\n    tok = lambda s: list(jieba.cut(s))\nexcept Exception:\n    tok = lambda s: list(s)\nwords = []\nfor t in df['text']: words.extend(tok(t))\nfor w, n in Counter(words).most_common(20):\n    print(w, n)"}],
            [_q_single("中文分词最常用的第三方库是？", ["jieba","numpy","requests","math"], 0)]),
        _ch(3, "词云与简单情感打分",
            "好差评分别取高频词；尽量加载 wordcloud 做图。",
            [{"title": "词云", "code":
                "import pandas as pd; from collections import Counter\ndf = pd.read_csv('sample-reviews.csv')\ntry:\n    import jieba\n    tok = lambda s: list(jieba.cut(s))\nexcept Exception:\n    tok = lambda s: list(s)\npos = ' '.join(df.loc[df['label']=='好评','text'])\nneg = ' '.join(df.loc[df['label']=='差评','text'])\nprint('【好评 Top 15】', Counter(tok(pos)).most_common(15))\nprint('【差评 Top 15】', Counter(tok(neg)).most_common(15))\ntry:\n    from wordcloud import WordCloud; import matplotlib.pyplot as plt\n    wc = WordCloud(background_color='white', width=700, height=350).generate(pos)\n    plt.figure(figsize=(9,4)); plt.imshow(wc, interpolation='bilinear'); plt.axis('off'); plt.title('好评词云'); plt.tight_layout(); plt.show()\nexcept Exception as e:\n    print('(wordcloud 不可用)', e)"}],
            [_q_fill("快速计数的内置类是 collections.____", "Counter")]),
    ]
    exercises = [
        _ex(1, "输出 1 星评价的 Top 10 词。",
            "import pandas as pd; from collections import Counter\ndf = pd.read_csv('sample-reviews.csv')\n",
            ["筛选 rating==1", "分词后 Counter().most_common(10)"],
            "texts = df.loc[df['rating']==1,'text']\ntry:\n    import jieba\n    tok = lambda s: list(jieba.cut(s))\nexcept Exception:\n    tok = lambda s: list(s)\nflat = [w for t in texts for w in tok(t)]\nprint(Counter(flat).most_common(10))"),
        _ex(2, "绘制不同评分的评论数柱状图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-reviews.csv')\n",
            ["df['rating'].value_counts().sort_index().plot(kind='bar')"],
            "df['rating'].value_counts().sort_index().plot(kind='bar', color='#2563eb')\nplt.xlabel('评分'); plt.ylabel('评论数'); plt.tight_layout(); plt.show()"),
        _ex(3, "基于正负词表打情感分，输出各标签平均分。",
            "import pandas as pd\ndf = pd.read_csv('sample-reviews.csv')\n",
            ["def score(text): pos_count - neg_count", "df.groupby('label')['score'].mean()"],
            "pos = ['清晰','细','丰富','好','推荐','入门','实战']\nneg = ['难','差','bug','太快','不细','错']\ndef score(text):\n    return sum(text.count(w) for w in pos) - sum(text.count(w) for w in neg)\ndf['score'] = df['text'].apply(score)\nprint('整体平均:', df['score'].mean().round(2))\nprint(df.groupby('label')['score'].mean().round(2))"),
    ]
    quizzes = [
        _q_single("中文分词最常用第三方库？", ["jieba","math","csv","os"], 0),
        _q_tf("wordcloud 不可用时，Counter 输出的词频也能给结论。", 0),
        _q_single("Counter.most_common(10) 返回？", ["Top 10 (词, 次数)","前 10 行","前 10 列","字母序 10 项"], 0),
        _q_multi("文本分析常用手段？", ["词频统计","词云","正负词表打分","字符随机替换"], [0,1,2]),
        _q_fill("Series 逐行处理用 .____", "apply"),
    ]
    final = [
        _q_single("自动挖掘课程优缺点最直接看？", ["好评/差评的高频关键词","课程时长","讲师","用户 ID 分布"], 0),
        _q_tf("情感分析结果可以作为唯一改进依据。", 1, "需结合人工抽样等多源证据。"),
        _q_multi("评论数据常用的分析手段？", ["词频","词云","好评/差评对比","随机数"], [0,1,2]),
        _q_fill("字符串序列合并成一个字符串用 ' '.____(list)。", "join"),
        _q_single("取 Top n 词频用？", ["Counter(...).most_common(n)","head(n)","sample(n)","mean()"], 0),
    ]
    return chapters, exercises, quizzes, final


def course5():
    chapters = [
        _ch(1, "相关性矩阵",
            "计算 duration / pauses / forwards vs 分数的相关系数并用热力图展示。",
            [{"title": "corr", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-duration-score.csv')\nprint(df.corr(numeric_only=True).round(2))\ntry:\n    import seaborn as sns; import matplotlib.pyplot as plt\n    fig, ax = plt.subplots(figsize=(6,5))\n    sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax)\n    plt.tight_layout(); plt.show()\nexcept Exception as e:\n    print('seaborn 不可用', e)"}],
            [_q_single("相关系数取值范围是？", ["[0,1]","[-1,1]","[0,100]","任意实数"], 1)]),
        _ch(2, "散点图与线性回归",
            "用 np.polyfit(x, y, 1) 拟合一元线性模型并画图。",
            [{"title": "回归", "code":
                "import pandas as pd; import numpy as np; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-duration-score.csv')\nx = df['duration_min'].values; y = df['quiz_score'].values\nslope, intercept = np.polyfit(x, y, 1)\nyh = slope * x + intercept\nfig, ax = plt.subplots(figsize=(7,5))\nax.scatter(x, y, alpha=.4, s=8); ax.plot(x, yh, 'r', lw=2, label=f'score={slope:.2f}*duration+{intercept:.1f}')\nax.set_xlabel('学习时长'); ax.set_ylabel('测验分数'); ax.legend()\nplt.tight_layout(); plt.show()\nprint('斜率=', round(slope,3), '; 截距=', round(intercept,2))"}],
            [_q_tf("np.polyfit(x, y, 1) 返回 [slope, intercept]。", 0),
             _q_fill("散点图用 plt.____", "scatter")]),
        _ch(3, "箱线图分组对比",
            "用 qcut 把 duration 分三档，比较不同档位分数分布。",
            [{"title": "boxplot", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-duration-score.csv')\ndf['duration_level'] = pd.qcut(df['duration_min'], 3, labels=['短','中','长'])\ndf.boxplot(column='quiz_score', by='duration_level', figsize=(7,5))\nplt.title('学习时长分档 vs 测验分数'); plt.suptitle(''); plt.tight_layout(); plt.show()"}],
            [_q_single("展示分组分布最直观？", ["散点图","箱线图","饼图","纯文本"], 1)]),
    ]
    exercises = [
        _ex(1, "输出 pause_count、forward_count、quiz_score 的相关系数矩阵。",
            "import pandas as pd\ndf = pd.read_csv('sample-duration-score.csv')\n",
            ["df[['pause_count','forward_count','quiz_score']].corr()"],
            "print(df[['pause_count','forward_count','quiz_score']].corr().round(3))"),
        _ex(2, "绘制 duration_min 的直方图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-duration-score.csv')\n",
            ["plt.hist(df['duration_min'], bins=30)"],
            "plt.hist(df['duration_min'], bins=30, edgecolor='black')\nplt.xlabel('学习时长(分钟)'); plt.ylabel('人数'); plt.title('学习时长分布')\nplt.tight_layout(); plt.show()"),
        _ex(3, "以 pause_count 为 x, quiz_score 为 y 做散点+直线并输出斜率。",
            "import pandas as pd; import numpy as np; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-duration-score.csv')\n",
            ["np.polyfit(x, y, 1)", "输出 slope"],
            "x = df['pause_count'].values; y = df['quiz_score'].values\nslope, intercept = np.polyfit(x, y, 1)\nprint('斜率=', round(slope,3), '; 截距=', round(intercept,2))\nplt.scatter(x,y,s=6,alpha=.4); plt.plot(x, slope*x+intercept, 'r')\nplt.xlabel('暂停次数'); plt.ylabel('分数'); plt.tight_layout(); plt.show()"),
    ]
    quizzes = [
        _q_single("相关系数 0 代表？", ["正相关","无线性相关","负相关","完全一致"], 1),
        _q_tf("相关性就是因果性。", 1, "相关性≠因果性。"),
        _q_multi("做相关性分析的常用图？", ["散点图","heatmap","pairplot","饼图"], [0,1,2]),
        _q_single("np.polyfit(x, y, 1) 返回？", ["只有斜率","斜率+截距","R 平方","只有截距"], 1),
        _q_fill("等频分箱用 pd.____", "qcut"),
    ]
    final = [
        _q_single("判断行为对成绩影响最直接看？", ["相关系数与回归斜率","姓名分布","行数","列名"], 0),
        _q_tf("学习时长与分数正相关不代表因果。", 0),
        _q_multi("学习行为分析常用图？", ["散点","箱线","相关性热力图","回归直线"], [0,1,2,3]),
        _q_fill("保留 3 位小数用 .round(____)", "3"),
        _q_single("-0.32 的相关系数代表？", ["越多越好","越多越差","无关系","完全一致"], 1),
    ]
    return chapters, exercises, quizzes, final


def course6():
    chapters = [
        _ch(1, "漏斗数据概览",
            "浏览→试学→加购→付费→完课，观察每阶段人数。",
            [{"title": "表", "code": "import pandas as pd\ndf = pd.read_csv('sample-funnel.csv')\nprint(df)"}],
            [_q_single("漏斗分析强调？", ["各阶段转化率","标题","用户 ID","随机数"], 0)]),
        _ch(2, "单漏斗图",
            "用柱状图展示整体漏斗。",
            [{"title": "漏斗", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-funnel.csv')\ntotal = df[df['channel']=='总计'].copy()\nprint(total)\nfig, ax = plt.subplots(figsize=(8,4))\nax.bar(total['stage'], total['users'], color='#2563eb')\nfor i, u in enumerate(total['users']):\n    ax.text(i, u, str(u), ha='center', va='bottom')\nplt.tight_layout(); plt.show()"}],
            [_q_tf("柱高表示每阶段通过用户数。", 0)]),
        _ch(3, "渠道对比与转化卡点",
            "通过 pivot_table 形成宽表后做渠道 × 阶段归一化柱状图。",
            [{"title": "对比", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-funnel.csv')\npv = df.pivot_table(index='channel', columns='stage', values='users')\nprint(pv)\npv_norm = pv.div(pv['浏览'], axis=0)\npv_norm.T.plot(kind='bar', figsize=(9,5))\nplt.ylabel('相对浏览的转化率'); plt.title('各渠道漏斗转化率'); plt.tight_layout(); plt.show()"}],
            [_q_fill("长表转宽表常用 pd._____", "pivot_table")]),
    ]
    exercises = [
        _ex(1, "输出相对于上一阶段的转化率。",
            "import pandas as pd\ndf = pd.read_csv('sample-funnel.csv')\ntotal = df[df['channel']=='总计'].copy()\n",
            ["pct_change()+1", "首阶段置为 1"],
            "total['conv'] = total['users'].pct_change() + 1\ntotal.loc[total.index[0], 'conv'] = 1.0\ntotal['conv'] = total['conv'].map(lambda v: f'{v:.2%}')\nprint(total[['stage','users','conv']])"),
        _ex(2, "绘制各渠道付费用户数柱状图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-funnel.csv')\n",
            ["筛选 stage=='付费'，再 plot(x='channel', kind='bar')"],
            "paid = df[df['stage']=='付费']\npaid.plot(kind='bar', x='channel', y='users', color='#f97316', figsize=(9,4), legend=False)\nplt.ylabel('付费用户数'); plt.tight_layout(); plt.show()"),
        _ex(3, "找到 “付费→完课” 转化率最低的渠道。",
            "import pandas as pd\ndf = pd.read_csv('sample-funnel.csv')\n",
            ["pivot_table(index='channel', columns='stage', values='users')", "pv['完课']/pv['付费'] 再 sort"],
            "pv = df.pivot_table(index='channel', columns='stage', values='users')\npv['c'] = pv['完课']/pv['付费']\nres = pv['c'].sort_values()\nprint('最低渠道:', res.index[0], f' ({res.iloc[0]:.2%})')"),
    ]
    quizzes = [
        _q_single("转化率通常指？", ["相对上一阶段的比例","绝对用户数","总用户数","随机值"], 0),
        _q_tf("可对不同渠道分别画漏斗以对比。", 0),
        _q_multi("识别转化卡点的方法？", ["每阶段转化率最低者","渠道×阶段最低格","加总所有阶段","只看标题"], [0,1]),
        _q_fill("行的变化率用 Series.____", "pct_change"),
        _q_single("归一化到浏览阶段最直接用？", ["users/users.iloc[0]",".mean()",".cumsum()",".rank()"], 0),
    ]
    final = [
        _q_single("提升付费率应关注？", ["各阶段转化率","标题","城市","随机数"], 0),
        _q_tf("某渠道试学→加购转化率低，可能需改进试学体验。", 0),
        _q_multi("提升付费率的常用手段？", ["优化试学内容","加购按钮/弹窗引导","限时优惠","忽略低转化渠道"], [0,1,2]),
        _q_fill("长表转换宽表用 df.____ 或 pivot_table。", "pivot"),
        _q_single("pct_change() 默认比较？", ["第一行","上一行","下一行","任一行"], 1),
    ]
    return chapters, exercises, quizzes, final


def course7():
    chapters = [
        _ch(1, "课程组合数据",
            "每行形如 '课程1,课程3,课程7'，代表一个用户学习的课程集合。",
            [{"title": "切分", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-course-bundles.csv')\ndf['course_list'] = df['courses'].str.split(',')\nprint(df['course_list'].head())\nall_c = sorted({c for s in df['course_list'] for c in s})\nprint('全部课程:', all_c)"}],
            [_q_single("把逗号字符串切分为列表用？", [".str.split(',')",".replace(',','')",".upper()",".zfill(3)"], 0)]),
        _ch(2, "频繁项集",
            "不依赖 mlxtend，手写简化版 Apriori。support = 共同出现次数 / 总用户数。",
            [{"title": "单项/两项支持度", "code":
                "import pandas as pd; from itertools import combinations; from collections import Counter\ndf = pd.read_csv('sample-course-bundles.csv')\nsets = [set(s.split(',')) for s in df['courses']]\nN = len(sets)\nc1 = Counter()\nfor s in sets:\n    for c in s: c1[frozenset({c})] += 1\nprint('Top 单项:')\nfor item, c in c1.most_common(8):\n    print(list(item), f'{c/N:.2%}')\nc2 = Counter()\nfor s in sets:\n    if len(s) >= 2:\n        for a, b in combinations(sorted(s), 2): c2[frozenset({a, b})] += 1\nprint('\\nTop 两项组合:')\nfor item, c in c2.most_common(8):\n    print(list(item), f'{c/N:.2%}')"}],
            [_q_tf("support 是组合出现的样本比例。", 0),
             _q_fill("生成长度为 2 的无序不重复组合用 itertools.____", "combinations")]),
        _ch(3, "关联规则与推荐",
            "conf(A→B) = support(A,B)/support(A)，据此给出 “学过 A 推荐 B” 的规则。",
            [{"title": "推荐", "code":
                "import pandas as pd; from itertools import combinations; from collections import Counter\ndf = pd.read_csv('sample-course-bundles.csv')\nsets = [set(s.split(',')) for s in df['courses']]\nc1 = Counter(); c2 = Counter()\nfor s in sets:\n    for c in s: c1[frozenset({c})] += 1\n    if len(s) >= 2:\n        for a, b in combinations(sorted(s), 2): c2[frozenset({a, b})] += 1\nrules = []\nfor p, cnt in c2.items():\n    a, b = sorted(p)\n    rules += [(f'{a} -> {b}', cnt / c1[frozenset({a})], cnt/len(sets))]\nrules.sort(key=lambda x: x[1], reverse=True)\nfor r in rules[:10]:\n    print(r[0], f'conf={r[1]:.2%}, supp={r[2]:.2%}')"}],
            [_q_single("高置信度 A→B 说明？", ["学过 A 的人很可能也学 B","A 人数一定多","B 更难","B 更便宜"], 0)]),
    ]
    exercises = [
        _ex(1, "输出被学习次数最多的前 5 门课程。",
            "import pandas as pd; from collections import Counter\ndf = pd.read_csv('sample-course-bundles.csv')\n",
            ["flat = [c for s in df['courses'] for c in s.split(',')]", "Counter(flat).most_common(5)"],
            "flat = [c for s in df['courses'] for c in s.split(',')]\nprint(Counter(flat).most_common(5))"),
        _ex(2, "输出 Top 10 两项组合的支持度。",
            "import pandas as pd; from itertools import combinations; from collections import Counter\ndf = pd.read_csv('sample-course-bundles.csv')\n",
            ["sets = [set(s.split(',')) for s in df['courses']]", "遍历 combinations(sorted(s),2) 并用 Counter 计数"],
            "sets = [set(s.split(',')) for s in df['courses']]\nN = len(sets)\nc = Counter()\nfor s in sets:\n    if len(s) >= 2:\n        for a,b in combinations(sorted(s), 2): c[frozenset({a,b})] += 1\nfor item, n in c.most_common(10):\n    print(list(item), f'{n/N:.2%}')"),
        _ex(3, "给定 TARGET='课程1'，输出最可能一起学习的 Top 3 课程（按置信度）。",
            "import pandas as pd; from collections import Counter; from itertools import combinations\ndf = pd.read_csv('sample-course-bundles.csv')\nTARGET = '课程1'\n",
            ["计算包含 TARGET 的用户数","计算 TARGET 与课程 X 的共现次数","conf = co_x / total_with_target"],
            "sets = [set(s.split(',')) for s in df['courses']]\ntotal = sum(1 for s in sets if TARGET in s)\nco = Counter()\nfor s in sets:\n    if TARGET in s:\n        for c in s:\n            if c != TARGET: co[c] += 1\nres = sorted(co.items(), key=lambda x: x[1]/total, reverse=True)\nfor c, n in res[:3]:\n    print(f'{TARGET} -> {c}: conf={n/total:.2%}')"),
    ]
    quizzes = [
        _q_single("support 衡量？", ["组合出现比例","最贵商品","最低价格","日期差"], 0),
        _q_tf("高置信度 A→B 常用来做“学过 A 推荐 B”。", 0),
        _q_single("combinations(seq, 2) 的含义？", ["生成有序对","长度为 2 的无序不重复组合","笛卡尔积","幂集"], 1),
        _q_multi("衡量关联规则的指标？", ["支持度","置信度","提升度","随机数"], [0,1,2]),
        _q_fill("按逗号切分字符串用 s._____", "split"),
    ]
    final = [
        _q_single("“学过这门课还会学什么”对应？", ["关联规则","聚类","回归","布局"], 0),
        _q_tf("都是热门课的高共现规则推荐价值有限。", 0),
        _q_multi("Apriori 工程化的常见步骤？", ["找频繁项","计算置信/提升","过滤低质量规则","随机推荐"], [0,1,2]),
        _q_fill("枚举无序不重复的组合用 itertools.____", "combinations"),
        _q_single("conf(A→B) 的公式？", ["support(A,B)/support(A)","sum(A) + sum(B)","product","random"], 0),
    ]
    return chapters, exercises, quizzes, final


def course8():
    chapters = [
        _ch(1, "读取并观察趋势",
            "parse_dates 把 date 列解析为 datetime，用双折线分别展示 visits 与 sales。",
            [{"title": "趋势图", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-traffic-sales.csv', parse_dates=['date'])\nprint(df.head())\nfig, ax1 = plt.subplots(figsize=(10,5))\nax1.plot(df['date'], df['visits'], color='#2563eb', label='访问量')\nax1.set_ylabel('访问量', color='#2563eb')\nax2 = ax1.twinx(); ax2.plot(df['date'], df['sales'], color='#f97316', label='销量')\nax2.set_ylabel('销量', color='#f97316')\nplt.title('访问量与销量时间序列'); plt.tight_layout(); plt.show()"}],
            [_q_tf("parse_dates=['date'] 可将日期字符串解析为 datetime。", 0),
             _q_fill("生成第二个 y 轴用 ax.____", "twinx")]),
        _ch(2, "移动平均平滑",
            "rolling(window=7, min_periods=1).mean() 产生 7 日移动平均。",
            [{"title": "MA7", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-traffic-sales.csv', parse_dates=['date'])\ndf['visits_ma7'] = df['visits'].rolling(7, min_periods=1).mean()\nfig, ax = plt.subplots(figsize=(10,5))\nax.plot(df['date'], df['visits'], alpha=.4, label='每日访问量')\nax.plot(df['date'], df['visits_ma7'], lw=2, label='7日 MA')\nax.legend(); plt.tight_layout(); plt.show()"}],
            [_q_single("滑动均值用？", [".rolling(window).mean()",".diff()",".dropna()",".head()"], 0)]),
        _ch(3, "简单短期预测",
            "用最近 7 日均值预测接下来 3 日，给排期做参考。",
            [{"title": "预测", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-traffic-sales.csv', parse_dates=['date'])\nmean7 = df['visits'].tail(7).mean()\nprint('最近7日平均访问量:', round(mean7,1))\nfuture = pd.date_range(df['date'].max() + pd.Timedelta(days=1), periods=3, freq='D')\npred = pd.DataFrame({'date': future, 'visits_pred': mean7})\nprint(pred)"}],
            [_q_single("生成连续日期序列用？", ["pd.date_range","pd.Series","pd.DataFrame","pd.cut"], 0)]),
    ]
    exercises = [
        _ex(1, "输出最近 14 日总销量与日均销量。",
            "import pandas as pd\ndf = pd.read_csv('sample-traffic-sales.csv', parse_dates=['date'])\n",
            ["s = df['sales'].tail(14)", "s.sum()、s.mean()"],
            "s = df['sales'].tail(14)\nprint('最近14日总销量:', s.sum().round(2), '; 日均:', s.mean().round(2))"),
        _ex(2, "绘制销量的 14 日移动平均曲线与原曲线叠加。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-traffic-sales.csv', parse_dates=['date'])\n",
            ["df['sales_ma14'] = df['sales'].rolling(14, min_periods=1).mean()"],
            "df['sales_ma14'] = df['sales'].rolling(14, min_periods=1).mean()\nfig, ax = plt.subplots(figsize=(10,5))\nax.plot(df['date'], df['sales'], alpha=.4, label='日销量')\nax.plot(df['date'], df['sales_ma14'], lw=2, label='14日 MA')\nax.legend(); plt.tight_layout(); plt.show()"),
        _ex(3, "用最近 7 日均值预测接下来 3 日访问量，把最近 21 日实际+预测画在同图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-traffic-sales.csv', parse_dates=['date'])\n",
            ["mean7 = df['visits'].tail(7).mean()", "pd.date_range(end_date, periods=3, freq='D')", "recent = df.tail(21) 与 pred 一起 plot"],
            "mean7 = df['visits'].tail(7).mean()\nfuture = pd.date_range(df['date'].max()+pd.Timedelta(days=1), periods=3, freq='D')\npred = pd.DataFrame({'date': future, 'visits': mean7})\nrecent = df.tail(21)\nfig, ax = plt.subplots(figsize=(10,5))\nax.plot(recent['date'], recent['visits'], 'b-o', label='最近21日')\nax.plot(pred['date'], pred['visits'], 'r--s', label='预测(近7日均)')\nax.legend(); plt.ylabel('访问量'); plt.title('访问量短期预测'); plt.tight_layout(); plt.show()"),
    ]
    quizzes = [
        _q_single("rolling(window=7).mean() 表示？", ["近 7 行求和","近 7 个观察值的均值平滑","乘积","前 7 行均值"], 1),
        _q_tf("以最近均值为未来值是一个实用的简单预测基准。", 0),
        _q_multi("时间序列常用的图？", ["折线图","移动平均叠加","按周/月柱状","饼图按分钟"], [0,1,2]),
        _q_fill("生成日期序列用 pd._____", "date_range"),
        _q_single("min_periods=1 的作用？", ["窗口未满也计算","只打印 1 行","限制 1 行","忽略缺失"], 0),
    ]
    final = [
        _q_single("预测流量高峰应关注？", ["访问量与移动平均趋势","用户 ID","评论","随机列"], 0),
        _q_tf("节假日/大促期间流量常出现尖峰，需单独识别。", 0),
        _q_multi("流量/销量时间序列的分析点？", ["趋势","周期","异常/尖峰","预测"], [0,1,2,3]),
        _q_fill("生成后续 3 天日期用 pd.date_range(start, ____=3, freq='D')", "periods"),
        _q_single("tail(7) 表示？", ["取最后 7 行","取前 7 行","随机 7 行","删除最后 7 行"], 0),
    ]
    return chapters, exercises, quizzes, final


def course9():
    chapters = [
        _ch(1, "教师多维评分概览",
            "每位老师有评分、完课率、互动率、复购率 4 个指标，先总体查看。",
            [{"title": "表", "code": "import pandas as pd\ndf = pd.read_csv('sample-teachers.csv')\nprint(df)"}],
            [_q_single("做综合评价的思路一般是？", ["归一化后加权","取最大值","取最小值","随机"], 0)]),
        _ch(2, "Min-Max 归一化与加权总分",
            "将评分压缩到 [0,1]，与其他百分比指标同一维度，再按权重累加。",
            [{"title": "综合评分", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-teachers.csv')\ndf['rating_norm'] = df['rating_5'] / 5.0\nw = {'rating_norm': 0.4, 'completion_rate': 0.25, 'interaction_rate': 0.15, 'repurchase_rate': 0.2}\ndf['total'] = df['rating_norm']*w['rating_norm'] + df['completion_rate']*w['completion_rate'] + df['interaction_rate']*w['interaction_rate'] + df['repurchase_rate']*w['repurchase_rate']\ndf = df.sort_values('total', ascending=False).reset_index(drop=True)\nprint(df[['teacher','total','rating_norm','completion_rate','interaction_rate','repurchase_rate']].round(3))\nfig, ax = plt.subplots(figsize=(9,5))\nax.bar(df['teacher'], df['total'], color='#2563eb')\nax.set_ylabel('综合得分'); ax.set_title('教师综合评分'); plt.tight_layout(); plt.show()"}],
            [_q_tf("不同量纲先归一化再加权是常见做法。", 0),
             _q_fill("把 5 分制映射到 0-1，用 df['rating_5'] / ____", "5")]),
        _ch(3, "雷达图",
            "Matplotlib 的 polar 轴画雷达图，对比不同老师的多维度表现。",
            [{"title": "雷达", "code":
                "import numpy as np; import matplotlib.pyplot as plt; import pandas as pd\ndf = pd.read_csv('sample-teachers.csv')\ndf['rating_norm'] = df['rating_5']/5\nlabels = ['评分','完课率','互动率','复购率']; N = len(labels)\nangles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()\nfig, ax = plt.subplots(figsize=(6,6), subplot_kw={'polar': True})\nfor _, row in df.iterrows():\n    values = [row['rating_norm'], row['completion_rate'], row['interaction_rate'], row['repurchase_rate']]\n    v = values + values[:1]; a = angles + angles[:1]\n    ax.plot(a, v, 'o-', label=row['teacher']); ax.fill(a, v, alpha=0.1)\nax.set_thetagrids([a*180/np.pi for a in angles], labels)\nax.set_ylim(0, 1); ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1))\nplt.title('教师多维综合评价'); plt.tight_layout(); plt.show()"}],
            [_q_single("雷达图用的坐标系是？", ["极坐标 polar","笛卡尔","对数","地理"], 0)]),
    ]
    exercises = [
        _ex(1, "计算每位教师的综合得分（评分 40% / 完课 25% / 互动 15% / 复购 20%）并排序。",
            "import pandas as pd\ndf = pd.read_csv('sample-teachers.csv')\n",
            ["df['rating_norm']=df['rating_5']/5","加权求和","sort_values"],
            "df['rating_norm'] = df['rating_5']/5\ndf['total'] = 0.4*df['rating_norm'] + 0.25*df['completion_rate'] + 0.2*df['interaction_rate'] + 0.15*df['repurchase_rate']\nout = df.sort_values('total', ascending=False).reset_index(drop=True)\nprint(out[['teacher','total','rating_5','completion_rate','interaction_rate','repurchase_rate']].round(3))"),
        _ex(2, "输出各维度的平均，并用柱状图呈现。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-teachers.csv')\n",
            ["[['rating_5','completion_rate','interaction_rate','repurchase_rate']].mean()",".plot(kind='bar')"],
            "means = df[['rating_5','completion_rate','interaction_rate','repurchase_rate']].mean()\nprint(means.round(3))\nmeans.plot(kind='bar', color=['#2563eb','#f97316','#16a34a','#8b5cf6'])\nplt.ylabel('平均值'); plt.title('各维度平均分'); plt.xticks(rotation=20); plt.tight_layout(); plt.show()"),
        _ex(3, "找出综合得分最高的教师，输出其得分与各维度指标。",
            "import pandas as pd\ndf = pd.read_csv('sample-teachers.csv')\n",
            ["先算 total","再 df.loc[df['total'].idxmax()]"],
            "df['rating_norm'] = df['rating_5']/5\ndf['total'] = 0.4*df['rating_norm'] + 0.25*df['completion_rate'] + 0.2*df['interaction_rate'] + 0.15*df['repurchase_rate']\nbest = df.loc[df['total'].idxmax()]\nprint(best[['teacher','total','rating_5','completion_rate','interaction_rate','repurchase_rate']])"),
    ]
    quizzes = [
        _q_single("多指标综合评分第一步常做？", ["归一化/标准化","求和","取最大值","随机"], 0),
        _q_tf("权重需由业务或经验确定。", 0),
        _q_multi("可视化多维评价的方式？", ["雷达图","平行坐标","加权总分柱状图","表格"], [0,1,2,3]),
        _q_fill("取列中最大值所在行用 df['col'].idx____", "max"),
        _q_single("排序后重置索引用？", ["reset_index(drop=True)","dropna","head","mean"], 0),
    ]
    final = [
        _q_single("综合评价教师教学效果应看？", ["评分、完课率、互动率、复购率等多维度","讲师年龄","讲师手机","随机数"], 0),
        _q_tf("权重分配会显著影响排名，因此要谨慎。", 0),
        _q_multi("综合评分可视化常用形式？", ["雷达","柱状","条形","表格"], [0,1,2,3]),
        _q_fill("把 5 分制缩放到 [0,1] 用 / ____", "5"),
        _q_single("repurchase_rate 的含义？", ["复购率","完课率","点击率","留存率"], 0),
    ]
    return chapters, exercises, quizzes, final


def course10():
    chapters = [
        _ch(1, "用户画像数据概览",
            "浏览年龄、地域、职业、设备、学习时段与付费分布。",
            [{"title": "概览", "code":
                "import pandas as pd\ndf = pd.read_csv('sample-user-profile.csv')\nprint(df.head())\nprint(df.describe(include='all'))"}],
            [_q_single("汇总分类变量最常用？", ["value_counts","diff","rolling","shift"], 0)]),
        _ch(2, "分类分布可视化",
            "对 region/job/device 等分别画图，便于识别高占比人群。",
            [{"title": "分布图", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-user-profile.csv')\ncols = ['region','job','device']\nfig, axes = plt.subplots(1, 3, figsize=(16,5))\nfor ax, c in zip(axes, cols):\n    df[c].value_counts().plot(kind='bar', ax=ax); ax.set_title(c); ax.set_ylabel('人数')\nplt.tight_layout(); plt.show()"}],
            [_q_tf("使用 plt.subplots(1, N) 能方便生成多子图数组。", 0)]),
        _ch(3, "分层策略与精准运营",
            "按年龄（pd.cut 切分）与地域组合，对比各层平均付费金额。",
            [{"title": "分层", "code":
                "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-user-profile.csv')\ndf['age_bin'] = pd.cut(df['age'], bins=[16,25,35,45,60], right=False)\nagg = df.groupby(['region','age_bin'])['pay_amount'].mean().unstack().round(2)\nprint(agg.fillna(0))\nagg.plot(kind='bar', figsize=(10,5))\nplt.ylabel('平均付费金额'); plt.title('地域 × 年龄 分层平均付费'); plt.xticks(rotation=25); plt.tight_layout(); plt.show()"}],
            [_q_single("按区间切分年龄最方便用？", ["pd.cut","pd.qcut","sample","mean"], 0)]),
    ]
    exercises = [
        _ex(1, "输出不同职业的用户数与平均付费金额。",
            "import pandas as pd\ndf = pd.read_csv('sample-user-profile.csv')\n",
            ["df.groupby('job').agg(用户数=('user_id','count'), 平均付费=('pay_amount','mean'))"],
            "out = df.groupby('job').agg(用户数=('user_id','count'), 平均付费=('pay_amount','mean')).round(2)\nprint(out)"),
        _ex(2, "绘制学习时段 prefer_hour 的分布柱状图。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-user-profile.csv')\n",
            ["df['prefer_hour'].value_counts().sort_index().plot(kind='bar')"],
            "df['prefer_hour'].value_counts().sort_index().plot(kind='bar', color='#2563eb', figsize=(9,5))\nplt.xlabel('学习时段(小时)'); plt.ylabel('人数'); plt.title('用户学习时段偏好分布'); plt.tight_layout(); plt.show()"),
        _ex(3, "按 region + device 分组输出平均付费金额，并用分组柱状图呈现。",
            "import pandas as pd; import matplotlib.pyplot as plt\ndf = pd.read_csv('sample-user-profile.csv')\n",
            ["df.groupby(['region','device'])['pay_amount'].mean().unstack()",".plot(kind='bar')"],
            "pv = df.groupby(['region','device'])['pay_amount'].mean().unstack().round(2)\nprint(pv.fillna(0))\npv.plot(kind='bar', figsize=(10,5))\nplt.ylabel('平均付费金额'); plt.title('地域 × 设备 平均付费'); plt.xticks(rotation=25); plt.tight_layout(); plt.show()"),
    ]
    quizzes = [
        _q_single("汇总分类变量最常用？", ["value_counts","diff","shift","sample"], 0),
        _q_tf("可通过 plt.subplots(1, N) 生成多子图并排展示。", 0),
        _q_single("按区间切分年龄最方便？", ["pd.cut","pd.qcut","sample","mean"], 0),
        _q_multi("常用用户画像维度？", ["地域","职业","年龄","设备","学习时段"], [0,1,2,3,4]),
        _q_fill("把长表聚合后转宽表可用 .unstack 或 .______", "pivot_table"),
    ]
    final = [
        _q_single("形成可直接使用的运营方案应关注？", ["各维度的用户数与价值指标（付费/时长）","手机型号","用户 ID","随机数"], 0),
        _q_tf("年龄/地域/职业/设备/时段都是常见的画像分层维度。", 0),
        _q_multi("做用户画像常用的图表？", ["饼图","柱状图","分组柱状图","数据表"], [0,1,2,3]),
        _q_fill("分组聚合用 df.groupby(...).____(...)", "agg"),
        _q_single("pay_amount 代表？", ["付费金额","身高","完课率","评分"], 0),
    ]
    return chapters, exercises, quizzes, final


META = {
    2: {"title": "课程学习完成度与 dropout 流失预测",
        "subtitle": "学习进度、退出节点、完课率、用户流失特征",
        "businessGoal": "找出课程最容易流失的章节",
        "skills": ["数据清洗","特征工程","漏斗图","热力图"],
        "dataset": "sample-learning-progress.csv", "cover": "🎯"},
    3: {"title": "在线教育用户 RFM 价值分层分析",
        "subtitle": "R(最近学习) / F(学习频次) / M(学习时长或付费)",
        "businessGoal": "识别高价值用户、潜力用户与沉睡用户",
        "skills": ["RFM 分箱","用户标签","可视化分组"],
        "dataset": "sample-rfm.csv", "cover": "💎"},
    4: {"title": "课程评价 NLP 情感分析",
        "subtitle": "好评/差评挖掘、分词与词云",
        "businessGoal": "自动挖掘课程优缺点",
        "skills": ["jieba","WordCloud","简单情感打分"],
        "dataset": "sample-reviews.csv", "cover": "💬"},
    5: {"title": "学生学习时长与成绩相关性分析",
        "subtitle": "学习时长、暂停次数、快进次数 vs 章节测验分数",
        "businessGoal": "判断哪些行为影响成绩最大",
        "skills": ["相关性分析","散点图","箱线图","回归分析"],
        "dataset": "sample-duration-score.csv", "cover": "📈"},
    6: {"title": "在线课程付费转化漏斗分析",
        "subtitle": "浏览 → 试学 → 加购 → 付费 → 完课",
        "businessGoal": "找到转化卡点，提升付费率",
        "skills": ["漏斗图","转化率","渠道对比"],
        "dataset": "sample-funnel.csv", "cover": "🛒"},
    7: {"title": "推荐课程关联规则分析（Apriori）",
        "subtitle": "用户学习/购买的课程组合 → 关联规则",
        "businessGoal": "给学生做“学过这门课还会学什么”",
        "skills": ["mlxtend 思路","关联规则可视化"],
        "dataset": "sample-course-bundles.csv", "cover": "🔗"},
    8: {"title": "每日访问量与销量时间序列预测",
        "subtitle": "按日/周流量趋势、节假日波动与短期预测",
        "businessGoal": "预测流量高峰，用于服务器/运营排期",
        "skills": ["时间序列","移动平均","简单预测模型"],
        "dataset": "sample-traffic-sales.csv", "cover": "📅"},
    9: {"title": "教师授课质量多维度综合评分模型",
        "subtitle": "评分、完课率、互动率、复购率 → 综合指标",
        "businessGoal": "客观评价教师教学效果",
        "skills": ["权重计算","标准化","雷达图"],
        "dataset": "sample-teachers.csv", "cover": "🧑‍🏫"},
    10: {"title": "在线教育平台用户画像与精准运营策略",
         "subtitle": "年龄、地域、职业、偏好、设备、学习时段",
         "businessGoal": "输出可直接使用的精准运营方案",
         "skills": ["用户画像聚合","饼图","柱状图","分层策略"],
         "dataset": "sample-user-profile.csv", "cover": "🧑‍🎓"},
}

BUILDERS = {2: course2, 3: course3, 4: course4, 5: course5,
            6: course6, 7: course7, 8: course8, 9: course9, 10: course10}

if __name__ == "__main__":
    for cid, builder in BUILDERS.items():
        chapters, exercises, quizzes, final = builder()
        data = {"id": cid, **META[cid],
                "chapters": chapters, "exercises": exercises,
                "quizzes": quizzes, "finalExam": final}
        path = os.path.join(OUT, f"course-{cid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✔ 生成: {path}")
    print("所有课程 JSON 生成完成。")
