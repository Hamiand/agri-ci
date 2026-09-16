from decimal import Decimal

WEIGHTS={"date":Decimal("0.25"),"price":Decimal("0.20"),"logistics":Decimal("0.20"),
         "quality":Decimal("0.15"),"reliability":Decimal("0.10"),"volume":Decimal("0.10")}

def date_compatible(h_start,h_end,d_start,d_end):
    return h_start<=d_end and h_end>=d_start

def price_score(asking,target):
    if target is None or asking is None: return Decimal("70")
    if asking<=target: return Decimal("100")
    ratio=(asking-target)/target
    if ratio>=Decimal("0.25"): return Decimal("0")
    return max(Decimal("0"),Decimal("100")-(ratio/Decimal("0.25"))*Decimal("100"))

def quality_score(grade,required):
    if not required: return Decimal("80")
    return Decimal("100") if grade in required else Decimal("0")

def volume_score(available,required):
    ratio=min(Decimal("1"),available/required)
    # Deliberately limited effect: small farmers are not excluded.
    return Decimal("50")+ratio*Decimal("50")

def score_candidate(*,available,required,asking,target,grade,required_grades,
                    logistics=Decimal("70"),reliability=Decimal("70")):
    parts={"date":Decimal("100"),"price":price_score(asking,target),"logistics":logistics,
           "quality":quality_score(grade,required_grades),"reliability":reliability,
           "volume":volume_score(available,required)}
    total=sum(parts[k]*WEIGHTS[k] for k in WEIGHTS)
    return parts,total.quantize(Decimal("0.01"))
