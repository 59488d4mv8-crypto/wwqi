/**
 * router.js - 基于 location.hash 的简单单页路由
 */

const routes = new Map();

/**
 * 注册路由
 * @param {string} path - 如 "/", "/courses", "/courses/:id"
 * @param {(params: object) => string|Promise<string>} handler
 */
export function registerRoute(path, handler) {
  routes.set(path, handler);
}

/**
 * 解析当前 hash，匹配并渲染到 #app
 */
export function renderRoute() {
  const hash = window.location.hash || '#/';
  const path = hash.replace(/^#/, '');

  const app = document.getElementById('app');
  if (!app) return;

  for (const [pattern, handler] of routes.entries()) {
    const match = matchPath(pattern, path);
    if (match) {
      Promise.resolve(handler(match.params, path)).then((html) => {
        if (typeof html === 'string') {
          app.innerHTML = html;
          // 触发自定义事件，各视图可在自己模块中监听以挂载交互
          window.dispatchEvent(new CustomEvent('route:mounted', {
            detail: { path, params: match.params },
          }));
          window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
        }
      }).catch((err) => {
        console.error('[router] 渲染失败：', err);
        app.innerHTML = `<section class="not-found">
          <h1>出错了</h1>
          <p>${String(err.message || err)}</p>
          <a class="btn btn-primary" href="#/">返回首页</a>
        </section>`;
      });
      return;
    }
  }

  // 未匹配
  app.innerHTML = `<section class="not-found">
    <h1>404</h1>
    <p>抱歉，找不到该页面。</p>
    <a class="btn btn-primary" href="#/">返回首页</a>
  </section>`;
}

/**
 * 将动态路径与当前路径进行匹配
 * 支持 :id 形式的参数
 */
function matchPath(pattern, path) {
  const patternParts = pattern.split('/').filter(Boolean);
  const pathParts = path.split('/').filter(Boolean);

  if (patternParts.length !== pathParts.length) return null;

  const params = {};
  for (let i = 0; i < patternParts.length; i++) {
    const p = patternParts[i];
    const v = pathParts[i];
    if (p.startsWith(':')) {
      params[p.slice(1)] = decodeURIComponent(v);
    } else if (p !== v) {
      return null;
    }
  }
  return { params };
}

/**
 * 便捷导航
 */
export function navigate(path) {
  if (!path.startsWith('/')) path = '/' + path;
  window.location.hash = '#' + path;
}

/**
 * 初始化路由监听
 */
export function initRouter() {
  window.addEventListener('hashchange', renderRoute);
  renderRoute();
}
