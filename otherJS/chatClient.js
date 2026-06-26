(function (root) {
    const SESSION_KEY = 'psyche_session_id';
    const DEFAULT_TIMEOUT_MS = 10000;
    const ERROR_MESSAGE = 'Unable to reach Arya right now. Please try again.';

    function generateSessionId() {
        if (root.crypto && typeof root.crypto.randomUUID === 'function') {
            return root.crypto.randomUUID();
        }
        return `psyche-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    }

    function getSessionId(storage) {
        const store = storage || root.localStorage;
        let sessionId = store.getItem(SESSION_KEY);
        if (!sessionId) {
            sessionId = generateSessionId();
            store.setItem(SESSION_KEY, sessionId);
        }
        return sessionId;
    }

    function resetSessionId(storage) {
        const store = storage || root.localStorage;
        store.removeItem(SESSION_KEY);
    }

    function handleTimeout(controller, timeoutMs) {
        return root.setTimeout(function () {
            controller.abort();
        }, timeoutMs || DEFAULT_TIMEOUT_MS);
    }

    function handleError() {
        return ERROR_MESSAGE;
    }

    async function sendMessage(message, options) {
        const config = options || {};
        const apiUrl = config.apiUrl;
        if (!apiUrl) {
            throw new Error(handleError());
        }

        const fetchImpl = config.fetchImpl || root.fetch;
        const storage = config.storage || root.localStorage;
        const controller = new root.AbortController();
        const timeoutId = handleTimeout(controller, config.timeoutMs);
        const sessionId = getSessionId(storage);

        try {
            const response = await fetchImpl(`${apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.token || ''}`
                },
                body: JSON.stringify({
                    message,
                    session_id: sessionId
                }),
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.session_id) {
                storage.setItem(SESSION_KEY, data.session_id);
            }
            return data;
        } catch (error) {
            const friendlyError = new Error(handleError(error));
            friendlyError.cause = error;
            throw friendlyError;
        } finally {
            root.clearTimeout(timeoutId);
        }
    }

    async function getHistory(page, limit, options) {
        const config = options || {};
        const apiUrl = config.apiUrl;
        if (!apiUrl) throw new Error(handleError());

        const fetchImpl = config.fetchImpl || root.fetch;
        const controller = new root.AbortController();
        const timeoutId = handleTimeout(controller, config.timeoutMs);

        try {
            const response = await fetchImpl(`${apiUrl}/chat/history?page=${page}&limit=${limit}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${config.token || ''}`
                },
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            const friendlyError = new Error(handleError(error));
            friendlyError.cause = error;
            throw friendlyError;
        } finally {
            root.clearTimeout(timeoutId);
        }
    }

    const client = {
        sendMessage,
        getHistory,
        handleError,
        handleTimeout,
        getSessionId,
        resetSessionId,
        SESSION_KEY,
        ERROR_MESSAGE
    };

    root.PsycheCareChatClient = client;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = client;
    }
})(typeof window !== 'undefined' ? window : globalThis);
