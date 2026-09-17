"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Plot={id:string;name:string;plot_ref:string}; type Product={id:string;code:string;name_fr:string};
export default function Harvest(){const [plots,setPlots]=useState<Plot[]>([]);const [products,setProducts]=useState<Product[]>([]);const [msg,setMsg]=useState("");const [busy,setBusy]=useState(false);
 useEffect(()=>{api("/plots").then(setPlots).catch(e=>setMsg(e instanceof Error?e.message:"Impossible de charger vos parcelles."));api("/products").then(setProducts).catch(e=>setMsg(e instanceof Error?e.message:"Impossible de charger les produits."));},[]);
 async function submit(e:React.FormEvent<HTMLFormElement>){e.preventDefault();if(busy)return;const form=e.currentTarget;const f=new FormData(form);const quantity=Number(f.get("quantity"));const start=String(f.get("start")||"");const end=String(f.get("end")||"");
 if(!Number.isFinite(quantity)||quantity<=0){setMsg("La quantité estimée doit être supérieure à 0 kg.");return;}if(!start||!end||end<start){setMsg("La date de fin prévue ne peut pas être antérieure à la date de début.");return;}setBusy(true);setMsg("");
 try{const d=await api("/harvests",{method:"POST",body:JSON.stringify({plot_id:f.get("plot_id"),product_code:f.get("product_code"),expected_start_date:start,expected_end_date:end,estimated_quantity_kg:quantity})});setMsg(`Récolte annoncée ✓ ${d.harvest_ref}`);form.reset();}catch(e){setMsg(e instanceof Error?e.message:"Erreur AGRI-CI");}finally{setBusy(false);}}
 return <main className="workflow"><WorkflowHeader title="Ma prochaine récolte" subtitle="Annoncez tôt. AGRI-CI peut chercher le marché avant la récolte."/>
 <form className="agriForm" onSubmit={submit}><label>Produit<select name="product_code" required><option value="">Choisir</option>{products.map(p=><option key={p.id} value={p.code}>{p.name_fr}</option>)}</select></label>
 <label>Parcelle<select name="plot_id" required><option value="">Choisir ma parcelle</option>{plots.map(p=><option key={p.id} value={p.id}>{p.name} — {p.plot_ref}</option>)}</select></label>
 <label>Quantité estimée (kg)<input name="quantity" type="number" min="0.001" step="0.001" required placeholder="500"/></label>
 <div className="two"><label>Début prévu<input name="start" type="date" required/></label><label>Fin prévue<input name="end" type="date" required/></label></div>
 <button disabled={busy}>{busy?"ENREGISTREMENT…":"ANNONCER MA RÉCOLTE"}</button>{msg&&<div className="result">{msg}</div>}</form></main>}
