/**
 * ui.js - 通用 UI 组件：Toast, 进度条, 徽章卡片
 */
import { state, flushAchievements, BADGES } from './state.js';

/**
 * 创建一个 Toast 通知（自动消失）
 */
export function toast({ title, body, type = 'info', timeout = 3200 } = {}) {
    const container = ensureContainer();
    const node = document.createElement('div');
    node.className = `toast ${type}`;
    node.style.cssText = `background:#fff;border:1px solid #e2e8f0;border-left:4px solid ${
        type === 'success' ? '#16a34a' : type === 'danger' ? '#dc2626' : type === 'warning' ? '#d97706' : '#2563eb'
    };border-radius:10px;padding:12px 14px;margin-bottom:8px;box-shadow:0 6px 16px rgba(15,23,42,0.12);font-size:0.92rem;`;
    node.innerHTML = `
        <div style="font-weight:600;margin-bottom:4px;">${title || '提示'}</div>
        <div style="color:#475569;">${body || ''}</div>`;
    container.appendChild(node);
    setTimeout(() => {
        node.style.transition = 'opacity .3s';
        node.style.opacity = '0';
        setTimeout(() => node.remove(), 300);
    }, timeout);
    return node;
}

function ensureContainer() {
    let el = document.getElementById('toast-container');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'toast-container';
    el.style.cssText = 'position:fixed;top:20px;right:20px;z-index:999;width:320px;pointer-events:none;';
    document.body.appendChild(el);
    return el;
}

/** 徽章墙 HTML 块 */
export function renderBadges() {
    const owned = new Set(state.badges || []);
    const items = BADGES.map((b) => {
        const has = owned.has(b.id);
        const title = has ? b.title : '未解锁';
        const desc = has ? b.desc : '继续学习以解锁此徽章';
        return `
        <div class="badge-card" style="opacity:${has ? 1 : 0.45};background:${has ? '#f8fafc' : '#f1f5f9'};border:1px solid #e2e8f0;border-radius:12px;padding:14px;">
          <div style="font-size:1.8rem;text-align:center;">${b.icon}</div>
          <div style="font-weight:600;text-align:center;margin-top:6px;">${b.title}</div>
          <div style="color:#64748b;font-size:0.85rem;text-align:center;margin-top:4px;">${desc}</div>
          ${b.points ? `<div style="text-align:center;margin-top:6px;font-size:0.8rem;color:#2563eb;">+${b.points} 分</div>` : ''}
        </div>`;
    }).join('');
    return `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-top:16px;">${items}</div>`;
}

/** 在任意时刻刷新成就并弹出 toast */
export function notifyNewBadges(newIds) {
    for (const id of newIds) {
        const b = BADGES.find((x) => x.id === id);
        if (!b) continue;
        toast({ title: `🎉 获得徽章：${b.title}`, body: b.desc, type: 'success', timeout: 4200 });
    }
}

/** 供外部调用：手动触发检测并弹窗 */
export function triggerFlush() {
    const newIds = flushAchievements();
    notifyNewBadges(newIds);
    return newIds;
}
