"use client";
import {useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
export default function Payments(){const [msg,setMsg]=useState("");const [rows,setRows]=useState<any[]>([]);const [busy,setBusy]=useState(false);
 async function submit(e:React.FormEvent<HTMLFormElement>){e.preventDefault();setBusy(true);setMsg("");const f=new FormData(e.currentTarget);
 try{const d=await api(`/payments/orders/${f.get("order_id")}/prepare`,{method:"POST",body:JSON.stringify({
 price_xof_per_kg:Number(f.get("price")),transport_xof:Number(f.get("transport")||0),
 service_xof:Number(f.get("service")||0),other_xof:Number(f.get("other")||0),provider:f.get("provider")})});
 setRows(d.prepared||[]);setMsg(`${d.prepared?.length||0} règlement(s) préparé(s) sur les quantités livrées et non encore réglées.`);}catch(e){setRows([]);setMsg(e instanceof Error?e.message:"Erreur");}finally{setBusy(false);}}
 return <main className="workflow"><WorkflowHeader title="Préparer les règlements" subtitle="AGRI-CI calcule le brut sur la quantité réellement livrée, répartit les coûts autorisés et prépare le net dû à chaque producteur."/>
 <form className="agriForm" onSubmit={submit}><label>Référence technique de la commande<input name="order_id" required/></label><label>Prix commercial (XOF/kg)<input name="price" type="number" min="1" required placeholder="500"/></label>
 <label>Transport total (XOF)<input name="transport" type="number" min="0" defaultValue="7000"/></label><label>Service AGRI-CI total (XOF)<input name="service" type="number" min="0" defaultValue="4500"/></label>
 <label>Autres coûts autorisés (XOF)<input name="other" type="number" min="0" defaultValue="1500"/></label><label>Prestataire<input name="provider" required placeholder="PAYMENT_PARTNER"/></label>
 <button disabled={busy}>{busy?"PRÉPARATION…":"PRÉPARER LES RÈGLEMENTS"}</button></form>{msg&&<div className="result">{msg}</div>}
 <section className="demandList">{rows.map((p,i)=><article className="demandCard" key={p.payment_ref||i}><span className="pill2">{p.status}</span><h2>{p.payment_ref}</h2><b>{Number(p.net_amount_xof).toLocaleString("fr-FR")} XOF net</b><p>{Number(p.delivered_quantity_kg).toLocaleString("fr-FR")} kg livrés • brut {Number(p.gross_amount_xof).toLocaleString("fr-FR")} XOF</p></article>)}</section></main>}
