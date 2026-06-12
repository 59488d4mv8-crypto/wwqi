/**
 * state.js - 全局状态单例（学习数据+UI状态）
 */
import { loadState, saveState, addScore, touchStreak, awardBadge, getCourse, computeLevel, exportJSON, importJSON, clearAll } from './storage.js';
import { detectUnlock, BADGES } from './achievements.js';

export const state = loadState();
// 初始化学习 streak
touchStreak(state);

/** 持久化到 localStorage */
export function persist() {
    saveState(state);
}

/** 计算当前等级/进度 */
export function levelInfo() {
    const level = computeLevel(state.score);
    const nextLevel = Math.min(20, level + 1);
    const currentMin = level * level * 10;
    const nextMin = nextLevel * nextLevel * 10;
    const need = nextMin - currentMin;
    const progress = need === 0 ? 100 : Math.min(100, Math.round(((state.score - currentMin) / need) * 100));
    return { level, progress, score: state.score, nextMin };
}

/** 触发解锁徽章检测，并返回新徽章；同时持久化 */
export function flushAchievements() {
    touchStreak(state);
    const newly = detectUnlock(state);
    if (newly.length) persist();
    return newly;
}

export { addScore, awardBadge, getCourse, persist, exportJSON, importJSON, clearAll, BADGES };
