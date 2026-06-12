/**
 * editor.js - 代码编辑器区域 + 控制台 + 图像渲染
 *
 * 提供 renderEditor(opts)，返回 { el, getCode, setCode, reset }
 * opts: { initial: string, title, mode: 'run' | 'exercise', checkExpected?: (code, result)=>{passed, message}, datasetFiles: [{ name, url }] }
 */
import { boot, runInWorker, fetchDatasetFile } from './pyodide-runner.js';
import { toast } from './ui.js';

export function renderEditor({ initial, title, mode = 'run', checkExpected, datasetFiles }) {
    const container = document.createElement('div');
    container.className = 'code-runner';
    container.innerHTML = `
      <div class="code-runner-header">
        <div style="font-weight:600;">${title || '🐍 Python 代码'}</div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-secondary" data-action="reset" style="padding:6px 12px;font-size:0.85rem;">重置</button>
          <button class="btn btn-primary" data-action="run" style="padding:6px 14px;font-size:0.85rem;">▶ 运行</button>
          ${mode === 'exercise' ? '<button class="btn btn-accent" data-action="submit" style="padding:6px 14px;font-size:0.85rem;">📝 提交答案</button>' : ''}
        </div>
      </div>
      <div class="code-runner-editor">
        <textarea class="editor-textarea" spellcheck="false" style="width:100%;min-height:200px;padding:12px;border:0;background:#0b1220;color:#f1f5f9;font-family:Menlo,Consolas,'Courier New',monospace;font-size:0.9rem;line-height:1.55;resize:vertical;outline:none;"></textarea>
      </div>
      <div class="code-runner-output" data-output style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:12px 16px;min-height:80px;max-height:420px;overflow:auto;font-family:Menlo,Consolas,'Courier New',monospace;font-size:0.88rem;color:#334155;white-space:pre-wrap;"></div>
      <div data-images style="display:flex;flex-wrap:wrap;gap:12px;padding:8px 12px;background:#fff;"></div>
    `;
    const textarea = container.querySelector('.editor-textarea');
    const output = container.querySelector('[data-output]');
    const images = container.querySelector('[data-images]');
    textarea.value = initial || '';

    // Tab 键插入 4 空格
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const s = textarea.selectionStart;
            const end = textarea.selectionEnd;
            textarea.value = textarea.value.slice(0, s) + '    ' + textarea.value.slice(end);
            textarea.selectionStart = textarea.selectionEnd = s + 4;
        }
    });

    function appendOut(text, cls) {
        const span = document.createElement('span');
        span.textContent = text;
        if (cls) span.style.color = cls;
        output.appendChild(span);
        output.scrollTop = output.scrollHeight;
    }

    function clearOut() {
        output.innerHTML = '';
        images.innerHTML = '';
    }

    async function run({ forSubmit = false } = {}) {
        clearOut();
        appendOut(`▶ 运行 ${forSubmit ? '并校验结果' : '中'}...\n`);
        try {
            await boot();
            // 准备数据集
            let files = [];
            if (datasetFiles && datasetFiles.length) {
                for (const f of datasetFiles) {
                    try {
                        const got = await fetchDatasetFile(f.name, f.url);
                        files.push(got);
                        appendOut(`📦 已准备数据集：${f.name}\\n`);
                    } catch (e) {
                        appendOut(`⚠️ 无法下载 ${f.name}: ${e.message}\\n`);
                    }
                }
            }
            const code = textarea.value;
            const r = await runInWorker(code, files);
            if (r.ok) {
                if (!output.textContent.includes('\n') || output.textContent.length < 80) {
                    appendOut('✅ 运行成功（无输出）。\\n');
                } else {
                    appendOut('\\n✅ 运行结束。\\n');
                }
            } else {
                appendOut(`❌ 错误：\\n${r.error || ''}\\n`, '#dc2626');
            }
            for (const img of r.images || []) {
                const el = document.createElement('img');
                el.src = 'data:image/png;base64,' + img;
                el.style.cssText = 'max-width:100%;border:1px solid #e2e8f0;border-radius:8px;background:#fff;';
                images.appendChild(el);
            }
            return r;
        } catch (err) {
            appendOut(`⛔ 异常：${err.message || err}\\n`, '#dc2626');
            return { ok: false, error: err.message };
        }
    }

    container.querySelector('[data-action="reset"]').addEventListener('click', () => {
        textarea.value = initial || '';
        clearOut();
    });
    container.querySelector('[data-action="run"]').addEventListener('click', () => run());
    if (mode === 'exercise') {
        container.querySelector('[data-action="submit"]').addEventListener('click', async () => {
            const r = await run({ forSubmit: true });
            if (!r.ok) {
                toast({ title: '代码有错误', body: '请先修正再提交', type: 'danger' });
                return;
            }
            const result = (typeof checkExpected === 'function') ? checkExpected(textarea.value, { output: output.textContent, images: r.images }) : { passed: !!output.textContent };
            if (result.passed) {
                toast({ title: '🎉 自动评分：通过', body: result.message || '答案符合预期，继续加油！', type: 'success' });
            } else {
                toast({ title: '🤔 未通过', body: result.message || '请参考提示再试试。', type: 'warning' });
            }
            container.dispatchEvent(new CustomEvent('editor:submitted', { detail: { passed: result.passed, message: result.message } }));
        });
    }

    return {
        el: container,
        getCode: () => textarea.value,
        setCode: (v) => { textarea.value = v; },
        reset: () => { textarea.value = initial || ''; clearOut(); },
    };
}
