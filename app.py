from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/politica-privacidade')
def politica_privacidade():
    return render_template('politica_privacidade.html')

@app.route('/termos')
def termos_de_uso():
    return render_template('termos.html')

if __name__ == '__main__':
    app.run(debug=True)
