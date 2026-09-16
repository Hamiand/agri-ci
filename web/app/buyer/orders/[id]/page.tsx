"use client";
import {useEffect,useState} from "react";import {useParams} from "next/navigation";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Ops={order_ref:string;quantity_kg:number;status:string;collected_quantity_kg:number;lots_quantity_kg:number;delivered_quantity_kg:number;transport_jobs:{transport_ref:string;status:string;origin:string;destination:string}[]};
export default function OrderOps(){const {id}=useParams<{id:string}>();const [o,setO]=useState<Ops|null>(null);const [msg,setMsg]=useState("");
 async function load(){try{setO(await api(`/orders/${id}/operations`));}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 useEffect(()=>{load();},[]);
 if(!o)return <main className="workflow"><WorkflowHeader title="Suivi de commande" subtitle="Chargement…"/>{msg&&<div className="empty">{msg}</div>}</main>;
 const pct=(x:number)=>Math.min(100,100*x/o.quantity_kg);
 return <main className="workflow"><WorkflowHeader title={o.order_ref} subtitle={`${o.quantity_kg.toLocaleString("fr-FR")} kg • ${o.status}`}/>
 <section className="timeline">
 {[[ "COLLECTE",o.collected_quantity_kg],["LOTS QUALITÉ",o.lots_quantity_kg],["LIVRAISON",o.delivered_quantity_kg]].map(([n,v])=><div className="timelineStep" key={String(n)}><span>{n}</span><b>{Number(v).toLocaleString("fr-FR")} / {o.quantity_kg.toLocaleString("fr-FR")} kg</b><div className="bar light"><i style={{width:`${pct(Number(v))}%`}}/></div></div>)}
 </section><h2 className="sectionTitle">Transport</h2><section className="demandList">{o.transport_jobs.length?o.transport_jobs.map(j=><article className="demandCard" key={j.transport_ref}><span className="pill2">{j.status}</span><h2>{j.transport_ref}</h2><p>{j.origin} → {j.destination}</p></article>):<div className="empty">Transport pas encore planifié.</div>}</section>
 <button className="refreshButton" onClick={load}>ACTUALISER LE SUIVI</button></main>}
