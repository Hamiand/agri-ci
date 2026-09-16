"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Demand={id:string;demand_ref?:string;product_code?:string;product_name?:string;quantity_required_kg?:number;destination_city?:string;target_price_xof_per_kg?:number;status?:string};
export default function Demands(){const [rows,setRows]=useState<Demand[]>([]);const [msg,setMsg]=useState("Chargement…");
 useEffect(()=>{api("/demands").then(d=>{const r=Array.isArray(d)?d:(d.items||[]);setRows(r);setMsg(r.length?"":"Aucune demande active pour le moment.");}).catch(e=>setMsg(e.message));},[]);
 return <main className="workflow"><WorkflowHeader title="Ce que les acheteurs recherchent" subtitle="Voyez la demande avant de décider quoi vendre ou produire."/>
 <section className="demandList">{rows.map(d=><article className="demandCard" key={d.id}><span className="pill2">{d.status||"PUBLIÉE"}</span><h2>{d.product_name||d.product_code||"Produit agricole"}</h2>
 <b>{d.quantity_required_kg?.toLocaleString("fr-FR")} kg recherchés</b><p>{d.destination_city||"Lieu de livraison à confirmer"}</p>
 {d.target_price_xof_per_kg&&<small>Prix cible : {d.target_price_xof_per_kg} XOF/kg</small>}</article>)}</section>{msg&&<div className="empty">{msg}</div>}</main>}
