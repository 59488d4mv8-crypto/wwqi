/**
 * views/courses.js - 课程列表
 */
import { loadAllCourses, courseProgress } from '../courses.js';

export async function renderCourses() {
    const courses = await loadAllCourses();
    const cards = courses.map((c) => {
        const p = courseProgress(c.id, c);
        const skills = (c.skills || []).slice(0, 4).map((s) => `<span class="tag" style="font-size:0.78rem;padding:2px 8px;">${s}</span>`).join('');
        return `
        <div class="card" style="cursor:pointer;" onclick="location.hash='#/courses/${c.id}'">
            <div class="card-header">
                <div style="font-weight:600;">项目 ${c.id}：${c.title}</div>
                <span class="card-id" style="color:#64748b;">进度 ${p}%</span>
            </div>
            <div class="card-subtitle">${c.subtitle || ''}</div>
            <div class="card-body" style="color:#334155;font-size:0.92rem;">
                <div style="margin-bottom:8px;"><b>目标：</b>${c.businessGoal || ''}</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">${skills}</div>
            </div>
            <div style="background:#e2e8f0;height:8px;border-radius:999px;overflow:hidden;">
                <div style="background:#2563eb;height:100%;width:${p}%;"></div>
            </div>
            <div style="margin-top:14px;display:flex;justify-content:space-between;align-items:center;">
                <span style="color:#64748b;font-size:0.85rem;">📊 数据集：${c.dataset || 'sample.csv'}</span>
                <a class="btn btn-primary" href="#/courses/${c.id}" style="padding:8px 14px;font-size:0.9rem;">进入 →</a>
            </div>
        </div>`;
    }).join('');

    return `
    <section style="margin-bottom:12px;">
        <h1 class="page-title">📘 10 个 Python 商务数据分析实战项目</h1>
        <p class="page-subtitle">每个项目都包含知识点讲解、可运行代码、互动练习、章节测验与综合测评。</p>
    </section>
    <div class="cards-grid">${cards}</div>`;
}
