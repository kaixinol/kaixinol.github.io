import * as SunCalc from "https://esm.sh/suncalc";
import { getGeoFromIP } from "./getIPLocation.js";
(function () {
  let canvas = null;
  let ctx = null;
  let animationId = null;
  let stars = [];

  let seed = parseInt(localStorage.getItem("cosmos_seed") || "0", 10);
  if (!seed) {
    seed = Math.floor(Math.random() * 1e9);
    localStorage.setItem("cosmos_seed", String(seed));
  }

  async function shouldShowStars() {
    if (!document.body.classList.contains("dark")) return false;
    const { lat, lon } = await getGeoFromIP();
    console.log(`Cosmos.js: Location detected at lat=${lat}, lon=${lon}`);
    const sun = SunCalc.getPosition(new Date(), lat, lon);
    const moon = SunCalc.getMoonIllumination(new Date());
    return (
      (sun.altitude * 180) / Math.PI <= -18 &&
      !(moon.phase >= 0.42 && moon.phase <= 0.58)
    );
  }

  // --- 核心渲染引擎 ---
  function createPrng(s) {
    return function () {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
  }

  function initStars() {
    const w = globalThis.innerWidth;
    const h = globalThis.innerHeight;
    const seededRand = createPrng(seed);

    // 密度稍微调低一点，配合稍大的尺寸，避免拥挤
    const count = Math.min(Math.floor((w * h) / 4500) + 120, 1000);
    const colors = ["#ffffff", "#ffe9c4", "#d4fbff", "#a0cfff"];

    stars = [];
    for (let i = 0; i < count; i++) {
      const isDynamic = seededRand() < 0.1; // 10% 动感星

      stars.push({
        x: seededRand() * w,
        y: seededRand() * h,
        // 【调优】尺寸上调：普通星 0.5~1.8，动感星 1.0~2.5
        size: isDynamic ? 1.0 + seededRand() * 1.5 : 0.5 + seededRand() * 1.3,
        color: colors[Math.floor(seededRand() * colors.length)],
        opacity: 0.3 + seededRand() * 0.6,
        canTwinkle: seededRand() > 0.3,
        twinkleSpeed: 0.001 + seededRand() * 0.004,
        phase: seededRand() * Math.PI * 2,

        // 【调优】动感星星速度降低 50%，且 X/Y 轴异步以消除椭圆感
        floatSpeedX: isDynamic
          ? 0.0003 + seededRand() * 0.0005
          : 0.0001 + seededRand() * 0.0002,
        floatSpeedY: isDynamic
          ? 0.0003 + seededRand() * 0.0005
          : 0.0001 + seededRand() * 0.0002,
        floatOffsetX: seededRand() * Math.PI * 2,
        floatOffsetY: seededRand() * Math.PI * 2,
        ampX: isDynamic ? 1.5 + seededRand() * 2.0 : 0.2 + seededRand() * 0.4,
        ampY: isDynamic ? 1.5 + seededRand() * 2.0 : 0.2 + seededRand() * 0.4,
      });
    }
  }

  function draw() {
    if (!ctx) return;
    ctx.clearRect(0, 0, globalThis.innerWidth, globalThis.innerHeight);
    const time = Date.now();

    stars.forEach((s) => {
      let alpha = s.opacity;
      if (s.canTwinkle) {
        const breathing = Math.sin(time * s.twinkleSpeed + s.phase);
        alpha = s.opacity * (0.7 + 0.3 * breathing);
      }

      // 使用独立的 X 和 Y 正弦函数，产生非圆形的自由漂浮轨迹
      const offsetX = Math.sin(time * s.floatSpeedX + s.floatOffsetX) * s.ampX;
      const offsetY = Math.sin(time * s.floatSpeedY + s.floatOffsetY) * s.ampY;

      ctx.beginPath();
      ctx.arc(s.x + offsetX, s.y + offsetY, s.size, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
      ctx.fill();
    });
    animationId = requestAnimationFrame(draw);
  }

  // --- 高清适配与生命周期 ---
  function setupCanvas() {
    if (!canvas) return;
    const dpr = globalThis.devicePixelRatio || 1;
    canvas.width = globalThis.innerWidth * dpr;
    canvas.height = globalThis.innerHeight * dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }

  function start() {
    if (canvas) return;
    canvas = document.createElement("canvas");
    Object.assign(canvas.style, {
      position: "fixed",
      top: 0,
      left: 0,
      width: "100vw",
      height: "100vh",
      zIndex: -1,
      pointerEvents: "none",
      background: "transparent",
    });
    document.body.appendChild(canvas);
    ctx = canvas.getContext("2d");
    setupCanvas();
    initStars();
    draw();
  }

  function stop() {
    if (animationId) cancelAnimationFrame(animationId);
    if (canvas) {
      canvas.remove();
      canvas = null;
      ctx = null;
    }
  }

  // --- 监听与初始化 ---
  const observer = new MutationObserver(() => {
    if (!document.body.classList.contains("dark")) {
      stop();
    } else {
      shouldShowStars().then((yes) => (yes ? start() : stop()));
    }
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["class"],
  });

  let resizeTimer;
  globalThis.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (canvas) {
        setupCanvas();
        initStars();
      }
    }, 250);
  });

  shouldShowStars().then((yes) => yes && start());
})();
