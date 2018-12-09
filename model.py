#encoding:utf-8
from sqlalchemy import *
from flask import Response
import datetime

engine = create_engine('sqlite:///./pinyin.db')
#engine.echo = True
metadata = MetaData(engine)
conn = engine.connect()

tb_zi=Table('zi', metadata,autoload=True)
tb_ci=Table('ci', metadata,autoload=True)
tb_log=Table('log', metadata,autoload=True)

def QueryObj( sql ):
    result = conn.execute(sql).fetchall()
    ret = []
    for row in result:
        r = obj();
        for t in row.items():
            if t[1] == None:
                setattr( r, t[0], "")
            else:
                setattr( r, t[0], t[1])
        ret.append(r)
    return ret;

def query5(ls,**kw):
    r=obj(result=200,ls=ls)
    for k,v in kw.items():
        setattr(r,k,QueryObj(v))
    return Response(tojson(r), mimetype='application/json')

def todict(p):
    d = p
    if type(p)!=type({}):
        d = p.__dict__
    return d

def towhere(where):
    r = " and ".join([ k+"='"+str(v)+"'" for k,v in todict(where).items()])
    r =r.replace("='(", " in (")
    r =r.replace(")'", ")")
    return r

def toinsert(tbl,obj):
    if type(obj) == type([]):
        if len(obj)== 0:
            return ""
        [delattr(u,"id") for u in obj if hasattr(u,"id")]
        d = todict(obj[0])
        fields=",".join(map( lambda x: "'"+x+"'", d.keys()))
        values = ",".join(["("+",".join(map( lambda x: "'"+str(x)+"'", u.__dict__.values()))+")" for u in obj ])
        sql = "insert into {0}({1}) values{2}".format(tbl, fields,values)
    else:
        d = todict(obj)
        if "id" in d:
            del d["id"]
        fields=",".join(map( lambda x: "'"+x+"'", d.keys()))
        values=",".join(map( lambda x: "'"+str(x)+"'", d.values()))
        sql = "insert into {0}({1}) values({2})".format(tbl, fields,values)
    return sql

def toupdate(tbl,values,where):
    dvals = todict(values)
    if "id" in dvals:
        del dvals["id"]
    vals=",".join([ k+"='"+str(v)+"'" for k,v in dvals.items()])
    whrs=" and ".join([ k+"='"+str(v)+"'" for k,v in todict(where).items()])
    sql = "update {0} set {1} where {2}".format(tbl, vals,whrs)
    return sql

def todelete(tbl,where):
    whrs=" and ".join([ k+"='"+str(v)+"'" for k,v in where.__dict__.items()])
    sql = "delete from {0} where {1}".format(tbl, whrs)
    return sql

def insert(tbl,obj):
    sql=toinsert(tbl,obj)
    conn.execute(sql) if sql != "" else 0
def insertq(tbl,obj):
    sql=toinsert(tbl,obj)
    conn.execute(toinsert(tbl,obj)) if sql != "" else 0
    return QueryObj("select * from "+tbl+" where id in (select max(id) from "+tbl+")")
def delete(tbl,obj):
    conn.execute(todelete(tbl,obj))
def querycount(tbl,where):
    whrs=" and  "0.join([ k+"='"+str(v)+"'" for k,v in where.__dict__.items()])
    rs =QueryObj( "select count(*) as count from {0} where {1}".format(tbl, whrs) )
    return rs[0].count

