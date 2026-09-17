"use client";
import {useState} from "react";
import {API,setTokens} from "@/lib/api";
import {useRouter} from "next/navigation";

function destination(roles:string[]=[]){
 if(roles.includes("OPERATIONS_MANAGER")||roles.includes("ADMIN")) return "/operations";
 if(roles.includes("BUYER")||roles.includes("PRO_BUYER")) return "/buyer";
 return "/farmer";
}

export default function Login(){
 const [message,setMessage]=useState("");const [busy,setBusy]=useState(false);const router=useRouter();
 async function submit(e:React.FormEvent<HTMLFormElement>){
  e.preventDefault();setBusy(true);setMessage("");const fd=new FormData(e.currentTarget);
  try{
   const r=await fetch(`${API}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:fd.get("phone"),password:fd.get("password")})});
   const data=await r.json().catch(()=>({}));
   if(r.ok){setTokens(data.access_token,data.refresh_token);setMessage("Connexion réussie.");router.replace(destination(data?.user?.roles));}
   else setMessage(data?.error?.message||data?.detail||"Numéro ou mot de passe incorrect.");
  }catch{setMessage("Serveur AGRI-CI indisponible.");}
  finally{setBusy(false);}
 }
 return <main className="auth"><form onSubmit={submit}><div className="brandMark">A</div><h1>Bienvenue</h1>
 <p>Connectez-vous à AGRI-CI.</p><label>Numéro de téléphone<input name="phone" type="tel" autoComplete="tel" placeholder="+225..." required/></label>
 <label>Mot de passe<input name="password" type="password" autoComplete="current-password" required/></label><button disabled={busy}>{busy?"Connexion…":"Se connecter"}</button>
 {message&&<div className="message" role="status">{message}</div>}</form></main>
}