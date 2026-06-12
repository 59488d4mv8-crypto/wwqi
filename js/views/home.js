/**
 * views/home.js - 首页（Hero + 仪表盘）
 */
import { state, levelInfo } from '../state.js';
import { loadAllCourses, courseProgress } from '../courses.js';
import { BADGES } from '../achievements.js';

export async function renderHome() {
    const courses = await loadAllCourses();
    const { level, progress, score } = levelInfo();

    const totalPassed = Object.values(state.courses).filter((c) => c.finalPassed).length;
    const totalExercises = Object.values(state.courses).reduce(
        (acc, c) => acc + Object.values(c.exercises || {}).filter((e) => e.passed).length,
        0,
    );
    const totalChapters = Object.values(state.courses).reduce(
        (acc, c) => acc + Object.values(c.chapters || {}).filter((ch) => ch.read).length,
        0,
    );

    const recent = courses.slice(0, 4).map((c) => {
        const p = courseProgress(c.id, c);
        return `
            <div style="flex:1 1 240px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;">
                <div style="font-size:1.4rem;margin-bottom:6px;">${c.cover || '📘'}</div>
                <div style="font-weight:600;">项目 ${c.id}：${c.title}</div>
                <div style="color:#64748b;font-size:0.9rem;margin:6px 0 10px;">${c.subtitle || ''}</div>
                <div style="background:#e2e8f0;height:8px;border-radius:999px;overflow:hidden;">
                    <div style="background:#2563eb;height:100%;width:${p}%;"></div>
                </div>
                <div style="color:#64748b;font-size:0.82rem;margin-top:6px;">进度 ${p}%</div>
                <a href="#/courses/${c.id}" style="display:inline-block;margin-top:12px;text-decoration:none;background:#2563eb;color:#fff;padding:8px 14px;border-radius:8px;font-size:0.9rem;">继续学习 →</a>
            </div>`;
    }).join('');

    return `
    <section class="hero">
        <h1>🐍 Python 商务数据分析实战学院</h1>
        <p>10 个真实场景项目，从注册行为分析到用户画像。学习、练习、测评一体化；浏览器内直接跑 Python 代码。</p>
        <div style="margin-top:14px;">
            <a class="btn btn-primary" href="#/courses">浏览课程 →</a>
            <a class="btn btn-secondary" href="#/achievements" style="margin-left:8px;">查看成就</a>
        </div>
        <div class="hero-stats" style="margin-top:28px;">
            <div class="hero-stat"><div class="label">当前等级</div><div class="value">Lv.${level}</div></div>
            <div class="hero-stat"><div class="label">积分</div><div class="value">${score}</div></div>
            <div class="hero-stat"><div class="label">已完成项目</div><div class="value">${totalPassed}</div></div>
            <div class="hero-stat"><div class="label">已获得徽章</div><div class="value">${(state.badges || []).length} / ${BADGES.length}</div></div>
        </div>
        <div style="margin-top:12px;max-width:480px;">
            <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#f1f5f9;">
                <span>Lv.${level}</span><span>距 Lv.${Math.min(20, level + 1)} ${Math.max(0, (level + 1) * (level + 1) * 10 - score)} 分</span>
            </div>
            <div style="background:rgba(255,255,255,0.25);height:10px;border-radius:999px;margin-top:4px;overflow:hidden;">
                <div style="background:#fbbf24;height:100%;width:${progress}%;transition:width .3s;"></div>
            </div>
        </div>
    </section>

    <section style="margin-top:28px;">
        <h2 style="margin:0 0 8px;">📚 最近/热门项目</h2>
        <p style="color:#64748b;margin:0 0 14px;">共 ${courses.length} 个项目。阅读章节 ${totalChapters} 次，通过练习 ${totalExercises} 个。</p>
        <div style="display:flex;gap:14px;flex-wrap:wrap;">${recent}</div>
    </section>

    <section style="margin-top:28px;">
        <h2 style="margin:0 0 8px;">🧭 如何学习</h2>
        <ol style="color:#334155;line-height:1.8;">
            <li>从课程列表选择一个项目，阅读知识点章节。</li>
            <li>每个章节都有可运行的 Python 代码示例（点击 ▶ 运行）。</li>
            <li>进入“互动练习”写代码并提交（系统会自动评分）。</li>
            <li>完成“综合测评”解锁项目徽章，等级提升。</li>
            <li>学习进度保存在浏览器本地，可随时导出备份。</li>
        </ol>
    </section>`;
}
