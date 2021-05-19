## 環境構築

### 設定

[config.tfvars](config.tfvars)に定数が設定されているので、このファイルに必要項目を入力します。

### IAMユーザ登録

terraform用のユーザーを作成します。

https://console.aws.amazon.com/iam/home

### 認証情報登録

AWS-CLIで作成したユーザの認証情報を登録します。

profile名は[main.tf](main.tf)で設定している値にしてください。

```bash
$ aws configure --profile movie
AWS Access Key ID [None]: ******************
AWS Secret Access Key [None]: ****************
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

### GitHub OAuth token作成

CodePipeline構築時にGitHub OAuth tokenが必要になります。

repo全てにチェックを入れて作成してください。

https://github.com/settings/tokens

作成したtokenを環境変数に登録してください。
```bash
$ export GITHUB_TOKEN=**********
```

### tfstate管理用環境構築

tfstateファイルをS3、lock管理をDynamoDBで行うため、
この環境のみ先に構築します。

バケット名、テーブル名は[main.tf](main.tf)の値を使用してください。
```hcl-terraform
bucket         = "movie-app-tfstate-bucket"
dynamodb_table = "movie-lock"
```

```bash
# tfstateファイル管理用のS3バケット作成
$ ./init_terraform_bucket.sh {バケット名} {プロファイル名}

# lock管理用テーブルを作成
$ ./init_terraform_lock_table.sh {テーブル名} {プロファイル名}
```

### terraform初期化

```bash
$ terraform init
```

### 環境構築

```bash
$ terraform apply --var-file=config.tfvars
```

### DBパスワード
DBのパスワードはランダムな文字列を自動的に生成します。

生成されたパスワードは下記のコマンドで確認できます。
```bash
$ terraform show
...
random_string.password:
  id = none
  length = 16
  lower = true
  min_lower = 0
  min_numeric = 0
  min_special = 0
  min_upper = 0
  number = true
  result = G4H0nDwxBjfhWsIB
  special = false
  upper = true
```

### 環境破棄するとき
下記のコマンドで破棄できます。
S3バケットにファイルが残っているとS3バケットの削除ができないので、
事前に削除しておく必要があります。

```bash
$ terraform destroy --var-file=config.tfvars
```
