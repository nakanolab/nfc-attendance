# NFC対応学生証による出席確認ツール

## 設定手順

1. [Anaconda](https://www.anaconda.com/distribution/) をインストール ([Miniconda](https://docs.conda.io/en/latest/miniconda.html) でも可)
1. `conda create -n nfc python=3.7` で仮想環境 `nfc` を作成
1. `conda activate nfc`
1. NFC カードリーダーを PC に接続 (SONY PaSoRi RC-S380/P で稼働確認済み)
1. [nfcpy](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html) の手順に従って、ドライバーと nfcpy をインストール
1. `pip install pygame`
1. `conda install spyder` (統合開発環境 Spyder を使うわけではないが、Qt 関連のライブラリを味よくインストールするため)
1. Git がインストールされているならばターミナルから `git clone https://github.com/nakanolab/nfc-attendance.git` を実行し、本リポジトリをダウンロード (`Download ZIP` したファイルを展開しても可)
1. `cd nfc-attendance`
1. 同じディレクトリに履修者情報ファイル (risyu.csv) を置く (このファイルは「成績報告（学部）」→「履修者情報の取得（全担当科目）」からダウンロード)
1. `log` という名のサブディレクトリを作成する

## 使用方法
1. NFC カードリーダーを PC に接続
1. Anaconda Prompt にて `nfc-attendance` のディレクトリに `cd`
1. `conda activate nfc`
1. `python kitcard_scanner.py` を実行すると GUI が立ち上がる（ターミナルウィンドウにはログメッセージが出力されるので、必要に応じてチェック）
1. 上のプルダウンメニューから出席を取る科目を選択
1. 「受付開始」をクリック（ターミナルにはクラスごとの受講者数が表示される）
1. 学生証をカードリーダーにかざしてもらう
1. 出席確認を終えるには「受付終了」ボタンをクリックする（ターミナルには欠席者一覧が表示される）

## 補足
- ログメッセージはファイル `log/attendance-コースコード-YYYY-MM-DD.log` にも同じ内容が保存される
- GUI を終了した後でプログラムを再実行すると、同じコースコードで同じ日のログファイルが存在していれば、すでに出席が確認された学生の情報は反映される
