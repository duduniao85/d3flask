from flask import  Flask,render_template
import pandas as pd
import tushare as ts
app = Flask(__name__)
@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route('/indexquote',methods=['GET', 'POST'])
def indexquote():
    df=ts.get_rrr()
    df=df.sort(columns='date')
    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)