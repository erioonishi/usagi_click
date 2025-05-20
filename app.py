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
