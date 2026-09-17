"use client";
import {useEffect,useState} from "react";import {useParams} from "next/navigation";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Ops={order_ref:string;quantity_kg:number;status:string;collected_quantity_kg:number;lots_quantity_kg:number;delivered_quantity_kg:number;transport_jobs:{transport_ref:string;status:string;origin:string;destination:string}[]};
export default function OrderOps(){const {id}=useParams<{id:string}>();const [o,setO]=useState<Ops|null>(null);const [msg,setMsg]=useState("Chargement…");const [busy,setBusy]=useState(false);
 async function load(){if(busy)return;setBusy(true);try{setO(await api(`/orders/${id}/operations`));setMsg("");}catch(e){setMsg(e instanceof Error?e.message:"Impossible de charger le suivi de cette commande.");}finally{setBusy(false);}}
 useEffect(()=>{void load();},[id]);
 if(!o)return <main className="workflow"><WorkflowHeader title="Suivi de commande" subtitle="Collecte, qualité, transport et livraison."/>{msg&&<div className="empty">{msg}</div>}{!busy&&<button className="refreshButton" onClick={load}>RÉESSAYER</button>}</main>;
 const pct=(x:number)=>o.quantity_kg>0?Math.min(100,100*x/o.quantity_kg):0;
 return <main className="workflow"><WorkflowHeader title={o.order_ref} subtitle={`${o.quantity_kg.toLocaleString("fr-FR")} kg • ${o.status}`}/>
 {msg&&<div className="result">{msg}</div>}<section className="timeline">
 {[["COLLECTE",o.collected_quantity_kg],["LOTS QUALITÉ",o.lots_quantity_kg],["LIVRAISON",o.delivered_quantity_kg]].map(([n,v])=><div className="timelineStep" key={String(n)}><span>{n}</span><b>{Number(v).toLocaleString("fr-FR")} / {o.quantity_kg.toLocaleString("fr-FR")} kg</b><div className="bar light"><i style={{width:`${pct(Number(v))}%`}}/></div></div>)}
 </section><h2 className="sectionTitle">Transport</h2><section className="demandList">{o.transport_jobs.length?o.transport_jobs.map(j=><article className="demandCard" key={j.transport_ref}><span className="pill2">{j.status}</span><h2>{j.transport_ref}</h2><p>{j.origin} → {j.destination}</p></article>):<div className="empty">Transport pas encore planifié.</div>}</section>
 <button className="refreshButton" disabled={busy} onClick={load}>{busy?"ACTUALISATION…":"ACTUALISER LE SUIVI"}</button></main>}
