/**
 * storage.js - 本地持久化（localStorage）
 */
const KEY = 'pyedu_state_v1';

export function loadState() {
    try {
        const raw = localStorage.getItem(KEY);
        if (!raw) return defaultState();
        const parsed = JSON.parse(raw);
        return { ...defaultState(), ...parsed };
    } catch (err) {
        console.warn('[storage] 读取失败', err);
        return defaultState();
    }
}

export function saveState(state) {
    state.updatedAt = new Date().toISOString();
    try {
        localStorage.setItem(KEY, JSON.stringify(state));
    } catch (err) {
        console.error('[storage] 写入失败', err);
    }
}

function defaultState() {
    return {
        version: 1,
        score: 0,
        totalRuns: 0,
        firstCodeRunAt: null,
        courses: {},     // courseId -> { completed, finalPassed, finalScore, chapters: { chapId: { read, quizPassed, score } }, exercises: { exId: { passed, tries } }, codeDraft: '' }
        badges: [],      // badgeIds
        streak: { days: 0, lastDate: null },
        profile: { nickname: '学员' + Math.floor(Math.random() * 9000 + 1000) },
        updatedAt: new Date().toISOString(),
    };
}

export function getCourse(state, courseId) {
    if (!state.courses[courseId]) {
        state.courses[courseId] = {
            completed: false,
            finalPassed: false,
            finalScore: null,
            finalTries: 0,
            chapters: {},
            exercises: {},
            codeDraft: '',
            firstVisitedAt: new Date().toISOString(),
        };
    }
    return state.courses[courseId];
}

export function addScore(state, delta, reason) {
    state.score = Math.max(0, (state.score || 0) + delta);
    if (reason) console.debug(`[storage] +${delta} 分 (${reason})`);
}

/** 基于积分计算等级：level = floor(sqrt(score / 10))，封顶 20 */
export function computeLevel(score) {
    return Math.min(20, Math.floor(Math.sqrt(Math.max(0, score || 0) / 10)));
}

/** 根据当前日期计算连续学习天数 */
export function touchStreak(state) {
    const today = toDateKey(new Date());
    if (state.streak.lastDate === today) return state.streak.days;
    if (!state.streak.lastDate) {
        state.streak.days = 1;
        state.streak.lastDate = today;
        return state.streak.days;
    }
    const diff = dayDiff(state.streak.lastDate, today);
    if (diff === 1) {
        state.streak.days = (state.streak.days || 0) + 1;
    } else {
        state.streak.days = 1;
    }
    state.streak.lastDate = today;
    return state.streak.days;
}

function toDateKey(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

function dayDiff(a, b) {
    const da = new Date(a); const db = new Date(b);
    return Math.round((db - da) / (24 * 3600 * 1000));
}

/** 导出 JSON 字符串（供下载） */
export function exportJSON(state) {
    return JSON.stringify(state, null, 2);
}

/** 导入 JSON（覆盖） */
export function importJSON(text) {
    const parsed = JSON.parse(text);
    if (typeof parsed !== 'object' || parsed === null) {
        throw new Error('数据格式不正确');
    }
    return { ...defaultState(), ...parsed };
}

/** 清空本地数据 */
export function clearAll() {
    localStorage.removeItem(KEY);
}

/** 添加徽章，若新徽章则返回 true */
export function awardBadge(state, badgeId) {
    if (!state.badges) state.badges = [];
    if (!state.badges.includes(badgeId)) {
        state.badges.push(badgeId);
        return true;
    }
    return false;
}

export { KEY as STORAGE_KEY };
