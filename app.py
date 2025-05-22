 #Flaskの基本機能(アプリ作成、HTML表示、リダイレクト、リクエスト取得)を読み込む
from flask import Flask, render_template, redirect, request
import threading #スレッドを使うためのライブラリ(現状、使っていない）
import os #OS操作のためのライブラリ(サーバーの終了に使う)
import signal #プロセスに信号を送るためのライブラリ(サーバー停止用)

app = Flask(__name__) #Flaskアプリのインスタンスを作る

@app.route('/') #URLのルート(トップページ / )にアクセスしたら、index.htmlを返す
def index():
    return render_template('index.html')

@app.route('/stage1') #/stage1にアクセスしたら、stage1.htmlを返す
def stage1():
    return render_template('stage1.html')

@app.route('/stage2') #/stage2にアクセスしたら、stage2.htmlを返す
def stage2():
    return render_template('stage2.html')

@app.route('/stage3') #/stage3にアクセスしたら、stage3.htmlを返す
def stage3():
    return render_template('stage3.html')

@app.route('/stage4') #/stage4にアクセスしたら、stage4.htmlを返す
def stage4():
    return render_template('stage4.html')

@app.route('/clear') #/clearにアクセスしたら
def clear():
    #どのステージから来たか(URLのクエリパラメータから取得)<例>?from_stage=2
    stage = request.args.get('from_stage', '1')  #デフォルト1
    return render_template('clear.html', from_stage=stage) #clear.htmlにその情報を渡して返す

#/next_stageにPOSTで現在のステージ番号を受け取り、次のステージのページにリダイレクトする
@app.route('/next_stage', methods=['POST'])
def next_stage():
    current = request.form.get('from_stage')
    if current == '1':
        return redirect('/stage2')
    elif current == '2':
        return redirect('/stage3')
    elif current == '3':
        return redirect('/stage4')
    elif current == '4':
        return redirect('/allclear')
    else:
        return redirect('/')

@app.route('/continue') #/continueにアクセスしたら、continue.htmlを返す
def continue_stage():
    return render_template('continue.html')

@app.route('/allclear') #/allclearにアクセスしたら、allclear.htmlを返す
def allclear():
    return render_template('allclear.html')

@app.route('/end') #/endにアクセスしたら、end.htmlを返す
def end():
    return render_template('end.html')

#/shutdownにend.htmlからPOSTでアクセスされたらサーバーを停止する処理を呼び出しシャットダウン中のメッセージを返す
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server(): #自分(サーバープロセス)に終了の信号を送ってサーバーを停止
    os.kill(os.getpid(), signal.SIGTERM)

#このファイルを直接実行した時だけ、Flaskの開発用サーバーを起動する。デバッグモードを有効にしている
if __name__ == '__main__':
    app.run(debug=True)


'''
★app = Flask(__name__)
Flaskアプリのインスタンスを作る
Flask(...)：Flaskのアプリを作る命令
__name__：今動いているこのファイルの名前が入る⇒どこにHTMLファイルや静的ファイルがあるかを知るため
__name__ を使って**アプリの場所（フォルダ）**を判断
app = ...：作ったFlaskアプリをappという変数に入れて使う

★@app.route('/') ⇒ URLの / (トップページ)にアクセスしたときに動かして
def index(): ⇒ indexという名前の関数を作る
    return render_template('index.html') ⇒ render_templateはHTMLファイルを表示するためのFlaskの命令
まとめるとURLのルート(トップページ / )にアクセスしたら、index.htmlを返す

★@app.route('/clear') ⇒ /clearにアクセスしたらこの下のclear()関数を動かす
def clear(): ⇒ clearという名前の関数を作り/clearにアクセスされたときに画面にクリア画面を出すための命令
    stage = request.args.get('from_stage', '1')
    ⇒HTMLから?from_stage=2のような情報があったら、それを取り出す
    request.args.get('from_stage')：URLからfrom_stageの値を取り出す
    例：/clear?from_stage=3 → '3' を取れる
    '1'：もし何も指定がなかったら、'1' にしておく（初期値）
    結果として stage という変数には、'1', '2', '3' などが文字列で入る
    return render_template('clear.html', from_stage=stage)#clear.htmlにその情報を渡して返す
    ⇒clear.html を表示して、そこにfrom_stageの情報を渡す
    clear.html の中で {{ from_stage }} と書けば、ステージの数字が使えるようになる
    「ステージ2クリア」と表示ができる
まとめると/clear?from_stage=2 のようにアクセスされたらそのステージ番号(ここでは2)をclear.htmlに渡して表示する

★@app.route('/shutdown', methods=['POST'])
⇒/shutdownというURLにアクセスされたときにHTTPのPOSTメソッドで来たリクエストだけを受け付ける（GETでは動かないように制限）
def shutdown(): ⇒  shutdownという関数を定義する。この関数は/shutdownにPOSTでアクセスされたときに呼び出される
    shutdown_server()  ⇒この関数が呼ばれると Flaskサーバーが止まる
    shutdown(): の中のshutdown_server()

★def shutdown_server(): #自分(サーバープロセス)に終了の信号を送ってサーバーを停止
    os.kill(os.getpid(), signal.SIGTERM)
    os.getpid()は「今動いている自分のプロセスのID」を取得(Flask)アプリそのもののID
    signal.SIGTERMは「終了して」という合図（信号）
    os.kill(プロセスID, 信号)で「自分自身に '終了' の信号を送って、自分を止める」という意味
まとめるとFlaskサーバー自身をプログラムで止める関数(ボタンなどからサーバーを停止したいときに使う)

★デバックモードとは
デバッグモード(debug=True)とは、Flaskを開発中に便利にするモード
間違いやエラーを見つけやすくし、開発をサポート
特徴としては
1. 自動リロード(コードを保存したら自動再起動)
2. エラーメッセージが詳しく表示されるのでバグの原因がすぐに分かる

★★コメントなしのコードが必要な場合★★
from flask import Flask, render_template, redirect, request
import threading 
import os
import signal

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stage1')
def stage1():
    return render_template('stage1.html')

@app.route('/stage2')
def stage2():
    return render_template('stage2.html')

@app.route('/stage3')
def stage3():
    return render_template('stage3.html')

@app.route('/stage4')
def stage4():
    return render_template('stage4.html')

@app.route('/clear')
def clear():
    # どのステージから来たか（URLのクエリパラメータから取得）
    stage = request.args.get('from_stage', '1')  # デフォルト1
    return render_template('clear.html', from_stage=stage)

@app.route('/next_stage', methods=['POST'])
def next_stage():
    current = request.form.get('from_stage')
    if current == '1':
        return redirect('/stage2')
    elif current == '2':
        return redirect('/stage3')
    elif current == '3':
        return redirect('/stage4')
    elif current == '4':
        return redirect('/allclear')
    else:
        return redirect('/')

@app.route('/continue')
def continue_stage():
    return render_template('continue.html')

@app.route('/allclear')
def allclear():
    return render_template('allclear.html')

@app.route('/end')
def end():
    return render_template('end.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    app.run(debug=True)

'''