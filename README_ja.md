# LJPJTシステム開発テンプレートリポジトリ
文責: 阪本　浩太郎 [@ktr-skmt](https://github.com/ktr-skmt) ( sakamoto.ljpjt@besna.institute )

本リポジトリは、共有タスクLJPJTのシステム開発のためのテンプレートリポジトリである。GitHub上で`Use this template`ボタンをクリックすることで、本リポジトリをコピーして利用することができる。

## 開発環境の構築

[VSCode](https://azure.microsoft.com/ja-jp/products/visual-studio-code/) による開発を**推奨**する。
なお、安定版ではない[VSCode Insiders](https://code.visualstudio.com/insiders/)による開発を非推奨とする。

以下の手順を実行することで開発環境を構築できる．

### インストール

- [VSCode](https://azure.microsoft.com/ja-jp/products/visual-studio-code/)
- [Docker](https://docs.docker.com/get-docker/)

### VSCode の設定

VSCode を起動し，拡張機能の[Visual Studio Code Remote Containers](https://code.visualstudio.com/docs/remote/containers) をインストールする．

[コマンドパレット](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette)を開き，
```
Remote-Containers: Reopen in Container
```
を選択する．

## システムの開発

### ディレクトリ構成の概要
```plaintext
├── dataset  # テストデータの保存先
├── evaluation_results
│   └── development  # 評価結果の保存先
├── scripts
│   └── generate_lockfile.sh  # requirements.txt の生成スクリプト
├── submissions
│   └── development  # ソルバの実行結果の保存先
├── app.ini  # 設定ファイル
├── README.md  # このファイル
├── requirements.in  # 依存パッケージのリスト
├── requirements.txt  # 依存パッケージのバージョン固定リスト
├── schema.yaml  # データスキーマ
└── solver.py  # ソルバの実装
```

### 設定ファイルの準備
チーム名、所属は参加登録時に届け出たものをそれぞれ`app.ini`の`TEAM_NAME`と`AFFILIATION`に設定する（※いずれもハイフン「-」は使用不可）。
システム名を`SYSTEM_NAME`に設定する（※ハイフン「-」は使用不可）。

チームごとに異なるAPIキーを`API_KEY`に設定する。APIキーは参加登録完了時にうけとることができる。

テストデータは運営から指定されたファイル名を`TEST_DATA`に設定する。

`MODE`は`development`または`leaderboard`のいずれかを設定する。`development`モードでは、評価結果をリーダーボードに反映させずに受け取ることができる。`leaderboard`モードでは、受け取った評価結果をリーダーボードに反映させることができる。

```toml
[system]
TEAM_NAME = Team1
AFFILIATION = Affiliation2
SYSTEM_NAME = System3

[settings]
API_KEY = your-api-key-here
TEST_DATA = test001.jsonl
MODE = development
```

### ソルバの実装

#### データスキーマ
ソルバの入力データと出力データは[データスキーマ](schema.yaml)に従う。

#### 入力データ（テストデータ）
入力データは`Tort`のリストである。入力データは`PlaintiffClaim`の`is_accepted`, `DefendantClaim`の`is_accepted`、`Tort`の`court_decision`がすべて`null`になっている。ソルバは`null`の箇所にbool値を埋める処理をする。
```python
test_data: list[Tort] = [
    Tort(
        version="test001.jsonl",
        tort_id="0",
        undisputed_facts=[
            UndisputedFact(
                id="0",
                description="本件報道の報道時間は全体で約三分間であり、原告の動画像と実名の字幕が報道されたのは約六秒間であった。",
            )
        ],
        plaintiff_claims=[
            PlaintiffClaim(
                id="0",
                description="社会的活動に対する評価の資料として前科の公表が是認される余地はない。",
                is_accepted=null,
            )
        ],
        defendant_claims=[
            DefendantClaim(
                id="0",
                description="本件報道は、その報道手段においても、前記の報道目的を達成させる上で、必要最小限の相当な方法であった。",
                is_accepted=null,
            )
        ],
        court_decision=null,
    ),
    Tort(...),
    Tort(...),
    ...
]
```
#### 出力データ
出力データも`Tort`のリストである。ソルバの処理の結果、入力データで`null`だった箇所にbool値が埋められる。
* Tort Predictionタスクへの参加条件は、すべての`Tort`の`court_decision`がbool値で埋められていることである。ひとつでも`null`があるとTort Predictionタスクは不参加となる。
* また、Rationale Extractionタスクへの参加条件は、すべての`PlaintiffClaim`と`DefendantClaim`の`is_accepted`がbool値で埋められていることである。ひとつでも`null`があるとRationale Extractionタスクは不参加となる。

```python
return [
    Tort(
        version="test001.jsonl",
        tort_id="0",
        undisputed_facts=[
            UndisputedFact(
                id="0",
                description="本件報道の報道時間は全体で約三分間であり、原告の動画像と実名の字幕が報道されたのは約六秒間であった。",
            )
        ],
        plaintiff_claims=[
            PlaintiffClaim(
                id="0",
                description="社会的活動に対する評価の資料として前科の公表が是認される余地はない。",
                is_accepted=False,
            )
        ],
        defendant_claims=[
            DefendantClaim(
                id="0",
                description="本件報道は、その報道手段においても、前記の報道目的を達成させる上で、必要最小限の相当な方法であった。",
                is_accepted=True,
            )
        ],
        court_decision=False,
    ),
    Tort(...),
    Tort(...),
    ...
]
```

#### アルゴリズムの作成
Tort PredictionタスクとRationale Extractionタスクのそれぞれの目的は、タスクの紹介ページを参照すること。
ここでは実装に関して、上記の入力データ・出力データの説明の通り、入力データにある`null`をbool値で埋めるアルゴリズムを作成する。アルゴリズムは、プロジェクトルートにある`solver.py`の`solve`関数に実装する。`solve`関数の中身は自由に変更できる。
```python
# TODO: Write your own algorithm
def solve(test_data: list[Tort]) -> list[Tort]:
    system_result: list[Tort] = [algorithm(tort) for tort in test_data]
    return system_result
```

### ソルバの実行

VSCode の Remote Container のターミナルで次のコマンドを実行する。これにより、`app.ini`に設定された`TEST_DATA`のファイル名のテストデータがダウンロードされて読み込まれ、`solve`関数が実行される。評価結果は標準出力に出力される。
```bash
python -m solver
```

#### コールドスタートに起因するエラーメッセージ

下記のようなエラーメッセージが標準出力に出力された場合は、約1分後に再実行するとエラーメッセージが解消され、評価結果が標準出力に出力される（評価システムのコールドスタートによるもの）。

```bash
$ python -m solver
EVALUATION RESULT: evaluation_results/development/test001_your-team-name-here_your-affiliation-here_your-system-name-here_20241213185310.jsonl
---
Tort prediction task
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/workspaces/LJPJT-dev-template/solver.py", line 48, in <module>
    main(solve)
  File "/workspaces/LJPJT-dev-template/src/utils.py", line 152, in main
    pipeline(submission)
  File "/workspaces/LJPJT-dev-template/src/utils.py", line 143, in pipeline
    filename_with_timestamp, evaluation_result = evaluate(filename)
                                                 ^^^^^^^^^^^^^^^^^^
  File "/workspaces/LJPJT-dev-template/src/utils.py", line 97, in evaluate
    print(f"Accuracy: \t{evaluation_result['tort_prediction_task']['accuracy']}")
                         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

### ログの確認
ログはソルバの実行結果と評価結果の2つがある。
#### ソルバの実行結果
`solve`関数の実行結果は`submissions/{MODE}/`（`submissions/development/`または`submissions/leaderboard/`）に保存される。ファイル名は`app.ini`に設定された`TEST_DATA`と`SYSTEM_NAME`と`AFFILIATION`と`TEAM_NAME`とタイムスタンプによって決まる。`TEST_DATA`が`test.jsonl`の場合、ファイル名は`test_{SYSTEM_NAME}_{AFFILIATION}_{TEAM_NAME}_{タイムスタンプ}.jsonl`である。ファイルの中身は`solve`関数の実行結果である。

#### 評価結果
評価結果は、`evaluation_results/{MODE}/`（`evaluation_results/development/`または`evaluation_results/leaderboard/`）に保存される。ファイル名は`app.ini`に設定された`TEST_DATA`と`SYSTEM_NAME`と`AFFILIATION`と`TEAM_NAME`とタイムスタンプによって決まる。`TEST_DATA`が`test001.jsonl`の場合、ファイル名は`test001_{SYSTEM_NAME}_{AFFILIATION}_{TEAM_NAME}_{タイムスタンプ}.jsonl`である。ファイルの中身は`solve`関数の実行結果に対する評価結果である。

## Python の依存パッケージの管理

### requirements.in の更新

- 必ず手動で更新すること
- 直接依存しているパッケージのみを書くこと
- [PyPI](https://pypi.org/)で利用可能なパッケージのみを書くこと

例) flake8 の バージョンを 1.2.X にしたい場合: `flake8~=1.2.3`
参考： https://www.python.org/dev/peps/pep-0440/#version-specifiers

以下のコマンドによる更新は禁止
```bash
pip freeze > requirements.in
pip freeze >> requirements.in
```

### requirement.txt の更新

以下のコマンドを実行
```bash
rm requirements.txt
./scripts/generate_lockfile.sh
```
