/**
 * achievements.js - 徽章定义与解锁检测
 */
export const BADGES = [
    { id: 'first_run', icon: '▶️', title: '初次运行', desc: '首次成功运行 Python 代码', points: 10 },
    { id: 'course_1', icon: '1️⃣', title: '完成项目 1', desc: '通过项目 1 综合测评', points: 30 },
    { id: 'course_3', icon: '3️⃣', title: '完成项目 3', desc: '通过项目 3 综合测评', points: 30 },
    { id: 'course_5', icon: '5️⃣', title: '完成项目 5', desc: '通过项目 5 综合测评', points: 30 },
    { id: 'course_10', icon: '🔟', title: '完成项目 10', desc: '通过项目 10 综合测评', points: 50 },
    { id: 'streak_3', icon: '🔥', title: '连续学习 3 天', desc: '连续学习打卡 3 天', points: 20 },
    { id: 'streak_7', icon: '💪', title: '连续学习 7 天', desc: '连续学习打卡 7 天', points: 40 },
    { id: 'ex_all_in_1', icon: '✅', title: '项目 1 全练习通关', desc: '项目 1 所有练习自动评分通过', points: 20 },
    { id: 'full_mark_quiz', icon: '💯', title: '满分通过测验', desc: '任一章节测验获得满分', points: 20 },
    { id: 'score_100', icon: '🏅', title: '积分达 100', desc: '累计学习积分达到 100', points: 0 },
    { id: 'score_500', icon: '🥈', title: '积分达 500', desc: '累计学习积分达到 500', points: 0 },
    { id: 'score_1000', icon: '🥇', title: '积分达 1000', desc: '累计学习积分达到 1000', points: 0 },
    { id: 'exporter', icon: '📦', title: '数据导出者', desc: '导出过学习数据', points: 5 },
    { id: 'runs_10', icon: '🔟', title: '代码运行 10 次', desc: '累计运行代码 10 次', points: 10 },
];

export function getBadge(id) {
    return BADGES.find((b) => b.id === id);
}

/** 检测并解锁徽章，返回新解锁的徽章 id 列表 */
export function detectUnlock(state) {
    const newly = [];
    const ensure = (id) => {
        if (!state.badges.includes(id)) {
            state.badges.push(id);
            newly.push(id);
        }
    };
    if (state.firstCodeRunAt) ensure('first_run');
    if ((state.totalRuns || 0) >= 10) ensure('runs_10');

    const courseIds = Object.keys(state.courses);
    const passedCourses = courseIds.filter((cid) => state.courses[cid]?.finalPassed);
    if (passedCourses.includes('1')) ensure('course_1');
    if (passedCourses.includes('3')) ensure('course_3');
    if (passedCourses.includes('5')) ensure('course_5');
    if (passedCourses.includes('10')) ensure('course_10');

    // ex_all_in_1：项目 1 的每个练习都通过
    const c1 = state.courses['1'];
    if (c1 && Object.keys(c1.exercises || {}).length > 0) {
        const allPass = Object.values(c1.exercises).every((e) => e.passed);
        if (allPass) ensure('ex_all_in_1');
    }

    // 满章测验：任一章节 score === 100 或任一 finalScore === 100
    const hasFull = courseIds.some((cid) => {
        const c = state.courses[cid] || {};
        const fullChapter = Object.values(c.chapters || {}).some((ch) => ch.score === 100);
        const fullFinal = c.finalScore === 100;
        return fullChapter || fullFinal;
    });
    if (hasFull) ensure('full_mark_quiz');

    if ((state.streak?.days || 0) >= 3) ensure('streak_3');
    if ((state.streak?.days || 0) >= 7) ensure('streak_7');
    if ((state.score || 0) >= 100) ensure('score_100');
    if ((state.score || 0) >= 500) ensure('score_500');
    if ((state.score || 0) >= 1000) ensure('score_1000');
    if (state.everExported) ensure('exporter');

    return newly;
}
