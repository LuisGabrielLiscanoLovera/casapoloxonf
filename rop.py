import os
from flask import Flask, jsonify, make_response
from flask import redirect
from flask import render_template
from flask import request
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as DT
from os import remove as rm



project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "polodb.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
dt=DT.now()
db = SQLAlchemy(app)

class Book(db.Model):
    title = db.Column(db.String(2), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<OP: {}>".format(self.title)
   
class Prenda(db.Model):
    id_prenda  =db.Column(db.Integer,    unique=True, nullable=False, primary_key=True)
    op         =db.Column(db.String(16), unique=True, nullable=False)
    fecha      =db.Column(db.DateTime)
    estado     =db.Column(db.Integer)
    id_color   =db.Column(db.Integer)
    cant_total =db.Column(db.Integer)
    referencia =db.Column(db.String(16))
    
    def __repr__(self):
        #return self.op
        return "<OP: {}>".format(self.op)
        
class Operacion(db.Model):
    id_operacion  = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    id_prenda     = db.Column(db.Integer)
    fecha         = db.Column(db.DateTime)
    id_talla      = db.Column(db.Integer)
    can_terminada = db.Column(db.Integer)

    def __repr__(self):
        return "<Title: {}>".format(self.id_operacion)

class Talla(db.Model):
    id_talla = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    nom_talla= db.Column(db.String(2))
    def __repr__(self):
        return "<Title: {}>".format(self.nom_talla)

def ct(id_prenda):
    operacion = db.engine.execute('select id_operacion, can_terminada, id_talla, fecha from operacion where id_prenda ={};'.format(id_prenda))
    sumaTotal= db.engine.execute('select sum(can_terminada) as suma from operacion where id_prenda ={};'.format(id_prenda))
    sct=()
    ct=()
    fec=()
    tll=()
    idop=()
    for row in operacion:
        lidop=list(idop)
        lidop.append(row.id_operacion)
        idop=tuple(lidop)
        lct=list(ct)
        lct.append(row.can_terminada)
        ct=tuple(lct)
        lfec=list(fec)
        lfec.append(row.fecha)
        fec=tuple(lfec)
        tallas = db.engine.execute('select nom_talla from talla where id_talla ={};'.format(row.id_talla))
        #tallas = db.engine.execute('select id_talla from talla where id_talla ={};'.format(row.id_talla))
        for row in tallas:
            ltll = list(tll)
            ltll.append(row.nom_talla)
            tll = tuple(ltll)
    for row in sumaTotal:
        lsct = list(sct)
        lsct.append(row.suma)
        sct=tuple(lsct)
        rt=int(row.suma)
    return {'ct':ct,'tll':tll,'fecp':fec,'sct':sct,'rt':rt,'idop':idop}

@app.route('/test',methods=["GET", "POST"])

def gettest():
    prenda = Prenda.query.all()
    datas = {"draw": 1,
      "recordsTotal": 57,
      "recordsx`x`Filtered": 57}
    datas['data'] = []
    for row in prenda:
        datas['data'].append({"id_pr":"{}".format(int(row.id_prenda)),
        "id_operacion":ct(row.id_prenda)['idop'],
          "op": "{}".format(row.op),
          "referencia":"{}".format(row.op),
          "color": "{}".format(row.id_color),
          "cantidadTotal": "{}".format(row.cant_total),
          "fecha": "{}".format(row.fecha),
          "canTerminada":ct(row.id_prenda)['ct'],
          "tallas":ct(row.id_prenda)['tll'],
          "total":ct(row.id_prenda)['sct'],
          "feechaOperacion": ct(row.id_prenda)['fecp'],
          "canFaltante": "{}".format(row.cant_total-ct(row.id_prenda)['rt']),  
          "salary": "$162,700"
})
    print (datas)
    abuelo=jsonify(datas)
    return (abuelo)
    
@app.route('/data')
def get_data():
    p
    renda = Prenda.query.all()
    data = []
    for row in prenda:
        data.append([{
        'id prenda': '{}'.format(row.id_prenda),
        'op': '{}'.format(row.op),
        'color':'{}'.format(row.id_color),
        'cant_total':'{}'.format(row.cant_total)
        }])
    return jsonify(data)

@app.route('/', methods=["GET", "POST"])
def home():
    if request.form:
        try:
            prenda = Prenda(op=request.form.get("op"),
            referencia=request.form.get("referencia"),
            id_color   = request.form.get("color"),
            cant_total = request.form.get("cant_total"),
            fecha = dt)
            operacion  = Operacion(fecha=dt,id_prenda=request.form.get("id_prenda"),
            can_terminada=request.form.get("can_terminada"),
            id_talla=request.form.get("id_talla"))
            db.session.add(operacion)
            db.session.add(prenda)
            db.session.commit()


        except Exception as e:
            print("Failed to add prenda")
            print(e)
    prenda    = Prenda.query.all()
    query     = Prenda.query.filter_by(id_prenda = '1')
    operacion = Operacion.query.all()
    resultado = db.engine.execute('select * from operacion;')

    data = []
    for row in prenda:
        data.append([{'id prenda': '{}'.format(row.id_prenda),
    'op': '{}'.format(row.op),
    'color':'{}'.format(row.id_color),
    'cant_total':'{}'.format(row.cant_total)}])

    gdt=gettest()
    return render_template("tr.html",prenda=prenda,dgt=gdt,operacion=operacion,greeting="from python")

    #return render_template("home.html", prenda=prenda)

@app.route('/api/v1.0/mensaje')
def create_task():
    response = make_response(jsonify({"message": "desde piton y yei", "severity": "danger"}))
    return response

   # return jsonify('Hola mundo desde Flask returnando un yeson')



@app.route("/greeting")
def greeting():
    return {"greeting": "Hello from Flask!"}

@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        book = Book.query.filter_by(title=oldtitle).first()
        book.title = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update book title")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    op = request.form.get("op")
    prenda = Prenda.query.filter_by(op=op).first()
    db.session.delete(prenda)
    db.session.commit()
    return redirect("/")



if __name__ == "__main__":#app.run(debug=False)
    app.run(debug=False,host="127.0.0.1", port=5000)
