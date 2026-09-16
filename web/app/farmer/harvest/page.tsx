"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Plot={id:string;name:string;plot_ref:string}; type Product={id:string;code:string;name_fr:string};
export default function Harvest(){const [plots,setPlots]=useState<Plot[]>([]);const [products,setProducts]=useState<Product[]>([]);const [msg,setMsg]=useState("");
 useEffect(()=>{api("/plots").then(setPlots).catch(()=>{});api("/products").then(setProducts).catch(()=>{});},[]);
 async function submit(e:React.FormEvent<HTMLFormElement>){e.preventDefault();const f=new FormData(e.currentTarget);
 try{const d=await api("/harvests",{method:"POST",body:JSON.stringify({plot_id:f.get("plot_id"),product_code:f.get("product_code"),
 expected_start_date:f.get("start"),expected_end_date:f.get("end"),estimated_quantity_kg:Number(f.get("quantity"))})});
 setMsg(`Récolte annoncée ✓ ${d.harvest_ref}`);}catch(e){setMsg(e instanceof Error?e.message:"Erreur AGRI-CI");}}
 return <main className="workflow"><WorkflowHeader title="Ma prochaine récolte" subtitle="Annoncez tôt. AGRI-CI peut chercher le marché avant la récolte."/>
 <form className="agriForm" onSubmit={submit}><label>Produit<select name="product_code" required><option value="">Choisir</option>{products.map(p=><option key={p.id} value={p.code}>{p.name_fr}</option>)}</select></label>
 <label>Parcelle<select name="plot_id" required><option value="">Choisir ma parcelle</option>{plots.map(p=><option key={p.id} value={p.id}>{p.name} — {p.plot_ref}</option>)}</select></label>
 <label>Quantité estimée (kg)<input name="quantity" type="number" min="1" required placeholder="500"/></label>
 <div className="two"><label>Début prévu<input name="start" type="date" required/></label><label>Fin prévue<input name="end" type="date" required/></label></div>
 <button>ANNONCER MA RÉCOLTE</button>{msg&&<div className="result">{msg}</div>}</form></main>}
