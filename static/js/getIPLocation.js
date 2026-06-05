async function fetchGeoWithFallback() {
  const providers = [
    {
      url: "https://ipapi.co/json",
      map: (d) => ({
        latitude: d.latitude,
        longitude: d.longitude,
        country_code: d.country_code,
        ip: d.ip
      })
    },
    {
      url: "https://ipinfo.io/json",
      map: (d) => {
        const [lat, lon] = (d.loc || "").split(",");
        return {
          latitude: lat ? parseFloat(lat) : null,
          longitude: lon ? parseFloat(lon) : null,
          country_code: d.country || null,
          ip: d.ip || null
        };
      }
    },
    /*{
      url: "https://ip-api.com/json",
      map: (d) => ({
        latitude: d.lat,
        longitude: d.lon,
        country_code: d.countryCode,
        ip: d.query || null
      })
    },
    {
      url: "https://ipwho.is/",
      map: (d) => ({
        latitude: d.latitude,
        longitude: d.longitude,
        country_code: d.country_code,
        ip: d.ip || null
      })
    },*/
    {
      url: "https://get.geojs.io/v1/ip/geo.json",
      map: (d) => ({
        latitude: parseFloat(d.latitude),
        longitude: parseFloat(d.longitude),
        country_code: d.country_code,
        ip: d.ip || d.ip_address || null
      })
    }
  ];

  for (const p of providers) {
    try {
      const res = await fetch(p.url, { cache: "no-store" });
      if (!res.ok) continue;

      const data = await res.json();
      const mapped = p.map(data);

      if (mapped.latitude && mapped.longitude) {
        return mapped;
      }
    } catch (_) {
      // ignore and try next provider
    }
  }

  return null;
}
// --- 逻辑判断 ---
export async function getGeoFromIP() {
    const CHINA_TZ_MAP = {
        "Asia/Shanghai": { lat: 31.2304, lon: 121.4737 }, // 上海
        "Asia/Chongqing": { lat: 29.5630, lon: 106.5516 }, // 重庆
        "Asia/Harbin": { lat: 45.7528, lon: 126.6583 }, // 哈尔滨
        "Asia/Urumqi": { lat: 43.8257, lon: 87.6167 }, // 乌鲁木齐
    };

    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const isChinaTZ = /Asia\/(Shanghai|Chongqing|Harbin|Urumqi)/.test(tz);

    try {
        const data = await fetchGeoWithFallback();
        const ipIsChina = data?.country_code === "CN";

        // 正常情况：中国IP + 中国时区
        if (ipIsChina && isChinaTZ) {
            return {
                lat: data.latitude,
                lon: data.longitude,
                flag: "normal",
            };
        }

        // 关键：国外IP + 中国时区 => 异常（可能 VPN / 代理 / DNS 干扰）
        if (!ipIsChina && isChinaTZ) {
            console.warn(
                `Detected mismatch: non-CN IP (${data?.ip}) but China timezone (possible proxy / restriction)`,
            );

            const fallback = CHINA_TZ_MAP[tz] || CHINA_TZ_MAP["Asia/Shanghai"];

            return {
                ...fallback,
                flag: "suspicious_geo_mismatch",
            };
        }

        // 其他情况：直接用 IP
        if (data.latitude && data.longitude) {
            return {
                lat: data.latitude,
                lon: data.longitude,
                flag: "ip_based",
            };
        }
    } catch (_e) {
        // ignore network/location errors
    }

    return {
        lat: 34.7466,
        lon: 113.6254,
        flag: "fallback_default",
    };
}
