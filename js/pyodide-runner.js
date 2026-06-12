/**
 * pyodide-runner.js - 浏览器端 Python 执行（Pyodide + Worker）
 *
 * 使用 Web Worker 加载 Pyodide 并运行代码，主线程不阻塞。
 * 支持写入 CSV 文件到 Pyodide 文件系统，供学生代码中的 pd.read_csv 使用。
 */
import { state, persist, addScore, flushAchievements } from './state.js';

let worker = null;
let callId = 0;
const pending = new Map();
let bootPromise = null;

function ensureWorker() {
    if (worker) return worker;
    const workerCode = `
        const state = { pyodide: null, datasetFiles: [] };
        const CDN = 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/';

        async function loadPyodideAndLibs() {
            if (state.pyodide) return state.pyodide;
            self.postMessage({ type: 'log', text: '🔄 正在加载 Pyodide 环境...' });
            importScripts(CDN + 'pyodide.js');
            const pyodide = await self.loadPyodide({ indexURL: CDN });
            self.postMessage({ type: 'log', text: '✅ Pyodide 加载完成；正在加载常见 Python 库（pandas/matplotlib/numpy）...' });
            await pyodide.loadPackage(['pandas', 'matplotlib', 'numpy']);
            try {
                // matplotlib 中文支持（通过 font_manager 设置）
                pyodide.runPython(\`
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from matplotlib import font_manager
# 默认字体，尽量兼容（无中文字体时用默认 sans-serif）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
\`);
            } catch (e) { /* 忽略 */ }
            state.pyodide = pyodide;
            return pyodide;
        }

        async function writeFile(name, bytes) {
            const pyodide = state.pyodide;
            pyodide.FS.writeFile(name, new Uint8Array(bytes), { canOwn: true });
            state.datasetFiles.push(name);
        }

        async function runCode(code, files) {
            const pyodide = await loadPyodideAndLibs();
            // 写入文件
            for (const f of files || []) {
                try { await pyodide.FS.lookupPath(f.name); } catch(e) {
                    pyodide.FS.writeFile(f.name, new Uint8Array(f.bytes), { canOwn: true });
                }
            }

            // 捕获 stdout/stderr
            let output = '';
            let stdout = (text) => { output += text; self.postMessage({ type: 'stdout', text: String(text) }); };
            let stderr = (text) => { self.postMessage({ type: 'stderr', text: String(text) }); };
            pyodide.setStdout({ batched: (buf) => { stdout(buf); } });
            pyodide.setStderr({ batched: (buf) => { stderr(buf); } });

            // 准备一个可调用的 show()：每次 plt.show() 都把图写回 base64 png
            pyodide.runPython(\`
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import base64, io
def __pyedu_show():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close('all')
    return base64.b64encode(buf.getvalue()).decode('ascii')
plt.show = __pyedu_show
\`);

            let lastVal = null;
            let images = [];
            try {
                // 执行代码；若返回图像数据则记录
                const result = await pyodide.runPythonAsync(code);
                if (result !== undefined && result !== null) {
                    // 可能是字符串（base64）或普通值
                    const tp = String(typeof result);
                    if (tp === 'string' && result.length > 50 && /^[A-Za-z0-9+/=\\s]+$/.test(result)) {
                        images.push(result);
                    } else {
                        stdout(String(result) + '\\n');
                    }
                }
                return { ok: true, images };
            } catch (err) {
                return { ok: false, error: String(err.message || err), images };
            }
        }

        self.onmessage = async (evt) => {
            const { id, action, code, files } = evt.data;
            if (action === 'run') {
                const r = await runCode(code, files || []);
                self.postMessage({ id, done: true, ...r });
            } else if (action === 'boot') {
                await loadPyodideAndLibs();
                self.postMessage({ id, done: true, ok: true });
            }
        };
    `;
    const blob = new Blob([workerCode], { type: 'application/javascript' });
    const url = URL.createObjectURL(blob);
    worker = new Worker(url);
    worker.addEventListener('message', (e) => {
        const data = e.data || {};
        if (data.done && pending.has(data.id)) {
            const cb = pending.get(data.id);
            pending.delete(data.id);
            cb(data);
        } else if (data.type === 'stdout') {
            // 输出到编辑器 UI（通过全局事件）
            window.dispatchEvent(new CustomEvent('py:stdout', { detail: { text: data.text } }));
        } else if (data.type === 'stderr') {
            window.dispatchEvent(new CustomEvent('py:stderr', { detail: { text: data.text } }));
        } else if (data.type === 'log') {
            window.dispatchEvent(new CustomEvent('py:log', { detail: { text: data.text } }));
        }
    });
    worker.addEventListener('error', (e) => {
        window.dispatchEvent(new CustomEvent('py:error', { detail: { text: e.message } }));
    });
    return worker;
}

/** 确保 Pyodide 已加载；返回 Promise<void>，会更新状态 firstCodeRunAt */
export async function boot() {
    if (bootPromise) return bootPromise;
    const w = ensureWorker();
    return (bootPromise = new Promise((resolve, reject) => {
        const id = 'boot-' + (++callId);
        pending.set(id, (data) => (data.ok ? resolve() : reject(new Error('boot failed'))));
        w.postMessage({ id, action: 'boot' });
    }));
}

/** 在 Worker 中运行代码，返回 { ok, error, images, elapsed } */
export async function runInWorker(code, files) {
    const w = ensureWorker();
    const id = 'run-' + (++callId);
    // 超时保护
    const timeoutMs = 15000;
    let resolved = false;
    return new Promise((resolve) => {
        const timeout = setTimeout(() => {
            if (resolved) return;
            resolved = true;
            pending.delete(id);
            resolve({ ok: false, error: `⏰ 执行超时（${timeoutMs / 1000}s），请检查死循环或复杂计算。`, images: [] });
        }, timeoutMs);
        const started = Date.now();
        pending.set(id, (data) => {
            if (resolved) return;
            resolved = true;
            clearTimeout(timeout);
            // 更新全局状态：第一次运行
            if (!state.firstCodeRunAt) state.firstCodeRunAt = new Date().toISOString();
            state.totalRuns = (state.totalRuns || 0) + 1;
            addScore(state, 1, 'run-code');
            persist();
            flushAchievements();
            resolve({ ok: data.ok, error: data.error || '', images: data.images || [], elapsed: Date.now() - started });
        });
        w.postMessage({ id, action: 'run', code, files: files || [] });
    });
}

/** 工具：把一个 URL 下载成 { name, bytes } 供 Worker 写入 */
export async function fetchDatasetFile(name, url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`无法下载 ${url}`);
    const ab = await resp.arrayBuffer();
    return { name, bytes: new Uint8Array(ab) };
}
