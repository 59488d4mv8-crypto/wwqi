/**
 * views/achievements.js - 成就/徽章页
 */
import { state, levelInfo, flushAchievements } from '../state.js';
import { BADGES } from '../achievements.js';

export function renderAchievements() {
    const owned = new Set(state.badges || []);
    const { level, progress, score, nextMin } = levelInfo();

    const cards = BADGES.map((b) => {
        const has = owned.has(b.id);
        return `
        <div class="card" style="padding:16px;opacity:${has ? 1 : 0.55};background:${has ? '#fff' : '#f8fafc'};">
            <div style="font-size:1.8rem;text-align:center;">${b.icon}</div>
            <div style="font-weight:600;text-align:center;margin-top:6px;">${b.title}</div>
            <div style="color:#64748b;font-size:0.85rem;text-align:center;margin-top:4px;min-height:36px;">${b.desc}</div>
            <div style="text-align:center;margin-top:8px;color:${has ? '#16a34a' : '#94a3b8'};font-size:0.85rem;font-weight:600;">${has ? '✅ 已解锁' : '🔒 未解锁'}</div>
        </div>`;
    }).join('');

    return `
    <section style="margin-bottom:14px;">
        <h1 class="page-title">🏆 成就与等级</h1>
        <p class="page-subtitle">完成课程、练习、持续学习来解锁徽章、提升等级。</p>
    </section>

    <section class="card" style="padding:22px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="font-size:1rem;color:#64748b;">当前等级</div>
                <div style="font-size:2.2rem;font-weight:700;color:#2563eb;">Lv.${level}</div>
                <div style="color:#64748b;font-size:0.9rem;">总积分：${score}</div>
            </div>
            <div style="min-width:260px;flex:1;">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#475569;">
                    <span>Lv.${level}</span><span>距 Lv.${Math.min(20, level + 1)}：${nextMin - score} 分</span>
                </div>
                <div style="background:#e2e8f0;height:12px;border-radius:999px;margin-top:6px;overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#2563eb,#7c3aed);height:100%;width:${progress}%;"></div>
                </div>
                <div style="color:#64748b;font-size:0.85rem;margin-top:6px;">进度 ${progress}%</div>
            </div>
        </div>
        <div style="margin-top:14px;color:#475569;font-size:0.9rem;">
            已获得徽章：<b>${owned.size}</b> / ${BADGES.length}，完成项目：<b>${
                Object.values(state.courses).filter((c) => c.finalPassed).length
            }</b>，连续学习：<b>${state.streak?.days || 1}</b> 天。
        </div>
    </section>

    <section>
        <h2 style="margin:0 0 8px;">🎖 徽章墙</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;">${cards}</div>
    </section>`;
}
