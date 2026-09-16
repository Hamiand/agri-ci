"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type A={allocation_id:string;order_ref:string;product_name:string;allocated_quantity_kg:number;collected_quantity_kg:number;remaining_quantity_kg:number;status:string};
export default function Collection(){const [rows,setRows]=useState<A[]>([]);const [msg,setMsg]=useState("");
 async function load(){try{setRows(await api("/collection/my-allocations"));}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 useEffect(()=>{load();},[]);
 async function record(a:A){const qty=prompt(`Quantité réellement reçue (maximum ${a.remaining_quantity_kg} kg)`);if(!qty)return;
 const location=prompt("Lieu de collecte / village")||"Point de collecte AGRI-CI";
 try{await api("/collection",{method:"POST",body:JSON.stringify({order_allocation_id:a.allocation_id,received_quantity_kg:Number(qty),location_name:location})});setMsg("Collecte enregistrée ✓");await load();}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 return <main className="workflow"><WorkflowHeader title="Collecte" subtitle="Le poids réel remplace la quantité annoncée au moment de la collecte."/>
 {msg&&<div className="result">{msg}</div>}<section className="demandList">{rows.map(a=><article className="demandCard" key={a.allocation_id}><span className="pill2">{a.status}</span><h2>{a.product_name}</h2><b>{a.allocated_quantity_kg} kg alloués</b>
 <p>{a.collected_quantity_kg} kg collectés • {a.remaining_quantity_kg} kg restants</p><small>{a.order_ref}</small>
 {a.remaining_quantity_kg>0&&<div className="commitActions"><button onClick={()=>record(a)}>ENREGISTRER UNE COLLECTE</button></div>}</article>)}</section></main>}
