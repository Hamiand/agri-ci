"use client";
import {useEffect,useState} from "react";import Link from "next/link";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type D={id:string;demand_ref:string;product_name:string;quantity_required_kg:number;destination_city?:string;status:string;aggregation_status?:string;accepted_quantity_kg:number};
export default function MyDemands(){const [rows,setRows]=useState<D[]>([]);const [msg,setMsg]=useState("Chargement…");
 useEffect(()=>{api("/demands/mine").then(d=>{setRows(d);setMsg(d.length?"":"Aucune demande.");}).catch(e=>setMsg(e.message));},[]);
 return <main className="workflow"><WorkflowHeader title="Mes demandes" subtitle="Suivez le matching, l’agrégation et les confirmations des producteurs."/>
 <section className="demandList">{rows.map(d=><Link href={`/buyer/demands/${d.id}`} className="demandCard" key={d.id}>
 <span className="pill2">{d.aggregation_status||d.status}</span><h2>{d.product_name}</h2><b>{d.quantity_required_kg.toLocaleString("fr-FR")} kg</b>
 <p>{d.destination_city||"Destination à confirmer"} • {d.demand_ref}</p>{d.accepted_quantity_kg>0&&<small>{d.accepted_quantity_kg.toLocaleString("fr-FR")} kg confirmés</small>}</Link>)}</section>
 {msg&&<div className="empty">{msg}</div>}</main>}
