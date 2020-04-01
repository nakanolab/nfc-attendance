# NFC対応学生証による出席確認ツール

## 設定手順

1. [Anaconda](https://www.anaconda.com/distribution/) をインストール
1. `conda create -n nfc python=3.7` で仮想環境 `nfc` を作成
1. `conda activate nfc`
1. NFC カードリーダーを PC に接続 (SONY PaSoRi RC-S380/P で稼働確認済み)
1. [nfcpy](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html) の手順に従って、ドライバーと nfcpy をインストール
1. `pip install pygame`
1. `conda install spyder` (統合開発環境 Spyder を使うわけではないが、Qt 関連のライブラリを後顧の憂いなくインストールするため)
1. Git がインストールされているならばターミナルから `git clone https://github.com/nakanolab/nfc-attendance.git` を実行し、本リポジトリをダウンロード (`Download ZIP` したファイルを展開しても可)
1. `cd nfc-attendance`
1. 同じディレクトリに履修者情報ファイル (risyu.csv) を置く
1. `log` という名のサブディレクトリを作成する
1. `python kitcard_scanner.py` で実行
