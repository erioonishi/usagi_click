from flask import Flask, render_template, redirect, request, session, url_for  
import threading  
import os
import signal
import time
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション利用のための秘密鍵


# ランキングJSONファイルのパス（同じフォルダに置く想定）
RANKING_FILE = 'ranking.json'

@app.route('/')
def index():
    # トップページ（名前入力フォーム）
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    # index.htmlのフォームからユーザー名を受け取り、セッションに保存、ステージ1へリダイレクト
    username = request.form.get('username')
    if username:
        session['username'] = username
        session['stage1_start'] = time.time()  # ステージ1開始時刻を保存
        return redirect('/stage1')
    return redirect('/')

@app.route('/stage1')
def stage1():
    session['stage1_start'] = time.time()  # 開始時間を最新にセット
    # ステージ1の画面描画処理など
    return render_template('stage1.html')


@app.route('/stage2')
def stage2():
    # ステージ2開始時刻を保存
    session['stage2_start'] = time.time()
    return render_template('stage2.html')

@app.route('/stage3')
def stage3():
    # ステージ3開始時刻を保存
    session['stage3_start'] = time.time()
    return render_template('stage3.html')

@app.route('/stage4')
def stage4():
    # ステージ4開始時刻を保存
    session['stage4_start'] = time.time()
    return render_template('stage4.html')

@app.route('/clear')
def clear():
    # クリア画面：どのステージか取得し、経過時間計算・ランキング更新
    stage = request.args.get('from_stage', '1')
    username = session.get('username', '匿名')

    start_key = f'stage{stage}_start'
    start_time = session.get(start_key)
    if start_time:
        elapsed = round(time.time() - start_time, 2)
    else:
        elapsed = 0.0

    # ランキング読み込み
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = []
    else:
        ranking = []

    # 新記録を追加（日時も追加）
    entry = {
        'name': username,
        'stage': stage,
        'time': elapsed,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    ranking.append(entry)

    # ステージ順、クリア時間順にソート（全体のランキング）
    ranking = sorted(ranking, key=lambda x: (int(x['stage']), x['time']))

    # **指定ステージのみ抽出して上位5件に絞る**
    filtered_ranking = [r for r in ranking if r['stage'] == stage][:5]

    # ファイルに書き込み（全体のランキングを保存）
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

    # enumerateはテンプレート側で使うので渡す（もし必要なら）
    return render_template('clear.html', from_stage=stage, elapsed=elapsed, ranking=filtered_ranking, enumerate=enumerate)


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
    # AllClear時は最終ステージ（例：4）として処理
    stage = '4'
    username = session.get('username', '匿名')

    start_key = f'stage{stage}_start'
    start_time = session.get(start_key)
    if start_time:
        elapsed = round(time.time() - start_time, 2)
    else:
        elapsed = 0.0

    # ランキング読み込み
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = []
    else:
        ranking = []

    # 新記録を追加（日時も追加）
    entry = {
        'name': username,
        'stage': stage,
        'time': elapsed,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    ranking.append(entry)

    # ステージ順、クリア時間順にソート（全体のランキングを整列）
    ranking = sorted(ranking, key=lambda x: (int(x['stage']), x['time']))

    # ステージ4に該当する上位5件だけを抽出
    filtered_ranking = [r for r in ranking if r['stage'] == stage][:5]

    # 全体のランキングを保存（上書き）
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

    # allclear.html に必要なデータを渡す
    return render_template('allclear.html', elapsed=elapsed, ranking=filtered_ranking, enumerate=enumerate)


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
⇒/shutdownというURLにアクセスされたときにHTTPのPOSTメソッドで来たリクエストだけを受け付ける(GETでは動かないように制限）
def shutdown(): ⇒ shutdownという関数を定義する(この関数は/shutdownにPOSTでアクセスされたときに呼び出される)
    shutdown_server()  ⇒ この関数が呼ばれると Flaskサーバーが止まる
    shutdown(): の中のshutdown_server()

★def shutdown_server(): ⇒ 自分(サーバープロセス)に終了の信号を送ってサーバーを停止
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