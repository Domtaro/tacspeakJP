# TacspeakJP  

**日本語音声入力コマンディングツール**  


## はじめに | Introduction  

「TacspeakJP」は、jwebmeister氏制作のゲーム向け音声コマンディングツール「Tacspeak」を、日本語音声入力に対応するように改修したものです。  

'TacspeakJP' is modified edition of 'Tacspeak' tool created by jwebmeister. It provide Japanese language speach recognition.  
<!--
[![Ready or Notで使用するデモプレイ](https://img.youtube.com/vi/)](https://youtu.be/)
-->
---

オリジナルのTacspeakは、カスタマイズされた [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly) 音声認識フレームワークと、 動的デコードを実現する [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar/) エンジンによって、優れた認識精度や応答性を実現しています。  
一方で、Kaldiエンジンを使用する都合上、英語での音声認識しか利用できないという制限があります。  

TacspeakJPは、日本語でTacspeakを使用できることを目標とし、使用する音声認識エンジンを'Kaldi'から'WSR / SAPI 5' (Windows Speech Recognition / Microsoft’s Speech API version 5)へと変更する改修を行いました。  
'JP'と銘打っていますが、理論上、Windows音声認識で利用できる言語であればgrammarを用意すれば日本語以外でも動作可能なはずです。  

Original Tacspeak provides excellent response and high-accuracy recognition powered by modified Dragonfly and Kaldi Active Grammar.  
But that only use for English recognition due to limitation of Kaldi engine.  

TacspeakJP aim to use the Tackspeak with Japanese speeching. It solved by using 'WSR / SAPI 5' SR engine insteed of 'Kaldi'.  
I named 'JP' but, I guess it can works for any other languages what is supported by Windows Speech Recognition, with making grammar.  


## オリジナル版との違い | Differences from original Tackspeak  

- 改変されていない [Dragonfly](https://github.com/dictation-toolbox/dragonfly) を使用  
  Running on the original (not modified) Dragonfly.  
- 'Kaldi'エンジンの代わりに'WSR / SAPI 5'エンジンを使用  
  Running on the 'WSR / SAPI 5' engine insteed 'Kaldi'  
- 日本語用に編集したReady or Not向けgrammarを同梱  
  Includes grammar edited for Japanese language, to use on Ready or Not.  
- エンジン変更により、次の機能は使用できません。  
  Below features is omitted due to change the engine.  
    - 発話中の割込み認識（エールの優先認識） | Mid-utterance recognition (for yell)  
    - 実行中のキー操作による認識中断／再開（常にオン） | Toggle of recognition on/off (always on)  
    - その他 user_setting.py の KALDI_ENGINE_SETTINGS で設定されていた機能 | and the other options in KALDI_ENGINE_SETTINGS on user_setting.py  
- 認識精度はWindows音声認識の精度に依存します。これはトレーニングによって向上されます。  
  Accuracy of recognition depends on Windows Speech Recognition. It can be improved by training.  
- Windows音声認識の'音声辞書'機能により、特定の単語の認識精度を高めることができます。  
  And also can improve recognition of specific words, by using 'Speech Dictionary' within WSR.  


## 要件 | Requirements  

- OS: Windows 10/11, 64-bit （Windows 11での動作は未確認 | Windows 11 is not tested yet）  
- Microsoft Visual C++ 再頒布可能パッケージ | Microsoft Visual C++ Redistributable Package  
- Windows音声認識のセットアップ・設定 | Setup for Windows Speech Recognition  


## 導入 | Installation (in Japanese only)  

### ツールのダウンロードとインストール  
1. [Microsoft Visual C++ 再頒布可能パッケージ](https://aka.ms/vs/17/release/vc_redist.x64.exe) をダウンロードし、インストールする  
2. [TackspeakJPの最新バージョン](https://github.com/Domtaro/tacspeakJP/releases/latest/) をダウンロードする  
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
    - "おぷてぃわんど"や"はじょうつい"などの特別な単語を登録する（後述のgrammar設定のために、ひらがなで登録することを推奨します）  
    - 「完了時に発音を録音する」をチェックして自分の発音を登録することで、さらに認識精度を高められる。  
6. （任意）「高度な音声オプション」をクリック  
    - 「音声認識」タブの下部、「マイク」-「詳細設定」で使用するマイクを指定できる。後述のツール側オプションでも指定可能。  

### ツールのセットアップ・実行  
1. `user_settings.py` の内容を確認・編集する  
    - WSR_AUDIO_SOURCE_INDEX で使用するマイクを指定できる。どのマイクが何番のインデックスかは、 `tacspeakJP.exe --get_audio_sources` を実行することで確認できる  
2. grammar の内容を確認・編集する（Ready or Notの場合、デフォルト用として `tacspeak/grammar/_readyornot_jp.py` を同梱）  
    - `grammar_context` にフックするゲームのexeのパス（の一部）を指定する（case-insensitive）  
    - `ingame_key_bindings` にゲームの自分のキーバインド設定を反映する  
    - `map_` で始まる変数に、追加／変更したい言葉があれば反映する  
    - `spec` という変数に、追加／変更したい文法（言い回し）があれば反映する  
    - `YellFreeze` クラスに、エール（シャウト、降伏呼びかけ）の言葉を好みに応じて追加／変更する  
    - そのほか、[Dragonflyのドキュメント](https://dragonfly2.readthedocs.io/en/latest/rules.html) などを参考に、自分用のルールを追加できる  
3. `tacspeak.exe` を実行する（ツールとゲームの起動はどちらが先でも構いません。）  
4. 「ビギニングループ」という音声が聞こえて、"Ready to listen..." の表示で待機したら起動しています。ゲームを起動して使用してみてください  
    - マイクに喋ると、認識された音声が文字で表示されます。誤認識のチェックなどができます  
    - 起動時の「ビギニングループ」の音声は、Dragonfly標準部分で再生されているので設定等でオフにはできません。音量ミキサーでアプリの音量を0にすれば聞こえなくなるかもしれません  
5. Ctrl+C または 右上×で終了する  

***注意！***  
`./tacspeak/user_settings.py` と `./tacspeak/grammar/_*.py` は自動で読み込まれます。  
信頼できない第三者のファイルが混入し実行されないように注意してください。  


## 基本的な使い方（Ready or Notで説明） | Basic usage (in Japanese only)  

- 言葉をしゃべり、コマンドが成立した場合、「current team go stack up split」のように認識されたコマンドが表示され、キー入力が行われます。  
- 言い回しの例（付属の `_readyornot_jp.py` の内容）を以下に示します。  
### コマンドのサンプル  
- うごくな → Freeze!
- て を あげろ → Freeze!
- しゅうごう しろ → Fall in
- にれつ で うしろ に つけ → Fall in, double file
- だいやもんど たいけい で さいへんせい → Fall in, diamond formation
- はいち に つけ → Stack up split
- みぎ に てんかい → Stack up on the right
- すきゃん しろ → Scan the door
- みらー を つかえ → Use the mirror
- ぴっきんぐ しろ → Pick the door
- ぶろっく しろ → Use the wedge
- あけて とつにゅう しろ → Open and clear
- しょっとがん で あけて ふらっしゅ で くりあ しろ → Shotgun, flash and clear
- あけたら がす を なげて せいあつ しろ → Leader, CS and clear
- あいず で はいれ、 くりありんぐ しろ → On my mark, move in and clear
- いけ いけ いけ → Execute
- がす を つかえ → Deploy CS
- うしろ を むけ → You, Turn around
- こっち に こい → You, Move my position
- そこ で とまれ → You, stop
-  こうそく しろ → restrain
-  あいつ に てーざー を つかえ → Deploy teaser
-  そうさく しろ → Search and secure


## トラブルシューティング | Troubleshooting (in Japanese only)  

- 言葉がうまく認識されない  
    - Windows音声認識のトレーニングを実行してみてください。  
    - 一般的でない単語（ミラーガンなど）については音声辞書に登録してください。  
    - 「ひらけ　ふらっしゅで　くりあ　しろ」のように、言葉の区切りに意識的に間を持たせてみてください。  
    - 普段よりはっきり発音することを意識してみて下さい。  
    - マイクの感度が高い場合、周囲の雑音が影響することも考えられます。可能な限りマイク感度を下げ、空調などの雑音を減らしてください。  
- 言葉は正しいのにコマンドが発動しない  
    - 正しい位置をポイントしていることを確認してください。（ドアのコマンドならドアをポイントしていること）  
      ツール側では、「いまどこを見ているか」を判別しません。  
    - 複数の場面に同じ言葉の並びを設定するとうまくいかない場合があります。  
      例えば、単に「とまれ」とだけ言うと、チームへの停止命令か、動いている民間人への命令か特定できません。  
      どちらかのコマンドに、「そこで とまれ」のように言葉を加えてたりして区別できるようにしてみて下さい。  
    - 見かけ上は同じ「しゅうごう」でも、どうやら内部的に違いがあってコマンド発動に影響する場合があるようです。  
      WSRの仕様を把握しきれていないため詳細不明です。  
      「しゅうごう しろ」のように他の言葉と一緒に言うと改善する場合があります。  
    - 実際にキー入力で実行できないコマンドは動作しません  
      例えば、一部のドアで「左にスタック」が無効になっていたりするなど  
- 認識されるのが遅い  
    - Kaldiエンジンに比べると反応が遅いかもしれません。現状、Windows音声認識を使うことによる限界があります。  
    - エール（手を挙げろ！など）のように素早く発動することが重要なコマンドは、そもそも不向きです。  
      現実で言葉を言い終わってからコマンドを発動するという仕組み上、発動できる早さに限界があります。  
      これはKaldi Active Grammarで応答性を増した本家Tacspeakであっても同様です。  
      咄嗟のエールなどは最初の１回はキー入力で出すことをお勧めします。  
- そのほかの制限  
    - 視線の手前と奥に二つドアがある場合、どちらのドアへの指示かの選択が最初に追加されますが、付属のgrammarではそのパターンに対応していません。  
      あなたの手で改良すれば対応可能かもしれません。  
      本家Tacspeakでその話題の議論があったはずなので参考にするとよいかもしれません。  


## （開発者向け）ビルド方法 | How to build (for deveropper, in Japanese only)  

編集中です。以下はメモ。  

- Python 3.11 が必須（3.12不可）  
- freeze.txt の内容が前提パッケージ  
- win32comのためにVisual Studio（コミュニティ版で可）のインストールが必要  
    - Python 開発 - Python ネイティブ開発ツール をチェック  
      他にもあったかもしれないけど忘れた  
- ビルド手順  
    - `setup.py` のディレクトリでpowershellを開く  
    - `py -m venv "./.venv"`  
    - `./.venv/Scripts/activate`  
    - (.venv)に切り替わっていること  
    - `py -m pip install -r requirements.txt`  
    - `py setup.py build`  


## モチベーション | Motivation  

'Tacspeak'は、他にはないゲーム体験を提供してくれる素晴らしいツールです。しかし日本ではネイティブな英語発音に親しみづらい人も少なくなく、言語の壁で対象ユーザーが限られてしまうことをとても残念に感じました。  
そこで、より多くのユーザーにTacspeakの魅力を届けたいという思いから、日本語入力を取り扱うことができないか検討してみました。  

結果として、DragonflyがWSRをハンドルできることが分かったため、比較的少ない変更で実装できました。  
元々DragonflyやTacspeak自体がシンプルかつコンパクトな実装であったことにも助けられました。  

改めて、オリジナルTacspeak制作者のjwebmeister氏に感謝と敬意を表します。  

'Tacspeak' is an amazing tool that provides a unique gaming experience. However, in Japan, many people does not familiarized them with native English pronaunciation.  
Therefore, I tryed whether it would be possible to handle Japanese speech input to bring the experiences of Tacspeak to many users as possible.  

As a result, I found out that Dragonfly can handle WSR, so I was able to made it with few changes.  
It also helped that Dragonfly and Tacspeak themselves has simple and compact codes.  

I would like to express my thanks and respect to jwebmeister, the author of the original Tacspeak.  


## ロードマップ | Roadmap  

- 前提として、このプロジェクトは個人の趣味です。サポート内容や期間については一切お約束できないことをご了承ください。  
  This project is personal. I can not guarantee any support, but I would to help you as I can if you need.  
- 今のところ、プログラム本体にこれ以上変更を加える予定はありません。  
  I have no plan to change any more the main programs for now.  
- あるとすれば、Ready or Not向け付属grammarの改良、またはオリジナルTacspeakの変更で適用すべきものの反映などを想定しています。  
  If some changes happen on original Tacspeak, I would check if it need to be applied to my project. And also I may update the grammar contained.  
- その他、使い方などの問い合わせに適宜対応します。  
  I will reply to your questions/comments as I can.  
- このプロジェクトはオープンソースです。ライセンスの範囲内で誰でも自由に改変できます。  
  This project is open source. Anyone can modify that within license below.  


## 制作者 | Author  

- Domtaro ([@Domtaro](https://github.com/Domtaro))  
- Joshua Webb ([@jwebmeister](https://github.com/jwebmeister)) - The original Tacspeak  


## ライセンス | License  

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0-or-later). See the [LICENSE.txt file](LICENSE.txt) for details.  


## 謝辞 | Acknowledgments  

- Based upon and may include code from "Dragonfly" [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly), under the LGPL-3.0 license.  
