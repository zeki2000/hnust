/**
 * Cookie操作工具类
 * 创建于: 2024-04-23
 * 功能: 提供cookie的读取、设置和删除功能
 */

class CookieUtil {
    /**
     * 设置cookie
     * @param {string} name - cookie名称
     * @param {string} value - cookie值
     * @param {number} days - 过期天数(可选)
     * @param {string} path - 路径(可选，默认'/')
     * @param {string} domain - 域名(可选)
     * @param {boolean} secure - 是否仅HTTPS(可选)
     * @param {string} sameSite - SameSite属性(可选)
     */
    static set(name, value, days, path = '/', domain, secure, sameSite) {
        let expires = '';
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = `; expires=${date.toUTCString()}`;
        }

        let cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}${expires}; path=${path}`;
        
        if (domain) cookie += `; domain=${domain}`;
        if (secure) cookie += '; secure';
        if (sameSite) cookie += `; SameSite=${sameSite}`;
        
        document.cookie = cookie;
    }

    /**
     * 获取cookie值
     * @param {string} name - 要获取的cookie名称
     * @returns {string|null} - cookie值或null
     */
    static get(name) {
        const nameEQ = `${encodeURIComponent(name)}=`;
        const cookies = document.cookie.split(';');
        
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i];
            while (cookie.charAt(0) === ' ') {
                cookie = cookie.substring(1, cookie.length);
            }
            if (cookie.indexOf(nameEQ) === 0) {
                return decodeURIComponent(cookie.substring(nameEQ.length, cookie.length));
            }
        }
        return null;
    }

    /**
     * 删除cookie
     * @param {string} name - 要删除的cookie名称
     * @param {string} path - 路径(可选，默认'/')
     * @param {string} domain - 域名(可选)
     */
    static remove(name, path = '/', domain) {
        this.set(name, '', -1, path, domain);
    }

    /**
     * 检查cookie是否存在
     * @param {string} name - 要检查的cookie名称
     * @returns {boolean} - 是否存在
     */
    static has(name) {
        return this.get(name) !== null;
    }
}

// 导出为全局对象
window.CookieUtil = CookieUtil;

// 添加readCookie兼容函数
window.readCookie = function(name) {
    return CookieUtil.get(name);
};

// 兼容CommonJS环境
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CookieUtil;
}
