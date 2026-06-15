import shutil
import subprocess
from pathlib import Path

import pytest


CHAT_CLIENT = Path(__file__).resolve().parents[1] / "otherJS" / "chatClient.js"


def run_node(script):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for chat client tests")

    result = subprocess.run(
        [node, "-e", script],
        cwd=CHAT_CLIENT.parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_chat_client_session_payload_timeout_and_errors():
    script = rf"""
    const assert = require('assert');
    const client = require({str(CHAT_CLIENT)!r});

    function makeStorage(initial) {{
      const data = {{ ...(initial || {{}}) }};
      return {{
        data,
        getItem: (key) => data[key] || null,
        setItem: (key, value) => {{ data[key] = value; }},
        removeItem: (key) => {{ delete data[key]; }}
      }};
    }}

    (async () => {{
      const createdStorage = makeStorage();
      const createdSession = client.getSessionId(createdStorage);
      assert.ok(createdSession);
      assert.strictEqual(createdStorage.data[client.SESSION_KEY], createdSession);

      const persistedStorage = makeStorage({{ [client.SESSION_KEY]: 'existing-session' }});
      assert.strictEqual(client.getSessionId(persistedStorage), 'existing-session');

      let postedBody = null;
      const successStorage = makeStorage({{ [client.SESSION_KEY]: 'existing-session' }});
      const data = await client.sendMessage('hello', {{
        apiUrl: 'http://127.0.0.1:5000',
        token: 'token-123',
        storage: successStorage,
        fetchImpl: async (url, options) => {{
          assert.strictEqual(url, 'http://127.0.0.1:5000/chat');
          assert.strictEqual(options.headers.Authorization, 'Bearer token-123');
          postedBody = JSON.parse(options.body);
          return {{
            ok: true,
            json: async () => ({{ response: 'Hi', session_id: 'server-session' }})
          }};
        }}
      }});
      assert.deepStrictEqual(postedBody, {{
        message: 'hello',
        session_id: 'existing-session'
      }});
      assert.strictEqual(data.response, 'Hi');
      assert.strictEqual(successStorage.data[client.SESSION_KEY], 'server-session');

      await assert.rejects(
        client.sendMessage('slow', {{
          apiUrl: 'http://127.0.0.1:5000',
          storage: makeStorage(),
          timeoutMs: 1,
          fetchImpl: (url, options) => new Promise((resolve, reject) => {{
            options.signal.addEventListener('abort', () => reject(new Error('aborted')));
          }})
        }}),
        /Unable to reach Arya right now\. Please try again\./
      );

      await assert.rejects(
        client.sendMessage('fail', {{
          apiUrl: 'http://127.0.0.1:5000',
          storage: makeStorage(),
          fetchImpl: async () => ({{ ok: false, status: 500, json: async () => ({{}}) }})
        }}),
        /Unable to reach Arya right now\. Please try again\./
      );
    }})().catch((error) => {{
      console.error(error);
      process.exit(1);
    }});
    """
    run_node(script)
