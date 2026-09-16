"use client";
import {useState} from "react";
import {setTokens} from "@/lib/api";
import {useRouter} from "next/navigation";
export default function Login(){
 const [message,setMessage]=useState(""); const router=useRouter();
 async function submit(e:React.FormEvent<HTMLFormElement>){
  e.preventDefault(); const fd=new FormData(e.currentTarget);
  try{
   const r=await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/login`,{method:"POST",
    headers:{"Content-Type":"application/json"},body:JSON.stringify({email:fd.get("email"),password:fd.get("password")})});
   if(r.ok){const data=await r.json();setTokens(data.access_token,data.refresh_token);setMessage("Connexion réussie.");router.push("/farmer");}
   else setMessage("Identifiants incorrects.");
  }catch{setMessage("Serveur AGRI-CI indisponible.");}
 }
 return <main className="auth"><form onSubmit={submit}><div className="brandMark">A</div><h1>Bienvenue</h1>
 <p>Connectez-vous à AGRI-CI.</p><label>Email<input name="email" type="email" required/></label>
 <label>Mot de passe<input name="password" type="password" required/></label><button>Se connecter</button>
 {message&&<div className="message">{message}</div>}</form></main>
}