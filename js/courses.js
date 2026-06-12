/**
 * courses.js - 课程数据加载与访问
 */
import { state } from './state.js';

let cache = null;

/** 异步拉取课程 JSON（位于 /data/courses/course-<id>.json） */
export async function loadAllCourses() {
    if (cache) return cache;
    const ids = Array.from({ length: 10 }, (_, i) => i + 1);
    const jsons = await Promise.all(
        ids.map((id) => fetch(`./data/courses/course-${id}.json`).then((r) => r.json())),
    );
    cache = jsons;
    return cache;
}

export function getCached() {
    return cache || [];
}

export async function getCourseById(id) {
    const courses = await loadAllCourses();
    return courses.find((c) => String(c.id) === String(id));
}

/** 计算某个课程的总体进度（0-100） */
export function courseProgress(courseId, course) {
    if (!course) return 0;
    const cData = state.courses[courseId] || {};
    const chapterRead = Object.values(cData.chapters || {}).filter((c) => c.read).length;
    const exPassed = Object.values(cData.exercises || {}).filter((e) => e.passed).length;
    const totalChapters = (course.chapters || []).length;
    const totalEx = (course.exercises || []).length;
    const chaptersPart = totalChapters ? (chapterRead / totalChapters) * 50 : 0;
    const exPart = totalEx ? (exPassed / totalEx) * 40 : 0;
    const finalPart = cData.finalPassed ? 10 : 0;
    return Math.round(chaptersPart + exPart + finalPart);
}
