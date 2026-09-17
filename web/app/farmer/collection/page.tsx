"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type A={allocation_id:string;order_ref:string;product_name:string;allocated_quantity_kg:number;collected_quantity_kg:number;remaining_quantity_kg:number;status:string};
export default function Collection(){const [rows,setRows]=useState<A[]>([]);const [msg,setMsg]=useState("Chargement…");const [loading,setLoading]=useState(false);const [failed,setFailed]=useState(false);
 async function load(){if(loading)return;setLoading(true);setFailed(false);setMsg("Chargement…");try{const data=await api("/collection/my-allocations");const allocations=Array.isArray(data)?data:[];setRows(allocations);setMsg(allocations.length?"":"Aucune collecte liée à vos commandes pour le moment.");}catch(e){setRows([]);setFailed(true);setMsg(e instanceof Error?e.message:"Impossible de charger vos collectes.");}finally{setLoading(false);}}
 useEffect(()=>{void load();},[]);
 return <main className="workflow"><WorkflowHeader title="Mes collectes" subtitle="Suivez les quantités réellement enregistrées au point de collecte. La pesée est saisie par un agent AGRI-CI autorisé."/>
 {msg&&<div className="result">{msg}{failed&&<div className="commitActions"><button disabled={loading} onClick={()=>void load()}>{loading?"ACTUALISATION…":"RÉESSAYER"}</button></div>}</div>}<section className="demandList">{rows.map(a=><article className="demandCard" key={a.allocation_id}><span className="pill2">{a.status}</span><h2>{a.product_name}</h2><b>{Number(a.allocated_quantity_kg).toLocaleString("fr-FR")} kg prévus</b>
 <p>{Number(a.collected_quantity_kg).toLocaleString("fr-FR")} kg enregistrés • {Number(a.remaining_quantity_kg).toLocaleString("fr-FR")} kg restant à collecter</p><small>{a.order_ref}</small>
 </article>)}</section></main>}
