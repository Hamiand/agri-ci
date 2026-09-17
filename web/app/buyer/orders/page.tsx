"use client";
import {useEffect,useState} from "react";import Link from "next/link";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type O={id:string;order_ref:string;product_name:string;quantity_kg:number;status:string};
export default function Orders(){const [rows,setRows]=useState<O[]>([]);const [msg,setMsg]=useState("Chargement…");const [loading,setLoading]=useState(false);const [failed,setFailed]=useState(false);
 async function load(){if(loading)return;setLoading(true);setFailed(false);setMsg("Chargement…");try{const d=await api("/orders");const r=Array.isArray(d)?d:[];setRows(r);setMsg(r.length?"":"Aucune commande ferme.");}catch(e){setRows([]);setFailed(true);setMsg(e instanceof Error?e.message:"Impossible de charger vos commandes.");}finally{setLoading(false);}}
 useEffect(()=>{void load();},[]);
 return <main className="workflow"><WorkflowHeader title="Mes commandes" subtitle="Suivez la circulation physique de votre commande jusqu’à la livraison."/>
 <section className="demandList">{rows.map(o=><Link href={`/buyer/orders/${o.id}`} className="demandCard" key={o.id}><span className="pill2">{o.status}</span><h2>{o.product_name}</h2><b>{Number(o.quantity_kg).toLocaleString("fr-FR")} kg</b><p>{o.order_ref}</p></Link>)}</section>
 {msg&&<div className="empty">{msg}{failed&&<div className="commitActions"><button disabled={loading} onClick={()=>void load()}>{loading?"ACTUALISATION…":"RÉESSAYER"}</button></div>}</div>}</main>}
