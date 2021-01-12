try:
    import os
    from flask import Flask, jsonify, make_response,url_for
    from flask import redirect
    from flask import render_template
    from flask import request
    import json
    from flask_sqlalchemy import SQLAlchemy
    from datetime import datetime as DT,timedelta
    from random import choice
    from flask_cors import CORS, cross_origin
    from flask import  flash, session, abort
except Exception as e:print("Failed to import "+str(e))
try:
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = "sqlite:///{}".format(os.path.join(project_dir, "polodb.db"))
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_file
    app.config['SECRET_KEY'] = os.urandom(16)
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=120)
    dt=DT.now()
    db = SQLAlchemy(app)
except Exception as e:print("Failed in values"+str(e))


def gerar_token(tamanho):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUWVXYZ"
    password = ""
    for char in range(tamanho):password += choice(chars)
    return password

class Users(db.Model):
    id_users =db.Column(db.Integer,    unique=True, nullable=False, primary_key=True)
    username        =db.Column(db.String(56),nullable=False)
    email           =db.Column(db.String(56),nullable=False)
    password        =db.Column(db.String(56),nullable=False)
    contact         =db.Column(db.String(56),nullable=False)

class Prenda(db.Model):
    id_prenda   =db.Column(db.Integer,    unique=True, nullable=False, primary_key=True)
    op          =db.Column(db.String(16), unique=True, nullable=False)
    referencia =db.Column(db.String(16))
    fecha       =db.Column(db.DateTime)
    estado      =db.Column(db.String(9))
    id_color    =db.Column(db.Integer)
    cant_total  =db.Column(db.Integer)
    cant_tallaS =db.Column(db.Integer)
    cant_tallaM =db.Column(db.Integer)
    cant_tallaL =db.Column(db.Integer)
    cant_tallaXL =db.Column(db.Integer)
    cant_tallaXXL=db.Column(db.Integer)
    
    rS  =db.Column(db.Integer)
    rM  =db.Column(db.Integer)
    rL  =db.Column(db.Integer)
    rXL =db.Column(db.Integer)
    rXXL=db.Column(db.Integer)
    nota        =db.Column(db.String(56))
    
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
db.create_all()

def ct(id_prenda):
    operacion = db.engine.execute('select * from operacion where id_prenda ={};'.format(int(id_prenda)))
    sumaTotal = db.engine.execute('select sum(can_terminada) as suma from operacion where id_prenda ={};'.format(id_prenda))
    
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
        tallasT=db.engine.execute('select sum(can_terminada) as tallTT from operacion where id_prenda ={} AND id_talla={};'.format(row.id_prenda,row.id_talla))
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
    #print (tllT)
    return {'ct':ct,'tll':tll,'tllT':tllT,'fecp':fec,'sct':sct,'rt':rt,'idop':idop}


# ======================
#   Allow Cross Origin
# ======================


#@app.route('/signin/', methods=['GET', 'POST'])
@app.route("/login", methods=["POST"])
def login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
    registered_user = Users.query.filter_by(username=POST_USERNAME, password=POST_PASSWORD).first()
    if not registered_user is None:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

# Signup page
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        inserUser= Users(username=username,email=email,password=password,contact=contact)
        db.session.add(inserUser)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('index.html')

@app.route('/data',methods=["GET"])
def getData():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:
        prenda = Prenda.query.all()
        datas = {"draw": 1,
          "recordsTotal": 57,
          "recordsx`x`Filtered": 57}
        datas['data'] = []
        S=0
        M=0
        L=0
        XL=0
        XXL=0
        for row  in prenda:
            row.op=row.op.upper()
            row.referencia=row.referencia.upper()
            S  =row.rS
            M  =row.rM
            L  =row.rL
            XL =row.rXL
            XXL=row.rXXL            
            TT = int(row.cant_tallaS)+int(row.cant_tallaM)+int(row.cant_tallaL)+int(row.cant_tallaXL)+int(row.cant_tallaXXL)
            X  = row.cant_total-ct(row.id_prenda)['rt']
            if X <= 0:
                estado='<p class="text-danger">Cerrado</p>'
            else:
                estado='<p class="text-success">Abierto</p>'
            datas['data'].append({
          "id_pr":"{}".format(int(row.id_prenda)),
          "id_operacion":ct(int(row.id_prenda))['idop'],
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
          "rS": "{}".format(S),
          "rM": "{}".format(M),
          "rL": "{}".format(L),
          "rXL": "{}".format(XL),
          "rXXL": "{}".format(XXL),
          "totalTalla":"{}".format(int(TT)),
          "nota": "{}".format(row.nota),
          "tallas":ct(row.id_prenda)['tll'],
          "tallaS":ct(row.id_prenda)['tllT'],
          "total":ct(row.id_prenda)['sct'],
          "feechaOperacion": ct(row.id_prenda)['fecp'],
          "canFaltante": "{}".format(row.cant_total-ct(row.id_prenda)['rt']),
          "estado": estado,
})
        abuelo=jsonify(datas)
    print (datas)
    return (abuelo)

@app.route('/')
def home():
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        return redirect(url_for('registro'))#"Hello, Boss! <a href=\"/logout\"> Logout"
    return render_template('login.html')

@app.route('/registro', methods=["GET", "POST"])
def registro():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:#dt=str(dt[:-7])))
        if request.form:
            try:
                op           =request.form.get("op")
                referencia   =request.form.get("referencia")
                id_color     =request.form.get("color")
                cant_total   =request.form.get("cant_total")
                cant_tallaS  =request.form.get("cant_tallaS")
                cant_tallaM  =request.form.get("cant_tallaM")
                cant_tallaL  =request.form.get("cant_tallaL")
                cant_tallaXL =request.form.get("cant_tallaXL")
                cant_tallaXXL=request.form.get("cant_tallaXXL")

                if cant_total   =="":cant_total   =0
                if cant_tallaS  =="":cant_tallaS  =0
                if cant_tallaM  =="":cant_tallaM  =0
                if cant_tallaL  =="":cant_tallaL  =0
                if cant_tallaXL =="":cant_tallaXL =0
                if cant_tallaXXL=="":cant_tallaXXL=0

                prenda       =Prenda(op=op,
                referencia   =referencia,
                id_color     =id_color,
                cant_total   =cant_total,
                cant_tallaS  =cant_tallaS,
                cant_tallaM  =cant_tallaM,
                cant_tallaL  =cant_tallaL,
                cant_tallaXL =cant_tallaXL,
                cant_tallaXXL=cant_tallaXXL,
                rS  =cant_tallaS,
                rM  =cant_tallaM,
                rL  =cant_tallaL,
                rXL =cant_tallaXL,
                rXXL=cant_tallaXXL,                
                nota = request.form.get("nota"),
                estado=request.form.get("estado"),
                fecha = dt)
                
                if (str(request.form.get("op")))=="None" and (str(request.form.get("referencia")))=="None" and (str(request.form.get("color")))=="None" and (str(request.form.get("cant_total")))=="None" and (str(request.form.get("cant_tallaS")))=="None" and (str(request.form.get("cant_tallaM")))=="None" and (str(request.form.get("cant_tallaL")))=="None" and (str(request.form.get("cant_tallaXL")))=="None" and (str(request.form.get("cant_tallaXXL")))=="None" and (str(request.form.get("cant_nota")))=="None" and (str(request.form.get("estado")))=="None":
                    pass
                if (str(request.form.get("op")))=="None" and (str(request.form.get("referencia")))=="None" and (str(request.form.get("color")))=="None" and (str(request.form.get("cant_total")))=="None":
                    pass
                else:
                    db.session.add(prenda)
                    db.session.commit()

            except Exception as e:
                print("Failed to add prenda")
                print(e)
  
    gdt=getData()
    return render_template("tr.html",dgt=gdt)

@app.route('/operacion', methods=["POST"])
def operacion():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:
        if request.form:
            try:
                id_talla=request.form.get("id_talla")
                can_terminada = request.form.get("can_terminada")
                resta = Prenda.query.filter_by(id_prenda=request.form.get("id_prenda")).first()
                if id_talla=='1':resta.rS=(resta.rS-int(can_terminada))
                if id_talla=='2':resta.rM=(resta.rM-int(can_terminada))
                if id_talla=='3':resta.rL=(resta.rL-int(can_terminada))
                if id_talla=='4':resta.rXL=(resta.rXL-int(can_terminada))
                if id_talla=='5':resta.rXXL=(resta.rXXL-int(can_terminada))

                operacion     = Operacion(fecha         =dt,
                                          id_prenda     =request.form.get("id_prenda"),
                                          can_terminada = request.form.get("can_terminada"),
                                          id_talla      = request.form.get("id_talla"))        

                if (str(request.form.get("can_terminada")))=="Seleccione Talla" or (str(request.form.get("can_terminada")))=="None" or (str(request.form.get("can_terminada")))=="" or (str(request.form.get("id_prenda")))=="None":
                    pass
                else:
                    db.session.add(resta)
                    db.session.add(operacion)
                db.session.commit()

            except Exception as e:
                print("Failed to add operacion")
                print(e)
  
    return redirect(url_for('registro'))




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
        if (str(id_colornew))=="None":cant_total=0
        if (str(cant_totalnew))=="None":cant_total=0
        if (str(cant_tallaSnew))=="None":cant_tallaS=0
        if (str(cant_tallaMnew))=="None":cant_tallaM=0
        if (str(cant_tallaLnew))=="None":cant_tallaL=0
        if (str(cant_tallaXLnew))=="None":cant_tallaXL=0
        if (str(cant_tallaXXLnew))=="None":cant_tallaXXL=0

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
    return redirect("/registro")

@app.route("/delete", methods=["POST"])
def delete():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:
        idpre = request.form.get("id_pren")
        prenda = Prenda.query.filter_by(id_prenda=idpre).first()
        db.engine.execute('delete from operacion where id_prenda ={};'.format(idpre))
        db.engine.execute('delete from operacion where id_prenda ="";')

    #operacion = Operacion.query.filter_by(id_prenda=idpre)
  #  db.session.delete(operacion)
        db.session.delete(prenda)
        db.session.commit()
    return redirect("/registro")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

if __name__ == '__main__':
    app.debug = True
    app.secret_key =gerar_token(8)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(host='127.0.0.1', port=5000)
