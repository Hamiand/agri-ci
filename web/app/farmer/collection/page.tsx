"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type A={allocation_id:string;order_ref:string;product_name:string;allocated_quantity_kg:number;collected_quantity_kg:number;remaining_quantity_kg:number;status:string};
export default function Collection(){const [rows,setRows]=useState<A[]>([]);const [msg,setMsg]=useState("Chargement…");
 useEffect(()=>{api("/collection/my-allocations").then(data=>{setRows(data);setMsg(data.length?"":"Aucune collecte liée à vos commandes pour le moment.");}).catch(e=>setMsg(e instanceof Error?e.message:"Impossible de charger vos collectes."));},[]);
 return <main className="workflow"><WorkflowHeader title="Mes collectes" subtitle="Suivez les quantités réellement enregistrées au point de collecte. La pesée est saisie par un agent AGRI-CI autorisé."/>
 {msg&&<div className="result">{msg}</div>}<section className="demandList">{rows.map(a=><article className="demandCard" key={a.allocation_id}><span className="pill2">{a.status}</span><h2>{a.product_name}</h2><b>{a.allocated_quantity_kg} kg prévus</b>
 <p>{a.collected_quantity_kg} kg enregistrés • {a.remaining_quantity_kg} kg restant à collecter</p><small>{a.order_ref}</small>
 </article>)}</section></main>}
