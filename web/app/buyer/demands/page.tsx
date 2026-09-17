"use client";
import {useEffect,useState} from "react";import Link from "next/link";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type D={id:string;demand_ref:string;product_name:string;quantity_required_kg:number;destination_city?:string;status:string;aggregation_status?:string;accepted_quantity_kg:number};
export default function MyDemands(){const [rows,setRows]=useState<D[]>([]);const [msg,setMsg]=useState("Chargement…");const [loading,setLoading]=useState(false);const [failed,setFailed]=useState(false);
 async function load(){if(loading)return;setLoading(true);setFailed(false);setMsg("Chargement…");try{const d=await api("/demands/mine");const data=Array.isArray(d)?d:[];setRows(data);setMsg(data.length?"":"Aucune demande.");}catch(e){setRows([]);setFailed(true);setMsg(e instanceof Error?e.message:"Impossible de charger vos demandes.");}finally{setLoading(false);}}
 useEffect(()=>{void load();},[]);
 return <main className="workflow"><WorkflowHeader title="Mes demandes" subtitle="Suivez le matching, l’agrégation et les confirmations des producteurs."/>
 <section className="demandList">{rows.map(d=><Link href={`/buyer/demands/${d.id}`} className="demandCard" key={d.id}>
 <span className="pill2">{d.aggregation_status||d.status}</span><h2>{d.product_name}</h2><b>{Number(d.quantity_required_kg).toLocaleString("fr-FR")} kg</b>
 <p>{d.destination_city||"Destination à confirmer"} • {d.demand_ref}</p>{Number(d.accepted_quantity_kg)>0&&<small>{Number(d.accepted_quantity_kg).toLocaleString("fr-FR")} kg confirmés</small>}</Link>)}</section>
 {msg&&<div className="empty">{msg}{failed&&<div className="commitActions"><button disabled={loading} onClick={()=>void load()}>{loading?"ACTUALISATION…":"RÉESSAYER"}</button></div>}</div>}</main>}
