/**
 * app.js - 路由与应用启动
 */
import { renderHome } from './views/home.js';
import { renderCourses } from './views/courses.js';
import { renderCourseDetail, bindCourseDetail } from './views/courseDetail.js';
import { renderAchievements } from './views/achievements.js';
import { renderProfile, bindProfile } from './views/profile.js';
import { loadAllCourses, getCourseById } from './courses.js';
import { triggerFlush } from './ui.js';
import { persist } from './state.js';

const routes = [
    { pattern: '/', handler: () => renderHome() },
    { pattern: '/courses', handler: () => renderCourses() },
    { pattern: '/courses/:id', handler: (params) => renderCourseDetail(params.id) },
    { pattern: '/achievements', handler: () => renderAchievements() },
    { pattern: '/profile', handler: () => renderProfile() },
];

function matchPath(path) {
    for (const r of routes) {
        const pParts = r.pattern.split('/').filter(Boolean);
        const aParts = path.split('/').filter(Boolean);
        if (pParts.length !== aParts.length) continue;
        let ok = true;
        const params = {};
        for (let i = 0; i < pParts.length; i++) {
            if (pParts[i].startsWith(':')) {
                params[pParts[i].slice(1)] = decodeURIComponent(aParts[i]);
            } else if (pParts[i] !== aParts[i]) {
                ok = false; break;
            }
        }
        if (ok) return { route: r, params };
    }
    return null;
}

async function render() {
    const app = document.getElementById('app');
    if (!app) return;
    app.innerHTML = '<div style="padding:40px;color:#64748b;">正在加载…</div>';
    let hash = window.location.hash || '#/';
    let path = hash.replace(/^#/, '');
    if (!path.startsWith('/')) path = '/' + path;

    const match = matchPath(path);
    try {
        if (match) {
            const html = await match.route.handler(match.params);
            app.innerHTML = html;
            // 路由特定绑定
            if (match.route.pattern === '/profile') bindProfile();
            if (match.route.pattern === '/courses/:id') {
                const coursePromise = getCourseById(match.params.id);
                bindCourseDetail(match.params.id, coursePromise);
            }
        } else {
            app.innerHTML = `<section class="not-found">
                <h1>404</h1><p>找不到该页面。</p><a class="btn btn-primary" href="#/">返回首页</a></section>`;
        }
        // 每次路由都刷一下当前日期的连续学习记录 & 成就触发
        persist();
        triggerFlush();
    } catch (err) {
        console.error('[app] 渲染失败', err);
        app.innerHTML = `<section class="not-found"><h1>出错了</h1><p>${String(err.message || err)}</p><a class="btn btn-primary" href="#/">返回首页</a></section>`;
    }
    // 动态更新 meta 信息
    const pageTitle = inferPageTitle(path);
    document.title = pageTitle;
}

function inferPageTitle(path) {
    if (path === '/' || path === '') return 'Python 商务数据分析在线学院';
    if (path === '/courses') return '课程列表 · Python 商务数据分析';
    if (path.startsWith('/courses/')) return '项目详情 · Python 商务数据分析';
    if (path === '/achievements') return '成就与等级 · Python 商务数据分析';
    if (path === '/profile') return '我的档案 · Python 商务数据分析';
    return 'Python 商务数据分析在线学院';
}

// 初始化
window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', async () => {
    // 预先拉取课程 JSON 以便缓存
    try { await loadAllCourses(); } catch (err) { console.warn('[app] 加载课程失败', err); }
    render();
});

// 支持 Pyodide Worker 内的 stdout 事件提示
window.addEventListener('py:log', (e) => {
    const node = document.createElement('div');
    node.style.cssText = 'color:#1e40af;font-size:0.9rem;';
    node.textContent = e.detail.text;
    const app = document.getElementById('app');
    const live = app?.querySelector('[data-py-live-status]');
    if (live) {
        live.textContent = e.detail.text;
    }
});
