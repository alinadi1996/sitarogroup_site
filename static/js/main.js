(() => {
    "use strict";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const header = document.querySelector("[data-header]");
    const menuToggle = document.querySelector("[data-menu-toggle]");
    const mobileMenu = document.querySelector("[data-mobile-menu]");
    const themeToggle = document.querySelector("[data-theme-toggle]");

    const syncThemeToggle = () => {
        if (!themeToggle) return;
        const isLight = document.documentElement.dataset.theme === "light";
        themeToggle.setAttribute("aria-pressed", String(isLight));
        themeToggle.setAttribute("aria-label", isLight ? "فعال‌کردن حالت تیره" : "فعال‌کردن حالت روشن");
        themeToggle.title = isLight ? "حالت تیره" : "حالت روشن";
        const themeMeta = document.querySelector('meta[name="theme-color"]');
        themeMeta?.setAttribute("content", isLight ? "#f2f0e9" : "#07110f");
    };

    syncThemeToggle();
    themeToggle?.addEventListener("click", () => {
        const nextTheme = document.documentElement.dataset.theme === "light" ? "dark" : "light";
        document.documentElement.dataset.theme = nextTheme;
        try { localStorage.setItem("sitaro-theme", nextTheme); } catch (error) { /* Storage can be unavailable. */ }
        syncThemeToggle();
    });

    const updateHeader = () => header?.classList.toggle("is-scrolled", window.scrollY > 20);
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });

    const setMenu = (open) => {
        if (!menuToggle || !mobileMenu) return;
        menuToggle.setAttribute("aria-expanded", String(open));
        menuToggle.setAttribute("aria-label", open ? "بستن منو" : "باز کردن منو");
        mobileMenu.hidden = !open;
        document.body.classList.toggle("menu-open", open);
    };

    menuToggle?.addEventListener("click", () => setMenu(menuToggle.getAttribute("aria-expanded") !== "true"));
    mobileMenu?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMenu(false)));
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && menuToggle?.getAttribute("aria-expanded") === "true") {
            setMenu(false);
            menuToggle.focus();
        }
    });

    const supportDock = document.querySelector("[data-support-dock]");
    const supportPanel = document.querySelector("[data-support-panel]");
    const supportToggle = document.querySelector("[data-support-toggle]");
    const supportClose = document.querySelector("[data-support-close]");
    const supportForm = document.querySelector("[data-support-form]");
    const supportInput = document.querySelector("[data-support-input]");
    const supportLog = document.querySelector("[data-support-log]");
    const socialToggle = document.querySelector("[data-social-toggle]");
    const socialList = document.querySelector("[data-social-list]");

    const setSupport = (open, restoreFocus = false) => {
        if (!supportDock || !supportPanel || !supportToggle) return;
        supportDock.classList.toggle("is-open", open);
        supportToggle.setAttribute("aria-expanded", String(open));
        supportPanel.setAttribute("aria-hidden", String(!open));
        if (open) {
            supportPanel.removeAttribute("inert");
            window.setTimeout(() => supportInput?.focus({ preventScroll: true }), prefersReducedMotion ? 0 : 260);
        } else {
            supportPanel.setAttribute("inert", "");
            if (restoreFocus) supportToggle.focus({ preventScroll: true });
        }
    };

    const appendSupportMessage = (text, sender = "agent") => {
        if (!supportLog) return;
        const message = document.createElement("div");
        const prompt = document.createElement("span");
        const copy = document.createElement("p");
        message.className = `support-message support-message-${sender}`;
        prompt.className = "support-prompt";
        prompt.setAttribute("aria-hidden", "true");
        prompt.textContent = sender === "user" ? "YOU" : "AI";
        copy.textContent = text;
        message.append(prompt, copy);
        supportLog.append(message);
        supportLog.scrollTo({ top: supportLog.scrollHeight, behavior: prefersReducedMotion ? "auto" : "smooth" });
    };

    const answerSupportMessage = () => {
        window.setTimeout(() => {
            appendSupportMessage("برای بررسی دقیق و پیگیری درخواست، از گزینه «ثبت درخواست رسمی» استفاده کنید؛ تیم سیتارو اطلاعات پروژه را از همان مسیر دریافت می‌کند.");
        }, prefersReducedMotion ? 0 : 420);
    };

    supportPanel?.setAttribute("inert", "");
    supportToggle?.addEventListener("click", () => setSupport(!supportDock?.classList.contains("is-open")));
    supportClose?.addEventListener("click", () => setSupport(false, true));
    supportForm?.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = supportInput?.value.trim();
        if (!text) {
            supportInput?.focus();
            return;
        }
        appendSupportMessage(text, "user");
        supportForm.reset();
        answerSupportMessage();
    });
    document.querySelectorAll("[data-support-quick]").forEach((button) => {
        button.addEventListener("click", () => {
            if (!supportInput || !supportForm) return;
            supportInput.value = button.dataset.supportQuick || "";
            supportForm.requestSubmit();
        });
    });
    socialToggle?.addEventListener("click", () => {
        if (!socialList) return;
        const open = socialToggle.getAttribute("aria-expanded") !== "true";
        socialToggle.setAttribute("aria-expanded", String(open));
        socialList.hidden = !open;
    });
    document.querySelectorAll("[data-support-social]").forEach((button) => {
        button.addEventListener("click", () => {
            const channel = button.dataset.supportSocial || "شبکه اجتماعی";
            const url = button.dataset.supportUrl?.trim();
            if (url) {
                window.open(url, "_blank", "noopener,noreferrer");
                return;
            }
            appendSupportMessage(`ارتباط از طریق ${channel}`, "user");
            window.setTimeout(() => appendSupportMessage(`کانال ${channel} انتخاب شد. آدرس رسمی این شبکه هنوز در تنظیمات فرانت وارد نشده؛ برای ارتباط قطعی، درخواست رسمی ثبت کنید.`), prefersReducedMotion ? 0 : 300);
        });
    });
    const blogFeed = document.querySelector("[data-blog-feed]");
    const blogViewButtons = document.querySelectorAll("[data-blog-view]");
    const setBlogView = (view) => {
        if (!blogFeed || !["grid", "list"].includes(view)) return;
        blogFeed.dataset.view = view;
        blogViewButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.blogView === view)));
        try { localStorage.setItem("sitaro-blog-view", view); } catch (error) { /* Storage can be unavailable. */ }
    };
    if (blogFeed) {
        let initialBlogView = window.matchMedia("(max-width: 760px)").matches ? "list" : "grid";
        try { initialBlogView = localStorage.getItem("sitaro-blog-view") || initialBlogView; } catch (error) { /* Keep responsive default. */ }
        setBlogView(initialBlogView);
        blogViewButtons.forEach((button) => button.addEventListener("click", () => setBlogView(button.dataset.blogView)));
    }
    document.querySelectorAll("[data-journal-social]").forEach((button) => {
        button.addEventListener("click", () => {
            const channel = button.dataset.journalSocial;
            const supportChannel = Array.from(document.querySelectorAll("[data-support-social]")).find((item) => item.dataset.supportSocial === channel);
            if (!supportChannel) return;
            setSupport(true);
            if (socialToggle && socialList) {
                socialToggle.setAttribute("aria-expanded", "true");
                socialList.hidden = false;
            }
            supportChannel.click();
        });
    });
    document.addEventListener("pointerdown", (event) => {
        if (supportDock?.classList.contains("is-open") && !supportDock.contains(event.target)) setSupport(false);
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && supportDock?.classList.contains("is-open")) setSupport(false, true);
    });

    const reveals = document.querySelectorAll(".reveal-on-scroll");
    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
        reveals.forEach((item) => item.classList.add("is-visible"));
    } else {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        }, { rootMargin: "0px 0px -8%", threshold: 0.12 });
        reveals.forEach((item) => revealObserver.observe(item));
    }

    const filterButtons = document.querySelectorAll("[data-filter]");
    const projects = document.querySelectorAll("[data-category]");
    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const filter = button.dataset.filter;
            filterButtons.forEach((item) => {
                const active = item === button;
                item.classList.toggle("is-active", active);
                item.setAttribute("aria-pressed", String(active));
            });
            projects.forEach((project) => {
                const visible = filter === "all" || project.dataset.category.split(" ").includes(filter);
                project.classList.toggle("is-hidden", !visible);
            });
        });
    });

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.parentElement?.querySelector("input");
            if (!input) return;
            const willShow = input.type === "password";
            input.type = willShow ? "text" : "password";
            button.textContent = willShow ? "پنهان" : "نمایش";
            button.setAttribute("aria-label", willShow ? "پنهان کردن رمز عبور" : "نمایش رمز عبور");
        });
    });

    const canvas = document.getElementById("hero-canvas");
    if (!canvas) return;
    const context = canvas.getContext("2d", { alpha: true, desynchronized: true });
    if (!context) return;

    const host = canvas.parentElement;
    const phi = (1 + Math.sqrt(5)) / 2;
    const rawVertices = [
        [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ];
    const length = Math.hypot(...rawVertices[0]);
    const vertices = rawVertices.map(([x, y, z]) => [x / length, y / length, z / length]);
    const edges = [];
    for (let i = 0; i < vertices.length; i += 1) {
        for (let j = i + 1; j < vertices.length; j += 1) {
            const distance = Math.hypot(
                vertices[i][0] - vertices[j][0],
                vertices[i][1] - vertices[j][1],
                vertices[i][2] - vertices[j][2]
            );
            if (distance < 1.08) edges.push([i, j]);
        }
    }

    let width = 0;
    let height = 0;
    let pixelRatio = 1;
    let frame = 0;
    let visible = !document.hidden;
    let pointerX = 0;
    let pointerY = 0;
    let targetX = 0;
    let targetY = 0;

    const resize = () => {
        const bounds = host.getBoundingClientRect();
        width = Math.max(1, bounds.width);
        height = Math.max(1, bounds.height);
        pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
        canvas.width = Math.round(width * pixelRatio);
        canvas.height = Math.round(height * pixelRatio);
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    };

    const rotatePoint = ([x, y, z], rotationX, rotationY, rotationZ) => {
        const cosX = Math.cos(rotationX), sinX = Math.sin(rotationX);
        const cosY = Math.cos(rotationY), sinY = Math.sin(rotationY);
        const cosZ = Math.cos(rotationZ), sinZ = Math.sin(rotationZ);
        const y1 = y * cosX - z * sinX;
        const z1 = y * sinX + z * cosX;
        const x2 = x * cosY + z1 * sinY;
        const z2 = -x * sinY + z1 * cosY;
        return [x2 * cosZ - y1 * sinZ, x2 * sinZ + y1 * cosZ, z2];
    };

    const project = ([x, y, z], size) => {
        const perspective = 3.6 / (4.2 - z);
        return {
            x: width * 0.5 + x * size * perspective,
            y: height * 0.5 + y * size * perspective,
            z,
            scale: perspective
        };
    };

    const drawOrbit = (radius, tilt, rotation, alpha) => {
        context.beginPath();
        const steps = 90;
        for (let i = 0; i <= steps; i += 1) {
            const angle = (i / steps) * Math.PI * 2;
            const point = rotatePoint([Math.cos(angle), Math.sin(angle), 0], tilt, rotation, rotation * .22);
            const projected = project(point, radius);
            if (i === 0) context.moveTo(projected.x, projected.y);
            else context.lineTo(projected.x, projected.y);
        }
        context.strokeStyle = `rgba(103, 245, 196, ${alpha})`;
        context.lineWidth = .7;
        context.stroke();
    };

    const draw = (time = 0) => {
        if (!visible) return;
        context.clearRect(0, 0, width, height);
        pointerX += (targetX - pointerX) * .035;
        pointerY += (targetY - pointerY) * .035;

        const slowTime = prefersReducedMotion ? .6 : time * .00012;
        const rotationX = .18 + slowTime * .42 + pointerY * .18;
        const rotationY = -.35 + slowTime + pointerX * .26;
        const rotationZ = slowTime * .18;
        const size = Math.min(width, height) * .47;

        context.save();
        context.globalCompositeOperation = "lighter";
        drawOrbit(size * 1.18, 1.12, rotationY * .5, .11);
        drawOrbit(size * 1.02, -.62, rotationY * -.38, .085);
        drawOrbit(size * .9, .25, rotationY * .3, .06);
        context.restore();

        const transformed = vertices.map((vertex) => project(rotatePoint(vertex, rotationX, rotationY, rotationZ), size));

        edges.sort((a, b) => (transformed[a[0]].z + transformed[a[1]].z) - (transformed[b[0]].z + transformed[b[1]].z));
        edges.forEach(([startIndex, endIndex]) => {
            const start = transformed[startIndex];
            const end = transformed[endIndex];
            const depth = (start.z + end.z + 2) / 4;
            context.beginPath();
            context.moveTo(start.x, start.y);
            context.lineTo(end.x, end.y);
            context.strokeStyle = `rgba(103, 245, 196, ${.07 + depth * .43})`;
            context.lineWidth = .55 + depth * 1.1;
            context.stroke();
        });

        transformed.forEach((point, index) => {
            const depth = (point.z + 1) / 2;
            const radius = 1.4 + depth * 3;
            context.beginPath();
            context.arc(point.x, point.y, radius, 0, Math.PI * 2);
            context.fillStyle = depth > .62 ? `rgba(255, 255, 249, ${.35 + depth * .6})` : `rgba(103, 245, 196, ${.15 + depth * .55})`;
            context.fill();
            if (index % 3 === 0 && depth > .55) {
                context.beginPath();
                context.arc(point.x, point.y, radius * 3.2, 0, Math.PI * 2);
                context.strokeStyle = `rgba(103, 245, 196, ${depth * .12})`;
                context.stroke();
            }
        });

        const coreGradient = context.createRadialGradient(width * .5, height * .5, 0, width * .5, height * .5, size * .36);
        coreGradient.addColorStop(0, "rgba(103,245,196,.13)");
        coreGradient.addColorStop(.45, "rgba(103,245,196,.035)");
        coreGradient.addColorStop(1, "rgba(103,245,196,0)");
        context.fillStyle = coreGradient;
        context.beginPath();
        context.arc(width * .5, height * .5, size * .36, 0, Math.PI * 2);
        context.fill();

        if (!prefersReducedMotion) frame = requestAnimationFrame(draw);
    };

    const handlePointer = (event) => {
        const bounds = host.getBoundingClientRect();
        targetX = ((event.clientX - bounds.left) / bounds.width - .5) * 2;
        targetY = ((event.clientY - bounds.top) / bounds.height - .5) * 2;
    };

    const handleVisibility = () => {
        visible = !document.hidden;
        if (visible && !prefersReducedMotion) {
            cancelAnimationFrame(frame);
            frame = requestAnimationFrame(draw);
        } else {
            cancelAnimationFrame(frame);
        }
    };

    const resizeObserver = "ResizeObserver" in window ? new ResizeObserver(resize) : null;
    resizeObserver?.observe(host);
    if (!resizeObserver) window.addEventListener("resize", resize, { passive: true });
    if (window.matchMedia("(pointer: fine)").matches && !prefersReducedMotion) {
        host.addEventListener("pointermove", handlePointer, { passive: true });
        host.addEventListener("pointerleave", () => { targetX = 0; targetY = 0; }, { passive: true });
    }
    document.addEventListener("visibilitychange", handleVisibility);
    resize();
    draw(5000);
})();
