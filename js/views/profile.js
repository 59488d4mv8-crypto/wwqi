/**
 * views/profile.js - 我的档案 / 数据导出
 */
import { state, exportJSON, importJSON, clearAll, persist, flushAchievements } from '../state.js';
import { levelInfo } from '../state.js';
import { toast, triggerFlush } from '../ui.js';

export function renderProfile() {
    const { level, progress, score } = levelInfo();

    const rows = Object.keys(state.courses || {}).map((cid) => {
        const c = state.courses[cid];
        const p = (c.chapters && Object.values(c.chapters).filter((x) => x.read).length) || 0;
        const ex = Object.values(c.exercises || {}).filter((x) => x.passed).length;
        return `<tr>
            <td>项目 ${cid}</td>
            <td>${p}</td>
            <td>${ex}</td>
            <td>${c.finalScore ?? '-'}</td>
            <td>${c.finalPassed ? '<span style="color:#16a34a;font-weight:600;">已通过</span>' : '<span style="color:#64748b;">进行中</span>'}</td>
            <td><a href="#/courses/${cid}">进入 →</a></td>
        </tr>`;
    }).join('');

    return `
    <section style="margin-bottom:14px;">
        <h1 class="page-title">👤 我的档案</h1>
        <p class="page-subtitle">学习数据保存在你的浏览器本地。你可以导出 JSON 作为备份，并在其他浏览器导入恢复。</p>
    </section>

    <section class="card" style="padding:22px;margin-bottom:18px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="color:#64748b;font-size:0.9rem;">当前等级</div>
                <div style="font-size:2rem;font-weight:700;color:#2563eb;">Lv.${level}</div>
                <div style="color:#64748b;font-size:0.9rem;">积分 ${score} · 徽章 ${(state.badges || []).length}</div>
            </div>
            <div style="min-width:260px;flex:1;">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#475569;">
                    <span>Lv.${level}</span><span>进度 ${progress}%</span>
                </div>
                <div style="background:#e2e8f0;height:12px;border-radius:999px;margin-top:6px;overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#2563eb,#7c3aed);height:100%;width:${progress}%;"></div>
                </div>
            </div>
        </div>
    </section>

    <section class="card" style="padding:22px;margin-bottom:18px;">
        <h3 style="margin:0 0 8px;">📊 各项目学习摘要</h3>
        <div style="overflow:auto;">
            <table style="width:100%;border-collapse:collapse;font-size:0.92rem;">
                <thead><tr style="background:#f8fafc;color:#475569;">
                    <th style="padding:10px;text-align:left;">课程</th>
                    <th style="padding:10px;text-align:left;">已读章节</th>
                    <th style="padding:10px;text-align:left;">练习通过</th>
                    <th style="padding:10px;text-align:left;">综合得分</th>
                    <th style="padding:10px;text-align:left;">状态</th>
                    <th style="padding:10px;text-align:left;"></th>
                </tr></thead>
                <tbody>${rows || '<tr><td colspan="6" style="padding:14px;color:#64748b;">暂无记录，先选一个项目开始吧。</td></tr>'}</tbody>
            </table>
        </div>
    </section>

    <section class="card" style="padding:22px;">
        <h3 style="margin-top:0;">💾 数据备份</h3>
        <p style="color:#475569;">导出的 JSON 包含：等级、积分、徽章、章节进度、练习草稿与得分。</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <button class="btn btn-primary" id="btn-export">下载 JSON 备份</button>
            <label class="btn btn-secondary" for="file-import" style="cursor:pointer;">从 JSON 恢复</label>
            <input type="file" id="file-import" accept="application/json" style="display:none;">
            <button class="btn btn-secondary" id="btn-clear" style="color:#dc2626;border:1px solid #fecaca;">清空本地数据</button>
        </div>
        <div id="profile-feedback" style="margin-top:14px;color:#64748b;font-size:0.92rem;"></div>
    </section>
    `;
}

export function bindProfile() {
    const btnExport = document.getElementById('btn-export');
    if (btnExport) {
        btnExport.addEventListener('click', () => {
            state.everExported = true;
            persist();
            const json = exportJSON(state);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pyedu-backup-${new Date().toISOString().slice(0, 10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            triggerFlush();
            toast({ title: '已备份', body: '学习数据 JSON 已下载到本地。', type: 'success' });
        });
    }
    const fileInput = document.getElementById('file-import');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const f = e.target.files && e.target.files[0];
            if (!f) return;
            if (!confirm('恢复 JSON 会覆盖当前学习数据，确定继续？')) { fileInput.value = ''; return; }
            const reader = new FileReader();
            reader.onload = () => {
                try {
                    const imported = importJSON(String(reader.result));
                    Object.assign(state, imported);
                    persist();
                    triggerFlush();
                    document.getElementById('profile-feedback').innerHTML = '<span style="color:#16a34a;">✅ 已恢复。页面将刷新…</span>';
                    setTimeout(() => location.hash = '#/', 900);
                } catch (err) {
                    document.getElementById('profile-feedback').innerHTML = `<span style="color:#dc2626;">❌ 导入失败：${err.message}</span>`;
                }
            };
            reader.readAsText(f);
        });
    }
    const btnClear = document.getElementById('btn-clear');
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            if (!confirm('此操作会清空所有本地学习数据，确定继续？')) return;
            clearAll();
            toast({ title: '已清空', body: '即将刷新页面…', type: 'warning' });
            setTimeout(() => { location.hash = '#/'; location.reload(); }, 800);
        });
    }
}
