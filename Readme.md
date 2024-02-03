# MyFruitShop ウェブアプリケーション
- 果物屋さんが使用する場合を想定した販売管理サイトです。

## 必要なもの

アプリケーションを実行する前に、以下がインストールされていることを確認してください：

- Docker
- Docker Compose

## コードの実行手順

1. このリポジトリをクローンします：

   ```bash
   git clone https://github.com/PowerShellSh/django-sales-statistics-app.git
   cd myfruitshop

### 1. django project作成
- Djangoディレクトリに移動します：

```sh
cd django
```

- Djangoイメージファイルをビルドします：
```sh
docker image build -t django .
```

- Dockerを起動してログインします：
```sh
docker run -it -p 80:80 -v ./code:/code django bash
```

- 必要な資材（myfruitshopのrequirements.txt）が存在することを確認してexitで抜けます：
```sh
root@XXXXXXX:/code# ls
myfruitshop  requirements.txt
root@XXXXXXX:/code# exit
```
### 2. `docker-compose`でイメージを`build`する
docker-compose.ymlがあるディレクトリまで戻ります：
```sh
cd ../
docker-compose build
```

### 3. コンテナ起動

```sh
docker-compose up -d
```

### 4. Django側のコンテナに入り、runserverコマンド実行
```sh
docker-compose exec app bash
root@XXXXXXX:/code# python myfruitshop/manage.py runserver
```

ウェブブラウザで http://localhost:80 にアクセスします。
### 5.runserver後、うまく接続できない場合

解決方法その１
`Ctrl+C` でサーバーを停止し、次に以下のコマンドで再起動します：

```sh
docker-compose down -v
docker-compose up -d
docker-compose exec app bash
root@XXXXXXX:/code# python myfruitshop/manage.py runserver
```

解決方法その２
どのPythonファイルでもいいので空白を入れて一度保存してみてください。
自動読み込み機能で動作することがあります。

## その他 バックグランド起動方法

```sh
docker-compose up db -d
docker-compose up app -d
```

## 依存パッケージ
- mysqlclient==2.1:
用途: DjangoなどのフレームワークでMySQLデータベースを使用するため導入。
- pytest==7.4.3:
用途: ユニットテストや機能テストのためのPythonのテストフレームワークです。
- pytest-django==4.7.0:
用途: Djangoプロジェクトのためのpytestの拡張機能です


## コードのアピールポイント
- 可読性向上のため、できる限り型ヒントを意識して実装しました。

- 背景にはフルーツっぽさを一面に出したかったのですが、鬱陶しかったらすみません。

# その他の情報
- Django アプリケーションはポート 80 で実行されるように設定されています。
- MySQL はポート 3306 で実行されるように設定されています。
- ログイン情報は以下です
  - - user: root
  - - pass: password
