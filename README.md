# TacspeakJP  

**日本語音声入力コマンディングツール**  


## はじめに | Introduction  

「TacspeakJP」は、[jwebmeister](https://github.com/jwebmeister)氏制作のゲーム向け音声コマンディングツール「[Tacspeak](https://github.com/jwebmeister/tacspeak)」を、日本語音声入力に対応するように改修したものです。  
'TacspeakJP' is modified edition of 'Tacspeak' tool created by jwebmeister. It provide Japanese language speach recognition.  

サンプルとして、Ready or Notで使用している様子がこちらで見れます。  
You can watch a demo-play video below.

[![Ready or Notで使用するデモプレイYoutubeビデオ](http://img.youtube.com/vi/orJuWn9rZoc/maxresdefault.jpg)](https://youtu.be/orJuWn9rZoc)  

オリジナルのTacspeakは、カスタマイズされた [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly) 音声認識フレームワークと、 動的デコードを実現する [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar/) エンジンによって、優れた認識精度や応答性を実現しています。  
一方で、Kaldiエンジンを使用する都合上、英語での音声認識しか利用できないという制限があります。  

TacspeakJPは、日本語でTacspeakを使用できることを目標とし、使用する音声認識エンジンを'Kaldi'から'WSR / SAPI 5' (Windows Speech Recognition / Microsoft’s Speech API version 5)へと変更する改修を行いました。  
'JP'と銘打っていますが、理論上、Windows音声認識で利用できる言語であればgrammarを用意すれば日本語以外でも動作可能なはずです。  

---

Original Tacspeak provides excellent response and high-accuracy recognition powered by modified Dragonfly and Kaldi Active Grammar.  
But that only use for English recognition due to limitation of Kaldi engine.  

TacspeakJP aim to use the Tacspeak with Japanese speeching. It solved by using 'WSR / SAPI 5' SR engine insteed of 'Kaldi'.  
I named 'JP' but, I guess it can works for any other languages what is supported by Windows Speech Recognition, with making grammar.  


## オリジナル版との違い | Differences from original Tacspeak  

- 改変されていない [Dragonfly](https://github.com/dictation-toolbox/dragonfly) を使用  
- 'Kaldi'エンジンの代わりに'WSR / SAPI 5'エンジンを使用  
- 日本語用に編集したReady or Not向けgrammarを同梱  
- エンジン変更により、次の機能は使用できません。  
    - 発話中の割込み認識（エールの優先認識）
    - ~~実行中のキー操作による認識中断／再開（常にオン）~~  
      →v2024.2.3 から実装しました。
    - その他 user_setting.py の KALDI_ENGINE_SETTINGS で設定されていた機能
- 認識精度はWindows音声認識の精度に依存します。これはトレーニングによって向上されます。  
- Windows音声認識の'音声辞書'機能により、特定の単語の認識精度を高めることができます。  

---

- Running on the original (not modified) Dragonfly.
- Running on the 'WSR / SAPI 5' engine insteed 'Kaldi'
- Includes grammar edited for Japanese language, to use on Ready or Not.
- Below features is omitted due to change the engine.
  - Mid-utterance recognition (for yell)
  - ~~Toggle of recognition on/off (always on)~~  
    -> added from v2024.2.3
  - and the other options in KALDI_ENGINE_SETTINGS on user_setting.py
- Accuracy of recognition depends on Windows Speech Recognition. It can be improved by training.
- And also can improve recognition of specific words, by using 'Speech Dictionary' within WSR.

## 要件 | Requirements  

- OS: Windows 10/11, 64-bit （Windows 11での動作は未確認 | Windows 11 is not tested yet）  
- Microsoft Visual C++ 再頒布可能パッケージ | Microsoft Visual C++ Redistributable Package  
- Windows音声認識のセットアップ・設定 | Setup for Windows Speech Recognition  


## 導入 | Installation (in Japanese only)  

### ツールのダウンロードとインストール  
1. [Microsoft Visual C++ 再頒布可能パッケージ](https://aka.ms/vs/17/release/vc_redist.x64.exe) をダウンロードし、インストールする  
2. [TacspeakJPの最新バージョン](https://github.com/Domtaro/tacspeakJP/releases/latest/) をダウンロードする  
3. ダウンロードした.zipを任意の場所に解凍・配置する。  

### Windows音声認識のセットアップ  
1. 次のいずれかでコントロールパネルを開く  
    - Win+R → "control" と入力してEnter  
    - スタート → Windowsシステムツール から開く  
2. 「音声認識」をクリック（表示されない場合は 表示方法を"小さいアイコン"に変更）  
3. 「音声認識の開始」をクリック  
    - 初回であればセットアップが始まるので、画面の指示に従う。  
4. （任意・推奨）「コンピューターをトレーニングして認識精度を向上させる」をクリック  
    - 何回も実行でき、毎回違う内容を読み上げさせられる。２回ほどやっておくとよいと思われる。  
5. （任意・推奨）「音声辞書」に単語を登録する  
    - 「音声認識の開始」をクリックして音声認識のGUIを表示  
    - 画面上部のマイクアイコン または タスクバーのマイクアイコンを右クリック → 音声辞書を開く  
    - "おぷてぃわんど"や"はじょうつい"などの特別な言葉を登録する（後述のgrammar設定のために、ひらがなで登録することを推奨します）。  
    - 「完了時に発音を録音する」をチェックして自分の発音を登録することで、さらに認識精度を高められる。  
6. （任意）「高度な音声オプション」をクリック  
    - 「音声認識」タブの下部、「マイク」-「詳細設定」で使用するマイクを指定できる。後述のツール側オプションでも指定可能。  

### ツールのセットアップ・実行  
1. `user_settings.py` の内容を確認・編集する  
    - `WSR_AUDIO_SOURCE_INDEX` で使用するマイクを指定できる。どのマイクが何番のインデックスかは、 `tacspeakJP.exe --get_audio_sources` を実行することで確認できる。  
      - v2024.2.2（v0.2.0.1-jpの次）から、デフォルトでコメントアウト（指定なし）にしています。  
      - 指定されなかった場合は、何も設定を変えません。（Windows音声認識の設定で指定したマイクのまま）
    - `PTT_MODE` でプッシュ・トゥ・トーク（特定キー押下中のみ発話検出）などの機能を有効にできる。  
      以下のモードがある。
      - 0 - 常にON（デフォルト）
      - 1 - キー押下のたびにON/OFF切替（開始時ON）
      - 2 - キー押下のたびにON/OFF切替（開始時OFF）
      - 3 - キーを押している間だけON（プッシュ・トゥ・トーク）
      - 4 - キーを押している間だけOFF（プッシュ・トゥ・ミュート）
    - `PTT_KEY` で、上記 `PTT_MODE` に使用するキーを指定できる。（デフォルト`"left shift"`）  
      キーの名前は、 `tacspeakJP.exe --get_key_name` を実行し、キーを押すことで確認できる。  
      設定にあたって以下の点に注意すること。  
      - マウスのボタンの場合、キー名の先頭に `"mouse_"` をつける。（例：`"mouse_right"`, `"mouse_x2"`）  
      - テンキーのキーの場合、キー名の先頭に `"num "` をつける。（例：`"num 0"`, `"num enter"`）  
        ※つけなかった場合、キーボード本配列のキーでも反応してしまう。  
      - TacspeakJP自体のキー入力にも反応するので考慮すること。  
        例：`"mouse_middle"` を設定し、命令開始のキーも`"mouse_middle"`だと、命令発動時にPTTも押されてしまう
      - マウスのボタンは、連続で押下したときに反応しづらいため非推奨。
2. grammar（ルール） の内容を確認・編集する（Ready or Notの場合、デフォルト用として `tacspeak/grammar/_readyornot_jp.py` を同梱）  
   ### よく分からない場合は、いったん触らずにそのまま使ってみてください。  
    - `grammar_context` にフックするゲームのexeのパス（の一部）を指定する（大文字／小文字区別なし）。  
    - `inifile_name` に入っている、`Input.ini` （ReadyOrNotのキー設定ファイル）のパスが正しいことを確認する。  
      - v2024.2.2（v0.2.0.1-jpの次）から、ここで指定されたファイルから自動でキー設定を拾う機能を追加しました。  
      - 動作するためには、もしかしたらTacspeakJP.exeを管理者権限で実行する必要があるかもしれません。
      - うまく自動設定されないときや、手動で変更したい場合は、`ingame_key_bindings.update()` の中身を編集して指定してください。  
      - また、デバッグモードを有効にして起動すると、最初の方に`-- Ready or Not In-Game keybindings --`の行に挟まれる形で、ツールが取得したゲーム内キー設定の一覧を見ることができます。デバッグモードの使い方は「トラブルシューティング」の項目を参照してください。  
    - `map_` で始まる変数に、追加／変更したい言葉があれば反映する。（複数個所にあります）  
    - `spec` という変数に、追加／変更したい文法（言い回し）があれば反映する。（複数個所にあります）  
    - `YellFreeze` クラスに、エール（シャウト、降伏呼びかけ）の言葉を好みに応じて追加／変更する。（１箇所だけにあります）  
    - そのほか、[Dragonflyのドキュメント](https://dragonfly2.readthedocs.io/en/latest/rules.html) などを参考に、自分用のルールを追加できる。  
3. `tacspeak.exe` を実行する（ツールとゲームの起動はどちらが先でも構いません。）  
4. 「ビギニングループ」という音声が聞こえて、"Ready to listen..." の表示で待機したら起動しています。ゲームのウィンドウをアクティブにして試してみてください。  
    - マイクに喋ると、認識された音声が文字で表示されます。誤認識のチェックなどができます  
    - 起動時の「ビギニングループ」の音声は、Dragonflyにハードコーディングされた部分で再生されているので設定等でオフにはできません。音量ミキサーでアプリの音量を0にすれば聞こえなくなるかもしれません  
    - デバッグモードを使えば、ゲームを起動せずにテストすることもできます。詳細は「トラブルシューティング」の項目を参照してください。  
5. 使い終わったら、Ctrl+C または 右上×で終了する  

### **【注意！】**  
- `./tacspeak/user_settings.py` と `./tacspeak/grammar/_*.py` は自動で読み込まれます。  
信頼できない第三者のファイルが混入し実行されないように注意してください。  
- TacspeakJP（および本家Tacspeak）は、キーボード入力やマウス入力をTacspeakJPが代行入力することによって動作します。  
  ### このような動作は、ゲーム内のチート検出機能や、ゲームと一緒に動作するチート検出ソフトウェアにチート使用として検出される可能性があります。  
  そのため、TacspeakJPをそのようなチート検出の仕組みを持つゲームや、対人対戦のあるゲーム、オンラインランキング・スコアボードのあるゲーム、ランクマッチのあるゲーム、そのほか他のユーザーやゲームサービス提供者に不正行為と誤認されうる環境で使用することは推奨しません。  
  また当然、ゲームルール上禁止されている不正行為を意図的に行うために使用することは許されません。  
  ### TacspeakJPの制作者およびプロジェクト管理主体は、TacspeakJPを使用することによって発生した、上記のチート検出を含むあらゆる損害（アカウント停止など）について一切責任を負いません。  
  ※2024年2月時点で、実際にTacspeak（およびJP）の使用がチートとして検出された事例は報告されていません。

## 基本的な使い方（Ready or Notで説明） | Basic usage (in Japanese only)  

- プッシュ・トゥ・トークを有効にしている場合、`Mic ON` と表示されている状態のあいだ発話を受け付けます。  
- 言葉を喋り、コマンドが成立すると、「current team go stack up split」のように認識されたコマンドが表示され、キー入力が行われます。  
- 使えるアクション（コマンド）と、それに対応する言葉は、デバッグモードを使って確認できます。  
  ### 以下の手順で確認できるほか、あらかじめ付属の「Ready or Not用デフォルトgrammar」で出力したものを `sample_grammar_readyornot.txt` として同梱しています。  
  1. 「トラブルシューティング」の項目を参考に、デバッグモードを有効にしてTacspeakJPを起動してください。
  2. `Tacspeak.exe` と同じフォルダに、`.debug_grammar_readyornot.txt` というファイルが生成されます。
  3. その中身がアクション（コマンド）と、それを発動するための言葉のリストになっています。任意のテキストエディタ―などで開いてみて下さい。
  4. 見かたは次の通りです。下の画像も合わせて見てください。  
      - ファイルの先頭に、「Rule:～」で始まる行が複数あると思います。これがすなわちアクション（コマンド）の一覧です。  
        例えば「ExecuteOrCancelHeldOrder(ExecuteOrCancelHeldOrder)」は、ホールド状態の命令に対して、「実行」あるいは「キャンセル」を指示するアクションに該当します。  
      - それより下は、次の構造の記述が並んでいきます。  
        \---①アクション名---  
        ②全パターンを展開したもの  
        \---  
        ③基本構文  
        ④変数１  
        　変数２  
        　：  
        \------------  
      - 主に見てほしいのは③です。  
        「③を言うと①が発動する。さらに各単語などには④のバリエーションがある」  
        というイメージです。  
  ![tacspeakJP_commandList_sample_3_2](https://github.com/Domtaro/tacspeakJP/assets/143232038/937ec54f-96e2-49d4-b4be-be74263de991)  
- grammar（ルール）を自分でカスタマイズしている場合でも、その内容で一覧が生成されるはずです。  
- もう少し具体的な例（付属の `_readyornot_jp.py` の内容）についても以下に示します。  
### コマンドのサンプル  
- いけ → デフォルト命令（いわゆるzキー）
- うごくな → Freeze!
- て を あげろ → Freeze!
- しゅうごう しろ → Fall in
- にれつ で うしろ に つけ → Fall in, double file
- だいやもんど たいけい で さいへんせい → Fall in, diamond formation
- そこ に いけ → Move to there
- そこ を みて いろ → Cover there
- はいち に つけ → Stack up split
- みぎ に てんかい → Stack up on the right
- すきゃん しろ → Scan the door
- みらー を つかえ → Use the mirror
- ぴっきんぐ しろ → Pick the door
- そこを あけろ → Open the door
- そこを とじろ → Close the door
- かばー しろ → Cover the door
- ぶろっく しろ → Use the wedge
- うぇっじ を つかえ → Use the wedge
- あけて とつにゅう しろ → Open and clear
- しょっとがん で あけて ふらっしゅ で くりあ しろ → Shotgun, flash and clear
- あけたら がす を なげて せいあつ しろ → Leader, CS and clear
- あいず で はいれ、 くりありんぐ しろ → On my mark, move in and clear
- いけ いけ いけ → Execute
- がす を つかえ → Deploy CS
- うしろ を むけ → You, Turn around
- こっち に こい → You, Move my position
- そこ で とまれ → You, stop
- こうそく しろ → restrain
- あいつ に てーざー を つかえ → Deploy teaser
- そうさく しろ → Search and secure


## トラブルシューティング | Troubleshooting (in Japanese only)  

- 以下の内容のほか、 [トラブル調査チャート](https://github.com/Domtaro/tacspeakJP/discussions/14) の内容も参考にしてみてください。
- 言葉がうまく認識されない  
    - Windows音声認識のトレーニングを実行してみてください。  
    - 一般的でない単語（ミラーガンなど）については音声辞書に登録してください。  
    - 「ひらけ　ふらっしゅで　くりあ　しろ」のように、言葉の区切りに意識的に間を持たせてみてください。  
    - 普段よりはっきり発音することを意識してみて下さい。  
    - マイクの感度が高い場合、周囲の雑音が影響することも考えられます。可能な限りマイク感度を下げ、空調などの雑音を減らしてください。  
- 言葉は正しいのにコマンドが発動しない  
    - 正しい位置をポイントしていることを確認してください。（ドアに対するコマンドならドアをポイントしていること）  
      ツール側では、「ゲーム内で今どこを見ているか」を判別しません。  
    - 同じ言葉の並びを複数のコマンドに設定するとうまくいかない場合があります。  
      例えば、単に「とまれ」とだけ言うと、チームへの停止命令か、動いている民間人への命令か特定できません。  
      どちらかのコマンドに、「そこで とまれ」のように言葉を加えてたりして区別できるようにしてみて下さい。  
    - 他にも例えば、見かけ上は同じ「しゅうごう」でも、どうやら内部的に違いがあってコマンド発動に影響する場合があるようです。  
      WSRの仕様を把握しきれていないため詳細は不明です。  
      「しゅうごう しろ」のように他の言葉と一緒に言うと改善する場合があります。  
    - 実際にキー入力で実行できないコマンドは動作しません  
      例えば、一部のドアで「左にスタック」が無効になっていたりする場合など  
    - `./tacspeak/user_settings.py` で `DEBUG_MODE = True` を設定して起動することで、ツール単体で動作確認ができます。  
      ゲームを起動してアクティブにしている必要はなく、キー入力も実際には行われません。  
      発音の認識結果のほかに、エミュレートされたキーも表示されます。  
- 認識されるのが遅い  
    - Kaldiエンジンに比べると反応が遅いかもしれません。現状、Windows音声認識を使うことによる限界があります。  
    - エール（手を挙げろ！など）のように素早く発動することが重要なコマンドは、そもそも不向きです。  
      - 現実で言葉を言い終わってからようやくゲーム内でコマンドを発動するという仕組み上、発動できる速さに限界があります。  
      - これはKaldi Active Grammarで応答性を向上させた、本家Tacspeakでさえも同様です。  
      - 咄嗟のエールなどは最初の１回は手動でキー入力で出すことをお勧めします。  
- そのほかの制限  
    - 視線の手前と奥に二つドアがある場合、どちらのドアへの指示かを決める入力が先頭に追加されますが、付属のgrammarではそのパターンに対応していません。  
      しかし、あなたの手で改良すれば対応可能かもしれません。  
      本家Tacspeakでも [その件に関する議論](https://github.com/jwebmeister/tacspeak/issues/15) がありました（未解決）。参考にしてみてください。  


## （開発者向け）ビルド方法 | How to build (for deveropper, in Japanese only)  

編集中です。以下はメモ。  

- Python 3.11 が必須（3.12不可）  
- `Freeze.txt` の内容が前提パッケージ（`requirements.txt` と同一）  
- win32comのためにVisual Studio（コミュニティ版で可）のインストールが必要  
    - Python 開発 - Python ネイティブ開発ツール をチェック  
      他にもあったかもしれないけど忘れてしまった  
- ビルド手順  
    - `setup.py` のディレクトリでpowershellを開く  
    - `py -3.11 -m venv "./.venv"`  
    - `./.venv/Scripts/activate`  
    - (.venv)に切り替わっていること  
    - `py -m pip install -r requirements.txt` （前提パッケージに変更が無ければ２回目以降不要）  
    - `py setup.py build`  
- ビルド後、起動しようとすると'CLSIDToClassMap'に関するエラーが出てアベンドすることがあった。
  - %TEMP%\gen_py 下を全削除することで解消した。
  - 正確な原因は不明（世の中的には知られた事象のようではある）
  - 根本対策は未定（発生原理を理解していないため）

## モチベーション | Motivation  

'Tacspeak'は、他にはないゲーム体験を提供してくれる素晴らしいツールです。しかし日本ではネイティブな英語発音に親しみがない人も少なくなく、言語の壁で対象ユーザーが限られてしまうことをとても残念に感じました。  
そこで、より多くのユーザーにTacspeakの魅力を届けたいという思いから、日本語入力を取り扱うことができないか検討してみました。  

結果として、DragonflyがWSRをハンドルできることが分かったため、比較的少ない変更で実装できました。  
元々DragonflyやTacspeak自体がシンプルかつコンパクトな実装であったことにも助けられました。  

改めて、オリジナルTacspeak制作者のjwebmeister氏に感謝と敬意を表します。  

---

'Tacspeak' is an amazing tool that provides a unique gaming experience. However, in Japan, many people does not familiarized them with native English pronaunciation.  
Therefore, I tryed whether it would be possible to handle Japanese speech input to bring the experiences of Tacspeak to many users as possible.  

As a result, I found out that Dragonfly can handle WSR, so I was able to made it with few changes.  
It also helped that Dragonfly and Tacspeak themselves has simple and compact codes.  

I would like to express my thanks and respect to jwebmeister, the author of the original Tacspeak.  


## ロードマップ | Roadmap  

- まず、このプロジェクトは個人の趣味です。サポート内容や期間については一切お約束できないことをご了承ください。  
- 今のところ、プログラム本体にこれ以上変更を加える具体的な計画はありません。  
- あるとすれば、Ready or Not向け付属grammarの改良、またはオリジナルTacspeakの変更で適用すべきものの反映などを想定しています。  
- 何か機能を思いついたら実装するかもしれません。  
- その他、使い方などの問い合わせに適宜対応します。  
- このプロジェクトはオープンソースです。ライセンスの範囲内で誰でも自由に改変できます。私への伺い立て等も不要です。  

---

- This project is personal. I can not guarantee any support, but I would to help you as I can if you need.
- I have no detailed plan to change any more the main programs for now.
- If some changes happen on original Tacspeak, I would check if it need to be applied to my project. And also I may update the grammar contained.
- I may add something new if I got ideas.
- I will reply to your questions/comments as I can.
- This project is open source. Anyone can modify that within license below. It's no need to notify me.


## 制作者 | Author  

- Domtaro ([@Domtaro](https://github.com/Domtaro))  
- Joshua Webb ([@jwebmeister](https://github.com/jwebmeister)) - The original Tacspeak  


## ライセンス | License  

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0-or-later). See the [LICENSE.txt file](LICENSE.txt) for details.  


## 謝辞 | Acknowledgments  

- Based upon and may include code from "Dragonfly" [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly), under the LGPL-3.0 license.  
- Based upon and may include code from "Tacspeak" [jwebmeister/tacspeak](https://github.com/jwebmeister/tacspeak), under the AGPL-3.0 license.  
