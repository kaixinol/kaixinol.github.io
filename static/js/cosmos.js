import SunCalc from "https://esm.sh/suncalc";

(async function () {
  const CHINA_DEFAULT = { lat: 35.0, lon: 105.0 };

  // 获取用户地理位置
  function getLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) return reject();
      navigator.geolocation.getCurrentPosition(
        (pos) =>
          resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        () => reject(),
        { maximumAge: 60 * 60 * 1000, timeout: 5000 },
      );
    });
  }

  // 判断是否夜晚（太阳高度 <= -15°）
  function isNight(lat, lon) {
    const sun = SunCalc.getPosition(new Date(), lat, lon);
    const altitudeDeg = (sun.altitude * 180) / Math.PI;
    return altitudeDeg <= -15;
  }

  // 判断是否满月（phase 0.45~0.55 为满月）
  function isFullMoon() {
    const moon = SunCalc.getMoonIllumination(new Date());
    return moon.phase >= 0.45 && moon.phase <= 0.55;
  }

  // 主判断逻辑
  async function shouldContinue() {
    let lat, lon;
    try {
      ({ lat, lon } = await getLocation());
    } catch {
      ({ lat, lon } = CHINA_DEFAULT);
    }

    return (
      isNight(lat, lon) &&
      !isFullMoon() &&
      document.body.classList.contains("dark")
    );
  }

  if (!(await shouldContinue())) return;

  let svg = null; // 当前星空 SVG
  let seed = parseInt(localStorage.getItem("cosmos_seed") || "0", 10);
  if (!seed) {
    seed = Math.floor(Math.random() * 1e9);
    localStorage.setItem("cosmos_seed", String(seed));
  }

  const seededRand = (function () {
    let s = seed;
    return function () {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
  })();

  function debounce(fn, delay) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function createStars(w, h) {
    const svgNS = "http://www.w3.org/2000/svg";
    const starCount = Math.floor((w * h) / 2500) + 80;
    const colors = ["#ffffff", "#ffe9c4", "#d4fbff", "#a0cfff"];

    const newSvg = document.createElementNS(svgNS, "svg");
    newSvg.classList.add("cosmos-bg");
    newSvg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    newSvg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    newSvg.style.position = "absolute";
    newSvg.style.top = 0;
    newSvg.style.left = 0;
    newSvg.style.width = "100%";
    newSvg.style.height = "100%";
    newSvg.style.zIndex = 0;
    newSvg.style.pointerEvents = "none";

    for (let i = 0; i < starCount; i++) {
      const star = document.createElementNS(svgNS, "circle");
      const x = seededRand() * w;
      const y = seededRand() * h;
      // 稍微让星星大一点以便肉眼可见，但仍然很小
      const size = Math.max(0.5, seededRand() * 2.2);
      const color = colors[Math.floor(seededRand() * colors.length)];
      const opacity = (0.3 + seededRand() * 0.7).toFixed(2);

      star.setAttribute("cx", x);
      star.setAttribute("cy", y);
      star.setAttribute("r", size);
      star.setAttribute("fill", color);
      star.setAttribute("opacity", opacity);

      // 每颗星设置独立的随机漂浮振幅（0.3px~0.5px），方向与相位
      const ampX = (0.3 + seededRand() * 0.2).toFixed(3) + "px"; // 0.3 ~ 0.5 px
      const ampY = (0.3 + seededRand() * 0.2).toFixed(3) + "px";
      const dirX = (seededRand() * 2 - 1).toFixed(3); // -1 ~ 1
      const dirY = (seededRand() * 2 - 1).toFixed(3);
      const phase = (seededRand() * 1).toFixed(3);

      star.style.setProperty("--amp-x", ampX);
      star.style.setProperty("--amp-y", ampY);
      star.style.setProperty("--dir-x", dirX);
      star.style.setProperty("--dir-y", dirY);
      star.style.setProperty("--phase", phase);

      // 性能提示：告知浏览器我们将会变换 transform/opacity
      star.style.willChange = "transform, opacity";

      // 闪烁与漂浮（两个动画同时存在时指定延迟）
      if (seededRand() > 0.3) {
        const duration = (2 + seededRand() * 5).toFixed(2);
        const delay = (seededRand() * 5).toFixed(2);
        // float 动画在中点会移动到 var(--dir * --amp)
        star.style.animation = `twinkle ${duration}s infinite ease-in-out, float ${(
          10 +
          seededRand() * 20
        ).toFixed(2)}s infinite ease-in-out`;
        star.style.animationDelay = `${delay}s, ${(seededRand() * 10).toFixed(2)}s`;
      } else {
        const floatDuration = (10 + seededRand() * 20).toFixed(2);
        star.style.animation = `float ${floatDuration}s infinite ease-in-out`;
        star.style.animationDelay = `${(seededRand() * 10).toFixed(2)}s`;
      }

      newSvg.appendChild(star);
    }

    return newSvg;
  }

  function initCosmos() {
    if (!document.body.classList.contains("dark")) return;

    const container = document.getElementById("wrapper");
    if (!container) return;

    const w = window.innerWidth;
    const h = window.innerHeight;

    // 注入 CSS 动画（一次即可）
    if (!document.getElementById("twinkle-style")) {
      const style = document.createElement("style");
      style.id = "twinkle-style";
      style.innerHTML = `
        @keyframes twinkle {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }

        /* float 动画：在 50% 位移到 --dir * --amp 的位置，amp 单位为 px，范围控制在 0.3px~0.5px */
        @keyframes float {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(calc(var(--dir-x) * var(--amp-x)), calc(var(--dir-y) * var(--amp-y))); }
        }

        svg.cosmos-bg {
          display: block;
        }

        svg.cosmos-bg circle {
          pointer-events: none;
        }
      `;
      document.head.appendChild(style);
    }

    // 删除旧星空
    if (svg) svg.remove();

    svg = createStars(w, h);
    container.prepend(svg);

    // 保证内容在星空之上
    Array.from(container.children).forEach((c) => {
      if (c !== svg) {
        if (!c.style.position) c.style.position = "relative";
        c.style.zIndex = 1;
      }
    });
  }

  const debouncedInit = debounce(initCosmos, 200);

  // 如果 load/DOMContentLoaded 已经发生则立即执行，否则等待 DOMContentLoaded
  function attachAndMaybeRun() {
    window.addEventListener("resize", debouncedInit);
    if (
      document.readyState === "complete" ||
      document.readyState === "interactive"
    ) {
      initCosmos();
    } else {
      window.addEventListener("DOMContentLoaded", initCosmos, { once: true });
    }
  }

  attachAndMaybeRun();
})();
