"use client";
import {useEffect,useState} from "react";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type C={id:string;commitment_ref:string;quantity_kg:number;status:string;product_name:string;destination_city?:string;target_price_xof_per_kg?:number;asking_price_xof_per_kg?:number;expires_at:string};
export default function Commitments(){const [rows,setRows]=useState<C[]>([]);const [msg,setMsg]=useState("");
 async function load(){try{setRows(await api("/commitments"));}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 useEffect(()=>{load();},[]);
 async function act(id:string,action:"accept"|"decline"){try{await api(`/commitments/${id}/${action}`,{method:"POST"});setMsg(action==="accept"?"Proposition acceptée.":"Proposition refusée. AGRI-CI cherche un remplacement.");await load();}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 return <main className="workflow"><WorkflowHeader title="Propositions AGRI-CI" subtitle="Répondez aux demandes auxquelles votre offre peut contribuer."/>
 {msg&&<div className="result">{msg}</div>}<section className="demandList">{rows.map(c=><article className="demandCard" key={c.id}><span className="pill2">{c.status}</span><h2>{c.product_name}</h2><b>{c.quantity_kg} kg demandés</b><p>Destination : {c.destination_city||"à confirmer"}</p>
 <small>{c.asking_price_xof_per_kg?`Votre prix : ${c.asking_price_xof_per_kg} XOF/kg`:"Prix à confirmer"} • expire {new Date(c.expires_at).toLocaleString("fr-FR")}</small>
 {c.status==="PENDING"&&<div className="commitActions"><button onClick={()=>act(c.id,"accept")}>ACCEPTER</button><button className="decline" onClick={()=>act(c.id,"decline")}>REFUSER</button></div>}</article>)}</section></main>}
