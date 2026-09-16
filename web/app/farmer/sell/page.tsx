"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Harvest={id:string;harvest_ref:string;estimated_quantity_kg:number;expected_start_date:string};
export default function Sell(){const [harvests,setHarvests]=useState<Harvest[]>([]);const [msg,setMsg]=useState("");
 useEffect(()=>{api("/harvests").then(setHarvests).catch(()=>{});},[]);
 async function submit(e:React.FormEvent<HTMLFormElement>){e.preventDefault();const f=new FormData(e.currentTarget);
 try{const d=await api("/offers",{method:"POST",body:JSON.stringify({harvest_id:f.get("harvest_id"),quantity_kg:Number(f.get("quantity")),
 asking_price_xof_per_kg:f.get("price")?Number(f.get("price")):null,quality_grade:f.get("grade")||null})});
 setMsg(`Offre créée ✓ ${d.offer_ref}`);}catch(e){setMsg(e instanceof Error?e.message:"Erreur AGRI-CI");}}
 return <main className="workflow"><WorkflowHeader title="Vendre" subtitle="Choisissez une récolte déjà annoncée et la quantité à proposer."/>
 <form className="agriForm" onSubmit={submit}><label>Récolte<select name="harvest_id" required><option value="">Choisir</option>{harvests.map(h=><option key={h.id} value={h.id}>{h.harvest_ref} — {h.estimated_quantity_kg} kg — {h.expected_start_date}</option>)}</select></label>
 <label>Quantité à vendre (kg)<input name="quantity" type="number" min="1" required/></label><label>Prix souhaité / kg (XOF)<input name="price" type="number" min="1"/></label>
 <label>Qualité<select name="grade"><option value="">À déterminer</option><option>A</option><option>B</option><option>C</option></select></label>
 <button>METTRE EN VENTE</button>{msg&&<div className="result">{msg}</div>}</form></main>}
