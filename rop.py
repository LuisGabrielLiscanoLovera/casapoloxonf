try:
    import os
    from flask import Flask
    from flask import jsonify
    from flask import url_for
    from flask import flash
    from flask import session
    from flask import abort
    from flask import request
    from flask import render_template, redirect
    from flask_sqlalchemy import SQLAlchemy
    from datetime import datetime as DT,timedelta
    from random import choice
    from flask_cors import CORS, cross_origin
    
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
except Exception as e:
    print("Failed in values"+str(e))


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
    id_role         =db.Column(db.String(56))

class Integrnte(db.Model):
    id_integrante      =db.Column(db.Integer,   unique=True, nullable=False, primary_key=True)
    nom_integrante     =db.Column(db.String(56),nullable=False)
    email              =db.Column(db.String(56))
    cedula             =db.Column(db.String(56))
    contact            =db.Column(db.String(56))
    fecha              =db.Column(db.String(56))
    direcion           =db.Column(db.String(56))
    foto               =db.Column(db.String(56))

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
    can_resta     = db.Column(db.Integer)

class Tarea(db.Model):
    id_tarea      = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    nom_tarea     = db.Column(db.String(56))
    fecha         = db.Column(db.DateTime)
    duracion      = db.Column(db.String(56))
    precio        = db.Column(db.Integer)
    mininoDia     = db.Column(db.Integer)

    def __repr__(self):
        return "<Title: {}>".format(self.nom_tarea)
class Destajo(db.Model):
    id_prenda     = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    id_tarea      = db.Column(db.Integer)
    id_integrante = db.Column(db.Integer)
    cantidad      = db.Column(db.Integer)
    fecha         = db.Column(db.DateTime)
    id_talla      = db.Column(db.Integer)
    can_resta     = db.Column(db.Integer)

class Talla(db.Model):
    id_talla = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    nom_talla= db.Column(db.String(2))
    def __repr__(self):
        return "<Title: {}>".format(self.nom_talla)
db.create_all()

def ct(id_prenda):
    operacion = db.engine.execute('select * from operacion where id_prenda ={};'.format(int(id_prenda)))
    sumaTotal = db.engine.execute('select sum(can_terminada) as suma from operacion where id_prenda ={};'.format(id_prenda))
    sumaTotalR =db.engine.execute('select sum(can_resta) as sumaR from operacion where id_prenda ={};'.format(id_prenda))
    sct=()
    ct=()
    fec=None
    tll=()
    tllT=()
    idop=()
    histo=()
    rt=0
    for row in operacion:
        lidop=list(idop)
        lidop.append(row.id_operacion)
        idop=tuple(lidop)
        lct=list(ct)
        lct.append(row.can_terminada)
        ct=tuple(lct)
        fec=str('Fecha cierre:')+(str(row.fecha))[:16].translate({ord(' '): ' / '})+' <i class="icofont-clock-time"></i>'

        tallas   = db.engine.execute('select nom_talla from talla where id_talla ={};'.format(row.id_talla))
        tallasT  = db.engine.execute('select sum(can_terminada) as tallTT from operacion where id_prenda ={} AND id_talla={};'.format(row.id_prenda,row.id_talla))
        tallasTR = db.engine.execute('select sum(can_resta) as tallTR from operacion where id_prenda ={} AND id_talla={};'.format(row.id_prenda,row.id_talla))
        ts=''
        tm=''
        tl=''
        txl=''
        txxl=''
        histo=''
        for row in tallas:
            ltll = list(tll)
            ltll.append(row.nom_talla)
            tll = tuple(ltll)
            for roww in tallasT:
                ltllT=list(tllT)
                lhisto= list(histo)
                for rowww in tallasTR:
                    if roww.tallTT-rowww.tallTR ==0:pass
                    else:
                        ltllT.append(str("<br>"+str(row.nom_talla)+" = "+str(roww.tallTT-rowww.tallTR)+""))
                        lhisto.append(str("<br>"+str(row.nom_talla)+" = "+str(roww.tallTT)))
                        tllT = tuple(set(ltllT))
                        histo=tuple(set(lhisto))
    for row in sumaTotal:
        for roww in sumaTotalR:
            lsct = str(sct)
            if row.suma==None:
                rt=int(0)          
            if roww.sumaR ==None and row.suma==None :pass
            else:
                lsct=int(row.suma)-int(roww.sumaR)
                
                try:
                    rt=int(row.suma-roww.sumaR)
                except Exception as e:
                    pass
    return {'ct':ct,'tll':tll,'tllT':tllT,'fecp':fec,'sct':lsct,'rt':rt,'idop':idop,'histo':histo}

def vacio(vacio):
    if vacio==0:return ''
    else:return vacio
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
        flash('Usuario o Clave incorrecto!')
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
          "recordsTotal": len(prenda),
          "recordsx`x`Filtered": len(prenda)}
        datas['data'] = []
        S=0
        M=0
        L=0
        XL=0
        XXL=0
        i=0
        for row  in prenda:
            row.op=row.op.upper()
            row.referencia=row.referencia.upper()
            if type(row.cant_tallaS)   ==str:row.cant_tallaS  =0
            if type(row.cant_tallaM)   ==str:row.cant_tallaM  =0
            if type(row.cant_tallaL)   ==str:row.cant_tallaL  =0
            if type(row.cant_tallaXL)  ==str:row.cant_tallaXL =0
            if type(row.cant_tallaXXL) ==str:row.cant_tallaXXL=0
            TT = int(row.cant_tallaS)+int(row.cant_tallaM)+int(row.cant_tallaL)+int(row.cant_tallaXL)+int(row.cant_tallaXXL)
            X  = row.cant_total-ct(row.id_prenda)['rt']
            i=i+1
            if TT != int(row.cant_total):
                noIgual='<d class="h6 text-warnig"><small class="text-muted">Cantidad Total y Total tallas tienen un valor inconsistente </small></d>'
            else:noIgual=''
            if X <= 0:
                Prenda.query.filter_by(id_prenda=row.id_prenda).first().estado = 'Cerrado'
                db.session.commit()
                estado='<d class="h6 text-success">Cerrado<i class="icofont-minus-circle"></i></d>'
                opD='<d class="text-success icofont-verification-check">'+str(i)+')  '+str(row.op)+'</d>'
                fec=ct(row.id_prenda)['fecp']
            else:
                Prenda.query.filter_by(id_prenda=row.id_prenda).first().estado = 'Abierto'
                db.session.commit()
                estado='<d class="h6 text-info">Abierto<i class="icofont-automation"></i></d>'
                opD='<d class="text-info icofont-error">'+str(i)+')  '+str(row.op)+'</d>'
                fec=''

            fecha=(str(row.fecha))[:16].translate({ord(' '): ' / '})+' <i class="icofont-clock-time"></i>'
            datas['data'].append({
          "id_pr":"{}".format(int(row.id_prenda)),
          "id_operacion":ct(int(row.id_prenda))['idop'],
          "opD": "{}".format(opD),
          "op": "{}".format(row.op),
          "referencia":"{}".format(row.referencia),
          "color": "{}".format(str(row.id_color)),
          "cantidadTotal": "{}".format(row.cant_total),
          "fecha": "{}".format(fecha),
          "canTerminada":ct(row.id_prenda)['ct'],
          "tallaSS": "{}".format(vacio(row.cant_tallaS)),
          "tallaM": "{}".format(vacio(row.cant_tallaM)),
          "tallaL": "{}".format(vacio(row.cant_tallaL)),
          "tallaXL": "{}".format(vacio(row.cant_tallaXL)),
          "tallaXXL": "{}".format(vacio(row.cant_tallaXXL)),
          "totalTalla":"{}".format(int(TT)),
          "nota": "{}".format(row.nota),
          "tallas":ct(row.id_prenda)['tll'],
          "tallaS":ct(row.id_prenda)['tllT'],
          "feechaOperacion": fec,
          "estado": estado,
          "noIgual":noIgual,
          "historia":ct(row.id_prenda)['histo'],
})
        abuelo=jsonify(datas)
    #print (datas)
    return abuelo
app.route('/')
def home():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:
        return redirect(url_for('registro'))#"Hello, Boss! <a href=\"/logout\"> Logout"
    return render_template('login.html')

@app.route('/registro', methods=["GET", "POST"])
def registro():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:#dt=str(dt[:-7])))

        try:
            db.engine.execute("insert into users values(1,'admin','ccidbcomputacion@gmail.com','admin','3117569482');")
            db.engine.execute("insert into talla values(1,'S');")
            db.engine.execute("insert into talla values(2,'M');")
            db.engine.execute("insert into talla values(3,'L');")
            db.engine.execute("insert into talla values(4,'XL');")
            db.engine.execute("insert into talla values(5,'XXL');")
            db.engine.execute("insert into talla values(6,'Punto');")
        except Exception as e:pass

        if request.form:

            try:
                op           =request.form.get("op").upper()
                referencia   =request.form.get("referencia").upper()
                id_color     =request.form.get("color")
                cant_total   =request.form.get("cant_total")
                cant_tallaS  =request.form.get("cant_tallaS")
                cant_tallaM  =request.form.get("cant_tallaM")
                cant_tallaL  =request.form.get("cant_tallaL")
                cant_tallaXL =request.form.get("cant_tallaXL")
                cant_tallaXXL=request.form.get("cant_tallaXXL")
                nota         =request.form.get("nota")

                if nota =="":nota="No hay notas para este registro"
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
                nota = nota,
                estado=request.form.get("estado"),
                fecha = dt)

                if (str(request.form.get("op")))=="None" and (str(request.form.get("referencia")))=="None" and (str(request.form.get("color")))=="None" and (str(request.form.get("cant_total")))=="None" and (str(request.form.get("cant_tallaS")))=="None" and (str(request.form.get("cant_tallaM")))=="None" and (str(request.form.get("cant_tallaL")))=="None" and (str(request.form.get("cant_tallaXL")))=="None" and (str(request.form.get("cant_tallaXXL")))=="None" and (str(request.form.get("cant_nota")))=="None" and (str(request.form.get("estado")))=="None":
                    pass
                if (str(request.form.get("op")))=="None" and (str(request.form.get("referencia")))=="None" and (str(request.form.get("color")))=="None" and (str(request.form.get("cant_total")))=="None":
                    pass
                else:
                    predOP=Prenda.query.filter_by(op=op).first()
                    if predOP==None:
                        db.session.add(prenda)
                        db.session.commit()
                    else:
                        if predOP.op==op:flash('Esta op [ '+str(predOP.op)+' ] ya existe! con una cantidad total [ '+str(predOP.cant_total)+' ] Estado '+str(predOP.estado))
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
                can_terminada = request.form.get("can_terminada")
                id_talla      = request.form.get("id_talla")
                prenda        = Prenda.query.filter_by(id_prenda=request.form.get("id_prenda")).first()
                decremt       = request.form.get("resta")
#                oper          = Operacion.query.filter_by(id_prenda=request.form.get("id_prenda")).first()

                if str(decremt)=="resta":
                    can_resta     = request.form.get("can_terminada")
                    can_terminada = 0
                    if id_talla=='1':prenda.rS  =(prenda.rS+int(can_resta))
                    if id_talla=='2':prenda.rM  =(prenda.rM+int(can_resta))
                    if id_talla=='3':prenda.rL  =(prenda.rL+int(can_resta))
                    if id_talla=='4':prenda.rXL =(prenda.rXL+int(can_resta))
                    if id_talla=='5':prenda.rXXL=(prenda.rXXL+int(can_resta))

                else:
                    can_terminada = request.form.get("can_terminada")
                    can_resta     = 0
                    if id_talla=='1':prenda.rS  =(prenda.rS-int(can_terminada))
                    if id_talla=='2':prenda.rM  =(prenda.rM-int(can_terminada))
                    if id_talla=='3':prenda.rL  =(prenda.rL-int(can_terminada))
                    if id_talla=='4':prenda.rXL =(prenda.rXL-int(can_terminada))
                    if id_talla=='5':prenda.rXXL=(prenda.rXXL-int(can_terminada))

                operacion     = Operacion(fecha  =dt,
                                   id_prenda     = request.form.get("id_prenda"),
                                   can_terminada = can_terminada,
                                   can_resta     = can_resta,
                                   id_talla      = request.form.get("id_talla"))        

                if (str(request.form.get("can_terminada")))=="Seleccione Talla" or (str(request.form.get("can_terminada")))=="None" or (str(request.form.get("can_terminada")))=="" or (str(request.form.get("id_prenda")))=="None":pass
                else:pass
                db.session.add(prenda)
                db.session.add(operacion)
                db.session.commit()

            except Exception as e:
                flash('error en la operacion')
                print(e)
    return redirect(url_for('registro'))




@app.route("/update", methods=["POST"])
def update():
    try:
        id_prenda   = request.form.get("id_prenda")
        opnew=request.form.get("op").upper()
        referencianew = request.form.get("referencia").upper()
        id_colornew   = request.form.get("color")
        cant_totalnew = request.form.get("cant_total")
        cant_tallaSnew = request.form.get("cant_tallaS")
        cant_tallaMnew = request.form.get("cant_tallaM")
        cant_tallaLnew = request.form.get("cant_tallaL")
        cant_tallaXLnew = request.form.get("cant_tallaXL")
        cant_tallaXXLnew = request.form.get("cant_tallaXXL")
        notanew = request.form.get("nota")


        if id_colornew     =="":id_colornew==0
        if cant_totalnew   =="":cant_totalnew=0
        if cant_tallaSnew  =="":cant_tallaSnew=0
        if cant_tallaMnew  =="":cant_tallaMnew=0
        if cant_tallaLnew  =="":cant_tallaLnew=0
        if cant_tallaXLnew =="":cant_tallaXLnew=0
        if cant_tallaXXLnew=="":cant_tallaXXLnew=0

        prend    = Prenda.query.filter_by(id_prenda=id_prenda).first()
        prend.op = opnew
        prend.referencia    = referencianew
        prend.id_color      = id_colornew
        prend.cant_total    = cant_totalnew
        prend.cant_tallaS   = cant_tallaSnew
        prend.cant_tallaM   = cant_tallaMnew
        prend.cant_tallaL   = cant_tallaLnew
        prend.cant_tallaXL  = cant_tallaXLnew
        prend.cant_tallaXXL = cant_tallaXXLnew
        prend.rS  = cant_tallaSnew
        prend.rM  = cant_tallaMnew
        prend.rL  = cant_tallaLnew
        prend.rXL = cant_tallaXLnew
        prend.rXXL= cant_tallaXXLnew
        prend.nota= notanew
        db.engine.execute('delete from operacion where id_prenda ={};'.format(id_prenda))
        db.session.commit()
    except Exception as e:
        flash('error en la operacion no se pudo actualizar!')
        print(e)
    return redirect("/registro")

@app.route("/delete", methods=["POST"])
def delete():
    if 1==5:#not session.get("logged_in"):
        flash('No se encuentra registrado')
        return render_template("login.html")
    else:
        try:
            idpre = request.form.get("id_pren")
            prenda = Prenda.query.filter_by(id_prenda=idpre).first()
            db.engine.execute('delete from operacion where id_prenda ={};'.format(idpre))
            db.engine.execute('delete from operacion where id_prenda ="";')

            db.session.delete(prenda)
            db.session.commit()
        except Exception as e:
            flash('error en la operacion no se pudo borrar!')
            print(e)

    return redirect("/registro")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route('/background_process')
def background_process():
    if 1==5:#not session.get("logged_in"):
        return render_template("login.html")
    else:
        if request.args:
            try:
                id_prenda     = request.args.get("id_prenda", 0, type=int)
                can_terminada = request.args.get("can_terminada", 0, type=int)
                id_talla      = request.args.get("id_talla", 0, type=int)
                prenda        = Prenda.query.filter_by(id_prenda=id_prenda).first()
                decremt       = request.args.get("resta", 0, type=int)
#                oper          = Operacion.query.filter_by(id_prenda=request.form.get("id_prenda")).first()
                if str(decremt)=="resta":
                    can_resta     = can_terminada
                    can_terminada = 0
                    if id_talla==1:prenda.rS  =(prenda.rS+int(can_resta))
                    if id_talla==2:prenda.rM  =(prenda.rM+int(can_resta))
                    if id_talla==3:prenda.rL  =(prenda.rL+int(can_resta))
                    if id_talla==4:prenda.rXL =(prenda.rXL+int(can_resta))
                    if id_talla==5:prenda.rXXL=(prenda.rXXL+int(can_resta))

                else:
                    can_terminada = can_terminada
                    can_resta     = 0
                    if id_talla==1:prenda.rS  =(prenda.rS-int(can_terminada))#db.engine.execute ('UPDATE prenda set rS = 1 where id_prenda=1;')
                    if id_talla==2:prenda.rM  =(prenda.rM-int(can_terminada))
                    if id_talla==3:prenda.rL  =(prenda.rL-int(can_terminada))
                    if id_talla==4:prenda.rXL =(prenda.rXL-int(can_terminada))
                    if id_talla==5:prenda.rXXL=(prenda.rXXL-int(can_terminada))
                operacion     = Operacion(fecha  =dt,
                                   id_prenda     = id_prenda,
                                   can_terminada = can_terminada,
                                   can_resta     = can_resta,
                                   id_talla      = id_talla)
                if id_talla=="Seleccione Talla" or id_talla=="None" or can_terminada=="None" or can_terminada=="" or id_prenda=="None":pass
                else:
                    db.session.add(prenda)
                    db.session.add(operacion)
                    db.session.commit()
            except Exception as e:
                flash('error en la operacion')
                print(e)
    #datas = getData()['datas']
    return jsonify(result='id_talla:'+str(id_talla)+' cantidad:'+str(can_terminada))



@app.route('/getDataFaltante/<id_prenda>')
def getDataFaltante(id_prenda):
    operacion = db.engine.execute('select * from operacion where id_prenda ={};'.format(int(id_prenda)))
    t=()
    tll=()
    tllT=()
    for row in operacion:
        tallas   = db.engine.execute('select nom_talla from talla where id_talla ={};'.format(row.id_talla))
        tallasT  = db.engine.execute('select sum(can_terminada) as tallTT from operacion where id_prenda ={} AND id_talla={};'.format(row.id_prenda,row.id_talla))
        tallasTR = db.engine.execute('select sum(can_resta) as tallTR from operacion where id_prenda ={} AND id_talla={};'.format(row.id_prenda,row.id_talla))

        for row in tallas:
            ltll = list(tll)
            ltll.append(row.nom_talla)
            tll = tuple(ltll)
            for roww in tallasT:
                ltllT=list(tllT)
                for rowww in tallasTR:
                    if roww.tallTT-rowww.tallTR ==0:pass
                    else:
                        ltllT.append(str(str(row.nom_talla)+" = "+str(roww.tallTT-rowww.tallTR)+"   \n "))
                        tllT = tuple(set(ltllT))
    ltllT=(tllT)
    

    prenda   = db.engine.execute('select rS, rM, rL, rXL, rXXL , op, cant_total from prenda where id_prenda ={};'.format(id_prenda))
    for i in prenda:
        rS=i.rS
        rM=i.rM
        rL=i.rL
        rXL=i.rXL
        rXXL=i.rXXL
        total=ct(id_prenda)['sct'],
        canFalt=i.cant_total-ct(id_prenda)['rt']
        if canFalt  ==0:canFalt='(Completa!)'
        elif canFalt  <0:canFalt ="Se pasa por ("+str(canFalt*-1)  +")"   
        else:canFalt='falta : '+str(canFalt)

        if rS  ==0:rS  ='----------'
        elif rS  <0:rS ="Se pasa por ("+str(rS*-1)  +")"
        else:rS  ='falta : '+str(rS)
        if rM  ==0:rM  ='----------'
        elif rM <0:rM ="Se pasa por ("+str(rM*-1)  +")"
        else:rM  ='falta : '+str(rM)
        if rL  ==0:rL  =('----------')
        elif rL  <0:rL ="Se pasa por ("+str(rL*-1)  +")"
        else:rL  ='falta : '+str(rL)
        if rXL ==0:rXL ='----------'
        elif rXL  <0:rXL =" Se pasa por ("+str(rXL*-1)  +")"
        else:rXL  ='falta : '+str(rXL)
        if rXXL==0:rXXL='----------'
        elif rXXL  <0:rXXL ="Se pasa por ("+str(rXXL*-1)  +")"
        else:rXXL  ='falta : '+str(rXXL)   
    return jsonify(megaRS=str(rS),
        megaRM=str(rM),
        megaRL=str(rL),
        megaRXL=str(rXL),
        megaRXXL=str(rXXL),
        megacanFalt=str(canFalt),
        megacanCR=total,
        megacanPS=ltllT)
        #result ='id_talla:'+str(id_talla)+' cantidad:'+str(can_terminada)
        #return jsonify(prenda)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = gerar_token(8)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(host='127.0.0.1', port=5000)
    #app.run(host=str(direccion_equipo), port=4000)
