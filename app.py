#Flaskの基本機能(アプリ作成、HTML表示、リダイレクト、リクエスト取得)を読み込む
from flask import Flask, render_template, redirect, request, session, url_for  
import threading  #スレッドを使うためのライブラリ(現状、使っていない）
import os #OS操作のためのライブラリ(サーバーの終了に使う)
import signal #プロセスに信号を送るためのライブラリ(サーバー停止用)
import time #時刻の取得、待機時間、経過時間の計測などに使う
import json # PythonのデータをJSON形式で保存・読み込みするために使う

app = Flask(__name__) #Flaskアプリのインスタンスを作る
app.secret_key = 'your_secret_key'  #セッションを安全に扱うための「秘密鍵」を設定【下に追記】

#ランキングJSONファイルのパス(同じフォルダに置く想定)
RANKING_FILE = 'ranking.json'

@app.route('/') #URLのルート(トップページ / )にアクセスしたら、login.htmlを返す
def root():
    return redirect(url_for('login')) #redirect(リダイレクト)は、別の場所へ自動的に移動させるという意味

#ログイン画面の処理でPOSTされたパスワードが「usa」なら成功、それ以外ならエラーメッセージを表示
@app.route('/login', methods=['GET', 'POST']) #ページを表示するGETとフォームを送信するPOST両方のリクエストを受け付ける
def login():
    error = None #エラーメッセージを格納する変数を初期化して、最初はエラーがないのでNoneにしておく
    if request.method == 'POST': #もしフォームが送信されてきた(POSTリクエストだった)場合の処理に入る
                                 #GETの場合(最初にページを開いたとき)はこの中には入らない
        if request.form['password'] == 'usa': #フォームに入力されたパスワードの値がusaかどうか
            return redirect(url_for('index'))
        else:
            error = 'パスワードが間違っています'
    return render_template('login.html', error=error) #render(レンダー)は、表示するという意味

@app.route('/index')#/indexにアクセスしたら、index.htmlを返す
def index():
    #名前入力フォーム
    return render_template('index.html')

@app.route('/start', methods=['POST']) 
def start():
    # index.htmlのフォームからユーザー名を受け取り、セッションに保存、ステージ1へリダイレクト
    username = request.form.get('username')
    if username: #ユーザー名がちゃんと入力されていれば(空でなければ)次の処理へ
        session['username'] = username #ユーザー名をFlaskのセッションに保存し、他のページでもログイン中のユーザー名を使えるようする
        session['stage1_start'] = time.time()  # ステージ1開始時刻を保存
        return redirect('/stage1') #入力が正しくできていれば、次のステージ/stage1に進む
    return redirect('/') #ユーザー名が入力されていなかった場合(空欄)トップページに戻す(/→ログインにリダイレクト)
    #session(セッション)はユーザーごとの一時的なデータの保存領域を指す

@app.route('/stage1') #/stage1にアクセスしたら、stage1.htmlを返す
def stage1():
    session['stage1_start'] = time.time()  # 開始時間を最新にセット
    #ステージ1の画面描画処理など
    return render_template('stage1.html')

@app.route('/stage2') #/stage2にアクセスしたら、stage2.htmlを返す
def stage2():
    #ステージ2開始時刻を保存
    session['stage2_start'] = time.time()
    return render_template('stage2.html')

@app.route('/stage3') #/stage3にアクセスしたら、stage3.htmlを返す
def stage3():
    #ステージ3開始時刻を保存
    session['stage3_start'] = time.time()
    return render_template('stage3.html')

@app.route('/stage4') #/stage4にアクセスしたら、stage4.htmlを返す
def stage4():
    #ステージ4開始時刻を保存
    session['stage4_start'] = time.time()
    return render_template('stage4.html')

@app.route('/clear') #/clearにアクセスしたら
def clear():
    #クリア画面：どのステージか取得し、経過時間計算・ランキング更新
    #どのステージのクリアなのか取得して、開始時間との差でクリア時間を計算
    stage = request.args.get('from_stage', '1') #デフォルト1
    username = session.get('username', '匿名') #セッションからユーザー名を取得し、セッションに名前がなければ '匿名' として処理

    start_key = f'stage{stage}_start'
    start_time = session.get(start_key) #ステージごとの開始時間はsession['stage1_start']のように保存していたのでそれを読み出す
    if start_time:
        elapsed = round(time.time() - start_time, 2) #開始時刻がある場合は現在時刻との差から経過時間を計算(秒、少数2位まで)
    else:
        elapsed = 0.0 #なければ0.0(例外対策)
    #elapsed(イラプスト)経過したという意味⇒かかった時間

    #ランキングファイルがあれば読み込む、エラー時や存在しないときは空リストにする
    if os.path.exists(RANKING_FILE): #exists(イグジスツ)は存在するという意味
        with open(RANKING_FILE, 'r', encoding='utf-8') as f: #RANKING_FILE(ランキングのJSONファイル)があれば開いて'r'読み込み
            try: #【下に追記】
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = [] #ファイルが壊れている場合も例外処理で空リスト
    else:
        ranking = [] #なければ空リストから始める

    #今回の記録(名前・ステージ・時間・日時)をランキングに追加
    entry = {
        'name': username,
        'stage': stage,
        'time': elapsed,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S') #strftime日付や時刻を文字列(str)に変換するための関数
    }
    ranking.append(entry)

    #ステージ順、クリア時間順にソート(全体のランキング)
    ranking = sorted(ranking, key=lambda x: (int(x['stage']), x['time'])) #x⇒変数、lambda(ラムダ)⇒名前のない関数(＝無名関数)
    #指定ステージのみ抽出して上位5件に絞る
    filtered_ranking = [r for r in ranking if r['stage'] == stage][:5] #今回クリアしたステージだけに絞って、上位5人分だけを取り出す


    #ファイルに書き込み（全体のランキングをJSONファイルに保存）
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2) #json.dump⇒Pythonのデータ(辞書やリストなど)をJSON形式のファイルに書き込む関数【下に追記】

    #enumerateはテンプレート側で使うので渡す【下に追記】
    return render_template('clear.html', from_stage=stage, elapsed=elapsed, ranking=filtered_ranking, enumerate=enumerate)

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
    #AllClear時は最終ステージ(例：4)として処理
    stage = '4'
    username = session.get('username', '匿名')

    start_key = f'stage{stage}_start'
    start_time = session.get(start_key)
    if start_time:
        elapsed = round(time.time() - start_time, 2)
    else:
        elapsed = 0.0

    #ランキング読み込み
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = []
    else:
        ranking = []

    #新記録を追加(日時も追加)
    entry = {
        'name': username,
        'stage': stage,
        'time': elapsed,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    ranking.append(entry)

    #ステージ順、クリア時間順にソート(全体のランキングを整列)
    ranking = sorted(ranking, key=lambda x: (int(x['stage']), x['time']))

    #ステージ4に該当する上位5件だけを抽出
    filtered_ranking = [r for r in ranking if r['stage'] == stage][:5]

    #全体のランキングを保存（上書き）
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

    #セッションからステージ開始時間を削除
    if start_key in session:
        session.pop(start_key)

    #allclear.html に必要なデータを渡す
    return render_template('allclear.html', elapsed=elapsed, ranking=filtered_ranking, enumerate=enumerate)


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

★app.secret_key = 'your_secret_key'
・Flaskのsessionはユーザーごとに情報(例：ログイン状態、名前、開始時間など)を一時的に保持する仕組み
・このセッション情報はクライアント側(ブラウザ)に暗号化された形で保存される
・そのため、内容が改ざんされていないかを検証するための署名(サイン)が必要
・その署名に使われるのがsecret_key(秘密鍵)
※実際に現場で使うときはもっと複雑なkeyにする

★@app.route('/') ⇒ URLの / (トップページ)にアクセスしたときに動かして
def login(): ⇒ loginという名前の関数を作る
    return render_template('login.html') ⇒ render_templateはHTMLファイルを表示するためのFlaskの命令
まとめるとURLのルート(トップページ / )にアクセスしたら、login.htmlを返す

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

★try-except文は、Pythonにおけるエラー処理(例外処理)のための構文
⇒もしエラーが起きても、止まらず別の処理をする
try     エラーが起きそうな処理を書く
except	エラーが起きたときにどうするか書く
else	tryが成功(＝エラーなし)だったとき実行
finally	エラーの有無に関係なく、最後に必ず実行される(ファイルの後始末などに便利)

★ json.dump(ranking, f, ensure_ascii=False, indent=2) 
ranking⇒Pythonのリストや辞書などのデータ(ここではランキング情報のリストなど)
f⇒書き込み用に開いているファイルオブジェクト
ensure_ascii=False⇒日本語などの非ASCII文字をそのまま文字として保存(Unicodeエスケープせずに読みやすく)
indent=2⇒JSONファイルの出力をインデント(字下げ))2スペースで整形

★return render_template('clear.html', from_stage=stage, elapsed=elapsed, ranking=filtered_ranking, enumerate=enumerate)
clear.html にデータを渡して表示する
・from_stage: 何ステージをクリアしたか
・elapsed: (エラプスト)そのステージのクリアタイム
・ranking: 指定ステージの上位5人のランキング
・enumerate: HTMLでランキング順位を表示するため({% for i, r in enumerate(ranking) %}などで使う)
  (イナマーレート)は、リストやタプルなどの繰り返し可能なものをループするときに、同時にインデックス番号(何番目か)も取得できる便利な関数

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
from flask import Flask, render_template, redirect, request, session, url_for  
import threading
import os
import signal
import time
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

RANKING_FILE = 'ranking.json'

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == 'usa':
            return redirect(url_for('index'))
        else:
            error = 'パスワードが間違っています'
    return render_template('login.html', error=error)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST']) 
def start():
    username = request.form.get('username')
    if username:
        session['username'] = username
        session['stage1_start'] = time.time()
        return redirect('/stage1')
    return redirect('/')

@app.route('/stage1')
def stage1():
    session['stage1_start'] = time.time()
    return render_template('stage1.html')

@app.route('/stage2')
def stage2():
    session['stage2_start'] = time.time()
    return render_template('stage2.html')

@app.route('/stage3')
def stage3():
    session['stage3_start'] = time.time()
    return render_template('stage3.html')

@app.route('/stage4')
def stage4():
    session['stage4_start'] = time.time()
    return render_template('stage4.html')

@app.route('/clear')
def clear():
    stage = request.args.get('from_stage', '1')
    username = session.get('username', '匿名')

    start_key = f'stage{stage}_start'
    start_time = session.get(start_key)
    if start_time:
        elapsed = round(time.time() - start_time, 2)
    else:
        elapsed = 0.0 #なければ0.0(例外対策)

    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = []
    else:
        ranking = []

    entry = {
        'name': username,
        'stage': stage,
        'time': elapsed,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    ranking.append(entry)

    ranking = sorted(ranking, key=lambda x: (int(x['stage']), x['time']))
    filtered_ranking = [r for r in ranking if r['stage'] == stage][:5]

    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

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
    stage = '4'
    username = session.get('username', '匿名')

    start_key = f'stage{stage}_start'
    start_time = session.get(start_key)
    if start_time:
        elapsed = round(time.time() - start_time, 2)
    else:
        elapsed = 0.0

    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                ranking = []
    else:
        ranking = []

    entry = {
        'name': username,
        'stage': stage,
        'time': elapsed,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    ranking.append(entry)

    ranking = sorted(ranking, key=lambda x: (int(x['stage']), x['time']))

    filtered_ranking = [r for r in ranking if r['stage'] == stage][:5]

    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)

    if start_key in session:
        session.pop(start_key)

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