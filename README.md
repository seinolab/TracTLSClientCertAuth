# TracTLSClientCertAuth

クライアント証明書で認証を行うための Trac プラグインです。

`SSL_CLIENT_S_DN` で渡されたクライアント証明書の認証情報を `REMOTE_HOST` に設定し直すだけの適当な実装です。

ChatGPT が生成したコードをちょっと手直ししたものです。私は Python には詳しくないので、変なところがあるかもしれません。識者の方、おかしい部分などご指摘歓迎いたします。

## インストール

個別の Trac プロジェクトにインストールする場合:

```
setup.py bdist_egg
cp dist/tracopt_auth_tls_client_certs-1.0-py3.9.egg /path/to/trac/plugins
```

※ 出来上がった `.egg` ファイルを Trac の管理画面から読み込ませても OK です。

Trac プロジェクト全体で使用する場合:

```
setup.py bdist_egg
sudo python3 setup.py install
```

## 使用例

複数の Trac プロジェクトを運用している想定です。それぞれのプロジェクトは、以下の URL で運用しているとします。

* https://trac.example.com/foo/
* https://trac.example.com/bar/

各プロジェクトの認証ポイントは、以下の URL になります。

* https://trac.example.com/foo/login
* https://trac.example.com/bar/login

これらの URL を正規表現でまとめて指定します。Nginx ではクライアント証明書の DN が `$ssl_client_s_dn` に渡されるので、環境変数　`SSL_CLIENT_S_DN` にそのまま渡す設定にします。

```
    ssl_verify_client on;

    location ~ ^/([^/]+)/login$ {
        include fastcgi_params;
        fastcgi_pass unix:/run/trac/$1/trac.sock;
        fastcgi_param SCRIPT_NAME /$1;
        fastcgi_param PATH_INFO /login;
        fastcgi_param SSL_CLIENT_S_DN $ssl_client_s_dn;
    }
```

このプラグインが、`SSL_CLIENT_S_DN` に設定されているユーザ名（メールアドレスの `@` より前の部分）を取り出して、`REMOTE_USER` に設定します。これで認証が成功します。

## なぜこのプラグインを作ったのか

プラグインなしで、以下のようにすれば認証できるのでは？　という疑問はもっともですが、できませんでした（nginx/1.26.3）。

```
map $ssl_client_s_dn $ssl_client_s_dn_cn {
    default "";
    ~CN=(?<CN>[^,@]+) $CN;
}

server {
    ssl_verify_client on;

    location ~ ^/([^/]+)/login$ {
        include fastcgi_params;
        fastcgi_pass unix:/run/trac/$1/trac.sock;
        fastcgi_param SCRIPT_NAME /$1;
        fastcgi_param PATH_INFO /login;
        fastcgi_param REMOTE_USER $ssl_client_s_dn_cn;  # not work
    }
}
```

`$ssl_client_s_dn_cn` での変換は、`location` に正規表現を書くと動きませんでした。`location = /foo/login` のようにして、各プロジェクトごとに個別に書けば動きます（今までこうしていた）。まとめて書くにはどうしたらよいか？　と ChatGPT 相手に試行錯誤していました。こんな経緯です。

1. ChatGPTが「正規表現で書くと動かないので、個別に書くしかない。正規表現はやめて、個別に書く」がベストと回答
2. 私が `$ssl_client_s_dn_cn` は動かないが、`$ssl_client_s_dn` を直接渡すと動くこと気付く
3. 私が「`SSL_CLIENT_S_DN` で渡すから Trac 側で `REMOTE_USER` に読み替えて」と指示
4. ChatGPT がプラグインを出力

途中で諦めてしまったら改善できませんでしたが、ちょっとした気付きで乗り越えられるものです。ChatGPT が Trac プラグインまで出力できるとは驚きです。
