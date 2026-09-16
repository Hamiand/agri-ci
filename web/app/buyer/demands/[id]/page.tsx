"use client";
import {useEffect,useState} from "react";import {useParams} from "next/navigation";import WorkflowHeader from "@/components/WorkflowHeader";import {api} from "@/lib/api";
type Match={offer_ref:string;farmer_name:string;compatible_quantity_kg:number;asking_price_xof_per_kg?:number;quality_grade?:string;total_score:number};
type Agg={id:string;ref:string;target_quantity_kg:number;proposed_quantity_kg:number;accepted_quantity_kg:number;status:string;members?:any[]};
export default function DemandDetail(){const {id}=useParams<{id:string}>();const [matches,setMatches]=useState<Match[]>([]);const [agg,setAgg]=useState<Agg|null>(null);const [msg,setMsg]=useState("");
 async function match(){try{const d=await api(`/demands/${id}/match`,{method:"POST"});setMatches(d.matches);setMsg(`${d.compatible_quantity_kg} kg compatibles trouvés.`);}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 async function aggregate(){try{const d=await api(`/demands/${id}/aggregate`,{method:"POST"});const full=await api(`/aggregations/${d.aggregation_id}`);setAgg(full);setMsg("Propositions envoyées aux producteurs.");}catch(e){setMsg(e instanceof Error?e.message:"Erreur");}}
 async function refresh(){if(agg)try{setAgg(await api(`/aggregations/${agg.id}`));}catch{}}
 async function createOrder(){if(!agg)return;try{const d=await api(`/orders/from-aggregation/${agg.id}`,{method:"POST"});setMsg(`Commande ferme créée ✓ ${d.order_ref}`);}catch(e){setMsg(e instanceof Error?e.message:"Commande impossible");}}
 return <main className="workflow"><WorkflowHeader title="Matching & agrégation" subtitle="AGRI-CI recherche plusieurs offres compatibles pour constituer votre quantité."/>
 <div className="stepActions"><button onClick={match}>1. LANCER LE MATCHING</button><button onClick={aggregate} disabled={!matches.length}>2. LANCER L’AGRÉGATION</button>{agg&&<button onClick={refresh}>ACTUALISER</button>}</div>
 {msg&&<div className="result">{msg}</div>}
 {matches.length>0&&<section><h2 className="sectionTitle">Producteurs compatibles</h2><div className="demandList">{matches.map((m,i)=><article className="demandCard" key={i}><span className="score">{Math.round(m.total_score)}/100</span><h2>{m.farmer_name}</h2><b>{m.compatible_quantity_kg} kg</b><p>{m.offer_ref} • Qualité {m.quality_grade||"à confirmer"}</p><small>{m.asking_price_xof_per_kg?`${m.asking_price_xof_per_kg} XOF/kg`:"Prix à convenir"}</small></article>)}</div></section>}
 {agg&&<section><h2 className="sectionTitle">Agrégation {agg.ref}</h2><div className="progressCard"><b>{agg.accepted_quantity_kg} / {agg.target_quantity_kg} kg confirmés</b><div className="bar"><i style={{width:`${Math.min(100,100*agg.accepted_quantity_kg/agg.target_quantity_kg)}%`}}/></div><span>{agg.status}</span></div>
 {agg.accepted_quantity_kg>=agg.target_quantity_kg&&<button className="orderGate" onClick={createOrder}>CRÉER LA COMMANDE FERME</button>}
 <div className="demandList">{agg.members?.map((m,i)=><article className="demandCard" key={i}><h2>{m.farmer_name}</h2><b>{m.proposed_quantity_kg} kg proposés</b><p>{m.offer_ref}</p><span className="pill2">{m.commitment_status}</span></article>)}</div></section>}</main>}
