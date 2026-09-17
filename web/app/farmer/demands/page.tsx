"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Demand={id:string;demand_ref?:string;product_code?:string;product_name?:string;quantity_required_kg?:number;destination_city?:string;target_price_xof_per_kg?:number;status?:string;delivery_start_date?:string;delivery_end_date?:string};
const ACTIVE=new Set(["PUBLISHED","MATCHING","PARTIALLY_MATCHED","MATCHED","PENDING_CONFIRMATION"]);
export default function Demands(){const [rows,setRows]=useState<Demand[]>([]);const [msg,setMsg]=useState("Chargement…");
 async function load(){try{const d=await api("/demands");const all=Array.isArray(d)?d:(d.items||[]);const active=all.filter((x:Demand)=>!x.status||ACTIVE.has(x.status));setRows(active);setMsg(active.length?"":"Aucune demande active pour le moment.");}catch(e){setRows([]);setMsg(e instanceof Error?e.message:"Impossible de charger les demandes actives.");}}
 useEffect(()=>{void load();},[]);
 return <main className="workflow"><WorkflowHeader title="Ce que les acheteurs recherchent" subtitle="Consultez les demandes encore ouvertes avant de décider quoi vendre ou produire."/>
 <section className="demandList">{rows.map(d=><article className="demandCard" key={d.id}><span className="pill2">{d.status||"PUBLIÉE"}</span><h2>{d.product_name||d.product_code||"Produit agricole"}</h2>
 <b>{typeof d.quantity_required_kg==="number"?`${d.quantity_required_kg.toLocaleString("fr-FR")} kg recherchés`:"Quantité à confirmer"}</b><p>{d.destination_city||"Lieu de livraison à confirmer"}</p>
 {(d.delivery_start_date||d.delivery_end_date)&&<p>Livraison : {d.delivery_start_date?new Date(d.delivery_start_date).toLocaleDateString("fr-FR"):"date à confirmer"}{d.delivery_end_date?` → ${new Date(d.delivery_end_date).toLocaleDateString("fr-FR")}`:""}</p>}
 {typeof d.target_price_xof_per_kg==="number"&&<small>Prix cible indicatif : {d.target_price_xof_per_kg.toLocaleString("fr-FR")} XOF/kg</small>}</article>)}</section>{msg&&<div className="empty">{msg}</div>}</main>}
