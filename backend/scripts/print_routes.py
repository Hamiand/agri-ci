from app.main import app
for r in sorted(app.routes,key=lambda x:getattr(x,"path","")):
    methods=",".join(sorted(getattr(r,"methods",[]) or []))
    print(f"{methods:20} {getattr(r,'path','')}")
