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
    id_prenda   =db.Column(db.Integer,    unique=True, nullable=False, primary_key=True)
    op          =db.Column(db.String(16), unique=True, nullable=False)
    fecha       =db.Column(db.DateTime)
    estado      =db.Column(db.Integer)
    id_color    =db.Column(db.Integer)
    cant_total  =db.Column(db.Integer)
    cant_tallaS =db.Column(db.Integer)
    cant_tallaM =db.Column(db.Integer)
    cant_tallaL =db.Column(db.Integer)
    cant_tallaXL =db.Column(db.Integer)
    cant_tallaXXL=db.Column(db.Integer)
    nota        =db.Column(db.String(56))
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
    operacion = db.engine.execute('select * from operacion where id_prenda ={};'.format(id_prenda))
    sumaTotal= db.engine.execute('select sum(can_terminada) as suma from operacion where id_prenda ={};'.format(id_prenda))
    sct=()
    ct=()
    fec=()
    tll=()
    tllT=()
    idop=()
    rt=0
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
        tallasT=db.engine.execute('select  sum(can_terminada) as tallTT from operacion where id_prenda ={} AND id_talla={};'.format(row.id_prenda,row.id_talla))
        ts=''
        tm=''
        tl=''
        txl=''
        txxl=''
        for row in tallas:
            ltll = list(tll)
            ltll.append(row.nom_talla)
            tll = tuple(ltll)
            for roww in tallasT:
                ltllT=list(tllT)
                ltllT.append("<br>"+str(row.nom_talla)+" ="+str(roww.tallTT)+"")
                tllT = tuple(set(ltllT))
                              
    for row in sumaTotal:
        if row.suma==None:
            rt=int(0)
        lsct = list(sct)
        lsct.append(row.suma)
        sct=tuple(lsct)
        try:
            rt=int(row.suma)
        except Exception as e:
            pass
    return {'ct':ct,'tll':tll,'tllT':tllT,'fecp':fec,'sct':sct,'rt':rt,'idop':idop}

@app.route('/test',methods=["GET", "POST"])

def getData():
    prenda = Prenda.query.all()
    datas = {"draw": 1,
      "recordsTotal": 57,
      "recordsx`x`Filtered": 57}
    datas['data'] = []
    for row in prenda:
        datas['data'].append({
          "id_pr":"{}".format(int(row.id_prenda)),
          "id_operacion":ct(row.id_prenda)['idop'],
          "op": "{}".format(row.op),
          "referencia":"{}".format(row.referencia),
          "color": "{}".format(row.id_color),
          "cantidadTotal": "{}".format(row.cant_total),
          "fecha": "{}".format(row.fecha),
          "canTerminada":ct(row.id_prenda)['ct'],
          "tallaSS": "{}".format(row.cant_tallaS),
          "tallaM": "{}".format(row.cant_tallaM),
          "tallaL": "{}".format(row.cant_tallaL),
          "tallaXL": "{}".format(row.cant_tallaXL),
          "tallaXXL": "{}".format(row.cant_tallaXXL),
          "nota": "{}".format(row.nota),
          "tallas":ct(row.id_prenda)['tll'],
          "tallaS":ct(row.id_prenda)['tllT'],
          "total":ct(row.id_prenda)['sct'],
          "feechaOperacion": ct(row.id_prenda)['fecp'],
          "canFaltante": "{}".format(row.cant_total-ct(row.id_prenda)['rt']),
          "salary": "$162,700"
})
            
    #print (datas)
    abuelo=jsonify(datas)
    return (abuelo)

@app.route('/', methods=["GET", "POST"])
def home():
    #dt=str(dt[:-7])
    print (type(dt))
    if request.form:
        try:
            prenda = Prenda(op=request.form.get("op"),
            referencia = request.form.get("referencia"),
            id_color   = request.form.get("color"),
            cant_total = request.form.get("cant_total"),
            cant_tallaS = request.form.get("cant_tallaS"),
            cant_tallaM = request.form.get("cant_tallaM"),
            cant_tallaL = request.form.get("cant_tallaL"),
            cant_tallaXL = request.form.get("cant_tallaXL"),
            cant_tallaXXL = request.form.get("cant_tallaXXL"),
            nota = request.form.get("nota"),
            fecha = dt)
            operacion     = Operacion(fecha=dt,id_prenda=request.form.get("id_prenda"),
            can_terminada = request.form.get("can_terminada"),
            id_talla=request.form.get("id_talla"))
            if (str(request.form.get("op")))=="None" and (str(request.form.get("referencia")))=="None" and (str(request.form.get("color")))=="None" and (str(request.form.get("cant_total")))=="None":
                pass
            else:
                db.session.add(prenda)
            if (str(request.form.get("can_terminada")))=="":
                pass
            else:
                db.session.add(operacion)
            db.session.commit()


        except Exception as e:
            print("Failed to add prenda")
            print(e)
    prenda    = Prenda.query.all()
    query     = Prenda.query.filter_by(id_prenda = '1')
    operacion = Operacion.query.all()
    resultado = db.engine.execute('select * from operacion;')

    gdt=getData()
    return render_template("tr.html",prenda=prenda,dgt=gdt,operacion=operacion,greeting="from python")

@app.route('/api/v1.0/mensaje')
def create_task():
    response = make_response(jsonify({"message": "desde piton y yei", "severity": "danger"}))
    return response



@app.route("/greeting")
def greeting():
    return {"greeting": "Hello from Flask!"}

@app.route("/update", methods=["POST"])
def update():
    try:
        opnew=request.form.get("op"),
        referencianew = request.form.get("referencia"),
        id_colornew   = request.form.get("color"),
        cant_totalnew = request.form.get("cant_total"),
        cant_tallaSnew = request.form.get("cant_tallaS"),
        cant_tallaMnew = request.form.get("cant_tallaM"),
        cant_tallaLnew = request.form.get("cant_tallaL"),
        cant_tallaXLnew = request.form.get("cant_tallaXL"),
        cant_tallaXXLnew = request.form.get("cant_tallaXXL"),
        notanew = request.form.get("nota")

        opold=request.form.get("opold")
        referenciaold = request.form.get("referenciaold")
        id_colorold   = request.form.get("colorold")
        cantidadTotalold = request.form.get("cantidadTotalold")
        cant_tallaSold = request.form.get("cant_tallaSold")
        cant_tallaMold = request.form.get("cant_tallaMold")
        cant_tallaLold = request.form.get("cant_tallaLold")
        cant_tallaXLold = request.form.get("cant_tallaXLold")
        cant_tallaXXLold = request.form.get("cant_tallaXXLold")
        notaold = request.form.get("notaold")

        operacion = Prenda.query.filter_by(op=opold).first()
        operacion.op = str(opnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        referencia = Prenda.query.filter_by(referencia=referenciaold).first()
        operacion.referencia = str(referencianew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        color = Prenda.query.filter_by(id_color=id_colorold).first()
        color.id_color = str(id_colornew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        canTotal = Prenda.query.filter_by(cant_total=cantidadTotalold).first()
        canTotal.cant_total = str(cant_totalnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})
        

        canTallaS = Prenda.query.filter_by(cant_tallaS=cant_tallaSold).first()
        canTallaS.cant_tallaS = str(cant_tallaSnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        canTallaM = Prenda.query.filter_by(cant_tallaM=cant_tallaMold).first()
        canTallaM.cant_tallaM = str(cant_tallaMnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        canTallaL = Prenda.query.filter_by(cant_tallaL=cant_tallaLold).first()
        canTallaL.cant_tallaL = str(cant_tallaLnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        canTallaXL = Prenda.query.filter_by(cant_tallaXL=cant_tallaXLold).first()
        canTallaXL.cant_tallaXL = str(cant_tallaXLnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        canTallaXXL = Prenda.query.filter_by(cant_tallaXXL=cant_tallaXXLold).first()
        canTallaXXL.cant_tallaXXL = str(cant_tallaXXLnew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})

        #notas = Prenda.query.filter_by(nota=notaold).first()
        #for row in notas:
         #   print(row.nota)
        #notas.nota = str(notanew).translate({ord('('): None}).translate({ord(')'): None}).translate({ord("'"): None}).translate({ord(','): None})
        #print(str(notaold,notanew))
        db.session.commit()
    except Exception as e:
        print("Couldn't update book title")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    idpre = request.form.get("id_pren")
    oper  = request.form.get("id_operacion")
    prenda = Prenda.query.filter_by(id_prenda=idpre).first()
    operacion = Operacion.query.filter_by(id_operacion=oper).first()
    #db.session.delete(operacion)
    db.session.delete(prenda)
    db.session.commit()
    return redirect("/")



if __name__ == "__main__":#app.run(debug=False)
    app.run(debug=False,host="127.0.0.1", port=4000)
