## 了解什麼是 CSRF Token 與如何使用 #135

- 什麼是 CSRF 攻擊，該如何預防？
  CSRF，全名：「Cross Site Request Forgery」跨站請求偽造。這種攻擊方法是利用使用者已經在 A 網站驗證過身份，在自己的 B 網站（惡意網站）中偷偷嵌入可以連結到 A 網站的連結，當使用者瀏覽 B 網站的時候，在使用者無法察覺的情況下，帶著通過驗證的本地 cookie 順利進入 A 網站。

      **預防的方法**：
      1. 讓每一次的請求加上驗證，例如圖形驗證碼、簡訊驗證碼，但因為很麻煩，所以會適合比較危險的操作，例如：匯款。
      2. 不要用`GET`，而是 `POST` 來操作請求。因為 POST 需要使用者提交動作才能出發，使惡意網站需要引誘使用者去點擊某些按鈕，但是這需要仰賴使用者的警覺性。
      3. 瀏覽器本身加防護，讓本地 cookie 不是毫無限制的被使用，而是有限制的使用，例如 Chrome 的 `SameSite cookies` 功能。
      4. 呼應第一種加上驗證的方法，可以使用「`CSRF token`」。讓網站不是透過 cookie ，而是 CSRF token 驗證使用者的身分。

- 說明如何在 flask 專案中使用以下 `csrf_token()`語法。

  - INSTALL `flask_wtf`
  - 在 python 中 call:

  ```python
  from flask import Flask, render_template, request
  from flask_wtf import CSRFProtect
  app = Flask(__name__)
  app.secret_key = 'your-secret-key'
  csrf = CSRFProtect(app)
  ```

  - 在 .html 中 call:

  ```html
  <form method="post">
    <!-- 在這裡加入隱藏的輸入欄位，帶上 token -->
    <input
      type="hidden"
      name="csrf_token"
      value="{{ csrf_token() }}"
    />
    <div>
      <label for="username">Username:</label>
      <input type="text" id="username" name="username" required />
    </div>
    <div>
      <label for="password">Password:</label>
      <input type="password" id="password" name="password" required />
    </div>
    <div>
      <input type="submit" value="Log in" />
    </div>
  </form>
  ```

- ajax 需不需要使用 csrf token 進行防禦？該如何使用？
  用 ajax 也可以使用 csrf token，在 header 中加入 `csrf-token`，例如：

```javascript
$(function() {
    $.ajax({
      type: 'PATCH',
      url: '/comments/' + commentId,
      data: {
        comment: {
          body: body
        },
      },
//追記ここから
        headers: {
          'X-CSRF-Token' : $('meta[name="csrf-token"]').attr('content')
        },
//追記ここまで
      dataType: 'json',
    }).done(function (data) {

      //成功処理

    }).fail(function () {

      //失敗処理

    });
  })
});

```

- 參考文件：
  - [Explain This](https://www.explainthis.io/zh-hant/swe/what-is-csrf)
  - [CSRF-TOKEN in JS](https://qiita.com/nindendon/items/7a443e32b0e24c5bcf31)

## 學會 VS Code + VirtualEnv 組合技 #138

- 如何使用 Virtualenv 建立環境
  `python3 -m venv .venv` 但，`.venv` 可以是任何 .{filename} 名稱。
- 調教 VS Code 讓 VirtualEnv 環境更好用
  使用一個 VS Code 的套件叫做： `Python Environment Manager`，可以快速的切換虛擬環境。
- 如何測試環境使否有載入成功

  - 看 VS Code 的終端機前面有沒有出現`(.venv)`
    例如：

  ```shell
  (.venv_csrf) [~/my_project/mento-camp-missions/flask-project-1/csrf-example] (main) $
  ```

  - VS Code 終端機輸入`which python`，會出現：

  ```shell
  /Users/cyyeh/my_project/mento-camp-missions/flask-project-1/csrf-example/.venv_csrf/bin/python
  ```

  - 如果都沒有成功，可以輸入`source [.{filename}]/bin/activate`

- 如何判斷套件是否安裝成功
  - 輸入指令看有沒有成功：
  ```shell
  pip show <fileName>
  ```
  - 直接 import 試試看，執行 `flask run` 就可以知道有沒有成功。
