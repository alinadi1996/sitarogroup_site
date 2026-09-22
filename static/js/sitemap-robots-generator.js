(() => {
    "use strict";
    const tool = document.querySelector("[data-sr-tool]");
    if (!tool) return;

    const siteInput = tool.querySelector("[data-sr-site-url]");
    const urlsInput = tool.querySelector("[data-sr-urls]");
    const disallowInput = tool.querySelector("[data-sr-disallow]");
    const sitemapCode = tool.querySelector("[data-sr-sitemap]");
    const robotsCode = tool.querySelector("[data-sr-robots]");
    const status = tool.querySelector("[data-sr-status]");
    const count = tool.querySelector("[data-sr-count]");
    const feedback = tool.querySelector("[data-sr-feedback]");
    let output = null;

    const validUrl = (value) => { try { const url = new URL(value); return ["http:", "https:"].includes(url.protocol); } catch { return false; } };
    const escapeXml = (value) => value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
    const setFeedback = (message, error = false) => { feedback.textContent = message; feedback.classList.toggle("is-error", error); };
    const getUrls = () => [...new Set(urlsInput.value.split(/\r?\n/).map((url) => url.trim()).filter(Boolean))];

    const generate = () => {
        const site = siteInput.value.trim().replace(/\/+$/, "");
        const urls = getUrls();
        const invalid = urls.find((url) => !validUrl(url));
        if (!validUrl(site)) { setFeedback("آدرس اصلی سایت باید با http یا https وارد شود.", true); return; }
        if (!urls.length) { setFeedback("حداقل یک URL صفحه وارد کنید.", true); return; }
        if (invalid) { setFeedback(`این URL معتبر نیست: ${invalid}`, true); return; }
        const today = new Date().toISOString().slice(0, 10);
        const withDate = tool.querySelector("[data-sr-lastmod]").checked;
        const allowAssets = tool.querySelector("[data-sr-allow]").checked;
        const disallows = [...new Set(disallowInput.value.split(/\r?\n/).map((path) => path.trim()).filter(Boolean))];
        const invalidPath = disallows.find((path) => !path.startsWith("/"));
        if (invalidPath) { setFeedback(`مسیر غیرقابل‌خزش باید با / شروع شود: ${invalidPath}`, true); return; }
        const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((url) => `  <url>\n    <loc>${escapeXml(url)}</loc>${withDate ? `\n    <lastmod>${today}</lastmod>` : ""}\n  </url>`).join("\n")}\n</urlset>`;
        const robots = ["User-agent: *", ...(allowAssets ? ["Allow: /*.css$", "Allow: /*.js$"] : []), ...disallows.map((path) => `Disallow: ${path}`), "", `Sitemap: ${site}/sitemap.xml`].join("\n");
        output = { sitemap, robots };
        sitemapCode.textContent = sitemap;
        robotsCode.textContent = robots;
        count.textContent = `${urls.length} URL`;
        status.textContent = "فایل‌ها آماده‌اند";
        setFeedback("Sitemap و robots.txt آماده دانلود هستند.");
    };
    const copy = async (text) => { try { await navigator.clipboard.writeText(text); setFeedback("محتوا با موفقیت کپی شد."); } catch { setFeedback("کپی خودکار ممکن نشد. دسترسی Clipboard مرورگر را بررسی کنید.", true); } };
    const download = (type) => { if (!output) { setFeedback("ابتدا فایل‌ها را بسازید.", true); return; } const blob = new Blob([output[type]], { type: type === "sitemap" ? "application/xml" : "text/plain" }); const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = type === "sitemap" ? "sitemap.xml" : "robots.txt"; link.click(); URL.revokeObjectURL(link.href); setFeedback("فایل آماده دانلود شد."); };

    tool.querySelector("[data-sr-generate]").addEventListener("click", generate);
    tool.querySelector("[data-sr-reset]").addEventListener("click", () => { tool.querySelector("[data-sr-form]").reset(); output = null; sitemapCode.textContent = "<!-- URLهای سایت را وارد کنید. -->"; robotsCode.textContent = "# robots.txt آماده می‌شود"; count.textContent = "0 URL"; status.textContent = "در انتظار اطلاعات"; setFeedback("فرم پاک شد."); });
    tool.querySelectorAll("[data-sr-copy]").forEach((button) => button.addEventListener("click", () => output ? copy(output[button.dataset.srCopy]) : setFeedback("ابتدا فایل‌ها را بسازید.", true)));
    tool.querySelectorAll("[data-sr-download]").forEach((button) => button.addEventListener("click", () => download(button.dataset.srDownload)));
})();
