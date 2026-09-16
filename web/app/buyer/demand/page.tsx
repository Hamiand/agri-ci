"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Product={id:string;code:string;name_fr:string};
export default function Demand(){const [products,setProducts]=useState<Product[]>([]);const [msg,setMsg]=useState("");
 useEffect(()=>{api("/products").then(setProducts).catch(()=>{});},[]);
 async function submit(e:React.FormEvent<HTMLFormElement>){e.preventDefault();const f=new FormData(e.currentTarget);const grades=["A","B","C"].filter(g=>f.get(`g${g}`));
 try{const d=await api("/demands",{method:"POST",body:JSON.stringify({product_code:f.get("product_code"),quantity_required_kg:Number(f.get("quantity")),
 delivery_start_date:f.get("start"),delivery_end_date:f.get("end"),target_price_xof_per_kg:f.get("price")?Number(f.get("price")):null,
 quality_grades:grades,destination_city:f.get("city")||null})});setMsg(`Demande publiée ✓ ${d.demand_ref}`);}
 catch(e){setMsg(e instanceof Error?e.message:"Erreur AGRI-CI");}}
 return <main className="workflow"><WorkflowHeader title="Publier une demande" subtitle="Dites à AGRI-CI ce dont vous avez besoin. Le moteur cherchera et agrégera l’offre compatible."/>
 <form className="agriForm" onSubmit={submit}><label>Produit<select name="product_code" required><option value="">Choisir</option>{products.map(p=><option key={p.id} value={p.code}>{p.name_fr}</option>)}</select></label>
 <label>Quantité recherchée (kg)<input name="quantity" type="number" min="1" required placeholder="3000"/></label>
 <div className="two"><label>Livraison dès le<input name="start" type="date" required/></label><label>Jusqu’au<input name="end" type="date" required/></label></div>
 <label>Ville de destination<input name="city" placeholder="Abidjan"/></label><label>Prix cible / kg (XOF)<input name="price" type="number" min="1" placeholder="760"/></label>
 <fieldset><legend>Qualité acceptée</legend><label className="check"><input type="checkbox" name="gA"/> A</label><label className="check"><input type="checkbox" name="gB"/> B</label><label className="check"><input type="checkbox" name="gC"/> C</label></fieldset>
 <button>PUBLIER MA DEMANDE</button>{msg&&<div className="result">{msg}</div>}</form></main>}
